# Make root interface contracts locally complete

Prepared: 2026-09-07T09:01:19+10:00
Classification: PUBLIC
Status: Implementation verified locally; final branch publication and PR handoff pending.
Authorization: User continuation received 2026-09-07T09:19:06+10:00.
Size gate: Passed before product edits; the complete canonical candidate is 500 lines.
Evidence: [Measured candidate and migration map](evidence/size-gate.json).

## 1. Situation

### Operating Environment
Open Agent Knowledge expresses one node through seven structured parts, while explicit resolution can connect multiple documents. This change continues on `feat/add-resumable-repository-lifecycle` from reviewed snapshot `bb3a44d1c99e29fb5be99f42af0bb487a2cc2a87`; the branch implementation is evidence to examine, not the authority for the desired design.

### Current State
The root `AGENTS.md` is 384 lines, has no schemas part, and declares twelve interfaces using nine distinct external schema definitions; twelve persistent state entries also use an external checkpoint schema. `.agents/rules/repository-task.oak.md` owns thirteen lifecycle schemas, while `.agents/rules/repository-change.oak.md` owns three change schemas and stateless change processes. Current models permit relative interface schema targets, the resolver checks connected schema identities, and lifecycle checks exercise serialized checkpoints, approval, replay, cancellation, failures, and revision drift; inspection of those checks is not an execution result.

### Challenges
- Contract ownership: an address identifies a definition but does not put that definition or its field meanings in the interface-owning document.
- Meaning beyond shape: a task handle can request cancellation or status, and branch targets can request an update, request a merge, or report a merge. Direction, purpose, authority, routing, effects, and conditions must distinguish these uses.
- Line budget: only 116 lines remain before the existing 500-line root limit. Restoring public contracts alone and restoring every lifecycle contract have different costs; the latter requires a measured restructuring rather than a claim that simple insertion fits.
- Identity and scope: copying an external schema locally creates a different resolved identity. Local receive interfaces and their selected processes must change together; external calls must remain explicit adapters.
- False guarantees: typed booleans do not authenticate approvals, strings do not prove observed revisions, descriptions are not executable validators, and staged OAK rollback does not undo native host effects.

### Supporting Factors
- Higher intent: a document explains the contracts it owns without requiring that it implement every external capability itself.
- Adjacent efforts: preserve the existing resumable lifecycle, explicit graph resolution, generated authoring products, scoped AGENTS ownership, and immutable Git history.
- Supporting resources: root and scoped AGENTS documents, `examples/schemas/smeac_plan.oak.md`, `oak/node/parts/interfaces.py`, `oak/node/parts/schemas/model.py`, `oak/resolve/contracts.py`, `oak/context.py`, `oak/rules/guidance.py`, and `build/checks/repository_lifecycle.py` at the reviewed snapshot.

### Assumptions
- The user has accepted the architectural direction and authorized a plan commit on the existing branch. Implementation was subsequently authorized on 2026-09-07T09:19:06+10:00; plan readiness alone was not that authorization.
- Existing syntax already supports schema purpose, placeholder descriptions, local schema targets, interface descriptions, and typed calls. No new section, interface kind, schema alias, import mechanism, or completeness flag is needed.
- The root can remain boundary-complete while its execution depends on explicitly supplied OAK modules and host capabilities. It will not be described as executable without those dependencies.
- The existing twelve public interfaces, nine arrival routes, twelve state values, phase transitions, and safety conditions remain behavioral contracts unless the user explicitly changes the scope.

### Constraints and Limitations
- Constraint: retain the root branch and every original commit; append changes without amend, squash, rebase, force-push, merge, branch deletion, or unrelated branch synchronization.
- Constraint: the original planning delivery changed only this plan. The explicit implementation continuation now permits the product changes and verified task updates below, but not changes to completed historical records.
- Constraint: all root interfaces use local schema definitions, all source-selected root entry processes use the same local schema identities, and the root retains the checkpoint and contracts that explain its own lifecycle decisions.
- Constraint: keep the 500-line AGENTS limit and the existing canonical formatting checks. Do not hide missing meaning through minification, rule bags in constants, deleted safeguards, or moving essential root contracts into a schema-only dependency.
- Constraint: preserve canonical part order, meaningful responsibility for all seven root parts, scoped policy ownership, local state and interface operations, and the existing one-native-action-per-process lifecycle check.
- Constraint: retain relative schema support for explicitly graph-composed OAK documents. Root-specific locality is not a blanket core-language prohibition.
- Constraint: work directly without subagents. Use no em dash or asterisk emphasis in maintained documentation.
- Limitation: this plan is not a validated replacement root or evidence of production authorization, durability, delivery, or exactly-once external effects. The fit of a complete revised root must be demonstrated in Phase 1.
- Limitation: the planning session has GitHub read/write access but no downloaded executable checkout. Repository plan, lifecycle, and full verification commands have not run in this planning delivery.

