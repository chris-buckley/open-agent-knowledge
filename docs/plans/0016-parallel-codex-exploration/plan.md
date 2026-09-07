# Deliver OAK exploration agents as native Codex artifacts

Prepared: 2026-09-07T12:09:23+10:00
Classification: PUBLIC
Amendment: The user's 2026-09-07T03:57:06Z instruction removes host implementation and live-client acceptance, authorizes this plan update first, and then authorizes complete implementation and a review PR.
Readiness: Approved for the artifact-only scope below; no further implementation approval is required for this scope.
Execution: Implementation and separate technical review are complete; both full cloud entry points passed. Nineteen tasks are evidenced. D05.02 awaits final declared-dependency confirmation; D06.02 and D06.03 await committed remote verification and the actual PR URL/check results. No merge is authorized.
Recovery: Host task `82d0f13f-f86a-46bb-9f24-74f5d94bd5dd` continues from the verified final 615-file checkpoint 02, SHA-256 `884494e3345ab2eba9aabf4c200562072c5041d2b4cb85396e5af43225368d44`. Original governing authority stays pinned below; changed scoped AGENTS files are task outputs, not substituted governing inputs.
Evidence: [Final implementation handoff](report.md) and [artifact verification](evidence/artifact-verification.json). The [D03 review](evidence/d03-review.md) and [D03 content preservation](evidence/d03-preservation.json) remain milestone history. Final exact command receipts and full source manifests are included in delivery 03.
Branch: `docs/plan-parallel-codex-exploration`
Artifact-only base: `88340b4bde9d58295e881884a80a0a99c247e13a`. The earlier `7a655da3df59c247d5f626aeb57fcaa7ddbf5d9b` was the pre-amendment planning checkpoint.
Pinned governing and product baseline: `9956e6998869fcfbd84067eec0d6303273a54174`

## 1. Situation

### Operating Environment
OAK defines portable knowledge and ordered work. This change delivers the explorer's native Codex TOML, a portable parallel example, shared adaptor knowledge, and reusable directory-change planning. It does not supply a Codex runtime or execute a model.

### Current State
At the approved baseline, the branch contained the earlier plan, native-client research, and a blocked implementation preflight, but no product implementation. The execution header records current progress. The package already supports `ACT.tool(...)`, `Par(body=[...])`, and `Join()`; its existing delegation example uses a deterministic worker. The generated tree has the authoring skill, standalone authoring agent, grammar, and construct definitions, but no agent bundle or native explorer TOML.

### Challenges
- Honest portability: a native agent file is configuration and knowledge, not a supplied exact-tool registry, sandbox implementation, or proof of live concurrency.
- Source ownership: one explorer definition must produce its canonical OAK and native developer instructions without independent prompt copies.
- Delivery closure: copying the native TOML must not require a launcher, MCP server, source checkout, credentials file, or another generated product.
- Size: existing authoring limits remain 10,000 bytes for the skill entry and 64,000 bytes for the standalone agent; retain existing knowledge and literal teaching.
- Planning visibility: the detailed directory view must enter the actual SMEAC schema and prospective checks, not remain a chat convention.

### Supporting Factors
- Higher intent: usable agent artifacts with clear OAK meaning, native read-only defaults, parallel-authoring examples, and little machinery.
- Adjacent efforts: retain the agreed `generated/oak.agents/` layout, flat Python authoring, separate operational document scopes, and existing generated products.
- Supporting resources: pinned governing owners, the package and current example catalogue, existing generation/check entry points, and the official Codex documentation cited below.

### Assumptions
- The deliverable is the agent TOML and knowledge, not an installed or runtime-certified agent. The user explicitly removed host-related work.
- The native parent conversation orchestrates multiple instances of the same leaf explorer. It does not need a second installed coordinator agent or increased nested-delegation settings.
- The portable coordinator demonstrates checked OAK PAR/JOIN with repository-only deterministic registrations. Those illustrative exact tool names are not represented as Codex built-ins.
- Current OAK syntax is sufficient; no new language construct, runtime API, external task format, or dependency is required.

### Constraints and Limitations
- Constraint: preserve the original commits. This amendment starts a new, explicitly authorized artifact-only scope; earlier host tasks are withdrawn, not passed.
- Constraint: no app-server transport, MCP server, installer, launcher, runtime tool implementation, host authorization service, UI automation, live model calls, credential checks, or deployment scripts. Do not ship `run.py`, `serve.py`, `install.py`, `transport.py`, `tools.py`, or `contracts.py` in the generated agent bundle.
- Constraint: repository build, source examples, and verification Python remain necessary and authorized. They must not become a hidden runtime dependency of the native TOML.
- Constraint: no installed Codex, desktop access, model account, MCP SDK, or live-use budget is a completion gate for this amended scope. Do not claim those removed checks passed.
- Constraint: work directly without subagents. Preserve main, unrelated changes, APS history, the 500-line AGENTS bound, existing product byte limits, validator consent and identity safeguards, and scope-safe fusion.
- Constraint: generated files remain deliveries; edit their source owners and regenerate. Add no README indexes, speculative providers, permission DSL, dependency, or temporary CI/publishing infrastructure.
- Constraint: update the owning AGENTS knowledge for the durable scope and directory-planning decisions before proceeding with their implementation. Keep root lifecycle contracts unchanged.
- Limitation: native permissions, inherited tools, effective sandbox behavior, installation/discovery, model quality, and CLI/desktop runtime compatibility will not be certified by artifact tests.
- Limitation: direct archive networking failed in earlier preflight. Available connector access and existing source artifacts may support source restoration; any executed checks must identify the actual tested source and environment rather than silently using an older snapshot.

