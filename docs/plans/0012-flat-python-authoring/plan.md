# Flat Python authoring and statement bodies

Prepared: 2026-09-06T14:04:20+10:00
Classification: PUBLIC

Status: In progress. Implementation authorized; baseline verification passed.
Authorization: The user authorized end-to-end implementation and PR creation on 2026-09-06. Merge is not authorized.
Repository: chris-buckley/open-agent-knowledge
Reviewed main: eca953bd81f78f005fdc1b3d17ed060620f6c97d
Plan path: docs/plans/0012-flat-python-authoring/plan.md
Format: examples/schemas/smeac_plan.oak.md

## 1. Situation

### Operating Environment
OAK has direct Pydantic authoring, canonical text, explicit document resolution, execution, and generated teaching products. This change improves the Python source experience while retaining one canonical meaning and the existing core/host boundary. Repository separation, OAK Host, provider clients, and evaluation experiments are not part of this change.

### Current State
At the reviewed main revision, process and loop contents use `steps`, and the recursive union and base are `Step` and `StepModel`. Examples already name many schemas and processes, but their actions, bindings, conditions, and nested blocks are frequently constructed inside consumers. The current catalogue registers eight scenarios, three supporting workers, and twelve schema source modules; skill teaching now lives under `assets/examples`.

### Review Basis
The root and applicable scoped AGENTS documents, current SMEAC schema, catalogue, all registered example authoring sources, binding and repetition helpers, and detached shape-writer adapter inform this plan. Core statement models, surface descriptors, interpreter-context contracts, and JSON-LD encoding were inspected for consequences beyond examples. This is a source review, not an assertion that the repository's runtime checks passed; no repository suite was executed during planning.

Current source authorities are `AGENTS.md`, `oak/AGENTS.md`, `oak/node/AGENTS.md`, `oak/execute/AGENTS.md`, `oak/resolve/AGENTS.md`, `examples/AGENTS.md`, `build/AGENTS.md`, `skills/AGENTS.md`, `outputs/AGENTS.md`, and `docs/AGENTS.md`. Python defaults are owned by `.agents/rules/coding-standards.oak.md` and its topic documents. Completed plans remain history, not current architecture.

### Example Review and Required Disposition
All paths in this table are relative to `examples/`. Review means inspection of authoring sources; acceptance requires subsequent execution and generated-output checks. Retain means review and verify the source without manufacturing changes solely to touch every file.