## 2. Mission

The implementing interpreter makes the root's interface and lifecycle contracts locally understandable on the existing branch after explicit continuation, preserves resumable behavior, and verifies the result without weakening the 500-line limit or OAK's legitimate graph composition.

Task: deliver the complete approved change through the phases below, with evidence before any completion claim and no product implementation in the initial planning commit.
Purpose: distinguish a document's own promises from the external capabilities it uses, and distinguish locally complete boundary contracts from complete executable dependency closure.
End state: the root owns its public shapes, field meanings, checkpoint semantics, boundary purposes, and lifecycle decisions; general authoring guidance explains the unit of completeness; explicitly graph-composed documents remain supported; all applicable checks pass and a completion report identifies the verified revision.

### Contract Ownership and Scope

| Concern | Current guarantee | Required outcome |
| --- | --- | --- |
| Root boundary shape | All twelve interfaces use relative schema targets. | Define their nine distinct public shapes locally; reuse one local definition where the shape genuinely matches. |
| Field and boundary meaning | Purpose and description fields exist but are optional; root interfaces omit descriptions. | Explain every root boundary's purpose, authority, timing, and effects where relevant, using schema purpose, WHERE descriptions, interface descriptions, and connected processes without redundant prose. |
| Persistent lifecycle | Twelve root state values refer to an external checkpoint definition. | Keep those values and their local schema constraints in the root; retain task, phase, proposal, approval, workspace, verification, evidence, and changed-path semantics. |
| Task-specific receipts | Lifecycle requests and receipts live in a schema-only task module. | Move root-owned lifecycle definitions into the root. Remove the schema-only module when no real consumer remains; do not retain a compatibility stub without an identified contract. |
| External implementation | The change module owns naming and authorized Git operations. | Retain legitimate external work and its private process contracts, with explicit input/output mappings and validation at the root's local public boundary. |
| General OAK completeness | Valid references can resolve in a supplied graph; no universal interface-locality requirement exists. | Recommend local boundary definitions for independently understandable documents and require an honest single-document versus graph-composed delivery claim. Keep relative references valid in the core. |
| Validation and trust | Models, node validation, resolution, execution, and the host own different checks. | Enforce root locality structurally, review semantic adequacy separately, and keep user authenticity, persistence, revision observation, scheduling, and effects with the host. |

Schema definitions remain in the schemas part, not inside interface entries. Instructions retain only cross-cutting meaning that the other parts cannot carry. General completeness guidance does not require every OAK document to contain all seven parts.

### State Comparisons

#### E01: Local approval shape and explicit boundary meaning
Authority: required
Current state:
The root owns the approval entry process and state checks, but its payload definition lives elsewhere and its interface has no description.
```xml
<process id="decide-task" name="Decide task" input=".agents/rules/repository-task.oak.md#schema.approval-decision">
```
```text
task-approval RECEIVES .agents/rules/repository-task.oak.md#schema.approval-decision
```
Desired state:
The following are excerpts of the same root document, not an executable complete lifecycle. Existing assertions and host requirements remain in their owning parts.
```xml
<schemas>
<schema id="approval-decision" name="Approval Decision" purpose="Record the user's decision for one exact prepared proposal.">
Task id: <TASK_ID>
Proposal revision: <PROPOSAL_REVISION>
Approved: <APPROVED>

WHERE:
- <TASK_ID> is string; is non-empty; the host-issued task identity.
- <PROPOSAL_REVISION> is string; is non-empty; the host-derived identity of the proposal and its input workspace.
- <APPROVED> is boolean; true authorizes this proposal, while false declines it.
</schema>
</schemas>
```
```xml
<process id="decide-task" name="Decide task" input="schema.approval-decision">
```
```xml
<interfaces>
task-approval RECEIVES schema.approval-decision: A host-authenticated user decision; approval permits subsequent implementation, while refusal cancels the task.
</interfaces>
```
Acceptance: all twelve root interface targets resolve locally, and every source-selected root process uses the matching local schema identity. Preserve the shown approval fields, types, nonempty constraints, decision meaning, and refusal behavior; presentation and concise wording may vary with canonical rendering. Check locality and binding mechanically and review the explanation without opening external contract definitions. Authentication remains a host obligation, not a guarantee conferred by the description.

