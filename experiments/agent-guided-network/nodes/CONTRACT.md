# Numerical node contracts

Status: Proposed application contracts, not implemented OAK syntax or validators.
Purpose: Make a module's numerical meaning, update boundary, and revision identity explicit.

## Module record

Each module is one OAK document with a stable document path. The path identifies the module; do not add a new node identifier to OAK. Define exact input and output schema targets, an explicit forward process, supported numerical operation identities, and fixed parameter values for the revision.

A conceptual record must specify the following information. These names describe information requirements, not new OAK fields or a parallel configuration format.

| Information | Required meaning |
| --- | --- |
| Responsibility | What the module is intended to compute, distinguishable from evidence that it actually does so. |
| Inputs and outputs | Schema identity, tensor dimensions, dtype, axis order, channel meanings, and permitted batch dimensions. |
| Parameters | Constant targets, literal nested numerical values, tensor shape, dtype, and trainable/frozen designation. |
| Forward computation | Exact ordered operations, activation functions, numerical normalisation, and parameter use. |
| Connections | Explicit resolved process dependencies and input bindings, including aggregation order. |
| Update boundary | Allowed parameter targets, entry masks, norm bounds, and any fixed values that cannot change. |
| Numerical policy | Finite-value requirements, thresholds, supported precision, and tolerance policy. |
| Identity | Host-computed document and network revision evidence for reproducibility and drift rejection. |

The host adapter checks rectangular arrays, rank, dimensions, axis compatibility, finite values, and allowed numerical types. A nested JSON list is not sufficient evidence that those tensor constraints hold. Define how empty arrays, booleans, integers, and floating-point values are accepted or rejected before scoring a run.

Keep relation tables received for a particular example distinct from learned matrices that parameterise the computation. Do not accidentally memorise dataset instances into supposed general-purpose weights.

## Ownership and lifetime

The canonical node document owns its inline parameter values. Tensor objects loaded into the backend are derived working representations. Wrappers and solvers cannot become an alternative source of truth.

A proposal produces a detached candidate. Acceptance creates a new document revision and a corresponding compatible network snapshot. No parameter writes occur during a scored forward pass. Optimiser state and training observations belong to the training host or explicitly scoped training state, not hidden inference dependencies.

The whole snapshot must identify its topology, all referenced document revisions, numerical operation versions, preprocessing, dtype policy, and output decoding. Use host-computed content identities; an agent-written revision label is not verification evidence. The exact canonical hashing and parameter-serialisation procedure must be fixed before implementation claims reproducible snapshots.

## Initial module granularity

Aim for about 16 coherent modules, with relation selection, composition, evidence aggregation, conflict handling, and readout as candidate responsibilities. This is a design target, not a frozen layer architecture or a claim that every latent dimension has a human meaning.

Freeze the exact topology, equations, tensor shapes, and trainable parameter count before any scored comparison. Each baseline must use that same network unless the comparison explicitly studies a different architecture. Start with an acyclic graph; do not create illegal cyclic process calls to approximate recurrence.

## Learning records

The eventual OAK schemas must carry:

| Record | Minimum information |
| --- | --- |
| Observation | Network revision, module path, case identifiers, permitted inputs/outputs, diagnostic values, and measurement origin. |
| Proposal | Baseline network revision, target module and constants, mechanism, correction cases or numerical edits, preservation cases, and bounded fitting budget. |
| Candidate | Proposal identity, resulting parameter values, resulting snapshot identity, solver settings, and validation results. |
| Evaluation | Exact subject revision, evaluator version, split identity, seed, measured metrics, resource use, and observed pass/fail results. |
| Decision | Candidate and incumbent revisions, applicable acceptance rule, evidence references, and accepted/rejected/stale outcome. |

Rationales are optional explanatory records, never substitutes for these values. Candidate code execution is not an allowed proposal form in the first experiment. Implement these shapes with existing OAK facilities when the runtime work starts; do not invent task-specific YAML, custom tensor grammar, or claimed working APIs in this documentation stage.

## Acceptance boundary

The effect-producing host must reject a changed baseline immediately before committing an accepted update. A candidate can be schema-valid yet numerically invalid, correctly measured yet stale, or locally useful yet globally harmful. Each rejection is distinct and recorded.

The [training protocol](../training/PROTOCOL.md) owns update sequencing. The [export contract](../runtime/EXPORT.md) owns inference closure. [EXPERIMENT.md](../EXPERIMENT.md) owns the research intent.