| Source | Observed construction | Planned treatment and preservation check |
| --- | --- | --- |
| `fixed_knowledge/example.py` | Two named constants assembled directly in a Node. | Retain the already-flat teaching example; preserve omitted parts and both round-trips. |
| `shape_gallery/example.py` | Thin wrapper around the shared shape source. | Retain the wrapper; change only the owning schema library where needed. |
| `shape_writer/example.py` | Four inline ACT bodies and a coordinator with inline CALL/EMIT pairs. | Name actions, calls, emissions, policy, and nontrivial inputs before assembly. Preserve four ordered outputs and the referenced shapes. |
| `compound_growth/example.py` | Nested WHILE, CALL, SET, reflection ACT, and explicit emission bindings. | Define values, bindings, condition, statements, and loop separately. Put schemas before their consumers. Preserve limit 60, two arrivals, exact expected states, and failure isolation. |
| `interpreter_context/example.py` | ACT and nested binding constructors inside a process; context inspection reads `.steps`. | Use the flat title-review example as the primary before/after specimen. Update context access to `.body`; retain direct/context adapter parity and title policy. |
| `implementer/example.py` | Eight processes with nested actions, verification assertions, and blocked/success branches. | Name the evidence comparisons, assertions, snapshot/verify/commit actions, branches, and bindings. Preserve revision-linked acceptance and pre-effect drift rejection. |
| `delegation/example.py` | Tool dispatch and a CALL/EMIT coordinator constructed inline. | Extract named statements; retain the exact `agent.reviewer` name, result order, and separate worker document. |
| `delegation/task_reviewer.py` | Four processes with repeated nested local bindings. | Name actions/calls and meaningful input groups; preserve readonly policy, schema identities, and evidence/compliance/assessment separation. |
| `successor/example.py` | Deeply nested start/resume, review, compilation, proof assertions, ratification, and publication. | Assemble leaf-first named conditions and statements into unchanged branches. Preserve separate documents, six proof assertions, state lifetimes, and revision 13 to 14 fixture behaviour. |
| `successor/amendment_reviewer.py` | Inline review ACT and EMIT with named schemas and policies. | Flatten the action and emission; retain review-only authority and evidence requests. |
| `successor/successor_verifier.py` | Inline exact-tool ACT and EMIT with named proof schema. | Flatten the action and emission; preserve all proof fields and the prohibition on publication. |
| `schemas/api_coverage_table.py` | One schema with a readable template and long enum/WHERE expressions. | Name dense clauses or reusable enum values where this improves inspection; preserve HTTP methods, gap codes, and template bytes. |
| `schemas/code_changes.py` | Named schema with nested constraints and a repeated code-block template. | Extract meaningful clauses without a template builder; preserve path restrictions, fences, fixtures, and repetition limits. |
| `schemas/code_map.py` | Named schema with cross-placeholder line bounds. | Name dense clauses and keep bound dependencies visible; preserve LINE_TO relative to LINE_FROM and literal snippets. |
| `schemas/docs_index.py` | Named schema and a hierarchical literal template. | Keep the literal hierarchy together; flatten only dense clauses. Preserve indentation, URI/datetime constraints, and repetition instruction. |
| `schemas/error.py` | One schema with one constrained reason. | Retain the small design, or name the reason clause if clearer; preserve one line and maximum 160 characters without adding constraints. |
| `schemas/hierarchical_outline.py` | Named schema with level regexes and repeated STATEMENT slots. | Expose meaningful clauses; preserve three-level numbering, shared-slot behaviour, and exact whitespace. |
| `schemas/ideation_list.py` | Named schema with count-dependent bounds. | Keep count and number constraints visibly related; preserve examples and no new repeated-instance semantics. |
| `schemas/link_manifest.py` | Small named schema with four simple clauses. | Retain shallow details unless names clarify meaning; preserve URI and one-line description contracts. |
| `schemas/process_execution_table.py` | Named schema with status and timestamp clauses. | Flatten long clauses while preserving statuses, accepted/rejected values, and one-row layout; do not invent a process. |
| `schemas/shape_gallery.py` | Four named schemas, clause comprehensions, and populated constants built in Node assembly. | Define meaningful clause groups and populated constants before consumers. Retain shared SHAPES, samples, independent expected layouts, and the STEP placeholder. |
| `schemas/smeac_plan.py` | Large literal template and WHERE list including comparison authority. | Expose the template and meaningful clauses without creating a second schema language. Preserve five sections, compact phases, comparison fields, and authority values. |
| `schemas/verification.py` | Named reusable five-field evidence shape. | Keep the small shape explicit; preserve subject/revision/check/result/evidence semantics and the distinction between valid shape and performed verification. |

Supporting scope is also explicit:

| Source or delivery | Treatment |
| --- | --- |
| `examples/bindings.py` | Keep the existing typed `local_bindings` helper as the sole owner. Do not promote it into a new public builder or replace it with provider-dependent code. |
| `examples/schemas/repeat_marker.py` | Retain its already-flat, shared instruction and illustrative repetition boundary. |
| `examples/shape_writer/run.py` | Update actual model-field accesses when present, but retain the fixture's literal `steps` key and detached behaviour. Keep execution and file access at the host boundary. |
| `examples/catalog.py` | Preserve registration, source ownership, learning stages, source-driven generation, and detached declarations. Name meaningful constructed groups where helpful without duplicating the registry. |
| Package `__init__.py` files | Preserve their packaging role; update actual renamed imports only. |
| All scenario `.oak.md` files, samples, local schema copies, and copied `bindings.py` files | Regenerate through the catalogue. Never patch delivery copies by hand. |
| Skill teaching, guides, references, inert template, and assembled agent | Regenerate through their existing owners and verify closure, literal preservation, scope, and parity. |
| Model metadata, build fixtures, generated reference, and embedded Python snippets outside `examples/` | Migrate active API examples and references too. Leave deliberate old-input rejection specimens and historical quotations clearly identified. |