#### E02: Locally defined checkpoint meaning
Authority: required
Current state:
The root persists state but its phase definition is external.
```text
phase AS .agents/rules/repository-task.oak.md#schema.task-checkpoint.PHASE: "idle"
approved-revision AS .agents/rules/repository-task.oak.md#schema.task-checkpoint.APPROVED_REVISION: ""
```
Desired state:
The root defines the checkpoint schema locally and retains the state bindings and exact lifecycle phase vocabulary.
```text
phase AS schema.task-checkpoint.PHASE: "idle"
approved-revision AS schema.task-checkpoint.APPROVED_REVISION: ""
```
```text
- <PHASE> is string; is one of `idle`, `prepare`, `awaiting-approval`, `implement`, `refresh`, `verify`, `report`, `complete`, `cancelled`.
```
Acceptance: all twelve state entries retain their existing values, meanings, and lifetimes and validate against local schema slots. Preserve distinctions between initial empty values and nonempty incoming requests or successful receipts. Check invalid stored phases, initial state, new-task reset, and cross-arrival restoration. The root's schemas and processes explain the relationships; binding each slot alone does not prove a globally consistent checkpoint.

#### E03: Preserve resumable lifecycle and failure behavior
Authority: required
Current state:
The root and deterministic lifecycle checks describe the following successful path, with cancellation, refusal, stale-input rejection, revision checks, and failed-arrival state preservation around it. This is inspected behavior, not a claimed test run.
```text
idle -> prepare -> awaiting-approval -> implement -> refresh -> verify -> report -> complete
```
Desired state:
The same public protocol remains, with contract definitions moved to their owner rather than phases collapsed into one uncheckpointed action.
```text
idle -> prepare -> awaiting-approval -> implement -> refresh -> verify -> report -> complete
```
Acceptance: run serialized restore and happy-path tests; reject wrong task, wrong phase, duplicate preparation, stale or duplicate approval, implementation without matching authorization, completed-phase replay, invalid stored state, failed or empty verification, fabricated revisions, drift, and independent Git effects during an active task. Verify refusal, cancellation, status, reset, and result emissions. Preserve ASSERT-based invalid-request failures instead of replacing them with false trigger guards that silently yield zero matches. Retain host-derived revisions, pinned governing graphs, successful-return persistence, reconciliation before retry, and the fact that external effects are not rolled back or made exactly-once by OAK.

#### E04: Explicit completeness claims without banning shared schemas
Authority: required
Current state:
`Interface.schema_id` accepts local or relative schema targets. `task_context` renders an already resolved graph without loading files, and `build_interpreter_context` retains source documents and their separate scopes. Current guidance does not establish the stronger root-locality requirement.
Desired state:
General authoring guidance distinguishes boundary completeness, knowledge dependency closure, and host execution capability. Locally complete public contracts are the default for an independently understandable document; graph-composed deliveries disclose and supply their exact required closure. Shared external schemas remain valid for deliberately composed graphs, and directories or prose router paths do not become implicit imports.
Acceptance: retain positive tests for relative interface schema resolution and negative tests for missing, mistyped, or mismatched references. Keep document identity and policy scopes distinct in interpreter context. Teach that schema validity does not prove semantic adequacy, authorization, performed work, or delivery. The root-specific locality check must not be installed as a universal core rejection, and no new completeness flag or import syntax is introduced.

