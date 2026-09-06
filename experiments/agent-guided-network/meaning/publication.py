"""Publish audited evidence and update its owning documents without changing weights."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from reproduce import ARMS, REGIMES, SOURCE_COMMIT, package_evidence
from run import ROOT, identity, read, source_hashes

EXPERIMENT = ROOT / 'experiments/agent-guided-network'
DESTINATION = EXPERIMENT / 'results/meaning-run'
LABELS = ('Initial ordinary teaching', 'Repeat ordinary teaching', 'Varied wording',
          'Varied wording plus agreement', 'Agent-selected longer lessons', 'Matched-step ordinary continuation')


def publish_results(directory: Path) -> None:
    summary = read(directory / 'verified-summary.json')
    live = read(DESTINATION / 'live-session.json')
    if source_hashes() != live['scientific_sources']:
        raise ValueError('scientific source changed')
    if identity(live['proposal']) != live['decision']['proposal_sha256']:
        raise ValueError('live proposal identity changed')
    if identity(live['observation']) != live['proposal']['observation_sha256']:
        raise ValueError('live observation identity changed')
    for arm in ARMS:
        for regime, metrics in live['expected_means'][arm].items():
            for metric, expected in metrics.items():
                if abs(summary['means'][arm][regime][metric] - expected) > 1e-9:
                    raise ValueError(f'replay differs: {arm}/{regime}/{metric}')
    opposite, total = 0, 0
    for seed in ('401', '409', '419'):
        cases = read(directory / seed / 'final-cases.json')['sets']['ordinary']
        predictions = read(directory / seed / 'final.json')['agent']['unseen_wording']['predictions']
        for case, predicted in zip(cases, predictions, strict=True):
            event = next(event for event in reversed(case['events']) if event[0] == case['subject'])
            opposite += predicted == event[2 if case['before'] else 1]
            total += 1
    diagnostic = {'opposite_endpoint_answers': opposite, 'cases': total,
                  'fraction': opposite / total, 'status': 'post-selection error analysis; no subsequent fitting'}
    (directory / 'role-diagnostic.json').write_text(json.dumps(diagnostic, indent=2))
    package_evidence(directory, DESTINATION / 'reproduced')
    publication = {'checked_out_source': os.environ.get('GITHUB_SHA'),
                   'workflow_run_id': os.environ.get('GITHUB_RUN_ID'),
                   'scientific_source_commit': SOURCE_COMMIT,
                   'replay_matches_live_run_metrics': True,
                   'fresh_agent_decisions_during_reproduction': summary['fresh_agent_proposals_in_this_run'],
                   'role_diagnostic': diagnostic,
                   'postprocessor_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (DESTINATION / 'publication.json').write_text(json.dumps(publication, indent=2) + '\n')
    _write_report(summary, diagnostic)
    _update_index()
    _update_intent()
    _update_plan()


def _write_report(summary: dict, diagnostic: dict) -> None:
    rows = '\n'.join('| ' + label + ' | ' + ' | '.join(
        f"{100 * summary['means'][arm][regime]['accuracy']:.2f}%" for regime in REGIMES) + ' |'
        for arm, label in zip(ARMS, LABELS, strict=True))
    pairs = '\n'.join('| ' + label + ' | ' + ' | '.join(
        f"{100 * summary['means'][arm][regime]['both_correct']:.2f}%"
        for regime in ('same_meaning', 'direction', 'order')) + ' |'
        for arm, label in zip(ARMS, LABELS, strict=True))
    (DESTINATION / 'REPORT.md').write_text(f'''# Wording versus meaning: verified resumption

Recorded: 6 September 2026.
Verdict: Agent-selected teaching and agent-free execution demonstrated. Reliable transfer to unseen wording failed. This is not conversation or a general world model.
Scientific source: `{SOURCE_COMMIT}`. [Protocol](../../meaning/PROTOCOL.md), [live evidence](live-session.json), [raw archive and summaries](reproduced/summary.json), [publication provenance](publication.json).

## Evidence boundary

The source archive was checksum-verified against the published GitHub Actions artifact. The earlier temporary run directories were absent. This is a new execution of the existing committed protocol, not recovery of the missing run or reproduction of its previously quoted percentages. Prior unverified aggregate scores were visible in the conversation. These results are therefore not an independent blinded trial. No final measurements from the missing context or world-language runs are reinstated.

All nine original scientific files remain byte-identical to the source commit. The added reproduction and publication scripts audit results; they do not change training, inference, datasets, acceptance rules or parameters. Selection closed before this execution generated final cases. No parameter edits followed its final scores. A 45-second local command limit interrupted closure; partial files were preserved, and the unchanged closure routine was restarted before final cases existed. Local recovery evidence is in live-session.json.

## What ran

One 6,431-coefficient network encodes event sentences and questions with shared learned recurrent weights, attends to the ordered observation log, and selects one of six location words. Its vocabulary has 22 tokens and its capacity is 32 events. The OAK node owns inline quantised parameter records and explicit event-history state. Parameter records use signed 16-bit-range integers plus scales and float64 inference; JSON storage is not a packed 16-bit deployment.

The task asks the current location or the source location in the object's most recent reported move. The source room is explicitly present in that sentence, so a correct past answer is not proof of a learned temporal world model. Questions name their subjects. This profile does not resolve pronouns, generate multiword replies, learn matter or physics, or sustain open conversation. It contains no serving simulator, answer template or external language-model call.

The registered seeds are 401, 409 and 419. Each receives 1,024 training histories, 128 short development histories, 128 medium histories and 512 final histories per regime. Training histories have two to four moves; medium histories have five to six; final long histories have twelve to eighteen. Splits are by underlying history before wording is rendered. One held-out arrangement is evaluated using familiar words. Testing that arrangement is not testing new vocabulary.

## Actual agent participation

One live proposal on seed 401 mixed 1,024 longer histories with the original examples, retaining the agreement strength of 0.3. The proposal and its rationale preceded evaluation. Medium-history development accuracy rose from 92.97% to 99.22%; ordinary accuracy rose from 97.66% to 99.22%. The frozen rule accepted the candidate, and no second proposal was made. The choice was replayed numerically on seeds 409 and 419 and accepted there too. Those are not new agent trials.

This is an agent-selected lesson implemented through 400 numerical optimisation steps, not direct hand-placement of individual weights. Each fit presents two views per batch, 48 histories per batch. Controls separate ordinary repetition, varied wording, an agreement objective, and ordinary-history continuation with the same added step count. Step count is matched, not information or total cost: the longer-lesson arm receives additional histories. Conversation tokens and monetary cost are unavailable.

The durable reproduced archive is a numerical re-execution of the recorded choice and makes zero fresh agent decisions. Its metrics are checked against the live execution. The live proposal, observation, decision, selected identity and local environment are retained separately in live-session.json. Three seeds and one shared-context proposer are not a population of independent agents.

## Final accuracy

Descriptive means over three numerical seeds; higher is better. Same histories recur across models and wording views, so those predictions are not independent samples.

| Treatment | Familiar wording | New object-room combinations | Longer histories | Unseen wording |
| --- | ---: | ---: | ---: | ---: |
{rows}

The combination set changes the final queried destination to an object-room pairing absent from training. Current-location questions therefore require the withheld destination; before-location questions still ask a previously allowed source. They must not be treated as equivalent tests. The summary retains exact correct/count breakdowns for both question types by seed.

## Paired meaning tests

Both answers must be correct. Mere agreement, or simply changing the answer, does not pass.

| Treatment | Same event, changed wording | Reversed move direction | Reordered events |
| --- | ---: | ---: | ---: |
{pairs}

Direction pairs have identical word multisets but different correct answers. A deterministic bag-of-words answer function cannot answer both correctly. That is an analytical control, not a trained bag-of-words benchmark. Order pairs contain the same events in different orders. The selected network handles many such contrasts in familiar wording, but fails the held-out arrangement of the same meaning.

## Error analysis and interpretation

On unseen wording, {diagnostic['opposite_endpoint_answers']} of {diagnostic['cases']} selected-network answers ({100 * diagnostic['fraction']:.2f}%) give the other endpoint of the queried move: source instead of destination, or destination instead of source. This post-selection diagnostic identifies a systematic role-confusion pattern on these cases, not a universal causal explanation of its hidden representation. No training followed this analysis.

The longer-history lesson improves long-history performance relative to the matched-step continuation, but does not solve wording transfer. The repeat control is stronger on some paired direction/order tests. Neither more varied wording nor the agreement objective is an across-the-board improvement here. Participation has been demonstrated; robust reusable meaning has not.

The next research question is how to teach stable source/destination roles across sentence positions. Any new lesson or architecture must use a newly declared study with fresh held-out forms. The current held-out wording must not be silently reopened as evidence of untouched generalisation.

## Verification and finalisation

All saved labels, predictions, losses, paired metrics and aggregate scores were independently recomputed with the NumPy inference implementation. Training/development/final history separation and selected-model identities were checked. All original source hashes match the freeze. Eighteen meaning preflight checks and the 59 prior-study checks pass, alongside the two complete branch verification entry points and generation freshness.

The twelve selected-model export checks cover {summary['isolated_restored_predictions']:,} predictions in clean processes with model-bound state restoration after observations and questions. They exclude OAK, PyTorch, simulator imports, credentials and network use. Actual OAK execution with serialised state is checked on {summary['oak_serialised_state_samples']} samples. Maximum observed PyTorch/NumPy probability difference is {summary['maximum_torch_numpy_difference']:.3g}; all tested decisions agree. These are sampled checks, not universal proofs.

The complete raw archive contains candidate and selected parameters, observations, proposals, decisions, selection closure, cases, predictions, canonical OAK nodes and standalone exports. Every archived member is SHA-256 checked against the manifest. The selected exports require Python and NumPy, not the teaching agent. Successful export does not make the model conversationally ready.

Local pydantic-settings 2.14.1 is below the repository's declared minimum 2.15; that environment discrepancy is retained. The evidence workflow installs declared repository dependencies and pins the study's numerical versions. Its exact environment is recorded in the reproduced freeze. Branch checks and PR integration are distinct: the draft PR's pre-existing conflicts with newer main are not resolved by this experiment, and no merge into main is authorised.

## Reproduce

Install repository dependencies and meaning/requirements.txt, then run from the repository root:

```sh
OPENBLAS_NUM_THREADS=1 python experiments/agent-guided-network/meaning/run.py test
OPENBLAS_NUM_THREADS=1 python experiments/agent-guided-network/meaning/reproduce.py replay /tmp/oak-meaning-replay
```

Replay starts a new output directory, preserves the committed settings, performs no new agent reasoning, and fails on inconsistent evidence or export behaviour. The raw archive is `reproduced/records.tar.xz`; its manifest and archive hash sit beside it.
''', encoding='utf-8')


def _update_index() -> None:
    index = EXPERIMENT / 'LEARNINGS.md'
    text = index.read_text()
    if '| L019 |' in text:
        raise ValueError('meaning findings already published')
    rows = '''| L019 | An agent-selected longer-history lesson improves the registered long-history test relative to ordinary continuation. | One live choice plus two numerical replay seeds; extra data differs, so this is participation, not isolated agent superiority. | [Meaning resumption](results/meaning-run/REPORT.md#final-accuracy) |
| L020 | Strong familiar-wording accuracy does not establish stable meaning across a held-out word arrangement. | Selected model: 99.35% familiar versus 8.07% unseen wording in this re-execution. | [Paired tests](results/meaning-run/REPORT.md#paired-meaning-tests) |
| L021 | Most unseen-wording errors return the opposite endpoint of the queried move. | 1,340 of 1,536 cases, 87.24%; post-selection diagnostic, not a universal mechanistic explanation. | [Error analysis](results/meaning-run/REPORT.md#error-analysis-and-interpretation) |
| L022 | The held-out combination score mixes two materially different question types. | Current questions ask an unseen destination association; before questions ask an allowed source. Stratified counts are retained. | [Combination scope](results/meaning-run/REPORT.md#final-accuracy) |
| L023 | Selected one-token models survive state restoration and agent-free export on tested cases. | 6,144 isolated predictions, 96 OAK samples; not a conversational or universal-equivalence result. | [Verification](results/meaning-run/REPORT.md#verification-and-finalisation) |
| L024 | More wording variation or agreement training is not uniformly better in this fixed study. | Ordinary repetition is stronger on some paired tests; all controls and losses remain visible. | [Comparisons](results/meaning-run/REPORT.md#paired-meaning-tests) |'''
    marker = '\n## How to extend this index'
    before, after = text.split(marker, 1)
    text = before.rstrip() + '\n' + rows + '\n\n' + marker.lstrip('\n') + after
    text = text.replace('None has been measured here.', 'The meaning resumption measures a narrow six-choice version, not those broader conversational abilities.')
    text = text.replace('## Evidence ledger', 'D005, 6 September 2026: missing context/world-language run files and their quoted scores remain unverified. The committed wording study is re-executed and audited rather than reconstructed from prose. Prior aggregate exposure is disclosed. See the meaning resumption report.\n\n## Evidence ledger', 1)
    index.write_text(text, encoding='utf-8')


def _update_intent() -> None:
    intent = EXPERIMENT / 'EXPERIMENT.md'
    lines = intent.read_text().splitlines()
    for index, line in enumerate(lines):
        if line.startswith('Status:'):
            lines[index] = 'Status: Feasibility, attention, compression and wording-versus-meaning studies are measured. The latest study verifies one-token numerical answers and exposes failed unseen-wording transfer. Reliable conversation and broad generalisation remain unproven. See LEARNINGS.md.'
            break
    lines.extend(['', '## Verified wording-versus-meaning resumption', '',
                  'The [meaning report](results/meaning-run/REPORT.md) records a new execution of the existing committed protocol, not recovery of missing context results. One live teaching choice is followed by numerical replay, independent metric recomputation and model-bound memory-restoration checks. The original scientific source remains unchanged. This model selects a single location word; it is not the proposed conversational world model.'])
    intent.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def _update_plan() -> None:
    plan = ROOT / 'docs/plans/0011-agent-guided-network/plan.md'
    text = plan.read_text()
    phase = '''### Phase 12: Verify and publish wording evidence
Objective: Deliver the existing wording-versus-meaning experiment without a new architecture or unsupported recovery claims.
- [x] Key task: P12.01 Recover the checksum-verified committed source and distinguish it from missing context and wording run records.
- [x] Key task: P12.02 Re-execute the registered comparisons, record one live teaching choice and numerical replays, and close selection before this execution creates final cases.
- [x] Key task: P12.03 Recompute every saved metric independently, verify model-bound state restoration and OAK/export decisions, and retain raw records and source identities.
- [x] Key task: P12.04 Publish audited evidence and update the learning index after branch checks pass; disclose pre-existing main integration conflicts separately.
Success criteria: The meaning report, raw archive, member hashes, live record, reproduction command and verification evidence are present on the same branch. Failed wording transfer is reported rather than relabelled as conversation.
Transition trigger: The verified research delivery is recorded; broader conversational capability and main integration remain separate work.

'''
    marker = '### Coordinating Instructions'
    if '### Phase 12:' in text or marker not in text:
        raise ValueError('unexpected plan state')
    text = text.replace(marker, phase + marker, 1)
    text = text.replace('authorised sequential-assistant feasibility, attention, and compression studies',
                        'authorised sequential-assistant feasibility, attention, compression, and wording studies')
    plan.write_text(text, encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    publish_results(parser.parse_args().directory)