### Challenges
- Cross-cutting names: `steps` is used in models, visitors, execution, surface metadata, JSON-LD, checks, and generated references. An example-only rename would leave incompatible consumers.
- Different meanings: instruction `body` is text, whereas process `body` will be an ordered list. JSON-LD needs an explicit ordered-list representation rather than a global list interpretation of all bodies.
- False flattening: adding helper processes or CALLs merely to reduce Python indentation would change binding scopes and output promotion.
- Excessive extraction: one name per trivial literal can make sources harder to follow. Extract meaningful constructions, not every leaf indiscriminately.
- Reused objects: separately named Pydantic instances are not automatically immutable. Do not mutate shared authored objects after assembly or bypass normal validation.

### Supporting Factors
- Higher intent: make the source read as named knowledge and ordered work, without changing meaning or adding an authoring framework.
- Adjacent efforts: existing compact OAK syntax, self-contained examples, current skill layout, modular Python standards, and SMEAC state comparisons remain intact.
- Supporting resources: existing Pydantic models, `local_bindings`, render/parse/resolve checks, deterministic hosts, conformance checks, and generated product ownership.

### Assumptions
- The requested direction includes `Statement` and `body`; implementation approval covers the explicit migration below, not just visual formatting.
- No separately identified consumer requires the old Python names. Add no compatibility alias without an explicitly approved consumer and contract.
- If main changes before implementation, compare the new revision with the reviewed baseline and refresh affected evidence before editing.

### Constraints and Limitations
- Constraint: preserve seven parts, entry identities, typed targets, templates, authored statement order, branching, process scopes, tool names, and external-effect boundaries.
- Constraint: leave OAK Host, provider integrations, package/repository splits, new agent frameworks, and language extensions outside this plan.
- Constraint: use current dependencies and direct Pydantic construction; no fluent builder, decorators, opaque factories, or post-construction mutation.
- Constraint: preserve old plans, legacy APS, literal payloads, and unrelated changes. No new README indexes.
- Limitation: source inspection establishes the migration surface, not runtime correctness. Full checks are mandatory during implementation.

## 2. Mission

The implementation agent updates OAK's Python authoring and statement-body contract across the repository in one complete change after user authorization, so examples become flatter without changing their knowledge or behaviour.

Task: Complete the contract migration, every applicable example update, derived products, negative checks, and independent review before declaring the change finished.
Purpose: Let an author define meaningful pieces once and assemble readable schemas, processes, and nodes from those pieces.
End state: `Statement` and `body` are the current Python vocabulary; examples are flat where it helps; authored OAK and execution outcomes are preserved; intentional serialized changes are documented and verified.

### Migration Contract

| Current | Desired | Boundary |
| --- | --- | --- |
| `Step`, `StepModel` | `Statement`, `StatementModel` | Recursive union, base, imports, annotations, rebuild namespaces, and applicable public exports. |
| `Process.steps`, `Foreach.steps`, `While.steps`, `Par.steps` | Corresponding `.body` | Constructor keywords, model fields, dumps, JSON Schema, validation locations, readers, and writers. |
| `If.then`, `If.otherwise` | Unchanged field names, now containing Statements | Branch names already express their role. Do not add another branch rename. |
| `iter_steps`, `step_values`, statement-specific parser/executor/encoder helper names | `iter_statements`, `statement_values`, and matching statement names | Preserve traversal and execution order, arguments apart from the named migration, and effects. |
| `oak/node/parts/processes/steps.py`, `oak/parse/steps.py`, `oak/execute/steps.py` | Sibling `statements.py` modules | Move actual owners and update all imports; do not leave forwarding modules. |
| Surface identifiers `step-*`, model slots `steps` / `STEPS` | `statement-*`, `body` / `BODY` | Update the shared descriptor and every consumer. Actual OAK keywords and delimiters stay unchanged. |
| JSON-LD process/loop/parallel `steps` | `body` with an explicit `@list` object | Keep the global `body` term usable for instruction text. Preserve ordered nested statements. |
| JSON-LD `thenSteps` | `then`, retaining its ordered-list context | Match the existing Python branch name; preserve `otherwise` and branch semantics. |

