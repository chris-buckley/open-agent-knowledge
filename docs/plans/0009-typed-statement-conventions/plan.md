# Typed statement conventions from one working example

Prepared: 2026-09-05T21:46:45+10:00
Classification: PUBLIC

Plan: 0009-typed-statement-conventions
Format: `examples/schemas/smeac_plan.oak.md`
Repository: `chris-buckley/open-agent-knowledge`
Baseline: `main` at `4fd86cee4b85bb946a9c8ce7eab2c405e5568144`
Branch: `plan/typed-statement-conventions`
Plan status: Ready for implementation approval.
Execution status: Not started. All implementation tasks remain open.
Authorization gate: This request authorizes this plan and its new branch only. A later explicit instruction to implement authorizes delivery through a review pull request. Merging requires separate authorization.

## 1. Situation

### Operating Environment
OAK uses schemas and explicit bindings to constrain process values. This change improves one existing example and shared authoring guidance, not the language grammar or execution engine.

### Current State
The merged scenario collection supplies a four-stage teaching core to both the authoring skill and assembled agent. `examples/shape_writer/example.py` already gives `process.decide-change` input and output schemas, named bindings, and a deterministic fixture. Naming and contract guidance already lives in `oak/rules/guidance.py`; extend that owner rather than create another vocabulary system.

### Challenges
- Ambiguous promises: a verb can conceal whether work checks a contract, makes a judgment, or requests an external effect.
- False typing: capitalised placeholders do not create semantic types, and schema-valid answers are not necessarily correct.
- Identity drift: edits to shared guidance change the optional validator's whole-package fingerprint even when validation behaviour stays unchanged.
- Size pressure: the assembled agent must remain within 64,000 bytes; the skill entry remains limited to 10,000 bytes and 500 lines.

### Supporting Factors
- Higher intent: make inputs, relationships, results, and effects explicit while preserving natural language where interpretation is needed.
- Adjacent efforts: retain the merged self-contained scenarios, shared teaching, scope-safe assembly, and verification.
- Supporting resources: existing schemas, source generators, deterministic fixtures, detached demonstrations, and repository checks.

### Assumptions
- The existing decision step can demonstrate the convention without another process, schema, or scenario.
- Clearer wording need not change the task, contracts, or surrounding control flow.
- Fixture equivalence proves only the tested dataflow. Preserving the intended judgment also requires explicit prose review.

### Constraints and Limitations
- Constraint: leave grammar, reserved words, datatypes, parser acceptance, model fields, resolver and execution semantics, shared schema definitions, and dependency requirements unchanged.
- Constraint: refine one example process. No broad renaming, function registry, glossary subsystem, noun-verb parser, mandatory style checker, or task-specific format.
- Constraint: preserve exact tool names, document identities, part responsibilities, lifetimes, schema targets, binding names, step order, and the four-stage teaching core.
- Constraint: conventions remain advisory. Valid alternative prose remains valid OAK; preferred verbs are not commands or capabilities.
- Limitation: this pilot's role values are constrained strings, not new Evidence or Finding datatypes. Their truth and quality remain outside structural validation.

## 2. Mission

The implementing agent refines one typed decision statement and derives compact shared authoring guidance on the named branch after execution approval, then delivers verified examples and both authoring forms in a review pull request.

Task: Complete the five phases as one bounded change before requesting implementation review.
Purpose: Standardise what an authored action promises, not merely how it sounds.
End state: One working exemplar shows explicit roles; a few source-owned conventions explain construction, verb responsibility, and validation limits; generated teaching stays identical across skill and agent; applicable checks pass.

## 3. Execution

Intent: Refine the real decision step, then extract only guidance that helps explain it. Preserve its contracts and use the smallest useful wording change. Do not turn English vocabulary into another execution language.
Concept of operations: Capture the pilot baseline, clarify the statement, and test preserved contracts. Derive shared guidance through existing owners. Refresh capability identity and generated products, then complete verification and PR delivery on this branch.

### Selected pilot

Owner: `examples/shape_writer/example.py`, `decide_change_process`, target `process.decide-change`.

Current action text:

```text
For <CRITERION>, weigh <CURRENT> against <PROPOSED> and produce <DECISION> and <RATIONALE>.
```

Proposed action text:

```text
Assess <CURRENT> and <PROPOSED> against <CRITERION>; produce <DECISION> and <RATIONALE>.
```

Keep the existing process name, `shape_gallery.oak.md#schema.option-comparison` input, and `shape_gallery.oak.md#schema.decision-brief` output. Preserve the ACT schema attributes, bindings, and outputs. The sentence is not itself the typed contract, a new ASSESS command, or evidence of improved model performance.

