# Add restricted parallel Codex exploration

Prepared: 2026-09-07T12:09:23+10:00
Classification: PUBLIC
Amendment: Preserve the 2026-09-07T02:29:23Z generated .agents packaging and SMEAC directory-change scope; add researched native Codex CLI and ChatGPT desktop delivery at the user's 2026-09-07T02:52:43Z request. Supersedes plan-only checkpoint `a9d2666cc4d71429c4c2769f9ad4b3a18cfceed6` without rewriting it.
Readiness: Ready for implementation approval as a researched design with mandatory installed-host, native-client, and delivery-size gates. Native runtime compatibility and live acceptance are not yet verified.
Execution: Not started. Every implementation task remains open.
Authorization: The user authorizes research and amending this plan and its supporting research record on the existing branch. Only planning documents change now. Product implementation, native installation, live Codex calls, dependency installation, a pull request, and a merge still require their stated approvals.
Branch: `docs/plan-parallel-codex-exploration`
Baseline and governing revision: `9956e6998869fcfbd84067eec0d6303273a54174`
Plan location: `docs/plans/0016-parallel-codex-exploration/plan.md`
Restored checkpoint: plan-only commit `a9d2666cc4d71429c4c2769f9ad4b3a18cfceed6`; all 34 earlier implementation tasks are still open, with no implementation authorization to carry forward. This expanded proposal retains their identifiers and requires approval at its new committed revision.

## 1. Situation

### Operating Environment
OAK expresses portable knowledge and execution contracts; a host supplies models, tools, credentials, persistence, and effects. The capability uses a real Codex interpreter to explore OAK without changing it, with independent investigations dispatched through OAK's existing parallel tool actions. Its native clients are Codex CLI and the new ChatGPT desktop app's local Codex view, not VS Code or an ordinary hosted Chat/Work conversation.

### Current State
At the pinned baseline, `ACT.tool(...)` constructs an exact tool-backed action and renders as `ACT TOOL`; `Par` accepts independent exact tool actions with distinct output bindings, followed by `Join`. The existing delegation example dispatches `agent.reviewer` through `ToolContract`, but its worker uses deterministic fixture responses; the repository has no `.agents/adapters` directory. The authoring skill has brief delegation guidance, whereas the legacy APS snapshot contains dedicated subagent and platform-adapter material. There is no generated .agents bundle, native Codex installation payload, or OAK MCP entry. The SMEAC template has State Comparisons but no dedicated directory-change view. The previous planning checkpoint did not promise native-client discovery; that gap is explicitly closed here.

### Challenges
- Enforcement: a prompt, declared allowlist, read-only hint, or custom-agent default does not establish the worker's effective capabilities. Codex child sessions can inherit parent runtime overrides, and tool hooks have documented coverage and failure limitations.
- Host integration: OAK expects a tool result with declared bindings, not a spawned thread identifier. The adapter must own Codex session startup, tool dispatch, completion, validation, deadlines, and cleanup.
- Parallel meaning: both workers must inspect the same immutable snapshot; their reports remain isolated until JOIN. Existing PAR failure semantics must not become silent partial success.
- Context: full applicable governing documents and explicit OAK dependencies must be available without flattening their scope or trusting automatic AGENTS discovery to avoid truncation.
- Evidence: schema-valid text is not proof of a read, a rejected operation, overlapping execution, or a correct interpretation. Host observations and semantic review must remain distinct.
- Delivery size: the baseline standalone authoring artifact is 63,981 bytes against a 64,000-byte limit. Adding guidance and adapter knowledge requires a measured, meaning-preserving fit, not an assumed exception.
- Packaging: a generated agent document is not a runnable Codex installation. Deliver the scenario graph, fixture runner, and shared adaptor together while keeping maintained sources and runtime dependencies explicit.
- Native delivery: a discoverable TOML file, shared host configuration, and an app-server process are different artifacts. Preserve OAK execution and worker restrictions through the installed entry instead of treating natural-language parallel spawning as PAR.
- Client identity: distinguish the new ChatGPT desktop app's Codex view from ChatGPT Classic, Chat/Work, cloud mode, and the IDE extension; test the actual requested clients.
- Planning visibility: detailed trees must identify actual source/output changes and removals, not decorate an incomplete inventory or require rewriting historical plans.

### Supporting Factors
- Higher intent: make OAK useful on its own repository while demonstrating exact tool use, restricted agents, parallel execution, and explicit orchestration contracts.
- Adjacent efforts: preserve flat Python authoring, self-contained examples, locally understandable public contracts, shared skill/agent generation, and the existing repository lifecycle.
- Supporting resources: the sources and governing owners below, the existing executor and example catalogue, the APS snapshot as historical design reference, and current official Codex documentation.

### Assumptions
- Codex means a real Codex runtime through its app-server protocol, not merely a model name or a deterministic substitute. Model selection and authentication remain explicit host choices.
- A compatible, already installed Codex runtime and authorized model access can be supplied for implementation acceptance. Their availability has not been established in this planning session.
- Required use includes an installed native custom-agent entry in both Codex CLI and the new ChatGPT desktop app's Codex view, using local execution on an explicitly selected OAK project. The delivered launcher remains the shared implementation/preflight path, not a substitute for native-client acceptance. A10 through A13 define installation, the local MCP entry, and the independent restricted workers. The `.agents` bundle suffix is not a native discovery mechanism.
- The initial workload is a fixed pair of independent investigations, not an unbounded agent pool or dynamically recursive delegation.
- The existing OAK language is sufficient. Product implementation does not require a new statement, part, alias language, permission keyword, or scheduler.

### Constraints and Limitations
- Constraint: change only this plan and its supporting `evidence/native-clients-research.md` during this planning amendment. Preserve main and all original commits; do not amend, squash, rebase, force-push, merge, or delete branches.
- Constraint: use `ACT.tool(...)`, `Par(body=[...])`, and `Join()` in Python and their current canonical OAK renders. Keep meaningful definitions flat and named before assembly.
- Constraint: work directly without research subagents. Later authorization may permit only the bounded Codex demonstration workers described here, not unrestricted delegation by the implementing assistant.
- Constraint: retain OAK's host boundary, local worker state/interface ownership, explicit graph composition, exact tool names, and current transaction semantics.
- Constraint: each backend explorer has no usable editing, command execution, package installation, general web/network, connector, or worker-spawning capability. Model-service/authentication traffic is a separate, explicitly authorized host connection.
- Constraint: preserve the 500-line AGENTS limit, 10,000-byte skill-entry limit, 64,000-byte standalone-agent limit, validator identity and consent safeguards, literal teaching content, and scope-safe fusion.
- Constraint: keep maintained repository-support sources in `.agents`, example sources in their scenario, and product deliveries in `generated`, including the newly authorized `generated/oak.agents/` layout. Update the build owner's generated-layout, generator-map, and output-map contracts explicitly; the old closed output set cannot be silently bypassed. Add no directory README indexes or provider-specific skill-frontmatter fields.
- Constraint: add the annotated Directory Changes subsection to the actual SMEAC schema, its canonical sibling, owning guidance, and verification during implementation, not only this plan. Keep the five SMEAC sections and compact phase format; do not retrofit inactive/completed historical records or broaden their existing format exemptions.
- Constraint: ship native TOML/configuration and the local MCP integration in this change, but do not treat the native caller as the restricted worker. Do not install anything during planning or weaken the independent backend boundary to imitate native child threads. The required desktop acceptance is not satisfied by VS Code, browser ChatGPT, ChatGPT Classic, or a headless test.
- Constraint: retain APS as unchanged historical reference. Do not import its input/format syntax, USE/CAPTURE conventions, tool aliases, external task-config formats, or dated platform claims into OAK.
- Limitation: repository sources were inspected through GitHub. The earlier pinned archive attempt failed to resolve `codeload.github.com`; this amendment uses the verified plan bytes and source inspection rather than claiming an executable checkout. Full repository checks, native desktop/CLI acceptance, installation, and live Codex execution have not run.
- Limitation: the capability and size gates below can block implementation acceptance. A blocker must be reported specifically; it must not be hidden by weakening the agreed restrictions or redefining completion.

### Governing Knowledge and Source Record