This is a deliberate breaking Python and serialized-model/JSON-LD change. Document old and new field shapes and migrate in one pass. Keep operation `kind` values, entry types, schema identities, and authored-text syntax unchanged. Do not claim existing Python callers or JSON-LD consumers are byte-compatible.

Keep existing stable diagnostic codes unless a separately justified contract change is approved. Natural-language uses of "step", domain IDs such as `reflection-step`, the shape-gallery STEP placeholder, fixture data named `steps`, and historical examples are not obsolete Python APIs. An obsolete-name scan must classify those occurrences rather than replace every match.

### State Comparisons

#### E01: Define an action before assembling its process
Authority: required
Current state:
The title-review source at the reviewed revision embeds its action and value binding inside the process. The following excerpt uses that module's existing constants and schemas.
```python
review_title_process = Process(
    id="review-title", name="Review title", input=SCHEMA_TITLE, output=SCHEMA_REVIEW,
    steps=[
        ACT(
            "Assess <TITLE> under the title policy and produce <VERDICT> and <REASON>.",
            input=SCHEMA_TITLE, output=SCHEMA_REVIEW,
            inputs=[ValueBinding(
                placeholder=PLACEHOLDER_TITLE,
                value=BindingValue(binding=PLACEHOLDER_TITLE),
            )],
            outputs=[PLACEHOLDER_VERDICT, PLACEHOLDER_REASON],
        ),
        Emit(interface=INTERFACE_REVIEW_OUTPUT),
    ],
)
```
Desired state:
```python
title_value = BindingValue(binding=PLACEHOLDER_TITLE)
title_binding = ValueBinding(placeholder=PLACEHOLDER_TITLE, value=title_value)

review_title_text = (
    "Assess <TITLE> under the title policy and produce <VERDICT> and <REASON>."
)
review_title_action = ACT(
    review_title_text,
    input=SCHEMA_TITLE,
    output=SCHEMA_REVIEW,
    inputs=[title_binding],
    outputs=[PLACEHOLDER_VERDICT, PLACEHOLDER_REASON],
)
emit_review = Emit(interface=INTERFACE_REVIEW_OUTPUT)

review_title_process = Process(
    id="review-title",
    name="Review title",
    input=SCHEMA_TITLE,
    output=SCHEMA_REVIEW,
    body=[review_title_action, emit_review],
)
```
Acceptance: The separately named values remain ordinary validated OAK models. Process assembly contains references instead of nested statement construction. Preserve the action text, contracts, binding source, outputs, and emission order exactly. Domain names may vary elsewhere; no new process or wrapper API is introduced. Confirm the example renders identically and direct/context execution agrees.

#### E02: Flatten construction without flattening execution scope
Authority: required
Current state:
`compound_growth/example.py` nests a comparison, CALL, bindings, and SET inside `While(steps=[...])`, itself inside `Process(steps=[...])`. The Step union has eleven variants; IF owns `then` and `otherwise`, while FOREACH, WHILE, and PAR own `steps`.
Desired state:
Define the existing comparison and each existing statement separately, then assemble the block and process. This assembly excerpt refers to those separately defined objects, not new helper processes.
```python
growth_loop = While(
    condition=balance_below_target,
    limit=60,
    body=[scale_current_balance_call, update_current_balance],
)
grow_balance_process = Process(
    id="grow-balance",
    name="Grow balance",
    input=SCHEMA_GROWTH_TARGET,
    body=[
        growth_loop,
        reflect_growth_action,
        scale_reflection_target_call,
        update_reflection_target,
        emit_reflection,
    ],
)
```
Acceptance: Apply body consistently to Process, Foreach, While, and Par, including nested instances. Retain IF branch names. Preserve eleven variants, discriminators, nonempty bodies, PAR restrictions, JOIN order, child scopes, and loop bounds. The growth fixture still yields balances 815.04 and 6642.28 with reflection targets 6400 and 51200; failed reflection cannot leak staged state or emissions.

