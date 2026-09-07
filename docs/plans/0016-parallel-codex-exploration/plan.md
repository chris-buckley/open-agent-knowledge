# Add restricted parallel Codex exploration

Prepared: 2026-09-07T12:09:23+10:00
Classification: PUBLIC
Readiness: Ready for implementation approval, with explicit compatibility and delivery-size gates.
Execution: Not started. Every implementation task remains open.
Authorization: The user requested this plan on 2026-09-07. This authorizes a planning branch and plan commit, not product implementation, live Codex calls, installation, a pull request, or a merge.
Branch: `docs/plan-parallel-codex-exploration`
Baseline and governing revision: `9956e6998869fcfbd84067eec0d6303273a54174`
Plan location: `docs/plans/0016-parallel-codex-exploration/plan.md`

## 1. Situation

### Operating Environment
OAK expresses portable knowledge and execution contracts; a host supplies models, tools, credentials, persistence, and effects. The proposed capability uses a real Codex interpreter to explore the OAK repository without changing it, with independent investigations dispatched through OAK's existing parallel tool actions.

### Current State
At the pinned baseline, `ACT.tool(...)` constructs an exact tool-backed action and renders as `ACT TOOL`; `Par` accepts independent exact tool actions with distinct output bindings, followed by `Join`. The existing delegation example dispatches `agent.reviewer` through `ToolContract`, but its worker uses deterministic fixture responses; the repository has no `.agents/adapters` directory. The authoring skill has brief delegation guidance, whereas the legacy APS snapshot contains dedicated subagent and platform-adapter material.

### Challenges
- Enforcement: a prompt, declared allowlist, read-only hint, or custom-agent default does not establish the worker's effective capabilities. Codex child sessions can inherit parent runtime overrides, and tool hooks have documented coverage and failure limitations.
- Host integration: OAK expects a tool result with declared bindings, not a spawned thread identifier. The adapter must own Codex session startup, tool dispatch, completion, validation, deadlines, and cleanup.
- Parallel meaning: both workers must inspect the same immutable snapshot; their reports remain isolated until JOIN. Existing PAR failure semantics must not become silent partial success.
- Context: full applicable governing documents and explicit OAK dependencies must be available without flattening their scope or trusting automatic AGENTS discovery to avoid truncation.
- Evidence: schema-valid text is not proof of a read, a rejected operation, overlapping execution, or a correct interpretation. Host observations and semantic review must remain distinct.
- Delivery size: the baseline standalone authoring artifact is 63,981 bytes against a 64,000-byte limit. Adding guidance and adapter knowledge requires a measured, meaning-preserving fit, not an assumed exception.

### Supporting Factors
- Higher intent: make OAK useful on its own repository while demonstrating exact tool use, restricted agents, parallel execution, and explicit orchestration contracts.
- Adjacent efforts: preserve flat Python authoring, self-contained examples, locally understandable public contracts, shared skill/agent generation, and the existing repository lifecycle.
- Supporting resources: the sources and governing owners below, the existing executor and example catalogue, the APS snapshot as historical design reference, and current official Codex documentation.

### Assumptions
- Codex means a real Codex runtime through its app-server protocol, not merely a model name or a deterministic substitute. Model selection and authentication remain explicit host choices.
- A compatible, already installed Codex runtime and authorized model access can be supplied for implementation acceptance. Their availability has not been established in this planning session.
- The first supported invocation is the repository launcher starting isolated Codex sessions. Native parent-to-child spawning and installation into `.codex/agents` are not the enforcement mechanism for this delivery.
- The initial workload is a fixed pair of independent investigations, not an unbounded agent pool or dynamically recursive delegation.
- The existing OAK language is sufficient. Product implementation does not require a new statement, part, alias language, permission keyword, or scheduler.

