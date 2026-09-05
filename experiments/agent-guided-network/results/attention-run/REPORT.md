# Attention: a harder sequential-assistant study

Recorded: 5 September 2026.
Verdict: Numerical attention and agent-free export demonstrated. Generalisation remains limited; no agent superiority established.
Source baseline: `06eae1cd9aaf697b705a16f6d96baad01f8988fa`.
[Frozen source and environment](freeze.json), [study](../../attention/study.oak.md), [raw results](final.json).

## What changed

Two OAK attention documents now own genuine query, key, value, and output projection matrices. Their typed processes execute scaled dot-product cross-attention through a closed numerical host profile. The first retrieves a bridge key, and the second uses it to retrieve a class value. A numerical softmax decodes class probabilities. Four documents form each snapshot: both attention modules, root orchestration, and shared contracts.

This is single-head cross-attention, not a complete Transformer, multi-head self-attention, or a language model. Eight matrices contain 416 trainable scalars. Padding masks, axis dimensions, finite-value rules, and supported operations are explicit. The old four-module, 11-scalar experiment and its evidence are unchanged.

The running assistant again represented the logical node roles sequentially. No independent agents or paid model API calls were launched. There were four fresh proposals on seed 7. Seeds 19 and 31 replayed their methods numerically and applied the same independent acceptance rule; they were not fresh reasoning sessions.

## Task and evidence separation

Every case supplies new random continuous keys and values in two tables. The query matches a first-table key; its associated value matches a second-table key, whose class is the answer. Numerical inputs contain neither the target indices nor the answer. The input-dependent attention weights are activations, not learned parameter constants.

For each seed, training uses 512 cases and development uses 256 cases, with three to six valid table entries. Final evaluation uses 512 new cases per regime: the training distribution, sixteen-entry tables, and sixteen-entry tables with an almost identical wrong key at each hop. The crowded distractor angle is 0.12 radians. These stress cases were not used for selection. [Selected network identities](selected.json) were written after selection closed and before final metrics.

Seed 0 was a separate implementation pilot. The source and OAK study were frozen before scored observations. Data identities include shape, field names, contents, labels, and target indices. Separation is procedural, not an adversarial security barrier against the implementing assistant.

All numerical fitting uses identical final training labels. The assistant additionally sees aggregate intermediate alignment and entropy diagnostics, not intermediate fitting targets. Query/key matrices begin randomly; value/output matrices start near identity for every treatment. This prior is explicit rather than credited as discovered knowledge.

## What the assistant actually did

| Proposal | Change | Development accuracy | Development cross-entropy | Decision |
| --- | --- | --- | --- | --- |
| 001 | Halve the second output projection only | 91.80% to 91.80% | 0.413657 to 0.282055 | Accepted |
| 002 | Double both blocks' attention scores via query/key scaling | 91.80% to 91.41% | 0.282055 to 0.318192 | Rejected |
| 003 | Fit only the second block for 150 gradient steps | 91.80% to 92.58% | 0.282055 to 0.547387 | Rejected |
| 004 | Fit only the first block for 150 gradient steps | 91.80% to 91.02% | 0.282055 to 0.344659 | Rejected |

The only accepted live-session edit was output calibration, not a learned improvement to query/key matching. It changed a real inline OAK matrix without any gradient calculation for that edit. The two rejected fitting proposals still consumed 300 gradient steps. Rejections are retained, not removed from resource accounting.

Proposal 002 increased first-hop target mass from 83.19% to 93.21% while worsening final loss. This is direct evidence, on these cases, that more concentrated attention need not improve the composed network. It is not a general claim that sharp attention is undesirable.

On replay seed 19, calibration and direct sharpening were accepted. On replay seed 31, calibration and first-block fitting were accepted. The same suggested update can behave differently on a different numerical network. These acceptances are numerical transfer observations, not additional assistant decisions.

## Results

Values below are descriptive three-seed means: one actual decision session plus two replay seeds. They are not three independent assistant trials. Higher accuracy and lower cross-entropy are better.

| Treatment | Ordinary accuracy | Longer-table accuracy | Crowded-key accuracy |
| --- | --- | --- | --- |
| Initial | 52.28% | 39.71% | 33.98% |
| Common 80-step warm-up | 91.80% | 72.14% | 37.43% |
| 600-step Adam with development checkpoints | 91.80% | 72.14% | 37.43% |
| Adam plus fixed numerical scaling grid | 92.12% | 74.02% | 37.50% |
| Recorded assistant sequence | 93.49% | 77.67% | 38.02% |

