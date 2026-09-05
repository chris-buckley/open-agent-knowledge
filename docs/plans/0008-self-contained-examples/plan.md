# Self-contained examples and shared skill teaching

Prepared: 2026-09-05T20:36:02+10:00
Classification: PUBLIC

Plan: 0008-self-contained-examples
Format: `examples/schemas/smeac_plan.oak.md`
Repository: `chris-buckley/open-agent-knowledge`
Baseline: `main` at `cd1f8aed74b24f8515a3e176972e9f2cbcb53e5a`
Branch: `plan/self-contained-examples`
Plan status: Complete.
Execution status: All 29 tasks complete; delivered for review in PR #13.
Authorization gate: The user authorized end-to-end implementation and a review pull request at 2026-09-05T20:45:48+10:00. Merging still requires separate user authorization.

## 1. Situation

### Operating Environment
OAK expresses knowledge through seven closed parts and supports Python authoring, canonical OAK documents, explicit document resolution, and execution with host-supplied capabilities. This change concerns the repository example collection and the teaching material delivered through its existing authoring skill and assembled agent.

### Current State
Executable agent sources and sibling renders live under `examples/agents/`, while reusable schema sources and renders live under `examples/schemas/`; `build/checks/human_examples.py` explicitly registers their verification. `build/authoring_guides.py` currently composes three teaching examples, including fixed knowledge defined in that generator and examples derived from the shape gallery and shape writer. `build/authoring.py` generates the skill and assembled agent, with parity, fusion-scope, freshness, and size checks in `build/checks/authoring.py`.

### Challenges
- Scattered scenario dependencies: Moving a file can break Python imports, relative OAK targets, fixture hosts, generated material, and verification registration.
- Competing source owners: Hand-maintained teaching copies would drift from the runnable examples they explain.
- Misleading self-containment: A readable entry document is not portable when it silently depends on another scenario directory or an unavailable host capability.
- Scope and size pressure: Embedding operational examples as active authoring knowledge changes behavior; embedding the entire advanced collection also risks exceeding the assembled-agent budget.

### Supporting Factors
- Higher intent: Make one compact validated unit easier to author, understand, and reuse without adding language concepts.
- Adjacent efforts: Preserve the existing shape-first schemas, compact syntax, shared skill and agent sources, and SMEAC plan conventions.
- Supporting resources: Existing example sources, populated shape instances, deterministic hosts, explicit loaders, generation functions, and repository checks provide the starting material.

### Assumptions
- The existing examples provide most of the required teaching coverage; introduce a new example only for a demonstrated gap.
- Reusable schema definitions remain source-owned under `examples/schemas/`; scenario packaging may generate local dependency renders from those sources.
- Python authoring requires the repository and its declared dependencies. Self-contained OAK delivery does not mean vendoring OAK, Python, credentials, or an interpreter into every folder.
- An execution-capable environment with the declared dependencies is available before implementation can be reported as verified. Confirm this in Phase 1.

### Constraints and Limitations
- Constraint: Keep the grammar, datatype catalogue, model and execution semantics, Pydantic version requirements, and other dependencies unchanged. Vocabulary expansion, typed matrices, and new statement syntax are out of scope.
- Constraint: Preserve existing demonstrated behavior, populated outputs, exact tool names, separate document scopes, and all valid verification coverage.
- Constraint: Use the existing OAK and Python forms. Do not introduce a task-specific manifest language, provider-specific packaging, repository README index, or manually maintained second teaching collection.
- Constraint: Preserve the authoring skill's no-install path, optional-validation consent rules, immutable validator identity checks, 10,000-byte entry limit, 500-line entry limit, and 64,000-byte assembled-agent limit.
- Constraint: Apply current scoped AGENTS ownership and update affected sources, active references, checks, and generated outputs together. Preserve historical claims and path snapshots in completed plans; repair navigational links where necessary.
- Limitation: Fixture execution demonstrates the supported scenario and dataflow, not arbitrary model quality or a real external effect.
- Limitation: Plan preparation used the GitHub connection. A local checkout attempt failed with `Could not resolve host: github.com`; the full repository suite has not run during preparation.

## 2. Mission

