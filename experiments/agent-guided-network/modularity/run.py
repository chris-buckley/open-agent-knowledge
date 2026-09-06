"""Staged modular learning with frozen sources and pre-evaluation agent proposals."""
from __future__ import annotations

import argparse
import copy
from dataclasses import asdict
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import tarfile
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(EXPERIMENT / 'meaning'))

import numpy as np
import torch
from torch.nn import functional as F
from oak import Constant, Node, render
from graph import Proposal, compile_graph, graph_hashes, join_parameters, validate_revision, write_graph
from operations import GROUPS, SHAPES, Program, canonical_bytes, identity
from runtime import encode_inputs
from task import Case, FORMS, generate_cases, render_case
from train import NAMES, configure, record_network, restore_network

SEEDS = (503, 509, 521)
PRIOR_SEEDS = (401, 409, 419)
NEW_FORMS = (*FORMS, 'the {o} from the {s} moved to the {d}', 'from the {s} to the {d} the {o} moved')
SETTINGS = {'seeds': SEEDS, 'prior_seeds': PRIOR_SEEDS, 'train': 1024, 'development': 128,
            'final': 256, 'steps': 300, 'batch': 48, 'rate': .003, 'agreement': .3,
            'min_gain': .01, 'max_regression': .03, 'max_proposals': 2, 'forms': NEW_FORMS}
ARCHIVE = EXPERIMENT / 'results/meaning-run/reproduced/records.tar.xz'
SOURCE_NAMES = ('operations.py', 'graph.py', 'run.py', 'tests.py', 'verify.py', 'PROTOCOL.md')


def read(path: Path) -> Any:
    return json.loads(path.read_text())


