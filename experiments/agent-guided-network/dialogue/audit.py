"""Post-selection evidence audit, paired representation checks, and isolated exports."""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable

import numpy as np
import torch

from run import SETTINGS, dataset, development, episodes, read, verify
from evaluate import evaluate, score_summary
from graph import (Revision, compile_graph, graph_hashes, join_parameters, oak_run,
                   validate_oak_revision, validate_python_revision, write_graph)
from runtime import (GROUPS, SHAPES, VOCAB, Program, Session, canonical_bytes,
                     encode_inputs, identity, predict, token_ids)
from train import configure, from_record

ARMS = ('baseline', 'ordinary', 'selected')
REGIMES = ('ordinary', 'combination', 'long', 'wording')


def save(path: Path, record: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(record))


def measured(function: Callable[[], Any], repeats: int = 5) -> float:
    function()
    durations = []
    for _ in range(repeats):
        start = time.perf_counter()
        function()
        durations.append(time.perf_counter() - start)
    return statistics.median(durations)


def audit_run(directory: Path, seed: int) -> dict[str, Any]:
    frozen = verify(directory)
    closed, proposal = read(directory / 'SELECTION_CLOSED.json'), read(directory / 'proposal.json')
    folder, data = directory / str(seed), dataset(directory, seed)
    if identity(read(folder / 'data.json')) != frozen['data'][str(seed)]:
        raise AssertionError('training/development data identity differs')
    baseline = read(folder / 'baseline.json')
    best = max(range(1, SETTINGS['blocks'] + 1),
               key=lambda number: read(folder / f'block-{number}-scores.json')['development']['mean'])
    if baseline != read(folder / f'block-{best}.json'):
        raise AssertionError('baseline selection differs')
    selected_ids = {arm: identity(read(folder / (arm + '.json'))) for arm in ARMS}
    if selected_ids != closed['selected'][str(seed)] or closed['proposal'] != identity(proposal):
        raise AssertionError('selection identity differs')
    candidates = [read(folder / f'candidate-{representation}.json') for representation in ('oak', 'python')]
    if candidates[0] != candidates[1]:
        raise AssertionError('OAK/Python independently fitted weights differ')
    candidate = candidates[0]
    revision = Revision(identity(baseline), tuple(proposal['groups']))
    changed = validate_python_revision(baseline, candidate, revision)
    if changed != validate_oak_revision(folder / 'baseline-oak', folder / 'candidate-oak', revision):
        raise AssertionError('revision policy differs')
    before, after = development(baseline, data), development(candidate, data)
    accepted = (after['mean'] >= before['mean'] + SETTINGS['min_gain'] and
                all(after[regime]['reply_accuracy'] >= before[regime]['reply_accuracy'] - SETTINGS['max_regression']
                    for regime in ('ordinary', 'varied')))
    for representation in ('oak', 'python'):
        decision = read(folder / f'decision-{representation}.json')
        if decision['before'] != before or decision['after'] != after or decision['accepted'] != accepted:
            raise AssertionError('decision evidence differs')
        if not frozen['created_ns'] < proposal['created_ns'] < decision['evaluated_ns'] < closed['closed_ns']:
            raise AssertionError('proposal and selection chronology differs')
    selected = read(folder / 'selected.json')
    if selected != (candidate if accepted else baseline) or selected != join_parameters(folder / 'selected-oak'):
        raise AssertionError('selected OAK source differs')
    old, new = graph_hashes(folder / 'baseline-oak'), graph_hashes(folder / 'candidate-oak')
    actual_changed = [name for name in old if old[name] != new[name]]
    if set(actual_changed) != {name + '.oak.md' for name in changed}:
        raise AssertionError('unexpected document change')
    seen = set()
    for other_seed in SETTINGS['seeds']:
        for rows in dataset(directory, other_seed).values():
            keys = [row.key for row in rows]
            if len(set(keys)) != len(keys) or seen.intersection(keys):
                raise AssertionError('teaching/development histories overlap')
            seen.update(keys)
    for other_seed in SETTINGS['seeds']:
        for rows in read(directory / str(other_seed) / 'final-cases.json').values():
            keys = [row['key'] for row in rows]
            if len(set(keys)) != len(keys) or seen.intersection(keys):
                raise AssertionError('final histories overlap')
            seen.update(keys)
    saved = read(folder / 'final.json')
    final_sets = read(folder / 'final-cases.json')
    scores = {}
    for arm in ARMS:
        model = read(folder / (arm + '.json'))
        scores[arm] = {}
        for regime in REGIMES:
            result = evaluate(model, episodes(final_sets[regime]))
            if identity(result) != identity(saved[arm][regime]):
                raise AssertionError('saved score, reply, label, or conversation differs')
            scores[arm][regime] = score_summary(result)
    no_history = evaluate(selected, episodes(final_sets['ordinary']), erase_history=True)
    if identity(no_history) != identity(saved['without_history']):
        raise AssertionError('history intervention differs')
    evidence = {'seed': seed, 'scores': scores, 'without_history': score_summary(no_history),
                'independent_candidate_weight_identity': identity(candidate), 'representations_identical': True,
                'selected': selected_ids, 'accepted': accepted, 'changed_documents': actual_changed,
                'unchanged_documents': sorted(set(old) - set(actual_changed)),
                'final_predictions_recomputed': len(ARMS) * len(REGIMES) * SETTINGS['final_episodes'] * 4,
                'all_history_identities_disjoint': True, 'scientific_source_hashes_match': True}
    save(folder / 'audit.json', evidence)
    print(json.dumps(evidence, indent=2), flush=True)
    return evidence


