# Compression: direct placement and smaller numerical models

Recorded: 6 September 2026, Brisbane time.
Verdict: Exact folding and a smaller task-specific replacement demonstrated. No advantage attributable to agent judgement over the matched structured search. No compression of general intelligence demonstrated.
Baseline: `01093746154ef972842df1c1c0f298101921b579`.
Protocol commit: `35317423f42720bfdc50637b3109f80409e07882`.
[Source and environment freeze](freeze.json), [frozen OAK study](../../compression/study.oak.md), [all final measurements](records.tar.xz), [selected models](records.tar.xz), [storage accounting](storage-accounting.json), [replay](replay.json).

The lossless [records.tar.xz](records.tar.xz) contains exact `final.json`, `selected.json`, `SELECTION_CLOSED`, per-seed controls, data identities, observations, proposals, and decisions. The readable live records also remain beside this report. The archive hash is recorded in verification.json; it is an evidence container, not a model-compression metric.

## User intent and actual intervention

The hypothesis is that an agent can deliberately place or change weights to produce a much more compressed AI, then leave an agent-free network. We operationalised this as retained task capability at reduced actual parameter storage. Merely changing a matrix is not compression. A compact solution for one synthetic retrieval problem is not a general AI.

One physical assistant made seven live proposals across three fresh data seeds, with six accepted and one rejected. The assistant used earlier development feedback when choosing later proposals; these are shared-context decisions, not three independent agents. Only the first data seed involved a multi-step discovery sequence. The other two tested a consciously transferred choice. Numerical replay made zero new assistant decisions. No additional model API or paid service was used. Conversation tokens and monetary cost are unavailable.

The experiment uses the previously selected seed-7 attention model as one fixed 416-coefficient teacher. New seeds 107, 223, and 331 change data, not teacher training. We did not retrain three independent teachers.

## Exact compression before learning