#### E05: Complete contracts within the unchanged line limit
Authority: required
Current state:
The root has 384 lines, `agent-line-limit` is 500, and build-owned AGENTS checks require the maximum. Adding every root-owned schema verbatim is not demonstrated to fit. Earlier discussion estimates for insertion are not a measured final candidate.
Desired state:
A canonical root of no more than 500 lines contains local public definitions, checkpoint meaning, root-owned decision and receipt contracts, meaningful boundary descriptions, and the unchanged lifecycle safeguards. Supported compact syntax and genuinely separate stateless work may reduce plumbing; mandatory root knowledge does not disappear into opaque constants or schema-only helper files.
Acceptance: measure the exact baseline and complete rendered candidate, identify any justified delegation with its contract, and preserve all existing line-bound and canonicality checks. Produce the whole candidate before landing product edits. If the complete candidate cannot satisfy the limit and unchanged behavior, stop at the gate and report the measured conflict for an explicit user decision; this plan authorizes neither increasing the limit nor reducing the requested scope.

#### E06: Explicit adaptation to legitimate external work
Authority: required
Current state:
The root's naming process and its two interfaces use external change-description and change-name schemas. The change module owns the naming knowledge and work, and source-backed trigger validation requires exact resolved identity.
Desired state:
The root's public naming schemas and source-selected process contracts are local, while the existing external process keeps its own private contracts. This excerpt illustrates the intended adapter using existing CALL and EMIT syntax.
```xml
<process id="name-change" name="Name change" input="schema.change-description" output="schema.change-name">
CALL .agents/rules/repository-change.oak.md#process.name-change (
  TYPE=$TYPE,
  SCOPE=$SCOPE,
  SUMMARY=$SUMMARY,
  BREAKING=$BREAKING,
  MIGRATION=$MIGRATION,
) -> BRANCH, SUBJECT, BODY
EMIT interface.name-result
</process>
```
Acceptance: input values cross an explicit typed call, results validate against the local public contract, and source-backed receives never rely on equivalence between different schema identities. Retain stateless external naming and Git operation behavior, target authorization, inactive-task gating, and original policy scope. Use focused compatibility tests for intentionally matching public/private contracts rather than implicit aliases or blind copies. Private schema ownership and layout may vary where the complete candidate justifies it.

## 3. Execution

Intent: make the root explain what it accepts, what it means, and what it promises while retaining the existing resumable protocol. Improve ownership and teaching rather than merely replacing long paths with short ones. Keep every safety invariant and make any size conflict visible before implementation.
Concept of operations: first establish a complete, canonical, under-limit candidate and the migration map, then apply root ownership and general guidance changes on the same branch. Preserve external composition through explicit adapters, extend both positive and rejection checks, and regenerate products from their owners. Finish with observed end-to-end verification and a report; implementation phases are not deferred product releases.

### Phase 1: Establish the complete candidate and size gate
Objective: verify the baseline, map each contract owner, and demonstrate feasibility without changing product files.
- [x] Key task: P01.01 Read the current branch tip, root and applicable scoped AGENTS, source models, resolver, context, lifecycle checks, plan checks, and affected authoring/build sources; preserve unrelated changes and compare any drift with the reviewed snapshot.
- [x] Key task: P01.02 Inventory twelve root interfaces, nine distinct public schemas, thirteen task-module schemas, three change-module schemas, twelve state values, all source-backed routes, process/action contracts, external consumers, and exact dependency closure.
- [x] Key task: P01.03 Record a root-versus-external ownership and target migration map; keep all root-owned lifecycle definitions local, justify private external contracts, and plan removal of the redundant schema-only task dependency after its last consumer moves.
- [x] Key task: P01.04 Construct a complete candidate outside the product tree using current models and canonical render; retain public payloads, phases, semantic explanations, host obligations, and the one-native-action-per-process invariant.
- [x] Key task: P01.05 Measure the complete candidate against 500 lines and all existing formatting checks; document any genuine stateless delegation and reject minification, instruction dumping, or weakened checks as a size workaround.
Success criteria: E01, E02, E05, and E06 have a complete candidate and precise migration map; candidate parsing, rendering, graph resolution, and exact size measurements are recorded, or a measured blocking conflict is reported without product implementation.
Transition trigger: explicit implementation continuation is present and the candidate meets the unchanged size and behavioral requirements; otherwise the work remains blocked at this gate.

