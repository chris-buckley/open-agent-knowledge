# Native Codex clients: research and implementation decisions

Reviewed: 2026-09-07
Authority: Research supporting Plan 0016; the plan owns the accepted scope and gates.
Request: 2026-09-07T02:52:43Z, native Codex agent delivery for the ChatGPT desktop app and Codex CLI, not VS Code.
Repository baseline: `9956e6998869fcfbd84067eec0d6303273a54174`
Restored planning checkpoint: `a9d2666cc4d71429c4c2769f9ad4b3a18cfceed6`

## Method and evidence limits

Read current official OpenAI help and developer documentation before amending the plan. Followed redirects from developers.openai.com to learn.chatgpt.com and compared product migration, local/hosted execution, agent configuration, MCP, app-server, permissions, discovery, and release information. Inspected the existing OAK plan, governing owners, dependency declaration, execution contracts, and source/delivery map. Legacy APS remains design history, not evidence of current Codex support.

These are documentation observations and design conclusions, not installed-runtime certification. No Codex binary, native client, generated agent, permission profile, model invocation, MCP bridge, installer, or desktop UI was executed in this research. A TOML parse, documentation match, recorded version, or schema-valid result cannot substitute for the acceptance runs.

## Source register

### R01: The requested desktop product

Source: [Moving to the new ChatGPT desktop app](https://help.openai.com/en/articles/20001276).

Observation: The new desktop product includes Chat, Work, and a separate Codex view. The former Codex app updates into this product. The previous ChatGPT application can coexist as ChatGPT Classic. The views are not interchangeable execution environments.

Decision: Target the new ChatGPT desktop app's Codex view on a local project, plus Codex CLI. Record the actual app version, operating system, view, local mode, and selected project. Do not substitute Classic, ordinary Chat/Work, browser ChatGPT, an IDE extension, cloud execution, or a headless app-server test for desktop acceptance. A user on a different surface receives an explicit unsupported-target result, not an undocumented compatibility promise.

### R02: Native custom-agent files

Source: [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Observation: Local Codex discovers standalone TOML custom-agent definitions in project `.codex/agents/` or personal `~/.codex/agents/`. Required fields are `name`, `description`, and `developer_instructions`. These are spawned-session configuration layers, not a mechanism that automatically replaces the main conversation. The same page documents activity in the desktop and CLI and warns that live parent sandbox/approval overrides can be reapplied to children.

Decision: Generate `oak-exploration.toml` from a small OAK native-entry document. The name distinguishes the client entry from the actual restricted explorer. Do not export a second, weaker direct-native explorer or claim its TOML alone enforces restrictions. Keep the backend's independently controlled worker sessions. Require native discovery and invocation evidence in both clients; valid syntax alone is insufficient.

### R03: The local connection shared by the two targets

Source: [Model Context Protocol](https://learn.chatgpt.com/docs/extend/mcp).

Observation: Local Codex hosts support stdio MCP servers. The desktop app and CLI can share their host configuration, in user `config.toml` or trusted-project `.codex/config.toml`. Desktop settings expose MCP server addition/restart; CLI exposes MCP management and `/mcp`. Documented defaults include a 60-second tool timeout, per-server tool filters, and required-server startup failure.

Decision: Supply one local stdio OAK MCP server with one exploration operation. Set an explicit timeout longer than the bounded OAK workflow and require the enabled server. Do not interpret a per-server filter as a global native-tool allowlist. Discovery depends on the actual host and configuration scope; it is not implied by files sitting under generated.

### R04: Hosted ChatGPT is not this local connection

Source: [Developer mode and MCP apps in ChatGPT](https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt).

Observation: The hosted developer-mode integration discusses remote MCP servers rather than direct access to a local stdio process. Its account and workspace conditions should not be transplanted into local Codex configuration.

Decision: Keep this delivery local. It needs no public server, secure tunnel, plugin marketplace submission, remote deployment, or website. A future ordinary Chat/Work integration would require a separately researched and authorized contract. Do not silently broaden this task to obtain that different surface.

### R05: Configuration and discovery are layered

Sources: [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference), [Config basics](https://learn.chatgpt.com/docs/config-file/config-basic), and [Projects and chats](https://learn.chatgpt.com/docs/projects).

Observation: Project configuration requires trust, and some host/auth/provider settings cannot be overridden there. Codex CLI uses its selected working directory. Desktop project configuration and instruction discovery depend on the chosen local project; multi-folder discovery follows the primary folder, as also recorded in the [official changelog](https://learn.chatgpt.com/docs/changelog).

Decision: Install into an explicit target project, not automatically into the inspected checkout or a guessed home. Preserve unrelated configuration and require the user to establish project trust. Record CLI CWD, desktop primary folder, and effective configuration source. Credentials, provider routing, and user-specific absolute paths are installation/runtime inputs, never checked-in agent content. Reject stale or conflicting installations rather than overwriting user work.

### R06: Complete governing context needs its own proof

Source: [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

Observation: Automatic instruction loading follows a directory hierarchy and has a combined byte limit, 32 KiB by default. It does not establish that all applicable scoped OAK governing documents were delivered in full.

Decision: Preserve the plan's pinned, complete context manifests for the backend workers and restore them after any compaction. Installation must not replace repository AGENTS or silently raise a global instruction limit. The native entry contains its complete small OAK invocation contract; successful worker context validation remains independent of parent chat context.

### R07: App-server is the backend, not the native MCP entry

Source: [Codex App Server](https://learn.chatgpt.com/docs/app-server).

Observation: The app-server protocol supplies thread/turn lifecycle, structured output, interruption, and version-derived schemas. Client-supplied dynamic tools are experimental; `outputSchema` is turn-specific. Dynamic tools and config inspection do not in themselves prove that built-in capabilities have disappeared.

Decision: Retain one app-server stdio process per worker and the no-tool synthesis session. Generate and fingerprint the actual installed protocol schema. Validate startup, effective turn configuration, real tool exposure, and denials before accepting a build. The new MCP server calls OAK, which calls this backend; it is not an alternative Codex transport or a second scheduler. No model call occurs during ordinary import, generation, native-agent discovery, or MCP startup.

### R08: Permissions are not just one flag

Sources: [Permissions](https://learn.chatgpt.com/docs/permissions), [Agent approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security), [Hooks](https://learn.chatgpt.com/docs/hooks), and R02/R03/R07.

Observation: Local command permissions, hosted capabilities, MCP tool policy, configuration inheritance, and model-visible tool exposure are separate concerns. Hooks and metadata do not provide a universal guarantee. The documentation does not establish this project's required complete restricted profile on an arbitrary installed build.

Decision: Keep the existing compatibility gate open until implementation probes establish every required boundary. Inspect shell/unified/code execution, editing, search, plugins/apps, MCP, browser/computer use, delegation, installation, approval expansion, and configuration changes separately. Record absent versus advertised-but-denied tools honestly. Unknown reachable paths refuse startup. The frontend must never be described as an OS sandbox; its parent privileges do not become backend parameters.

### R09: Avoid the deprecated Codex MCP server

Sources: [Codex MCP server](https://learn.chatgpt.com/docs/mcp-server) and [official changelog](https://learn.chatgpt.com/docs/changelog).

Observation: OpenAI marks the `codex mcp-server` command deprecated in August 2026 and directs integrations toward app-server. The release log records CLI 0.153.4 on September 4. Its Git tag was resolved through the GitHub connector to `3d2ee51ca2d5db578f328aa75e20aa22c0197c9a`.

Decision: Our own `serve.py` is an OAK MCP bridge, not this deprecated command. The release is a research reference, not a required version blindly equated with an installed binary or the desktop's bundled host. Record and test frontend, backend, protocol, model, and operating-system identities separately. This research did not complete an audit of the released tool-dispatch implementation.

### R10: Use maintained protocol support

Source: [Build an MCP server](https://developers.openai.com/plugins/build/mcp-server).

Observation: OpenAI identifies the official Python SDK, published as `mcp`, and describes explicit input/output schemas, structured results, tool annotations, and handler authorization. Tool metadata is not an authorization receipt.

Decision: Keep MCP as an optional host dependency and use its maintained stdio server implementation rather than writing another protocol stack. Pin the supported SDK range from implementation evidence; install only with consent. Keep the ordinary OAK build and offline fixture paths independent of a Codex account. Do not add plugin UI, remote authentication infrastructure, or a general agent framework.

## Selected end-to-end design

```text
Codex CLI or ChatGPT desktop app / Codex / local project
  -> discovered oak-exploration.toml native entry
  -> one local OAK MCP exploration request
  -> OAK execute(coordinator), with validated input
       -> Par: agent.explore-runtime + agent.explore-contracts
            -> separate restricted Codex app-server workers
       -> Join
       -> no-tool synthesis, validation, and local emission
  -> bounded structured MCP result plus host receipt
  -> native entry returns the result to the parent conversation
```

The native entry's developer instructions are the losslessly serialized canonical OAK entry document, not a separately maintained prose prompt and not a fused coordinator/worker graph. The native entry selects the bridge; it does not pretend that native model spawning is OAK PAR. Backend worker sessions are independent of native-child inheritance. They may not appear as native child threads in the frontend UI, so show actual receipts rather than promise a UI topology the bridge does not provide.

The server binds repository root, allowed commit and paths, model, strict profile, audit directory, and budget from a human-authorized launch. Model arguments cannot select arbitrary roots, executables, credentials, transports, or permission profiles. Validate the complete request against that authorization before model work. Only one exploration operation per authorized installation may run at once, even across a CLI server and a desktop server; use a host-owned interprocess admission lock, not a queue. The admitted operation may run its two independent workers concurrently.

Use one blocking MCP call returning the completed result, with bounded progress notifications where supported. Do not add job polling, recursive workers, or success-shaped thread IDs. Pin an overall backend deadline and a larger MCP timeout. Cancellation, disconnect, tool timeout, and process shutdown must propagate to the backend supervisor; independently bounded worker deadlines remain the last defense. Test whether each actual native client delivers cancellation. A client that cannot meet the accepted cleanup contract is not certified by a successful happy path.

## Installation contract

Generate a ready agent definition and a clearly labelled configuration fragment beneath the scenario's `codex/.codex/` tree. The generated installer resolves explicit machine paths and merges only OAK's namespaced MCP configuration into the target `.codex/config.toml`; the fragment is not a replacement user config. The resulting installed configuration must be complete, valid, and contain no unresolved placeholders. The agent file is discoverable only after installation in the actual project's `.codex/agents/`.

The installer defaults to a no-write preview. Explicit application installs only the named entry and owned MCP block, preserves unrelated bytes/settings, records a receipt, and refuses unowned name collisions. A repeated identical installation is a no-op. Updating/removing owned material requires expected-content checks and retains user edits instead of deleting them. No automatic dependency installation, project trust, global policy change, config weakening, shell command assembled from model input, or repository commit occurs. Use standard TOML parsing and a small explicitly owned block; do not implement a generic configuration merger.

## Acceptance evidence still required

The amended plan must separately prove generated/installed bytes, native discovery, MCP initialization and exact tool identity, blocked unauthorized requests, actual OAK execution, live overlap, complete governing context, and useful citations. Run the agreed ACT investigation once from each requested native client through a copied generated bundle, using the same approved repository commit. Compare invariants and evidence, not stochastic prose equality.

Record client-visible invocation evidence and correlate it with backend request IDs, tool events, timestamps, fingerprints, and cleanup. A screenshot alone is not proof that the backend executed. A simulated transport or direct Python call is not evidence that desktop discovery worked. If direct UI tools are unavailable, an explicitly identified human can operate the desktop checklist and supply observed evidence; mark attribution and keep the task open until it is obtained. No VS Code substitute is allowed.

Documentation supports the chosen native discovery and local connection architecture. It does not certify the installed restriction profile or these end-to-end runs. Thus the plan can specify an executable implementation with explicit gates, but it must not mark either client's runtime acceptance complete before those observations exist.
