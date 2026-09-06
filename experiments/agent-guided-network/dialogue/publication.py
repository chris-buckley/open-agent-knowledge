"""Package audited dialogue evidence and maintain its intent, learning and task records."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

from runtime import canonical_bytes
from run import verify

EXPERIMENT = Path(__file__).resolve().parents[1]
ROOT = EXPERIMENT.parents[1]


def publish(directory: Path) -> None:
    verify(directory)
    summary = json.loads((directory / 'summary.json').read_text())
    target = EXPERIMENT / 'results/dialogue-run'
    reproduced = target / 'reproduced'
    reproduced.mkdir(parents=True, exist_ok=False)
    for seed in (601, 607):
        shutil.copyfile(Path(__file__).with_name('chat.py'), directory / str(seed) / 'export/chat.py')
        dialogues = json.loads((directory / str(seed) / 'final.json').read_text())['selected']['ordinary']['dialogues']
        success = next(row for row in dialogues if row['replies'] == row['expected'])
        failure = next(row for row in dialogues if row['kinds'][-1] == 'missing' and row['replies'][-1] != row['expected'][-1])
        for name, row in [('success', success), ('failure', failure)]:
            (directory / str(seed) / 'export' / (name + '.json')).write_bytes(canonical_bytes(row))
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
    (reproduced / 'archive.json').write_bytes(canonical_bytes({'sha256': hashlib.sha256((reproduced / 'records.tar.xz').read_bytes()).hexdigest(), 'members': len(manifest)}))
    shutil.copyfile(directory / 'summary.json', reproduced / 'summary.json')
    source = directory / '601' / 'selected-oak'
    node_target = EXPERIMENT / 'nodes/dialogue-learned'
    shutil.copytree(source, node_target, dirs_exist_ok=True)
    for seed in (601, 607):
        shutil.copyfile(Path(__file__).with_name('chat.py'), directory / str(seed) / 'export/chat.py')
    report = _report(summary)
    (target / 'REPORT.md').write_text(report)
    learnings = EXPERIMENT / 'LEARNINGS.md'
    text = learnings.read_text()
    additions = [
        ('L025', 'A numerical OAK graph generates multiword replies and consumes its own earlier replies.', 'Demonstrated only on a 47-token, four-object, four-room task; no open-domain competence.'),
        ('L026', 'Separately fitting the same update from OAK and Python sources produces identical weights and replies.', 'Two seeds, one shared teaching decision; no isolated agent productivity experiment.'),
        ('L027', 'Equivalent host safeguards reject the same deliberately invalid edits in both representations.', 'One accepted valid edit and six rejected fault classes; scripted checks, not real agent error rates.'),
        ('L028', 'Correct individual replies substantially overstate complete-conversation success.', 'Scoped model: 55.76% ordinary replies but 11.72% complete four-turn conversations in this execution.'),
        ('L029', 'The tested networks fail withheld object-destination associations.', 'Scoped model: zero correct first answers in 256 combination dialogues; zero complete dialogues.'),
        ('L030', 'The scoped model rarely acknowledges missing information.', 'One correct missing-information reply in 85 ordinary cases; fluent invented locations remain a serious failure.'),
        ('L031', 'OAK compilation adds measured storage and execution overhead in this implementation.', 'Identical numerical model; fixture-specific latency, not a general performance or productivity claim.'),
        ('L032', 'The new wording test also introduces words unused in teaching.', 'This is a mixed wording/lexical shift, not a clean familiar-word-order experiment.'),
    ]
    rows = ''.join(f'| {key} | {finding} | {limit} | [Dialogue evidence](results/dialogue-run/REPORT.md) |\n' for key, finding, limit in additions)
    if '| L025 |' not in text:
        text = text.replace('\n## How to extend this index', '\n' + rows + '\n## How to extend this index')
        text = text.replace('Updated: 6 September 2026.', 'Updated: 7 September 2026.')
        text = text.replace('The meaning resumption measures a narrow six-choice version, not those broader conversational abilities.',
                            'The dialogue continuation generates short sentences, but fails reliable four-turn conversation and unfamiliar combinations. This is not broad conversational competence.')
        learnings.write_text(text)
    intent = EXPERIMENT / 'EXPERIMENT.md'
    text = intent.read_text()
    if '## Measured generated-dialogue comparison' not in text:
        text += '\n## Measured generated-dialogue comparison\n\nThe [dialogue study](dialogue/PROTOCOL.md) now uses eight executable OAK documents and a 38,519-coefficient word generator. It produces multiword replies without an external agent. Identical OAK/Python training yields identical parameters; equivalent host safeguards reject the same scripted faults. This establishes functional equivalence, not an OAK advantage in language quality or agent productivity. The [report](results/dialogue-run/REPORT.md) preserves severe failures in complete conversations, missing information and unseen combinations. Final weights are frozen; dialogue memory changes during inference. Earlier unverified context studies are not reinstated.\n'
        intent.write_text(text)
    plan = ROOT / 'docs/plans/0011-agent-guided-network/plan.md'
    text = plan.read_text()
    if 'P13.01' not in text:
        section = '''\n### Phase 13: Generate dialogue and compare representations
Objective: Test natural-language generation and a matched OAK/Python update without claiming broad conversation.
- [x] Key task: P13.01 Commit the protocol, freeze numerical source and data, and implement an eight-document generated-dialogue graph plus the same Python computation.
- [x] Key task: P13.02 Record one live teaching proposal, fit it separately through both representations, retain controls, and close selection before final cases.
- [x] Key task: P13.03 Audit all final replies, scoped edits, isolated exports, sampled restored state and native OAK execution; publish raw evidence and update LEARNINGS.md.
Success criteria: Evidence reproduces the recorded predictions and explicitly reports poor conversational reliability and no representation-specific accuracy advantage. OAK-native and host-added checks are distinguished. Independent agent-productivity and main-integration claims remain open.
Transition trigger: The audited research artifact is preserved; no reliable conversational deployment or merge into main is authorised.
'''
        text = text.replace('\n## 4. Admin and Logistics', section + '\n## 4. Admin and Logistics')
        if 'P13.01' not in text:
            raise AssertionError('plan section anchor differs')
        plan.write_text(text)
    (target / 'publication.json').write_bytes(canonical_bytes({'scientific_source': '5e5c17c9779705a03843f0b63dc832eb4d0ac0cc',
        'protocol': 'b0b89bcc1010a62903230f99036b15ec4fc6098f', 'archive_members': len(manifest),
        'claimed_ready_for_conversation': False, 'main_merge_authorised': False}))


def _report(summary: dict) -> str:
    table = '| Training arm | Ordinary replies | Complete ordinary dialogues | Long replies | New combinations | New wording |\n| --- | ---: | ---: | ---: | ---: | ---: |\n'
    for arm, label in [('baseline', 'Initial selected checkpoint'), ('ordinary', 'Full-model ordinary continuation'), ('selected', 'Scoped varied-wording update, OAK = Python')]:
        s = summary['scores'][arm]
        values = [s['ordinary']['reply_accuracy'], s['ordinary']['dialogue_accuracy'], s['long']['reply_accuracy'], s['combination']['reply_accuracy'], s['wording']['reply_accuracy']]
        table += '| ' + label + ' | ' + ' | '.join(f'{100 * value:.2f}%' for value in values) + ' |\n'
    timings = summary['timing_seconds_median']
    sizes = summary['size_bytes']
    return f'''# Generated dialogue: matched OAK and Python experiment

Recorded: 7 September 2026, Brisbane time.
Verdict: Restricted multiword generation and agent participation demonstrated. Reliable natural-language conversation failed. Matched OAK/Python training and inference are equivalent; no representation-specific learning advantage was found.
Scientific source: `5e5c17c9779705a03843f0b63dc832eb4d0ac0cc`. [Protocol](../../dialogue/PROTOCOL.md), [live proposal and freeze](live-session.json), [reproduced records](reproduced/records.tar.xz), [summary](reproduced/summary.json), [archive manifest](reproduced/manifest.json).

## What this model does

Eight OAK documents own the encoder, attention, recurrent decoder, next-word readout, conversation history, generation state, shared contracts and composition. The actual CALL graph is lowered into a numerical program. The same learned operations run at each output position. Matrices are inline constants; the embedding is owned once and shared during generation. There are 38,519 coefficients, 47 vocabulary tokens, a 256-input-token limit, 24-message limit and 14 generated positions. The model is trained from scratch, not a pretrained chatbot.

A shared recurrent encoder reads the complete dialogue log. Attention retrieves evidence for each next word, a recurrent decoder updates generation state, and the learned readout selects the word. Only capitalization, spacing, punctuation and stopping at EOS are deterministic text rendering. No sentence template, answer lookup, simulator, external model or teaching agent chooses a serving reply. Teaching examples and expected sentences are templated and explicitly supplied. Inference requires Python and NumPy.

The task consists of four connected turns: current location, a pronoun/past follow-up, a new movement event, and a switch to another object that may be unobserved. All four objects and four rooms are known. The past location is explicitly present as a source in the reported move; this is not learned physics or a general temporal theory. There is no broad vocabulary, open-domain conversation, genuine correction/negation curriculum, causal explanation or autonomous question asking. Unknown words map to a declared unknown token.

## What was frozen and what was taught

Two numerical seeds, 601 and 607, each receive 2,048 training episodes, 64 ordinary development episodes and 64 reworded development episodes. Four blocks of 300 Adam steps select the baseline checkpoint on mean development reply accuracy. Optimiser state restarts per block. Batch size is 48 and learning rate is 0.003. Teacher-forced gold replies are used as training context; scored dialogues use only the model's own generated replies. This difference can contribute to inference errors and is not hidden.

One live assistant proposal on seed 601 teaches the same histories in original and alternate wording while changing only encoder and attention parameters. Decoder and readout remain frozen. This is lesson selection and numerical fitting, not direct scalar hand-placement. The proposal is recorded before candidate evaluation; seed 607 replays the method, not another agent's reasoning. Both updates pass the frozen development acceptance rule. Only encoder.oak.md and attention.oak.md change; six neighbouring documents remain byte-identical. Frozen decoder/readout weights do not freeze their outputs: they receive changed representations and the shared embedding.

The proposed update is independently fitted from OAK-loaded and Python-loaded copies with identical data, batches, initial weights, optimiser settings and seed. All 38,519 resulting coefficients are identical within each paired run. Final replies are therefore identical too. A full-model ordinary-data continuation is a separate control; its permitted trainable groups and wording differ from the scoped intervention. It is not the OAK-versus-Python comparison. It uses the same 300 added steps but a less restrictive checkpoint rule, retained explicitly.

All selections close before 128 untouched episodes per seed/regime are generated. Episode splits exclude repeated underlying initial move histories across all training, development and final groups and both seeds. New random seeds alone are not counted as generalisation. The combination test excludes specific object-destination pairs during teaching. Long stories have 8-10 initial moves instead of 1-3. New wording changes sentence arrangement and includes question words unused in teaching despite being listed in the vocabulary. It is a mixed wording/lexical shift, not pure word-order transfer. Four-turn histories and output patterns remain strongly structured.

## Results

Descriptive two-seed means, not independent agent trials. Exact full replies are scored, including the required fact and sentence. Alternative valid paraphrases would fail this narrow exact-match metric. Conversation success requires all four replies correct.

{table}
All arms have zero complete-conversation accuracy on the new-combination set. For the scoped model, none of its 256 first current-location answers on that set is correct. Averaging over other turns would hide this failure. The scoped model answers only 1 of 85 ordinary missing-information questions correctly, often inventing a location. There is no reliable abstention mechanism.

Readable sentence generation is not the same as reliable conversation. The scoped update helps some longer stories but underperforms ordinary continuation on familiar replies and whole conversations. An accepted development update has no guarantee outside the selection distribution. All controls and every raw dialogue are retained; a good example is not representative of all cases.

## OAK versus Python

The matched representation comparison finds identical learned weights, acceptance outcomes and generated replies. The scripted safeguard comparison accepts one valid edit and rejects six invalid classes in both: wrong owner, stale revision, empty change, invalid shape, nonfinite value and changed vocabulary. These are shared host checks. OAK supplies canonical documents, dependencies, explicit CALL composition and state contracts; the adapter supplies numerical operations, tensor checks, graph lowering and edit-policy enforcement. No independent agent-error, effort or productivity experiment was performed. One shared conversation and reused code cannot establish those benefits.

The measured first ordinary utterance on model 601 took a median {1000 * timings['python_direct']:.2f} ms directly, {1000 * timings['oak_lowered']:.2f} ms through the lowered program, and {1000 * timings['oak_load_resolve_execute']:.2f} ms with OAK loading/resolution/execution included. Compilation alone took {1000 * timings['compile']:.2f} ms. This is one fixture, not a hardware-independent speed ratio, throughput or energy benchmark. Both paths include their respective validation and tensor decoding. Native complete-dialogue sweeps were too slow for several command limits; only explicitly completed samples are reported below.

Using the same runtime file, direct model plus runtime is {sizes['python_runtime_plus_model']:,} bytes and lowered program plus runtime is {sizes['lowered_runtime_plus_program']:,} bytes. Canonical OAK is {sizes['canonical_oak']:,} bytes. JSON floats are not a packed weight format. Python/NumPy installation, state storage, comparison fixtures and developer tools are excluded from these paired payload figures. No model compression or general speed improvement is claimed.

## Verified boundaries

All 12,288 saved final replies across three arms, four regimes and two seeds are recomputed. Model hashes, unchanged source, disjoint histories, proposal chronology and selected identities are checked. Isolated processes match 4,096 selected-model replies in both direct and lowered engines. Another 256 sampled turns per engine are checked sequentially with model-bound state serialized and restored after every turn. These processes exclude OAK, PyTorch, the simulator, repository reads, credentials and network activity.

Actual native OAK execution is checked on four connected-turn samples in total, two per model. It agrees with the reference replies. The full native sweep was not completed and is not counted as passing. PyTorch/NumPy probabilities agree within the maximum absolute error recorded for 32 sampled turns, with matching generated tokens on those samples. These are sampled numerical checks, not universal equivalence proofs. Twenty preflight tests cover generation, state, strict profile checks and representation parity. Repository verification is recorded separately.

One combined fitting command was interrupted before a candidate record existed and the same candidate fit was restarted. Additional partial compute is unknown and is not excluded from the cost caveat. Several verification calls timed out before completion; successful final coverage is stated explicitly, not inferred from partial output. The local environment uses pydantic-settings 2.14.1, below the declared minimum 2.15. Any CI validation under declared dependencies is a separate recorded check. Conversation tokens, monetary cost and independent agent effort are unavailable.

## Using the artifact

The raw archive contains teaching data, source identities, initial and candidate weights, scoped changes, selected OAK graphs, final cases, actual generated conversations and standalone exports. Extraction preserves the run-relative directories. Use `dialogue/chat.py EXPORT_DIRECTORY --engine oak` or `--engine python` with a selected export. Each export contains model.json, program.json and runtime.py. `/reset` clears the conversation and `/save`/`/load` test model-bound state. The model often gives wrong answers and should not be used as an information service.

The replay entry point repeats the committed teaching method and checks result identities, making zero new agent decisions. A new lesson must use a new experiment and untouched tests; this final set must not be relabelled unseen after further training.

## Interpretation

OAK is operationally useful as the explicit numerical-module representation and edit boundary. This paired experiment does not find a learning-quality advantage over equivalent Python, and it measures added overhead. The network has progressed from selecting one location word to generating connected sentences, but has not achieved dependable natural-language conversation. The next capability problem is grounding those sentences in the supplied facts, preserving role meanings and acknowledging absent evidence, not adding more confident-sounding output.
'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    publish(parser.parse_args().directory)
