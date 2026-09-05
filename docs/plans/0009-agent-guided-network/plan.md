# Agent-guided numerical network experiment

Prepared: 2026-09-05T21:27:28+10:00
Classification: PUBLIC

## 1. Situation

### Operating Environment
OAK describes portable knowledge units with explicit parts and host execution boundaries. The user wants agents to participate in learning by revising node-owned matrices, then be removed so the resulting numerical network performs inference alone.

### Current State
The design starts from `cd1f8aed74b24f8515a3e176972e9f2cbcb53e5a` on `experiment/agent-guided-network`. The original request authorised the design package. On 5 September 2026 the user subsequently authorised implementation and a small real experiment, with the running assistant acting sequentially for all logical node roles. No additional paid model API or merge into main is authorised. The [experiment specification](../../../experiments/agent-guided-network/EXPERIMENT.md) owns the proposed architecture.

### Challenges
- Credit assignment: a final network error does not identify a safe local matrix change.
- Coordination: individually useful proposals can conflict when combined.
- Evidence: successful packaging does not demonstrate superior learning.

### Supporting Factors
- Higher intent: learned capability belongs to the numerical network, not its temporary agents.
- Adjacent efforts: OAK's existing schemas, constants, processes, and host tool boundaries.
- Supporting resources: primary research and official export documentation in the experiment's source register.

### Assumptions
- A fixed-topology, approximately 16-module pilot can test the mechanism before scaling toward hundreds.
- Numerical fitting is permitted as a collaborator with the learning agents.

### Constraints and Limitations
- Constraint: preserve inline, node-owned parameter constants within each immutable revision and use no agents in scored inference.
- Constraint: keep evaluation independent and do not invent new OAK parts or a task-specific configuration language.
- Limitation: the first study does not supply independent-agent ablations or hundred-node measurements.
- Limitation: direct cloning failed, but a checksum-verified GitHub Actions source artifact enabled actual local execution.

## 2. Mission

Record the experiment and execute the subsequently authorised four-module sequential-assistant feasibility study, while retaining open tasks for the broader research programme.

Task: Deliver the requested documentation-first commit, an executable numerical prototype, actual assistant decisions, measured comparisons, and agent-free export evidence.
Purpose: Make the user's learning intent precise, testable, and independent of inference-time agents.
End state: A measured, reproducible small experiment with engineering and scientific verdicts separated; unperformed broader studies remain open.

## 3. Execution

Intent: Build a numerical network first, then measure the contribution of temporary learning agents. Keep documentation readiness, implementation completion, engineering success, and scientific advantage distinct.
Concept of operations: Record the intent and contracts. After authorisation, implement numerical execution, add constrained learning, conduct controlled comparisons, and verify export without agents.

### Phase 1: Record the experiment design
Objective: Deliver the requested branch and self-contained experiment documentation.
- [x] Key task: P01.01 Read the root and applicable scoped owners and pin the repository baseline; evidence is recorded in the report.
- [x] Key task: P01.02 Create the experiment branch and synthesise intent, architecture, sources, risks, and evidence requirements.
- [x] Key task: P01.03 Define meaningful directories, repository routing, and an explicit not-yet-run evidence status.
- [x] Key task: P01.04 Commit the package, verify navigation and repository checks where executable, and record observed results and limitations.
Success criteria: The committed package contains EXPERIMENT.md and its linked specifications; all claimed checks have observed evidence and unavailable checks are stated.
Transition trigger: Design delivery is recorded; Phase 2 was authorised by the user on 5 September 2026.

### Phase 2: Establish the numerical network
Objective: Implement a small, fully numerical reference path before adding agents.
- [x] Key task: P02.01 Freeze module topology, equations, operation identities, parameter shapes, and OAK schema contracts.
- [x] Key task: P02.02 Implement canonical node authoring, inline parameters, immutable snapshots, and the restricted host adapter.
- [x] Key task: P02.03 Implement deterministic task generation, numerical execution, and basic validity and no-agent tests.
Success criteria: Executable evidence shows a reproducible numerical network with validated parameters and no interpreter dependency in its forward path.
Transition trigger: The numerical reference and initial tests pass on the frozen source revision.

### Phase 3: Implement constrained learning
Objective: Materialise agent proposals as tested numerical parameter changes.
- [x] Key task: P03.01 Implement observation, proposal, candidate, evaluation, and decision records with revision-aware acceptance.
- [ ] Key task: P03.02 Implement direct-edit and behavioural-proposal fitting treatments with numerical and resource bounds. Behavioural fitting is complete; the separate direct-edit treatment remains outside the first run.
- [x] Key task: P03.03 Implement independent whole-network evaluation, stale-candidate rejection, combined-update tests, and retained-incumbent rollback.
Success criteria: Executable tests demonstrate real matrix changes, preserved revision ownership, explicit failures, and no agent contribution to scored computation.
Transition trigger: A complete learning cycle and its negative cases pass; the bounded CPU feasibility budget is recorded in evaluation/study.oak.md.

