"""Recompute scientific measurements and test isolated graph-derived deployments."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

from run import (EXPERIMENT, SEEDS, Case, Program, baseline, canonical_bytes, current, development,
                 graph_hashes, identity, join_parameters, read, read_cases, render_view, score, verify_freeze, write)
from graph import compile_graph, export_graph, oak_run
from operations import GROUPS, SHAPES
from runtime import encode_inputs, forward, load_record
import numpy as np

_DRIVER = '''import sys,json,builtins
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from inference import Program
blocked_root=sys.argv[1]
def audit(event,args):
    if event.startswith('socket.'):
        raise RuntimeError('network forbidden')
    if event=='open' and isinstance(args[0],str) and args[0].startswith(blocked_root):
        raise RuntimeError('repository access forbidden')
sys.addaudithook(audit)
original_import=builtins.__import__
def guarded(name,*args,**kwargs):
    if name.split('.')[0] in ('oak','torch','task','train','transformers','run','runtime','graph'):
        raise RuntimeError('nondeployment import forbidden')
    return original_import(name,*args,**kwargs)
builtins.__import__=guarded
model=json.loads(Path('program.json').read_text())
requests=json.loads(Path('requests.json').read_text())
answers=[]
runner=Program(model)
for request in requests:
    runner.reset()
    for event in request['history']:
        runner.run('interface.observe',{'TEXT':event})
    saved=json.loads(json.dumps(runner.snapshot()))
    runner=Program(model)
    runner.restore(saved)
    output=runner.run('interface.answer',{'QUESTIONS':[request['question']]})
    answers.append(output['REPLIES'][0])
print(json.dumps(answers))
'''


def cases_from(rows: list[dict]) -> list[Case]:
    return [Case(tuple(tuple(event) for event in c['events']), c['subject'], c['before']) for c in rows]


def audit_seed(run: Path, seed: int) -> dict:
    verify_freeze(run)
    closed = read(run / 'SELECTION_CLOSED.json')
    folder = run / str(seed)
    raw_cases, results = read(folder / 'final-cases.json'), read(folder / 'final.json')
    checks, maximum, count = [], 0., 0
    for arm, selection in closed['selected'][str(seed)].items():
        source = folder / selection['folder']
        if identity(graph_hashes(source)) != selection['identity']:
            raise AssertionError('changed selected graph')
        reference_weights = load_record(join_parameters(source))
        for name, group in raw_cases.items():
            cases = cases_from(group['cases'])
            rendered = [render_view(case, group['form']) for case in cases]
            events, queries = encode_inputs([r[0] for r in rendered], [r[1] for r in rendered])
            reference = forward(reference_weights, events, queries)
            stored = results[arm][name]
            error = float(np.max(np.abs(reference - stored['probabilities'])))
            maximum = max(maximum, error)
            expected = reference.argmax(1).tolist()
            if error > 1e-12 or expected != stored['predictions'] or stored['labels'] != [c.answer for c in cases]:
                raise AssertionError('original numerical implementation disagrees')
            recomputed = score(compile_graph(source), cases, group['form'])
            if canonical_bytes(recomputed) != canonical_bytes(stored):
                raise AssertionError('saved scientific metric differs')
            payload = {'HISTORIES': [r[0] for r in rendered[:4]], 'QUESTIONS': [r[1] for r in rendered[:4]]}
            output, _ = oak_run(source, [('interface.batch', payload)])
            np.testing.assert_allclose(output[0]['PROBABILITIES'], reference[:4], atol=1e-12, rtol=0)
            count += 4
    source = current(run, seed)
    output = folder / 'verified-export'
    export = export_graph(source, output)
    requests, expected = [], []
    for name, group in raw_cases.items():
        for case, prediction in zip(cases_from(group['cases']), results['agent'][name]['predictions'], strict=True):
            history, question = render_view(case, group['form'])
            requests.append({'history': history, 'question': question})
            from operations import ROOMS
            expected.append(ROOMS[prediction])
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        for name in ('program.json', 'inference.py'):
            (work / name).write_bytes((output / name).read_bytes())
        (work / 'driver.py').write_text(_DRIVER)
        (work / 'requests.json').write_bytes(canonical_bytes(requests))
        result = subprocess.run([sys.executable, '-I', str(work / 'driver.py'), str(EXPERIMENT.parents[1])], cwd=work,
            env={'PATH': os.environ.get('PATH', ''), 'OPENBLAS_NUM_THREADS': '1'},
            capture_output=True, text=True, check=True, timeout=40)
        if json.loads(result.stdout) != expected:
            raise AssertionError('isolated restored-state predictions differ')
    report = {'seed': seed, 'all_predictions_recomputed': True, 'original_numpy_max_error': maximum,
              'oak_samples': count, 'isolated_restored_predictions': len(requests), 'export': export}
    write(folder / 'audit.json', report)
    print(json.dumps(report, indent=2), flush=True)
    return report


def summary(run: Path) -> dict:
    verify_freeze(run)
    per_seed = {str(seed): read(run / str(seed) / 'final.json') for seed in SEEDS}
    means = {arm: {regime: {metric: float(np.mean([records[arm][regime][metric] for records in per_seed.values()]))
                           for metric in ('accuracy', 'loss')} for regime in per_seed[str(SEEDS[0])][arm]}
             for arm in per_seed[str(SEEDS[0])]}
    # Make the architecture comparison before interpreting any new teaching change.
    equivalence = []
    for seed in SEEDS:
        graph = run / str(seed) / 'baseline'
        assert join_parameters(graph) == baseline(seed)
        data = read_cases(run, seed)
        cases = data['ordinary'] + data['medium']
        rendered = [render_view(case, 0) for case in cases]
        events, questions = encode_inputs([r[0] for r in rendered], [r[1] for r in rendered])
        reference = forward(load_record(baseline(seed)), events, questions)
        predicted = Program(compile_graph(graph)).run('interface.batch', {'HISTORIES': [r[0] for r in rendered], 'QUESTIONS': [r[1] for r in rendered]})
        error = float(np.max(np.abs(reference - predicted['PROBABILITIES'])))
        if error > 1e-12:
            raise AssertionError('decomposition changed the initial function')
        equivalence.append({'seed': seed, 'cases': len(cases), 'max_error': error})
    audit = [read(run / str(seed) / 'audit.json') for seed in SEEDS]
    result = {'means': means, 'decomposition_checks': equivalence, 'audit': audit,
              'coefficients_per_owner': {group: sum(int(np.prod(SHAPES[name])) for name in names) for group, names in GROUPS.items()},
              'scope': 'three initial models and one shared-context proposer, one-token answers not conversation',
              'fresh_final_forms': [4, 5], 'known_previous_failure_form_now_taught': 3,
              'source_hashes': verify_freeze(run)['sources']}
    write(run / 'summary.json', result)
    print(json.dumps(means, indent=2), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('audit', 'summary'))
    parser.add_argument('directory', type=Path)
    parser.add_argument('--seed', type=int, choices=SEEDS)
    args = parser.parse_args()
    if args.command == 'summary': summary(args.directory)
    elif args.seed is None: parser.error('audit needs a seed')
    else: audit_seed(args.directory, args.seed)