#### E03: Distinguish instruction text from ordered JSON-LD bodies
Authority: required
Current state:
`oak/render/json_ld/context.py` maps `body` to ordinary instruction text, while `steps` and `thenSteps` have list containers. `entries.py` separately encodes those fields. Renaming the list-container key to body globally would incorrectly treat instruction text as a list.
Desired state:
Keep the ordinary `body` term mapping and explicitly wrap process, loop, and parallel bodies in `@list`. These are partial JSON-LD node specimens using the existing OAK vocabulary prefix.
```json
{"@type": "oak:Instruction", "body": "Keep the task scope."}
```
```json
{"@type": "oak:Process", "body": {"@list": [{"@type": "oak:Act", "instruction": "Review the supplied context."}]}}
```
The specimens demonstrate field encoding; full documents still require their normal validated entries. Rename the branch-list term `thenSteps` to `then` in both context and encoding; preserve the existing ordered treatment of `otherwise`. Python model dumps use ordinary body arrays, not JSON-LD list objects.
Acceptance: Mixed documents preserve instruction strings and ordered nested statement lists. Check context mappings, exact rendered JSON-LD shapes, and branch order independently of the encoder. No old structural steps/thenSteps fields remain in current encoding. Do not modify keys inside constant JSON literals or other user data. Update interchange documentation explicitly rather than claiming wire compatibility.

#### E04: Keep schemas readable without altering their information shapes
Authority: required
Current state:
Schema sources range from a small one-clause error shape to the large SMEAC template and WHERE list. Several contain dense constraints, nested comprehensions, or populated constants constructed directly in Node assembly.
Desired state:
Keep named schemas; place a meaningful template, long clause, or reusable clause group before its consumer when this improves reading. Assemble Nodes from named entries. Retain simple inline `Type`, small `where` calls, and meaningful existing helpers when extraction would add only navigation. Preserve adjacent string literals and use no strip/dedent normalization.
Acceptance: Review all twelve schema modules and record either the concrete improvement or why the current flat form is retained. Preserve exact template bytes, clause order, constraints, example values, allowed enums, cross-placeholder bounds, and repeated-slot semantics. Keep the literal STEP placeholder and sample-data steps key unchanged. Validate positive and negative bindings and populated layout fixtures.

#### E05: Deliver one complete change across all current consumers
Authority: required
Current state:
The catalogue regenerates scenario siblings, samples, local schema copies, copied bindings, and the teaching catalogue. The authoring build consumes shared rules and examples to produce the skill and assembled agent; the optional validator pins a core revision and source/dependency fingerprints.
Desired state:
Every current source consumer uses the new API. Regenerated deliveries use the current `assets/examples`, numbered references, separate guides, and inert template layout. Existing scenario document text remains unchanged; terminology and contract documentation change only through their source owners. Both skill and assembled agent retain equivalent operational behaviour.
Acceptance: Cover all 23 registered source modules plus helpers, catalogue, embedded active examples, checks, metadata, and generated reference. Preserve detached closure, exact literals, fixture outcomes, consent behaviour, source scopes, schema identities, and the four teaching stages. Refresh validator identity against a real immutable commit containing the changed core. Full verification and repeated generation must pass without unexplained differences or stale files.

## 3. Execution

Intent: Remove construction nesting that obscures knowledge, not structure that conveys its meaning. Rename the model vocabulary consistently and prove that the authoring change preserves routing, values, order, and effects. Do not trade readability for a new abstraction layer.
Concept of operations: Establish a trustworthy baseline, migrate the model and consumers, flatten the registered sources, regenerate the products, and verify all boundaries. The phases form one complete deliverable, not optional follow-on projects. All implementation tasks remain open until their stated evidence exists.