The existing graph has no intervening nonlinearity between certain projections. Matrix multiplication therefore folds eight learned matrices into two 8-by-8 matching kernels and one 4-by-4 class kernel, for 144 coefficients. The formula and the change of intermediate bridge coordinates are explicit in [the protocol](../../compression/COMPRESSION.md#exact-folding).

This reduces stored coefficients by 65.38% (2.89 times fewer). It is an algebraic simplification available to an automatic compiler, not an agent-learning achievement. Across all 12,288 final predictions, its maximum probability difference from the teacher was 4.718447854656915e-15 and all decisions matched. Real-arithmetic associativity supports the formula; sampled floating-point agreement does not guarantee identical rounding or ties on every input.

## Smaller replacement through shared structure

The assistant first removed cross-coordinate entries, then tied each kernel's diagonal to one scalar. The selected model has:

```text
first matching kernel:  2048 * identity(8)
second matching kernel: 2048 * identity(8)
class output kernel:       8 * identity(4)
```

These three gains are stored explicitly in OAK constants. The encoding expands to 20 nonzero positions across 144 effective matrix positions. This is three independent stored coefficients, not three neurons or three connections. The runtime implements the declared identity encoding; it does not consult an agent or hide extra learned weights.

The replacement changes the teacher's function and often corrects its mistakes. It is not exact compression of the teacher's learned behaviour. All families receive the same declared task prior: matching keys share a coordinate basis and the values include candidate class encodings. Using identity matrices encodes that prior. Calling this unsupervised discovery of a general reasoning algorithm would be incorrect.

## Data and controls

Training and development each contain 192 new cases from each of three regimes: short tables, sixteen-entry tables, and sixteen-entry tables with a wrong key 0.12 radians from the correct key at each hop. Every case uses freshly sampled continuous keys. Final testing uses 1,024 new cases per regime and adds a harder 32-entry, 0.04-radian regime. Across three data seeds there are 12,288 final cases. The final test set was generated only after all selections were closed in SELECTION_CLOSED and `selected.json` inside [records.tar.xz](records.tar.xz).

An implementation-only seed-zero lifecycle test preceded source freeze. Fitting uses final training labels only. Development diagnostics and scores inform selection; final tests do not. Procedural separation is not an adversarial barrier against the assistant that implements the evaluator.

Controls include the fixed teacher, exact folding, two magnitude-pruning fractions, diagonal projection, 200-step Adam fits in 144/20/3-coefficient families with development checkpoints, four fixed tied-gain candidates, and a larger 36-candidate grid. The four-candidate grid has the same maximum candidate budget as each live trial, not the same total cost. The live trials actually used four, two, and one proposals. Each fitted family uses the same training data, fixed rate 0.05, and checkpoint interval 20; this is not exhaustive optimiser tuning.

A separate exact nearest-key algorithm reads only supplied keys and values. It uses zero learned coefficients and achieves 100% on every final regime. It is an algorithmic control, not a hidden export fallback. This is a strong warning that this task can be solved by structure rather than statistical learning.

## Results

Accuracy percentages below are means over the three fresh data seeds for one fixed teacher and one shared-context assistant. They are not independent-agent population estimates.

| Model | Independent coefficients | Short | Sixteen entries | Near distractors | Harder 32-entry stress |
| --- | ---: | ---: | ---: | ---: | ---: |
| Teacher / exact folded teacher | 416 / 144 | 92.45 | 74.80 | 32.71 | 31.74 |
| Magnitude pruning | 36 plus indices | 98.11 | 88.41 | 39.75 | 36.13 |
| Diagonal projection | 20 | 100.00 | 98.80 | 44.50 | 39.55 |
| Fitted dense | 144 | 99.19 | 93.00 | 67.42 | 56.18 |
| Fitted diagonal | 20 | 99.97 | 99.90 | 47.01 | 39.39 |
| Fitted tied gains | 3 | 100.00 | 100.00 | 48.01 | 41.83 |
| Fixed four-candidate search | 3 | 100.00 | 100.00 | 100.00 | 61.78 |
| Fixed 36-candidate search | 3 | 100.00 | 100.00 | 100.00 | 50.68 |
| Assistant direct placement | 3 | 100.00 | 100.00 | 100.00 | 61.78 |
| Exact nearest-key algorithm | 0 learned | 100.00 | 100.00 | 100.00 | 100.00 |

The four-candidate search selects exactly the same kernels as the assistant on every seed. It explains the entire selected-model benefit. No agent superiority is established, despite the improvement over the much larger teacher and the limited fitting baselines.

The larger grid selects gains [512, 8192, 8] on every seed, based on a development loss difference of roughly 1.4e-9 compared with the assistant's [2048, 2048, 8]. It performs worse on the harder stress set. The per-seed paired 95% bootstrap intervals for the assistant minus this grid on that set are [9.28, 13.48], [9.18, 13.48], and [8.50, 12.60] percentage points. They describe these fixed models on sampled cases, not evidence over independent agents. The smaller non-agent grid still matches the assistant, so these intervals cannot establish agent-specific value. Selection among almost equal floating-point losses is also a portability limitation.

On harder stress cases, assistant accuracy improves over the teacher but cross-entropy worsens: 2.341369 versus 1.531828. The larger grid's cross-entropy is 3.881288. More confident wrong answers remain a serious failure mode. The replacement does not retain a loss-based quality guarantee outside the development regimes.

## Live proposal ledger

| Data seed | Proposal | Change | Accepted | Development observation |
| --- | --- | --- | --- | --- |
| 107 | 001 | Keep diagonal entries, 20 coefficients | Yes | Short 100%, long 97.40%, near 48.96% |
| 107 | 002 | Place gains [32, 32, 8] | Yes | Short/long 100%; near 53.13% |
| 107 | 003 | Place gains [512, 512, 8] | Yes | All regimes 100%; near loss 0.001429 |
| 107 | 004 | Place gains [2048, 2048, 8] | Yes | All regimes 100%; near loss 0.001006 |
| 223 | 001 | Transfer gains [2048, 2048, 8] | Yes | All regimes 100% |
| 223 | 002 | Try gains [8192, 8192, 8] | No | Loss improvement below frozen 1e-6 threshold |
| 331 | 001 | Transfer gains [2048, 2048, 8] | Yes | All regimes 100% |

Every numerical proposal and concise rationale was written before evaluation. [Seed 107](107/proposals/001.oak.md), [seed 223](223/proposals/001.oak.md), and [seed 331](331/proposals/001.oak.md) start their respective records. Corresponding observations and decisions, including the rejection, remain in each seed directory. There are no fitting steps inside the agent arm. The overall study still uses numerical optimisation for controls and starts from a previously trained teacher.

## Storage is not just coefficient count

| Representation | Coefficients | Float64 payload | Model JSON | Canonical OAK | Complete export |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original teacher | 416 | 3,328 bytes | 13,248 bytes | 21,591 bytes | 18,623 bytes |
| Folded dense | 144 | 1,152 bytes | 3,144 bytes | 12,821 bytes | 12,864 bytes |
| Diagonal projection | 20 | 160 bytes | 752 bytes | 10,305 bytes | 10,472 bytes |
| Assistant / four-candidate search | 3 | 24 bytes | 422 bytes | 9,958 bytes | 10,142 bytes |

The 138.67-fold coefficient reduction from 416 to three is not a 138.67-fold deployment reduction. The actual uncompressed package is 1.84 times smaller. Against the folded model using the same runtime, the complete reduction is 1.27 times. The compact runtime alone is 9,456 bytes, including validation and encodings. Python and NumPy installation size, process memory, latency, FLOPs, and energy were not included or benchmarked; no savings in those quantities are claimed.

The original teacher export uses readable JSON, while the compact export uses compact JSON. Serialising both model records under the same compact policy gives 8,608 versus 422 bytes, a 20.40-fold model-file difference. This accounts for metadata and avoids crediting whitespace removal as weight compression. Sparse controls additionally report index counts, uint16-equivalent index bytes, and their actual JSON sizes. All measurements are uncompressed, not archive-compression ratios. File sizes and policy are retained in storage-accounting.json.

## Validation and reproduction

Twenty-two preflight tests passed, including finite differences for all 167 coordinates across dense, diagonal, and tied families; exact folding; OAK XML/Markdown round trips; actual OAK executor parity; masks; forbidden tools; malformed kernels; symlink rejection; stale/closed proposals; frozen-source rejection; and a complete seed-zero pilot lifecycle.

All twelve agent seed/regime exports passed clean isolated execution on 12,288 predictions, without agents, OAK imports, credentials, network activity, or repository reads. Maximum observed output difference is 0.0. Twenty-four sampled predictions through the actual OAK executor also matched. Four additional original-teacher export checks cover 4,096 cases. These are sampled numerical checks, not a formal proof for every floating-point input.

A complete fresh numerical replay reproduces all selected coefficients within tolerance, all treatments' accuracy/loss/fidelity metrics, and all seven acceptance decisions. It reports zero new assistant decisions. Use the commands in [the compression protocol](../../compression/COMPRESSION.md#reproduce). Full run snapshots and standalone exports are regenerable; representative folded and selected OAK networks are committed under nodes/compression-folded and nodes/compression-learned. Repository and CI checks are recorded separately in [the delivery report](../../../../docs/plans/0011-agent-guided-network/report.md).

## Interpretation

The positive finding is that deliberately imposed structure can give a dramatically smaller numerical solution to this task, and OAK can store that structure without retaining the agent. Exact folding separately removes representation redundancy while preserving the original function. The negative finding is that a simple non-agent search, given the same structural family, finds the same compact solution; an exact task algorithm does better still.

The next useful hypothesis is not simply larger gains. It is whether agents can identify compact structure on tasks where the matching basis or useful intermediate representation is not supplied, against automated structure selection under matched information and budgets. That is a future study. None of its results is implied here.