### Authorization and superseded scope

The prior plan at `612eeae81971c7b75d89d75171ba9a33de8b38d9` and [implementation preflight](evidence/implementation-preflight.md) remain historical evidence. All 42 former implementation tasks were open. Their identifiers and acceptance history remain recoverable in Git; none is retrospectively marked complete. This replacement uses D-prefixed tasks and E13 through E20 to distinguish the approved new work.

| Former responsibility | Disposition in this amendment |
| --- | --- |
| Installed backend/protocol/profile and native UI gates | Withdrawn by the user. |
| Live calls, permission enforcement, admission, cancellation and audit services | Withdrawn; no replacement service or prompt-only enforcement claim. |
| Native installer, MCP merge fragment and optional SDK dependency | Withdrawn; deliver one ready TOML for manual placement. |
| Portable worker, flat ACT.tool/PAR/JOIN example and failure semantics | Retained with explicitly deterministic repository verification. |
| Generated .agents scenario bundle, shared adaptor knowledge and authoring parity | Retained; generated bundle contains text/TOML only. |
| SMEAC Directory Changes source, sibling render, owning guidance and checks | Retained in full. |
| Completed-work PR | Authorized after implementation and verification; no merge authorized. |

The [native-client research](evidence/native-clients-research.md) explains the superseded host design. Its historical decisions do not reintroduce removed work. For the present artifact contract, [official subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents) describes standalone files under project `.codex/agents/` or personal `~/.codex/agents/`, required `name`, `description`, and `developer_instructions`, and parent runtime overrides. The [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) documents the settings used below. These sources were rechecked on 2026-09-07; they are not observations of an installed client. The intended consumers remain Codex CLI and the ChatGPT desktop app's local Codex mode, not a VS Code integration or ordinary hosted Chat/Work.

## 2. Mission

The implementing assistant delivers and verifies the approved artifact-only OAK exploration capability on this branch, then opens a review PR without requiring a Codex host.

Task: generate a ready leaf-agent TOML from OAK, retain an executable repository-only parallel demonstration, expand shared authoring knowledge, implement annotated SMEAC directory changes, and verify the complete change.
Purpose: make the actual agent easy to obtain and inspect while preserving responsibility, source identity, and honest capability claims.
End state: the generated scenario contains coordinator, explorer, sample knowledge, and a ready `oak-explorer.toml`; the shared adaptor is an OAK knowledge document, not executable host machinery. The source/checks demonstrate OAK parallel semantics offline; the native file embeds the exact explorer knowledge and documented read-only defaults. The actual planning schema and prospective checks include detailed directory views.

### Architecture Decisions

#### A01: One native leaf explorer, not an integration service

Generate `generated/oak.agents/parallel_exploration/codex/.codex/agents/oak-explorer.toml`. Its `name` is `oak-explorer`, avoiding built-in name replacement. Define a useful description, then serialize the exact canonical `explorer.oak.md` as `developer_instructions`; TOML decoding must recover identical bytes including newlines. No independent English prompt, truncated instructions, machine-specific path, included script, or external OAK reference is allowed.

Use the documented defaults `sandbox_mode = "read-only"`, `approval_policy = "never"`, `web_search = "disabled"`, and `[agents] enabled = false` for the leaf. Do not invent a `tools` allowlist field or disable all file-reading capability by assuming shell tools are unnecessary. Explicitly describe these as requested native configuration defaults: inherited parent runtime overrides and external tool availability remain host concerns. The OAK worker restricts its own task to reads and evidence, forbids edits, installation, unrequested network/connectors, and further delegation, and reports blocked/unknown conditions rather than inventing evidence. Configuration validity does not prove universal enforcement.

Leave model/provider/authentication choices to the user's native client. The delivered TOML is ready for manual copying into the target project's `.codex/agents/` or the user's chosen personal agent directory; generation performs no installation and never edits `.codex/config.toml`. The shared adaptor explains discovery locations, collisions, inherited settings, the two intended client surfaces, and verification limits. No separate native coordinator TOML is needed: the normal parent conversation requests two independent `oak-explorer` instances, waits, reconciles evidence, and owns the final answer.

#### A02: Keep the portable coordinator and native usage distinction explicit

