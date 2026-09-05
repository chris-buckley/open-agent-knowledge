# Attention extension

Authorised: 5 September 2026, on `experiment/agent-guided-network`.
Status: Implemented, measured, exported, and numerically replayed. See [the attention report](../results/attention-run/REPORT.md).
Prior evidence: [First-run report](../results/first-run/REPORT.md), retained unchanged.

## Intent and boundary

Add a real attention OAK document, not an agent instruction to pay attention. The running assistant continues acting sequentially for the logical node roles. Every prediction is numerical before, during, and after learning. Accepted edits revise inline matrix constants; no live constant changes or inference-time language-model calls are permitted.

The extension uses two sequential single-head cross-attention modules. This is the scaled dot-product mechanism used within Transformers, not a complete Transformer, multi-head implementation, decoder, language model, or hundred-node demonstration. It adds no OAK syntax or core runtime semantics.

## Computation

For each attention node, query and keys have width eight. The first value/output width is eight; the second is four:

```text
Q = query @ WQ
K = keys @ WK
V = values @ WV
A = softmax(mask(Q K^T / sqrt(8)))
output = (A V) @ WO
```

The first output becomes the second node's query. A fixed numerical softmax turns the second output into four class probabilities. The decoder is first-index argmax. Each node owns separate WQ, WK, WV, and WO matrices. Together these contain 416 trainable scalars, compared with 11 in the first study. Attention matrices A depend on the input and are temporary numerical activations, not learned parameter constants.

One/zero padding masks exclude invalid keys. All-masked rows, non-finite values, booleans, strings, invalid dimensions, and unsupported documents are rejected. This is non-causal table lookup; no autoregressive causal-mask behaviour is claimed. Permuting keys, values, and masks together must preserve output.

## Harder task

A query identifies an entry in a first key/value table. That entry's value identifies an entry in a second table. The second entry carries the target class. Every example supplies new random continuous keys and values, with distractors and padding. The target indices and labels are not inference inputs.

Training and development contain three to six valid entries per table. The final study evaluates fresh examples with the same distribution, sixteen-entry tables, and sixteen-entry tables containing nearly identical distractor keys. The last two are held-out stress tests, not data used to select agent updates. Their failure is a valid finding.

The key/query matrices begin as independent random matrices. Value/output matrices begin near identity for every treatment. This architectural prior is disclosed; the system does not discover the task formulation from prose.

## Study and controls

[The canonical OAK study](study.oak.md) freezes sampling, equations, methods, learning budgets, tolerances, acceptance, information access, and the separate seed-zero pilot. `study.py` is its authoring source. Source and data hashes are recorded before scored proposals.

Each seed has a common 80-step warm-up. A strong numerical baseline receives 600 further Adam steps with development-selected checkpoints. A non-agent control adds a fixed nine-candidate attention/output scaling grid. The assistant may make up to four proposals: targeted or joint fitting, bounded query/key scaling with fitting, direct sharpening, or direct output calibration. Each fitting proposal costs 150 gradient steps; direct proposals cost zero. Candidate and gradient counts are recorded separately. There is no claim of matched total cost when conversation telemetry is unavailable.

All fitting uses the same final training labels. The agent also sees aggregate alignment and entropy diagnostics; these are not intermediate fitting targets. This information distinction is reported, rather than pretending identical supervision implies identical diagnostic access.

The agent makes fresh decisions only for seed 7. Seeds 19 and 31 numerically replay its chosen methods and independently apply the fixed acceptance rule. Replay is not a new agent session. No instruction/meaning ablation or independent-agent benefit is established by this treatment.

Selection closes before final metrics. Post-selection uniform-attention interventions separately disable either attention block or both, without retraining. They test functional dependence, not a fair comparison between trained architectures or a universal explanation of the learned matrices.

## OAK and delivery structure

`author.py` defines four canonical documents per snapshot: `attention.oak.md`, `attention-readout.oak.md`, `network.oak.md`, and `contracts.oak.md`. The two attention documents own matrices and typed processes. The root owns request routing, explicit calls, numerical decoding, and emission. The closed host profile checks whole-document structural equality before lowering; it does not silently drop prose or unsupported actions.

Representative snapshots belong under `../nodes/attention-initial/` and `../nodes/attention-learned/`. Actual observations, proposals, candidate decisions, selected revisions, and metrics belong under `../results/attention-run/`. The full run retains every candidate snapshot and standalone export; committed reports and replay reproduce them.

`numeric.py` is also the standalone exported implementation. Exports contain the complete numerical pipeline, matrices, source revision, and hashes. Clean isolated processes block network and repository reads. Exact output and decision checks cover each test regime, with separate OAK-executor parity samples. Passing sampled checks is not a proof for all possible inputs.

## Commands

Install the existing repository dependencies and experiment-local requirements. From the repository root:

```sh
OPENBLAS_NUM_THREADS=1 python experiments/agent-guided-network/attention/run.py test
OPENBLAS_NUM_THREADS=1 python experiments/agent-guided-network/attention/run.py prepare /tmp/oak-attention
OPENBLAS_NUM_THREADS=1 python experiments/agent-guided-network/attention/run.py observe /tmp/oak-attention
```

Use `propose` with `--method` and `--rationale`, then a separate `apply --proposal PATH`. After all proposals are evaluated, `finish` freezes selection and evaluates tests and exports. `replay DESTINATION --recorded experiments/agent-guided-network/results/attention-run` reproduces recorded numerical decisions, not new language-model reasoning.

## Primary sources

[Attention Is All You Need, section 3.2.1](https://arxiv.org/html/1706.03762v7) defines scaled dot-product attention; section 3.2.3 distinguishes cross-attention and self-attention. Inspected 5 September 2026. The paper supports the mathematical mechanism, not the hypothesis that temporary OAK agents improve training.

[NumPy einsum documentation](https://numpy.org/doc/stable/reference/generated/numpy.einsum.html) documents the explicit indexed contractions used by this implementation. The experiment retains the existing NumPy dependency and checks all 416 gradient entries by finite differences.