### Phase 1: Establish the baseline and owning contracts
Objective: Record the accepted migration and a reproducible before-state before implementation changes.
- [x] Key task: P01.01 Confirm the active main revision against the reviewed SHA, read all applicable AGENTS and routed Python/specialist material, and reconcile any intervening changes without rewriting history.
- [x] Key task: P01.02 Run the unmodified complete verification commands and capture existing failures separately; record source-derived canonical XML/Markdown, model and JSON-LD samples, scenario outcomes, and generated file sets for comparison.
- [x] Key task: P01.03 Inventory Step/StepModel, steps fields, step modules/helpers, surface identifiers, metadata, error codes, and generated examples; classify structural references versus literal/domain/history exceptions.
- [x] Key task: P01.04 Update the owning examples AGENTS rule for define-before-assemble authoring, and the relevant node/build ownership contracts for statement bodies and verification; avoid copying the same policy into multiple owners.
Success criteria: The before-state and all affected owners are identified; E01 through E05 have concrete verification subjects; no baseline failure is represented as a successful check.
Transition trigger: The migration scope and independent baseline evidence are recorded.

### Phase 2: Migrate statements and every semantic consumer
Objective: Make the new contract coherent across models, parsing, validation, resolution, rendering, and execution.
- [x] Key task: P02.01 Rename Step/StepModel, the three step modules, exports, recursive annotations/rebuild namespaces, field metadata, and all four steps fields; retain IF branch names and normal model validation.
- [x] Key task: P02.02 Update direct authoring helpers, model/index/flow validation, process visitors, target discovery, resolver checks, native interpreter context, executor frames, parallel handling, and supplied handler types without changing behaviour.
- [x] Key task: P02.03 Update oak/surface/processes.py and its parser, renderer, grammar, and documentation consumers together, including step-prefixed surface IDs and STEPS slots; preserve authored tokens and delimiters.
- [x] Key task: P02.04 Update JSON-LD statement encoding, context terms, helper names, and metadata using explicit body list objects; retain scalar instruction bodies, branch ordering, and literal JSON isolation.
- [x] Key task: P02.05 Migrate active model examples and repository checks with the API, and document intentional Python/model/JSON-LD breaks without aliases or forwarding modules; preserve explicitly retained diagnostic contracts.
Success criteria: E02 and E03 pass for all eleven variants, nested combinations, normal dumps, JSON Schema, JSON-LD, and existing OAK text. Current code imports no obsolete statement module or alias.
Transition trigger: The complete core contract is implemented and its focused positive and negative checks pass.

### Phase 3: Flatten all applicable human authoring sources
Objective: Make each example a readable assembly of named, directly validated pieces.
- [x] Key task: P03.01 Implement E01 in interpreter_context and flatten shape_writer actions, calls, emissions, and meaningful input groups; retain the existing deterministic adapters and output contracts.
- [x] Key task: P03.02 Flatten compound_growth leaf values, binding groups, comparison, loop, calls, writes, reflection, and emission; use schema-before-consumer dependency order and keep runtime work inside host functions.
- [x] Key task: P03.03 Flatten implementer verification gates and blocked/success branches while preserving exact snapshot, revision, check, effect, and completion semantics.
- [x] Key task: P03.04 Flatten delegation and its task_reviewer without fusing scopes or changing exact tool dispatch; preserve the original worker result.
- [x] Key task: P03.05 Flatten successor and its amendment_reviewer/successor_verifier leaf workers, including review guards, start/resume bindings, six proof assertions, state writes, and publication branches.
- [x] Key task: P03.06 Review and update all twelve schema sources under the dispositions above; retain simple forms, preserve literal layouts, and move only meaningful dense definitions outside consumers.
- [x] Key task: P03.07 Verify fixed_knowledge, the shape_gallery wrapper, repetition helper, binding owner, catalogue, and detached runner; record justified unchanged sources instead of adding unused structure.
Success criteria: E01, E02, and E04 hold; all 23 registered source modules have a recorded disposition. No process, loop, or branch hides nontrivial statement construction inside its assembly list, and no new runtime scope was introduced for layout.
Transition trigger: The source review confirms flat construction, preserved contracts, and complete example coverage.

