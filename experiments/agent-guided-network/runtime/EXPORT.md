# Numerical runtime and export contract

Status: Proposed; no numerical adapter or exporter is implemented.

## Runtime boundary

Construct a numerical graph from resolved, validated OAK documents and a restricted registry of host-implemented operations. Keep exact OAK schema identities and document scopes. An exact named-tool action is a dispatch boundary, not proof that the tool is pure, differentiable, or exportable.

The initial operation set should include only what the frozen benchmark requires. Candidate categories include matrix multiplication, elementwise arithmetic, declared activation functions, fixed-axis reductions, concatenation, and explicit numerical selection. These are design categories, not already registered tool names. Each actual operation needs defined shapes, dtypes, numerical behaviour, implementation identity, and export support.

Preserve the numerical backend's computation graph and gradients. Do not repeatedly render intermediate tensors to OAK text or route tensor edges through outside-arrival triggers. One host invocation may execute the compiled graph while OAK retains the source contracts and composition.

Start with an acyclic, bounded graph and no external side effects. Keep parameter revisions fixed for a forward pass. Any later recurrence or persistent inference state requires a new explicit contract and a corresponding test treatment.

## Export eligibility

An inference entry point is eligible only when its reachable computation is closed over declared numerical operations, parameter constants, approved input preparation, required numerical state, and output decoding.

Reject an export containing unresolved interpreter-native actions, natural-language routing, network calls, undeclared preprocessing, external language-model encoders, or agent-based answer repair. Reject unsupported operations rather than silently falling back to an agent. Training-only documents may remain as source material, but no reachable inference dependency may require them.

Never remove behaviour-affecting instructions and call the result equivalent. Such a node must be redesigned so its inference meaning is fully executable. General OAK documents are not promised to satisfy this restricted contract.

## Artifact and reproducibility

The deployment artifact must include or identify the numerical graph, parameter values, source snapshot, operator versions, dtype/shape policy, preprocessing, decoding, and required state initialisation. A model file without these dependencies is not the full network.

OAK documents remain the maintained source. Backend parameter objects and any deployment model are derived artifacts. Compare the exported constants against the accepted source revision after the declared dtype conversion; do not rely only on test outputs to detect parameter drift.

PyTorch-to-ONNX export and ONNX Runtime are candidate implementation tools, subject to supported operations and pinned versions. [R09 in the source register](../research/SOURCES.md) supports that route, not export of arbitrary OAK.

## Required tests

| Check | Evidence required |
| --- | --- |
| No-agent forward path | Numerical computation succeeds without constructing wrappers or calling a language model. |
| Dependency closure | Reachable operations and all required input/output transformations are identified; forbidden dependencies are rejected. |
| Parameter identity | Exported parameters match the accepted node revisions under declared numerical conversion. |
| Clean loading | A new process with no credentials, network access, training memory, or ambient files loads the complete artifact. |
| Numerical equivalence | Reference and export agree within predeclared absolute and relative tolerances on normal, boundary, and held-out cases. |
| Decision equivalence | Thresholded outputs are checked separately, especially near decision boundaries. |
| Negative cases | Missing weights, wrong shapes, unsupported operations, hidden agent calls, and changed source revisions fail explicitly. |

Test with evaluation-mode behaviour and controlled random seeds where relevant. Numerical closeness on samples is not a proof of equivalence for all possible inputs. Report the coverage and remaining uncertainty.

The same checks apply before and after agent-guided learning. Unwrapping removes training support; it must not introduce a new model whose differences obscure what was learned.