| Role | Existing binding | Contract |
| --- | --- | --- |
| Subjects | CURRENT, PROPOSED | Comparison-cell strings. |
| Standard | CRITERION | Comparison-cell string. |
| Judgment | DECISION | Non-empty string. |
| Explanation | RATIONALE | Non-empty string. |

### Guidance to extract

Describe an action with its participants and relationship, and identify results when the task produces them. Bind roles to existing schemas where values need validation. Omit roles that are not needed; do not force every sentence into one template.

Use a contextual contrast: `validate` checks an identified contract; `assess` makes a judgment against a criterion; `publish` requests an external effect whose implementation and authority remain with the host. Emitting an interface instance is not proof of external publication. These are preferred descriptions, not reserved tokens or newly executable operators.

Separate role names, structural validation, and evidential claims. A well-formed rationale can be wrong; declaring a tool does not supply it; fluent prose does not implement an effect. Keep these distinctions in shared guidance without a new truth checker or weakened validation.

### Phase 1: Establish the baseline
Objective: Capture the exact contracts and scope that the wording change must preserve.
- [ ] Key task: P01.01 Read applicable AGENTS owners, the pilot and its schema/fixture dependencies, authoring generators, relevant checks, and matching specialist references before editing.
- [ ] Key task: P01.02 Record baseline checks, pilot structure, fixture outputs, product sizes, protected file fingerprints, and validator identity in implementation evidence.
- [ ] Key task: P01.03 Review the proposed sentence against the role table; record that no subject, criterion, output, authority, or proof obligation is lost or invented.
Success criteria: Evidence identifies the exact pilot, protected contracts, observed baseline results, and the limited intended prose change.
Transition trigger: Baseline evidence and the role-preservation review are recorded under this plan.

### Phase 2: Refine one exemplar
Objective: Demonstrate the convention through the existing pipeline rather than a new tutorial subsystem.
- [ ] Key task: P02.01 Refine only the selected ACT sentence in its Python source, retaining process identity, schemas, bindings, call order, and the existing sample.
- [ ] Key task: P02.02 Record the before/after role explanation in completion evidence; use the generated working example as the portable exemplar instead of maintaining a second authored copy.
- [ ] Key task: P02.03 Extend existing checks for valid bindings, missing or wrong-type values, unexpected outputs, and non-empty but unjustified decision text; distinguish structural rejection from a shape-valid judgment that still needs review.
Success criteria: Fixture outputs and layouts stay the same. Existing mechanisms reject malformed values without misreporting valid structure as sound reasoning. Structural comparison permits only the reviewed action-text change.
Transition trigger: Focused checks pass and their evidential limits are recorded.

### Phase 3: Derive shared conventions
Objective: Extract a few reusable rules without new syntax or a large vocabulary catalogue.
- [ ] Key task: P03.01 Refine overlapping entries in `oak/rules/guidance.py`; add only indispensable rules for explicit roles, relationships, schema-backed bindings, and appropriate outputs or effects.
- [ ] Key task: P03.02 Include the validate/assess/publish contrast and validation limits while preserving alternative domain wording and exact tool names. Do not turn the contrast into a callable vocabulary.
- [ ] Key task: P03.03 Assign every changed or added rule one guide owner in `build/authoring_guides.py`; update applicable AGENTS pointers only where needed, without copying the rules into multiple owners.
- [ ] Key task: P03.04 Extend existing guidance checks for single ownership and shared delivery; demonstrate that alternative well-formed ACT prose still parses. Do not implement English-word rejection or claim general semantic equivalence from fixtures.
Success criteria: Each convention has one maintained source and a concrete exemplar. No registry, mandatory phrase template, new format, or parser restriction has appeared.
Transition trigger: Shared ownership and focused authoring checks pass within the agreed scope.

### Phase 4: Refresh the capability
Objective: Deliver matching skill and agent knowledge with truthful identity and unchanged scope.
- [ ] Key task: P04.01 Commit changed package sources, pin the optional validator to that immutable source revision, recompute the complete package fingerprint, and confirm the unchanged dependency fingerprint. Advance skill version 2.1.0 to 2.2.0 without changing validator logic or consent behaviour.
- [ ] Key task: P04.02 Regenerate scenario snapshots, catalogue, skill references, teaching documents, assembled agent, and affected generated authoring reference through source owners. Never patch generated files by hand.
- [ ] Key task: P04.03 Preserve existing size and line limits. Revise overlapping guidance or shorten redundant explanation in touched guides without removing obligations, teaching documents, grammar material, or validator consent information; do not raise the limits.
- [ ] Key task: P04.04 Verify skill/agent knowledge and execution parity, closed detached teaching bundles, inert embedded examples, and rejection of supporting operational fusion.
Success criteria: Fingerprints match the retrievable pinned revision; generated forms share the changed guidance and full teaching mapping; budgets and scope checks pass. Grammar, shared schemas, dependencies, and runtime implementation stay unchanged.
Transition trigger: Generated products and capability identity pass their checks together.