After implementation authorization, the implementing agent reorganizes OAK's existing examples into self-contained scenario directories on this branch and generates shared skill teaching from those sources before requesting review, so readers can progress from simple knowledge to stateful work without duplicated definitions or language changes.

Task: Deliver the complete example reorganization, shared teaching generation, verification, and completion report in one implementation pass before opening the review pull request.
Purpose: Establish concrete, trustworthy examples as the basis for later convention and type-system decisions.
End state: Every registered scenario has one source owner, canonical renders, declared requirements, and appropriate fixtures; exported OAK dependencies remain inside its directory; the skill and assembled agent share one curated teaching core; all applicable checks pass with recorded evidence.

## 3. Execution

Intent: Teach the existing language before extending it. Keep each example as small as its lesson permits, reuse existing sources, and make omissions and host requirements explicit. Preserve one maintained meaning across repository examples, skill teaching, and the assembled agent.
Concept of operations: First inventory dependencies and capture the baseline. Reorganize complete scenarios, close their exported dependencies, and fill only the missing steps in a four-stage teaching progression. Generate the shared teaching core from that collection, verify portability and behavior, and deliver one reviewable branch. These phases are ordered work within one change, not deferred product releases.

### Target Layout and Ownership

Use stable snake_case scenario directory names under `examples/`; record learning order in the catalogue rather than encoding it into Python import paths. The default scenario contains `example.py` and its generated sibling `example.oak.md`. Add supporting document pairs, local generated schema dependencies, fixture data, or a host adapter only when the scenario requires them.

| Location | Responsibility |
| --- | --- |
| `examples/<scenario>/` | One complete scenario, its authoring source, canonical entry, required local OAK documents, fixtures, and host demonstration code where needed. |
| `examples/schemas/` | Existing reusable schema source definitions and their canonical library renders; do not move the SMEAC schema in this change. |
| `examples/catalog.py` | One small explicit Python registration used by example verification, teaching selection, and catalogue generation; not a new configurable framework. |
| `examples/catalog.oak.md` | Generated OAK teaching catalogue containing learning order, entry paths, lessons, omitted parts, requirements, and invocation guidance. |
| `skills/oak-authoring/references/examples/<scenario>/` | Generated teaching bundles for the selected core, including their required OAK documents and populated input/output material. |
| `build/authoring_guides.py` and `build/authoring.py` | Compose guides and generate deliveries from the registered sources, without owning independent scenario definitions. |
| `outputs/oak-authoring.oak.md` | The assembled authoring capability containing the same selected teaching knowledge as the skill, with examples kept inert. |

A delivered scenario is self-contained when its entry, every required OAK document, and its fixtures fit inside its directory and resolve there without another scenario or the network. Shared Python authoring imports must be declared; regeneration may use the repository schema library. Demonstration execution from an isolated bundle may use an installed OAK runtime and its explicitly included host adapter, but must not reach back into other example directories. Do not describe repository-dependent regeneration as standalone execution.

Supporting operational documents stay separate. Reuse existing safe fusion only when its declarative-support preconditions hold; otherwise package the required documents locally. Rebase only typed targets through an explicit identity mapping, preserving resolved contract relationships. Do not rewrite literal payloads, prose, templates, scripts, or tool names to imitate relocation.

### Teaching Progression

| Stage | Lesson | Starting material | Required demonstration |
| --- | --- | --- | --- |
| 1. Fixed knowledge | Useful OAK need not contain processes or state. | The fixed-knowledge example currently defined by `teaching_examples()`. | The two existing fixed facts, canonical rendering, and justified omissions. |
| 2. Shaped information | A schema defines a shape; an instance fills it. | `examples/schemas/shape_gallery.py`. | Existing table, hierarchy, section, and code layouts with complete populated instances and fixed-cardinality explanations. |
| 3. Typed workflow | Receive, compose local work, and emit without persistent state. | `examples/agents/shape_writer.py`. | Existing request fixture, validated intermediate outputs, ordered emissions, and fixture-only host disclosure. |
| 4. Persistent state | Use state only when a later arrival must observe a changed value. | The smallest suitable existing stateful example identified during the inventory. | At least two arrivals, initial and final state, an expected result, and a rejected or failing path that preserves transactional guarantees. |

