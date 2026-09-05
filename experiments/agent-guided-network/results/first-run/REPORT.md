# First sequential-assistant feasibility run

Recorded: 2026-09-05.
Verdict: Engineering demonstrated on a four-module synthetic task. No demonstrated scientific advantage over numerical-only training.

## What actually ran

One running assistant acted sequentially for the logical node-agent responsibilities. There were four numerical modules, three trainable matrices containing 11 trainable scalars, one frozen composition matrix, and six OAK documents per network snapshot. No 100-agent fleet was launched. The assistant made four actual proposals for seed 7 after reading training diagnostics and development feedback. Three were accepted and one was rejected. Seeds 19 and 31 replayed the recorded methods numerically; they were not new agent sessions.

The first requested commit, `5a25878b5ee0a42252e92d4af549ac4149cde24f`, changed EXPERIMENT.md before implementation. The implementation ran against the repository snapshot rooted at `a825c588b699b453bb24703c68bb724b033b0797`. [Frozen code hashes and environment](freeze.json) identify the exact new numerical source used, independent of the later publication commit.

## Task and controls

The task predicts two-hop reachability with an explicit veto in four-entity relation worlds. Every input, operation, activation, parameter, connection, threshold, and output is numerical. The exact Boolean oracle supplies labels, not inference-time answers. This is a small learned classifier, not an exact logic engine or a deployment permission system.

A separate seed-0 pilot preceded the [frozen OAK study record](../../evaluation/study.oak.md). Each scored seed used 128 training worlds, 64 development worlds, and 256 final-test worlds. Duplicate complete worlds were checked within and across splits. Entity-pair decisions within a world are correlated; the 12,288 final-test decisions are not 12,288 independent replicates. Final-test metrics were computed only after all selected treatment snapshots were recorded in [selected.json](selected.json).

The assistant and automatic concept-fitting control knew the target rule and intermediate relation targets. End-to-end Adam used the final labels. This is privileged semantic supervision, not evidence that an agent discovered the rule. Budgets differ and conversation token/cost telemetry is unavailable. No matched-cost or statistical-superiority claim is made.

## Results

The table reports three-seed means. Only seed 7 involved fresh assistant decisions; the other two are numerical transfer/replay checks. Ranges are descriptive, not confidence intervals. Binary cross-entropy (BCE) is better when lower.

| Treatment | Mean final-test accuracy | Mean final-test BCE | Accuracy range |
| --- | --- | --- | --- |
| Initial network | 57.3649% | 0.63592272 | 44.4824% to 65.9912% |
| Common 50-step warm start | 82.0557% | 0.49194600 | 81.2500% to 83.5449% |
| Numerical-only Adam | 99.9430% | 0.00667289 | 99.9023% to 99.9756% |
| Automatic concept fitting | 99.9268% | 0.01991129 | 99.9023% to 99.9756% |
| Six random proposals | 82.7393% | 0.47679402 | 81.2256% to 84.3506% |
| Assistant-guided sequence | 99.9268% | 0.00643748 | 99.9023% to 99.9756% |

For the actual seed-7 assistant session, initial accuracy was 44.4824%, the warm start was 81.2500%, and the selected agent-guided network reached 99.9023% on 4,096 held-out entity-pair decisions. Numerical-only Adam and the automatic concept-fitting control also reached 99.9023% on that seed. [All raw per-seed results](final.json) are retained, including balanced accuracy and class balance.

The agent sequence has slightly lower mean BCE than numerical-only Adam but slightly lower mean accuracy. The difference is too small and the study too limited to establish an agent advantage. Automatic concept fitting matches the agent sequence's accuracy with fewer readout optimisation steps, illustrating why numerical fitting and extra supervision cannot be credited to agent understanding alone.

## Actual assistant decisions

| Proposal | Numerical change requested | Development result | Decision |
| --- | --- | --- | --- |
| 001 | Correct the right selector only | Accuracy 81.4453% to 75.0977%; BCE improves but the 2-point regression cap fails | Rejected; incumbent unchanged |
| 002 | Correct right selector and refit readout jointly | Accuracy 86.7188%; BCE 0.27426010 | Accepted |
| 003 | Correct the left selector only | Accuracy 99.9023%; BCE 0.06103364 | Accepted |
| 004 | Recalibrate readout only | Accuracy 99.9023%; BCE 0.00782546 | Accepted; selection then closed |

[Observations](7/observations/001.oak.md), [proposals](7/proposals/001.oak.md), and [decisions](7/decisions/001.oak.md) are canonical OAK records. Each proposal existed before its evaluation and identifies its baseline and observation hashes. Rationales are explanations, not proof of causal attribution. All four records, including the rejection, are retained under the corresponding directories.

## Resource accounting

All methods start from the same 50-step warm-up at each seed. Numerical-only training explores three learning rates with 400 steps each, selecting on development BCE. The actual assistant sequence uses three least-squares calls and 800 readout-gradient steps across four candidate evaluations, including the rejected first fit. The automatic concept control uses two fits and 400 readout steps. Random search evaluates six candidates. All fitting uses training data; development data only selects candidates.

[Preparation timing](preparation.json) and each decision's measured tool duration are recorded. The durations exclude the assistant's reasoning and repository development work and must not be presented as total training cost. Model identity is the session-reported GPT-6 Pro identity, not an independently attested API model identifier. No external model API calls were made; conversation tokens and monetary cost are not exposed and are recorded as unknown.

## Unwrapping and verification

Every selected agent network was exported to a generated `model.json` and `inference.py`. The artifact needs Python and NumPy, not OAK, an agent, credentials, training history, or a language-model service. There is no ONNX exporter and no claim to compile arbitrary OAK. The adapter accepts one closed profile by full structural comparison of its canonical OAK documents; it refuses altered instructions, schemas, tools, wiring, or fixed constants.

All three exports passed fresh-process tests with a clean working directory, stripped environment, Python isolation, blocked socket activity, and blocked repository/OAK-document access. Exported parameters matched their source matrices. Maximum output difference was 0.0, with exact decision equivalence across 256 held-out worlds and three boundary worlds per seed. OAK executor checks on two held-out worlds per seed also matched the lowered numerical runtime with maximum error 0.0. These sampled checks are not a universal mathematical equivalence proof.

Seventeen executable checks passed before source freeze: OAK XML and Markdown round trips, resolution, OAK/numerical parity, finite-difference gradients, immutable inference, invalid tensors, fixed parameters, forbidden instructions/tools, symlinks, duplicate-data checks, stale proposals, closed selection, and clean export. A second complete run reproduced all recorded numerical results and reported zero new assistant proposals. Repository-wide checks and publication evidence are recorded separately in the [delivery report](../../../../docs/plans/0010-agent-guided-network/report.md).

## Scope and remaining questions

This demonstrates the engineering mechanism: a real assistant can choose numerical matrix updates for OAK nodes, rejected updates can be retained, accepted matrices can be versioned, and the learned network can run after the assistant is removed.

It does not establish hundred-node scaling, independent-agent benefits, semantic-description effects, direct hand-edited weight superiority, a general tensor compiler, formal export equivalence, or generalisation beyond this synthetic generator. No architecture, scoring rule, or final-test setting was changed after scored feedback. Broader study tasks remain visibly open in the plan.
