"""Staged dialogue study: freeze, fit, propose, close, test, and audit."""
from __future__ import annotations

import argparse
import copy
from dataclasses import asdict
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from evaluate import evaluate, score_summary
from graph import Revision, join_parameters, validate_oak_revision, validate_python_revision, write_graph
from runtime import GROUPS, MAX_INPUT, MAX_REPLY, SHAPES, VOCAB, canonical_bytes, identity
from task import Episode, generate, records
from train import Network, configure, fit, model_record

SETTINGS = {'seeds': [601, 607], 'training_episodes': 2048, 'development_episodes': 64,
            'final_episodes': 128, 'blocks': 4, 'block_steps': 300, 'proposal_steps': 300,
            'batch': 48, 'rate': 0.003, 'min_gain': 0.01, 'max_regression': 0.03,
            'width': 48, 'max_input': MAX_INPUT, 'max_reply': MAX_REPLY, 'vocabulary': len(VOCAB)}
SCIENTIFIC_FILES = ('runtime.py', 'graph.py', 'task.py', 'train.py', 'evaluate.py', 'run.py', 'tests.py')


def read(path: Path) -> Any:
    return json.loads(path.read_text())


def write(path: Path, record: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(canonical_bytes(record))


def source_hashes() -> dict[str, str]:
    return {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in SCIENTIFIC_FILES}


def verify(directory: Path, *, selection: bool = False) -> dict[str, Any]:
    frozen = read(directory / 'freeze.json')
    if frozen['sources'] != source_hashes() or frozen['settings'] != SETTINGS:
        raise ValueError('source or settings changed after freeze')
    if selection and (directory / 'SELECTION_CLOSED.json').exists():
        raise ValueError('model selection is closed')
    return frozen


def episodes(raw: list[dict[str, Any]]) -> list[Episode]:
    return [Episode(row['key'], tuple(row['users']), tuple(row['answers']), tuple(row['kinds'])) for row in raw]


def reword(rows: list[Episode]) -> list[Episode]:
    """Teaching-only paraphrases of the same latent episodes, with unchanged answers."""
    pattern = r'The (\w+) moved from the (\w+) to the (\w+)\.'
    return [Episode(row.key, tuple(re.sub(pattern, r'The \1 went to the \3 from the \2.', text) for text in row.users),
                    row.answers, row.kinds) for row in rows]


def dataset(directory: Path, seed: int) -> dict[str, list[Episode]]:
    stored = read(directory / str(seed) / 'data.json')
    return {name: episodes(rows) for name, rows in stored.items()}


def development(record: dict[str, Any], data: dict[str, list[Episode]]) -> dict[str, Any]:
    scores = {name: score_summary(evaluate(record, data[name])) for name in ('ordinary', 'varied')}
    scores['mean'] = sum(scores[name]['reply_accuracy'] for name in ('ordinary', 'varied')) / 2
    return scores


def initialise(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=False)
    seen: set[str] = set()
    identities = {}
    for seed in SETTINGS['seeds']:
        training = generate(seed * 100 + 1, SETTINGS['training_episodes'], excluded=seen)
        seen.update(row.key for row in training)
        ordinary = generate(seed * 100 + 2, SETTINGS['development_episodes'], excluded=seen)
        seen.update(row.key for row in ordinary)
        distinct = generate(seed * 100 + 3, SETTINGS['development_episodes'], excluded=seen)
        seen.update(row.key for row in distinct)
        stored = {'training': records(training), 'ordinary': records(ordinary), 'varied': records(reword(distinct))}
        write(directory / str(seed) / 'data.json', stored)
        write(directory / str(seed) / 'initial.json', model_record(Network(seed)))
        identities[str(seed)] = identity(stored)
    write(directory / 'freeze.json', {'sources': source_hashes(), 'settings': SETTINGS, 'data': identities,
          'created_ns': time.time_ns(), 'python': sys.version, 'baseline': '58c37dec3f71355eba18ee933e522e9d18f9acdd',
          'environment': {name: importlib.metadata.version(name) for name in ('numpy', 'torch', 'pydantic', 'pydantic-settings')}})


def block(directory: Path, seed: int, number: int) -> None:
    verify(directory, selection=True)
    if not 1 <= number <= SETTINGS['blocks']:
        raise ValueError('invalid training block')
    folder = directory / str(seed)
    before = read(folder / ('initial.json' if number == 1 else f'block-{number-1}.json'))
    data = dataset(directory, seed)
    model, costs = fit(before, data['training'], seed=seed + number, steps=SETTINGS['block_steps'])
    scores = development(model, data)
    write(folder / f'block-{number}.json', model)
    write(folder / f'block-{number}-scores.json', {'cost': costs, 'development': scores})
    if number == SETTINGS['blocks']:
        best = max(range(1, number + 1), key=lambda n: read(folder / f'block-{n}-scores.json')['development']['mean'])
        baseline = read(folder / f'block-{best}.json')
        write(folder / 'baseline.json', baseline)
        write_graph(baseline, folder / 'baseline-oak')
        write(folder / 'baseline-selection.json', {'block': best, 'identity': identity(baseline)})
    print(json.dumps({'seed': seed, 'block': number, 'seconds': costs['seconds'], 'development': scores}), flush=True)


def propose(directory: Path, groups: tuple[str, ...], lesson: str, rationale: str) -> None:
    verify(directory, selection=True)
    if lesson not in ('ordinary', 'varied') or not groups or not set(groups) <= set(GROUPS):
        raise ValueError('invalid proposal')
    seed = SETTINGS['seeds'][0]
    baseline = read(directory / str(seed) / 'baseline.json')
    observation = development(baseline, dataset(directory, seed))
    write(directory / 'proposal.json', {'groups': groups, 'lesson': lesson, 'rationale': rationale,
          'observation': observation, 'baseline': identity(baseline), 'created_ns': time.time_ns(),
          'physical_proposers': 1, 'live_seed': seed, 'later_seed_origin': 'numerical replay'})


def apply(directory: Path, seed: int, *, representation: str) -> None:
    verify(directory, selection=True)
    folder, proposal = directory / str(seed), read(directory / 'proposal.json')
    baseline = (join_parameters(folder / 'baseline-oak') if representation == 'oak' else read(folder / 'baseline.json'))
    if seed == SETTINGS['seeds'][0] and identity(baseline) != proposal['baseline']:
        raise ValueError('stale live proposal')
    data = dataset(directory, seed)
    teaching = data['training'] if proposal['lesson'] == 'ordinary' else data['training'] + reword(data['training'])
    model, cost = fit(baseline, teaching, seed=seed + 100, steps=SETTINGS['proposal_steps'], groups=tuple(proposal['groups']))
    revision = Revision(identity(baseline), tuple(proposal['groups']))
    changed = validate_python_revision(baseline, model, revision)
    if representation == 'oak':
        write_graph(model, folder / 'candidate-oak')
        assert validate_oak_revision(folder / 'baseline-oak', folder / 'candidate-oak', revision) == changed
    scores, before = development(model, data), development(baseline, data)
    accepted = (scores['mean'] >= before['mean'] + SETTINGS['min_gain'] and
                all(scores[name]['reply_accuracy'] >= before[name]['reply_accuracy'] - SETTINGS['max_regression'] for name in ('ordinary', 'varied')))
    write(folder / f'candidate-{representation}.json', model)
    write(folder / f'decision-{representation}.json', {'before': before, 'after': scores, 'accepted': accepted,
        'changed': changed, 'cost': cost, 'evaluated_ns': time.time_ns(), 'candidate': identity(model)})
    print(json.dumps({'seed': seed, 'representation': representation, 'accepted': accepted, 'scores': scores}), flush=True)


def control(directory: Path, seed: int) -> None:
    verify(directory, selection=True)
    folder = directory / str(seed)
    baseline = read(folder / 'baseline.json')
    data = dataset(directory, seed)
    model, cost = fit(baseline, data['training'], seed=seed + 100, steps=SETTINGS['proposal_steps'])
    before, after = development(baseline, data), development(model, data)
    selected = model if after['mean'] > before['mean'] else baseline
    write(folder / 'ordinary-candidate.json', model)
    write(folder / 'ordinary.json', selected)
    write(folder / 'ordinary-scores.json', {'cost': cost, 'before': before, 'after': after, 'selected': identity(selected)})
    print(json.dumps({'seed': seed, 'ordinary': after}), flush=True)


def close(directory: Path) -> None:
    verify(directory, selection=True)
    selected = {}
    for seed in SETTINGS['seeds']:
        folder = directory / str(seed)
        oak, python = read(folder / 'candidate-oak.json'), read(folder / 'candidate-python.json')
        decision = read(folder / 'decision-oak.json')
        if oak != python or decision['accepted'] != read(folder / 'decision-python.json')['accepted']:
            raise ValueError('matched representation training differs')
        model = oak if decision['accepted'] else read(folder / 'baseline.json')
        write(folder / 'selected.json', model)
        write_graph(model, folder / 'selected-oak')
        selected[str(seed)] = {name: identity(read(folder / (name + '.json'))) for name in ('baseline', 'ordinary', 'selected')}
    write(directory / 'SELECTION_CLOSED.json', {'selected': selected, 'closed_ns': time.time_ns(), 'proposal': identity(read(directory / 'proposal.json'))})


def final(directory: Path, seed: int) -> None:
    verify(directory)
    closed = read(directory / 'SELECTION_CLOSED.json')
    folder = directory / str(seed)
    excluded = {row.key for other_seed in SETTINGS['seeds'] for group in dataset(directory, other_seed).values() for row in group}
    for other_seed in SETTINGS['seeds']:
        path = directory / str(other_seed) / 'final-cases.json'
        if path.exists():
            excluded.update(row['key'] for group in read(path).values() for row in group)
    sets = {}
    for index, regime in enumerate(('ordinary', 'combination', 'long', 'wording')):
        rows = generate(seed * 100 + 50 + index, SETTINGS['final_episodes'], regime=regime, excluded=excluded)
        excluded.update(row.key for row in rows)
        sets[regime] = rows
    write(folder / 'final-cases.json', {name: records(rows) for name, rows in sets.items()})
    result = {}
    for arm in ('baseline', 'ordinary', 'selected'):
        model = read(folder / (arm + '.json'))
        if identity(model) != closed['selected'][str(seed)][arm]:
            raise ValueError('selected weights changed')
        result[arm] = {name: evaluate(model, rows) for name, rows in sets.items()}
    result['without_history'] = evaluate(read(folder / 'selected.json'), sets['ordinary'], erase_history=True)
    write(folder / 'final.json', result)
    print(json.dumps({arm: {name: score_summary(score) for name, score in scores.items()} for arm, scores in result.items() if arm != 'without_history'}), flush=True)


def main() -> None:
    configure()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('init', 'block', 'propose', 'apply', 'control', 'close', 'final'))
    parser.add_argument('directory', type=Path)
    parser.add_argument('--seed', type=int, choices=SETTINGS['seeds'])
    parser.add_argument('--block', type=int)
    parser.add_argument('--groups', nargs='+', choices=tuple(GROUPS))
    parser.add_argument('--lesson', choices=('ordinary', 'varied'))
    parser.add_argument('--rationale')
    parser.add_argument('--representation', choices=('oak', 'python'))
    args = parser.parse_args()
    if args.command == 'init':
        initialise(args.directory)
    elif args.command == 'block':
        block(args.directory, args.seed, args.block)
    elif args.command == 'propose':
        propose(args.directory, tuple(args.groups), args.lesson, args.rationale)
    elif args.command == 'apply':
        apply(args.directory, args.seed, representation=args.representation)
    elif args.command == 'control':
        control(args.directory, args.seed)
    elif args.command == 'close':
        close(args.directory)
    else:
        final(args.directory, args.seed)


if __name__ == '__main__':
    main()
