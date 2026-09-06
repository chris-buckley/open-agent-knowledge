# Research and repository evidence

Checked: 2026-09-05.
Scope: Primary-source metadata and abstracts, plus the official export documentation. This register does not claim experimental replication or exhaustive literature coverage. The proposed OAK system has not been validated by these papers.

## R01: Tensor Logic

Pedro Domingos. [Tensor Logic: The Language of AI](https://arxiv.org/abs/2510.12269v3). Submitted 14 October 2025; version 3 dated 16 October 2025.

The paper proposes a tensor-equation representation connecting logical rules and neural computation. It motivates representing relations and computations numerically in the same system. It does not demonstrate local language-model agents training OAK-defined modules, and its argument must not be treated as a guarantee that learned embeddings yield exact logical proofs.

Use here: mathematical motivation, not an implementation dependency or proof of the learning hypothesis.

## R02: OPRO

Chengrun Yang and colleagues. [Large Language Models as Optimizers](https://arxiv.org/abs/2309.03409v3). Submitted 7 September 2023; version 3 dated 15 April 2024; ICLR 2024.

OPRO generates proposals using previous candidates and their measured objective values. Its examples include small numerical optimisation problems, while its main application is prompt optimisation. This supports a propose-measure-repeat loop. It does not establish efficient direct generation of a large network's dense weights.

Use here: candidate-generation precedent and a reason to measure the numerical task rather than judge the explanation.

## R03: ROME

Kevin Meng, David Bau, Alex Andonian, and Yonatan Belinkov. [Locating and Editing Factual Associations in GPT](https://arxiv.org/abs/2202.05262v5). Submitted 10 February 2022; version 5 dated 13 January 2023; NeurIPS 2022.

ROME studies factual associations in pretrained transformers and modifies selected feed-forward weights using rank-one model editing. It provides evidence that concrete behavioural changes can be materialised as weight edits. It is not training a new distributed OAK network from scratch.

Use here: targeted numerical edits and evaluation of preservation, not a claim that arbitrary edits are safe.

## R04: MEMIT

Kevin Meng and colleagues. [Mass-Editing Memory in a Transformer](https://arxiv.org/abs/2210.07229v2). Submitted 13 October 2022; version 2 dated 1 August 2023.

MEMIT extends direct model editing to many factual associations in pretrained language models. Its setting and measurements differ from independent node agents learning a modular numerical system.

Use here: batched-edit precedent, not evidence that independently proposed updates can be combined without whole-network tests.

## R05: AlphaEvolve

Alexander Novikov and colleagues. [AlphaEvolve: A coding agent for scientific and algorithmic discovery](https://arxiv.org/abs/2506.13131v1). Submitted 16 June 2025; white paper.

AlphaEvolve uses language-model-generated code changes, evolutionary search, and evaluator feedback to improve algorithms. Its contribution relevant here is the separation between proposed changes and measured acceptance. Code evolution is not the parameter-only treatment proposed for this first experiment.

Use here: evaluator-governed search and retained candidates, not evidence for local weight-learning superiority.

## R06: FunL2O

Bingheng Li and colleagues. [FunL2O: LLM-Guided Feature Function Design for Learning to Optimize](https://arxiv.org/abs/2607.27389v1). Submitted 29 July 2026; preprint.

FunL2O proposes executable feature functions with an LLM, retrains the original learning-to-optimise model, and measures downstream performance using a fixed evaluation process. It is a close design-stage precedent for agent assistance whose proposals become executable artifacts. The edited objects are feature functions, not individual node matrices.

Use here: distinguish proposal validity from downstream utility. Its reported results are the authors' results, not evidence from OAK or an independent reproduction.

## R07: Preservation and change

Akshat Gupta, Dev Sajnani, and Gopala Anumanchipalli. [A Unified Framework for Model Editing](https://arxiv.org/abs/2403.14236v5). Submitted 21 March 2024; version 5 dated 9 October 2024; EMNLP 2024 Findings.

The paper relates ROME and MEMIT through a preservation-memorisation objective and introduces EMMET. It motivates explicitly balancing desired changes against retained behaviour. The regularised linear fitting objective in this experiment is our illustrative adaptation, not an assertion that the paper studied agent-generated local training targets.

Use here: formalise preservation alongside correction; do not equate sample preservation with a global guarantee.

## R08: Meaningful intermediate representations

Pang Wei Koh and colleagues. [Concept Bottleneck Models](https://proceedings.mlr.press/v119/koh20a.html). ICML 2020, PMLR 119, pages 5338-5348.

The work studies models that predict supplied concepts and use those concepts to predict labels, enabling intervention on intermediate representations. It motivates semantically meaningful module interfaces. Names alone do not establish those semantics. The paper's test-time concept interventions are not allowed in this experiment's agent-free inference path.

Use here: representation design and intervention tests, with any concept supervision disclosed to baselines.

## R09: Numerical export

PyTorch maintainers. [Export a PyTorch model to ONNX](https://docs.pytorch.org/tutorials/beginner/onnx/export_simple_model_to_onnx_tutorial.html). Official documentation checked 5 September 2026.

The tutorial documents exporting supported PyTorch computation and running/comparing it with ONNX Runtime. It supports one possible deployment path, not a compiler for arbitrary OAK processes. The page is maintained documentation; this register does not pin an experiment dependency to whichever release currently serves it.

Use here: select and pin actual backend versions, supported operations, and numerical tolerances when implementing the adapter.

## Repository evidence at the baseline

The inspected baseline is `cd1f8aed74b24f8515a3e176972e9f2cbcb53e5a`. Follow the current owning documents before later implementation; these references describe what grounded this design, not frozen authority over future OAK changes.

| Owner or source | Relevant contract |
| --- | --- |
| [Root AGENTS](../../../AGENTS.md) | Part-first authoring, scoped ownership, and repository workflow. |
| [Package owner](../../../oak/AGENTS.md) | OAK/host boundary and canonical representations. |
| [Node owner](../../../oak/node/AGENTS.md) | One idless node per document, part responsibilities, and value lifetimes. |
| [Constant model](../../../oak/node/parts/constants.py) | JSON-valued constants and optional schema binding, not tensor arithmetic. |
| [Execution owner](../../../oak/execute/AGENTS.md) | Exact named-tool actions, native interpretation, transaction semantics, and host boundaries. |
| [Resolution owner](../../../oak/resolve/AGENTS.md) | Explicit loading and relative targets; process-call cycles are rejected. |
| [Build owner](../../../build/AGENTS.md) | Complete verification entry points and generated-product freshness. |
| [Plan owner](../../../docs/AGENTS.md) | Numbered plan storage and SMEAC format. |

## Claim discipline

The proposed agent/solver division, node-local ownership, revision-aware coordination, and evaluation design are synthesis decisions. No source above proves the combined method, establishes its novelty, or licenses claims of superior learning. Record a negative or inconclusive outcome honestly. Do not promote a benchmark result from one setting into a general claim about neural learning or logical correctness.
