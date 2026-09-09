<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
owned-concern: "Codex native artifacts, placement, and evidence limits."

native-defaults: {"sandbox_mode": "read-only", "approval_policy": "never", "web_search": "disabled", "agents": {"enabled": false}}

authoring-profile: {"name": "oak-authoring", "description": "Create, read, update or delete OAK; clarify intent only when useful.", "agents": {"enabled": false}}

native-file-template: TEXT<<
name = <TOML_NAME>
description = <TOML_DESCRIPTION>
developer_instructions = <TOML_OAK_BODY>

[agents]
enabled = false
>>

mapping: YAML<<
- A Codex agent file is a complete TOML document, not Markdown with YAML frontmatter
  or a bare OAK file. Required top-level string fields are name (the registered agent
  identity), description (selection guidance), and developer_instructions (the complete
  canonical OAK body). Serialize the body as a TOML string and verify lossless decoding;
  do not substitute OAK constants for native TOML metadata or depend on a sibling
  instruction file.
- Write top-level metadata before the [agents] table; later keys belong to that table.
  The authoring-profile supplies name, description and agents.enabled=false. Generation
  supplies the complete developer_instructions value. An omitted model or reasoning
  setting resolves from explicit spawn values, then agents defaults, then the parent.
  Other omitted session settings inherit from the parent, subject to live overrides.
- Copy oak-explorer.toml manually to project .codex/agents/ or personal ~/.codex/agents/.
  Check collisions and project trust. Generation neither installs nor edits client
  configuration.
- Use Codex CLI or local Codex in ChatGPT desktop, not hosted Chat/Work. Clients choose
  models, credentials and omitted settings.
- Defaults enforce no universal tool allowlist. Parent live sandbox/approval overrides
  may replace them; inherited connectors remain host-controlled.
- The parent can request two independent oak-explorer instances and reconcile completed
  reports. Fixture tool names are not Codex built-ins; native prompting proves no
  OAK executor PAR/JOIN execution.
- Artifact checks cover content and closure, not installation, discovery, permissions
  or live behavior. This bundle supplies no host scripts.
- Authoring uses oak-authoring.toml in those same local agent directories, with exactly
  name, description, developer_instructions and agents.enabled=false. Inherit model,
  sandbox, approval, web and tool settings; do not reuse the explorer read-only profile
  for authoring.
- Embed the identical complete standalone authoring body, never a sibling file or
  another prompt. Return the full draft, current views and next decision to the parent;
  do not wait, spawn children or assume a direct-question tool. Configured no-delegation
  defaults are not enforcement evidence.
- Use only configured authoring-host tools within actual permission. Consumer tool/MCP
  requirements have separate identities and evidence; local MCP configuration belongs
  to the client/host. Do not provision servers, accounts or connectors. Do not invent
  a Codex launch flag.
- A repository copy under .agents/agents is not automatically registered. When the
  user requests a symlink, link the complete native TOML into .codex/agents, never
  rename or link bare OAK as TOML. Verify that the installed client follows the link
  and discovers the expected name. Installation links do not relax the build rules
  that reject symlinked source resources or generated outputs.
- Use a symlink-capable Git checkout for repository registration links. Verify that
  the link opens as readable TOML; resolving its target alone does not prove read-through.
- 'native-file-template is inert format guidance: replace each TOML_* marker with
  one properly encoded TOML string. Outer TOML assignments contain actual metadata
  and the entire OAK body; placeholders inside inert teaching constants remain literal.
  Codex reads the name field as identity; matching the filename to it is a convention.'
>>

sources: {"checked": "2026-09-09", "subagents": "https://learn.chatgpt.com/docs/agent-configuration/subagents", "configuration": "https://learn.chatgpt.com/docs/config-file/config-reference", "mcp": "https://learn.chatgpt.com/docs/extend/mcp?surface=cli"}
</constants>
