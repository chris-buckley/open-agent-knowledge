# Typed statement conventions from one working example

Prepared: 2026-09-05T21:46:45+10:00
Classification: PUBLIC

Plan: 0009-typed-statement-conventions
Format: `examples/schemas/smeac_plan.oak.md`
Repository: `chris-buckley/open-agent-knowledge`
Baseline: `main` at `4fd86cee4b85bb946a9c8ce7eab2c405e5568144`
Branch: `plan/typed-statement-conventions`
Plan status: In progress.
Execution status: 17 of 19 tasks verified locally; pinned bootstrap and PR delivery remain open.
Authorization gate: The user authorized end-to-end implementation and a review pull request at 2026-09-05T22:05:29+10:00. Merging requires separate authorization.

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

### Worked examples from the original conversation

These examples make the intended change reviewable. E01-E04 explain the bounded pilot and its shared guidance; E05-E07 retain the wider conversation as context and explicit non-goals. None authorizes another process, schema, datatype, keyword, tool, or teaching scenario. Code fences below are plan illustrations, not generated product files or claims of executed checks. The 19 implementation tasks remain unchanged; their verified status is tracked below.

#### E01: From a vague instruction to explicit roles

Illustrative weak wording from the conversation, not a quotation from the existing example:

```text
Review the information and decide what to do.
```

Role-explicit wording from the conversation:

```text
Assess <EVIDENCE> against <CRITERION>;
produce <FINDING> and <RATIONALE>.
```

The subject is the evidence, the standard is the criterion, and the results are a finding and its rationale. Names alone do not supply these values, validate them, or prove that the assessment is right. Existing input/output schemas and bindings must carry the actual contract.

The selected pilot uses CURRENT and PROPOSED as its subjects, CRITERION as its standard, and DECISION and RATIONALE as its results. Keep those existing names. Do not rename them to EVIDENCE or FINDING merely to imitate the conversational example, and do not introduce nominal Evidence or Finding types.

Other role patterns illustrate why a fixed noun-verb sequence is too weak:

```text
Select <CANDIDATE> from <CANDIDATES> using <CRITERION>.
Derive <RESULT> from <INPUT> using <RULE>.
Publish <REPORT> to <DESTINATION>.
```

These are prose patterns, not callable signatures or new commands. Selection needs candidates and a criterion; derivation needs inputs and a rule; publication needs an authorized effect and a destination. Do not invent a collection contract, result receipt, or host capability to fill an attractive template. Include only roles justified by the task.

#### E02: The actual pilot in Python and OAK

The current and proposed action sentences are recorded above under Selected pilot. This is the proposed ACT expression inside the existing `decide_change_process.steps`, using its existing imports, constants, helper, and schemas:

```python
ACT(
    "Assess <CURRENT> and <PROPOSED> against <CRITERION>; "
    "produce <DECISION> and <RATIONALE>.",
    input=SCHEMA_COMPARISON,
    output=SCHEMA_DECISION,
    inputs=local_bindings(PLACEHOLDERS_COMPARISON),
    outputs=PLACEHOLDERS_DECISION,
)
```

The corresponding current-syntax OAK fragment is below. It belongs inside the existing `process.decide-change`; it is not a complete standalone document. The referenced local schema document and visible input bindings remain required.

```text
ACT input="shape_gallery.oak.md#schema.option-comparison" output="shape_gallery.oak.md#schema.decision-brief": Assess <CURRENT> and <PROPOSED> against <CRITERION>; produce <DECISION> and <RATIONALE>. (
  CRITERION=$CRITERION,
  CURRENT=$CURRENT,
  PROPOSED=$PROPOSED,
) -> DECISION, RATIONALE
```

Only the instruction string changes. The input role order, schema identities, immutable local bindings, declared outputs, process identity, surrounding CALLs, and emission order stay unchanged. ACT remains interpreter-native; the example does not add an ASSESS opcode or a named tool.

For the same intended task, an alternative such as the following must remain syntactically acceptable. Its wording still needs human meaning review; parser acceptance is not proof of semantic equivalence.

```text
Compare <CURRENT> with <PROPOSED> using <CRITERION>;
produce <DECISION> and explain it in <RATIONALE>.
```

#### E03: Populated values and honest validation boundaries

The existing fixture supplies these decision-step inputs:

```json
{"CRITERION": "Blank title", "CURRENT": "Accepted", "PROPOSED": "Rejected"}
```

Its existing expected output bindings are unchanged:

```json
{"DECISION": "Reject blank titles.", "RATIONALE": "A title must identify the task."}
```

The populated decision schema remains shaped information rather than a copy of its definition:

```markdown
## Decision
Reject blank titles.

### Rationale
A title must identify the task.
```

The constraints and expected check behaviour below come from the pilot's existing schemas in `examples/schemas/shape_gallery.py` and the existing action boundary. They specify implementation checks to retain or add, not tests already performed by this plan amendment.

| Case | Example change | Expected boundary |
| --- | --- | --- |
| Valid fixture | Use the input and output objects above. | Binding validation succeeds; the demonstration also compares the exact expected result. |
| Wrong input type | Set CURRENT to the number 23. | The input schema rejects a number where a string is required. |
| Missing result | Omit RATIONALE. | Complete output binding validation rejects the missing role. |
| Empty result | Set DECISION to an empty string. | The decision schema's non-empty constraint rejects it. |
| Unexpected result | Add an undeclared CONFIDENCE output. | The action's exact declared-output boundary rejects the extra output. |
| Well-formed but contrary judgment | Set DECISION to "Accept blank titles." and RATIONALE to "No reason is needed." | Both remain non-empty strings, so the schema alone accepts them. The exact fixture expectation differs, and judgment quality still requires review. |

The final row is essential: a deterministic fixture demonstrates specific dataflow and expected values, not general correctness of an interpreter's reasoning. Better words do not turn structural validation into a truth checker. Pydantic remains the structural validation backend; this change neither replaces it nor claims that arbitrary English is validated by Rust.

#### E04: Verbs describe different promises

The following are advisory sentence examples, not additional implementation targets:

| Verb | Role-explicit prose | What it promises, and what it does not |
| --- | --- | --- |
| validate | Validate the payload against the named schema; report violations. | Check an identified contract through an actual check. Do not infer that one ran merely from a valid report shape. |
| assess | Assess the evidence against the criterion; produce a finding and rationale. | Make a judgment against an explicit standard. Do not label it a deterministic proof unless evidence supports that claim. |
| publish | Publish the report to the destination. | Request an external effect through an available, authorized host capability. Do not invent a tool or claim delivery before its result is observed. |

A generated report is not automatically a published report. An EMIT step stages a complete interface instance under OAK execution semantics; successful host delivery is a separate claim. Native ACT is not automatically pure, and a verb alone does not determine whether an action has external effects. Keep those effects and their evidence explicit where the task requires them.

Use the validate/assess/publish contrast in the shared guidance. Do not mechanically replace every use of review, check, weigh, decide, or another domain verb. This plan is about clear responsibility, not a universal synonym ban.

#### E05: Function templates and modifiers without a second language

The original typeshed sampling suggested templates such as `is_<state>`, `is_<relation>_to`, `contains_<what>`, and `<verb>_<object>`, plus modifiers such as negation and `_ignoring_<aspect>`. Retain the useful idea of a base meaning with explicit participants. Do not import those spellings as functions or extend the condition grammar in this pilot.

For relationships that OAK already supports, the sampled name can point to an existing expression rather than create an alias:

| Sampled vocabulary idea | Existing OAK condition fragment | Interpretation |
| --- | --- | --- |
| is_equal_to | `$CURRENT equals $PROPOSED` | Compare two already bound values. |
| is_not_equal_to | `NOT($CURRENT equals $PROPOSED)` | Negate the comparison result; no new negative predicate is introduced. |
| is_greater_than_or_equal_to | `$COUNT is at least $constant.minimum-count` | Use the established ordered-comparison phrase. |

These fragments assume the referenced bindings or constant exist and are valid for their comparisons. They do not add those bindings to the pilot, and an evaluation error is not a false value that negation turns into success.

Potential future vocabulary still needs a contract, not just a grammatical suffix:

| Earlier idea | Question that must be settled before any future implementation |
| --- | --- |
| equal to, greater than, subset of | What operand types and relation semantics apply? A preposition is wording, not a type system. |
| contains_only | Are duplicates allowed, is order meaningful, and must every listed value occur? |
| is_close_to | Which absolute or relative tolerance applies, and how are boundary cases handled? |
| is_equal_to_ignoring_case | Which explicit text-comparison policy applies? Do not infer it from the suffix alone. |
| is_file or contents_of | Is the operation checking a supplied observation or consulting the host filesystem? |
| send_body or disconnect | Which exact host capability implements the effect, and what result may be claimed? |

