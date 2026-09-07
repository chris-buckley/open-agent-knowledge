# Add restricted parallel Codex exploration

Prepared: 2026-09-07T12:09:23+10:00
Classification: PUBLIC
Amendment: User-requested generated .agents packaging and reusable directory-change planning on 2026-09-07T02:29:23Z; supersedes the packaging proposal at commit `2301236fd78392f10900edb8b3c75be07aac27b0`.
Readiness: Ready for implementation approval, with explicit compatibility and delivery-size gates.
Execution: Not started. Every implementation task remains open.
Authorization: The user requested the original plan and now authorizes amending it for the generated .agents bundle and the SMEAC directory-change schema. Only planning-file changes are authorized in this turn. Product implementation, live Codex calls, installation, a pull request, and a merge still require their stated approvals.
Branch: `docs/plan-parallel-codex-exploration`
Baseline and governing revision: `9956e6998869fcfbd84067eec0d6303273a54174`
Plan location: `docs/plans/0016-parallel-codex-exploration/plan.md`
Restored checkpoint: plan-only commit `2301236fd78392f10900edb8b3c75be07aac27b0`; no implementation phases completed and no implementation authorization to carry forward.

## 1. Situation

### Operating Environment
OAK expresses portable knowledge and execution contracts; a host supplies models, tools, credentials, persistence, and effects. The proposed capability uses a real Codex interpreter to explore the OAK repository without changing it, with independent investigations dispatched through OAK's existing parallel tool actions.

### Current State
At the pinned baseline, `ACT.tool(...)` constructs an exact tool-backed action and renders as `ACT TOOL`; `Par` accepts independent exact tool actions with distinct output bindings, followed by `Join`. The existing delegation example dispatches `agent.reviewer` through `ToolContract`, but its worker uses deterministic fixture responses; the repository has no `.agents/adapters` directory. The authoring skill has brief delegation guidance, whereas the legacy APS snapshot contains dedicated subagent and platform-adapter material. There is no generated .agents bundle, and the SMEAC template has State Comparisons but no dedicated directory-change view.

### Challenges
- Enforcement: a prompt, declared allowlist, read-only hint, or custom-agent default does not establish the worker's effective capabilities. Codex child sessions can inherit parent runtime overrides, and tool hooks have documented coverage and failure limitations.
- Host integration: OAK expects a tool result with declared bindings, not a spawned thread identifier. The adapter must own Codex session startup, tool dispatch, completion, validation, deadlines, and cleanup.
- Parallel meaning: both workers must inspect the same immutable snapshot; their reports remain isolated until JOIN. Existing PAR failure semantics must not become silent partial success.
- Context: full applicable governing documents and explicit OAK dependencies must be available without flattening their scope or trusting automatic AGENTS discovery to avoid truncation.
- Evidence: schema-valid text is not proof of a read, a rejected operation, overlapping execution, or a correct interpretation. Host observations and semantic review must remain distinct.
- Delivery size: the baseline standalone authoring artifact is 63,981 bytes against a 64,000-byte limit. Adding guidance and adapter knowledge requires a measured, meaning-preserving fit, not an assumed exception.
- Packaging: a generated agent document is not a runnable Codex installation. Deliver the scenario graph, fixture runner, and shared adaptor together while keeping maintained sources and runtime dependencies explicit.
- Planning visibility: detailed trees must identify actual source/output changes and removals, not decorate an incomplete inventory or require rewriting historical plans.

### Supporting Factors
- Higher intent: make OAK useful on its own repository while demonstrating exact tool use, restricted agents, parallel execution, and explicit orchestration contracts.
- Adjacent efforts: preserve flat Python authoring, self-contained examples, locally understandable public contracts, shared skill/agent generation, and the existing repository lifecycle.
- Supporting resources: the sources and governing owners below, the existing executor and example catalogue, the APS snapshot as historical design reference, and current official Codex documentation.

### Assumptions
- Codex means a real Codex runtime through its app-server protocol, not merely a model name or a deterministic substitute. Model selection and authentication remain explicit host choices.
- A compatible, already installed Codex runtime and authorized model access can be supplied for implementation acceptance. Their availability has not been established in this planning session.
- The first supported invocation is the delivered launcher under `generated/oak.agents/adaptors/codex/`, starting isolated Codex sessions against an explicitly selected scenario and repository. Native parent-to-child spawning and installation into `.codex/agents` are not the enforcement mechanism for this delivery. The `.agents` suffix is an OAK delivery naming convention, not host auto-discovery or an archive format.
- The initial workload is a fixed pair of independent investigations, not an unbounded agent pool or dynamically recursive delegation.
- The existing OAK language is sufficient. Product implementation does not require a new statement, part, alias language, permission keyword, or scheduler.

### Constraints and Limitations
- Constraint: change only this plan during planning. Preserve main and all original commits; do not amend, squash, rebase, force-push, merge, or delete branches.
- Constraint: use `ACT.tool(...)`, `Par(body=[...])`, and `Join()` in Python and their current canonical OAK renders. Keep meaningful definitions flat and named before assembly.
- Constraint: work directly without research subagents. Later authorization may permit only the bounded Codex demonstration workers described here, not unrestricted delegation by the implementing assistant.
- Constraint: retain OAK's host boundary, local worker state/interface ownership, explicit graph composition, exact tool names, and current transaction semantics.
- Constraint: the explorer has no usable editing, command execution, package installation, general web/network, connector, or worker-spawning capability. Model-service/authentication traffic is a separate, explicitly authorized host connection.
- Constraint: preserve the 500-line AGENTS limit, 10,000-byte skill-entry limit, 64,000-byte standalone-agent limit, validator identity and consent safeguards, literal teaching content, and scope-safe fusion.
- Constraint: keep maintained repository-support sources in `.agents`, example sources in their scenario, and product deliveries in `generated`, including the newly authorized `generated/oak.agents/` layout. Update the build owner's generated-layout, generator-map, and output-map contracts explicitly; the old closed output set cannot be silently bypassed. Add no directory README indexes or provider-specific skill-frontmatter fields.
- Constraint: add the annotated Directory Changes subsection to the actual SMEAC schema, its canonical sibling, owning guidance, and verification during implementation, not only this plan. Keep the five SMEAC sections and compact phase format; do not retrofit inactive/completed historical records or broaden their existing format exemptions.
- Constraint: retain APS as unchanged historical reference. Do not import its input/format syntax, USE/CAPTURE conventions, tool aliases, external task-config formats, or dated platform claims into OAK.
- Limitation: repository sources were inspected through GitHub. A pinned archive download failed because the container could not resolve `codeload.github.com`; there is no executable checkout in this planning session. Full repository checks and live Codex execution have not run.
- Limitation: the capability and size gates below can block implementation acceptance. A blocker must be reported specifically; it must not be hidden by weakening the agreed restrictions or redefining completion.

### Governing Knowledge and Source Record

The complete root and applicable scoped knowledge at the pinned revision govern this plan. The original planning session checked main at that revision. This amendment restores the complete pinned text and verifies the existing planning branch/checkpoint; it does not substitute newer governing knowledge. Restoring the complete pinned texts takes priority after context loss. This is an authorized amendment to the restored planning checkpoint, not a continuation of an approved implementation. The expanded proposal requires approval at its new committed revision; the pinned governing revision is unchanged.

| Owner or source | Relevance |
| --- | --- |
| `AGENTS.md` | Product purpose, lifecycle, approval, host trust, naming routing, and scoped ownership. |
| `.agents/rules/context.oak.md` | Read-only preparation and specialist routing. |
| `.agents/rules/repository-change.oak.md` | Planning-change naming and immutable Git history. |
| `docs/AGENTS.md`; `examples/schemas/smeac_plan.py`; `examples/schemas/smeac_plan.oak.md` | Numbered plan storage, compact phases, comparison authority, and the source/meaning of the new Directory Changes schema fields. |
| `oak/AGENTS.md`; `oak/node/AGENTS.md`; `oak/execute/AGENTS.md` | Host separation, canonical meaning, dataflow, exact tools, and PAR/JOIN semantics. |
| `examples/AGENTS.md`; `build/AGENTS.md` | Example ownership, generated delivery, fusion, limits, and verification. |
| `oak/authoring.py`; `oak/node/parts/processes/statements.py` | ACT helper and current Par/Join model contracts. |
| `oak/execute/actions.py` | Exact dispatch, concurrent invocation, result validation, and group failure. |
| `examples/delegation/example.py`; `examples/delegation/example.oak.md` | Existing typed coordinator/worker dispatch and deterministic host. |
| `examples/catalog.oak.md` | Current demonstrations and their honest host disclosures. |
| `build/authoring.py`; `build/authoring_guides.py`; `build/checks/plans.py` | Shared generation, supporting-document restrictions, routing, and plan structure checks. |
| `build/examples.py`; `build/checks/__init__.py`; pinned build and generated path inventories | Existing check registration, generation ownership, and observed paths for the current/planned directory trees. |
| `legacy-snapshot-aps/SKILL.md`; `legacy-snapshot-aps/guides/subagent-architecture-v1.0.0.guide.md` | Historical skill routing and bounded coordinator/worker ideas. |
| `legacy-snapshot-aps/platforms/README.md`; `legacy-snapshot-aps/platforms/generic/adaptor.md`; `legacy-snapshot-aps/platforms/claude-code/adaptor.md` | Historical adapter separation, contracts, tool registries, and permission mappings. |

