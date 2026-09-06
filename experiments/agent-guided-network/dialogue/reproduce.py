"""Repeat the recorded method; distinguish exact replay from cross-environment replication."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from run import (SETTINGS, apply, block, close, control, final, initialise, propose, read,
                 source_hashes, identity)
from train import configure
from audit import audit_run, export_and_check, summarise

RESULTS = Path(__file__).resolve().parents[1] / 'results/dialogue-run'


def replay(directory: Path, *, replication: bool = False) -> None:
    expected = read(RESULTS / 'expected.json')
    if source_hashes() != expected['sources']:
        raise AssertionError('scientific source differs from live execution')
    live = read(RESULTS / 'live-session.json')
    configure()
    initialise(directory)
    frozen = read(directory / 'freeze.json')
    if frozen['data'] != live['freeze']['data'] or frozen['settings'] != live['freeze']['settings']:
        raise AssertionError('data or scientific settings differ from live execution')
    for seed in SETTINGS['seeds']:
        for number in range(1, SETTINGS['blocks'] + 1):
            block(directory, seed, number)
    method = live['proposal']
    propose(directory, tuple(method['groups']), method['lesson'], method['rationale'])
    record = read(directory / 'proposal.json')
    record.update(execution_origin='numerical re-execution of the committed live method', fresh_agent_decisions=0)
    (directory / 'proposal.json').write_text(json.dumps(record, sort_keys=True, separators=(',', ':')))
    for seed in SETTINGS['seeds']:
        for representation in ('oak', 'python'):
            apply(directory, seed, representation=representation)
        control(directory, seed)
    close(directory)
    for seed in SETTINGS['seeds']:
        final(directory, seed)
    comparisons = {}
    for seed in SETTINGS['seeds']:
        audit_run(directory, seed)
        export_and_check(directory, seed)
        actual = identity(read(directory / str(seed) / 'final.json'))
        target = expected['final_result_hashes'][str(seed)]
        comparisons[str(seed)] = {'actual': actual, 'local_expected': target, 'identical': actual == target}
    evidence = {'fresh_agent_decisions': 0, 'mode': 'cross-environment replication' if replication else 'strict replay',
         'matches_live_final_result_hashes': all(row['identical'] for row in comparisons.values()),
         'result_comparison': comparisons, 'scientific_sources': source_hashes(),
         'same_data_and_settings_as_live': True, 'local_environment': live['freeze']['environment'],
         'current_environment': frozen['environment'],
         'boundary': 'All within-run data, decision, OAK/Python and export checks remain strict. A replication is not claimed to reproduce local checkpoints.'}
    (directory / 'replay.json').write_text(json.dumps(evidence, indent=2))
    summary = summarise(directory)
    summary.update(fresh_proposals=0, recorded_live_proposals=1, execution_origin=evidence['mode'], reproduction=evidence)
    (directory / 'summary.json').write_text(json.dumps(summary, sort_keys=True, separators=(',', ':')))
    if not replication and not evidence['matches_live_final_result_hashes']:
        raise AssertionError('replayed predictions or aggregate metrics differ from live execution; audit retained, exact replay failed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--replication', action='store_true', help='Record environment-dependent retraining as a separate run, never as exact replay.')
    args = parser.parse_args()
    replay(args.directory, replication=args.replication)