The portable coordinator is a separate, locally contract-complete OAK document. Preserve the agreed flat Python construction using `ACT.tool("agent.explore-runtime", ...)` and `ACT.tool("agent.explore-contracts", ...)`, distinct report bindings, `Par`, an immediately following `Join()`, and synthesis after the join. The repository example supplies real deterministic ToolContract registrations which invoke the worker's OAK arrival/process and return validated emissions. These names are fixture registry entries, not native Codex tools, and the generated native TOML must not require them.

The worker receives a question, path scope, and revision identity and emits a typed report with findings, file-and-line evidence, inspected coverage, unresolved questions, and an explicit completion/blocked status. Validate complete local contracts and preserve the difference between a supplied revision and one actually inspected. Do not promote a failed, blocked, wrong-revision, or malformed report into successful synthesis. Do not infer execution from a test file that was merely read.

Keep sample request/data and a native-parent invocation example as literal knowledge in `sample.oak.md`. The native invocation asks for two leaf explorers on independent execution/dataflow and contract/verification questions, the same revision, complete applicable AGENTS context, no changes, and a joined evidence-based answer. It does not claim that native interpretation mechanically runs the Python OAK executor. Actual OAK concurrency is demonstrated by deterministic repository tests, not by native runtime certification.

#### A03: Source and delivery ownership

| Owner | Responsibility |
| --- | --- |
| `examples/parallel_exploration/explorer.py` | Reusable locally complete OAK leaf definition; canonical sibling and native developer instructions share this source. |
| `examples/parallel_exploration/example.py` | Flat coordinator, complete fixtures, sample knowledge and registered repository-only demonstration. |
| `examples/catalog.py` | Scenario registration, complete source-scenario file set and source-derived catalogue; retain the existing four teaching stages. |
| `.agents/adaptors/codex/adaptor.oak.md` | Maintained pure OAK native-file metadata/settings knowledge, dated sources, use and limitations; constants/schemas only for safe authoring fusion. |
| `build/agents.py` | Deterministic text/TOML bundle generation and complete owned file set through existing safe generation primitives. |
| `build/authoring_guides.py` and `build/authoring.py` | Portable orchestration guidance, explicit routing, and the identical shared knowledge in skill and standalone agent. |
| `build/fusion.py` | Compact generated gN- support namespaces; preserve descriptive suffixes, typed targets, collision checks and literal values. |
| `build/authoring_validator.py` | Skill version metadata refresh only; retain the existing executable helper, immutable runtime revision and fingerprints. |
| `examples/schemas/smeac_plan.py` | Actual Directory Changes template and WHERE meaning, with regenerated canonical sibling. |
| `docs/AGENTS.md`, `examples/AGENTS.md`, `build/AGENTS.md` | Prospective plan policy, presentation/source ownership, generated layout and verification respectively. |
| Existing check registry and new `build/checks/agent_deliveries.py` | Static native metadata, exact embedding, closure, concurrency fixtures, rejected inputs, freshness, and explicit absence of host deliveries. |
| `build/checks/plans.py` and `build/checks/plan_fixtures.py` | Schema-derived directory checks, prospective adoption and independently populated positive/negative specimens. |
| `build/checks/shapes.py` | Inspect retained literal teaching against independent shape definitions and populated expectations; preserve existing behavioral checks. |

Bundle the OAK scenario graph and native TOML, not its repository demonstration code. Copying the TOML alone is sufficient for its declared instruction content. Copying a scenario closes its OAK references. The shared adaptor sits at `generated/oak.agents/adaptors/codex/adaptor.oak.md` and is also provided as identical knowledge under the authoring skill's `platforms/codex/` path. Generated duplication has one maintained source. Keep separate operational documents separate; do not fuse worker/coordinator scopes into the authoring agent. Supporting authoring documents remain constants/schemas only; examples are inert teaching.

Use the current complete generation paths and prune only owned subtrees. Preserve the existing grammar, definitions, template, core teaching documents, validator policy and no-install authoring. Measure any needed authoring-size reduction and review retained meaning independently; do not raise limits, drop required knowledge, externalize standalone dependencies, or encode prose opaquely.

#### A04: Reusable orchestration guidance

Carry forward APS's useful separation of coordinator, leaf workers, public contracts, task scope, request/result mapping, and host-specific knowledge. Express it in OAK, leaving APS untouched. Cover native ACT versus an exact tool action, independent task splitting, complete pinned governing context, immutable frame bindings, PAR/JOIN ordering, distinct outputs, all-or-fail results, conflict reconciliation, and evidence limits. Distinguish sequential CALL within a document from a host-spawned agent. Explain that a tool name or TOML default neither provisions a capability nor establishes its enforcement.

#### A05: Detailed directory planning belongs to the SMEAC schema

Insert `### Directory Changes` in Mission after End state and before State Comparisons in the actual SMEAC template. Add string placeholders/WHERE descriptions for DIRECTORY_BASELINE, DIRECTORY_CURRENT, DIRECTORY_PLANNED, DIRECTORY_OWNERSHIP, and DIRECTORY_VERIFICATION. Keep the five sections, comparison authority, and compact phases unchanged.

