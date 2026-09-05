# Compression through agent-guided weight placement

Authorised: 6 September 2026, Brisbane time.
Branch: `experiment/agent-guided-network`.
Baseline: `01093746154ef972842df1c1c0f298101921b579`.
Status: Protocol was recorded before scored proposals; implementation, seven live decisions, final testing, and numerical replay are complete. [Measured report](../results/compression-run/REPORT.md).
Learning ledger: [LEARNINGS.md](../LEARNINGS.md).

## Hypothesis and verdicts

The user's hypothesis is a much more compressed AI because training agents can deliberately place or change weights, then disappear. The measurable local hypothesis is a smaller numerical model at retained task capability. This is not a claim that hand editing inherently compresses intelligence.

Separate three verdicts: exact functional simplification; smaller task-capable replacement; advantage attributable to agent judgement. A positive result for one does not establish the others. A synthetic table-retrieval model is not a compressed general-purpose language model.

## Exact folding

The existing bias-free two-hop attention graph uses eight projection matrices and 416 floating-point coefficients. Let its first and second block parameters have suffixes 1 and 2. Associativity permits:

```text
M1 = WQ1 @ WK1.T / sqrt(8)
M2 = WV1 @ WO1 @ WQ2 @ WK2.T / sqrt(8)
T2 = WV2 @ WO2
A1 = softmax(mask(query @ M1 @ keys1.T))
bridge = A1 @ values1
A2 = softmax(mask(bridge @ M2 @ keys2.T))
probability = softmax(A2 @ values2 @ T2)
```

M1 and M2 each contain 64 coefficients; T2 contains 16. That is 144 stored coefficients, not 416. In real arithmetic this preserves final outputs for this particular graph. Floating-point differences and decision ties still need measurement. Intermediate bridge coordinates change, so this is a new explicit numerical profile, not silent alteration of the old node contract. No agent advantage is claimed for the algebra.

## Candidate representations

Use existing OAK constants to own exact numerical descriptors. No OAK grammar or hidden external parameter store is added. Each descriptor fixes its matrix dimension, encoding, numerical values, and any sparse indices.

Compare folded dense matrices (144 coefficients), magnitude-pruned folded matrices, diagonal matrices (20 coefficients), and scaled identity matrices (three independent coefficients shared across 20 diagonal positions). Tied coefficients, expanded nonzeros, implicit zero positions, sparse-index bytes, and full model-package size must all be disclosed. Generating a matrix from a scalar is parameter tying, not evidence that there is only one computational connection.

A running assistant may propose a diagonal projection or explicitly place the three gains of the scaled-identity representation. It must record the numerical proposal and a short rationale before evaluation. A deterministic compiler performs exact folding; it is not an agent.

## Study design

Use the previous selected seed-7 network as one fixed teacher. All new trials start from that same published network. Fresh data seeds are 107, 223, and 331, not new teacher-training seeds. One shared-context assistant makes fresh decisions separately for each data seed. These are not independent language-model runs; subsequent replay records zero decisions.

Use fresh training and development mixtures containing both short and sixteen-entry tables and near distractors. The earlier stressed tests motivated this new protocol but are not reused as fresh test evidence. Freeze all data recipes and source hashes before scored proposals. An implementation-only seed-zero pilot is separate.

Final tests use new short, sixteen-entry, and near-distractor cases, plus a harder 32-entry close-key stress set. The target remains exact two-hop retrieval of supplied keys and class values. This task has strong structure: queries and matching keys share an aligned basis, class values are supplied, and equality is meaningful. An exact nearest-key algorithm is an informative zero-learned-parameter control, not a neural result.

Controls include the frozen 416-coefficient teacher, exact folded teacher, magnitude pruning, diagonal projection, numerical fitting in the 144/20/3-coefficient families, a fixed four-candidate tied-gain search, and a larger fixed search using the same structural prior. All fitting receives final training labels; every method can use the declared task structure. No intermediate target fitting or test feedback is allowed. The strong search is deliberately reported separately from a candidate-count-matched control.

Each live trial permits four proposals and no numerical fitting inside the agent arm. Direct placement therefore has an unambiguous meaning. Candidate acceptance uses development capability at reduced actual model storage, not the agent's confidence. Freeze the precise tolerances, optimiser settings, candidate grids, counts, and selection rule in `study.oak.md` before observing scored data. Preserve rejected proposals.

## Evaluation and accounting

Report accuracy and cross-entropy per test regime, fidelity to the teacher separately, retained-capability verdicts, independent coefficient count, expanded nonzeros, parameter payload bytes, sparse-index bytes, canonical OAK bytes, model-file bytes, runtime bytes, and complete export bytes. A compressed task replacement may outperform the teacher while disagreeing with it; call that replacement, not exact compression.

Close every seed's selection and write all selected snapshot hashes before any final test metrics. Use paired case-level uncertainty for selected fixed-model comparisons; do not mistake many test cases for independent agent trials. Report differences across the three data seeds and disclose the single teacher. Equal numerical candidate counts do not establish matched total training cost: conversation cost is unavailable.

Export all needed numerical operators and parameters. Test isolated execution without OAK, agents, credentials, network use, or repository access; verify parameter identity and source-to-export predictions. The standalone implementation must not call the task oracle or infer hidden labels.

Keep old studies immutable. Maintain the learning index as evidence arrives. No merge into main or additional paid model service is authorised.

## Related primary work

[Deep Compression](https://arxiv.org/abs/1510.00149) combines pruning, quantisation, and coding. It motivates counting storage and metadata rather than only zeros. [The Lottery Ticket Hypothesis](https://arxiv.org/abs/1803.03635) studies sparse trainable subnetworks, not agents hand-placing weights. [Knowledge distillation](https://arxiv.org/abs/1503.02531) transfers behaviour to another model; a smaller model is not automatically an exact representation of its teacher. Abstracts checked on 6 September 2026. None establishes this experiment's agent-compression hypothesis.


## Implemented boundary

The closed compact profile uses four canonical OAK documents with typed calls and exact host tool names. Each kernel payload in OAK is a one-element list containing its named numerical descriptor, constrained by existing schema facilities and checked by the host. This packaging adds no grammar or invented OAK tensor type. New Python source, the study, the earlier attention source, and teacher documents were hashed before live observations. Old source and raw results are unchanged.

The final selections all use gains [2048, 2048, 8]. The fixed four-candidate control selects identical kernels. Full storage and stress failures are in the report and the learning index. The broader hypothesis remains unconfirmed.

## Reproduce

Install the repository dependencies and `experiments/agent-guided-network/requirements.txt`, then run from the repository root:

```sh
OPENBLAS_NUM_THREADS=1 python experiments/agent-guided-network/compression/run.py test
python -m tarfile -e experiments/agent-guided-network/results/compression-run/records.tar.xz /tmp/oak-compression-recorded
OPENBLAS_NUM_THREADS=1 python experiments/agent-guided-network/compression/run.py replay /tmp/oak-compression-replay --recorded /tmp/oak-compression-recorded
```

Replay regenerates every control, candidate, selected network, and standalone export. It reports zero new assistant decisions. A live run uses the same command prefix with `start RUN`, then `prepare RUN --seed SEED`, `propose RUN --seed SEED --kind identity --gains FIRST SECOND OUTPUT --rationale TEXT`, and a separate `apply RUN --seed SEED --number N`. Call `observe` before later proposals. Run `close` after all three seed selections, then `finish`. Use only the frozen study's seeds and budget; a changed protocol requires a separately identified study.