### Phase 4: Run controlled comparisons
Objective: Test engineering improvement and the added value of agents separately.
- [x] Key task: P04.01 Run a separate pilot and freeze splits, seeds, metrics, effect thresholds, acceptance rules, tolerances, and budgets before scored comparisons.
- [ ] Key task: P04.02 Execute the declared baselines and semantic, diagnostic, and coordination ablations with complete cost accounting. The first-run numerical controls are complete; broader ablations and matched conversation-cost accounting remain open.
- [x] Key task: P04.03 Freeze selected candidates and evaluate the sealed final test set with uncertainty and failure reporting.
Success criteria: Immutable run records permit reproduction and support a declared positive, negative, or inconclusive result without data leakage or hidden resource advantages.
Transition trigger: Candidate selection is closed and measured comparison evidence is complete.

### Phase 5: Verify unwrapping and report
Objective: Demonstrate that the learned numerical capability survives removal of every agent dependency.
- [x] Key task: P05.01 Export the supported numerical graph with complete parameters, preprocessing, decoding, and source identity.
- [x] Key task: P05.02 Test clean offline loading, source-to-export parameter identity, numerical and decision equivalence, and forbidden-dependency rejection.
- [x] Key task: P05.03 Report engineering and scientific verdicts separately and record the measured limits before any scaling claim.
Success criteria: Agent-free artifact evidence and honest comparison verdicts are recorded; no claim of hundred-node scalability is made without its own study.
Transition trigger: The authorised experiment is complete when all applicable implementation and evaluation evidence has been reviewed.

### Coordinating Instructions
- Timeline: design requested on 5 September 2026; the bounded follow-on run was authorised and executed on that date.
- Boundaries: the authorised follow-on is a four-module feasibility run; independent-agent, semantic-ablation, and hundred-node studies remain outside this run.
- Operating guidelines: follow the experiment's node, training, export, and benchmark contracts; use the full repository verification entry points for implementation changes.
- Risk mitigation: preserve a revision-pinned incumbent, protect the final test set, and separate schema validity from observed numerical success.

### Contingencies
- If a proposal improves a module but harms the network then reject or re-evaluate it as a joint candidate.
- If export requires an agent or unsupported operation then fail eligibility rather than hide a fallback.
- If controls show no useful agent advantage then report that outcome without relabelling it as success.
- If a required verification surface is unavailable then record the exact limitation and do not claim the check passed.

## 4. Admin and Logistics

| Resource | Quantity | Source | Status |
| --- | --- | --- | --- |
| Branch and repository access | One experiment branch | Connected GitHub tools | AVAILABLE |
| Experiment specification | One linked design package | This change | AVAILABLE |
| Numerical runtime | One four-module NumPy adapter | Experiment source | AVAILABLE |
| Agent and compute budget | One assistant, six-proposal cap, bounded CPU fitting | User follow-on and frozen study | AVAILABLE |
| Sealed benchmark data | Three seeded train/dev/test splits | Frozen deterministic generator | AVAILABLE |

Supply: Keep dependencies unchanged for the design package. Select maintained numerical dependencies and record versions only when implementation requires them.
Transportation: Commit authored experiment records to the branch; store actual run artifacts with explicit identities when runs exist.
Sustainment: Keep source revisions, observations, costs, and conclusions attributable to one immutable run record.
Rollback: Do not modify main. During later learning, retain the accepted network independently of candidate branches.

## 5. Command and Signal

1. Repository owner: authorises implementation scope, scored-run budget, and any product promotion.
2. Implementing agent: executes only the authorised scope and records evidence; it does not replace missing owner authorisation.

| Channel | Medium | Purpose | Cadence |
| --- | --- | --- | --- |
| Design | EXPERIMENT.md and linked contracts | Maintain experimental meaning | On accepted design changes |
| Task state | This SMEAC plan | Record authorisation and checkboxes | On observed task transitions |
| Evidence | Report and immutable run records | Record actual checks and outcomes | At each delivered milestone or run |

Reporting: The first-run report records measured learning and export; the delivery report distinguishes local execution from CI. PR 14 remains the review vehicle; no merge is authorised.

| Decision | Authority | Escalation |
| --- | --- | --- |
| Create branch and design package | User request of 5 September 2026 | Repository owner |
| Begin implementation | User follow-on of 5 September 2026 | Repository owner |
| Spend resources on scored agent runs | Approved study budget | Repository owner |
| Accept a parameter candidate | Frozen evaluator and coordinator policy | Study owner for policy changes |
| Promote the experiment into OAK | Separate product decision | Repository owner |

### Acknowledgement
The implementing agent records the requested intent and observed first-run evidence. Implementation and the small sequential-assistant feasibility run were subsequently authorised by the user. Broader study tasks remain open unless observed evidence supports completion. No acknowledgement by another party is claimed.