Use current and planned fenced text trees with annotated affected files, purpose notes, and source/output owners. A fixed legend distinguishes [add], [modify], [move from PATH], [remove], [keep], and [check]. Moves name their source; removals remain visible. Do not use ellipses to hide affected leaves. A no-file-change plan retains a reason and `No directory or file changes.` instead of a fictional tree.

The docs owner requires the subsection for new plans from 0016 and for explicitly reopened older plans; existing historical records remain unchanged and retain all their other checks. Extend the existing plan checker from the schema's fields/fences, with independent fixed specimens for additions, moves, removals, no changes and an unknown baseline. Do not invent a tree parser, manifest language, or new diff engine. Final review separately reconciles the diagram with actual changed paths.

### Directory Changes

Baseline: product revision `9956e6998869fcfbd84067eec0d6303273a54174` plus the plan/research/preflight checkpoint `7a655da3df59c247d5f626aeb57fcaa7ddbf5d9b`. The earlier host file trees described proposed files, not implemented files; they are withdrawn, not files to delete.
Legend: [add] new; [modify] changed; [move from PATH] relocated; [remove] deleted; [keep] unchanged context; [check] verify and change only if needed.
Current:
```text
open-agent-knowledge/
├── .agents/rules/context.oak.md             # Context/specialist routing
├── examples/
│   ├── AGENTS.md                           # Example and schema conventions
│   ├── catalog.py                          # Registered scenarios
│   ├── catalog.oak.md                      # Generated catalogue
│   └── schemas/
│       ├── smeac_plan.py                   # SMEAC source, no Directory Changes
│       └── smeac_plan.oak.md               # Canonical schema delivery
├── build/
│   ├── AGENTS.md                           # Existing generated ownership
│   ├── authoring.py                        # Shared skill/standalone delivery
│   ├── authoring_guides.py                 # Existing knowledge and workflow
│   ├── authoring_validator.py              # Immutable optional validator
│   ├── generated.py                        # Safe generation primitives
│   └── checks/
│       ├── __init__.py                     # Complete check registration
│       ├── authoring.py                    # Shared knowledge and size checks
│       ├── human_examples.py               # Scenario closure
│       ├── outputs.py                      # Freshness and cold generation
│       └── plans.py                        # SMEAC structure checks
├── generated/
│   ├── oak-authoring.oak.md                # Standalone authoring delivery
│   ├── oak-authoring.skill/                # Existing skill; no Codex knowledge
│   ├── oak.ebnf                            # Grammar
│   └── definitions/                        # Construct reference
└── docs/
    ├── AGENTS.md                           # Prospective planning policy
    └── plans/0016-parallel-codex-exploration/
        ├── plan.md                         # Prior broad proposal
        └── evidence/
            ├── native-clients-research.md  # Historical host research
            └── implementation-preflight.md # Historical host blocker
```
Planned:
```text
open-agent-knowledge/
├── .agents/
│   ├── rules/context.oak.md                 # [modify] Route native adaptor knowledge
│   └── adaptors/codex/adaptor.oak.md         # [add] Sole maintained Codex knowledge
├── build/
│   ├── AGENTS.md                           # [modify] Artifact and verification ownership
│   ├── agents.py                           # [add] Five-file text/TOML generator
│   ├── authoring.py                        # [keep] Existing shared delivery entry point
│   ├── authoring_guides.py                 # [modify] Shared knowledge and action routing
│   ├── authoring_validator.py              # [modify] Skill version only, same validator
│   ├── fusion.py                           # [modify] Compact typed support prefixes
│   ├── generated.py                        # [keep] Existing safe write/prune primitive
│   └── checks/
│       ├── __init__.py                     # [modify] Register artifact verification
│       ├── agent_deliveries.py             # [add] Artifact and parallel rejection checks
│       ├── authoring.py                    # [modify] Retention, routing and parity checks
│       ├── human_examples.py               # [keep] Catalogue-driven scenario checks
│       ├── outputs.py                      # [modify] Complete cold/repair ownership
│       ├── plan_fixtures.py                # [add] Independent populated plan specimens
│       ├── plans.py                        # [modify] Schema-derived directory validation
│       └── shapes.py                       # [modify] Retained-teaching integration fix
├── examples/
│   ├── AGENTS.md                           # [modify] Artifact and tree conventions
│   ├── catalog.py                          # [modify] Register offline parallel scenario
│   ├── catalog.oak.md                      # [modify] Source-derived catalogue
│   ├── parallel_exploration/
│   │   ├── explorer.py                     # [add] Sole worker authoring source
│   │   ├── explorer.oak.md                 # [add] Canonical worker from explorer.py
│   │   ├── example.py                      # [add] Flat coordinator and offline fixtures
│   │   ├── example.oak.md                  # [add] Canonical coordinator from example.py
│   │   └── sample.oak.md                   # [add] Request/usage data from example.py
│   └── schemas/
│       ├── smeac_plan.py                   # [modify] Five described directory fields
│       └── smeac_plan.oak.md               # [modify] Canonical schema from smeac_plan.py
├── generated/
│   ├── oak.agents/
│   │   ├── parallel_exploration/
│   │   │   ├── coordinator.oak.md          # [add] From example.py, separate OAK scope
│   │   │   ├── explorer.oak.md             # [add] From explorer.py
│   │   │   ├── sample.oak.md               # [add] From example.py
│   │   │   └── codex/.codex/agents/
│   │   │       └── oak-explorer.toml       # [add] Exact worker in native wrapper
│   │   └── adaptors/codex/adaptor.oak.md    # [add] Identical maintained adaptor copy
│   ├── oak-authoring.oak.md                # [modify] Shared knowledge fused by authoring.py
│   ├── oak-authoring.skill/
│   │   ├── SKILL.md                        # [modify] Typed shared-knowledge routing
│   │   ├── guides/
│   │   │   ├── subagent-orchestration.oak.md # [add] From authoring_guides.py
│   │   │   ├── authoring.oak.md            # [modify] Concise template-use guidance
│   │   │   ├── review.oak.md               # [modify] Same eight literal teaching documents
│   │   │   └── validation.oak.md           # [modify] Same helper/consent, skill version
│   │   ├── platforms/codex/adaptor.oak.md  # [add] Same maintained Codex knowledge
│   │   ├── references/
│   │   │   ├── 00-structure.oak.md         # [keep] Complete structural knowledge
│   │   │   ├── 01-schemas.oak.md           # [modify] Route complete literal shape gallery
│   │   │   ├── 02-constants.oak.md         # [keep] Constant forms and rules
│   │   │   ├── 03-state.oak.md             # [modify] Remove duplicate lifetime table
│   │   │   ├── 04-interfaces.oak.md        # [keep] Local boundary knowledge
│   │   │   ├── 05-triggers.oak.md          # [modify] Concise unchanged routing meaning
│   │   │   ├── 06-processes.oak.md         # [modify] Delegate rules move to shared guide
│   │   │   ├── 07-instructions.oak.md      # [keep] Irreducible policy guidance
│   │   │   └── oak.ebnf                    # [keep] Same complete grammar
│   │   ├── assets/examples/               # [keep] All original literal teaching files
│   │   ├── _template/                     # [keep] Entry and empty scaffold directories
│   │   └── scripts/validate.py            # [modify] Source-derived skill version only
│   ├── oak.ebnf                           # [keep] No grammar change
│   └── definitions/                       # [keep] No core-model change
└── docs/
    ├── AGENTS.md                          # [modify] Adoption from 0016 and explicit reopen
    └── plans/0016-parallel-codex-exploration/
        ├── plan.md                        # [modify] Reconciled paths and evidenced status
        ├── report.md                      # [add] Actual results and publication handoff
        └── evidence/
            ├── native-clients-research.md # [keep] Superseded host design history
            ├── implementation-preflight.md # [keep] Superseded blocker history
            ├── d03-review.md              # [add] Preserved checkpoint-02 milestone review
            ├── d03-preservation.json      # [add] Preserved checkpoint-02 content evidence
            └── artifact-verification.json # [add] Final check, content and review evidence
```
Ownership: A03 identifies every source and generator. The `.agents` suffix names an OAK bundle directory, not the hidden source directory or an automatic Codex discovery path. No runtime Python is delivered in this new bundle; the existing optional authoring validator remains unchanged in responsibility. No existing product move/removal is required.
Verification: compare every added/modified/deleted path with this annotated view and the exact source-derived manifests; unchanged directory context hides no changed leaves. The final report and delivery changes.json record that reconciliation, not a new tree language. Repository-only fixtures may execute Python; native TOML and knowledge remain detached static artifacts. An annotated tree is not proof of completed implementation.