| Treatment | Ordinary cross-entropy | Longer-table cross-entropy | Crowded-key cross-entropy |
| --- | --- | --- | --- |
| Initial | 1.226091 | 1.340928 | 1.359804 |
| Warm-up / selected Adam | 0.374128 | 1.009967 | 2.127948 |
| Numerical scaling grid | 0.283477 | 0.731262 | 1.579706 |
| Recorded assistant sequence | 0.256849 | 0.695283 | 1.691944 |

On the actual seed-7 session, accuracy was 94.53%, 75.20%, and 40.43% across these regimes. The accepted calibration edit did not change those accuracies. A fixed non-agent scaling grid selected identical weights and obtained identical metrics on that seed. It also matched the replay sequence on seed 19. The aggregate difference versus the grid comes from first-block fitting accepted on replay seed 31, not multiple new agent discoveries.

The ordinary assistant-sequence accuracy range is 92.77% to 94.53%; longer-table range 75.20% to 80.27%; crowded-key range 33.98% to 40.43%. No confidence interval or statistical-superiority claim is made. The crowded-key cross-entropy remains worse than the untrained initial network's mean even though accuracy is somewhat higher. Confident errors are a major limitation.

## Does attention actually matter?

After selection, replace attention weights by a uniform distribution over valid positions, without retraining. On ordinary cases, the recorded sequence averages 93.49% accuracy normally, 66.47% with the first attention block disabled, and 51.56% with the second disabled. Disabling both also yields 51.56%, because a uniform second block ignores its query.

These interventions establish functional dependence in this implementation. They are not matched retraining experiments or a proof that attention weights explain each prediction. The uniform control is above the four-class 25% guessing rate because a class value is present among the supplied candidates; predicting the prevalent supplied class is informative. Accuracy alone must not be interpreted against a naive 25% baseline.

## What we learned

The attention mechanism is a usable numerical OAK node and survives removal of all agent machinery. Calibration and retrieval quality are distinct: reducing output confidence can lower loss without fixing any answer. Concentrating attention can amplify a wrong match or a distorted intermediate representation. Extending training on the same small data need not help: the checkpoint-selected Adam control retained the warm-up on all three seeds.

The larger limitation is distribution shift. Training on short, well-separated random tables did not produce reliable long-context or nearly ambiguous retrieval. The crowded case also exposes that confident errors can increase after training. A plausible next research hypothesis is to train and select with explicit length and key-similarity diversity, rather than assume bigger matrix norms solve the problem. That hypothesis was not tested or retroactively added to this study.

This study does not establish that semantic agent understanding beats optimisation. The baseline uses one fixed learning rate, not exhaustive tuning or regularisation search. The scaling grid explains the live-session benefit. Cost and diagnostic access are not fully matched. One favourable replay-seed update does not support a general advantage.

## Resources and reproducibility

Every seed receives 80 common warm-up steps. The Adam baseline receives 600 additional steps, checking development loss at the initial checkpoint and every 25 steps. The scaling control adds nine fixed candidates. The live assistant proposes two direct edits and two 150-step fitting edits: 300 total additional gradient steps and four final candidate evaluations. Agent token and monetary costs are unavailable. Recorded tool durations exclude conversation and repository development.

Twenty attention tests passed, including all 416 finite-difference gradient entries, masked-key exclusion, all-masked rejection, permutation invariance, distinct table lengths, mutation protection, forbidden OAK instructions/tools, stale proposals, and export integrity. A separate full replay reproduced every recorded treatment's accuracy and cross-entropy and counted zero new assistant proposals.

All nine seed/regime export checks cover 512 cases each, for 4,608 tested predictions. Generated inference needs only Python and NumPy. Each clean isolated process blocks sockets and repository/OAK reads, starts without credentials, and verifies parameter identity. Maximum observed output difference is 0.0 with exact argmax agreement. Separate OAK executor checks on two cases per seed/regime also have maximum difference 0.0. These are sampled checks, not universal equivalence proofs.

Canonical initial and selected seed-7 matrices are committed under `nodes/attention-initial` and `nodes/attention-learned`. The full run ZIP contains every candidate snapshot and all three standalone exports. [The replay command](../../attention/ATTENTION.md) regenerates them from recorded decisions. Repository and CI delivery checks are reported separately from scientific results.