### Phase 4: Refresh derived knowledge and delivery
Objective: Ship one consistent current API and the unchanged scenario knowledge through every generated product.
- [x] Key task: P04.01 Refresh shared authoring guidance only where relevant, update build/authoring_guides.py, build/fusion.py, and active teaching snippets for renamed API consumers, preserving literal embedded documents and operational scope.
- [x] Key task: P04.02 Run catalogue generation to refresh scenario snapshots, samples, local dependencies, copied bindings, and catalog.oak.md; require unchanged baseline scenario OAK bytes rather than accepting unexplained snapshot updates.
- [x] Key task: P04.03 Regenerate EBNF and model/surface reference; inspect model examples, JSON Schema definitions, surface paths, and removal of stale generated pages.
- [ ] Key task: P04.04 Commit the changed core normally, then update the optional validator's immutable revision and source/dependency fingerprints according to its existing identity checks; never point it at floating main or invent a revision.
- [ ] Key task: P04.05 Regenerate SKILL.md, numbered references, guides, assets/examples, the inert _template scaffold, and outputs/oak-authoring.oak.md; retain current file ownership, consent outcomes, and size budgets.
Success criteria: E05 holds across the actual exported file sets and validator identity; every generated change is explained by a source change, and no scenario literal or operational scope drifts.
Transition trigger: All delivered forms are regenerated from their source owners and ready for full verification.

### Phase 5: Verify semantics, rejection paths, and freshness
Objective: Prove the new API and flatter sources preserve meaning while rejecting obsolete structural input.
- [x] Key task: P05.01 Add focused checks to the existing verification system for named versus inline construction, all eleven Statement variants, recursive bodies, IF branches, schema metadata, and missing/empty/malformed body rejection.
- [x] Key task: P05.02 Reject old steps inputs, mixed body/steps inputs, old public aliases, and stale imports; test valid and invalid nested combinations without relaxing existing validation or PAR/JOIN restrictions.
- [x] Key task: P05.03 Compare current canonical models against the baseline with a model-aware field migration only; compare authored XML/Markdown bytes exactly, and validate intentional JSON-LD differences using independent mixed-body/order/literal specimens.
- [x] Key task: P05.04 Run every catalogue scenario, both groupings, schema binding and layout checks, and declared detached demonstrations with repository imports/network blocked; verify evidence rejection, state isolation, context scopes, and simulated-effect disclosures.
- [ ] Key task: P05.05 Run compileall, python -m build.examples, and python build/examples.py, including skill-agent parity, consent, fingerprint, reference freshness, plan, and scoped AGENTS checks; record the exact tested commit and observed results.
- [ ] Key task: P05.06 Repeat all affected generation and require no diff; search obsolete identifiers, fields, module paths, surface IDs, and active snippets, recording each legitimate literal/history/diagnostic exception explicitly.
Success criteria: E01 through E05 are evidenced at the final candidate; complete verification passes, detached products remain bounded, and repeated generation changes nothing. A text search or valid schema is never substituted for behavioural evidence.
Transition trigger: The exact final candidate satisfies every preservation, rejection, and delivery check.

### Phase 6: Review and deliver the completed change
Objective: Complete the implementation only after independent contract and source review.
- [ ] Key task: P06.01 Review the final diff independently against the migration table, every example disposition, and E01 through E05; apply findings and rerun all affected verification against the resulting candidate.
- [ ] Key task: P06.02 Add report.md with actual changed paths, retained examples, compatibility changes, commands/results, final revision, and remaining limitations; check off tasks only when their evidence is present.
- [ ] Key task: P06.03 Commit without rewriting history and open the implementation PR with a subject marking the deliberate breaking contract; do not merge without a separate user instruction.
Success criteria: All applicable tasks are complete, E01 through E05 are independently reviewed, the final verdict is supported, and the PR points to the verified candidate rather than an earlier revision.
Transition trigger: Implementation is ready for user review; merge authorization remains separate.

### Coordinating Instructions
- Timeline: Start only after explicit implementation authorization. Finish all phases before the implementation PR is described as complete; no delivery-time estimate is asserted.
- Boundaries: This planning change writes only this plan. Implementation updates the existing repository, not sibling repositories or provider integrations.
- Operating guidelines: Define dependencies before consumers; keep meaningful names near use; assemble named entries directly. Existing shallow helpers and data-driven groups remain valid. Do not enforce an arbitrary maximum indentation score as proof of good design.
- Risk mitigation: Preserve baseline expectations independently of new constructors; classify field renames by model type; never perform a recursive blanket replacement of keys inside literal payloads.