### State Comparisons

#### E13: A ready native leaf without host machinery
Authority: required
Current state:
No native TOML exists. The previous plan required an entry agent, scripts, MCP and installation before acceptance.
Desired state:
A01's single ready `oak-explorer.toml` embeds the full locally complete explorer OAK, with useful metadata and documented read-only/leaf defaults. Manual placement instructions identify `.codex/agents/`; no config fragment or launcher is needed.
Acceptance: parse TOML; compare decoded developer instructions byte-for-byte with the canonical worker; parse/resolve/round-trip that OAK; verify metadata, documented settings, literal preservation and no external instruction dependency. Reject stale/truncated/rewritten content and unknown required fields. Native installation and behavior are explicitly not tested.

#### E14: Preserve flat tool-backed parallel authoring
Authority: required
Current state:
The agreed composition exists only as a planning specimen. The runtime supports it already.
Desired state:
```python
explore_runtime_action = ACT.tool(
    "agent.explore-runtime",
    runtime_question,
    input=SCHEMA_EXPLORATION_REQUEST,
    output=SCHEMA_RUNTIME_REPORT,
    inputs=runtime_request_bindings,
    outputs=["RUNTIME_REPORT"],
)
explore_contracts_action = ACT.tool(
    "agent.explore-contracts",
    contracts_question,
    input=SCHEMA_EXPLORATION_REQUEST,
    output=SCHEMA_CONTRACT_REPORT,
    inputs=contracts_request_bindings,
    outputs=["CONTRACT_REPORT"],
)
parallel_exploration = Par(body=[explore_runtime_action, explore_contracts_action])
join_exploration = Join()
explore_repository_process = Process(
    id="explore-repository",
    name="Explore repository",
    input=SCHEMA_EXPLORATION_REQUEST,
    body=[parallel_exploration, join_exploration, synthesize_exploration_action, emit_exploration],
)
```
Acceptance: preserve this composition and its contracts while allowing canonical whitespace. Complete all definitions and fixture registrations. Execute with a bounded synchronization barrier to prove both calls enter before either is released, distinct outputs, immediate JOIN and synthesis only after successful validation. Test wrong revision, blocked/malformed/missing/extra results, output collisions and branch failure without success emission. This proves OAK fixture behavior, not live Codex execution.

