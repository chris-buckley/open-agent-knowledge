"""Re-execute the recorded module choice and audit provenance without new agent decisions."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import tarfile
import time
from typing import Any, Callable

import numpy as np

from run import (EXPERIMENT, SEEDS, SETTINGS, baseline, close, configure, controls,
                 current, datasets, development, evaluate_proposal, final, identity, initialise,
                 old_histories, propose, read, read_cases, render_view, source_hashes, verify_freeze, write)
from graph import (Proposal, compile_graph, export_graph, graph_hashes, join_parameters, oak_run,
                   validate_revision)
from operations import GROUPS, SHAPES, Program
from runtime import encode_inputs, forward, load_record
from task import Case
from verify import audit_seed, summary as summarise

DESTINATION = EXPERIMENT / 'results/modularity-run'
ARMS = ('baseline', 'ordinary', 'varied', 'agent')
REGIMES = ('ordinary', 'combination', 'long', 'unseen_a', 'unseen_b')


def _case(record: dict[str, Any]) -> Case:
    return Case(tuple(tuple(event) for event in record['events']), record['subject'], record['before'])


def _median(function: Callable[[], object], repeats: int = 5) -> float:
    function()
    durations = []
    for _ in range(repeats):
        start = time.perf_counter()
        function()
        durations.append(time.perf_counter() - start)
    return float(np.median(durations))


def audit_provenance(directory: Path) -> dict[str, Any]:
    """Check data separation, recorded decisions and actual scoped parameter changes."""
    frozen = verify_freeze(directory)
    closed = read(directory / 'SELECTION_CLOSED.json')
    old = old_histories()
    evidence = {}
    for seed in SEEDS:
        target = directory / str(seed)
        data = datasets(seed)
        stored_data = read_cases(directory, seed)
        if stored_data != data:
            raise AssertionError('saved training or development cases differ')
        if graph_hashes(target / 'baseline') != frozen['baseline_graphs'][str(seed)] or join_parameters(target / 'baseline') != baseline(seed):
            raise AssertionError('baseline differs from archived parameters')
        expected = {name: [asdict(case) for case in rows] for name, rows in data.items()}
        if frozen['data_identities'][str(seed)] != identity(expected):
            raise AssertionError('training or development identity differs')
        seen = set(old)
        counts = {}
        saved = read(target / 'final-cases.json')
        groups = {'teaching-' + name: rows for name, rows in data.items()}
        groups.update({'final-' + name: [_case(record) for record in group['cases']] for name, group in saved.items()})
        for label, group in groups.items():
            identities = [case.history_identity for case in group]
            if len(set(identities)) != len(group) or seen.intersection(identities):
                raise AssertionError('history overlap: ' + label)
            seen.update(identities)
            counts[label] = len(group)
        for arm in ARMS:
            selected = closed['selected'][str(seed)][arm]
            if identity(graph_hashes(target / selected['folder'])) != selected['identity']:
                raise AssertionError('selected graph drift')
        files = sorted((target / 'proposals').glob('*.json'))
        incumbent = target / 'baseline'
        decisions = []
        for file in files:
            proposal = read(file)
            observation = read(target / 'observations' / file.name)
            decision = read(target / 'decisions' / file.name)
            if identity(observation) != proposal['observation'] or identity(proposal) != decision['proposal']:
                raise AssertionError('proposal provenance mismatch')
            if not proposal['created_ns'] < decision['evaluated_ns'] < closed['closed_ns']:
                raise AssertionError('selection chronology differs')
            candidate = target / ('candidate-' + file.stem)
            policy = Proposal(proposal['baseline'], tuple(proposal['allowed_modules']), proposal['rationale'])
            boundary = validate_revision(incumbent, candidate, policy)
            if boundary != decision['boundary']:
                raise AssertionError('scoped revision evidence differs')
            before, after = development(incumbent, data), development(candidate, data)
            for label, scores in (('before', before), ('after', after)):
                if scores != decision[label]:
                    raise AssertionError('development metrics differ')
            accepted = (after['mean'] >= before['mean'] + SETTINGS['min_gain']
                        and all(after[key]['accuracy'] >= before[key]['accuracy'] - SETTINGS['max_regression']
                                for key in ('ordinary', 'reordered', 'medium')))
            if accepted != decision['accepted']:
                raise AssertionError('acceptance differs')
            if accepted:
                incumbent = candidate
            if incumbent.name != decision['incumbent']:
                raise AssertionError('incumbent selection differs')
            decisions.append({'origin': proposal['origin'], 'accepted': accepted,
                              'changed': boundary['changed'], 'unchanged': boundary['unchanged']})
        if current(directory, seed) != incumbent:
            raise AssertionError('current model differs')
        evidence[str(seed)] = {'disjoint_counts': counts, 'proposals': decisions}
    return {'source_hashes': source_hashes(), 'excluded_old_histories': len(old), 'per_seed': evidence,
            'registered_scientific_sources_match_freeze': True, 'case_separation': 'within each seed, including recovered previous-study histories'}


def measure_engineering(directory: Path) -> dict[str, Any]:
    """Measure one declared fixture, not a general speed or productivity benchmark."""
    seed = SEEDS[0]
    selected = read(directory / 'SELECTION_CLOSED.json')['selected'][str(seed)]['agent']['folder']
    node = directory / str(seed) / selected
    cases = [_case(record) for record in read(directory / str(seed) / 'final-cases.json')['ordinary']['cases'][:16]]
    histories, questions = zip(*(render_view(case, 0) for case in cases), strict=True)
    payload = {'HISTORIES': list(histories), 'QUESTIONS': list(questions)}
    joined = join_parameters(node)
    weights = load_record(joined)
    compiled = Program(compile_graph(node))

    def reference() -> np.ndarray:
        events, queries = encode_inputs(payload['HISTORIES'], payload['QUESTIONS'])
        return forward(weights, events, queries)

    timings = {'monolithic_numpy': _median(reference),
               'lowered_numpy': _median(lambda: compiled.run('interface.batch', payload)),
               'oak_with_load_resolution_and_validation': _median(lambda: oak_run(node, [('interface.batch', payload)])),
               'compile_once': _median(lambda: compile_graph(node))}
    from oak_io import export_node, write_node
    comparison = directory / 'size-comparison'
    comparison.mkdir(exist_ok=False)
    write_node(joined, comparison / 'monolithic.oak.md')
    old_export = export_node(comparison / 'monolithic.oak.md', comparison / 'monolithic-export')
    new_export = export_graph(node, comparison / 'modular-export')
    return {'fixture': 'selected seed 503, first 16 ordinary final cases, five timed repetitions after warm-up',
            'timing_seconds_median': timings,
            'scope': 'reference and lowered engines are loaded before timing; OAK timing includes loading, lowering, resolution and validation; not a pure dispatch comparison',
            'coefficients_by_owner': {group: sum(int(np.prod(SHAPES[name])) for name in names) for group, names in GROUPS.items()},
            'coefficient_count': sum(int(np.prod(shape)) for shape in SHAPES.values()),
            'oak_document_count': len(graph_hashes(node)),
            'monolithic_oak_bytes': (comparison / 'monolithic.oak.md').stat().st_size,
            'modular_oak_bytes': sum((node / name).stat().st_size for name in graph_hashes(node)),
            'monolithic_export_bytes': old_export['bytes'], 'modular_export_bytes': new_export['bytes'],
            'no_parameter_compression_claim': True, 'productivity_not_measured': True}


def replay(directory: Path) -> None:
    initialise(directory)
    for seed in SEEDS:
        controls(directory, seed)
        propose(directory, seed, ('encoder',), 'Replay the recorded seed-503 encoder-only varied-wording method.', 'replay')
        evaluate_proposal(directory, seed)
    close(directory)
    for seed in SEEDS:
        final(directory, seed)
        audit_seed(directory, seed)
    summarise(directory)
    audit(directory)


def audit(directory: Path) -> None:
    provenance = audit_provenance(directory)
    summary = read(directory / 'summary.json')
    targets = read(DESTINATION / 'expected.json')
    if targets['source_hashes'] != source_hashes():
        raise AssertionError('replay sources differ from local execution')
    for seed in SEEDS:
        final_record = read(directory / str(seed) / 'final.json')
        for arm in ARMS:
            for regime in REGIMES:
                actual = final_record[arm][regime]
                expected = targets['per_seed'][str(seed)][arm][regime]
                if identity(actual['predictions']) != expected['predictions_sha256']:
                    raise AssertionError('replay decisions differ')
                for metric in ('accuracy', 'loss'):
                    if abs(actual[metric] - expected[metric]) > 1e-9:
                        raise AssertionError('replay metric differs')
    evidence = {'provenance': provenance, 'engineering': measure_engineering(directory),
                'matches_local_prediction_hashes_and_metrics': True,
                'isolated_restored_predictions': sum(item['isolated_restored_predictions'] for item in summary['audit']),
                'oak_samples': sum(item['oak_samples'] for item in summary['audit']), 'maximum_probability_difference': max(item['original_numpy_max_error'] for item in summary['audit']),
                'fresh_agent_decisions': sum(p['origin'] == 'live' for s in provenance['per_seed'].values() for p in s['proposals'])}
    write(directory / 'evidence.json', evidence)
    print(json.dumps(evidence, indent=2), flush=True)


def package(directory: Path, destination: Path) -> None:
    evidence = read(directory / 'evidence.json')
    if not evidence['matches_local_prediction_hashes_and_metrics']:
        raise AssertionError('unverified evidence')
    destination.mkdir(parents=True, exist_ok=False)
    manifest = {path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(directory.rglob('*')) if path.is_file() and '__pycache__' not in path.parts}
    write(destination / 'manifest.json', manifest)
    with tarfile.open(destination / 'records.tar.xz', 'w:xz') as archive:
        for name in manifest:
            archive.add(directory / name, arcname=name, recursive=False)
    with tarfile.open(destination / 'records.tar.xz') as archive:
        for name, digest in manifest.items():
            stream = archive.extractfile(name)
            if stream is None or hashlib.sha256(stream.read()).hexdigest() != digest:
                raise AssertionError('archive member differs')
    write(destination / 'archive.json', {'sha256': hashlib.sha256((destination / 'records.tar.xz').read_bytes()).hexdigest(),
                                        'members': len(manifest), 'verified': True})
    write(destination / 'summary.json', read(directory / 'summary.json'))
    write(destination / 'evidence.json', evidence)


if __name__ == '__main__':
    configure()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('replay', 'audit', 'package'))
    parser.add_argument('directory', type=Path)
    parser.add_argument('--destination', type=Path)
    args = parser.parse_args()
    if args.command == 'replay':
        replay(args.directory)
    elif args.command == 'audit':
        audit(args.directory)
    elif args.destination is not None:
        package(args.directory, args.destination)
    else:
        parser.error('package requires --destination')