### Phase 2: Localize root contracts and preserve lifecycle ownership
Objective: implement the boundary-complete root and explicit external adapters without changing its public protocol.
- [x] Key task: P02.01 Record the accepted root ownership rule in the root's appropriate structured knowledge before further implementation, retaining the distinction between root policy and general language validity.
- [x] Key task: P02.02 Define the root's public schemas, checkpoint, and root-owned proposal, revision, change, verification, and outcome contracts locally; preserve exact payload validation and field meanings.
- [x] Key task: P02.03 Update state AS targets, interfaces, source-selected process inputs, local process outputs, and local ACT contracts together; preserve resolved identity wherever the source-trigger contract requires it.
- [x] Key task: P02.04 Add concise schema purpose, WHERE descriptions, and boundary descriptions where needed; distinguish cancellation from status and branch update, merge request, and confirmed merge receipt despite shared shapes.
- [x] Key task: P02.05 Preserve root state ownership, success transitions, assertions, revision checks, approval binding, checkpoint emissions, failure semantics, host trust requirements, and complete-result validation.
- [x] Key task: P02.06 Retain legitimate external change work behind explicit calls; validate root public outputs and private process bindings, and remove obsolete schema-only modules and references only after checking all current consumers.
Success criteria: E01, E02, E03, E05, and E06 hold in the implemented root; all seven parts have justified work, every root boundary schema and state schema is local, and the canonical root remains at most 500 lines.
Transition trigger: the root and exact required graph parse, resolve, and round-trip, with no unresolved migrated targets or behavior-changing shortcuts.

### Phase 3: Teach and record document completeness
Objective: establish an authoring principle without converting the root preference into a universal core-language restriction.
- [x] Key task: P03.01 Update `oak/rules/guidance.py` with local public-contract defaults, semantic completeness review, honest document-versus-graph delivery claims, and legitimate explicit external dependencies.
- [x] Key task: P03.02 Update owning scoped AGENTS records only for their concerns: `oak/node/AGENTS.md` for part ownership and local validation, `oak/resolve/AGENTS.md` for explicit closure and identity, `oak/AGENTS.md` for interpreter context and the host boundary, and build/example owners for affected verification and teaching.
- [x] Key task: P03.03 Preserve optional descriptions where meaning is already unambiguous, schema-only library documents, omitted unjustified parts, relative schema support, and separate operational document scopes; add no new syntax, model flag, implicit import, or requirement to materialize the whole graph into every file.
- [x] Key task: P03.04 Keep one authoritative owner per claim and route generated guides through their maintained sources; distinguish structural checks from semantic review and host-observed evidence.
Success criteria: E04 is documented consistently with E01 and E06; the guidance explains what is newly required for the root, what is recommended generally, and what existing runtime validation can actually prove.
Transition trigger: owner review finds no universal ban on shared schemas, contradictory standalone claim, duplicate procedural rule bag, or invented runtime capability.

### Phase 4: Verify locality, semantics, and behavioral preservation
Objective: replace layout-specific assumptions with stronger ownership checks while retaining positive and adversarial lifecycle coverage.
- [x] Key task: P04.01 Extend `build/checks/repository_lifecycle.py` and the owning AGENTS checks to require local root interface/state schemas, matching source-selected process identities, canonical documents, precise justified closure, and the unchanged line bound.
- [x] Key task: P04.02 Update the current exact-three-document fixture and missing-dependency cases to the final actual graph; do not merely remove closure assertions or continue requiring a retired task-schema module.
- [x] Key task: P04.03 Execute existing serialized checkpoint, happy-path, approval, replay, refusal, cancellation, drift, failure-before-effect, failure-after-effect, revision-receipt, verification, and branch-operation tests against the revised root.
- [x] Key task: P04.04 Add rejection cases for externalized root public schemas, missing local slots, local-versus-external source/process identity mismatches, wrong public/private adapter values, and malformed emitted instances.
- [x] Key task: P04.05 Retain a positive graph-composed interface example using an external shared schema; reject its missing or mistyped dependency without making the core reject legitimate relative targets.
- [x] Key task: P04.06 Review each root boundary using the root alone: identify payload meaning, caller or recipient where material, routing, allowed conditions, effects, refusal/cancellation/status behavior, and host assumptions; record any necessary external implementation dependency separately.
- [x] Key task: P04.07 Exercise a 501-line rejection and semantic mutation cases that remove approval/revision safeguards or replace rejecting assertions with silent guard filtering; keep meaningful behavioral tests distinct from checks for nonempty prose.
Success criteria: E01 through E06 are covered by observed structural, resolution, behavioral, and semantic-review evidence; no locality test rejects valid general graph composition, and unchanged failure semantics are demonstrated rather than assumed.
Transition trigger: all targeted checks pass with evidence tied to the candidate revision and no blocking semantic or size finding.