#### E15: Shared knowledge without lost meaning
Authority: required
Current state:
Delegation guidance is brief; the standalone agent is 63,981 bytes against 64,000. APS has useful historical orchestration/adaptor ideas.
Desired state:
Both authoring forms receive A04's orchestration guidance and the identical maintained Codex knowledge. Existing grammar, core teaching, template and validator safeguards remain available without installation.
Acceptance: measure sizes, preserve all required content and independent specimen identities, verify constants/schema-only supporting scope and detached skill/standalone closure, and review any simplification against meaning rather than byte count alone. Do not raise limits or hide content outside the standalone agent.

#### E16: Copyable text/TOML bundle
Authority: required
Current state:
The new bundle is absent; earlier runtime files were never implemented.
Desired state:
Directory Changes defines the complete five-file `oak.agents` delivery: coordinator, explorer, sample, native TOML and shared adaptor. Native file content is standalone; scenario OAK has closed explicit dependencies.
Acceptance: exact source-derived path/byte manifests, cold generation, repair and repeat-generation equality; detached validation with no source/build lookup; rejection of missing/extra/stale/symlink/escaping paths. No scripts, transport, SDK dependency or hidden registry requirement in the native TOML.

#### E17: Directory Changes in the actual SMEAC schema
Authority: required
Current state:
The template has State Comparisons but no dedicated directory-change fields.
Desired state:
A05's actual template and canonical sibling contain the annotated current/planned trees and five new described placeholders. The current plan is a real adoption example; tests also show a move, removal, no-change and unknown-baseline case.
Acceptance: verify both OAK groupings, filled schema instances, prospective docs/examples policy and schema-derived positive/negative checks. Reject missing/duplicated/out-of-order/empty/unclosed/unfilled views for applicable plans. Preserve historical records and their existing checks. Review the diagram against the actual diff separately.

#### E18: Useful task and honest evidence contracts
Authority: required
Current state:
No live result exists, and the old plan cannot be satisfied without an external host.
Desired state:
Retain this exact request as sample knowledge, not a claim that it has run:
```text
Trace how a tool-backed ACT is authored, validated, resolved, and executed in OAK.
Identify its governing contracts, implementation owners, demonstrations, and
verification gaps. Cite the inspected files. Change nothing.
```
The worker requests complete applicable governing text and one identified revision, distinguishes inspected tests from executed tests, and reports coverage, gaps and blocked work. The native-parent usage asks two independent instances of the same leaf to investigate and then reconcile findings.
Acceptance: inspect the complete worker/sample against these meanings, validate all sample bindings, and use deterministic fixtures without fabricating live citations or runtime receipts. No successful report may be manufactured from blocked or invalid fixture inputs.

#### E19: Durable policy and unchanged boundaries
Authority: required
Current state:
The build owner closes the generated layout to four products; docs has no directory-view adoption rule.
Desired state:
Owning AGENTS documents explicitly allow the new text/TOML bundle and prospective directory schema, and route the maintained Codex knowledge. Root lifecycle and OAK core remain unchanged.
Acceptance: canonical scoped knowledge, router/ownership checks, unchanged root and APS files, no unsupported host assertions, and no unjustified model, syntax, dependency or workflow edits.

#### E20: Completed reviewed delivery
Authority: required
Current state:
The branch has planning/preflight history only.
Desired state:
All revised tasks are evidenced, source and generated files agree, complete available repository verification succeeds, a separate final review checks original intent and artifacts, and a non-draft review PR is raised without merging.
Acceptance: record exact tested source/environment, command results, generated sizes/identities, changed paths and review findings. Repository CI may provide the declared-dependency full checks when the local environment is limited; identify those results separately. Never describe artifact tests as live Codex proof or a pending/failed check as success.

## 3. Execution