def write(path: Path, record: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(canonical_bytes(record))


def source_hashes() -> dict[str, str]:
    import hashlib
    files = [*(Path(__file__).with_name(name) for name in SOURCE_NAMES),
             *(EXPERIMENT / 'meaning' / name for name in ('runtime.py', 'task.py', 'train.py'))]
    return {str(path.relative_to(EXPERIMENT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}


def baseline(seed: int) -> dict:
    prior = dict(zip(SEEDS, PRIOR_SEEDS, strict=True)).get(seed, 401)
    with tarfile.open(ARCHIVE) as archive:
        return json.load(archive.extractfile(f'{prior}/agent.json'))


def old_histories() -> set[str]:
    seen: set[str] = set()
    for seed in PRIOR_SEEDS:
        train = generate_cases(seed * 100 + 1, 1024)
        short = generate_cases(seed * 100 + 2, 128, excluded={c.history_identity for c in train})
        medium = generate_cases(seed * 100 + 3, 128, regime='medium', excluded={c.history_identity for c in train + short})
        extra = generate_cases(seed * 100 + 4, 1024, regime='medium', excluded={c.history_identity for c in train + short + medium})
        seen.update(c.history_identity for c in train + short + medium + extra)
    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if all(key in value for key in ('events', 'subject', 'before')):
                seen.add(identity(value['events']))
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    with tarfile.open(ARCHIVE) as archive:
        for seed in PRIOR_SEEDS:
            visit(json.load(archive.extractfile(f'{seed}/final-cases.json')))
    return seen


def datasets(seed: int) -> dict[str, list[Case]]:
    seen = old_histories()
    result = {}
    for offset, (name, count, regime) in enumerate([
        ('ordinary_train', 512, 'ordinary'), ('medium_train', 512, 'medium'),
        ('ordinary', 128, 'ordinary'), ('medium', 128, 'medium')], 1):
        cases = generate_cases(seed * 100 + offset, count, regime=regime, excluded=seen)
        result[name] = cases
        seen.update(case.history_identity for case in cases)
    return result


def render_view(case: Case, form: int) -> tuple[list[str], str]:
    from operations import OBJECTS, ROOMS
    events = [NEW_FORMS[form].format(o=OBJECTS[o], s=ROOMS[s], d=ROOMS[d]) for o, s, d in case.events]
    return events, render_case(case, 0)[1]


def score(program: dict, cases: list[Case], form: int) -> dict:
    runner = Program(program)
    rendered = [render_view(case, form) for case in cases]
    predictions, losses, probabilities = [], [], []
    for start in range(0, len(cases), 64):
        rows = rendered[start:start + 64]
        output = runner.run('interface.batch', {'HISTORIES': [row[0] for row in rows], 'QUESTIONS': [row[1] for row in rows]})
        probability = output['PROBABILITIES']
        labels = [case.answer for case in cases[start:start + 64]]
        predictions.extend(probability.argmax(1).tolist())
        probabilities.extend(probability.tolist())
        losses.extend(-np.log(np.clip(probability[np.arange(len(labels)), labels], 1e-300, 1)))
    labels = [case.answer for case in cases]
    correct = np.asarray(predictions) == labels
    split = {}
    for name, flag in [('now', False), ('before', True)]:
        mask = np.array([case.before == flag for case in cases])
        split[name] = {'correct': int(correct[mask].sum()), 'count': int(mask.sum())}
    return {'accuracy': float(correct.mean()), 'loss': float(np.mean(losses)), 'predictions': predictions,
            'labels': labels, 'probabilities': probabilities, 'question_types': split}


def development(directory: Path, cases: dict[str, list[Case]]) -> dict:
    program = compile_graph(directory)
    scores = {}
    for name, kind, form in [('ordinary', 'ordinary', 0), ('reordered', 'ordinary', 3), ('medium', 'medium', 3)]:
        measured = score(program, cases[kind], form)
        scores[name] = {key: measured[key] for key in ('accuracy', 'loss')}
    scores['mean'] = float(np.mean([value['accuracy'] for value in scores.values()]))
    return scores


def fit(record: dict, cases: list[Case], groups: tuple[str, ...], forms: tuple[int, ...], seed: int) -> tuple[dict, dict]:
    network = restore_network(record).train()
    permitted = {NAMES[name] for group in groups for name in GROUPS[group]}
    for name, parameter in network.named_parameters():
        parameter.requires_grad_(name in permitted)
    parameters = [p for p in network.parameters() if p.requires_grad]
    optimiser = torch.optim.Adam(parameters, lr=SETTINGS['rate'])
    encoded = {}
    for form in forms:
        rendered = [render_view(case, form) for case in cases]
        events, queries = encode_inputs([row[0] for row in rendered], [row[1] for row in rendered])
        encoded[form] = (torch.from_numpy(events), torch.from_numpy(queries), torch.tensor([case.answer for case in cases]))
    generator = np.random.default_rng(seed)
    started = time.monotonic()
    for _ in range(SETTINGS['steps']):
        indices = generator.integers(len(cases), size=SETTINGS['batch'])
        a, b = generator.choice(forms, size=2, replace=len(forms) == 1)
        xa, qa, target = (tensor[indices] for tensor in encoded[int(a)])
        xb, qb, _ = (tensor[indices] for tensor in encoded[int(b)])
        logits_a, hidden_a = network(xa, qa)
        logits_b, hidden_b = network(xb, qb)
        agreement = (F.normalize(hidden_a, dim=1) - F.normalize(hidden_b, dim=1)).square().sum(1).mean()
        loss = (F.cross_entropy(logits_a, target) + F.cross_entropy(logits_b, target)) / 2 + SETTINGS['agreement'] * agreement
        optimiser.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(parameters, 5)
        optimiser.step()
    candidate = record_network(network)
    selected_names = {name for group in groups for name in GROUPS[group]}
    for name in record['weights']:
        if name not in selected_names:
            candidate['weights'][name] = copy.deepcopy(record['weights'][name])
    return candidate, {'steps': SETTINGS['steps'], 'batch': SETTINGS['batch'], 'views': 2,
        'trainable_coefficients': sum(int(np.prod(SHAPES[name])) for name in selected_names),
        'presentations': SETTINGS['steps'] * SETTINGS['batch'] * 2, 'groups': groups, 'forms': forms,
        'seconds': time.monotonic() - started, 'last_loss': float(loss.detach())}


def verify_freeze(run: Path) -> dict:
    frozen = read(run / 'freeze.json')
    if frozen['sources'] != source_hashes() or canonical_bytes(frozen['settings']) != canonical_bytes(SETTINGS):
        raise ValueError('scientific source or settings changed')
    return frozen


def initialise(run: Path) -> None:
    run.mkdir(parents=True, exist_ok=False)
    data = {str(seed): {name: [asdict(case) for case in rows] for name, rows in datasets(seed).items()} for seed in SEEDS}
    for seed in SEEDS:
        write_graph(baseline(seed), run / str(seed) / 'baseline')
        write(run / str(seed) / 'data.json', data[str(seed)])
    write(run / 'freeze.json', {'sources': source_hashes(), 'settings': SETTINGS,
        'baseline_graphs': {str(seed): graph_hashes(run / str(seed) / 'baseline') for seed in SEEDS},
        'data_identities': {key: identity(value) for key, value in data.items()},
        'excluded_history_count': len(old_histories()), 'protocol_commit': 'c4d808d5bd89265bc87ac108b67da373268617a2',
        'source_baseline': '17a96a8be4f7ef1c0fdd4bb90884be94feb97d92', 'created_ns': time.time_ns(),
        'environment': {name: importlib.metadata.version(name) for name in ('numpy', 'torch', 'pydantic', 'pydantic-settings')},
        'python': platform.python_version(), 'agent': 'one shared-context assistant', 'conversation_cost': None})


def read_cases(run: Path, seed: int) -> dict[str, list[Case]]:
    raw = read(run / str(seed) / 'data.json')
    if identity(raw) != verify_freeze(run)['data_identities'][str(seed)]:
        raise ValueError('training or development data changed')
    return {name: [Case(tuple(tuple(event) for event in case['events']), case['subject'], case['before']) for case in rows]
            for name, rows in raw.items()}


def controls(run: Path, seed: int) -> None:
    cases = read_cases(run, seed)
    if (run / 'SELECTION_CLOSED.json').exists():
        raise ValueError('selection is closed')
    base = run / str(seed) / 'baseline'
    before = development(base, cases)
    write(run / str(seed) / 'baseline-development.json', before)
    for name, forms in [('ordinary', (0,)), ('varied', (0, 1, 2, 3))]:
        candidate, resources = fit(join_parameters(base), cases['ordinary_train'] + cases['medium_train'], tuple(GROUPS), forms, seed)
        folder = run / str(seed) / name
        write_graph(candidate, folder)
        after = development(folder, cases)
        selected = name if after['mean'] > before['mean'] else 'baseline'
        write(run / str(seed) / (name + '-control.json'), {'selected': selected, 'development': after, 'resources': resources})
    print(json.dumps({'seed': seed, 'baseline': before,
                      'ordinary': read(run / str(seed) / 'ordinary-control.json')['development'],
                      'varied': read(run / str(seed) / 'varied-control.json')['development']}, indent=2), flush=True)


def current(run: Path, seed: int) -> Path:
    decisions = sorted((run / str(seed) / 'decisions').glob('*.json'))
    return run / str(seed) / (read(decisions[-1])['incumbent'] if decisions else 'baseline')


def propose(run: Path, seed: int, groups: tuple[str, ...], rationale: str, origin: str) -> dict:
    cases = read_cases(run, seed)
    folder = run / str(seed)
    proposals = list((folder / 'proposals').glob('*.json'))
    if (run / 'SELECTION_CLOSED.json').exists() or len(proposals) >= 2 or len(proposals) != len(list((folder / 'decisions').glob('*.json'))):
        raise ValueError('closed, exhausted or pending selection')
    if not groups or any(group not in GROUPS for group in groups):
        raise ValueError('unknown parameter owner')
    model = current(run, seed)
    observation = {'baseline': identity(graph_hashes(model)), 'development': development(model, cases)}
    index = f'{len(proposals) + 1:03}'
    proposal = {'baseline': observation['baseline'], 'allowed_modules': list(groups), 'rationale': rationale,
                'origin': origin, 'observation': identity(observation), 'created_ns': time.time_ns()}
    write(folder / 'observations' / (index + '.json'), observation)
    write(folder / 'proposals' / (index + '.json'), proposal)
    (folder / 'proposals' / (index + '.oak.md')).write_text(render(Node(constants=[Constant(id='proposal', value=[proposal])])), encoding='utf-8')
    print(json.dumps(observation, indent=2), flush=True)
    return proposal


def evaluate_proposal(run: Path, seed: int) -> dict:
    cases = read_cases(run, seed)
    if (run / 'SELECTION_CLOSED.json').exists():
        raise ValueError('selection is closed')
    folder = run / str(seed)
    proposal_file = sorted((folder / 'proposals').glob('*.json'))[-1]
    raw = read(proposal_file)
    observation = read(folder / 'observations' / proposal_file.name)
    if raw['observation'] != identity(observation) or (folder / 'decisions' / proposal_file.name).exists():
        raise ValueError('changed or already used evidence')
    incumbent = current(run, seed)
    proposal = Proposal(raw['baseline'], tuple(raw['allowed_modules']), raw['rationale'])
    if identity(graph_hashes(incumbent)) != proposal.baseline:
        raise ValueError('stale proposal before fitting')
    candidate, resources = fit(join_parameters(incumbent), cases['ordinary_train'] + cases['medium_train'],
                               proposal.allowed_modules, (0, 1, 2, 3), seed)
    candidate_name = 'candidate-' + proposal_file.stem
    write_graph(candidate, folder / candidate_name)
    boundary = validate_revision(incumbent, folder / candidate_name, proposal)
    before, after = observation['development'], development(folder / candidate_name, cases)
    accepted = after['mean'] >= before['mean'] + SETTINGS['min_gain'] and all(
        after[name]['accuracy'] >= before[name]['accuracy'] - SETTINGS['max_regression'] for name in ('ordinary', 'reordered', 'medium'))
    # Recheck the effect-producing boundary immediately before promotion.
    repeated = validate_revision(incumbent, folder / candidate_name, proposal)
    if repeated != boundary:
        raise ValueError('revision changed during evaluation')
    decision = {'accepted': bool(accepted), 'before': before, 'after': after, 'boundary': boundary,
                'resources': resources, 'proposal': identity(raw), 'evaluated_ns': time.time_ns(),
                'incumbent': candidate_name if accepted else incumbent.name}
    write(folder / 'decisions' / proposal_file.name, decision)
    print(json.dumps({'seed': seed, **{name: decision[name] for name in ('accepted', 'before', 'after')},
                      'changed': boundary['changed']}, indent=2), flush=True)
    return decision


def close(run: Path) -> None:
    verify_freeze(run)
    selected = {}
    for seed in SEEDS:
        folder = run / str(seed)
        if len(list((folder / 'proposals').glob('*.json'))) != len(list((folder / 'decisions').glob('*.json'))):
            raise ValueError('pending proposals')
        arms = {'baseline': 'baseline', 'agent': current(run, seed).name}
        arms.update({name: read(folder / (name + '-control.json'))['selected'] for name in ('ordinary', 'varied')})
        selected[str(seed)] = {arm: {'folder': name, 'identity': identity(graph_hashes(folder / name))} for arm, name in arms.items()}
    write(run / 'SELECTION_CLOSED.json', {'selected': selected, 'freeze': identity(read(run / 'freeze.json')), 'closed_ns': time.time_ns()})


def final(run: Path, seed: int) -> None:
    cases = read_cases(run, seed)
    closed = read(run / 'SELECTION_CLOSED.json')
    if closed['freeze'] != identity(read(run / 'freeze.json')):
        raise ValueError('selection identity changed')
    seen = old_histories() | {c.history_identity for rows in cases.values() for c in rows}
    tests = {}
    for offset, (name, regime, form) in enumerate([('ordinary', 'ordinary', 0), ('combination', 'combination', 0),
            ('long', 'long', 0), ('unseen_a', 'ordinary', 4), ('unseen_b', 'ordinary', 5)], 20):
        rows = generate_cases(seed * 100 + offset, 256, regime=regime, excluded=seen)
        seen.update(c.history_identity for c in rows)
        tests[name] = {'form': form, 'cases': [asdict(c) for c in rows]}
    folder = run / str(seed)
    write(folder / 'final-cases.json', tests)
    results = {}
    for arm, selection in closed['selected'][str(seed)].items():
        graph = folder / selection['folder']
        if identity(graph_hashes(graph)) != selection['identity']:
            raise ValueError('selected parameters changed')
        program = compile_graph(graph)
        results[arm] = {}
        for name, group in tests.items():
            rows = [Case(tuple(tuple(event) for event in c['events']), c['subject'], c['before']) for c in group['cases']]
            results[arm][name] = score(program, rows, group['form'])
    write(folder / 'final.json', results)
    print(json.dumps({arm: {name: round(record['accuracy'], 4) for name, record in groups.items()} for arm, groups in results.items()}, indent=2), flush=True)


def main() -> None:
    configure()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('init', 'controls', 'propose', 'evaluate', 'close', 'final'))
    parser.add_argument('directory', type=Path)
    parser.add_argument('--seed', type=int, choices=SEEDS)
    parser.add_argument('--groups', nargs='+', choices=tuple(GROUPS), default=['encoder'])
    parser.add_argument('--rationale', default='')
    parser.add_argument('--origin', choices=('live', 'replay'), default='replay')
    args = parser.parse_args()
    if args.command in ('controls', 'propose', 'evaluate', 'final') and args.seed is None:
        parser.error('this operation needs a seed')
    if args.command == 'init': initialise(args.directory)
    elif args.command == 'controls': controls(args.directory, args.seed)
    elif args.command == 'propose': propose(args.directory, args.seed, tuple(args.groups), args.rationale, args.origin)
    elif args.command == 'evaluate': evaluate_proposal(args.directory, args.seed)
    elif args.command == 'close': close(args.directory)
    else: final(args.directory, args.seed)


if __name__ == '__main__':
    main()