The original plan records these official Codex documentation references from 2026-09-07. They are retained design references, not proof of an installed runtime's behavior; this packaging amendment does not claim a fresh Codex compatibility audit:

| Source | Relevant observation and design consequence |
| --- | --- |
| [App-server protocol](https://developers.openai.com/codex/app-server/) | Provides request/notification lifecycles, structured turn output, interruption, and experimental dynamic tools. Use a version-checked stdio adapter rather than parsing terminal prose. |
| [Configuration reference](https://developers.openai.com/codex/config-reference/) | Distinguishes command tooling, MCP tool filters, feature controls, and project instruction limits. Do not treat an MCP allowlist as a global capability filter. |
| [Subagents](https://developers.openai.com/codex/subagents/) | Describes custom-agent configuration and inherited live parent overrides. Start independent restricted sessions rather than relying on a writable parent's worker defaults. |
| [Hooks](https://developers.openai.com/codex/hooks/) | Covers many local tools but excludes hosted paths and warns against treating hooks as complete enforcement. Hooks may add defense and observations, not replace the primary boundary. |
| [Agent approvals and security](https://developers.openai.com/codex/agent-approvals-security) | Command sandbox/network policy does not govern all hosted capabilities. Disable or separately constrain every reachable surface. |

## 2. Mission

After explicit implementation approval, the implementing agent delivers and verifies a generated OAK agent bundle with a restricted Codex explorer, parallel coordinator, shared adaptor, reusable authoring guidance, and directory-change planning schema, so the capability works on OAK itself and its ownership is visible.

Task: complete every approved phase in this branch before reporting implementation complete; create an implementation PR only when separately authorized.
Purpose: demonstrate portable OAK meaning driving a real host without confusing instructions, configuration, tool visibility, permission enforcement, and observed behavior.
End state: `generated/oak.agents/` contains a self-contained scenario graph and fixture demonstration beside a shared `adaptors/codex/` directory. One explorer definition serves two concurrent Codex sessions; joined reports yield source-backed synthesis without repository changes. The generated skill and standalone authoring agent teach the same contracts, and the actual SMEAC schema makes annotated current/planned directory trees reusable in future plans.

### Architecture Decisions

#### A01: An OAK worker and an executable Codex adapter are different artifacts

The explorer is a typed OAK document. Its receive interface and entry process share its own local request schema; its native investigation ACT has an explicit output contract and emits a complete local result. The coordinator is another OAK document with locally explained dispatch and result contracts. Neither document embeds credentials, CLI configuration dialects, or provider-specific language semantics.

The host adapter starts the worker's OAK execution and supplies a Codex-backed native interpreter. That interpreter receives the OAK invocation and its resolved document context, exposes the restricted read tools, and returns structured values for OAK validation. The host collects the worker's emission, validates it, and explicitly maps it to the coordinator's declared result binding. This exercises the existing executor rather than treating OAK as a decorative prompt around an unrelated Python workflow.

#### A02: Use app-server over stdio, with isolated sessions

Use the installed `codex app-server` stdio interface, one isolated process/session per concurrently active worker. Initialize the protocol, verify required capabilities, inspect effective configuration, create an ephemeral thread, start the turn with an output schema, service only registered read-tool requests, and await a successful terminal turn before returning. Record the actual binary version, protocol-schema fingerprint, selected model, and effective profile with each run.

App-server is chosen because this task needs client-owned dynamic tool handling, lifecycle events, and bounded interruption. A simple `codex exec` or SDK wrapper is smaller for ordinary jobs but does not by itself establish this plan's complete enforcement and event contract. Do not add both transports, fall back to an inherited native subagent, fork Codex, or build a general host framework in this change. Experimental protocol use is explicit and guarded by compatibility checks, not described as a stable universal API.

The adapter fails before launching model work when the installed build cannot establish the declared capability restrictions. A current-documentation citation or a configuration file that parses is not enough. Unknown configuration fields, unsupported tool suppression, inherited capabilities, or incomplete policy inspection fail the compatibility gate; they do not authorize weaker operation.

#### A03: Use one explorer definition and explicit branch result mappings

Retain the proposed exact OAK tool registrations `agent.explore-runtime` and `agent.explore-contracts`. Both use one implementation and the same worker document; their small dispatch wrappers supply the branch assignment and map the validated worker result to `RUNTIME_REPORT` or `CONTRACT_REPORT` respectively. These are real entries in the supplied OAK registry, not guessed Codex built-ins or a new OAK alias mechanism.

The request includes a host-issued request identity, question, allowed relative paths, immutable snapshot identity, and governing-knowledge identity. Each worker result explains the inspected revision, findings, file-and-line evidence, actual read coverage, and unresolved questions. Host receipts carry tool observations, effective permissions, timestamps, and session identities separately from model-authored findings.

Use ordinary current OAK schemas for public top-level bindings. Any additional nested JSON validation needed for report items or transport payloads is explicitly host-owned, with a documented mapping and rejection tests; it is not claimed as a new OAK schema feature. Branch wrappers validate before mapping. The synthesis contract rejects mismatched snapshots and cannot treat a worker's self-reported read or permission assertion as host evidence.

#### A04: Restricted capabilities are enforced at the boundary

Expose only these proposed dynamic read operations, with exact runtime names recorded in the adapter's supplied registry:

| Operation | Permitted behavior | Required restrictions |
| --- | --- | --- |
| `repository_list` | List approved snapshot entries. | Relative paths, deterministic pagination, bounded result counts, no host filesystem enumeration. |
| `repository_read` | Read a bounded line range from an approved text blob. | Reject traversal, absolute paths, symlinks, binary files, secrets, and paths outside the authorized manifest; return blob identity and line range. |
| `repository_search` | Search approved text blobs. | Literal search initially, bounded scope, results, and bytes; never pass a model string to a shell. |
| `repository_revision` | Describe the pinned snapshot and its manifest. | Host-computed immutable identity; no write or ref-moving operations. |
| `repository_diff` | Read a bounded diff against an explicitly permitted base. | No arbitrary Git arguments, external diff, textconv, hooks, network, or model-controlled command execution. |

The model cannot select a workspace root, widen a read set, replace the profile, add tools, supply credentials, or approve an escalation. Disable shell/unified execution, editing, nested delegation, hosted search, apps/connectors, browser/computer use, automatic skill/plugin activation, MCP servers, and dependency installation unless the precise surface is one of the owned read operations. Use an isolated configuration/home and neutral working directory outside the inspected checkout, deny approval and permission expansion, and do not inherit user or project config that silently enables capabilities. Supply pinned governing knowledge explicitly rather than allowing ancestor-directory discovery to add or truncate it. Retain an appropriate read-only sandbox as defense in depth. Custom hooks, when used, are not the only defense against a callable prohibited surface.

A declared-but-denied built-in is not described as absent. The effective capability record distinguishes advertised, callable, denied, and unsupported surfaces. No prohibited effect may succeed even when requested directly. If a reachable path cannot be controlled before execution in the supported build, strict mode is unsupported and the launcher refuses it. Post-hoc logs and unchanged bytes are detection evidence, not substitutes for prevention.

The host needs authorized model-service traffic and may write its own bounded audit files outside the repository. The explorer does not receive those transport credentials or writable audit paths. Read-only does not mean no billing, no host bookkeeping, or universal protection against a compromised operating system.

#### A05: Pin repository content and governing knowledge independently

At launch, the host selects a Git commit and builds a read-only manifest-backed snapshot outside the developer's working tree, with content identities computed from real bytes. Both branches receive the identical snapshot. Default to committed content; refuse silently mixing uncommitted changes, and report their exclusion when the source checkout is dirty. An explicit future working-tree snapshot mode is not part of this delivery.

Load the complete root and applicable scoped AGENTS text before inspection in each scope, with full coverage records. Use whole resolved OAK documents and explicit dependencies; do not transplant scoped instructions into a new owner or rely on a prose summary. The exploration path set includes the transitive governing documents it needs. The adapter must refuse missing, truncated, or policy-incompatible context; bounded investigation results may be paged but governing knowledge may not be silently clipped.

Do not execute repository instructions to install tools, change configuration, or broaden worker authority. Retrieved code, fixtures, and quoted instructions remain inspected data. Governing AGENTS policy is scoped knowledge, not host permission. Normal worker-context compaction is not permission to forget the pinned knowledge; restoration must retain its identity and complete content, or the run ends as blocked.

Record live-checkout identities before and after the run separately from the immutable snapshot. External concurrent changes do not rewrite the snapshot or automatically become the explorer's fault, but they prevent an unqualified claim that the live checkout remained unchanged.

#### A06: Existing PAR/JOIN semantics own the orchestration

The coordinator uses `Par(body=[explore_runtime_action, explore_contracts_action])`, an immediately following `Join()`, then one native synthesis ACT and a local emission. Inputs are complete before dispatch; branches read no sibling outputs; each produces a unique binding. PAR launches the exact tools concurrently and JOIN establishes when their validated results are usable by subsequent work.

Retain current all-or-fail behavior. If a branch fails, times out, returns malformed data, or violates scope, the group does not promote a partial result or emit a successful synthesis. Diagnostic receipts may be retained by the host. OAK currently waits for the group rather than promising fail-fast sibling cancellation; impose a deadline inside each adapter call, interrupt overdue Codex turns, terminate and reap their processes, and bound cleanup. Do not change executor failure semantics or claim rollback of external model calls and cost.

Use two workers as the initial concurrency ceiling and no worker recursion. A synthesis Codex session has no repository tools and receives only the joined reports and their host receipts. It reconciles conflicting evidence, distinguishes gaps from defects, and produces one user-facing answer; agreeing worker prose is not independent proof.

#### A07: Re-imagine APS adapter knowledge in OAK

| Useful APS idea | OAK treatment |
| --- | --- |
| A platform adapter separate from the standard. | A pure OAK adapter knowledge document plus a small executable host binding; no core-language changes. |
| Coordinator as dispatch owner; bounded leaf workers. | Explicit `ACT.tool`, worker schemas/interfaces, isolated host sessions, and no recursive worker tool. |
| Public request and response mappings. | Complete local schemas, validated arrivals/emissions, ToolContract checks, and one explicit mapping per dispatch boundary. |
| Tool registries and platform capability facts. | Exact supplied registry entries, dated source evidence, effective-profile observations, and failure when unsupported. |
| Parallel review and sequential handoffs. | Existing PAR/JOIN for independent tool calls; CALL for local process composition; host invocation stays distinct from both. |
| Adapter templates and installation conventions. | Teach verified Codex mappings without installing a less-restricted native agent or scaffolding unrelated project configuration. |

Do not copy APS platform tables as present-day truth. Do not add `predefinedTools.json`, `config.json` aliases, USE/CAPTURE syntax, or generic fallback execution. The required guide explains native ACT versus exact tools, request/result ownership, independent task splitting, full scoped context, least privilege, concurrency bounds, JOIN, conflict reconciliation, failure, cleanup, evidence, and permission inheritance.

#### A08: Deliver an oak.agents bundle from one set of maintained sources

Use `generated/oak.agents/` alongside `generated/oak-authoring.skill/`. The bundle contains scenario directories directly, initially `parallel_exploration/`, and a separate shared `adaptors/codex/` directory. Do not insert another examples directory or create empty future scenarios/providers. The suffix identifies a directory of generated OAK agent deliveries; it is not the repository's hidden `.agents/` source directory, a new OAK part, an archive, or an automatically installed Codex agent.

| Path or owner | Planned responsibility |
| --- | --- |
| `examples/parallel_exploration/example.py` and sibling `example.oak.md` | Flat coordinator source and canonical repository render, including both tool-backed branches, JOIN, and synthesis. |
| `examples/parallel_exploration/explorer.py` and sibling `explorer.oak.md` | One reusable typed leaf worker; no separately maintained Codex prompt copy. |
| `examples/parallel_exploration/sample.oak.md`; `run.py` | Source-derived complete sample request/data and detached deterministic fixture demonstration. The fixture runner accepts an explicit entry path and never defaults to live model work. |
| `examples/catalog.py`; `examples/catalog.oak.md` | Register the scenario, owned sample generator, local dependency closure, regeneration, and source-directory fixture command without displacing the four-stage teaching core. |
| `.agents/adaptors/codex/adaptor.oak.md` | Maintained pure OAK Codex contract, capability policy, dated version evidence, invocation meaning, and unsupported cases; constants/schemas only where shared with authoring fusion. |
| `.agents/adaptors/codex/run.py`, `transport.py`, `tools.py`, `contracts.py` | Maintained host implementation for explicit launch/preflight, bounded stdio lifecycle, manifest-backed reads, and validated mappings. These sources also produce the executable generated adaptor; no runtime-only implementation is hidden in the source checkout. |
| `build/agents.py` | Generate the complete `oak.agents` bundle from the registered example sources and maintained adaptor files through the existing generated-file primitives. Own its complete file set, entry mapping, byte freshness, and narrow cleanup. Never use delivered scripts as build source. |
| `generated/oak.agents/parallel_exploration/coordinator.oak.md`, `explorer.oak.md`, `sample.oak.md`, `run.py` | Copyable scenario containing its complete OAK document graph, required sample data, and offline fixture runner. Explicitly map the source entry `example.oak.md` to delivered `coordinator.oak.md`; keep worker scope separate. |
| `generated/oak.agents/adaptors/codex/adaptor.oak.md`, `run.py`, `transport.py`, `tools.py`, `contracts.py` | Generated, usable Codex adaptor and exact executable helper deliveries. The launcher accepts explicit scenario, repository, commit, and external audit paths. It does not load agent documents or implementation code from `.agents`, `examples`, or `build`. |
| `build/authoring_guides.py`; `build/authoring_platforms.py` | Compose portable orchestration and transform the maintained Codex knowledge into shared authoring material without a second policy source. |
| `build/authoring.py` | Register the new shared authoring documents and regenerate both forms. Preserve existing scope-safe fusion; a generic fusion rewrite is not presumed. |
| `generated/oak-authoring.skill/guides/subagent-orchestration.oak.md`; `platforms/codex/adaptor.oak.md` beneath that skill | Generated authoring guidance and Codex knowledge from their owners. The skill's platforms path is a teaching projection, not a second executable adaptor directory. |
| `generated/oak-authoring.oak.md` | Contains the same authoring knowledge through existing fusion. Operational coordinator/worker documents and host scripts are not fused into this authoring agent. |
| `examples/schemas/smeac_plan.py` and sibling `.oak.md`; `docs/AGENTS.md` | Source and canonical delivery of the A09 Directory Changes subsection; durable prospective plan-authoring policy. |
| `build/checks/codex_adapter.py`; `build/checks/agent_deliveries.py` | Protocol, permissions, lifecycle, parallelism, copied-bundle usability, cold generation, exact file/byte closure, and rejection checks. Keep the existing AGENTS-policy checker distinct. |
| `build/checks/plans.py`; `build/checks/outputs.py`; `build/checks/__init__.py`; existing authoring/example checks | Schema-derived planning checks, expanded generated ownership, and registration through the existing `build/examples.py` entry points. |
| `build/AGENTS.md`; `examples/AGENTS.md`; `.agents/rules/context.oak.md` | Explicit generated output/source ownership, scenario and tree-authoring rules, and routing to maintained Codex knowledge. Keep root AGENTS and its lifecycle unchanged. |
| This plan; later `report.md` and `evidence/` | Amended scope, expected/observed directory views, checkpoints, acceptance receipts, source identities, and final review. |

Define self-containment honestly at two levels. Each scenario contains its complete OAK graph and offline fixture demonstration, with no dependency on another scenario. The whole `oak.agents` bundle additionally contains the shared executable Codex adaptor needed for live use. Installed OAK/dependencies, compatible Codex, authorized model access, and the repository explicitly selected for inspection remain external runtime inputs; they are not vendored or silently installed. Copying only a scenario does not include the live adaptor. Copying the whole bundle must require no maintained source checkout.

The maintained fixture runner uses delivered `coordinator.oak.md` as its default entry; the source-scenario command supplies `--entry example.oak.md`. Use explicit entry/typed-target relocation when necessary, not replacement of arbitrary script text, instructions, tool names, or literal payloads. Generated adaptor scripts are exact deliveries from their maintained files and accept explicit paths rather than deriving a development repository from their own location. All real use and acceptance operate on generated deliveries, not a privileged source-only launcher.

Use the same Codex knowledge source for the runtime bundle and the skill projection; verify equality or a documented, lossless projection before fusion. This intentional generated duplication does not create a second policy owner. Keep coordinator and worker operational documents separate; bundling is not fusion. Do not produce the earlier conversational `generated/oak-exploration/` layout or install `.codex/agents` files. The earlier `.agents/adapters/codex/` spelling was an unimplemented proposal, not an existing directory to move; maintained and executable delivery directories now use `adaptors/codex/`.

Extend `build/AGENTS.md`'s closed generated-layout, generator-map, and output-map explicitly for the new bundle, then update output validation, cold generation, and repair checks. Retain the existing four products and make each generator prune only its owned subtree. Do not edit generated files by hand, broaden cleanup across unrelated outputs, or add another publishing workflow. Record source-to-delivery bytes and reject missing, extra, stale, escaping, symlinked, or source-checkout-dependent deliveries.

The authoring size gate remains mandatory before broad product work: inventory candidate bytes and remove only demonstrated redundant representation or repeated explanatory prose through the correct owner. Do not strip examples, externalize required standalone knowledge into the new agent bundle, encode it opaquely, raise a limit, or hide an unrelated validator rewrite. If a readable complete candidate cannot fit, stop for a specific scope decision.

#### A09: Make annotated directory changes part of the SMEAC schema

Extend the existing schema's Mission section with `### Directory Changes`, after End state and before State Comparisons. This is an ordinary presentation subsection of the current SMEAC schema, not a sixth top-level section or a new OAK/configuration language. Add ordinary string placeholders and explanatory WHERE clauses for `DIRECTORY_BASELINE`, `DIRECTORY_CURRENT`, `DIRECTORY_PLANNED`, `DIRECTORY_OWNERSHIP`, and `DIRECTORY_VERIFICATION`. Current and planned views use separate fenced text blocks; a fixed explanatory legend defines change annotations. Keep the existing comparison authority and phase contracts intact.

The tree should expose the affected file hierarchy with useful inline purpose notes, not only broad directory names. Include maintained source, generated deliveries, examples, adaptors, documentation, and verification owners. Show actual observed current paths separately from future paths; state explicitly when a proposed artifact is absent. Distinguish `[add]`, `[modify]`, `[move from <path>]`, `[remove]`, `[keep]`, and `[check]` (an existing path inspected/regenerated that might remain byte-identical). Use indentation and optional tree branches with aligned `#` purpose notes. Moves name both old and new paths, removals remain visible as tombstones, and generated files identify their owner. Collapse only unrelated unchanged paths; no ellipsis may hide an affected file or a required dependency.

`docs/AGENTS.md` owns use of the subsection in new plans and explicitly reopened/updated plans going forward; `examples/AGENTS.md` owns the presentation guidance alongside its other schema-authoring conventions. Require a populated view for repository file changes. A plan with genuinely no file changes retains the subsection with the explicit sentence `No directory or file changes.` and a reason instead of inventing a tree. Do not retrofit inactive/completed historical records. Enforce the new required subsection for plan 0016 and subsequently allocated plan IDs; this feature-specific adoption boundary does not exempt older plans from their existing SMEAC, comparison, storage, or navigation checks. Any explicitly reopened older plan adopts the current policy when its scope is updated.

Derive structural expectations from the canonical schema in `build/checks/plans.py`: placement, field labels, populated fenced views, and absence of unresolved schema markers. Test added/modified paths, explicit move/removal annotations, a no-file-change case, unknown/missing baselines disclosed honestly, and rejection of malformed or missing required views. Preserve fixed independent specimens so changing the template cannot redefine the intended layout. Do not build a new tree parser, path DSL, task manifest, or general diff engine. Structural validity does not prove the tree matches reality: final review separately compares it with the observed Git diff, owned generated path/byte manifests, and the source/output map. Resolve omissions and unsupported ownership claims before completion.

### Directory Changes

Baseline: product/source revision `9956e6998869fcfbd84067eec0d6303273a54174`, plus the already committed plan at `2301236fd78392f10900edb8b3c75be07aac27b0`. This is an affected-scope view, not an exhaustive repository inventory. The unimplemented prior proposals are not current files. Only this plan changes in the present amendment; all product paths below remain intended implementation outcomes.
Legend: `[add]` new; `[modify]` existing content changes; `[move from PATH]` relocation; `[remove]` deleted path shown as a tombstone; `[keep]` relevant unchanged context; `[check]` inspect/regenerate and change only if required. No moves or removals of existing product files are planned here.
Current:
```text
open-agent-knowledge/
├── .agents/
│   └── rules/
│       └── context.oak.md                # Current specialist/context routing
├── examples/
│   ├── AGENTS.md                        # Current example and schema conventions
│   ├── catalog.py                       # Source scenario registration
│   ├── catalog.oak.md                   # Generated scenario/schema catalogue
│   ├── delegation/                     # Existing deterministic delegation fixture
│   │   ├── example.py                  # ACT.tool("agent.reviewer", ...)
│   │   └── example.oak.md              # Existing coordinator render
│   └── schemas/
│       ├── smeac_plan.py               # Current schema source; no Directory Changes
│       └── smeac_plan.oak.md           # Current canonical schema delivery
├── build/
│   ├── AGENTS.md                       # Current four-product output ownership
│   ├── authoring.py                    # Existing skill and standalone generation
│   ├── authoring_guides.py             # Existing shared authoring knowledge
│   ├── authoring_validator.py          # Optional immutable validator source
│   ├── generated.py                   # Shared safe generation primitives
│   ├── fusion.py                      # Existing scope-safe assembly
│   ├── examples.py                    # Both established verification entry points
│   └── checks/
│       ├── __init__.py                 # Ordered check registration
│       ├── authoring.py                # Authoring parity, limits, and closure
│       ├── human_examples.py           # Catalogue-driven scenario checks
│       ├── architecture.py             # Existing scoped ownership checks
│       ├── outputs.py                  # Current generated-set/freshness checks
│       └── plans.py                    # Existing SMEAC/comparison validation
├── generated/
│   ├── oak.ebnf                        # Current grammar reference
│   ├── definitions/                    # Current generated construct definitions
│   ├── oak-authoring.oak.md             # Current standalone authoring agent
│   └── oak-authoring.skill/             # Current modular authoring delivery
│       ├── SKILL.md                    # Current routing
│       ├── references/                 # Existing language knowledge
│       ├── guides/                     # Existing shared authoring guides
│       │   ├── authoring.oak.md         # Authoring practice and template knowledge
│       │   ├── review.oak.md            # Review criteria and literal teaching
│       │   └── validation.oak.md        # Optional validation and identity policy
│       ├── assets/examples/            # Existing four-stage teaching core
│       ├── _template/                  # Existing inert skill scaffold
│       └── scripts/validate.py         # Optional generated validator
└── docs/
    ├── AGENTS.md                       # Current plan-storage/authoring policy
    └── plans/0016-parallel-codex-exploration/
        └── plan.md                     # Existing plan-only checkpoint
```
Planned:
```text
open-agent-knowledge/
├── .agents/
│   ├── rules/
│   │   └── context.oak.md                       # [modify] Route Codex source knowledge
│   └── adaptors/                               # [add] Maintained host-support sources
│       └── codex/
│           ├── adaptor.oak.md                  # [add] Sole Codex knowledge/policy owner
│           ├── run.py                          # [add] Delivery-safe launcher/preflight
│           ├── transport.py                    # [add] Bounded app-server lifecycle
│           ├── tools.py                        # [add] Manifest-backed read capabilities
│           └── contracts.py                    # [add] Protocol/request/result mappings
├── examples/
│   ├── AGENTS.md                               # [modify] Bundle/tree authoring guidance
│   ├── catalog.py                              # [modify] Register scenario and samples
│   ├── catalog.oak.md                          # [modify] Regenerated catalogue/disclosures
│   ├── parallel_exploration/                   # [add] Maintained flat example authoring
│   │   ├── example.py                          # [add] Coordinator, ACT.tool, Par, Join
│   │   ├── example.oak.md                      # [add] Canonical source-scenario entry
│   │   ├── explorer.py                         # [add] One reusable worker source
│   │   ├── explorer.oak.md                     # [add] Canonical worker document
│   │   ├── sample.oak.md                       # [add] Source-derived request/sample data
│   │   └── run.py                              # [add] Offline fixture; explicit entry path
│   └── schemas/
│       ├── smeac_plan.py                       # [modify] Directory Changes fields/meaning
│       └── smeac_plan.oak.md                   # [modify] Regenerate from schema source
├── build/
│   ├── AGENTS.md                               # [modify] Bundle/schema/check ownership
│   ├── agents.py                               # [add] Generate complete oak.agents bundle
│   ├── authoring_platforms.py                  # [add] Codex knowledge teaching projection
│   ├── authoring_guides.py                     # [modify] Orchestration knowledge/routing
│   ├── authoring.py                            # [modify] Shared skill/standalone delivery
│   ├── authoring_validator.py                  # [check] Version/fingerprints if affected
│   ├── generated.py                            # [keep] Reuse safe generation primitives
│   ├── fusion.py                               # [check] Preserve existing scope-safe fusion
│   ├── examples.py                             # [keep] Existing verification entry points
│   └── checks/
│       ├── __init__.py                         # [modify] Register new offline checks
│       ├── codex_adapter.py                    # [add] Restrictions/protocol/concurrency
│       ├── agent_deliveries.py                 # [add] Bundle freshness and detached use
│       ├── authoring.py                        # [modify] New knowledge/parity/file-set checks
│       ├── human_examples.py                   # [check] Existing scenario closure checks
│       ├── outputs.py                          # [modify] Expand exact owned output set
│       ├── plans.py                            # [modify] Schema-derived tree checks
│       └── architecture.py                     # [check] Preserve scoped ownership checks
├── generated/
│   ├── oak.ebnf                                # [keep] No OAK grammar change
│   ├── definitions/                            # [keep] No core-model change
│   ├── oak.agents/                             # [add] Copyable agent capability bundle
│   │   ├── parallel_exploration/               # [add] Self-contained graph/fixture scenario
│   │   │   ├── coordinator.oak.md              # [add] From example.py; explicit entry map
│   │   │   ├── explorer.oak.md                 # [add] From explorer.py; separate scope
│   │   │   ├── sample.oak.md                   # [add] Complete generated sample data
│   │   │   └── run.py                          # [add] Generated offline fixture runner
│   │   └── adaptors/                           # [add] Shared live-host implementations
│   │       └── codex/
│   │           ├── adaptor.oak.md              # [add] From maintained Codex knowledge
│   │           ├── run.py                      # [add] Generated live launcher/preflight
│   │           ├── transport.py                # [add] Generated protocol implementation
│   │           ├── tools.py                    # [add] Generated restricted read tools
│   │           └── contracts.py                # [add] Generated boundary validation
│   ├── oak-authoring.oak.md                     # [modify] Same new authoring knowledge
│   └── oak-authoring.skill/
│       ├── SKILL.md                            # [modify] Route orchestration/Codex guidance
│       ├── guides/
│       │   ├── subagent-orchestration.oak.md    # [add] Portable coordinator/worker guidance
│       │   ├── authoring.oak.md                # [check] Existing authored guidance
│       │   ├── review.oak.md                   # [check] Retain required literal teaching
│       │   └── validation.oak.md               # [check] Identity only when affected
│       ├── platforms/codex/
│       │   └── adaptor.oak.md                  # [add] Same Codex knowledge, teaching form
│       ├── references/                         # [keep] Existing language references
│       ├── assets/examples/                    # [keep] Retain four-stage teaching core
│       ├── _template/                          # [keep] Retain inert skill scaffold
│       └── scripts/validate.py                 # [check] Exact source-derived validator
└── docs/
    ├── AGENTS.md                               # [modify] Require annotated future plan trees
    └── plans/0016-parallel-codex-exploration/
        ├── plan.md                             # [modify] This amendment; later task evidence
        ├── report.md                           # [add later] Actual results and observed tree
        └── evidence/                           # [add later] Only actual supporting records
```
Ownership: `.agents/adaptors/codex/` owns maintained host implementation, not hand-edited outputs. Example Python sources own scenario documents and sample data; `build/agents.py` owns the generated bundle. `build/authoring_guides.py` and `build/authoring_platforms.py` own teaching composition from those sources. `examples/schemas/smeac_plan.py` owns the schema shape, while docs and examples AGENTS own prospective use and presentation. A08 lists the complete ownership mappings. No extra runnable OAK scopes are fused together.
Verification: compare current entries with the pinned source inventory, then compare the implemented change set and generated manifests with this planned view. Expand any newly identified affected leaves before acceptance and reconcile conditional `[check]` paths without forcing gratuitous edits. Evidence filenames are intentionally not invented before their observations exist; enumerate the actual files in the completion report. The expected tree is required by E09/E10 and is not a claim that products already exist.

### State Comparisons

#### E01: Real worker behind the existing tool API
Authority: required
Current state:
The delegation example uses the following existing Python construction and a deterministic `_reviewer_agent` host. It does not start Codex.
```python
agent_reviewer_action = ACT.tool(
    TOOL_AGENT_REVIEWER,
    agent_reviewer_text,
    input=SCHEMA_WORKER_REQUEST,
    output=SCHEMA_WORKER_RESULT,
    inputs=local_bindings(REQUEST_PLACEHOLDERS),
    outputs=list(RESULT_PLACEHOLDERS),
)
```
Desired state:
The new registry entries invoke the one explorer OAK document through the Codex native interpreter described in A01 and A02. A validated worker emission, not a session identifier or canned finding, reaches the coordinator. The old fixture remains honestly labelled and is not rewritten as evidence of live behavior.
Acceptance: trace one actual invocation from ACT.tool through ToolContract, worker arrival/process, Codex investigation, output validation, and mapped worker emission. Runtime values and model wording may vary; the ownership and validation sequence must match. Offline tests and live evidence are reported separately.

#### E02: Flat Python construction and real parallel execution
Authority: required
Current state:
`Par` and `Join` already exist, but the proposed Codex pair and its joined synthesis are absent. The agreed conversation sketch omitted request binding and adapter definitions; it was illustrative, not runnable delivery.
Desired state:
Retain this composition, completing the separately defined schemas, bindings, actions, interface, and host registrations in the implementation:
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

parallel_exploration = Par(
    body=[explore_runtime_action, explore_contracts_action],
)
join_exploration = Join()

explore_repository_process = Process(
    id="explore-repository",
    name="Explore repository",
    input=SCHEMA_EXPLORATION_REQUEST,
    body=[
        parallel_exploration,
        join_exploration,
        synthesize_exploration_action,
        emit_exploration,
    ],
)
```
Acceptance: preserve ACT.tool, named flat composition, distinct output names, explicit complete request bindings, immediate JOIN, and post-JOIN synthesis. The complete example must parse, resolve, round-trip in both groupings, and run. A barrier-based offline test proves both calls are launched before either is released; live host intervals prove overlapping Codex work. Launching twice sequentially or returning early thread handles fails.

#### E03: Enforced read-only capabilities
Authority: required
Current state:
No repository Codex adapter implements or evidences an effective read-only tool profile. Codex custom-agent configuration and OAK prose alone do not establish it.
Desired state:
The A04 read registry is the only usable investigation capability. Prohibited calls are refused before effects, unknown profiles refuse startup, and no worker can widen its own scope. Host transport/audit activity is disclosed separately.
Acceptance: directly exercise valid reads and denied writes, shell execution, installation, network/search, connector use, nested spawning, traversal, symlink escape, arbitrary Git flags, and permission expansion. Include missing/failed hooks and unexpected inherited configuration; enforcement cannot depend on a cooperative model. Record exact supported runtime/profile and negative-test receipts, with no claim of universal sandbox proof.

#### E04: Reusable orchestration and Codex adapter knowledge
Authority: required
Current state:
OAK's process guide briefly mentions delegated documents and independent exact tool actions. APS has a fuller orchestration guide and platform adapters written in APS's own historical syntax.
Desired state:
Generate the OAK orchestration guide and Codex adapter knowledge at A08's paths. Explain coordinator/worker boundaries, both mappings, scoped context, restrictions, PAR/JOIN, failure, and evidence. Teach Codex configuration as host-specific data, never OAK permission syntax.
Acceptance: review every retained APS idea against A07, cite current Codex primary sources, validate the OAK documents, and prove skill/standalone knowledge parity. Unsupported platform claims and operational supporting documents must be rejected. No APS files change.

#### E05: Shared delivery without weakened limits
Authority: required
Current state:
The generated authoring agent is 63,981 bytes; its existing bound is 64,000 bytes. Existing core scenarios, grammar, validator source, template, and knowledge participate in delivery and fusion checks.
Desired state:
The new guidance fits both existing limits while preserving required existing knowledge, literal teaching, validator trust/consent, and all current generated products. The additional .agents bundle has its own complete path/byte checks; separating operational agents is not a way to externalize required standalone authoring knowledge. New code remains outside OAK core and the no-install authoring path.
Acceptance: produce a byte inventory and semantic before/after review at the size gate. Run exact fresh-byte/path checks, detached skill and standalone closure, rejected operational-fusion cases, and second-generation no-diff checks. A raised limit, opaque encoding, omitted teaching, external dependency for formerly standalone knowledge, or a skipped gate fails.

#### E06: Useful evidence on the actual OAK repository
Authority: required
Current state:
No live Codex-backed answer to the agreed ACT investigation has been observed in this work. Existing demonstrations disclose their deterministic hosts.
Desired state:
Execute this exact user-facing task against an identified OAK snapshot:
```text
Trace how a tool-backed ACT is authored, validated, resolved, and executed in OAK.
Identify its governing contracts, implementation owners, demonstrations, and
verification gaps. Cite the inspected files. Change nothing.
```
Split execution/dataflow from contract/verification investigation. Join the two reports and return one explanation with revision-bound path/line citations, actual coverage, unresolved questions, and any disagreement.
Acceptance: a human/implementer semantic review checks the trace against source, not merely expected keywords. Reports distinguish inspected tests from executed tests and gaps from proven defects. Preserve sanitized live receipts, overlapping intervals, model/profile identities, output validation, and before/after content manifests. No live run means this comparison remains open.

#### E07: Failure is not partial success
Authority: required
Current state:
Current PAR validates and joins exact tool actions, keeps results isolated, and fails the group on action/output failure. The current executor does not promise fail-fast sibling cancellation or rollback of host effects.
Desired state:
The Codex bridge preserves those semantics while bounding every worker and cleaning up its resources. A failed branch prevents successful synthesis/emission; diagnostic receipts remain explicitly diagnostic.
Acceptance: cover malformed/missing/extra outputs, wrong snapshot, interrupted/failed Codex turns, duplicate or late protocol events, process death, deadline expiry, cancellation, and overlapping output rejection. Demonstrate no successful final emission and no leaked worker process. Preserve actual model cost rather than claiming rollback.

#### E08: Complete context and truthful snapshot identity
Authority: required
Current state:
OAK already distinguishes complete graphs and scoped documents; automatic host loading alone does not prove that the full required knowledge reached a worker.
Desired state:
Both workers use one host-fingerprinted immutable snapshot, complete applicable pinned AGENTS documents, and explicit OAK closure. Each scoped read is covered by its governing context; hostile instructions in inspected data cannot grant tools or change the approved task.
Acceptance: test missing/truncated governing content, ambiguous or escaping document references, oversized context, dirty live checkouts, changed source refs, scope changes, and a malicious fixture requesting edits or delegation. Check exact context manifests and source identities. Refuse uncertain context rather than silently summarizing it. Evidence of an unchanged snapshot and evidence of an unchanged live checkout remain separate.

#### E09: Copyable generated agent scenarios and a shared adaptor directory
Authority: required
Current state:
The pinned generated tree contains the grammar, definitions, authoring skill, and standalone authoring agent; no .agents product exists. The original unimplemented plan would have run scenario documents from examples and host code from .agents/adapters/codex. The intervening generated/oak-exploration suggestion was not committed product output.
Desired state:
Deliver the exact `generated/oak.agents/` subtree shown in Directory Changes: `parallel_exploration/` owns coordinator.oak.md, explorer.oak.md, sample.oak.md, and run.py; sibling `adaptors/codex/` owns adaptor.oak.md and the four narrow executable modules. Preserve the existing products. The scenario alone closes its OAK graph and offline fixture; the copied full bundle supplies the shared live adaptor, with external runtime, model, and inspected-repository requirements disclosed.
Acceptance: verify complete path/byte equality against source-owned generation, cold generation and repair, copied-scenario fixture execution, and copied-full-bundle preflight with source/build imports and implicit network blocked. Reject missing or stale documents/scripts, symlink/escape paths, undeclared sibling-scenario dependencies, and fallback reads of .agents or examples source. Run authorized live E06 through the delivered adaptor, not a source-only launcher. Exact delivered directory/entry names and scope separation must match; findings may vary. No root-hidden .agents installation, native .codex agent installation, README index, or speculative empty provider directory is added.

#### E10: Detailed directory-change views in the actual reusable SMEAC schema
Authority: required
Current state:
The SMEAC Mission template has End state followed by State Comparisons. It has no dedicated Directory Changes fields or prospective annotated-tree policy. A conversational tree is not a reusable schema change.
Desired state:
Insert this subsection into the actual template, using current string placeholder/WHERE conventions and retaining the existing five-section order:
````markdown
### Directory Changes

Baseline: <DIRECTORY_BASELINE>
Legend: [add] new; [modify] changed; [move from PATH] relocated; [remove] deleted; [keep] unchanged context; [check] verify and change only if needed.
Current:
```text
<DIRECTORY_CURRENT>
```
Planned:
```text
<DIRECTORY_PLANNED>
```
Ownership: <DIRECTORY_OWNERSHIP>
Verification: <DIRECTORY_VERIFICATION>
````
The present plan supplies a populated real example. Additional fixed verification specimens demonstrate an explicit move and removal, rather than falsely claiming this change moves existing files. Adopt the section in new/updated planning, with a reasoned no-file-change alternative and no retroactive rewrite of inactive/completed plans.
Acceptance: inspect the changed Python schema, generated canonical sibling, docs/examples ownership rules, and schema-derived plan checks. Validate both OAK groupings and populated instances; accept add/modify/move/remove/no-change/unknown-baseline specimens and reject missing, duplicated, out-of-order, empty, unclosed, or unresolved-placeholder sections for newly applicable plans. Preserve independent expected specimen meaning and older structural checks. Final review compares the actual diff and owned deliveries with the detailed tree; structural parsing alone is not proof of path truth. A plan-only note, chat-only convention, or unchecked diagram does not complete this change.

## 3. Execution

Intent: Deliver a useful exploration capability, not a new agent framework. Keep OAK contracts visible and make Codex's real capabilities and limitations testable. Preserve the user's flat authoring and explicit parallelism, and finish the generated bundle, shared guidance, directory-change schema, and verification rather than stopping at a working launcher.
Concept of operations: Establish permission and delivery feasibility before broad implementation. Build the portable worker/coordinator and narrow host adapter, then prove offline boundaries before any authorized live run. Generate the portable bundle and shared authoring deliveries, update the reusable planning schema, exercise the real repository task from the delivered bundle, and independently review the result against every required comparison and annotated path change.

### Phase 1: Establish compatibility and delivery gates
Objective: Confirm an executable foundation without weakening the approved design.
- [ ] Key task: P01.01 Restore the pinned governing graph, this amended plan, branch/checkpoint, and exact implementation authorization; read affected source in full and applicable coding standards/specialist skills before editing. Confirm A08/A09 and E09/E10 are included in the approval.
- [ ] Key task: P01.02 Inspect the supplied Codex version, generated protocol schema, effective configuration, dynamic-tool support, and isolation facilities; record a version-specific capability matrix and refuse unsupported surfaces.
- [ ] Key task: P01.03 Prove the restricted profile with offline protocol/policy probes, including failed hooks and inherited capabilities; document host model-traffic and audit-write boundaries separately.
- [ ] Key task: P01.04 Assemble and measure a readable candidate for both new knowledge documents and both authoring deliveries; inventory retained knowledge and demonstrate a fit under existing byte limits without weakening safeguards.
Success criteria: A01 through A09 are executable on a named supported host; E03, E05, and E08 have concrete feasibility evidence, and E09/E10 have explicit source/output ownership and schema-evolution decisions. No hidden architectural substitution or scope expansion is needed. No live model call is implied by this gate.
Transition trigger: Capability and size gates both pass; otherwise retain an exact blocked checkpoint and obtain a specific scope decision before continuing.

### Phase 2: Author the worker and parallel coordinator
Objective: Express the actual workflow through current OAK contracts and flat Python sources.
- [ ] Key task: P02.01 Define complete local worker request/result schemas, evidence meanings, receive-trigger-process identity, native investigation ACT, and emitted result in the new scenario.
- [ ] Key task: P02.02 Define coordinator schemas and the two explicit request/result mappings to the same worker definition; keep host receipts distinguishable from model findings.
- [ ] Key task: P02.03 Implement E02's named ACT.tool actions, Par, Join, synthesis, and output interface; give both branches complete immutable-snapshot request bindings.
- [ ] Key task: P02.04 Register the scenario, source-owned sample.oak.md, complete local dependencies, canonical siblings, and detached fixture demonstration. Make the fixture runner accept an explicit entry path so source example.oak.md and delivered coordinator.oak.md need no literal-rewriting trick. Preserve existing examples and the four-stage core.
Success criteria: E01, E02, E07, and E08 have passing structural, identity, dataflow, and detached fixture checks in both canonical groupings; no real Codex result is claimed yet.
Transition trigger: The complete scenario runs with honest deterministic hosts and preserves current executor semantics.

### Phase 3: Implement the restricted Codex adapter
Objective: Bridge OAK execution to actual Codex without granting the worker broad host authority.
- [ ] Key task: P03.01 Add the maintained pure OAK Codex adapter contract and its explicit context routing; implement the narrow stdio transport using the verified version-specific protocol.
- [ ] Key task: P03.02 Implement manifest-backed listing, bounded reads/search, revision inspection, and restricted diff, with path, byte, secret, symlink, and argument defenses.
- [ ] Key task: P03.03 Implement isolated startup, effective-profile checks, denied approvals/escalation, disabled ambient capabilities, full governing-context delivery, and host-owned audit receipts outside the repository.
- [ ] Key task: P03.04 Implement the Codex native interpreter, worker execute/arrival/emission lifecycle, two exact ToolContract registrations, validated result mappings, and no-tool synthesis interpreter.
- [ ] Key task: P03.05 Implement the delivery-safe launcher with explicit scenario, repository, commit, and external audit location; add bounded calls, timeout/interruption/cleanup, no automatic retries, and clear unavailable/unsupported/failed outcomes. It must run from the generated adaptor without imports or reads from the maintained source directories.
Success criteria: E01, E03, E07, and E08 pass without network or a model through controlled protocol fixtures; ordinary imports, generation, and fixture execution require neither Codex nor credentials.
Transition trigger: The adapter is ready for adversarial offline verification; no live use occurs before its separate authorization gate.

### Phase 4: Verify boundaries and concurrency offline
Objective: Demonstrate controls independently of model cooperation and preserve the current parallel contract.
- [ ] Key task: P04.01 Add allowed-operation and prohibited-operation tests covering every E03 class, including direct requests rather than only model refusals.
- [ ] Key task: P04.02 Use synchronized/barrier-based tool fixtures to prove simultaneous dispatch, isolated inputs/results, same-snapshot use, JOIN ordering, and deterministic promotion independent of completion order.
- [ ] Key task: P04.03 Exercise E07 failure classes, duplicate/late events, protocol mismatch, denial, process termination, and bounded cleanup; require no final success emission on group failure.
- [ ] Key task: P04.04 Exercise E08 knowledge completeness, scope crossing, malicious file content, changed refs, and dirty-checkout disclosures; verify host-derived citations and read receipts against actual blobs.
- [ ] Key task: P04.05 Register adapter and scenario checks in build/checks/__init__.py for both existing complete verification entry points, keeping live model tests explicit and opt-in; do not create another test entry point.
Success criteria: E02, E03, E07, and E08 pass with substantive negative tests and no model dependency. Permission assertions, same-named fake tools, or a pair of sequential calls cannot satisfy the tests.
Transition trigger: All offline safety and contract checks pass on the implementation revision.

### Phase 5: Deliver the agent bundle, guidance, and planning schema
Objective: Distribute the usable capability and make its annotated change-tree presentation reusable.
- [ ] Key task: P05.01 Add the focused portable orchestration guide covering A07 and complete runnable before/after examples with exact ACT.tool and PAR/JOIN semantics.
- [ ] Key task: P05.02 Generate Codex adapter knowledge from its maintained owner, with dated source references, supported profile/transport, exact mappings, and honest unsupported cases.
- [ ] Key task: P05.03 Route both new documents from the authoring entry and include their same knowledge in the standalone agent; preserve constants/schema-only supporting fusion and literal examples.
- [ ] Key task: P05.04 Refresh build/example ownership, explicit generated-layout/generator-map/output-map contracts, skill metadata/version and immutable validator fingerprints where required, and generated paths/bytes without changing installation-consent behavior.
- [ ] Key task: P05.05 Implement build/agents.py using the existing generation primitives to deliver E09's scenario and shared adaptor from their sole maintained owners; preserve literal bytes, explicit entry relocation, closed document graphs, and narrow cleanup ownership.
- [ ] Key task: P05.06 Add build/checks/agent_deliveries.py and update output/check registration for clean cold generation, source/byte equality, repeated generation, detached fixture execution, and copied-bundle adaptor preflight with repository/build imports and implicit network blocked. Cover missing dependencies, stale scripts, escaped paths, and cross-scenario coupling.
- [ ] Key task: P05.07 Extend examples/schemas/smeac_plan.py with A09's Directory Changes fields and descriptions, regenerate its .oak.md sibling, and complete a populated example showing additions, modifications, moves, removals, generated outputs, and ownership. Keep this plan as a real adoption example; future snapshots are clearly labelled expected, not observed.
- [ ] Key task: P05.08 Update docs/AGENTS.md and examples/AGENTS.md for prospective annotated-tree use, and extend build/checks/plans.py with schema-derived field/fence validation and positive/negative examples. Apply the new subsection requirement from plan 0016 onward without weakening older checks; do not retrofit inactive/completed records. Register and run the checks through the existing entry points.
Success criteria: E04, E05, E09, and E10 pass offline: both authoring forms contain the same new knowledge; the complete generated agent bundle works when copied away from source; required old content and behavior remain; byte limits hold; the updated SMEAC schema, guidance, and rejection checks agree; repeated generation is clean.
Transition trigger: Offline repository verification and shared delivery checks pass, and live acceptance is ready for explicit authorization.

### Phase 6: Run authorized live acceptance on OAK
Objective: Establish real Codex usefulness and concurrency without changing the repository.
- [ ] Key task: P06.01 Obtain or restore explicit authorization for the named model/provider, inspected commit, data disclosure, and bounded run budget; verify credentials without exposing them and recheck the effective profile.
- [ ] Key task: P06.02 Execute E06 from a detached copy of the delivered oak.agents bundle with two overlapping restricted Codex workers and one no-tool synthesis against the explicitly supplied OAK repository; preserve messages/results, tool receipts, context identities, timestamps, and sanitized usage observations. No helper may reach back to the implementation checkout for its code or agent documents.
- [ ] Key task: P06.03 Run one separately labelled adversarial live probe in a disposable snapshot; pair any observed model refusal with direct offline denial evidence, and verify no prohibited effect or surviving process.
- [ ] Key task: P06.04 Review the findings against source, verify citations and coverage, reconcile disagreements, and compare snapshot/live-checkout content manifests without hiding external drift or uncertainty.
Success criteria: E01, E02, E03, E06, E07, E08, and E09 have real version-bound execution evidence in addition to fixture checks. Missing authorization, runtime, credentials, or completed model work leaves live acceptance open, not skipped as passed.
Transition trigger: Live acceptance succeeds within the approved budget, or a precise blocked/failed checkpoint is retained without additional calls or silent retries.

### Phase 7: Verify and independently review the complete change
Objective: Confirm the delivered result against the original intent, not only implementation tests.
- [ ] Key task: P07.01 Run compilation, affected generators including `python -m build.agents` and the SMEAC sibling generator, `python -m build.examples`, and `python build/examples.py` in the required isolated environment; rerun generation and require no diff.
- [ ] Key task: P07.02 Compare the actual final diff and complete generated path/byte manifests with the annotated Directory Changes view and A08 source mapping. Resolve omitted or misclassified paths, obsolete proposals, unnecessary files, all limits, scope-safe fusion, optional dependencies, and unchanged APS/history; report actual before/after trees separately from expected specimens.
- [ ] Key task: P07.03 Independently review A01 through A09 and E01 through E10 against the user's requests: useful evidence, genuine tool enforcement/concurrency, generated .agents packaging, self-contained scenarios, shared adaptors, detailed reusable directory-change planning, preserved meaning, ownership, missing deliveries, and unnecessary machinery. Fix findings and repeat affected checks.
- [ ] Key task: P07.04 Complete the matching report with exact verified source/workspace identities, task evidence, limitations, changed paths, and final verdict; mark only evidenced tasks complete and create a PR only if authorized, with no merge.
Success criteria: Every required comparison E01, E02, E03, E04, E05, E06, E07, E08, E09, and E10 passes; the report separates inspected, executed, and verified results; independent review finds no material unresolved issue.
Transition trigger: Verified implementation is ready for the authorized review step; otherwise preserve remaining open tasks and the specific blocker.

### Coordinating Instructions
- Timeline: this is the 2026-09-07 planning delivery, amended for the user's generated-bundle and directory-tree request. No implementation deadline or unattended future work is promised; each authorized work session records its achieved checkpoint.
- Boundaries: no OAK syntax/runtime redesign, writable agents, automatic dependency downloads, remote publishing infrastructure, new CI workflow, alternative provider, recursive delegation, or unbounded scheduling. The SMEAC schema and owned documentation/check changes in A09 are explicitly in scope, not an unbounded planning-framework rewrite.
- Operating guidelines: preserve exact source identities and full applicable instructions after context recovery; do not replay completed phases or assume that a newer main changes this plan's governing revision.
- Risk mitigation: enforce capabilities before effects, separate trusted receipts from untrusted findings, preserve immutable snapshots and contracts, refuse unclear context, and keep failure diagnostic rather than successful.
- Live budget: propose at most four Codex sessions for the acceptance round: two exploration workers, one no-tool synthesis, and one adversarial probe. Initial ceilings are two concurrent workers, 40 read-tool calls per worker, 600 seconds per session, and zero automatic retries. Freeze compatible context/output byte ceilings during preflight and refuse overflow without truncating governing knowledge. These are resource ceilings, not work-time estimates. The user must approve the actual model/provider and spending or token ceiling before live use; a missing ceiling blocks live acceptance.
- Verification: host-controlled timing intervals demonstrate overlap, not a speedup claim. Equivalent snapshots, meaningful source-backed findings, and denial behavior matter more than keyword matching. Do not represent a successful fixture as live inference.

### Contingencies
- If the installed Codex build cannot enforce the strict profile, then stop at the compatibility gate with the exact unsupported surface. Do not substitute prompt-only restrictions, a writable native child, another transport, or a patched Codex fork.
- If required shared knowledge cannot fit within existing byte limits, then present the measured overage and retained-content comparison for a scope decision. Do not silently increase limits or drop capabilities.
- If credentials, execution access, network, or live authorization are unavailable, then complete authorized offline work, retain open live tasks, and report the exact blocker without claiming end-to-end completion.
- If a worker fails, times out, or returns invalid evidence, then retain diagnostic receipts, interrupt and reap that worker, allow bounded group cleanup, and emit no successful synthesis. Any new attempt requires authorization consistent with the approved budget.
- If the source checkout changes, then retain the pinned snapshot and report drift. A request to inspect different content creates a new request/snapshot rather than silently altering an active run.
- If the copied agent bundle needs an undisclosed source checkout, sibling scenario, or user-specific configuration, then fix the delivery closure and rerun detached checks; do not redefine self-contained to conceal that dependency. Installed runtime/model access and the explicitly inspected repository remain declared external inputs.
- If the final file set differs from the annotated tree, then reconcile the inventory and required comparisons before completion. A newly discovered material scope change requires approval; a diagram is not permission to add unnecessary files.
- If repository policy conflicts with the proposed scope, then stop and ask for the specific policy decision; do not reinterpret tests or local implementation as authority to relax it.

## 4. Admin and Logistics

| Resource | Quantity | Source | Status |
| --- | --- | --- | --- |
| Pinned repository knowledge and inspected source | One revision | GitHub at the baseline above | AVAILABLE |
| Planning branch and this document | One plan | User-authorized planning delivery | AVAILABLE |
| Executable checkout and isolated Python environment | One environment | Implementation host satisfying `pyproject.toml` and build policy | PENDING |
| Compatible installed Codex and protocol schema | One verified build | Explicitly supplied implementation host | PENDING |
| Authorized provider/model credentials and run budget | One named configuration | User/host, never repository files | PENDING |
| Manifest-backed snapshot and restricted read registry | One snapshot per run | Adapter implementation | PENDING |
| Sanitized receipts and semantic review | Offline and live sets | Completion report and its evidence directory | PENDING |
| Copyable generated agent bundle and shared adaptor | One bundle, one initial scenario | build/agents.py from example/support source owners | PENDING |
| Annotated directory-change planning schema | One canonical SMEAC schema | examples/schemas/smeac_plan.py, docs owner, and plan checks | PENDING |

Supply: use existing repository dependencies where suitable; inspect standards, library documentation, and types before adding code or packages. Keep Codex optional for importing, building, and testing OAK; downloads and installation require separate permission.
Transportation: maintain OAK schemas and documents as the authored knowledge; use Codex's own JSON-RPC and configuration formats only at the host boundary. Move exact validated results through the declared mappings and keep credentials and raw private runtime data out of committed evidence.
Sustainment: record runtime/protocol/profile identities, context coverage, sanitized tool events, deadlines, actual available usage data, and clear not-performed reasons. Keep maintained source separate from generated knowledge and executable deliveries, update the adapter's supported-version evidence when its host changes, and maintain the change-tree policy with its canonical SMEAC schema rather than platform memory.
Rollback: this amendment changes only the existing planning document; the earlier planning commit is preserved. Implementation corrections are new commits; never rewrite history or erase evidence. Read-only investigations have no repository edits to revert, but Codex requests, cost, host audit files, and external concurrent changes are not rolled back by OAK transactions.

## 5. Command and Signal

1. The user owns intent, implementation approval, live data/model/spend authorization, material scope changes, PR creation, and merge decisions.
2. The implementing assistant owns direct repository work, truthful checkpoints, contract-preserving execution, verification, and final review; bounded demonstration workers return evidence but gain no implementation authority.

| Channel | Medium | Purpose | Cadence |
| --- | --- | --- | --- |
| User conversation | Brief progress and decision messages | Report meaningful findings, blockers, authorization needs, and outcomes. | During substantial work and at gates. |
| This plan | Versioned Markdown | Retain scope, acceptance examples, open tasks, and continuation checkpoint. | At authorized phase transitions. |
| Completion report and evidence | Versioned sanitized receipts | Record actual checks, live/fixture distinctions, identities, limitations, and final verdict. | As observations are established. |

Reporting: planning readiness is not execution approval or implementation completion. Preserve the plan commit identity and governing revision on continuation; then record authorization and exact progress without fabricating a host lifecycle receipt.
Reporting: every completed task requires observed evidence, and E06 requires actual Codex results. State separately what was inspected, executed, verified, assumed, blocked, or not performed.
Reporting: the planning session performed repository/documentation inspection and a local structural review of the planning text only. It did not execute the repository's verifier, launch Codex, install dependencies, change product files, or open a PR.

| Decision | Authority | Escalation |
| --- | --- | --- |
| Amend and commit this plan on its existing branch | User's 2026-09-07T02:29:23Z packaging and planning-schema request | User for further material scope changes; preserve the earlier commit. |
| Implement the plan | User's explicit continuation for this plan revision | No implementation until received. |
| Run Codex and transmit source/context to its model service | User/host authorization for the named model, data, and budget | Block live acceptance if absent. |
| Install/download dependencies or tools | Separate explicit user consent | Do not infer from planning, validation, or live-use requests. |
| Relax restrictions, size bounds, or language/ownership scope | User | Stop at the relevant gate. |
| Create a PR or merge | Explicit user authorization for that operation | Keep the branch unmerged otherwise. |

### Acknowledgement
The implementing assistant must acknowledge this exact plan and restore its complete governing knowledge before execution. The user's planning and amendment requests acknowledge the direction, not completion of the implementation or approval of a live run. The Directory Changes view is already populated here, but changing the actual SMEAC schema, product directories, and generators remains explicitly planned work.