Keep all existing advanced scenarios discoverable and verified even when they are not selected for the compact teaching core. Stage 4 may use a new minimal example only when the existing scenarios cannot demonstrate the lesson clearly within the shared teaching budget; do not replace or silently reduce their original coverage.

### Phase 1: Inventory and establish the baseline
Objective: Fix the scenario boundaries, dependencies, learning coverage, and observed baseline before moving sources.
- [x] Key task: P01.01 Read every applicable scoped AGENTS document and affected source in full; inventory all registered agent and schema examples, collaborators, fixtures, generated consumers, and verification imports.
- [x] Key task: P01.02 Record a complete old-to-new path and ownership map, grouping collaborating documents by scenario and identifying shared schema sources without leaving orphaned examples.
- [x] Key task: P01.03 Run both repository verification entry points before changes and capture existing snapshot identities, populated outputs, available execution traces, and authoring-product byte counts; record any baseline failure without relabelling it as a pass.
- [x] Key task: P01.04 Select the four-stage teaching core, identify the smallest justified stateful demonstration, and establish each scenario's entry, dependency closure, requirements, and isolated execution command.
Success criteria: Every current registration and generated consumer is accounted for; the migration and lesson maps are explicit; baseline results and size measurements are recorded as evidence, with no unresolved baseline failure hidden.
Transition trigger: The baseline is understood, the source map preserves coverage, and implementation authorization is recorded.

### Phase 2: Establish scenario directories and local dependencies
Objective: Reorganize complete examples without changing their demonstrated meaning or introducing duplicate source ownership.
- [x] Key task: P02.01 Move registered agent scenarios into their mapped directories with source and canonical sibling pairs; retain collaborating operational documents as separate local documents and remove obsolete active paths.
- [x] Key task: P02.02 Keep reusable schema definitions at their existing owner and generate any required scenario-local dependency renders from those definitions rather than copying editable schema code.
- [x] Key task: P02.03 Repair Python imports, source identities, typed relative targets, explicit loaders, fixture expectations, and generation paths; preserve contract identity relationships, process behavior, literal contents, and exact tool names.
- [x] Key task: P02.04 Implement the minimal explicit catalogue registration and derive example coverage and learning order from it; reuse existing build and run functions instead of introducing a second runner framework.
- [x] Key task: P02.05 Make each scenario's lesson, omitted parts, host requirements, fixture limitations, entry path, and regeneration or demonstration command discoverable from its source and generated catalogue.
Success criteria: The complete migration map is realized; no existing example or required dependency is orphaned; each exported OAK graph stays inside its scenario; source review and dependency checks demonstrate single ownership.
Transition trigger: Relocated examples render, resolve, and retain their baseline fixtures and behavior.

### Phase 3: Complete the teaching progression
Objective: Provide the smallest complete progression from fixed facts to work across arrivals.
- [x] Key task: P03.01 Move the existing fixed-knowledge definition out of the authoring-guide generator into its own scenario source and generate both repository and teaching forms from that source.
- [x] Key task: P03.02 Expose the shape-gallery lesson through a scenario entry backed by the existing shared definitions and populated instances; preserve actual presentation checks rather than asserting only binding validity.
- [x] Key task: P03.03 Preserve the shape-writer pipeline as the typed stateless lesson, including its complete sample request, expected intermediate and final outputs, and explicit deterministic-host limitation.
- [x] Key task: P03.04 Provide the selected persistent-state lesson with two or more arrivals and explicit state assertions; verify both successful progression and a failing or rejected path without claiming rollback of external effects.
- [x] Key task: P03.05 Add only missing fixtures or teaching steps and keep small fixtures inline when that is clearer; do not create empty fixture directories, placeholder hosts, invented tool implementations, or artificial use of all seven parts.
Success criteria: All four lessons have complete observable examples and justified omissions; fixture assertions and populated outputs are recorded as evidence; every new scenario is justified by a documented coverage gap.
Transition trigger: The four-stage progression passes its scenario checks and can supply teaching material without hand-maintained copies.