The complete root and applicable scoped knowledge at the pinned revision govern this plan. The original planning session checked main at that revision. This native-client amendment restores the complete pinned text and verifies the existing planning branch/checkpoint; it does not substitute newer governing knowledge. Restoring the complete pinned texts takes priority after context loss. This is an authorized amendment to the restored planning checkpoint, not a continuation of an approved implementation. The expanded proposal requires approval at its new committed revision; the pinned governing revision is unchanged.

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

The primary-source research for this amendment preceded plan edits; final link and consistency checks validate the resulting record. The [native-client research record](evidence/native-clients-research.md) records current primary sources R01 through R10, scope distinctions, rejected shortcuts, and remaining runtime evidence. Current documentation supports native discovery and a shared local MCP connection for the two requested targets, not universal restriction enforcement on an arbitrary installed build. These protocol references remain relevant:

| Source | Relevant observation and design consequence |
| --- | --- |
| [App-server protocol](https://developers.openai.com/codex/app-server/) | Provides request/notification lifecycles, structured turn output, interruption, and experimental dynamic tools. Use a version-checked stdio adapter rather than parsing terminal prose. |
| [Configuration reference](https://developers.openai.com/codex/config-reference/) | Distinguishes command tooling, MCP tool filters, feature controls, and project instruction limits. Do not treat an MCP allowlist as a global capability filter. |
| [Subagents](https://developers.openai.com/codex/subagents/) | Defines native TOML discovery and inherited live parent overrides. Generate a native entry but keep actual exploration in independent restricted sessions. |
| [Hooks](https://developers.openai.com/codex/hooks/) | Covers many local tools but excludes hosted paths and warns against treating hooks as complete enforcement. Hooks may add defense and observations, not replace the primary boundary. |
| [Agent approvals and security](https://developers.openai.com/codex/agent-approvals-security) | Command sandbox/network policy does not govern all hosted capabilities. Disable or separately constrain every reachable surface. |

The research also verifies the [new ChatGPT desktop product and separate Codex view](https://help.openai.com/en/articles/20001276), [shared local MCP configuration](https://learn.chatgpt.com/docs/extend/mcp), and [native custom-agent fields](https://learn.chatgpt.com/docs/agent-configuration/subagents). The supported desktop target is its local Codex view. No user-specific installed version or operating-system compatibility is assumed. The [Codex MCP server command](https://learn.chatgpt.com/docs/mcp-server) is deprecated; our own MCP bridge is distinct from that command.

## 2. Mission

After explicit implementation approval, the implementing agent delivers and verifies a generated OAK agent bundle usable through Codex CLI and the ChatGPT desktop app's local Codex view, preserving a restricted explorer, parallel coordinator, shared adaptor, native installation, reusable authoring guidance, and directory-change planning schema.

Task: complete every approved phase in this branch before reporting implementation complete; create an implementation PR only when separately authorized.
Purpose: demonstrate portable OAK meaning driving a real host without confusing instructions, configuration, tool visibility, permission enforcement, and observed behavior.
End state: `generated/oak.agents/` contains a self-contained scenario graph and fixture demonstration beside a shared `adaptors/codex/` directory. A generated native TOML entry and installed local MCP configuration route into the same OAK coordinator. One explorer definition serves two concurrent restricted Codex sessions; joined reports yield source-backed synthesis without repository changes. Both native clients have separate acceptance evidence. The generated skill and standalone authoring agent teach the same contracts, and the actual SMEAC schema makes annotated current/planned directory trees reusable in future plans.

### Architecture Decisions

#### A01: An OAK worker and an executable Codex adapter are different artifacts

The explorer is a typed OAK document. Its receive interface and entry process share its own local request schema; its native investigation ACT has an explicit output contract and emits a complete local result. The coordinator is another OAK document with locally explained dispatch and result contracts. Neither document embeds credentials, CLI configuration dialects, or provider-specific language semantics.

The host adapter starts the worker's OAK execution and supplies a Codex-backed native interpreter. That interpreter receives the OAK invocation and its resolved document context, exposes the restricted read tools, and returns structured values for OAK validation. The host collects the worker's emission, validates it, and explicitly maps it to the coordinator's declared result binding. This exercises the existing executor rather than treating OAK as a decorative prompt around an unrelated Python workflow.

#### A02: Use app-server over stdio, with isolated sessions

Use the installed `codex app-server` stdio interface, one isolated process/session per concurrently active worker. Initialize the protocol, verify required capabilities, inspect effective configuration, create an ephemeral thread, start the turn with an output schema, service only registered read-tool requests, and await a successful terminal turn before returning. Record the actual binary version, protocol-schema fingerprint, selected model, and effective profile with each run. Generate schemas from that binary. Supply `outputSchema` on every relevant turn, and explicitly negotiate experimental dynamic-tool support; adding dynamic tools does not remove built-ins.

App-server is chosen because this task needs client-owned dynamic tool handling, lifecycle events, and bounded interruption. A simple `codex exec` or SDK wrapper is smaller for ordinary jobs but does not by itself establish this plan's complete enforcement and event contract. Do not add a second backend Codex transport, fall back to an inherited native worker, fork Codex, or build a general host framework. A11's local MCP ingress invokes the same OAK execution and app-server backend; it is not the deprecated `codex mcp-server` command or an alternative scheduler. Experimental protocol use is explicit and guarded by compatibility checks, not described as a stable universal API.

The adapter fails before launching model work when the installed build cannot establish the declared capability restrictions. A current-documentation citation, a configuration file that parses, or `config/read` alone is not an effective tool-inventory proof. Preflight records actual supported feature controls and per-turn policy, not an invented universal allowlist. Unknown configuration fields, unsupported tool suppression, inherited capabilities, or incomplete policy inspection fail the compatibility gate; they do not authorize weaker operation.

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

Each backend model cannot select a workspace root, widen a read set, replace the profile, add tools, supply credentials, or approve an escalation. Disable shell/unified execution, editing, nested delegation, hosted search, apps/connectors, browser/computer use, automatic skill/plugin activation, MCP servers, and dependency installation unless the precise surface is one of the owned read operations. Use an isolated configuration/home and neutral working directory outside the inspected checkout, deny approval and permission expansion, and do not inherit user or project config that silently enables capabilities. Supply pinned governing knowledge explicitly rather than allowing ancestor-directory discovery to add or truncate it. Retain an appropriate read-only sandbox as defense in depth. Custom hooks, when used, are not the only defense against a callable prohibited surface.

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

Use two backend workers as the initial concurrency ceiling and no worker recursion; native-entry sessions are separately accounted client work, not backend workers. A synthesis Codex session has no callable external tools and receives the joined reports, their host receipts, and its own complete scoped OAK invocation/context. It does not receive repository-read or dispatch capabilities. It reconciles conflicting evidence, distinguishes gaps from defects, and produces one user-facing answer; agreeing worker prose is not independent proof.

#### A07: Re-imagine APS adapter knowledge in OAK

| Useful APS idea | OAK treatment |
| --- | --- |
| A platform adapter separate from the standard. | A pure OAK adapter knowledge document plus a small executable host binding; no core-language changes. |
| Coordinator as dispatch owner; bounded leaf workers. | Explicit `ACT.tool`, worker schemas/interfaces, isolated host sessions, and no recursive worker tool. |
| Public request and response mappings. | Complete local schemas, validated arrivals/emissions, ToolContract checks, and one explicit mapping per dispatch boundary. |
| Tool registries and platform capability facts. | Exact supplied registry entries, dated source evidence, effective-profile observations, and failure when unsupported. |
| Parallel review and sequential handoffs. | Existing PAR/JOIN for independent tool calls; CALL for local process composition; host invocation stays distinct from both. |
| Adapter templates and installation conventions. | Generate native TOML and an explicitly installed local MCP entry from OAK; preserve the independently restricted workers and avoid unrelated project scaffolding. |

Do not copy APS platform tables as present-day truth. Do not add `predefinedTools.json`, `config.json` aliases, USE/CAPTURE syntax, or generic fallback execution. The required guide explains native ACT versus exact tools, request/result ownership, independent task splitting, full scoped context, least privilege, concurrency bounds, JOIN, conflict reconciliation, failure, cleanup, evidence, and permission inheritance. Explain native discovery versus installation, the native entry versus backend worker, the two requested client surfaces, and MCP versus app-server without duplicating maintained platform policy.

#### A08: Deliver an oak.agents bundle from one set of maintained sources

Use `generated/oak.agents/` alongside `generated/oak-authoring.skill/`. The bundle contains scenario directories directly, initially `parallel_exploration/`, and a separate shared `adaptors/codex/` directory. Do not insert another examples directory or create empty future scenarios/providers. The suffix identifies a directory of generated OAK agent deliveries; it is not the repository's hidden `.agents/` source directory, a new OAK part, an archive, or an automatically installed Codex agent.

| Path or owner | Planned responsibility |
| --- | --- |
| `examples/parallel_exploration/example.py` and sibling `example.oak.md` | Flat coordinator source and canonical repository render, including both tool-backed branches, JOIN, and synthesis. |
| `examples/parallel_exploration/explorer.py` and sibling `explorer.oak.md` | One reusable typed backend leaf worker; the native entry is a different boundary, not a second copy of this prompt. |
| `examples/parallel_exploration/sample.oak.md`; `run.py` | Source-derived complete sample request/data and a maintained detached deterministic fixture runner. The fixture runner accepts an explicit entry path and never defaults to live model work. |
| `examples/catalog.py`; `examples/catalog.oak.md` | Register the scenario, owned sample generator, local dependency closure, regeneration, and source-directory fixture command without displacing the four-stage teaching core. |
| `.agents/adaptors/codex/adaptor.oak.md` | Maintained pure OAK Codex contract, capability policy, dated version evidence, invocation meaning, and unsupported cases; constants/schemas only where shared with authoring fusion. |
| `.agents/adaptors/codex/run.py`, `transport.py`, `tools.py`, `contracts.py`, `serve.py`, `install.py` | Maintained host implementation for explicit launch/preflight, bounded stdio lifecycle, manifest-backed reads, validated mappings, local MCP ingress, and content-checked native installation. These sources also produce the executable generated adaptor; no runtime-only implementation is hidden in the source checkout. |
| `build/agents.py` | Generate the complete `oak.agents` bundle from the registered example sources and maintained adaptor files through the existing generated-file primitives. Own its complete file set, entry mapping, byte freshness, and narrow cleanup. Never use delivered scripts as build source. |
| `generated/oak.agents/parallel_exploration/coordinator.oak.md`, `explorer.oak.md`, `sample.oak.md`, `run.py` | Copyable scenario containing its complete OAK document graph, required sample data, and offline fixture runner. Explicitly map the source entry `example.oak.md` to delivered `coordinator.oak.md`; keep worker scope separate. |
| `generated/oak.agents/adaptors/codex/adaptor.oak.md`, `run.py`, `transport.py`, `tools.py`, `contracts.py`, `serve.py`, `install.py` | Generated, usable Codex adaptor and exact executable helper deliveries. The launcher accepts explicit scenario, repository, commit, and external audit paths. It does not load agent documents or implementation code from `.agents`, `examples`, or `build`. |
| `examples/parallel_exploration/codex_entry.py` and sibling `codex_entry.oak.md` | Small locally complete OAK native-entry contract. The generated TOML embeds this exact canonical knowledge, not another prose prompt or the backend worker scope. |
| `generated/oak.agents/parallel_exploration/codex/entry.oak.md`; `.codex/agents/oak-exploration.toml`; `.codex/config.fragment.toml` beneath that codex directory | Native entry knowledge, ready custom-agent definition, and explicitly labelled merge fragment. build/agents.py derives metadata and values from the example and adaptor owners. Installation materializes complete machine-specific configuration without editing generated files. |
| `pyproject.toml` | Declare the optional Codex-host MCP SDK dependency range selected by compatibility evidence, without adding it to the core mandatory dependency path. |
| `build/authoring_guides.py`; `build/authoring_platforms.py` | Compose portable orchestration and transform the maintained Codex knowledge into shared authoring material without a second policy source. |
| `build/authoring.py` | Register the new shared authoring documents and regenerate both forms. Preserve existing scope-safe fusion; a generic fusion rewrite is not presumed. |
| `generated/oak-authoring.skill/guides/subagent-orchestration.oak.md`; `platforms/codex/adaptor.oak.md` beneath that skill | Generated authoring guidance and Codex knowledge from their owners. The skill's platforms path is a teaching projection, not a second executable adaptor directory. |
| `generated/oak-authoring.oak.md` | Contains the same authoring knowledge through existing fusion. Operational coordinator/worker documents and host scripts are not fused into this authoring agent. |
| `examples/schemas/smeac_plan.py` and sibling `.oak.md`; `docs/AGENTS.md` | Source and canonical delivery of the A09 Directory Changes subsection; durable prospective plan-authoring policy. |
| `build/checks/codex_adapter.py`; `build/checks/codex_native.py`; `build/checks/agent_deliveries.py` | Protocol, permissions, lifecycle, native configuration/MCP/installation, parallelism, copied-bundle usability, cold generation, exact file/byte closure, and rejection checks. Keep the existing AGENTS-policy checker distinct. |
| `build/checks/plans.py`; `build/checks/outputs.py`; `build/checks/__init__.py`; existing authoring/example checks | Schema-derived planning checks, expanded generated ownership, and registration through the existing `build/examples.py` entry points. |
| `build/AGENTS.md`; `examples/AGENTS.md`; `.agents/rules/context.oak.md` | Explicit generated output/source ownership, scenario and tree-authoring rules, and routing to maintained Codex knowledge. Keep root AGENTS and its lifecycle unchanged. |
| This plan; later `report.md` and `evidence/` | Amended scope, expected/observed directory views, checkpoints, acceptance receipts, source identities, and final review. |

Define self-containment honestly at two levels. Each scenario contains its complete OAK graph and offline fixture demonstration, with no dependency on another scenario. The whole `oak.agents` bundle additionally contains the shared executable Codex adaptor needed for live use. Installed OAK/dependencies, compatible Codex, authorized model access, and the repository explicitly selected for inspection remain external runtime inputs; they are not vendored or silently installed. Copying only a scenario does not include the live adaptor. Copying the whole bundle must require no maintained source checkout.

The maintained fixture runner uses delivered `coordinator.oak.md` as its default entry; the source-scenario command supplies `--entry example.oak.md`. Use explicit entry/typed-target relocation when necessary, not replacement of arbitrary script text, instructions, tool names, or literal payloads. Generated adaptor scripts are exact deliveries from their maintained files and accept explicit paths rather than deriving a development repository from their own location. All real use and acceptance operate on generated deliveries, not a privileged source-only launcher. Native installation uses the copied full bundle as its stable executable source; moving or deleting it requires reinstallation, not a silent source-checkout fallback.

Use the same Codex knowledge source for the runtime bundle and the skill projection; verify equality or a documented, lossless projection before fusion. This intentional generated duplication does not create a second policy owner. Keep coordinator and worker operational documents separate; bundling is not fusion. Do not produce the earlier conversational `generated/oak-exploration/` layout. Native `.codex/agents` installation is now an explicitly authorized planned deliverable under A10 through A12, superseding the former exclusion; actual installation still requires separate consent. The earlier `.agents/adapters/codex/` spelling was an unimplemented proposal, not an existing directory to move; maintained and executable delivery directories now use `adaptors/codex/`.

Extend `build/AGENTS.md`'s closed generated-layout, generator-map, and output-map explicitly for the new bundle, then update output validation, cold generation, and repair checks. Retain the existing four products and make each generator prune only its owned subtree. Do not edit generated files by hand, broaden cleanup across unrelated outputs, or add another publishing workflow. Record source-to-delivery bytes and reject missing, extra, stale, escaping, symlinked, or source-checkout-dependent deliveries.

The authoring size gate remains mandatory before broad product work: inventory candidate bytes and remove only demonstrated redundant representation or repeated explanatory prose through the correct owner. Do not strip examples, externalize required standalone knowledge into the new agent bundle, encode it opaquely, raise a limit, or hide an unrelated validator rewrite. If a readable complete candidate cannot fit, stop for a specific scope decision.

#### A09: Make annotated directory changes part of the SMEAC schema

Extend the existing schema's Mission section with `### Directory Changes`, after End state and before State Comparisons. This is an ordinary presentation subsection of the current SMEAC schema, not a sixth top-level section or a new OAK/configuration language. Add ordinary string placeholders and explanatory WHERE clauses for `DIRECTORY_BASELINE`, `DIRECTORY_CURRENT`, `DIRECTORY_PLANNED`, `DIRECTORY_OWNERSHIP`, and `DIRECTORY_VERIFICATION`. Current and planned views use separate fenced text blocks; a fixed explanatory legend defines change annotations. Keep the existing comparison authority and phase contracts intact.

The tree should expose the affected file hierarchy with useful inline purpose notes, not only broad directory names. Include maintained source, generated deliveries, examples, adaptors, documentation, and verification owners. Show actual observed current paths separately from future paths; state explicitly when a proposed artifact is absent. Distinguish `[add]`, `[modify]`, `[move from <path>]`, `[remove]`, `[keep]`, and `[check]` (an existing path inspected/regenerated that might remain byte-identical). Use indentation and optional tree branches with aligned `#` purpose notes. Moves name both old and new paths, removals remain visible as tombstones, and generated files identify their owner. Collapse only unrelated unchanged paths; no ellipsis may hide an affected file or a required dependency.

`docs/AGENTS.md` owns use of the subsection in new plans and explicitly reopened/updated plans going forward; `examples/AGENTS.md` owns the presentation guidance alongside its other schema-authoring conventions. Require a populated view for repository file changes. A plan with genuinely no file changes retains the subsection with the explicit sentence `No directory or file changes.` and a reason instead of inventing a tree. Do not retrofit inactive/completed historical records. Enforce the new required subsection for plan 0016 and subsequently allocated plan IDs; this feature-specific adoption boundary does not exempt older plans from their existing SMEAC, comparison, storage, or navigation checks. Any explicitly reopened older plan adopts the current policy when its scope is updated.

Derive structural expectations from the canonical schema in `build/checks/plans.py`: placement, field labels, populated fenced views, and absence of unresolved schema markers. Test added/modified paths, explicit move/removal annotations, a no-file-change case, unknown/missing baselines disclosed honestly, and rejection of malformed or missing required views. Preserve fixed independent specimens so changing the template cannot redefine the intended layout. Do not build a new tree parser, path DSL, task manifest, or general diff engine. Structural validity does not prove the tree matches reality: final review separately compares it with the observed Git diff, owned generated path/byte manifests, and the source/output map. Resolve omissions and unsupported ownership claims before completion.

#### A10: Native entry for exactly the two requested clients

Target Codex CLI and the new ChatGPT desktop app's Codex view in local-project mode. The desktop product includes other views, but this is not a promise that ordinary Chat/Work or ChatGPT Classic reads local agent TOML. VS Code, browser ChatGPT, cloud execution, and remote-host substitution are out of scope. Record the actual client/OS, selected project, effective host configuration, and backend binary separately. One tested OS combination may establish the supplied environment; it does not prove every desktop platform.

Generate `parallel_exploration/codex/.codex/agents/oak-exploration.toml`, with `name`, `description`, and `developer_instructions`. The name deliberately identifies the complete exploration entry rather than misleadingly labelling a native child as the restricted backend explorer. Its `developer_instructions` is a lossless TOML serialization of `codex/entry.oak.md`, derived from `examples/parallel_exploration/codex_entry.py`. The entry is a small complete OAK node with its own request/result contract and an exact bridge action; it returns the validated bridge result and limitations, never investigates through unrelated native tools or creates its own worker pool. Preserve literal bytes through TOML decoding and OAK parsing. No handwritten English prompt duplicate or fused operational graph is acceptable.

Custom agents are spawned-session configuration layers, not an automatic replacement for the main thread. The normal client conversation selects the named entry. The entry calls A11's local MCP operation, which executes the existing OAK coordinator and independent restricted workers. This gives native discovery and real OAK PAR/JOIN without relying on native child inheritance as enforcement. The native caller is not an OS security boundary: do not claim that its parent's unrelated tools are restricted or that this file alone prevents every caller action. No less-restricted direct-native worker is exported as an alternative. The actual explorer and synthesis sessions retain all A04 controls, regardless of parent permissions.

The MCP server name is `oak_exploration` and its sole workflow tool is `explore`. Resolve and test the exact model-visible tool name through the supported client registry during the compatibility gate; keep the confirmed naming projection in the adaptor owner and generate the entry's typed tool target from it. A guessed decorated name, runtime string substitution inside literal OAK, or an unregistered OAK alias is not acceptable. Refuse a registry mismatch. The entry reports missing configuration instead of falling back to native shell/spawn tools. Backend threads need not appear as native subagent UI threads; receipts, not a fabricated UI topology, identify their work.

#### A11: One local MCP ingress into the existing executor

Add `serve.py` using the maintained Python MCP SDK as an optional host dependency. Expose one bounded `explore` operation with explicit input/output schemas and a structured result; no generic shell, arbitrary script execution, file-writing tool, or alternate orchestration engine. Stdio is local and uses no public listener, tunnel, website, marketplace publication, or OAuth service. This new OAK server is not `codex mcp-server`; the latter's deprecation does not remove local MCP client support. Importing, discovering the agent, starting MCP, and listing tools perform no model work and grant no live authorization.

The trusted launcher provides an explicit host-side authorization command after real user consent, recording one scoped operation allowance outside the repository; this command is not an MCP or worker tool. It binds exact inputs, model/data/spend approval, bundle identity, and expiration, and a task change invalidates that allowance. The server configuration binds an explicit repository, immutable commit, permitted question/path envelope, model/provider, strict worker profile, and audit directory. A host-authenticated run allowance is additionally required for each admitted operation. Missing or expired allowances reject explore, and a spent allowance cannot initiate new model work; only the exact completed-result replay defined below is permitted. None of these states prevents safe MCP initialization and tool discovery, keeping required-server startup independent of live-use consent. The client supplies only the bounded task values and the host-issued operation identity, not arbitrary roots, executable paths, credentials, configuration patches, permission choices, or approval booleans. Validate both schema and authorization before starting OAK. Caller text, `readOnlyHint`, tool approval preferences, or a claimed approval string cannot create the allowance. Expose only sanitized non-secret identifiers; installation and live-use consent are separate.

Invoke the coordinator through `execute` and its declared arrival, not through a reimplementation of PAR in the MCP server. Return only a completed, validated emission plus a bounded host receipt identifying operation, snapshot, governing graph, profile, observed overlap, usage, and limitations. A session/job handle is not a successful result. Use supported MCP progress notifications for waiting clients, but no polling service or background queue. Set a 1,260-second overall backend deadline, including worker/synthesis startup and cleanup, and a larger 1,500-second MCP `tool_timeout_sec`; keep per-session and read-call ceilings below. Preflight must verify each actual client's wait/cancel behavior. Freeze bounded result sizes against the configured tool-output budget so required result fields and evidence are not silently truncated.

Use a host-owned interprocess admission lock for this authorized installation, shared by CLI and desktop server processes. Admit one workflow at a time, with two backend workers inside it; reject a competing request instead of multiplying the pool. Request identities bind exact inputs, bundle revision, and authorization. Duplicates of active/failed work do not restart it; a retained completed receipt may be returned only for the exact same request and allowance. A new attempt requires a new allowed operation. This is a narrow admission/replay guard, not a scheduler.

Propagate MCP cancellation, timeout, disconnect, and server shutdown to the active supervisor; interrupt and reap its workers, release admission, and retain diagnostic receipts without a success emission. Require cleanup within a configured 15-second shutdown bound after the server receives cancellation; the overall deadline remains independent. Test whether stopping the operation in each native client actually delivers cancellation. A client that leaves workers running without the required bounded contract fails acceptance rather than being certified by a happy path. Keep all host writes and model costs explicit; OAK cannot roll them back.

#### A12: Safe installation and complete generated native artifacts

The scenario delivers a valid ready agent TOML and a clearly labelled `codex/.codex/config.fragment.toml`, not a complete replacement user configuration. Generate the fragment's owned MCP policy values from the adaptor source. The installer resolves explicit absolute paths for the supplied Python, copied bundle, backend Codex binary, repository, and external host state, and writes a complete target-project `.codex/config.toml` entry plus `.codex/agents/oak-exploration.toml`. No unresolved placeholder or guessed machine path may remain in the installed result. Do not include credentials, global provider routing, user data, or a machine-specific generated file in Git.

`install.py` defaults to a no-write preview. Applying requires explicit approval of the exact destination and diff. Preserve unrelated config bytes, comments, agents, MCP servers, and protected settings. Use standard TOML parsing and one clearly delimited, owned MCP block rather than a generic configuration merger; reject unowned name collisions and ambiguous layouts. Repeated identical installation is a no-op. Updating or uninstalling checks expected owned content and records/restores only that content; user edits or concurrent drift stop the operation. Validate the final parsed configuration after the merge and keep a bounded external installation receipt. Never auto-trust a project, replace AGENTS, alter a global permission policy, enable unrelated agents/plugins, install dependencies, or commit installation state.

Set the owned enabled MCP server as required, filter it to `explore`, and choose explicit approval behavior that does not bypass the separately required host allowance. The backend inherits neither the caller's MCP configuration nor its transport credentials. Missing compatible Python/OAK/optional MCP/Codex dependencies, disabled native agents, an untrusted project, or a conflicting host configuration produce actionable preflight failure, not a silent user/global fallback. The native client must reload the configuration in a new session; the desktop route documents selecting Codex, Local mode, the intended primary folder, MCP restart/discovery, and the named entry. CLI uses an explicit working directory and verifies MCP discovery. Installation in an actual developer checkout is an authorized setup effect, separately fingerprinted before read-only acceptance begins.

#### A13: Native acceptance cannot be replaced by a headless demonstration

Require the E06 task through the installed entry once in Codex CLI and once in the ChatGPT desktop app's local Codex view. Use the same approved repository commit and a copied generated bundle. Record native agent discovery/selection, exact MCP tool invocation, request correlation, actual executor trace, worker overlap, validated final output, cited source, governing manifests, and cleanup. Compare invariants and source adequacy rather than exact stochastic wording. The native frontend and the independently installed backend may have different versions; record both.

Exercise missing/incorrect configuration, conflicting agent names, unsupported/Classic/wrong-view targets, stale bundle/tool identity, unauthorized input expansion, duplicate and simultaneous client requests, cancellation, and timeout. Most adversarial transport cases are offline; the native clients still need observed startup, invocation, and cancellation behavior. A screenshot alone proves neither backend execution nor enforcement. No CLI-only, VS Code, or app-server fixture can tick the desktop task. When direct desktop operation is unavailable, an explicitly identified human may run the exact checklist and supply correlated receipts; until then the desktop task stays open. Computer Use requires its own user authorization. The final verdict cannot be complete while either required client is unverified.

### Directory Changes

Baseline: product/source revision `9956e6998869fcfbd84067eec0d6303273a54174`, plus the already committed plan at `a9d2666cc4d71429c4c2769f9ad4b3a18cfceed6`. This is an affected-scope view, not an exhaustive repository inventory. The unimplemented prior proposals are not current files. Only this plan and the named native-client research record change in the present amendment; all product paths below remain intended implementation outcomes.
Legend: `[add]` new; `[modify]` existing content changes; `[move from PATH]` relocation; `[remove]` deleted path shown as a tombstone; `[keep]` relevant unchanged context; `[check]` inspect/regenerate and change only if required. No moves or removals of existing product files are planned here.
Current:
```text
open-agent-knowledge/
├── pyproject.toml                       # Current mandatory dependencies; no MCP extra
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
├── pyproject.toml                           # [modify] Optional Codex-host dependency
├── .agents/
│   ├── rules/
│   │   └── context.oak.md                       # [modify] Route Codex source knowledge
│   └── adaptors/                               # [add] Maintained host-support sources
│       └── codex/
│           ├── adaptor.oak.md                  # [add] Sole Codex knowledge/policy owner
│           ├── run.py                          # [add] Delivery-safe launcher/preflight
│           ├── transport.py                    # [add] Bounded app-server lifecycle
│           ├── tools.py                        # [add] Manifest-backed read capabilities
│           ├── contracts.py                    # [add] Protocol/request/result mappings
│           ├── serve.py                        # [add] Single-operation local MCP ingress
│           └── install.py                      # [add] Preview/apply/verify owned native files
├── examples/
│   ├── AGENTS.md                               # [modify] Bundle/tree authoring guidance
│   ├── catalog.py                              # [modify] Register scenario and samples
│   ├── catalog.oak.md                          # [modify] Regenerated catalogue/disclosures
│   ├── parallel_exploration/                   # [add] Maintained flat example authoring
│   │   ├── example.py                          # [add] Coordinator, ACT.tool, Par, Join
│   │   ├── example.oak.md                      # [add] Canonical source-scenario entry
│   │   ├── explorer.py                         # [add] One reusable worker source
│   │   ├── explorer.oak.md                     # [add] Canonical worker document
│   │   ├── codex_entry.py                      # [add] Native entry OAK source/metadata
│   │   ├── codex_entry.oak.md                  # [add] Canonical native invocation contract
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
│       ├── codex_native.py                     # [add] TOML/install/MCP/native contracts
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
│   │   │   ├── run.py                          # [add] Generated offline fixture runner
│   │   │   └── codex/                          # [add] Native Codex installation payload
│   │   │       ├── entry.oak.md                # [add] Exact native-entry OAK knowledge
│   │   │       └── .codex/
│   │   │           ├── agents/
│   │   │           │   └── oak-exploration.toml # [add] Ready native custom-agent definition
│   │   │           └── config.fragment.toml    # [add] Owned MCP merge input; not user config
│   │   └── adaptors/                           # [add] Shared live-host implementations
│   │       └── codex/
│   │           ├── adaptor.oak.md              # [add] From maintained Codex knowledge
│   │           ├── run.py                      # [add] Generated live launcher/preflight
│   │           ├── transport.py                # [add] Generated protocol implementation
│   │           ├── tools.py                    # [add] Generated restricted read tools
│   │           ├── contracts.py                # [add] Generated boundary validation
│   │           ├── serve.py                    # [add] Generated MCP entry to same executor
│   │           └── install.py                  # [add] Generated safe native installer
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
        └── evidence/                           # [add] Research now; observed receipts later
            └── native-clients-research.md       # [add now] Primary sources and conclusions
```
Ownership: `.agents/adaptors/codex/` owns maintained host implementation, not hand-edited outputs. Example Python sources own scenario documents and sample data; `build/agents.py` owns the generated bundle. `build/authoring_guides.py` and `build/authoring_platforms.py` own teaching composition from those sources. `examples/schemas/smeac_plan.py` owns the schema shape, while docs and examples AGENTS own prospective use and presentation. A08 and A10 through A12 list the complete ownership mappings. Native machine-specific `.codex` installation is an external authorized setup output, not a tracked source-directory addition. No extra runnable OAK scopes are fused together.
Verification: compare current entries with the pinned source inventory, then compare the implemented change set and generated manifests with this planned view. Expand any newly identified affected leaves before acceptance and reconcile conditional `[check]` paths without forcing gratuitous edits. The research filename above is known now. Runtime evidence filenames are not invented before observations exist; enumerate actual receipts in the completion report. The separate installation view below describes outputs on the explicitly approved target host. The expected tree is required by E09/E10 and is not a claim that products already exist.

#### Native installation destination

The copied bundle is a generated delivery. After separately approved installation, the selected target project receives this owned content; the existing user configuration is not replaced:
```text
target-project/
└── .codex/                                 # [add or modify] Explicit trusted project
    ├── agents/
    │   └── oak-exploration.toml            # [add] Exact generated native entry
    └── config.toml                        # [modify or add] Only owned MCP block
```
The real target path, pre-existing state, installed configuration values, and receipt are observed during setup. Neither this diagram nor a generated fragment proves installation or native discovery.

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
For each actual backend explorer, the A04 read registry is the only usable investigation capability; the native client entry is a separately described ingress, not that security boundary. Prohibited calls are refused before effects, unknown profiles refuse startup, and no worker can widen its own scope. Host transport/audit activity is disclosed separately.
Acceptance: directly exercise valid reads and denied writes, shell execution, installation, network/search, connector use, nested spawning, traversal, symlink escape, arbitrary Git flags, and permission expansion. Include missing/failed hooks, unexpected inherited configuration, and a native caller using broader live permissions; the latter must not change the backend profile. Enforcement cannot depend on a cooperative model. Record exact supported runtime/profile and negative-test receipts, with no claim of universal sandbox proof.

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
The Codex bridge preserves those semantics while bounding every worker and cleaning up its resources. The MCP ingress propagates cancellation/disconnect/deadline failure and cannot return a successful result before the validated OAK emission. A failed branch prevents successful synthesis/emission; diagnostic receipts remain explicitly diagnostic.
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
Deliver the exact `generated/oak.agents/` subtree shown in Directory Changes: the scenario owns its coordinator, explorer, sample, offline runner, and generated Codex entry/TOML/merge payload; sibling `adaptors/codex/` owns the knowledge and six narrow executable modules, including the MCP server and installer. Preserve the existing products. The scenario alone closes its OAK graph and offline fixture; the copied full bundle supplies the shared live adaptor, with external runtime, model, and inspected-repository requirements disclosed.
Acceptance: verify complete path/byte equality against source-owned generation, cold generation and repair, copied-scenario fixture execution, and copied-full-bundle preflight with source/build imports and implicit network blocked. Reject missing or stale documents/scripts, symlink/escape paths, undeclared sibling-scenario dependencies, and fallback reads of .agents or examples source. Run authorized live E06 through the delivered adaptor, not a source-only launcher. Exact delivered directory/entry names and scope separation must match; findings may vary. No root-hidden .agents installation, README index, or speculative empty provider directory is added. Native .codex installation is required by E11/E12 after explicit approval; it is not performed by generation or assumed from the bundle suffix.

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

#### E11: Ready native TOML and safe installation
Authority: required
Current state:
Checkpoint a9d2666 contains only a plan for a generated OAK bundle and app-server launcher. It explicitly excluded native agent installation; no native TOML, MCP server, merge fragment, or installer exists.
Desired state:
Generate A10/A12's `codex/entry.oak.md`, `.codex/agents/oak-exploration.toml`, and `.codex/config.fragment.toml` under the scenario, plus the shared `serve.py` and `install.py`. An explicitly approved installation yields a ready native agent and complete owned MCP configuration in the selected target project's `.codex` directory. The TOML's developer instructions decode to the exact OAK entry; no independently maintained prompt or hand-filled placeholder remains.
Acceptance: test TOML parsing and required metadata, OAK round-trip equality, exact source/delivery identity, agent/tool-name collisions, missing dependencies, unsafe paths, spaces/Unicode paths, preview with zero writes, idempotent apply, changed-config refusal, receipt integrity, owned update/removal, and preservation of unrelated comments/settings. A generated file not installed in a discovery location does not pass native installation. The config fragment must be labelled as merge input, never a replacement user config. Runtime setup remains separately authorized.

#### E12: Both requested native clients execute the same OAK workflow
Authority: required
Current state:
Neither a Codex CLI custom-agent invocation nor a ChatGPT desktop invocation of this capability has run. A Python launcher and an IDE example do not establish those native integrations.
Desired state:
```text
Codex CLI OR ChatGPT desktop app / Codex / Local
  -> installed oak-exploration native agent
  -> local OAK MCP explore operation
  -> OAK coordinator: Par -> Join -> synthesis -> validated emission
  -> completed native result with revision-bound evidence
```
The two parallel workers use the same explorer document and independent restricted app-server sessions. Native-client installation uses the copied generated bundle; no source-checkout fallback is available. The native entry is not described as a sandbox, and native child spawning does not replace OAK PAR.
Acceptance: run E06 separately in the actual CLI and desktop Codex view on the same approved commit, with discovered agent metadata, exact MCP tool identity, correlated client/backend receipts, genuine overlap, full governing context, source-checked findings, no prohibited effects, and bounded cleanup. Exercise missing/unsupported targets, authorization failure, broader parent permissions, duplicate/cross-client admission, cancellation and timeout through the native connection. Record app/CLI/backend/OS versions separately. Wrong views, ChatGPT Classic, VS Code, hosted browser execution, screenshots alone, fixtures, or CLI-only success cannot complete desktop acceptance. Missing UI access leaves the desktop task open with a named evidence operator and checklist, not an invented pass.

## 3. Execution

Intent: Deliver a useful exploration capability, not a new agent framework. Keep OAK contracts visible and make Codex's real capabilities and limitations testable. Preserve the user's flat authoring and explicit parallelism, and finish the generated bundle, native Codex CLI/ChatGPT desktop delivery, shared guidance, directory-change schema, and verification rather than stopping at a working launcher.
Concept of operations: Establish permission and delivery feasibility before broad implementation. Build the portable worker/coordinator and narrow host adapter, then prove offline boundaries before any authorized live run. Generate the portable bundle and shared authoring deliveries, update the reusable planning schema, install the native entry explicitly and exercise the real repository task through each requested client from the delivered bundle, and independently review the result against every required comparison and annotated path change.

### Phase 1: Establish compatibility and delivery gates
Objective: Confirm an executable foundation without weakening the approved design.
- [ ] Key task: P01.01 Restore the pinned governing graph, this amended plan and research record, branch/checkpoint, and exact implementation authorization; read affected sources and applicable standards before editing. Approval must include A01 through A13 and E01 through E12, not only the earlier 34-task scope.
- [ ] Key task: P01.02 Inspect the supplied Codex version, generated protocol schema, effective configuration, dynamic-tool support, and isolation facilities; record a version-specific capability matrix and refuse unsupported surfaces.
- [ ] Key task: P01.03 Prove the restricted profile with offline protocol/policy probes, including failed hooks and inherited capabilities; document host model-traffic and audit-write boundaries separately.
- [ ] Key task: P01.04 Assemble and measure a readable candidate for both new knowledge documents and both authoring deliveries; inventory retained knowledge and demonstrate a fit under existing byte limits without weakening safeguards.
- [ ] Key task: P01.05 Inspect installed native-agent discovery/schema contracts and exact MCP naming through no-model probes, client timeout/cancellation facilities, optional SDK range, target desktop view/OS, and actual UI evidence access. Record separate CLI, desktop-host, and backend versions and an executable native acceptance checklist; real product discovery and invocation remain Phase 6 checks.
Success criteria: A01 through A13 have concrete implementation paths on the named host; E03, E05, and E08 have concrete feasibility evidence, and E09 through E12 have explicit source/output ownership, schema evolution, native discovery/installation mappings, and separate acceptance operators. Record any installed-profile or UI evidence blocker instead of claiming compatibility. No hidden architectural substitution or scope expansion is needed. No live model call is implied by this gate.
Transition trigger: Capability and size gates both pass; otherwise retain an exact blocked checkpoint and obtain a specific scope decision before continuing.

### Phase 2: Author the worker and parallel coordinator
Objective: Express the actual workflow through current OAK contracts and flat Python sources.
- [ ] Key task: P02.01 Define complete local worker request/result schemas, evidence meanings, receive-trigger-process identity, native investigation ACT, and emitted result in the new scenario.
- [ ] Key task: P02.02 Define coordinator schemas and the two explicit request/result mappings to the same worker definition; keep host receipts distinguishable from model findings.
- [ ] Key task: P02.03 Implement E02's named ACT.tool actions, Par, Join, synthesis, and output interface; give both branches complete immutable-snapshot request bindings.
- [ ] Key task: P02.04 Register the scenario, source-owned sample.oak.md, complete local dependencies, canonical siblings, and detached fixture demonstration. Make the fixture runner accept an explicit entry path so source example.oak.md and delivered coordinator.oak.md need no literal-rewriting trick. Preserve existing examples and the four-stage core.
- [ ] Key task: P02.05 Author the small native-entry OAK document and metadata from A10, with complete local request/result contracts, the observed exact bridge target, and no backend scope transplant or alternate worker pool.
Success criteria: E01, E02, E07, E08, and E11 have passing structural, identity, dataflow, and detached fixture checks in both canonical groupings; no real Codex result is claimed yet.
Transition trigger: The complete scenario runs with honest deterministic hosts and preserves current executor semantics.

### Phase 3: Implement the restricted Codex adapter
Objective: Bridge OAK execution to actual Codex without granting the worker broad host authority.
- [ ] Key task: P03.01 Add the maintained pure OAK Codex adapter contract and its explicit context routing; implement the narrow stdio transport using the verified version-specific protocol.
- [ ] Key task: P03.02 Implement manifest-backed listing, bounded reads/search, revision inspection, and restricted diff, with path, byte, secret, symlink, and argument defenses.
- [ ] Key task: P03.03 Implement isolated startup, effective-profile checks, denied approvals/escalation, disabled ambient capabilities, full governing-context delivery, and host-owned audit receipts outside the repository.
- [ ] Key task: P03.04 Implement the Codex native interpreter, worker execute/arrival/emission lifecycle, two exact ToolContract registrations, validated result mappings, and no-tool synthesis interpreter.
- [ ] Key task: P03.05 Implement the delivery-safe launcher with explicit scenario, repository, commit, and external audit location; add bounded calls, timeout/interruption/cleanup, no automatic retries, and clear unavailable/unsupported/failed outcomes. It must run from the generated adaptor without imports or reads from the maintained source directories.
- [ ] Key task: P03.06 Implement A11's optional-SDK stdio MCP server, one validated exploration operation, host-bound authorization, interprocess admission/replay guards, complete result mapping, and bounded cancellation/disconnect handling into the same OAK executor.
- [ ] Key task: P03.07 Implement A12's generated-safe native installer: no-write preview, explicit destination/diff approval, validated TOML materialization, owned-block merge, idempotent content-checked update/removal, and external receipts without changing unrelated configuration or installing dependencies.
Success criteria: E01, E03, E07, E08, and E11 pass without network or a model through controlled protocol fixtures; ordinary imports, generation, and fixture execution require neither Codex nor credentials.
Transition trigger: The adapter is ready for adversarial offline verification; no live use occurs before its separate authorization gate.

### Phase 4: Verify boundaries and concurrency offline
Objective: Demonstrate controls independently of model cooperation and preserve the current parallel contract.
- [ ] Key task: P04.01 Add allowed-operation and prohibited-operation tests covering every E03 class, including direct requests rather than only model refusals.
- [ ] Key task: P04.02 Use synchronized/barrier-based tool fixtures to prove simultaneous dispatch, isolated inputs/results, same-snapshot use, JOIN ordering, and deterministic promotion independent of completion order.
- [ ] Key task: P04.03 Exercise E07 failure classes, duplicate/late events, protocol mismatch, denial, process termination, and bounded cleanup; require no final success emission on group failure.
- [ ] Key task: P04.04 Exercise E08 knowledge completeness, scope crossing, malicious file content, changed refs, and dirty-checkout disclosures; verify host-derived citations and read receipts against actual blobs.
- [ ] Key task: P04.05 Register adapter and scenario checks in build/checks/__init__.py for both existing complete verification entry points, keeping live model tests explicit and opt-in; do not create another test entry point.
- [ ] Key task: P04.06 Add offline MCP and native-installation tests for handshake/discovery, output schemas, actual registry mismatch, configuration collision/drift, no-model startup, disallowed request expansion, duplicate/cross-process calls, disconnect, timeout, cancellation, and no partial success; keep native real-client evidence distinct.
Success criteria: E11/E12's offline native contracts pass; E02, E03, E07, and E08 pass with substantive negative tests and no model dependency. Permission assertions, same-named fake tools, or a pair of sequential calls cannot satisfy the tests.
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
- [ ] Key task: P05.09 Generate the native OAK entry, complete agent TOML, labelled MCP merge fragment, shared MCP server/installer, and versioned setup/CLI/desktop instructions from their owners. Declare only the optional host dependency, cover both source and copied-bundle paths, and include the same new authoring knowledge in both authoring forms.
Success criteria: E04, E05, E09, E10, and E11 pass offline: both authoring forms contain the same new knowledge; the complete generated agent bundle works when copied away from source; required old content and behavior remain; byte limits hold; the updated SMEAC schema, guidance, and rejection checks agree; repeated generation is clean.
Transition trigger: Offline repository verification and shared delivery checks pass, and live acceptance is ready for explicit authorization.

### Phase 6: Run authorized live acceptance on OAK
Objective: Establish real Codex usefulness and concurrency without changing the repository.
- [ ] Key task: P06.01 Obtain or restore explicit authorization for the named model/provider, inspected commit, data disclosure, and bounded run budget; verify credentials without exposing them and recheck the effective profile.
- [ ] Key task: P06.02 Prepare a detached copied bundle, explicitly approved native installation, host authorization and immutable OAK snapshot. The two native runs below jointly supply E06 evidence: each executes two overlapping restricted workers and no-tool synthesis through the delivered code, never a privileged source-only launcher. Retain correlated receipts and source identities.
- [ ] Key task: P06.03 Run one separately labelled adversarial live probe and native cancellation probes in both clients within the approved budget in disposable scope; pair model refusals with direct offline denial evidence. Verify cancellation reaches the backend and that no prohibited effect or surviving process is hidden.
- [ ] Key task: P06.04 Review the findings against source, verify citations and coverage, reconcile disagreements, and compare snapshot/live-checkout content manifests without hiding external drift or uncertainty.
- [ ] Key task: P06.05 Invoke the installed oak-exploration entry from Codex CLI at the explicit target project; verify native discovery, MCP identity, full OAK execution, useful citations, overlap, parent/backend policy separation, and cleanup with actual client/backend correlation.
- [ ] Key task: P06.06 Invoke the same installed entry in the new ChatGPT desktop app's local Codex view using the intended primary project folder and MCP restart/discovery. Record actual app/OS and observer, correlate the backend run, and verify E12 including native stop/cancellation behavior; do not substitute VS Code or a headless run.
Success criteria: E01, E02, E03, E06, E07, E08, E09, E11, and E12 have real version-bound execution evidence in addition to fixture checks. Missing authorization, runtime, credentials, actual desktop observation, or completed model work leaves the corresponding live acceptance open, not skipped as passed.
Transition trigger: Live acceptance succeeds within the approved budget, or a precise blocked/failed checkpoint is retained without additional calls or silent retries.

### Phase 7: Verify and independently review the complete change
Objective: Confirm the delivered result against the original intent, not only implementation tests.
- [ ] Key task: P07.01 In an explicitly provisioned isolated environment including the declared optional host test dependencies, run compilation, affected generators including `python -m build.agents` and the SMEAC sibling generator, `python -m build.examples`, and `python build/examples.py` in the required isolated environment; rerun generation and require no diff.
- [ ] Key task: P07.02 Compare the actual final diff and complete generated path/byte manifests with the annotated Directory Changes view and A08 source mapping. Resolve omitted or misclassified paths, obsolete proposals, unnecessary files, all limits, scope-safe fusion, optional dependencies, and unchanged APS/history; report actual before/after trees separately from expected specimens.
- [ ] Key task: P07.03 Independently review A01 through A13 and E01 through E12 against the user's requests: useful evidence, genuine tool enforcement/concurrency, generated .agents packaging, self-contained scenarios, shared adaptors, detailed reusable directory-change planning, generated native TOML and safe installation, actual Codex CLI and ChatGPT desktop use without a weaker backend, preserved meaning, ownership, missing deliveries, and unnecessary machinery. Fix findings and repeat affected checks.
- [ ] Key task: P07.04 Complete the matching report with exact verified source/workspace identities, task evidence, limitations, changed paths, and final verdict; mark only evidenced tasks complete and create a PR only if authorized, with no merge.
Success criteria: Every required comparison E01, E02, E03, E04, E05, E06, E07, E08, E09, E10, E11, and E12 passes; the report separates inspected, executed, and verified results; independent review finds no material unresolved issue.
Transition trigger: Verified implementation is ready for the authorized review step; otherwise preserve remaining open tasks and the specific blocker.

### Coordinating Instructions
- Timeline: this is the 2026-09-07 research-led planning amendment for native Codex CLI and ChatGPT desktop delivery. Preserve earlier bundle/schema scope. No implementation deadline or unattended future work is promised; each authorized session records its achieved checkpoint.
- Boundaries: no core OAK syntax/runtime redesign, writable backend agents, automatic downloads, remote publishing, new CI workflow, alternate provider, recursive workers, or general scheduler. The SMEAC schema change, native TOML/config payload, local MCP ingress, and safe project installation are explicitly in scope. Native callers do not bypass the restricted backend. VS Code and ordinary Chat/Work integrations are not substitute deliverables.
- Operating guidelines: preserve exact source identities and full applicable instructions after context recovery; do not replay completed phases or assume that a newer main changes this plan's governing revision.
- Risk mitigation: enforce capabilities before effects, separate trusted receipts from untrusted findings, preserve immutable snapshots and contracts, refuse unclear context, and keep failure diagnostic rather than successful.
- Live budget: propose at most eleven backend Codex sessions for acceptance: two workers plus one synthesis per native client (six total), one adversarial worker probe, and two cancellation probes with at most two workers each and no synthesis (four total). Admit only one workflow across native clients and at most two backend workers concurrently. Retain 40 read calls per worker, 600 seconds per backend session, zero automatic retries, A11's 1,260-second overall deadline and 15-second cancellation cleanup, and a 1,500-second MCP timeout. Native parent/entry model work is additional cost, explicitly included in the user-approved total spend/token ceiling and recorded separately; backend session ceilings do not bound ambient client usage. No model/provider, data disclosure, or missing cost ceiling is inferred from installation or a read-only label. Freeze compatible context/result bounds at preflight without clipping governing knowledge.
- Verification: host-controlled timing intervals demonstrate overlap, not a speedup claim. Equivalent snapshots, meaningful source-backed findings, and denial behavior matter more than keyword matching. Do not represent a successful fixture as live inference.

### Contingencies
- If the installed Codex build cannot enforce the strict profile, then stop at the compatibility gate with the exact unsupported surface. Do not substitute prompt-only restrictions, a writable native child, another transport, or a patched Codex fork.
- If required shared knowledge cannot fit within existing byte limits, then present the measured overage and retained-content comparison for a scope decision. Do not silently increase limits or drop capabilities.
- If credentials, execution access, network, or live authorization are unavailable, then complete authorized offline work, retain open live tasks, and report the exact blocker without claiming end-to-end completion.
- If a worker fails, times out, or returns invalid evidence, then retain diagnostic receipts, interrupt and reap that worker, allow bounded group cleanup, and emit no successful synthesis. Any new attempt requires authorization consistent with the approved budget.
- If the source checkout changes, then retain the pinned snapshot and report drift. A request to inspect different content creates a new request/snapshot rather than silently altering an active run.
- If the copied agent bundle needs an undisclosed source checkout, sibling scenario, or unmaterialized machine configuration, then fix the delivery closure and rerun detached checks; do not redefine self-contained to conceal that dependency. Installed runtime/model access and the explicitly inspected repository remain declared external inputs.
- If native agent discovery, trusted-project configuration, exact tool naming, cancellation, or the ChatGPT desktop local Codex target cannot be verified, then retain the specific native task open. Do not substitute an IDE, silently bypass installation through the launcher, or mark desktop success from a screenshot or headless check.
- If installed configuration or owned agent content has changed, then stop update/removal and preserve user work. Reconcile with an explicit installation diff; never overwrite unrelated settings or silently move to personal/global configuration.
- If the final file set differs from the annotated tree, then reconcile the inventory and required comparisons before completion. A newly discovered material scope change requires approval; a diagram is not permission to add unnecessary files.
- If repository policy conflicts with the proposed scope, then stop and ask for the specific policy decision; do not reinterpret tests or local implementation as authority to relax it.

## 4. Admin and Logistics

| Resource | Quantity | Source | Status |
| --- | --- | --- | --- |
| Pinned repository knowledge and inspected source | One revision | GitHub at the baseline above | AVAILABLE |
| Planning branch and this document | One plan | User-authorized planning delivery | AVAILABLE |
| Executable checkout and isolated Python environment | One environment | Implementation host satisfying `pyproject.toml` and build policy | PENDING |
| Compatible backend Codex and protocol schema | One verified backend build | Explicitly supplied implementation host | PENDING |
| Native Codex CLI and ChatGPT desktop app / local Codex | Two observed clients | Supplied host and explicit desktop observer; no IDE substitute | PENDING |
| Native installation and local MCP SDK | One owned project installation | Generated native payload and optional host dependency | PENDING |
| Native-client primary-source research | One dated record | evidence/native-clients-research.md, R01 through R10 | AVAILABLE |
| Authorized provider/model credentials and run budget | One named configuration | User/host, never repository files | PENDING |
| Manifest-backed snapshot and restricted read registry | One snapshot per run | Adapter implementation | PENDING |
| Sanitized receipts and semantic review | Offline and live sets | Completion report and its evidence directory | PENDING |
| Copyable generated agent bundle and shared adaptor | One bundle, one initial scenario | build/agents.py from example/support source owners | PENDING |
| Annotated directory-change planning schema | One canonical SMEAC schema | examples/schemas/smeac_plan.py, docs owner, and plan checks | PENDING |

Supply: use existing repository dependencies where suitable; inspect standards, library documentation, and types before adding code or packages. Declare MCP in an optional Codex-host dependency group, pinning the supported range from evidence rather than installing an unchecked latest package. Keep Codex and that optional host group unnecessary for ordinary OAK import, generation, and existing fixture paths; keep live/SDK imports lazy. Full implementation verification uses an explicitly provisioned environment with the declared Codex-host extra to run every new offline MCP check; a missing extra blocks those checks rather than passing a skip. Downloads and installation require separate permission.
Transportation: maintain OAK schemas and documents as the authored knowledge; use Codex's own JSON-RPC and configuration formats only at the host boundary. Move exact validated results through the declared mappings and keep credentials and raw private runtime data out of committed evidence.
Sustainment: record runtime/protocol/profile identities, context coverage, sanitized tool events, deadlines, actual available usage data, and clear not-performed reasons. Keep maintained source separate from generated knowledge and executable deliveries, update the adapter's supported-version evidence when its host changes, and maintain the change-tree policy with its canonical SMEAC schema rather than platform memory.
Rollback: this amendment changes only the plan and supporting native-client research; all earlier commits remain. Native setup/update/removal is a separately authorized host effect with guarded receipts and preservation of unrelated configuration. Implementation corrections are new commits; never rewrite history or erase evidence. Read-only investigations have no repository edits to revert, but Codex requests, cost, host audit files, and external concurrent changes are not rolled back by OAK transactions.

## 5. Command and Signal

1. The user owns intent, implementation approval, native destination/install approval, live data/model/spend authorization, material scope changes, PR creation, and merge decisions.
2. The implementing assistant owns direct repository work, truthful checkpoints, contract-preserving execution, verification, and final review; bounded demonstration workers return evidence but gain no implementation authority.

| Channel | Medium | Purpose | Cadence |
| --- | --- | --- | --- |
| User conversation | Brief progress and decision messages | Report meaningful findings, blockers, authorization needs, and outcomes. | During substantial work and at gates. |
| This plan | Versioned Markdown | Retain scope, acceptance examples, open tasks, and continuation checkpoint. | At authorized phase transitions. |
| Completion report and evidence | Versioned sanitized receipts | Record actual checks, live/fixture distinctions, identities, limitations, and final verdict. | As observations are established. |

Reporting: planning readiness is not execution approval or implementation completion. Preserve the plan commit identity and governing revision on continuation; then record authorization and exact progress without fabricating a host lifecycle receipt.
Reporting: every completed task requires observed evidence, and E06/E12 require actual Codex results and separate native-client evidence. State separately what was inspected, executed, verified, assumed, blocked, or not performed.
Reporting: the planning session performed repository/documentation inspection and local structural/source-diff checks of the planning documents only. It did not execute the repository's verifier, launch Codex, install dependencies, change product files, or open a PR.

| Decision | Authority | Escalation |
| --- | --- | --- |
| Amend and commit plan/research on the existing branch | User's 2026-09-07T02:52:43Z research and native-client request, retaining the earlier packaging/schema intent | User for further material scope changes; preserve every earlier commit. |
| Implement the plan | User's explicit continuation for this plan revision | No implementation until received. |
| Run Codex and transmit source/context to its model service | User/host authorization for the named model, data, and budget | Block live acceptance if absent. |
| Install/update/remove native project files and MCP block | Explicit user consent for the shown destination and content diff | Keep preview-only if absent; never infer project trust or permission escalation. |
| Install/download dependencies or tools | Separate explicit user consent | Do not infer from planning, validation, or live-use requests. |
| Relax restrictions, size bounds, or language/ownership scope | User | Stop at the relevant gate. |
| Create a PR or merge | Explicit user authorization for that operation | Keep the branch unmerged otherwise. |

### Acknowledgement
The implementing assistant must acknowledge this exact plan and restore its complete governing knowledge before execution. The user's planning and amendment requests acknowledge the direction, not completion of the implementation or approval of a live run. The Directory Changes view is already populated here, but changing the SMEAC schema, product directories, generators, native integrations, and installed host files remains explicitly planned work. Research is complete for this design revision; implementation and native-runtime certification are not.