Intent: Deliver the agent files the user actually needs, not a framework for running a host. Preserve the parallel OAK teaching, usable native explorer, shared sources and explicit tool/permission limitations. Use tests to demonstrate the narrowed intent rather than retain superseded gates or weaken unrelated safeguards.
Concept of operations: Commit this amendment first. Restore and inspect exact sources, apply durable ownership corrections, implement the worker/parallel example and generated native artifacts, then update the shared knowledge and actual planning schema. Verify deterministic behavior, artifact closure/freshness and the complete repository before the final review and authorized PR.

### Phase 1: Establish the revised artifact scope
Objective: Restore exact inputs and source owners without requiring a Codex host.
- [x] Key task: D01.01 Commit this amended plan before product implementation and retain the prior research/preflight as history.
- [x] Key task: D01.02 Restore the pinned governing texts, source/checkpoint identities, applicable Python standards and specialist knowledge; inspect affected source and generation/check paths.
- [x] Key task: D01.03 Record the durable artifact-only ownership and prospective tree policy in the owning AGENTS files; retain root lifecycle and limits.
Success criteria: E19 has explicit authority and owners, no removed host prerequisite remains, and the working source used for implementation is identified accurately.
Transition trigger: The revised scope and complete applicable knowledge are available for implementation.

### Phase 2: Implement the worker and parallel example
Objective: Express the investigation and independent work through current OAK contracts.
- [x] Key task: D02.01 Author the reusable worker with complete local schemas, receive/trigger/process identity, native ACT, evidence/gap/blocked meanings and emission.
- [x] Key task: D02.02 Complete E14's named flat coordinator, two mappings, immediate JOIN, post-join synthesis and output boundary.
- [x] Key task: D02.03 Supply repository-only deterministic worker/ToolContract fixtures, the exact sample request and native-parent usage; register canonical siblings and the scenario without displacing core teaching.
- [x] Key task: D02.04 Verify genuine synchronized fixture concurrency, input/revision identity, output isolation and rejection/failure behavior in both groupings.
Success criteria: E14 and E18 pass with complete usable artifacts and honestly labelled fixture evidence; no live result or native tool registration is invented.
Transition trigger: The scenario and its negative tests pass using the current OAK executor.

### Phase 3: Generate native artifacts and shared guidance
Objective: Deliver the standalone native leaf and shared knowledge without host scripts.
- [x] Key task: D03.01 Author the pure OAK Codex adaptor from the rechecked documented file/settings contract, including inheritance, manual placement and enforcement limitations.
- [x] Key task: D03.02 Implement the deterministic five-file bundle generator, metadata/settings ownership and lossless readable TOML serialization; preserve independent operational scopes.
- [x] Key task: D03.03 Add portable subagent-orchestration guidance and route it plus identical Codex knowledge through both authoring forms.
- [x] Key task: D03.04 Measure and review any size reduction before accepting generated authoring outputs; preserve required knowledge, teaching, template, grammar, validator identity and consent.
- [x] Key task: D03.05 Add exact native metadata/embedding, literal-escaping, no-host-files, detached closure, cold-generation, repair and stale/unsafe-path rejection checks.
Success criteria: E13, E15 and E16 pass; the native TOML contains no script/bridge dependency, both authoring forms share the new knowledge, and existing byte limits hold.
Transition trigger: Complete artifact generation and targeted rejection checks pass without Codex, MCP or model access.

### Phase 4: Implement reusable directory-change planning
Objective: Make the detailed tree a checked part of the real SMEAC format.
- [x] Key task: D04.01 Extend the SMEAC Python template and described placeholders, regenerate its canonical sibling and verify complete populated instances.
- [x] Key task: D04.02 Extend the existing plan checker from the schema with independent positive/negative specimens and the prospective adoption boundary; preserve all older checks.
- [x] Key task: D04.03 Reconcile this plan's annotated tree and owning guidance with actual implementation paths, including source-to-generated mapping.
Success criteria: E17 and E19 pass for both groupings, applicable plans and rejected malformed views; historical plans and APS remain unchanged.
Transition trigger: Schema, policy, examples and structural checks agree with the intended directory view.

### Phase 5: Verify the complete artifact change
Objective: Demonstrate source, delivery and repository consistency.
- [x] Key task: D05.01 Register all new checks through the existing verification entry points and update complete generated ownership/cold-repair checks.
- [ ] Key task: D05.02 Run compilation, affected generators, both complete repository check entry points and repeat generation; obtain identified CI results for declared-dependency verification where needed.
- [x] Key task: D05.03 Compare generated file/byte manifests, retained-content identities, byte sizes, canonical documents and actual changes with E13 through E19 and the annotated tree.
- [x] Key task: D05.04 Separately review the result against the user's original agent/parallelism intent and the explicit no-host amendment; correct findings and rerun affected checks.
Success criteria: E13 through E19 have substantive evidence, no required knowledge or safeguards were sacrificed, and repository verification contains no unresolved failure.
Transition trigger: The reviewed product and exact evidence are ready for delivery reporting.