### Phase 5: Verify and deliver
Objective: Complete the bounded change with reproducible evidence and a review pull request.
- [ ] Key task: P05.01 Run compilation, catalogue and package generators, `python -m build.examples`, and `python build/examples.py`, retaining detached, rejection, scope, and parity checks.
- [ ] Key task: P05.02 Run the existing approved detached validator bootstrap and cache-reuse integration against the new immutable revision, preserving separate end-user installation consent in both authoring forms.
- [ ] Key task: P05.03 Repeat generation with no product diff; compare protected files and pilot structures to the baseline; remove obsolete live teaching wording while preserving historical before/after evidence.
- [ ] Key task: P05.04 Review the final diff for changed meaning, duplicated guidance, invented capabilities, and overstated proof; fix findings and re-run affected checks before recording the verdict.
- [ ] Key task: P05.05 Commit the complete change and `report.md` with per-task evidence, open its PR to main, verify final-head CI, and complete checkboxes only against observed evidence. Do not merge.
Success criteria: All applicable tasks have evidence, both full checks and final-head CI pass, generation is stable, and the unmerged PR links the plan and report. Blocked tasks remain explicitly open.
Transition trigger: The complete change is delivered for review at a verified final head.

### Coordinating Instructions
- Timeline: create the plan now; start execution only after explicit approval. These phases constitute one delivery, not deferred feature releases.
- Boundaries: matrix/collection types, typeshed import, ontologies, function systems, backend replacement, and wider vocabulary standardisation are outside this change.
- Operating guidelines: example first, one owner per rule, preserved negation and obligation, existing generators and verification entry points.
- Risk mitigation: review prose separately from structural tests; retain fixture-host disclosures; account for package fingerprints before capability publication.

### Contingencies
- If main or the branch changes before execution, inspect the delta and reconcile only necessary changes without overwriting newer work.
- If the proposed sentence changes meaning, use a smaller clarification of the same process and explain why; do not expand the pilot or alter its schemas.
- If the agent exceeds its budget, remove redundancy within touched guidance while retaining meaning and required material; do not shrink the teaching contract or silently increase limits.
- If the pinned revision is unavailable or verification cannot run, record the actual failure and leave the task open rather than using a stale identity or claiming success.

## 4. Admin and Logistics

| Resource | Quantity | Source | Status |
| --- | --- | --- | --- |
| Pilot and fixture | One existing process | `examples/shape_writer/example.py` and scenario | AVAILABLE |
| Shared contracts | Two existing schemas | `examples/schemas/shape_gallery.py` | AVAILABLE |
| Guidance and packaging | Existing owners | `oak/rules/guidance.py`, `build/authoring_guides.py`, `build/authoring.py` | AVAILABLE |
| Verification | Existing checks and CI | `build/checks/`, `build/AGENTS.md`, `.github/workflows/verify.yml` | AVAILABLE |
| Execution approval | One explicit instruction | User | PENDING |

Supply: Reuse existing dependencies and fixtures. Add no package, runtime service, model account, or dataset.
Transportation: Commit sources and generated products to this branch. The eventual PR carries the diff; shared generators deliver identical teaching to both forms.
Sustainment: Keep this stable plan path. Add `report.md` and populated evidence during implementation as needed, with exact commands, revisions, outcomes, and limitations.
Rollback: Revert bounded implementation commits before merge if necessary. Keep source, validator identity, and generated products consistent; do not revert unrelated main changes.

## 5. Command and Signal

1. User: owns scope, implementation approval, and later merge authorization.
2. Implementing agent: executes the approved plan, records evidence, and fixes review findings within scope.

| Channel | Medium | Purpose | Cadence |
| --- | --- | --- | --- |
| Conversation | Short messages | Decisions, findings, blockers | Meaningful milestones |
| Plan and report | Versioned Markdown | Task state and evidence | As verified |
| Review PR | GitHub | Final diff and checks | Complete delivery |

Reporting: Separate observed structural validation, fixture behaviour, prose review, and untested model-quality claims. Identify the tested commit and checks actually performed.

| Decision | Authority | Escalation |
| --- | --- | --- |
| Create this plan and branch | Agent under current request | User |
| Implement and open its review PR | User's later explicit instruction | User |
| Add syntax, types, dependencies, mandatory wording, or a broader pilot | User | Stop scope expansion and report conflict |
| Merge | User's separate authorization | User |

### Acknowledgement
The scope is acknowledged as plan creation only. Readiness is not implementation approval, and no implementation result is claimed here.
