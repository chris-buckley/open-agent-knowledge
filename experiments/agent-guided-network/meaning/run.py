"""Staged, hash-pinned study. Final sets are inaccessible until selection closes."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import numpy as np
from oak import Constant, Node, parse, render
from runtime import PROFILE, ROOMS, Session, canonical_bytes, encode_inputs, forward, load_record
from task import Case, direction_pairs, generate_cases, order_pairs, render_case
from train import Network, configure, evaluate, fit, record_network
from oak_io import export_node, oak_dialogue, write_node

SETTINGS = {'seeds': [401, 409, 419], 'train': 1024, 'development': 128, 'final': 512, 'pairs': 256,
            'steps': 400, 'batch': 48, 'rate': .003, 'agreement': .3, 'min_gain': .01,
            'max_regression': .03, 'max_proposals': 2, 'max_events': 32,
            'views': 2, 'width': 24, 'vocabulary': 22, 'answers': 6}
SOURCES = ('runtime.py', 'task.py', 'train.py', 'oak_io.py', 'run.py', 'tests.py', 'verify.py', 'study.oak.md', 'requirements.txt')


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def write(path: Path, record: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(canonical_bytes(record))


def identity(record: object) -> str:
    return hashlib.sha256(canonical_bytes(record)).hexdigest()


def source_hashes() -> dict[str, str]:
    return {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in SOURCES}


def verify_freeze(directory: Path) -> dict:
    freeze = read(directory / 'freeze.json')
    if freeze['sources'] != source_hashes() or freeze['settings'] != SETTINGS:
        raise ValueError('frozen source or settings changed')
    return freeze


def cases_for(seed: int) -> tuple[list[Case], list[Case], list[Case]]:
    training = generate_cases(seed * 100 + 1, SETTINGS['train'])
    excluded = {c.history_identity for c in training}
    short = generate_cases(seed * 100 + 2, SETTINGS['development'], excluded=excluded)
    medium = generate_cases(seed * 100 + 3, SETTINGS['development'], regime='medium', excluded=excluded | {c.history_identity for c in short})
    return training, short, medium


def development(record: dict, seed: int) -> dict:
    _, short, medium = cases_for(seed)
    scores = {}
    for name, cases, form in [('ordinary', short, 0), ('reworded', short, 2), ('medium', medium, 2)]:
        result = evaluate(record, cases, form)
        scores[name] = {key: result[key] for key in ('accuracy', 'loss')}
    scores['mean'] = float(np.mean([scores[k]['accuracy'] for k in ('ordinary', 'reworded', 'medium')]))
    return scores


def initialise(directory: Path) -> None:
    directory.mkdir(exist_ok=False, parents=True)
    datasets = {str(seed): [identity([asdict(c) for c in cases]) for cases in cases_for(seed)] for seed in SETTINGS['seeds']}
    write(directory / 'freeze.json', {'profile': PROFILE, 'settings': SETTINGS, 'sources': source_hashes(),
          'datasets': datasets, 'source_baseline': 'a96de31abb234ee41c0843bab079b41bfdeae973',
          'protocol_commit': '932ffd05a41babd1652b0169329cbbe8fe486713', 'python': platform.python_version(),
          'environment': {name: importlib.metadata.version(name) for name in ('numpy', 'torch', 'pydantic', 'pydantic-settings')},
          'created_unix_ns': time.time_ns(), 'prior_context_results': 'unverified and not reused'})


def train_seed(directory: Path, seed: int) -> None:
    verify_freeze(directory)
    if (directory / 'SELECTION_CLOSED.json').exists():
        raise ValueError('selection is closed')
    training, _, _ = cases_for(seed)
    target = directory / str(seed)
    target.mkdir(exist_ok=False)
    initial = record_network(Network(seed))
    baseline, cost = fit(initial, training, seed=seed, steps=SETTINGS['steps'], forms=(0,))
    write(target / 'initial.json', initial)
    write(target / 'baseline.json', baseline)
    records = {'baseline': {'cost': cost, 'development': development(baseline, seed)}}
    for name, forms, agreement in [('repeat', (0,), 0), ('wording', (0, 1, 2), 0), ('agreement', (0, 1, 2), .3)]:
        candidate, resources = fit(baseline, training, seed=seed + 1, steps=SETTINGS['steps'], forms=forms, agreement=agreement)
        before, after = development(baseline, seed), development(candidate, seed)
        selected = candidate if after['mean'] > before['mean'] else baseline
        write(target / (name + '.json'), selected)
        write(target / (name + '-candidate.json'), candidate)
        records[name] = {'cost': resources, 'development': development(selected, seed), 'candidate_development': after,
                         'selected_final_checkpoint': selected is candidate}
    write(target / 'training.json', records)
    print(json.dumps({name: record['development'] for name, record in records.items()}, indent=2), flush=True)


def current(directory: Path, seed: int) -> dict:
    files = sorted((directory / str(seed) / 'decisions').glob('*.json'))
    return read(directory / str(seed) / 'agreement.json') if not files else read(directory / str(seed) / read(files[-1])['incumbent_file'])


def observation(directory: Path, seed: int) -> dict:
    model = current(directory, seed)
    _, short, medium = cases_for(seed)
    evidence = {'model_sha256': identity(model), 'development': development(model, seed), 'errors': []}
    result = evaluate(model, medium, 2)
    for case, answer in zip(medium, result['predictions'], strict=True):
        if answer != case.answer and len(evidence['errors']) < 4:
            events, question = render_case(case, 2)
            evidence['errors'].append({'events': events, 'question': question, 'expected': ROOMS[case.answer], 'actual': ROOMS[answer]})
    return evidence


def propose(directory: Path, seed: int, mode: str, rationale: str, *, origin: str = 'live') -> Path:
    verify_freeze(directory)
    if (directory / 'SELECTION_CLOSED.json').exists():
        raise ValueError('selection is closed')
    folder = directory / str(seed)
    pending = sorted((folder / 'proposals').glob('*.json'))
    if len(pending) != len(list((folder / 'decisions').glob('*.json'))):
        raise ValueError('evaluate the pending proposal first')
    if len(pending) >= SETTINGS['max_proposals'] or mode not in ('weaker', 'stronger', 'longer'):
        raise ValueError('proposal outside budget or menu')
    observed = observation(directory, seed)
    index = f'{len(pending) + 1:03}'
    write(folder / 'observations' / (index + '.json'), observed)
    proposal = {'seed': seed, 'mode': mode, 'rationale': rationale, 'origin': origin,
                'model_sha256': observed['model_sha256'], 'observation_sha256': identity(observed),
                'steps': SETTINGS['steps'], 'before_evaluation_unix_ns': time.time_ns()}
    path = folder / 'proposals' / (index + '.json')
    write(path, proposal)
    path.with_suffix('.oak.md').write_text(render(Node(constants=[Constant(id='proposal', value=[proposal])])), encoding='utf-8')
    return path


def evaluate_proposal(directory: Path, seed: int) -> dict:
    verify_freeze(directory)
    if (directory / 'SELECTION_CLOSED.json').exists():
        raise ValueError('selection is closed')
    folder = directory / str(seed)
    path = sorted((folder / 'proposals').glob('*.json'))[-1]
    proposal = read(path)
    if (folder / 'decisions' / path.name).exists():
        raise ValueError('proposal already evaluated')
    observed = read(folder / 'observations' / path.name)
    incumbent = current(directory, seed)
    if identity(incumbent) != proposal['model_sha256'] or identity(observed) != proposal['observation_sha256']:
        raise ValueError('stale or changed proposal evidence')
    training, short, medium = cases_for(seed)
    strength = {'weaker': 0., 'stronger': 1., 'longer': .3}[proposal['mode']]
    if proposal['mode'] == 'longer':
        seen = {c.history_identity for c in [*training, *short, *medium]}
        training = training + generate_cases(seed * 100 + 4, SETTINGS['train'], regime='medium', excluded=seen)
    candidate, cost = fit(incumbent, training, seed=seed + int(path.stem) + 10, steps=SETTINGS['steps'], forms=(0, 1, 2), agreement=strength)
    before, after = observed['development'], development(candidate, seed)
    accepted = after['mean'] >= before['mean'] + SETTINGS['min_gain'] and all(
        after[k]['accuracy'] >= before[k]['accuracy'] - SETTINGS['max_regression'] for k in ('ordinary', 'reworded', 'medium'))
    selected = candidate if accepted else incumbent
    write(folder / ('candidate-' + path.stem + '.json'), candidate)
    model_name = 'incumbent-' + path.stem + '.json'
    write(folder / model_name, selected)
    decision = {'accepted': bool(accepted), 'before': before, 'after': after, 'resources': cost,
                'incumbent_file': model_name, 'selected_sha256': identity(selected), 'proposal_sha256': identity(proposal)}
    write(folder / 'decisions' / path.name, decision)
    return decision


def close_selection(directory: Path) -> dict:
    verify_freeze(directory)
    selected = {}
    for seed in SETTINGS['seeds']:
        folder = directory / str(seed)
        proposals = list((folder / 'proposals').glob('*.json'))
        decisions = list((folder / 'decisions').glob('*.json'))
        if len(proposals) != len(decisions):
            raise ValueError('unresolved proposals')
        agent = current(directory, seed)
        write(folder / 'agent.json', agent)
        # The continuation control receives the same additional step count, but only original histories.
        control = read(folder / 'agreement.json')
        control_costs = []
        for index in range(len(proposals)):
            candidate, cost = fit(control, cases_for(seed)[0], seed=seed + index + 11, steps=SETTINGS['steps'], forms=(0, 1, 2), agreement=.3)
            if development(candidate, seed)['mean'] > development(control, seed)['mean']:
                control = candidate
            control_costs.append(cost)
        write(folder / 'continuation.json', control)
        write(folder / 'continuation-cost.json', control_costs)
        selected[str(seed)] = {name: identity(read(folder / (name + '.json')))
                              for name in ('baseline', 'repeat', 'wording', 'agreement', 'agent', 'continuation')}
    record = {'selected': selected, 'freeze_sha256': identity(read(directory / 'freeze.json')), 'closed_unix_ns': time.time_ns()}
    write(directory / 'SELECTION_CLOSED.json', record)
    return record


def final_seed(directory: Path, seed: int) -> dict:
    verify_freeze(directory)
    closed = read(directory / 'SELECTION_CLOSED.json')
    if closed['freeze_sha256'] != identity(read(directory / 'freeze.json')):
        raise ValueError('changed freeze')
    excluded = {c.history_identity for group in cases_for(seed) for c in group}
    excluded.update(c.history_identity for c in generate_cases(seed * 100 + 4, SETTINGS['train'], regime='medium', excluded=excluded))
    sets = {}
    for index, regime in enumerate(('ordinary', 'combination', 'long')):
        sets[regime] = generate_cases(seed * 100 + 80 + index, SETTINGS['final'], regime=regime, excluded=excluded)
        excluded.update(c.history_identity for c in sets[regime])
    directions = direction_pairs(seed * 100 + 90, SETTINGS['pairs'], excluded=excluded)
    excluded.update(c.history_identity for pair in directions for c in pair)
    orders = order_pairs(seed * 100 + 91, SETTINGS['pairs'], excluded=excluded)
    folder = directory / str(seed)
    write(folder / 'final-cases.json', {'sets': {k: [asdict(c) for c in v] for k, v in sets.items()},
          'direction': [[asdict(c) for c in pair] for pair in directions], 'order': [[asdict(c) for c in pair] for pair in orders]})
    results = {}
    for name, expected in closed['selected'][str(seed)].items():
        record = read(folder / (name + '.json'))
        if identity(record) != expected:
            raise ValueError('selected weights changed')
        scores = {regime: evaluate(record, cases, 0) for regime, cases in sets.items()}
        scores['unseen_wording'] = evaluate(record, sets['ordinary'], 3)
        canonical = np.array(scores['ordinary']['predictions'])
        paraphrase = np.array(scores['unseen_wording']['predictions'])
        labels = np.array(scores['ordinary']['labels'])
        scores['same_meaning'] = {'both_correct': float(np.mean((canonical == labels) & (paraphrase == labels))),
                                  'agreement': float(np.mean(canonical == paraphrase))}
        for kind, pairs in [('direction', directions), ('order', orders)]:
            answer = evaluate(record, [c for pair in pairs for c in pair], 0)
            predictions = np.array(answer['predictions']).reshape(-1, 2)
            labels = np.array(answer['labels']).reshape(-1, 2)
            scores[kind] = {**answer, 'both_correct': float(np.mean(np.all(predictions == labels, axis=1))),
                           'different_answers': float(np.mean(predictions[:, 0] != predictions[:, 1]))}
        results[name] = scores
    write(folder / 'final.json', results)
    return {name: {regime: score.get('accuracy', score.get('both_correct')) for regime, score in results[name].items()} for name in results}


def main() -> None:
    configure()
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('study', 'init', 'train', 'observe', 'propose', 'evaluate', 'close', 'final', 'test'))
    parser.add_argument('directory', type=Path, nargs='?')
    parser.add_argument('--seed', type=int, default=401)
    parser.add_argument('--mode', choices=('weaker', 'stronger', 'longer'))
    parser.add_argument('--rationale', default='')
    parser.add_argument('--origin', choices=('live', 'replay'), default='live')
    args = parser.parse_args()
    if args.command == 'study':
        Path(__file__).with_name('study.oak.md').write_text(render(Node(constants=[Constant(id='profile', value=PROFILE), Constant(id='settings', value=SETTINGS)])))
        return
    if args.command == 'test':
        import unittest
        import tests
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
        raise SystemExit(0 if result.wasSuccessful() else 1)
    if args.directory is None:
        parser.error('directory is required')
    directory = args.directory
    match args.command:
        case 'init': initialise(directory)
        case 'train': train_seed(directory, args.seed)
        case 'observe': print(json.dumps(observation(directory, args.seed), indent=2))
        case 'propose': print(propose(directory, args.seed, args.mode, args.rationale, origin=args.origin))
        case 'evaluate': print(json.dumps(evaluate_proposal(directory, args.seed), indent=2))
        case 'close': print(json.dumps(close_selection(directory), indent=2))
        case 'final': print(json.dumps(final_seed(directory, args.seed), indent=2))


if __name__ == '__main__':
    main()