### Phase 4: Generate the shared skill teaching core
Objective: Deliver the selected lessons through the existing skill and assembled agent from identical maintained sources.
- [x] Key task: P04.01 Generate the OAK catalogue and selected teaching directories from the shared registration, with local dependency closure and complete populated teaching material; keep bulky execution-only fixtures outside the compact core.
- [x] Key task: P04.02 Update guide composition, reading routes, example rationale, and review inputs to consume the registered core; remove superseded flat teaching paths and generator-owned duplicate scenario definitions.
- [x] Key task: P04.03 Embed the same selected teaching knowledge in the assembled agent as inert data, including any required supporting example documents; preserve the authoring entry as the only operational scope.
- [x] Key task: P04.04 Apply existing skill version and fingerprint policy to the changed product; retain optional-validation consent and no-install behavior, and change validator identity only when the existing source or dependency fingerprint contract requires it.
- [x] Key task: P04.05 Measure both delivered forms and retain the current size and line limits; reduce repetition or choose a smaller equivalent lesson rather than truncate examples, widen limits, or silently remove required teaching coverage.
Success criteria: Generated deliveries match their sources; all four stages are present in the shared core; parity, inert-example scope, fingerprint, consent, and size checks pass with recorded measurements.
Transition trigger: Freshly generated skill and agent products pass their existing delivery checks and the new teaching-coverage checks.

### Phase 5: Verify portability and prevent regressions
Objective: Prove the reorganization preserves behavior and make the new example contract part of normal verification.
- [x] Key task: P05.01 Integrate all scenario registrations with the existing verification entry point; check canonical XML and Markdown round-trips, local resolution, complete bindings, sibling snapshots, populated layouts, and every declared demonstration run.
- [x] Key task: P05.02 Copy each exported scenario bundle into an isolated temporary directory and resolve it with a directory-bounded loader; run applicable included fixture hosts using only the declared runtime, with no repository fallback or network dependency.
- [x] Key task: P05.03 Add rejection checks for missing local dependencies, escaping targets, missing or stale snapshots, duplicate registration, omitted teaching stages, and source-versus-delivery drift.
- [x] Key task: P05.04 Retain and extend skill-versus-agent parity and fusion rejection checks so embedded example instructions, triggers, state, interfaces, and tool-shaped literals never become active authoring behavior.
- [x] Key task: P05.05 Compare scenario outputs, state transitions, and emissions with the baseline or explicitly justified new fixtures; regenerate twice and require identical owned file sets and bytes, including absence of stale generated paths.
Success criteria: Positive and negative checks pass; isolated-bundle runs prove the declared portability boundary; baseline comparisons, scope checks, and repeated-generation equality provide recorded evidence.
Transition trigger: All new contract checks are registered, passing, and preserve the existing verification coverage.

### Phase 6: Update ownership, review, and deliver
Objective: Deliver one coherent branch with accurate current documentation, complete evidence, and a review pull request.
- [x] Key task: P06.01 Update the affected examples, skills, build, and output ownership documents and active references from their source owners; repair historical navigational links without rewriting historical claims or path snapshots.
- [x] Key task: P06.02 Compile affected Python, regenerate all affected products, and run `python -m build.examples` and `python build/examples.py`; record exact commands, exit results, and the tested source revision or immutable working-tree identity.
- [x] Key task: P06.03 Review the complete diff and search active sources and generated products for replaced paths and duplicate definitions; confirm unchanged grammar, datatype and execution semantics, dependencies, host boundaries, and authoring validation policy.
- [x] Key task: P06.04 Add `report.md` with the final path map, per-task evidence, byte counts, actual check results, and limitations; mark tasks complete only when their evidence is present and independently recheck the final candidate.
- [x] Key task: P06.05 After all preceding tasks pass, commit the complete implementation on this branch, open a review pull request against `main`, inspect the actual changed-file list, and record the pull request and final commit; do not merge.
Success criteria: Every applicable checkbox has evidence, no unexplained diff remains, both verification entry points pass, regeneration is stable, and the complete reviewed change is committed with its report and review pull request.
Transition trigger: Mission complete when the verified branch and pull request are delivered; merge remains a separate user decision.

