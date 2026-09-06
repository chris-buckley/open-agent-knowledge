"""Preserve audited dialogue runs without conflating exact replay and replication."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
from typing import Any

from runtime import canonical_bytes
from run import verify

EXPERIMENT = Path(__file__).resolve().parents[1]
ROOT = EXPERIMENT.parents[1]
SOURCE = '5e5c17c9779705a03843f0b63dc832eb4d0ac0cc'
PROTOCOL = 'b0b89bcc1010a62903230f99036b15ec4fc6098f'


def publish(directory: Path) -> None:
    verify(directory)
    summary = json.loads((directory / 'summary.json').read_text())
    target = EXPERIMENT / 'results/dialogue-run'
    reproduced = target / 'reproduced'
    reproduced.mkdir(parents=True, exist_ok=False)
    for seed in (601, 607):
        export = directory / str(seed) / 'export'
        shutil.copyfile(Path(__file__).with_name('chat.py'), export / 'chat.py')
        rows = json.loads((directory / str(seed) / 'final.json').read_text())['selected']['ordinary']['dialogues']
        chosen = {'success': next(row for row in rows if row['replies'] == row['expected']),
                  'failure': next(row for row in rows if row['kinds'][-1] == 'missing' and row['replies'][-1] != row['expected'][-1])}
        for name, row in chosen.items():
            (export / (name + '.json')).write_bytes(canonical_bytes(row))
    manifest = {file.relative_to(directory).as_posix(): hashlib.sha256(file.read_bytes()).hexdigest()
                for file in sorted(directory.rglob('*')) if file.is_file() and '__pycache__' not in file.parts}
    (reproduced / 'manifest.json').write_bytes(canonical_bytes(manifest))
    with tarfile.open(reproduced / 'records.tar.xz', 'w:xz') as archive:
        for name in manifest:
            archive.add(directory / name, arcname=name, recursive=False)
    with tarfile.open(reproduced / 'records.tar.xz') as archive:
        for name, expected in manifest.items():
            stream = archive.extractfile(name)
            if stream is None or hashlib.sha256(stream.read()).hexdigest() != expected:
                raise AssertionError('archived member differs')
    (reproduced / 'archive.json').write_bytes(canonical_bytes({
        'sha256': hashlib.sha256((reproduced / 'records.tar.xz').read_bytes()).hexdigest(), 'members': len(manifest)}))
    for name in ('summary.json', 'replay.json'):
        shutil.copyfile(directory / name, reproduced / name)
    shutil.copytree(directory / '601/selected-oak', EXPERIMENT / 'nodes/dialogue-learned', dirs_exist_ok=True)
    (target / 'REPORT.md').write_text(_report(summary))
    _update_owners()
    (target / 'publication.json').write_bytes(canonical_bytes({
        'scientific_source': SOURCE, 'protocol': PROTOCOL, 'archive_members': len(manifest),
        'mode': summary['execution_origin'], 'matches_local_results': summary['reproduction']['matches_live_final_result_hashes'],
        'claimed_ready_for_conversation': False, 'main_merge_authorised': False}))


def _update_owners() -> None:
    findings = (
        ('L025', 'An OAK graph generates multiword replies and consumes its own previous replies.', 'Restricted 47-token, four-object, four-room task; no open-domain competence.'),
        ('L026', 'Separately fitting the same update from OAK and Python sources gives identical weights and replies.', 'Within each paired execution; not independent agent-productivity trials.'),
        ('L027', 'Equivalent host safeguards accept the same valid edit and reject the same invalid edits.', 'Six fault classes; scripted checks, not measured agent error rates or native OAK tensor checks.'),
        ('L028', 'Individual-reply accuracy substantially overstates complete-conversation success.', 'Local scoped model: 55.76% ordinary replies but 11.72% complete conversations. Replication is reported separately.'),
        ('L029', 'The tested networks fail withheld object-destination associations.', 'Local scoped model: zero correct first answers and complete dialogues in 256 combination cases. Replication counts remain separate.'),
        ('L030', 'The scoped model rarely acknowledges missing information.', 'Local run: one correct reply in 85 ordinary missing-information cases. Replication counts are separate.'),
        ('L031', 'This OAK execution adapter adds storage and latency overhead.', 'Identical numerical model; fixture-specific timing, not a general performance or productivity verdict.'),
        ('L032', 'The wording test also introduces vocabulary entries unused in teaching.', 'Mixed wording and lexical shift, not a clean familiar-word-order experiment.'),
        ('L033', 'Fixed seeds and matching scientific source did not reproduce local checkpoints in another environment.', 'Strict CI replay failed. Replication is labelled separately; its cause is not isolated. Within-run representation equality still holds.'),
    )
    index = EXPERIMENT / 'LEARNINGS.md'
    text = index.read_text()
    if '| L025 |' not in text:
        rows = ''.join(f'| {key} | {claim} | {scope} | [Dialogue evidence](results/dialogue-run/REPORT.md) |\n'
                       for key, claim, scope in findings)
        text = text.replace('\n## How to extend this index', '\n' + rows + '\n## How to extend this index')
        text = text.replace('Updated: 6 September 2026.', 'Updated: 7 September 2026.')
        text = text.replace('The meaning resumption measures a narrow six-choice version, not those broader conversational abilities.',
                            'The dialogue study generates short sentences, but fails reliable four-turn conversation and unfamiliar combinations.')
        index.write_text(text)
    intent = EXPERIMENT / 'EXPERIMENT.md'
    text = intent.read_text()
    status = ('Status: Restricted generated dialogue and matched OAK/Python training are measured. Paired representations give identical weights within each run; reliable conversation fails. Cross-environment retraining differs and is reported separately. See LEARNINGS.md and results/dialogue-run/REPORT.md.')
    text = '\n'.join(status if line.startswith('Status:') else line for line in text.splitlines()) + '\n'
    if '## Measured generated-dialogue comparison' not in text:
        text += ('\n## Measured generated-dialogue comparison\n\nThe [dialogue study](dialogue/PROTOCOL.md) uses eight executable OAK documents and 38,519 coefficients to generate words. '
                 'The [report](results/dialogue-run/REPORT.md) records identical paired OAK/Python updates, equivalent host safeguard checks and severe factual and whole-conversation failures. '
                 'This is no demonstrated learning-quality or agent-productivity advantage for OAK. Exact cross-environment checkpoint replay failed; a separately labelled replication retains its own weights and predictions. '
                 'Parameters remain fixed during dialogue, while the exported numerical system updates its own conversation history. Earlier unverified context studies are not reinstated.\n')
    intent.write_text(text)
    plan = ROOT / 'docs/plans/0011-agent-guided-network/plan.md'
    text = plan.read_text()
    if 'P13.01' not in text:
        phase = '''\n### Phase 13: Generate dialogue and compare representations
Objective: Measure generated replies and matched OAK/Python learning without claiming broad conversation.
- [x] Key task: P13.01 Commit the protocol, freeze numerical source and data, and implement an eight-document generator and the same Python computation.
- [x] Key task: P13.02 Record one live teaching proposal, fit it separately through both representations, retain controls and close selection before final cases.
- [x] Key task: P13.03 Audit saved replies, scoped edits, isolated exports and sampled restored/native state; preserve the evidence and update LEARNINGS.md.
Success criteria: Each frozen-model audit reproduces its own saved predictions. Cross-environment retraining differences are retained rather than claimed to pass exact replay. Scientific capability failure, host versus OAK checks and unmatched agent effort are explicit.
Transition trigger: The audited research artifact is preserved. No reliable conversational deployment, independent-agent advantage or merge into main is authorised.
'''
        text = text.replace('\n## 4. Admin and Logistics', phase + '\n## 4. Admin and Logistics')
        if 'P13.01' not in text:
            raise AssertionError('plan section anchor differs')
        plan.write_text(text)


def _report(summary: dict[str, Any]) -> str:
    table = '| Arm | Ordinary replies | Complete ordinary conversations | Long replies | New combinations | New wording |\n| --- | ---: | ---: | ---: | ---: | ---: |\n'
    for arm, label in (('baseline', 'Selected baseline'), ('ordinary', 'Full-model ordinary continuation'), ('selected', 'Scoped update: OAK = Python')):
        s = summary['scores'][arm]
        values = (s['ordinary']['reply_accuracy'], s['ordinary']['dialogue_accuracy'], s['long']['reply_accuracy'],
                  s['combination']['reply_accuracy'], s['wording']['reply_accuracy'])
        table += '| ' + label + ' | ' + ' | '.join(f'{100 * value:.2f}%' for value in values) + ' |\n'
    missing = [item['scores']['selected']['ordinary']['per_kind']['missing'] for item in summary['audits']]
    current = [item['scores']['selected']['combination']['per_kind']['current'] for item in summary['audits']]
    timings, sizes = summary['timing_seconds_median'], summary['size_bytes']
    reproduction = summary['reproduction']
    return f'''# Generated dialogue: OAK versus Python

Recorded: 7 September 2026, Brisbane time.
Verdict: Restricted word generation and agent participation demonstrated. Reliable natural-language conversation failed. No representation-specific learning advantage established.
Source: `{SOURCE}`. [Protocol](../../dialogue/PROTOCOL.md), [live proposal](live-session.json), [local summary](local-summary.json), [this run](reproduced/summary.json), [raw records](reproduced/records.tar.xz).

## Evidence boundary

This report's table describes {reproduction['mode']}. Exact identity with local final-result hashes: {reproduction['matches_live_final_result_hashes']}. These runs must not be averaged or presented as independent agent trials.

The first [strict CI replay](https://github.com/chris-buckley/open-agent-knowledge/actions/runs/34067276443) failed because retrained checkpoints and final replies differed from the local execution. The error and source identity remain in [strict-replay-failure.json](strict-replay-failure.json). Matching seeds and numerical package versions did not establish cross-environment reproducibility. The specific cause has not been isolated. [PyTorch's guidance](https://docs.pytorch.org/docs/stable/notes/randomness.html) does not guarantee identical results across platforms.

The default replay still requires exact local result identities and fails on a mismatch. The explicit `--replication` delivery mode was added after that failure. It preserves a separately labelled re-execution, all differing hashes and its own model artifacts. No frozen scientific code, data, fitting settings, acceptance rule or final tests changed. All within-run audits and OAK/Python equality checks remain strict. [replay.json](reproduced/replay.json) records the actual identity comparison, environments and zero new agent decisions.

## Model and task

Eight canonical OAK documents own the encoder, attention, recurrent decoder, word readout, conversation memory, generation state, shared contracts and composition. Actual CALL/ACT processes are lowered into numerical instructions. There are 38,519 coefficients, 47 vocabulary tokens, 256 input-token capacity, 24-message capacity and 14 generated positions. Parameters are float32 values stored as JSON, not a packed compressed format.

The learned encoder reads the ordered dialogue. At each word, attention retrieves numerical evidence, the decoder updates generation state and a learned readout selects the next token. Parameters are shared across positions. The embedding has one encoder owner and is also used by generation. Only spacing, punctuation, capitalization and stopping at EOS are deterministic text conversion. There is no serving sentence template, answer lookup, simulator, external model, pretrained chatbot or teaching agent. Standalone inference needs Python and NumPy.

Each episode has four connected turns: current location, a pronoun/past follow-up, a newly reported movement and a question about another object that may be unobserved. Four objects and four rooms are known. The source location is explicitly present in the reported movement, so a correct past answer does not establish general temporal reasoning. There is no unrestricted vocabulary, genuine correction/negation curriculum, physical simulation, causal explanation or autonomous question asking. Unknown words map to a declared unknown token. These are restricted generated exchanges, not dependable general conversation.

## Training and selection

Seeds 601 and 607 each use 2,048 teaching episodes, 64 ordinary development episodes and 64 separately worded development episodes. Four 300-step Adam blocks use batch size 48 and learning rate 0.003, restarting optimiser state each block. Select the baseline checkpoint with the highest mean development reply accuracy. Teaching text and answers are templated. Training uses gold previous replies; scored conversations use only the model's own generated replies. This mismatch is disclosed and may contribute to errors.

One assistant proposal on seed 601 adds alternate wording of the same teaching histories and fits only encoder and attention for 300 steps. It is lesson selection and numerical fitting, not direct placement of every scalar. Seed 607 replays the method, not another agent session. Only encoder.oak.md and attention.oak.md change; six neighbouring documents remain byte-identical. Frozen decoder/readout weights do not freeze their behaviour when upstream representations and the shared embedding change.

The update is independently fitted from OAK-loaded and Python-loaded copies with identical initial weights, examples, batches, optimiser settings and seed. All resulting coefficients and acceptance outcomes match within each pair. A separate full-model ordinary continuation uses the same added step count but different allowed parameters, wording and a less restrictive checkpoint selection rule. It is not the OAK-versus-Python comparison. Conversation costs and extra partial fitting compute are unknown; no matched independent-agent effort experiment was run.

Selection closes before 128 final episodes per seed/regime are generated. Initial underlying move histories are disjoint across all teaching, development and final groups and both seeds. The new-combination set requires withheld object-destination pairings. Long stories have 8-10 initial moves rather than 1-3. The wording test also introduces question words unused in teaching despite appearing in the vocabulary: a mixed wording/lexical shift, not pure word-order transfer. The four-turn structure remains strongly templated.

## Results

Descriptive two-seed means. Exact full replies must match the expected sentence and fact. Valid alternative paraphrases would fail this narrow metric. Complete conversation requires all four replies correct.

{table}
The scoped model gives {sum(row['correct'] for row in current)} correct first answers out of {sum(row['count'] for row in current)} new-combination conversations. Average reply accuracy includes easier later turns and must not conceal this failure. It correctly acknowledges missing information in {sum(row['correct'] for row in missing)} of {sum(row['count'] for row in missing)} ordinary missing-information cases. Fluent invented locations remain a serious weakness.

The original local scoped model scored 55.76% ordinary replies and 11.72% complete ordinary conversations; local full-model ordinary continuation scored 67.58% and 22.27%. Those local figures are preserved separately, not described as exactly reproduced by CI. Training trade-offs can differ between executions. No consistent superiority of the scoped lesson is assumed. A selected successful conversation is an illustration, not typical performance; complete failures and every generated reply remain in the archive.

## Matched representation comparison

OAK and Python yield identical paired trained weights and replies. Both accept the valid scripted edit and reject the same six invalid classes: wrong owner, stale revision, empty change, malformed tensor, nonfinite value and altered vocabulary. These are shared host safeguards, not demonstrated native OAK tensor protections or real agent-error rates. OAK supplies canonical document ownership, dependency resolution, explicit process composition and state contracts. The adapter supplies numerical operations, tensor checks, lowering and edit-policy enforcement.

For the first ordinary utterance on seed 601, direct Python takes {1000 * timings['python_direct']:.2f} ms, lowered OAK {1000 * timings['oak_lowered']:.2f} ms and OAK including load/resolve/execute {1000 * timings['oak_load_resolve_execute']:.2f} ms. Compilation is {1000 * timings['compile']:.2f} ms. These are warm median timings for one fixture, five repeats except native/compile three, not a general throughput, energy or productivity claim. Paths include their respective validation and parameter decoding; native timing includes loading and resolution.

Model plus shared runtime uses {sizes['python_runtime_plus_model']:,} bytes directly and {sizes['lowered_runtime_plus_program']:,} bytes compiled. Canonical OAK uses {sizes['canonical_oak']:,} bytes. Installed dependencies, state files and testing fixtures are excluded. No model-compression or speed benefit is claimed. Whether OAK helps agents understand or maintain larger systems remains untested by this scripted paired comparison.

## Verification and use

All 12,288 final replies across three arms, four regimes and two seeds are recomputed from their frozen models. Source/data hashes, selected identities, recorded proposal chronology and scoped changes are audited. Each selected model is exported to isolated direct and lowered engines: 4,096 replies per engine in total match this run's saved predictions. A further 256 sampled turns per engine save and restore model-bound state after every turn. These processes exclude OAK, PyTorch, teaching code, simulator access, credentials, repository reads and network activity.

Native OAK checks cover four connected turns total, two per model, with serialized state. A complete native sweep was not finished within local command limits and is not claimed. PyTorch/NumPy comparisons cover 32 sampled turns; probability differences and token agreement are recorded per seed. These are sampled checks, not universal equivalence proofs. Twenty new preflight tests and 99 existing tests pass; repository/CI status is separate from a capability verdict.

Local pydantic-settings 2.14.1 was below the repository's declared minimum. CI installs declared repository dependencies. One local combined fitting command was interrupted before its candidate record and the same fit was restarted; additional partial compute is unknown. Verification timeouts are disclosed rather than counted as passes. None of this makes the deployed model a reliable information service.

The archive includes initial, candidate and selected weights, training/evaluation cases, proposals, decisions, generated replies, canonical graphs and standalone exports. Every member is SHA-256 checked. Each seed's export contains model.json, program.json, runtime.py, chat.py and selected success/failure examples. Run `python chat.py EXPORT_DIRECTORY --engine oak` or `--engine python`; `/reset`, `/save` and `/load` operate on the model's own episode memory.

The default `dialogue/reproduce.py NEW_DIRECTORY` is strict replay. `--replication` records a separately labelled environment-specific execution; it must not be reported as reproducing the local checkpoints. Both make zero fresh agent decisions. New teaching requires a new study and untouched tests, not reuse of this final set as unseen evidence.

## Interpretation

The experiment advances from one-word classification to generated connected sentences. It also shows that readable language can conceal weak factual tracking and near-total failure to acknowledge absent evidence. OAK is operational as an executable modular representation and revision boundary, but the matched Python system learns the same model and the adapter adds overhead. Reliable general conversation and an OAK-specific agent-productivity advantage remain unestablished.
'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    publish(parser.parse_args().directory)
