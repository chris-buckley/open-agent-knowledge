"""Reproduce recorded teaching choices and independently verify the numerical evidence."""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import tarfile
import time

import numpy as np

from run import (SETTINGS, cases_for, close_selection, evaluate_proposal, final_seed, identity,
                 initialise, propose, read, source_hashes, train_seed, verify_freeze, write)
from runtime import ROOMS, SHAPES, encode_inputs, forward, load_record
from task import Case, generate_cases, render_case
from train import configure
from verify import verify_model

SOURCE_COMMIT = '7e2ef857f16978492d00a4790cb960e323b154ff'
ARMS = ('baseline', 'repeat', 'wording', 'agreement', 'agent', 'continuation')
REGIMES = ('ordinary', 'combination', 'long', 'unseen_wording')
REPLAY_MODES = ('longer',)
TOLERANCE = 1e-10


def replay_study(directory: Path) -> None:
    """Replay one recorded longer-history choice, not a fresh agent session."""
    initialise(directory)
    write(directory / 'resumption.json', {
        'source_commit': SOURCE_COMMIT,
        'execution': 'numerical replay of the recorded resumption choice',
        'fresh_agent_decisions': 0,
        'prior_unverified_aggregates_exposed': True,
        'independent_blinded_trial': False,
    })
    for seed in SETTINGS['seeds']:
        train_seed(directory, seed)
        for mode in REPLAY_MODES:
            propose(directory, seed, mode,
                    'Replay the live resumption choice: mix longer histories while retaining original examples.',
                    origin='replay')
            print(json.dumps(evaluate_proposal(directory, seed)), flush=True)
    close_selection(directory)
    for seed in SETTINGS['seeds']:
        print(json.dumps(final_seed(directory, seed)), flush=True)


def _case(record: dict) -> Case:
    return Case(tuple(tuple(event) for event in record['events']), record['subject'], record['before'])


def _predict(record: dict, cases: list[Case], form: int) -> tuple[np.ndarray, float]:
    weights = load_record(record)
    predictions, losses = [], []
    for start in range(0, len(cases), 128):
        batch = cases[start:start + 128]
        rendered = [render_case(case, form) for case in batch]
        events, questions = encode_inputs([row[0] for row in rendered], [row[1] for row in rendered])
        probabilities = forward(weights, events, questions)
        labels = np.array([case.answer for case in batch])
        predictions.extend(probabilities.argmax(-1).tolist())
        losses.extend((-np.log(probabilities[np.arange(len(batch)), labels])).tolist())
    return np.array(predictions), float(np.mean(losses))


def _check_score(record: dict, cases: list[Case], form: int, saved: dict) -> dict:
    labels = np.array([case.answer for case in cases])
    predictions, loss = _predict(record, cases, form)
    accuracy = float(np.mean(predictions == labels))
    if not np.array_equal(labels, saved['labels']) or not np.array_equal(predictions, saved['predictions']):
        raise AssertionError('saved labels or predictions do not reproduce')
    if abs(loss - saved['loss']) > TOLERANCE or accuracy != saved['accuracy']:
        raise AssertionError('saved metrics do not reproduce')
    return {'accuracy': accuracy, 'loss': loss}


def _check_splits(directory: Path, seed: int, sets: dict, pairs: dict) -> None:
    training, short, medium = cases_for(seed)
    expected = [identity([asdict(case) for case in group]) for group in (training, short, medium)]
    if expected != read(directory / 'freeze.json')['datasets'][str(seed)]:
        raise AssertionError('training or development identities changed')
    seen = {case.history_identity for group in (training, short, medium) for case in group}
    extra = generate_cases(seed * 100 + 4, SETTINGS['train'], regime='medium', excluded=seen)
    seen.update(case.history_identity for case in extra)
    groups = [*sets.values(), *([case for pair in group for case in pair] for group in pairs.values())]
    for group in groups:
        identities = {case.history_identity for case in group}
        if len(identities) != len(group) or seen & identities:
            raise AssertionError('duplicate or leaked history')
        seen.update(identities)
    for left, right in pairs['direction']:
        a, q = render_case(left, 0)
        b, r = render_case(right, 0)
        if Counter(' '.join(a + [q]).split()) != Counter(' '.join(b + [r]).split()) or left.answer == right.answer:
            raise AssertionError('invalid word-multiset contrast')
    for left, right in pairs['order']:
        if sorted(left.events) != sorted(right.events) or left.answer == right.answer:
            raise AssertionError('invalid event-order contrast')