### Coordinating Instructions
- Timeline: Plan preparation occurs on 5 September 2026. Execution begins only after explicit authorization and completes as one change; there is no promised elapsed-time deadline.
- Boundaries: Source ownership stays in examples and existing generators. Permit necessary reference and check updates, but no new OAK grammar, datatype, general packaging runtime, vocabulary subsystem, dependency, or provider integration.
- Operating guidelines: Follow existing naming and part-responsibility conventions. Prefer a two-file example, add structure only when justified, and preserve exact host tool contracts and fixture disclosures.
- Risk mitigation: Use the migration map and baseline comparisons to detect omissions, isolated bundles to detect hidden dependencies, and source-derived generation to detect drift. The unchanged full suite remains the acceptance gate.

### Contingencies
- If an existing example depends on another operational document, then keep it separate within the scenario bundle and update explicit typed targets; do not broaden fusion to flatten it.
- If a teaching bundle exceeds the existing budget, then remove duplication or use a smaller source-backed lesson while retaining all four stages and full runnable examples outside the core.
- If relocation exposes an unrelated semantic defect, then record it with evidence and keep it out of this change; do not hide failures or expand language scope without user authorization.
- If an execution environment or required dependency is unavailable, then record the exact blocker and leave affected verification tasks open; no inspection or fixture claim substitutes for a command that did not run.
- If the base branch changes before execution, then review the intervening diff, reconcile this plan's path map and ownership requirements, and record the updated implementation baseline before moving files.

## 4. Admin and Logistics

| Resource | Quantity | Source | Status |
| --- | --- | --- | --- |
| Repository baseline and scoped rules | One pinned revision | GitHub connection, baseline recorded above | AVAILABLE |
| Existing examples and verification sources | All registered examples | `examples/` and `build/checks/` | AVAILABLE |
| Plan and implementation branch | One branch | `plan/self-contained-examples` | AVAILABLE |
| Execution environment and declared dependencies | Local worktree and isolated CI | Verified repository export and GitHub Actions with declared dependencies | AVAILABLE |
| Shared teaching and generated products | One source-derived collection | Existing authoring generators | AVAILABLE |

Supply: Reuse current schema sources, fixture data, package dependencies, and generators. Do not install dependencies as part of plan preparation; preserve the separate consent policy of the delivered optional validator.
Transportation: Carry changes through this branch. Generate scenario and skill artifacts from source, and provide explicit local document mappings instead of network or working-directory discovery.
Sustainment: Maintain one registration and source owner per concern. Keep normal verification responsible for scenario completeness, canonical snapshots, portability, shared teaching parity, and generated-file ownership.
Rollback: Use normal Git reverts of this change's commits if recovery is needed. Do not force-push, overwrite unrelated work, delete historical evidence, or leave a mixture of old and new generated paths.

## 5. Command and Signal

1. Chris Buckley, product owner: controls scope, implementation authorization, and merge decisions.
2. Implementing agent: performs the authorized plan, maintains evidence, and prepares the review pull request; does not inherit product-owner authority.

| Channel | Medium | Purpose | Cadence |
| --- | --- | --- | --- |
| User conversation | Chat | Authorization, meaningful progress, blockers, and delivery | At authorization, meaningful milestones, and completion |
| Plan | `plan.md` | Stable task identifiers, scope, and verified task status | As evidence establishes completion |
| Completion report | `report.md` | Actual results, migration map, evidence, and remaining limits | Created during implementation and finalized for review |
| Pull request | GitHub | Review the complete change against `main` | After execution and verification, not during plan preparation |

Reporting: Report plan preparation separately from implementation completion. This plan-only commit does not prove the example migration, regenerated products, or repository checks. Record the plan's structural verification separately; for execution, associate each completed task with inspected files or actual command results and distinguish simulated demonstrations from external effects.

| Decision | Authority | Escalation |
| --- | --- | --- |
| Create and commit this plan | Current user request | User |
| Execute the complete plan and open its review pull request | Explicit user instruction to execute | User |
| Choose file grouping and fixtures within the recorded contracts | Implementing agent after authorization | User if a current repository contract conflicts |
| Change language, dependencies, scope, or size limits | User only; not authorized by this plan | User |
| Merge into `main` | Separate explicit user authorization | User |

### Acknowledgement
All parties MUST acknowledge receipt and understanding of this plan.
The user authorized implementation and a review pull request. The implementing agent acknowledges the plan; completion remains evidence-gated and merge is not authorized.