### Phase 5: Refresh examples and generated deliveries
Objective: propagate the accepted ownership principle through maintained examples and generated authoring forms without editing deliveries by hand.
- [x] Key task: P05.01 Inspect affected example registration, existing shared-schema scenarios, and authoring guide composition; add or adapt the smallest teaching example that contrasts local public contracts with explicit external work.
- [x] Key task: P05.02 Register working examples with populated inputs and outputs and honestly labeled host effects; preserve the existing four-stage learning core, detached graph closure, and positive shared-schema demonstrations.
- [x] Key task: P05.03 Regenerate affected catalogue snapshots, guides, skill, assembled agent, and references through their source owners; update validator fingerprints only through their existing policy when affected.
- [x] Key task: P05.04 Verify XML and Markdown round-trips, closure, source-snapshot equality, scope-safe fusion behavior, standalone delivery claims, generated freshness, and existing authoring product byte limits.
- [x] Key task: P05.05 Run the complete verification entry points `python -m build.examples` and `python build/examples.py` in the build-prescribed environment after compilation and generation; record actual commands, revisions, and outcomes.
Success criteria: E04 and E06 are taught by truthful working examples, E05 remains satisfied, required comparisons retain coverage, complete checks pass, and repeated generation produces no additional diff.
Transition trigger: generated deliveries match maintained sources and both complete verification entry points succeed with recorded evidence.

### Phase 6: Complete review and handoff
Objective: demonstrate the full accepted outcome on the existing branch without claiming unobserved results or authorizing a merge.
- [x] Key task: P06.01 Review the final diff directly without subagents; search current files for retired schema paths, contradictory locality rules, stale closure assumptions, altered safeguards, and unsupported standalone or exactly-once claims.
- [x] Key task: P06.02 Add `report.md` in this plan directory with the verified revision, changed paths, measured line counts, exact graph closure, E01 through E06 results, test evidence, limitations, and final verdict.
- [ ] Key task: P06.03 Check off tasks only against observed evidence, reconcile any changed scope with the user, and ensure every applicable task passes before marking the plan complete.
- [ ] Key task: P06.04 Commit completed work without rewriting history and create or update the branch pull request for review after successful implementation; leave merge and branch deletion to separate explicit authorization.
Success criteria: E01 through E06 have traceable observed results, every applicable checkbox passes, the branch contains the complete change and report, and the review handoff states any remaining uncertainty accurately.
Transition trigger: mission complete with a review-ready branch and completion report; no automatic merge follows.

### Coordinating Instructions
- Timeline: plan requested on 2026-09-07 in Australia/Brisbane. Work is request-driven; no background execution or wall-clock completion promise is implied.
- Boundaries: the initial commit contains only `docs/plans/0015-local-interface-contracts/plan.md`. Later implementation includes the root, owning modules, scoped guidance, relevant checks, examples, generated deliveries, and the matching report, not unrelated repository changes.
- Operating guidelines: use the existing branch, direct work, explicit typed targets, canonical render, stable task and comparison identifiers, short progress updates, source-owned generation, and preserved history.
- Risk mitigation: make the full-candidate size gate first; keep approval and revision checks behavioral; verify graph identity and public/private adaptation; distinguish machine validation, semantic review, and host truth.

### Contingencies
- If the complete candidate exceeds 500 lines after justified restructuring, then report its exact count and the competing constraints; request a decision before changing the limit, weakening behavior, or externalizing mandatory root contracts.
- If the branch or governing knowledge changes before execution, then inspect the new tip and reconcile the delta without overwriting it; seek renewed authorization only for changed scope or approved inputs.
- If local and external contracts become intentionally distinct, then retain an explicit typed adapter and test its values; do not treat copied definitions as the same identity or add a schema-alias workaround.
- If a current consumer still needs the task-schema module, then document that consumer and migrate it within scope or surface the compatibility conflict before deleting the module.
- If native work fails after an external effect, then reconcile the effect before retrying and follow the existing revision/cancellation policy; do not claim rollback or repeat a completed phase.
- If a needed environment or check is unavailable, then record not-run results and leave verification tasks unchecked rather than substituting prose confidence for execution evidence.