### Constraints and Limitations
- Constraint: change only this plan during planning. Preserve main and all original commits; do not amend, squash, rebase, force-push, merge, or delete branches.
- Constraint: use `ACT.tool(...)`, `Par(body=[...])`, and `Join()` in Python and their current canonical OAK renders. Keep meaningful definitions flat and named before assembly.
- Constraint: work directly without research subagents. Later authorization may permit only the bounded Codex demonstration workers described here, not unrestricted delegation by the implementing assistant.
- Constraint: retain OAK's host boundary, local worker state/interface ownership, explicit graph composition, exact tool names, and current transaction semantics.
- Constraint: the explorer has no usable editing, command execution, package installation, general web/network, connector, or worker-spawning capability. Model-service/authentication traffic is a separate, explicitly authorized host connection.
- Constraint: preserve the 500-line AGENTS limit, 10,000-byte skill-entry limit, 64,000-byte standalone-agent limit, validator identity and consent safeguards, literal teaching content, and scope-safe fusion.
- Constraint: keep repository support in `.agents`, example sources in their scenario, and generated product deliveries under the existing `generated` products. Add no directory README indexes or provider-specific skill-frontmatter fields.
- Constraint: retain APS as unchanged historical reference. Do not import its input/format syntax, USE/CAPTURE conventions, tool aliases, external task-config formats, or dated platform claims into OAK.
- Limitation: repository sources were inspected through GitHub. A pinned archive download failed because the container could not resolve `codeload.github.com`; there is no executable checkout in this planning session. Full repository checks and live Codex execution have not run.
- Limitation: the capability and size gates below can block implementation acceptance. A blocker must be reported specifically; it must not be hidden by weakening the agreed restrictions or redefining completion.

### Governing Knowledge and Source Record

The complete root and applicable scoped knowledge at the pinned revision govern this plan. Complete root text was already available in the conversation; main was checked again and still resolved to the same revision. Restoring the complete pinned texts takes priority after context loss. This is a new planning task, not a continuation of a previous implementation checkpoint.

| Owner or source | Relevance |
| --- | --- |
| `AGENTS.md` | Product purpose, lifecycle, approval, host trust, naming routing, and scoped ownership. |
| `.agents/rules/context.oak.md` | Read-only preparation and specialist routing. |
| `.agents/rules/repository-change.oak.md` | Planning-change naming and immutable Git history. |
| `docs/AGENTS.md`; `examples/schemas/smeac_plan.oak.md` | Numbered plan storage, compact phases, comparison authority, and evidence. |
| `oak/AGENTS.md`; `oak/node/AGENTS.md`; `oak/execute/AGENTS.md` | Host separation, canonical meaning, dataflow, exact tools, and PAR/JOIN semantics. |
| `examples/AGENTS.md`; `build/AGENTS.md` | Example ownership, generated delivery, fusion, limits, and verification. |
| `oak/authoring.py`; `oak/node/parts/processes/statements.py` | ACT helper and current Par/Join model contracts. |
| `oak/execute/actions.py` | Exact dispatch, concurrent invocation, result validation, and group failure. |
| `examples/delegation/example.py`; `examples/delegation/example.oak.md` | Existing typed coordinator/worker dispatch and deterministic host. |
| `examples/catalog.oak.md` | Current demonstrations and their honest host disclosures. |
| `build/authoring.py`; `build/authoring_guides.py`; `build/checks/plans.py` | Shared generation, supporting-document restrictions, routing, and plan structure checks. |
| `legacy-snapshot-aps/SKILL.md`; `legacy-snapshot-aps/guides/subagent-architecture-v1.0.0.guide.md` | Historical skill routing and bounded coordinator/worker ideas. |
| `legacy-snapshot-aps/platforms/README.md`; `legacy-snapshot-aps/platforms/generic/adaptor.md`; `legacy-snapshot-aps/platforms/claude-code/adaptor.md` | Historical adapter separation, contracts, tool registries, and permission mappings. |

Official Codex documentation inspected on 2026-09-07 is planning evidence, not proof of an installed runtime's behavior:

| Source | Relevant observation and design consequence |
| --- | --- |
| [App-server protocol](https://developers.openai.com/codex/app-server/) | Provides request/notification lifecycles, structured turn output, interruption, and experimental dynamic tools. Use a version-checked stdio adapter rather than parsing terminal prose. |
| [Configuration reference](https://developers.openai.com/codex/config-reference/) | Distinguishes command tooling, MCP tool filters, feature controls, and project instruction limits. Do not treat an MCP allowlist as a global capability filter. |
| [Subagents](https://developers.openai.com/codex/subagents/) | Describes custom-agent configuration and inherited live parent overrides. Start independent restricted sessions rather than relying on a writable parent's worker defaults. |
| [Hooks](https://developers.openai.com/codex/hooks/) | Covers many local tools but excludes hosted paths and warns against treating hooks as complete enforcement. Hooks may add defense and observations, not replace the primary boundary. |
| [Agent approvals and security](https://developers.openai.com/codex/agent-approvals-security) | Command sandbox/network policy does not govern all hosted capabilities. Disable or separately constrain every reachable surface. |

## 2. Mission

After explicit implementation approval, the implementing agent delivers and verifies a restricted Codex-backed OAK explorer and parallel coordinator for the OAK repository, together with reusable OAK orchestration and adapter guidance, so real tool use is useful, bounded, and evidenced.

Task: complete every approved phase in this branch before reporting implementation complete; create an implementation PR only when separately authorized.
Purpose: demonstrate portable OAK meaning driving a real host without confusing instructions, configuration, tool visibility, permission enforcement, and observed behavior.
End state: one reusable explorer definition serves two concurrent Codex sessions, OAK joins validated reports and synthesizes their evidence, prohibited operations cannot succeed, repository content is unchanged, and the generated skill and standalone agent teach the same contracts.

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

#### A08: One set of sources, explicit deliveries

| Path or owner | Planned responsibility |
| --- | --- |
| `examples/parallel_exploration/example.py` and sibling `example.oak.md` | Flat coordinator source and canonical render, including both tool-backed branches, JOIN, and synthesis. |
| `examples/parallel_exploration/explorer.py` and sibling `explorer.oak.md` | One reusable typed leaf worker, used by the example and the actual repository launcher; no separately maintained Codex prompt copy. |
| `examples/parallel_exploration/run.py` and source-owned sample fixtures | Detached deterministic contract demonstration with honest disclosure; no default live calls. |
| `examples/catalog.py`; `examples/catalog.oak.md` | Register the new scenario and its complete delivered graph without displacing the existing four-stage teaching core. |
| `.agents/adapters/codex/adaptor.oak.md` | Maintained pure OAK source for the Codex binding contract, capability policy, version evidence, installation/invocation meaning, and unsupported cases. Constants/schemas only where shared with authoring fusion. |
| `.agents/adapters/codex/run.py` | Explicit repository launcher and preflight; uses the same scenario documents on the selected OAK snapshot. |
| `.agents/adapters/codex/transport.py`, `tools.py`, `contracts.py` | Bounded app-server lifecycle, manifest-backed reads, and validated mappings. Keep these roles narrow; no provider-agnostic framework. |
| `build/authoring_guides.py`; a focused `build/authoring_platforms.py` | Own orchestration guide composition and transform the maintained adapter knowledge into generated teaching, without copying policy into another source. |
| `build/authoring.py`; `build/fusion.py` only if genuinely needed | Register shared knowledge in both deliveries, preserve supporting-document restrictions and literal payloads, and maintain exact fresh products. No generic fusion rewrite is presumed. |
| `generated/oak-authoring.skill/guides/subagent-orchestration.oak.md` | Generated portable orchestration guidance. |
| `generated/oak-authoring.skill/platforms/codex/adaptor.oak.md` | Generated Codex-specific knowledge, not a provider-specific SKILL frontmatter extension or an installed runtime. |
| `generated/oak-authoring.oak.md` | Contains the same new authoring knowledge through existing scope-safe fusion; the executable host code stays repository support. |
| `build/checks/codex_adapter.py`; existing authoring/example/generated checks; `build/examples.py` | Offline contract, permissions, protocol, parallelism, closure, and delivery checks through the established verification entry points. |
| `build/AGENTS.md`; `examples/AGENTS.md`; `.agents/rules/context.oak.md` | Record the new source/verification ownership, scenario disclosures, and explicit routing to adapter knowledge for host work. Do not expand root AGENTS or alter its lifecycle. |
| This plan; later `report.md` and `evidence/` | Checkpoints, observed acceptance receipts, source identities, and final review. |

The scenario owns portable executable examples; the Codex adapter owns host-specific implementation; build owns delivery. New adapter support remains under the existing root scope, with its exact owning knowledge explicitly routed rather than adding a schema-only AGENTS file. Generated platform knowledge is constants/schemas supporting authoring, not an operational explorer fused into the authoring agent. Preserve the shared source meaning and no-install authoring behavior.

The size gate is mandatory before broad product work: inventory candidate bytes, remove only demonstrated redundant representation or repeated explanatory prose through the correct owner, and compare retained knowledge and behavior. Do not strip examples, externalize required standalone knowledge, encode it opaquely, raise a limit, or hide an unrelated validator rewrite in this task. If a readable complete candidate cannot fit, stop for a specific scope decision; the plan does not pre-authorize a limit change.

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
The new guidance fits both existing limits while preserving required existing knowledge, literal teaching, validator trust/consent, and all current generated products. New code remains outside OAK core and the no-install authoring path.
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

## 3. Execution

Intent: Deliver a useful exploration capability, not a new agent framework. Keep OAK contracts visible and make Codex's real capabilities and limitations testable. Preserve the user's flat authoring and explicit parallelism, and finish the shared guidance and verification rather than stopping at a working launcher.
Concept of operations: Establish permission and delivery feasibility before broad implementation. Build the portable worker/coordinator and narrow host adapter, then prove offline boundaries before any authorized live run. Complete the shared authoring deliveries, exercise the real repository task, and independently review the result against every required comparison.

### Phase 1: Establish compatibility and delivery gates
Objective: Confirm an executable foundation without weakening the approved design.
- [ ] Key task: P01.01 Restore the pinned governing graph, this plan, branch/checkpoint, and exact implementation authorization; read affected source in full and applicable coding standards/specialist skills before editing.
- [ ] Key task: P01.02 Inspect the supplied Codex version, generated protocol schema, effective configuration, dynamic-tool support, and isolation facilities; record a version-specific capability matrix and refuse unsupported surfaces.
- [ ] Key task: P01.03 Prove the restricted profile with offline protocol/policy probes, including failed hooks and inherited capabilities; document host model-traffic and audit-write boundaries separately.
- [ ] Key task: P01.04 Assemble and measure a readable candidate for both new knowledge documents and both authoring deliveries; inventory retained knowledge and demonstrate a fit under existing byte limits without weakening safeguards.
Success criteria: A01 through A08 are executable on a named supported host; E03, E05, and E08 have concrete feasibility evidence, and no hidden architectural substitution or scope expansion is needed. No live model call is implied by this gate.
Transition trigger: Capability and size gates both pass; otherwise retain an exact blocked checkpoint and obtain a specific scope decision before continuing.

### Phase 2: Author the worker and parallel coordinator
Objective: Express the actual workflow through current OAK contracts and flat Python sources.
- [ ] Key task: P02.01 Define complete local worker request/result schemas, evidence meanings, receive-trigger-process identity, native investigation ACT, and emitted result in the new scenario.
- [ ] Key task: P02.02 Define coordinator schemas and the two explicit request/result mappings to the same worker definition; keep host receipts distinguishable from model findings.
- [ ] Key task: P02.03 Implement E02's named ACT.tool actions, Par, Join, synthesis, and output interface; give both branches complete immutable-snapshot request bindings.
- [ ] Key task: P02.04 Register the scenario, source-owned samples, local dependencies, canonical siblings, and detached fixture demonstration; preserve all existing examples and four-stage core teaching selection.
Success criteria: E01, E02, E07, and E08 have passing structural, identity, dataflow, and detached fixture checks in both canonical groupings; no real Codex result is claimed yet.
Transition trigger: The complete scenario runs with honest deterministic hosts and preserves current executor semantics.

### Phase 3: Implement the restricted Codex adapter
Objective: Bridge OAK execution to actual Codex without granting the worker broad host authority.
- [ ] Key task: P03.01 Add the maintained pure OAK Codex adapter contract and its explicit context routing; implement the narrow stdio transport using the verified version-specific protocol.
- [ ] Key task: P03.02 Implement manifest-backed listing, bounded reads/search, revision inspection, and restricted diff, with path, byte, secret, symlink, and argument defenses.
- [ ] Key task: P03.03 Implement isolated startup, effective-profile checks, denied approvals/escalation, disabled ambient capabilities, full governing-context delivery, and host-owned audit receipts outside the repository.
- [ ] Key task: P03.04 Implement the Codex native interpreter, worker execute/arrival/emission lifecycle, two exact ToolContract registrations, validated result mappings, and no-tool synthesis interpreter.
- [ ] Key task: P03.05 Implement the launcher, explicit commit selection, bounded calls, timeout/interruption/cleanup, no automatic retries, and clear unavailable/unsupported/failed outcomes.
Success criteria: E01, E03, E07, and E08 pass without network or a model through controlled protocol fixtures; ordinary imports, generation, and fixture execution require neither Codex nor credentials.
Transition trigger: The adapter is ready for adversarial offline verification; no live use occurs before its separate authorization gate.

### Phase 4: Verify boundaries and concurrency offline
Objective: Demonstrate controls independently of model cooperation and preserve the current parallel contract.
- [ ] Key task: P04.01 Add allowed-operation and prohibited-operation tests covering every E03 class, including direct requests rather than only model refusals.
- [ ] Key task: P04.02 Use synchronized/barrier-based tool fixtures to prove simultaneous dispatch, isolated inputs/results, same-snapshot use, JOIN ordering, and deterministic promotion independent of completion order.
- [ ] Key task: P04.03 Exercise E07 failure classes, duplicate/late events, protocol mismatch, denial, process termination, and bounded cleanup; require no final success emission on group failure.
- [ ] Key task: P04.04 Exercise E08 knowledge completeness, scope crossing, malicious file content, changed refs, and dirty-checkout disclosures; verify host-derived citations and read receipts against actual blobs.
- [ ] Key task: P04.05 Register adapter and scenario checks in the existing complete verification entry points, keeping live model tests explicit and opt-in.
Success criteria: E02, E03, E07, and E08 pass with substantive negative tests and no model dependency. Permission assertions, same-named fake tools, or a pair of sequential calls cannot satisfy the tests.
Transition trigger: All offline safety and contract checks pass on the implementation revision.

### Phase 5: Deliver orchestration and adapter guidance
Objective: Teach and distribute the working design from shared OAK sources.
- [ ] Key task: P05.01 Add the focused portable orchestration guide covering A07 and complete runnable before/after examples with exact ACT.tool and PAR/JOIN semantics.
- [ ] Key task: P05.02 Generate Codex adapter knowledge from its maintained owner, with dated source references, supported profile/transport, exact mappings, and honest unsupported cases.
- [ ] Key task: P05.03 Route both new documents from the authoring entry and include their same knowledge in the standalone agent; preserve constants/schema-only supporting fusion and literal examples.
- [ ] Key task: P05.04 Refresh build/example ownership, skill metadata/version and immutable validator fingerprints where required, generated paths/bytes, and detached closure checks without changing installation-consent behavior.
Success criteria: E04 and E05 pass: both delivered forms contain the same new knowledge, required old content and behavior remain, byte limits hold, and repeated generation is clean.
Transition trigger: Offline repository verification and shared delivery checks pass, and live acceptance is ready for explicit authorization.

### Phase 6: Run authorized live acceptance on OAK
Objective: Establish real Codex usefulness and concurrency without changing the repository.
- [ ] Key task: P06.01 Obtain or restore explicit authorization for the named model/provider, inspected commit, data disclosure, and bounded run budget; verify credentials without exposing them and recheck the effective profile.
- [ ] Key task: P06.02 Execute E06 with two overlapping restricted Codex workers and one no-tool synthesis, preserving actual messages/results, tool receipts, context identities, timestamps, and sanitized usage observations.
- [ ] Key task: P06.03 Run one separately labelled adversarial live probe in a disposable snapshot; pair any observed model refusal with direct offline denial evidence, and verify no prohibited effect or surviving process.
- [ ] Key task: P06.04 Review the findings against source, verify citations and coverage, reconcile disagreements, and compare snapshot/live-checkout content manifests without hiding external drift or uncertainty.
Success criteria: E01, E02, E03, E06, E07, and E08 have real version-bound execution evidence in addition to fixture checks. Missing authorization, runtime, credentials, or completed model work leaves live acceptance open, not skipped as passed.
Transition trigger: Live acceptance succeeds within the approved budget, or a precise blocked/failed checkpoint is retained without additional calls or silent retries.

### Phase 7: Verify and independently review the complete change
Objective: Confirm the delivered result against the original intent, not only implementation tests.
- [ ] Key task: P07.01 Run compilation, affected generators, `python -m build.examples`, and `python build/examples.py` in the required isolated environment; rerun generation and require no diff.
- [ ] Key task: P07.02 Review the final diff, full generated path/byte manifests, obsolete names, all limits, scope-safe fusion, optional dependency behavior, and unchanged APS/history.
- [ ] Key task: P07.03 Independently review A01 through A08 and E01 through E08 for useful evidence, genuine tool enforcement/concurrency, preserved meaning, ownership, missing deliveries, and unnecessary machinery; fix findings and repeat affected checks.
- [ ] Key task: P07.04 Complete the matching report with exact verified source/workspace identities, task evidence, limitations, changed paths, and final verdict; mark only evidenced tasks complete and create a PR only if authorized, with no merge.
Success criteria: Every required comparison E01, E02, E03, E04, E05, E06, E07, and E08 passes; the report separates inspected, executed, and verified results; independent review finds no material unresolved issue.
Transition trigger: Verified implementation is ready for the authorized review step; otherwise preserve remaining open tasks and the specific blocker.

### Coordinating Instructions
- Timeline: this is the 2026-09-07 planning delivery. No implementation deadline or unattended future work is promised; each authorized work session records its achieved checkpoint.
- Boundaries: no OAK syntax/runtime redesign, writable agents, automatic dependency downloads, remote publishing infrastructure, new CI workflow, alternative provider, recursive delegation, or unbounded scheduling.
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

Supply: use existing repository dependencies where suitable; inspect standards, library documentation, and types before adding code or packages. Keep Codex optional for importing, building, and testing OAK; downloads and installation require separate permission.
Transportation: maintain OAK schemas and documents as the authored knowledge; use Codex's own JSON-RPC and configuration formats only at the host boundary. Move exact validated results through the declared mappings and keep credentials and raw private runtime data out of committed evidence.
Sustainment: record runtime/protocol/profile identities, context coverage, sanitized tool events, deadlines, actual available usage data, and clear not-performed reasons. Keep maintained source separate from generated knowledge, and update the adapter's supported-version evidence when its host changes.
Rollback: planning adds only this document. Implementation corrections are new commits; never rewrite history or erase evidence. Read-only investigations have no repository edits to revert, but Codex requests, cost, host audit files, and external concurrent changes are not rolled back by OAK transactions.

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
| Create and commit this plan on its new branch | User request in this conversation | User if the requested scope changes. |
| Implement the plan | User's explicit continuation for this plan revision | No implementation until received. |
| Run Codex and transmit source/context to its model service | User/host authorization for the named model, data, and budget | Block live acceptance if absent. |
| Install/download dependencies or tools | Separate explicit user consent | Do not infer from planning, validation, or live-use requests. |
| Relax restrictions, size bounds, or language/ownership scope | User | Stop at the relevant gate. |
| Create a PR or merge | Explicit user authorization for that operation | Keep the branch unmerged otherwise. |

### Acknowledgement
The implementing assistant must acknowledge this exact plan and restore its complete governing knowledge before execution. The user's planning request acknowledges the direction, not completion of the implementation or approval of a live run.