### Contingencies
- If main changes, compare and refresh the affected review before editing; preserve the branch history and use ordinary merge commits where integration is needed.
- If a baseline check fails, report and isolate it before interpreting candidate failures; never tick a verification task without its evidence.
- If a supported external consumer is identified, stop the breaking release decision for explicit contract review rather than silently add compatibility aliases.
- If extraction changes a document identity, scope, binding lifetime, output order, or effect boundary, restore the original semantic structure and flatten only its Python construction.
- If a generated snapshot changes unexpectedly, investigate its owner; do not accept the new snapshot merely to make freshness checks pass.

## 4. Admin and Logistics

| Resource | Quantity | Source | Status |
| --- | --- | --- | --- |
| Pinned source review | One main revision | eca953bd81f78f005fdc1b3d17ed060620f6c97d through GitHub | AVAILABLE |
| Example authoring inventory | 23 registered modules plus support sources | examples/catalog.py and the review table | AVAILABLE |
| Owning knowledge and format | Root/scoped AGENTS and SMEAC schema | Existing repository sources | AVAILABLE |
| Executable repository checkout and declared dependencies | One isolated implementation environment | Provision during implementation | PENDING |
| Baseline and candidate verification evidence | Two revision-linked records | Existing build and example checks | PENDING |
| Independent implementation review | One final-candidate review | Implementation completion gate | PENDING |

Supply: Reuse the declared dependencies and current helper owners. Read the routed Pydantic, JSON Schema, and JSON-LD specialist material before changing those contracts; do not install optional tooling without required approval.
Transportation: Keep the plan on a docs branch from the reviewed main revision. Carry the implementation through ordinary commits; regenerate artifacts rather than copying their edits between owners.
Sustainment: Keep durable authoring rules in the owning AGENTS documents and executable checks in the current build system. Preserve the current catalogue and generated product ownership instead of creating another index or framework.
Rollback: Revert the complete implementation with new commits if required, including its dependent generated products and validator identity. Do not amend, rebase, squash, force-push, or leave mixed old/new contracts in a purportedly completed revision.

Reference basis: [Python AST documentation](https://docs.python.org/3/library/ast.html) demonstrates body lists of statements; it is naming precedent, not an OAK runtime dependency. [Pydantic model documentation](https://docs.pydantic.dev/latest/concepts/models/) supports composing existing model instances and documents validation/rebuild behaviour; it does not make shared instances immutable. [JSON-LD 1.1 value ordering](https://www.w3.org/TR/json-ld11/#value-ordering) defines ordered lists, including explicit list objects used in E03. These sources were consulted on 2026-09-06; the decisions and acceptance criteria above remain specific to OAK.

## 5. Command and Signal

1. Chris Buckley, scope, contract, implementation-start, and merge authority.
2. Implementation agent, execution and evidence collection after authorization; unresolved scope or compatibility decisions return to Chris.

| Channel | Medium | Purpose | Cadence |
| --- | --- | --- | --- |
| Conversation | Chat | Report findings, blockers, and authorization boundaries | At meaningful checkpoints |
| Plan | This Markdown brief | Track tasks and accepted state comparisons | When observed status changes |
| Completion | report.md and implementation PR | Record verified outcome and review evidence | After complete implementation |

Reporting: Distinguish source inspection from executed verification. Record the exact candidate revision, commands, observed results, changed/retained examples, and compatibility consequences. The absence of live model calls is intentional; deterministic fixtures do not establish arbitrary model quality.

| Decision | Authority | Escalation |
| --- | --- | --- |
| Start implementation | Chris Buckley | Do not infer authorization from plan readiness |
| Change scope or add compatibility | Chris Buckley | Present the specific contract and consumer |
| Mark a task complete | Implementation agent with recorded evidence | Leave open when evidence is absent |
| Merge the implementation | Chris Buckley | Require a separate instruction |

### Acknowledgement
Receipt of this plan does not authorize implementation. The implementing agent must acknowledge the scope and applicable repository knowledge when the user instructs it to continue.