## 4. Admin and Logistics

| Resource | Quantity | Source | Status |
| --- | --- | --- | --- |
| Existing work branch | One | `feat/add-resumable-repository-lifecycle` | AVAILABLE |
| Reviewed baseline | One immutable snapshot | `bb3a44d1c99e29fb5be99f42af0bb487a2cc2a87` | AVAILABLE |
| Planning format and storage rules | One schema and scoped owners | `examples/schemas/smeac_plan.oak.md`, `docs/AGENTS.md`, `examples/AGENTS.md` | AVAILABLE |
| GitHub repository access | Read, implementation commits and PR | Connected repository tools | AVAILABLE |
| Executable verification environment | Python 3.13.5, dependencies outside checkout | `pyproject.toml` and `build/AGENTS.md` | AVAILABLE |
| Complete under-limit root candidate | One canonical 500-line root | Phase 1 measured candidate, promoted without weakened constraints | AVAILABLE |
| Implementation authorization | 2026-09-07T09:19:06+10:00 | User | AVAILABLE |

Supply: use existing package models, validators, build ownership, specialist skills where relevant, and repository dependencies. Do not add a dependency, format, framework, or remote download requirement merely to localize contracts.
Transportation: keep edits and evidence on the existing branch as new commits. Move schema targets and values through explicit typed mappings, and move generated products only through their owning generators.
Sustainment: retain this plan's stable path and identifiers, preserve checkpoints between implementation requests, and add evidence files only when useful for observed results. Keep the actual graph and host state pinned for a running lifecycle; prose plan status is not a substitute for runtime persistence.
Rollback: preserve the reviewed commit and all subsequent history. Correct mistakes with new commits or an authorized revert, preserve unrelated work, and reconcile host effects separately from OAK state; never claim that reverting repository text undoes external actions.

## 5. Command and Signal

1. Chris Buckley, product owner and authority for scope, changed constraints, implementation continuation, and merge decisions.
2. The implementing interpreter, responsible for direct execution, evidence, faithful progress state, and escalation; no subagent delegation.

| Channel | Medium | Purpose | Cadence |
| --- | --- | --- | --- |
| User discussion | This conversation | Explain findings, receive continuation, and surface conflicts | At decisions and meaningful progress |
| Persistent task record | This plan | Retain scope, gates, unchecked work, and completion criteria | On verified task-state changes |
| Review evidence | Branch commits and eventual report/PR | Identify exact changed content, observed checks, and verdict | At checkpoints and final handoff |

Reporting: Phase 1 measured the full candidate before product edits. Phases 2 through 5 now pass, including both complete verification entry points; the direct boundary review covers E01 through E06. See the observed evidence and completion report; final publication tasks remain open until performed.
Reporting: the original planning commit contained no product implementation. Later user continuation authorized this implementation, tests, report, and review-ready PR; no merge or branch deletion is authorized.
Reporting: report any proposed public protocol change, mandatory-root-contract relocation, limit relaxation, schema-language restriction, missing dependency, or unverified test immediately instead of silently changing the plan.

| Decision | Authority | Escalation |
| --- | --- | --- |
| Create and commit this plan on the existing branch | User authorization in this request | User |
| Begin product implementation | Explicit user continuation received 2026-09-07T09:19:06+10:00 | User |
| Choose internal layout within the accepted constraints | Implementing interpreter with measured evidence | User when scope or behavior changes |
| Relax 500 lines, remove a public boundary, or prohibit general relative schemas | User only through a revised approved scope | User |
| Mark implementation complete | Observed passing checks and direct final review | User for any unresolved limitation |
| Merge, delete the branch, or rewrite history | Separate explicit authorization; history-preservation rules still apply | User |

### Acknowledgement
All parties MUST acknowledge receipt and understanding of this plan.
The initial planning authorization and subsequent implementation continuation are recorded separately. The implementing interpreter followed the measured candidate gate and retains host-trust limitations; verification and final PR publication are recorded only after their actual results.