def audit_study(directory: Path) -> dict:
    """Recompute all scores and verify selected exports without editing the study."""
    verify_freeze(directory)
    closed = read(directory / 'SELECTION_CLOSED.json')
    if closed['freeze_sha256'] != identity(read(directory / 'freeze.json')):
        raise AssertionError('selection does not identify this freeze')
    summaries, checks = {}, []
    live_count, replay_count = 0, 0
    for seed in SETTINGS['seeds']:
        folder = directory / str(seed)
        raw = read(folder / 'final-cases.json')
        final = read(folder / 'final.json')
        sets = {name: [_case(case) for case in cases] for name, cases in raw['sets'].items()}
        pairs = {name: [[_case(case) for case in pair] for pair in raw[name]] for name in ('direction', 'order')}
        _check_splits(directory, seed, sets, pairs)
        summaries[str(seed)] = {}
        for proposal_file in sorted((folder / 'proposals').glob('*.json')):
            proposal = read(proposal_file)
            decision = read(folder / 'decisions' / proposal_file.name)
            observation = read(folder / 'observations' / proposal_file.name)
            if identity(proposal) != decision['proposal_sha256'] or identity(observation) != proposal['observation_sha256']:
                raise AssertionError('proposal evidence changed')
            if proposal['before_evaluation_unix_ns'] >= closed['closed_unix_ns']:
                raise AssertionError('proposal occurred after selection closed')
            live_count += proposal['origin'] == 'live'
            replay_count += proposal['origin'] == 'replay'
        for arm in ARMS:
            model = read(folder / (arm + '.json'))
            if identity(model) != closed['selected'][str(seed)][arm]:
                raise AssertionError('selected model changed')
            summary = {}
            for regime in REGIMES:
                cases = sets['ordinary' if regime == 'unseen_wording' else regime]
                form = 3 if regime == 'unseen_wording' else 0
                summary[regime] = _check_score(model, cases, form, final[arm][regime])
                if arm == 'agent':
                    destination = directory / 'verification' / str(seed) / regime
                    checks.append(verify_model(model, cases, destination, form=form))
            for name, group in pairs.items():
                cases = [case for pair in group for case in pair]
                summary[name] = _check_score(model, cases, 0, final[arm][name])
                predictions = np.array(final[arm][name]['predictions']).reshape(-1, 2)
                labels = np.array(final[arm][name]['labels']).reshape(-1, 2)
                both = float(np.mean(np.all(predictions == labels, axis=1)))
                different = float(np.mean(predictions[:, 0] != predictions[:, 1]))
                if both != final[arm][name]['both_correct'] or different != final[arm][name]['different_answers']:
                    raise AssertionError('paired metric mismatch')
                summary[name]['both_correct'] = both
            a = np.array(final[arm]['ordinary']['predictions'])
            b = np.array(final[arm]['unseen_wording']['predictions'])
            labels = np.array(final[arm]['ordinary']['labels'])
            same = {'both_correct': float(np.mean((a == labels) & (b == labels))),
                    'agreement': float(np.mean(a == b))}
            if same != final[arm]['same_meaning']:
                raise AssertionError('same-meaning metric mismatch')
            summary['same_meaning'] = same
            predictions = np.array(final[arm]['combination']['predictions'])
            labels = np.array(final[arm]['combination']['labels'])
            before = np.array([case.before for case in sets['combination']])
            summary['combination_by_question'] = {
                name: {'correct': int(np.sum(predictions[mask] == labels[mask])), 'count': int(np.sum(mask))}
                for name, mask in [('before', before), ('now', ~before)]}
            summaries[str(seed)][arm] = summary
        print('Verified raw cases, metrics, OAK and isolated state restore:', seed, flush=True)
    means = {
        arm: {regime: {metric: float(np.mean([summaries[str(seed)][arm][regime][metric]
                                            for seed in SETTINGS['seeds']]))
                       for metric in summaries[str(SETTINGS['seeds'][0])][arm][regime]}
              for regime in (*REGIMES, 'direction', 'order', 'same_meaning')}
        for arm in ARMS}
    result = {'source_commit': SOURCE_COMMIT, 'scientific_sources': source_hashes(),
              'means': means, 'per_seed': summaries,
              'fresh_agent_proposals_in_this_run': live_count, 'replay_proposals_in_this_run': replay_count,
              'stored_coefficients': sum(int(np.prod(shape)) for shape in SHAPES.values()),
              'export_checks': checks,
              'isolated_restored_predictions': sum(check['isolated_restored_state_cases'] for check in checks),
              'oak_serialised_state_samples': sum(check['oak_serialised_state_cases'] for check in checks),
              'maximum_torch_numpy_difference': max(check['torch_numpy_max_error'] for check in checks),
              'all_saved_metrics_recomputed': True, 'disjoint_histories_checked': True,
              'scope': 'one-token six-choice location answers, not conversation; prior aggregates were exposed',
              'audited_unix_ns': time.time_ns()}
    write(directory / 'verified-summary.json', result)
    return result


def package_evidence(directory: Path, destination: Path) -> None:
    """Publish raw records and source identity only after a successful audit."""
    summary = read(directory / 'verified-summary.json')
    if not summary['all_saved_metrics_recomputed']:
        raise ValueError('unverified evidence')
    destination.mkdir(parents=True, exist_ok=False)
    manifest = {path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(directory.rglob('*')) if path.is_file()}
    write(destination / 'manifest.json', manifest)
    write(destination / 'summary.json', summary)
    with tarfile.open(destination / 'records.tar.xz', 'w:xz') as archive:
        for name in manifest:
            archive.add(directory / name, arcname=name, recursive=False)
    with tarfile.open(destination / 'records.tar.xz') as archive:
        for name, digest in manifest.items():
            extracted = archive.extractfile(name)
            if extracted is None or hashlib.sha256(extracted.read()).hexdigest() != digest:
                raise AssertionError('evidence archive failed verification')
    write(destination / 'archive.json', {
        'sha256': hashlib.sha256((destination / 'records.tar.xz').read_bytes()).hexdigest(),
        'size_bytes': (destination / 'records.tar.xz').stat().st_size,
        'member_count': len(manifest), 'verified_member_hashes': True,
        'source_commit': SOURCE_COMMIT,
    })


def main() -> None:
    configure()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('replay', 'audit', 'package'))
    parser.add_argument('directory', type=Path)
    parser.add_argument('--destination', type=Path)
    args = parser.parse_args()
    if args.command == 'replay':
        replay_study(args.directory)
        audit_study(args.directory)
    elif args.command == 'audit':
        audit_study(args.directory)
    elif args.destination is None:
        parser.error('package requires --destination')
    else:
        package_evidence(args.directory, args.destination)


if __name__ == '__main__':
    main()