No typeshed harvesting, modifier engine, predicate registry, or additional operator is part of this plan. The relation examples clarify the distinction between vocabulary, typed arguments, and executable semantics.

#### E06: Locate the earlier concepts without reserving new words

This table preserves context from the original brainstorming. It is not an adopted glossary or a requirement to add all these terms to shared guidance.

| Original concepts | Concrete distinction to preserve |
| --- | --- |
| ENTITY and EVENT | A task is an entity under discussion; a task request arriving is an occurrence. Only outside arrivals route through triggers; ordered internal work stays in processes. |
| PREMISE and CONDITION | "Assume the supplied observations are complete" is a premise, not verified evidence. `$state.review-status equals "ready"` is a condition fragment, provided that state entry exists. |
| PERMITS | "The policy permits publication" describes a policy decision; it neither grants host credentials nor performs publication. |
| IN and OUT | Process input/output contracts describe local work; RECEIVES and EMITS describe document boundaries. Do not erase that distinction with one generic pair of labels. |
| DENOTES and DERIVE | "CRITERION denotes the comparison standard" explains a role. "Derive a result from inputs using a rule" describes work. |
| SENSE and ORGANISE | Prefer task-specific descriptions such as "Observe the supplied signal" or "Group the records by category" when those are the actual responsibilities. No observation or grouping capability is added here. |
| DEVOID | An empty string, an empty collection, a null value, and a missing binding are different cases; a poetic absence word must not collapse them. |
| RESPONSIBILITY and ATTENTION | Responsibility can identify who owns a check. Attention can describe which criterion to prioritise. Neither implies control over an interpreter's hidden model internals. |
| PROFOUND | State a reviewable objective such as "Explain the trade-off and one counterexample" rather than pretending a qualitative adjective is a deterministic constraint. |

The pilot takes only the immediately useful lesson: make participants, standards, outputs, and evidential limits explicit. Wider ontology and vocabulary design remains outside this delivery.

#### E07: Matrices remain context, not a hidden type extension

The earlier matrix discussion can already be illustrated as fixed JSON knowledge. This current-syntax constants fragment is explanatory and is not added to the selected scenario:

```text
<constants>
cost-matrix: [[2, 5, 8], [3, 7, 9]]

scenario-cube: [[[2, 5, 8], [3, 7, 9]], [[4, 6, 10], [5, 8, 12]]]
</constants>
```

These values illustrate a two-dimensional matrix and a three-axis array. Naming a constant matrix or cube does not itself impose numeric element, rectangularity, axis, or dimensional contracts. A future typed-collection proposal would need to specify those separately. This plan adds neither matrix types nor array operators, and it leaves Pydantic dependencies unchanged.

### Example-to-task traceability

E01-E03 explain the existing P01.03 and P02.01-P02.03 acceptance work. E04 explains P03.02; E05 reinforces advisory wording and unchanged parser acceptance in P03.04. E06-E07 document the existing scope boundary rather than create implementation tasks. The maintained production exemplar remains the source-owned decision process and its generated teaching copies, not these historical plan excerpts.

### Phase 1: Establish the baseline
Objective: Capture the exact contracts and scope that the wording change must preserve.
- [x] Key task: P01.01 Read applicable AGENTS owners, the pilot and its schema/fixture dependencies, authoring generators, relevant checks, and matching specialist references before editing.
- [x] Key task: P01.02 Record baseline checks, pilot structure, fixture outputs, product sizes, protected file fingerprints, and validator identity in implementation evidence.
- [x] Key task: P01.03 Review the proposed sentence against the role table; record that no subject, criterion, output, authority, or proof obligation is lost or invented.
Success criteria: Evidence identifies the exact pilot, protected contracts, observed baseline results, and the limited intended prose change.
Transition trigger: Baseline evidence and the role-preservation review are recorded under this plan.

### Phase 2: Refine one exemplar
Objective: Demonstrate the convention through the existing pipeline rather than a new tutorial subsystem.
- [x] Key task: P02.01 Refine only the selected ACT sentence in its Python source, retaining process identity, schemas, bindings, call order, and the existing sample.
- [x] Key task: P02.02 Record the before/after role explanation in completion evidence; use the generated working example as the portable exemplar instead of maintaining a second authored copy.
- [x] Key task: P02.03 Extend existing checks for valid bindings, missing or wrong-type values, unexpected outputs, and non-empty but unjustified decision text; distinguish structural rejection from a shape-valid judgment that still needs review.
Success criteria: Fixture outputs and layouts stay the same. Existing mechanisms reject malformed values without misreporting valid structure as sound reasoning. Structural comparison permits only the reviewed action-text change.
Transition trigger: Focused checks pass and their evidential limits are recorded.

