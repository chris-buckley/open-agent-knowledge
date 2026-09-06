"""Re-execute a committed teaching choice; this script makes no new agent decisions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from run import (SETTINGS, apply, block, close, control, final, initialise, propose, read,
                 source_hashes, identity)
from train import configure
from audit import audit_run, export_and_check, summarise

RESULTS = Path(__file__).resolve().parents[1] / 'results/dialogue-run'


def replay(directory: Path) -> None:
    expected = read(RESULTS / 'expected.json')
    if source_hashes() != expected['sources']:
        raise AssertionError('scientific source differs from live execution')
    live = read(RESULTS / 'live-session.json')
    configure()
    initialise(directory)
    for seed in SETTINGS['seeds']:
        for number in range(1, SETTINGS['blocks'] + 1):
            block(directory, seed, number)
    method = live['proposal']
    propose(directory, tuple(method['groups']), method['lesson'], method['rationale'])
    record = read(directory / 'proposal.json')
    record.update(execution_origin='numerical replay of the committed live proposal', fresh_agent_decisions=0)
    (directory / 'proposal.json').write_text(json.dumps(record, sort_keys=True, separators=(',', ':')))
    for seed in SETTINGS['seeds']:
        for representation in ('oak', 'python'):
            apply(directory, seed, representation=representation)
        control(directory, seed)
    close(directory)
    for seed in SETTINGS['seeds']:
        final(directory, seed)
    for seed in SETTINGS['seeds']:
        audit_run(directory, seed)
        export_and_check(directory, seed)
        actual = read(directory / str(seed) / 'final.json')
        if identity(actual) != expected['final_result_hashes'][str(seed)]:
            raise AssertionError('replayed predictions or aggregate metrics differ from live execution')
    summary = summarise(directory)
    summary.update(fresh_proposals=0, recorded_live_proposals=1, execution_origin='numerical replay')
    (directory / 'summary.json').write_text(json.dumps(summary, sort_keys=True, separators=(',', ':')))
    (directory / 'replay.json').write_text(json.dumps({'fresh_agent_decisions': 0,
         'matches_live_final_result_hashes': True, 'scientific_sources': source_hashes()}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    replay(parser.parse_args().directory)
