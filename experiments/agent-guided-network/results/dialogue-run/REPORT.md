# Generated dialogue: OAK versus Python

Recorded: 7 September 2026, Brisbane time.
Verdict: Restricted word generation and agent participation demonstrated. Reliable natural-language conversation failed. No representation-specific learning advantage established.
Source: `5e5c17c9779705a03843f0b63dc832eb4d0ac0cc`. [Protocol](../../dialogue/PROTOCOL.md), [live proposal](live-session.json), [local summary](local-summary.json), [this run](reproduced/summary.json), [raw records](reproduced/records.tar.xz).

## Evidence boundary

This report's table describes cross-environment replication. Exact identity with local final-result hashes: False. These runs must not be averaged or presented as independent agent trials.

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

| Arm | Ordinary replies | Complete ordinary conversations | Long replies | New combinations | New wording |
| --- | ---: | ---: | ---: | ---: | ---: |
| Selected baseline | 58.79% | 15.62% | 45.61% | 32.42% | 41.99% |
| Full-model ordinary continuation | 66.89% | 25.39% | 50.68% | 31.25% | 46.58% |
| Scoped update: OAK = Python | 66.02% | 28.52% | 53.12% | 33.89% | 44.04% |

The scoped model gives 0 correct first answers out of 256 new-combination conversations. Average reply accuracy includes easier later turns and must not conceal this failure. It correctly acknowledges missing information in 0 of 85 ordinary missing-information cases. Fluent invented locations remain a serious weakness.

The original local scoped model scored 55.76% ordinary replies and 11.72% complete ordinary conversations; local full-model ordinary continuation scored 67.58% and 22.27%. Those local figures are preserved separately, not described as exactly reproduced by CI. Training trade-offs can differ between executions. No consistent superiority of the scoped lesson is assumed. A selected successful conversation is an illustration, not typical performance; complete failures and every generated reply remain in the archive.

## Matched representation comparison

OAK and Python yield identical paired trained weights and replies. Both accept the valid scripted edit and reject the same six invalid classes: wrong owner, stale revision, empty change, malformed tensor, nonfinite value and altered vocabulary. These are shared host safeguards, not demonstrated native OAK tensor protections or real agent-error rates. OAK supplies canonical document ownership, dependency resolution, explicit process composition and state contracts. The adapter supplies numerical operations, tensor checks, lowering and edit-policy enforcement.

For the first ordinary utterance on seed 601, direct Python takes 4.48 ms, lowered OAK 18.97 ms and OAK including load/resolve/execute 881.32 ms. Compilation is 316.12 ms. These are warm median timings for one fixture, five repeats except native/compile three, not a general throughput, energy or productivity claim. Paths include their respective validation and parameter decoding; native timing includes loading and resolution.

Model plus shared runtime uses 800,275 bytes directly and 850,262 bytes compiled. Canonical OAK uses 846,138 bytes. Installed dependencies, state files and testing fixtures are excluded. No model-compression or speed benefit is claimed. Whether OAK helps agents understand or maintain larger systems remains untested by this scripted paired comparison.

## Verification and use

All 12,288 final replies across three arms, four regimes and two seeds are recomputed from their frozen models. Source/data hashes, selected identities, recorded proposal chronology and scoped changes are audited. Each selected model is exported to isolated direct and lowered engines: 4,096 replies per engine in total match this run's saved predictions. A further 256 sampled turns per engine save and restore model-bound state after every turn. These processes exclude OAK, PyTorch, teaching code, simulator access, credentials, repository reads and network activity.

Native OAK checks cover four connected turns total, two per model, with serialized state. A complete native sweep was not finished within local command limits and is not claimed. PyTorch/NumPy comparisons cover 32 sampled turns; probability differences and token agreement are recorded per seed. These are sampled checks, not universal equivalence proofs. Twenty new preflight tests and 99 existing tests pass; repository/CI status is separate from a capability verdict.

Local pydantic-settings 2.14.1 was below the repository's declared minimum. CI installs declared repository dependencies. One local combined fitting command was interrupted before its candidate record and the same fit was restarted; additional partial compute is unknown. Verification timeouts are disclosed rather than counted as passes. None of this makes the deployed model a reliable information service.

The archive includes initial, candidate and selected weights, training/evaluation cases, proposals, decisions, generated replies, canonical graphs and standalone exports. Every member is SHA-256 checked. Each seed's export contains model.json, program.json, runtime.py, chat.py and selected success/failure examples. Run `python chat.py EXPORT_DIRECTORY --engine oak` or `--engine python`; `/reset`, `/save` and `/load` operate on the model's own episode memory.

The default `dialogue/reproduce.py NEW_DIRECTORY` is strict replay. `--replication` records a separately labelled environment-specific execution; it must not be reported as reproducing the local checkpoints. Both make zero fresh agent decisions. New teaching requires a new study and untouched tests, not reuse of this final set as unseen evidence.

## Interpretation

The experiment advances from one-word classification to generated connected sentences. It also shows that readable language can conceal weak factual tracking and near-total failure to acknowledge absent evidence. OAK is operational as an executable modular representation and revision boundary, but the matched Python system learns the same model and the adapter adds overhead. Reliable general conversation and an OAK-specific agent-productivity advantage remain unestablished.
