# Benchmark and verdict protocol

Status: Study design; no dataset, trained network, or results are supplied.

## Task

Use synthetic compositional relations with deterministic ground truth and numerical inputs. A useful task family composes relations, combines supporting paths, and excludes a contradictory relation. For example, `target(a,c)` can be defined by a two-hop relationship or direct support, with an explicit exception condition.

The reference evaluator uses exact relational semantics. The learned numerical model may use continuous values, but its thresholding, output meaning, and loss must be fixed before evaluation. A high learned score is not a logical proof. Keep Boolean oracle calculations distinct from real-valued matrix products and embedding approximations.

The proposed initial size is about 16 meaningful modules. Before scored runs, freeze their exact equations, topology, shapes, operator registry, parameter count, and initialisation distribution. A hand-constructed exact solution is a smoke test or performance ceiling, not a learned result.

Use deterministic input preparation. Training examples, not canonical parameters, own their individual relation tables. Report any manually supplied rules or concepts, especially information that makes the target rule known to a proposer but not a baseline.

## Pre-registration gate

Before observing scored comparisons, record the task generator version, dataset and split identities, seed set, all hyperparameters, proposal and fitting budgets, evaluator implementation, primary metric, minimal practically meaningful effect, regression limits, acceptance rule, stopping conditions, and export tolerances.

Numerical thresholds remain undecided here because no pilot has run. Use a separate pilot to select them, then freeze them before the scored study. Do not retroactively choose thresholds that make a result pass. Adding a new treatment after seeing results requires a new study record.

## Comparison groups

| Treatment | What it isolates |
| --- | --- |
| Numerical optimiser only | A strong end-to-end learning baseline, with its tuning budget recorded. |
| Non-agent proposal search | Whether bounded random or structured parameter search explains the improvement. |
| Numerical fitting without an agent | The solver's contribution, using a declared non-agent rule for selecting correction targets. |
| One central agent with fitting | Whether decentralised node ownership helps beyond a single proposer. |
| Local agents with direct parameter edits | The original strong hypothesis that agents can directly choose useful numerical changes. |
| Local agents with numerical fitting | The recommended behavioural-proposal mechanism. |

Use identical network architecture, accessible supervision, initialisation seeds, and test cases wherever the comparison requires them. Record exceptions instead of calling unequal information equal. Central and local agents must receive comparable total context and resource allowances, not merely the same model name.

Report both matched candidate-evaluation budgets and total-resource comparisons. Include language-model calls and tokens, solver steps, training compute, candidate scoring, wall-clock observations, hardware, and provider prices or measured charges when available. No resource number may be guessed or omitted because it disadvantages a treatment.

## Ablations

Compare correct, absent, and shuffled module descriptions to test the value of meaning. Compare permitted gradient diagnostics with no gradient diagnostics. Compare local-only scoring with whole-network scoring in an isolated analysis treatment; local-only acceptance is not the recommended production policy. Compare revision-aware coordination with deliberately measured naive combination only in a contained diagnostic experiment.

Semantic descriptions do not establish interpretability. Use concept supervision or intervention checks where appropriate, and disclose that supervision to baselines. Count agent-provided examples, rules, and corrections as additional information.

## Data separation

Training cases may inform numerical fitting and agent diagnostics. Development cases may inform candidate selection under the stated policy. The sealed final test set is not available to agents, solvers, or the adaptive coordinator.

Where meaningful, hold out entity assignments and relation combinations rather than only random rows. Prevent exact duplicates or generator leakage across splits. Run independent seeds and keep failed runs in the accounting. Freeze the winning revision before final testing; using final-test results to revise it starts a new study.

## Measurements

The primary performance metric must match the task and its class balance. Report the selected predictive metric, uncertainty across seeds, and results by relevant relation or composition group. Also report candidate acceptance, invalid/stale proposal rates, local-to-global regressions, fitting residuals, parameter movement, and total resource use.

For stochastic training, use paired initialisation seeds where appropriate and report a predeclared uncertainty interval or comparison procedure. Do not claim superiority from a single favourable seed. Report the smallest practically useful effect independently from statistical uncertainty.

[Export tests](../runtime/EXPORT.md) establish that the deployed numerical network retains the measured capability. Export timing and memory are measured in the stated environment, not inferred from the absence of agents.

## Verdicts

| Verdict | Required conclusion |
| --- | --- |
| Engineering demonstrated | A reproducible improvement over the chosen initial network survives agent-free reference execution and clean export tests. |
| Scientific advantage supported | A predeclared, reproducible practical advantage over strong matched controls remains after accounting for uncertainty and total resources. |
| No demonstrated advantage | The system runs, but comparisons do not support a useful benefit from agents. |
| Inconclusive | Missing evidence, insufficient power, invalid comparisons, incomplete runs, or export failures prevent the intended conclusion. |

Scaling toward hundreds of nodes receives a separate verdict only after measured scaling studies. No export test establishes the truth of all predictions, and no numerical improvement alone proves that semantic agent understanding caused it.

[Result status](../results/STATUS.md) records whether any of these verdicts have actually been reached.