ISOLATED = r'''
import importlib.util, json, pathlib, sys
root = pathlib.Path(sys.argv[1])
forbidden = ('oak', 'torch', 'task', 'train', 'socket', 'requests', 'urllib', 'http')
def guard(event, args):
    if event == 'import' and args[0].split('.')[0] in forbidden:
        raise RuntimeError('forbidden inference import: ' + args[0])
    if event.startswith('socket.'):
        raise RuntimeError('network disabled')
    if event == 'open' and isinstance(args[0], (str, bytes)):
        text = str(args[0])
        if sys.argv[2] in text or 'site-packages/oak/' in text:
            raise RuntimeError('repository read disabled')
sys.addaudithook(guard)
spec = importlib.util.spec_from_file_location('dialogue_inference', root / 'runtime.py')
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
model = json.loads((root / 'model.json').read_text())
program = json.loads((root / 'program.json').read_text())
fixtures = json.loads((root / 'fixtures.json').read_text())
batch_count = 0
for start in range(0, len(fixtures), 32):
    group = fixtures[start:start + 32]
    histories = [[] for _ in group]
    compiled = module.Program(program)
    for turn in range(4):
        users = [fixture['users'][turn] for fixture in group]
        a = module.predict(model, histories, users)[0]
        b = compiled.run('interface.batch', {'HISTORIES': histories, 'TEXTS': users})['REPLIES']
        if a != b or a != [fixture['replies'][turn] for fixture in group]:
            raise AssertionError('isolated full-set batch prediction differs')
        for history, user, reply in zip(histories, users, a, strict=True):
            history.extend([{'role': 'user', 'text': user}, {'role': 'assistant', 'text': reply}])
        batch_count += len(group)
count = 0
for fixture in fixtures[::16]:
    direct, compiled = module.Session(model), module.Program(program)
    for user, expected in zip(fixture['users'], fixture['replies'], strict=True):
        a = direct.answer(user)
        b = compiled.run('interface.chat', {'TEXTS': [user]})['REPLIES'][0]
        if a != expected or b != expected:
            raise AssertionError('restored dialogue differs from scored model')
        state_a, state_b = direct.snapshot(), compiled.snapshot()
        direct, compiled = module.Session(model), module.Program(program)
        direct.restore(json.loads(json.dumps(state_a)))
        compiled.restore(json.loads(json.dumps(state_b)))
        count += 1
print(json.dumps({'full_set_batch_turns_per_engine': batch_count, 'restored_sample_turns_per_engine': count, 'restoration_after_each_sample_turn': True,
                  'engines': ['python', 'lowered-oak'], 'model_sha256': module.identity(model)}))
'''