### Phase 6: Deliver the finished review PR
Objective: Preserve a truthful completion record and raise the requested PR.
- [x] Key task: D06.01 Write report.md and artifact-verification.json with actual checked identities, outputs, task evidence, changed paths, limits, source-restoration limitations and final review verdict.
- [ ] Key task: D06.02 Commit the complete verified source/generated/documentation change without rewriting history; verify the remote file set and bytes.
- [ ] Key task: D06.03 Open and finalize the authorized review PR into main, check its verification results and report the native TOML path, with no merge or installed/live claim.
Success criteria: E20 passes and all 22 revised implementation tasks have evidence; withdrawn host tasks remain distinguishable from completed artifact work.
Transition trigger: The completed artifact-only change is ready for the user's review in its unmerged PR.

### Coordinating Instructions
- Timeline: complete authorized work in the current session as execution permits; retain a recoverable checkpoint for any genuine blocker.
- Boundaries: no host scripts, native installation, optional MCP dependency, live run, desktop automation, new workflow, core-language redesign or additional provider.
- Operating guidelines: preserve pinned governing knowledge and source identities; never interpret old host evidence as current authority or infer a passed live check from static files.
- Risk mitigation: native defaults and model instructions are not certified enforcement. Reject unsupported claims in artifacts and report all environment limitations honestly.

### Contingencies
- If a native setting cannot be supported by primary documentation, then omit the unsupported claim or use the documented contract; do not invent a field.
- If the complete authoring knowledge cannot fit the existing limits without loss, then retain the measured blocker rather than weakening a limit or dropping content.
- If a source file cannot be restored exactly, then identify that specific input and do not test against an undisclosed older implementation. Existing CI can verify the exact remote candidate; no temporary workflow may be introduced.
- If verification fails, then fix the approved implementation and rerun the affected checks before delivery.
- If the observed diff differs from the directory view, then reconcile the view and ownership rather than add files merely to match an obsolete diagram.

## 4. Admin and Logistics

| Resource | Quantity | Source | Status |
| --- | --- | --- | --- |
| Pinned repository knowledge and approved scope | One graph and plan | Existing branch and user amendment | AVAILABLE |
| Native TOML documentation | Two primary pages | Official OpenAI subagent/configuration references, rechecked 2026-09-07 | AVAILABLE |
| Exact repository source | Full bundle and verified final overlay | Controller inputs and complete file manifests | AVAILABLE |
| Final declared-dependency verification | Two complete entry points and freshness | Controller environment; cloud checks passed with noted package mismatch | PENDING |
| Generated agent bundle | Five text/TOML files | Source-owned build/agents.py | AVAILABLE |
| Shared authoring knowledge | Orchestration and Codex documents | Existing authoring generator and maintained adaptor | AVAILABLE |
| Directory-change schema | One SMEAC template and canonical sibling | Existing schema source and plan checker | AVAILABLE |

Supply: reuse existing dependencies and standard-library TOML parsing; add no runtime dependency or Codex/MCP requirement. Build verification remains separate from removed live-host provisioning.
Transportation: generate source-owned OAK and native TOML bytes, commit them to the existing branch, and expose the actual native file in the PR. Generation never installs files into a user's project or home.
Sustainment: retain one source for each knowledge concern, exact artifact tests, prospective tree guidance, and dated native configuration references. Future host compatibility is a separate task, not a hidden promise in this artifact delivery.
Rollback: corrections are new commits. The prior plan and preflight remain in history. No host configuration, credentials, model calls or deployed processes exist to roll back in this amended scope.

## 5. Command and Signal

1. The user owns scope, authorization and any later merge or runtime deployment decision.
2. The implementing assistant owns direct implementation, technical review and evidence; the authorized local controller supplies final declared-environment verification and Git/GitHub publication. No subagents are used.

| Channel | Medium | Purpose | Cadence |
| --- | --- | --- | --- |
| Conversation | Brief progress and result messages | Meaningful findings and final artifact/PR locations | During substantial work and at completion |
| This plan | Versioned Markdown | Approved scope and evidenced task status | At observed phase transitions |
| Report and evidence | Versioned files | Exact checks, limitations, retained meaning and review verdict | Before final delivery |

Reporting: distinguish inspected documentation, executed repository fixtures, verified artifact bytes, remote CI and unperformed native runtime behavior. No desktop or Codex runtime check is now required or claimed.

| Decision | Authority | Escalation |
| --- | --- | --- |
| Update this plan and implement artifact-only scope | User's 2026-09-07T03:57:06Z instruction | User only for a further material scope change |
| Raise the completed-work PR | Same instruction, retaining the earlier PR request | Do not merge |
| Add host code, dependencies, native installation or live execution | Not authorized in this narrowed task | Separate future request |
| Relax existing ownership, byte limits or other safeguards | Not authorized | Report measured conflict |

### Acknowledgement
The implementing assistant restores the pinned governing knowledge and records the scope change before product edits. The user's amendment authorizes this revised plan and immediate implementation through a PR; removed host prerequisites must not block artifact delivery or be misreported as passed.