### Phase 3: Derive shared conventions
Objective: Extract a few reusable rules without new syntax or a large vocabulary catalogue.
- [x] Key task: P03.01 Refine overlapping entries in `oak/rules/guidance.py`; add only indispensable rules for explicit roles, relationships, schema-backed bindings, and appropriate outputs or effects.
- [x] Key task: P03.02 Include the validate/assess/publish contrast and validation limits while preserving alternative domain wording and exact tool names. Do not turn the contrast into a callable vocabulary.
- [x] Key task: P03.03 Assign every changed or added rule one guide owner in `build/authoring_guides.py`; update applicable AGENTS pointers only where needed, without copying the rules into multiple owners.
- [x] Key task: P03.04 Extend existing guidance checks for single ownership and shared delivery; demonstrate that alternative well-formed ACT prose still parses. Do not implement English-word rejection or claim general semantic equivalence from fixtures.
Success criteria: Each convention has one maintained source and a concrete exemplar. No registry, mandatory phrase template, new format, or parser restriction has appeared.
Transition trigger: Shared ownership and focused authoring checks pass within the agreed scope.

### Phase 4: Refresh the capability
Objective: Deliver matching skill and agent knowledge with truthful identity and unchanged scope.
- [x] Key task: P04.01 Commit changed package sources, pin the optional validator to that immutable source revision, recompute the complete package fingerprint, and confirm the unchanged dependency fingerprint. Advance skill version 2.1.0 to 2.2.0 without changing validator logic or consent behaviour.
- [x] Key task: P04.02 Regenerate scenario snapshots, catalogue, skill references, teaching documents, assembled agent, and affected generated authoring reference through source owners. Never patch generated files by hand.
- [x] Key task: P04.03 Preserve existing size and line limits. Revise overlapping guidance or shorten redundant explanation in touched guides without removing obligations, teaching documents, grammar material, or validator consent information; do not raise the limits.
- [x] Key task: P04.04 Verify skill/agent knowledge and execution parity, closed detached teaching bundles, inert embedded examples, and rejection of supporting operational fusion.
Success criteria: Fingerprints match the retrievable pinned revision; generated forms share the changed guidance and full teaching mapping; budgets and scope checks pass. Grammar, shared schemas, dependencies, and runtime implementation stay unchanged.
Transition trigger: Generated products and capability identity pass their checks together.

### Phase 5: Verify and deliver
Objective: Complete the bounded change with reproducible evidence and a review pull request.
- [x] Key task: P05.01 Run compilation, catalogue and package generators, `python -m build.examples`, and `python build/examples.py`, retaining detached, rejection, scope, and parity checks.
- [ ] Key task: P05.02 Run the existing approved detached validator bootstrap and cache-reuse integration against the new immutable revision, preserving separate end-user installation consent in both authoring forms.
- [x] Key task: P05.03 Repeat generation with no product diff; compare protected files and pilot structures to the baseline; remove obsolete live teaching wording while preserving historical before/after evidence.
- [x] Key task: P05.04 Review the final diff for changed meaning, duplicated guidance, invented capabilities, and overstated proof; fix findings and re-run affected checks before recording the verdict.
- [ ] Key task: P05.05 Commit the complete change and `report.md` with per-task evidence, open its PR to main, verify final-head CI, and complete checkboxes only against observed evidence. Do not merge.
Success criteria: All applicable tasks have evidence, both full checks and final-head CI pass, generation is stable, and the unmerged PR links the plan and report. Blocked tasks remain explicitly open.
Transition trigger: The complete change is delivered for review at a verified final head.

### Coordinating Instructions
- Timeline: execution was authorized at 2026-09-05T22:05:29+10:00. These phases constitute one delivery, not deferred feature releases.
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
| Execution approval | One explicit instruction | User | AVAILABLE |

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
| Implement and open its review PR | Agent under the user's execution authorization | User |
| Add syntax, types, dependencies, mandatory wording, or a broader pilot | User | Stop scope expansion and report conflict |
| Merge | User's separate authorization | User |

### Acknowledgement
The user has authorized this bounded implementation and its review PR. No merge is authorized; completed tasks require observed evidence.