def export_and_check(directory: Path, seed: int) -> dict[str, Any]:
    verify(directory)
    folder = directory / str(seed)
    model = read(folder / 'selected.json')
    compiled = compile_graph(folder / 'selected-oak')
    destination = folder / 'export'
    destination.mkdir(exist_ok=True)
    save(destination / 'model.json', model)
    save(destination / 'program.json', compiled)
    shutil.copyfile(Path(__file__).with_name('runtime.py'), destination / 'runtime.py')
    fixtures = [dialogue for regime in REGIMES for dialogue in read(folder / 'final.json')['selected'][regime]['dialogues']]
    save(destination / 'fixtures.json', fixtures)
    # Import roots and credentials are omitted; no teaching/evaluator module is copied.
    env = {key: os.environ[key] for key in ('PATH', 'LD_LIBRARY_PATH', 'SYSTEMROOT') if key in os.environ}
    env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', PYTHONHASHSEED='0')
    isolated_file = folder / 'isolated-verification.json'
    if isolated_file.exists():
        isolated = read(isolated_file)
        if isolated['model_sha256'] != identity(model):
            raise AssertionError('stale isolated verification')
    else:
        outcome = subprocess.run([sys.executable, '-I', '-c', ISOLATED, str(destination), str(Path(__file__).resolve().parents[3])], env=env,
                                 cwd=destination, capture_output=True, text=True, check=True)
        isolated = json.loads(outcome.stdout)
    save(folder / 'isolated-verification.json', isolated)
    print('Isolated checks complete: ' + json.dumps(isolated), flush=True)
    native_turns = 0
    probability_difference = 0.0
    network = from_record(model).eval()
    for regime in REGIMES:
        dialogue = read(folder / 'final.json')['selected'][regime]['dialogues'][0]
        if regime == 'ordinary':
            arrivals = [('interface.chat', {'TEXTS': [text]}) for text in dialogue['users'][:2]]
            print('Native OAK sample: ' + str(seed) + ', first two connected turns', flush=True)
            start = time.perf_counter()
            outputs, _ = oak_run(folder / 'selected-oak', arrivals)
            if [output['REPLIES'][0] for output in outputs] != dialogue['replies'][:2]:
                raise AssertionError('actual OAK conversation differs')
            native_turns = 2
            save(folder / 'native-verification.json', {'matched_turns': 2, 'seconds': time.perf_counter() - start,
                  'fixture_key': dialogue['key'], 'scope': 'first two connected ordinary turns; state serialized by OAK host'})
        history = []
        for text, reply in zip(dialogue['users'], dialogue['replies'], strict=True):
            tokens = encode_inputs([history], [text])
            with torch.no_grad():
                numerical = network(torch.from_numpy(tokens)).softmax(-1).numpy()
            direct = predict(model, [history], [text])[1]
            probability_difference = max(probability_difference, float(np.abs(numerical - direct).max()))
            if not np.array_equal(numerical.argmax(-1), direct.argmax(-1)):
                raise AssertionError('training and numerical runtime token decisions differ')
            history.extend([{'role': 'user', 'text': text}, {'role': 'assistant', 'text': reply}])
    hashes = {file.name: __import__('hashlib').sha256(file.read_bytes()).hexdigest()
              for file in destination.iterdir() if file.name in ('model.json', 'program.json', 'runtime.py')}
    save(destination / 'manifest.json', hashes)
    evidence = {'isolated': isolated, 'native_oak_turns': native_turns, 'native_scope': 'two connected ordinary turns per model; full native sweep exceeded command limits',
                'torch_numpy_probability_max_absolute_difference': probability_difference,
                'graph_document_count': len(graph_hashes(folder / 'selected-oak')),
                'source_document_hashes': graph_hashes(folder / 'selected-oak')}
    save(folder / 'export-verification.json', evidence)
    print(json.dumps(evidence, indent=2), flush=True)
    return evidence


def faults(directory: Path) -> list[dict[str, Any]]:
    baseline = read(directory / str(SETTINGS['seeds'][0]) / 'baseline.json')
    results = []
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        before = root / 'before'
        write_graph(baseline, before)
        for case in ('valid', 'wrong_owner', 'stale', 'empty', 'shape', 'nonfinite', 'vocabulary'):
            model = copy.deepcopy(baseline)
            model['weights']['output_bias'][0] += 0.01
            permitted = ('encoder',) if case == 'wrong_owner' else ('readout',)
            revision = Revision('stale' if case == 'stale' else identity(baseline), permitted)
            if case == 'empty':
                model = copy.deepcopy(baseline)
            elif case == 'shape':
                model['weights']['output'] = [1]
            elif case == 'nonfinite':
                model['weights']['output_bias'][0] = float('nan')
            elif case == 'vocabulary':
                model['vocabulary'] = list(reversed(model['vocabulary']))
            outcomes = {}
            for representation in ('python', 'oak'):
                try:
                    if representation == 'python':
                        validate_python_revision(baseline, model, revision)
                    else:
                        write_graph(model, root / case)
                        validate_oak_revision(before, root / case, revision)
                    outcomes[representation] = 'accepted'
                except ValueError:
                    outcomes[representation] = 'rejected'
            expected = 'accepted' if case == 'valid' else 'rejected'
            if set(outcomes.values()) != {expected}:
                raise AssertionError('fault policy mismatch: ' + case)
            results.append({'case': case, **outcomes, 'owner': 'shared host validation, not native OAK tensor validation'})
    return results


def summarise(directory: Path) -> dict[str, Any]:
    audits = [read(directory / str(seed) / 'audit.json') for seed in SETTINGS['seeds']]
    scores = {arm: {regime: {metric: statistics.mean(item['scores'][arm][regime][metric] for item in audits)
                            for metric in ('reply_accuracy', 'dialogue_accuracy')}
                    for regime in REGIMES} for arm in ARMS}
    seed = SETTINGS['seeds'][0]
    folder = directory / str(seed)
    fixture = read(folder / 'final.json')['selected']['ordinary']['dialogues'][0]
    model = read(folder / 'selected.json')
    program = compile_graph(folder / 'selected-oak')
    payload = {'HISTORIES': [[]], 'TEXTS': [fixture['users'][0]]}
    engine = Program(program)
    timings = {'python_direct': measured(lambda: predict(model, [[]], payload['TEXTS'])),
               'oak_lowered': measured(lambda: engine.run('interface.batch', payload)),
               'oak_load_resolve_execute': measured(lambda: oak_run(folder / 'selected-oak', [('interface.batch', payload)]), 3),
               'compile': measured(lambda: compile_graph(folder / 'selected-oak'), 3)}
    runtime_bytes = Path(__file__).with_name('runtime.py').stat().st_size
    model_bytes = len(canonical_bytes(model))
    compiled_bytes = len(canonical_bytes(program))
    result = {'scores': scores, 'audits': audits,
              'export_checks': [read(directory / str(seed) / 'export-verification.json') for seed in SETTINGS['seeds']],
              'faults': faults(directory), 'timing_seconds_median': timings,
              'timing_scope': 'First ordinary final utterance, existing model; direct and lowered include per-call tensor decoding, native includes loading, resolving and validation. Five repetitions except native and compile: three. Not an agent effort or throughput benchmark.',
              'size_bytes': {'runtime_shared': runtime_bytes, 'python_model': model_bytes, 'lowered_program': compiled_bytes,
                             'python_runtime_plus_model': runtime_bytes + model_bytes,
                             'lowered_runtime_plus_program': runtime_bytes + compiled_bytes,
                             'canonical_oak': sum((folder / 'selected-oak' / name).stat().st_size for name in graph_hashes(folder / 'selected-oak'))},
              'coefficients': sum(int(np.prod(shape)) for shape in SHAPES.values()),
              'owner_coefficients': {group: sum(int(np.prod(SHAPES[name])) for name in names) for group, names in GROUPS.items()},
              'physical_proposers': 1, 'fresh_proposals': 1, 'agent_productivity_measured': False}
    save(directory / 'summary.json', result)
    print(json.dumps({key: value for key, value in result.items() if key not in ('audits', 'export_checks')}, indent=2))
    return result


if __name__ == '__main__':
    configure()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('audit', 'export', 'summary'))
    parser.add_argument('directory', type=Path)
    parser.add_argument('--seed', type=int, choices=SETTINGS['seeds'])
    args = parser.parse_args()
    if args.command == 'audit':
        audit_run(args.directory, args.seed)
    elif args.command == 'export':
        export_and_check(args.directory, args.seed)
    else:
        summarise(args.directory)
