<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
owned-concern: "Codex native artifacts, placement, and evidence limits."

native-defaults: {"sandbox_mode": "read-only", "approval_policy": "never", "web_search": "disabled", "agents": {"enabled": false}}

authoring-profile: {"name": "oak-authoring", "description": "Create, read, update or delete OAK; clarify intent only when useful.", "agents": {"enabled": false}}

mapping: YAML<<
- TOML requires name, description and developer_instructions. Embed complete canonical
  worker OAK verbatim, with no external instruction file.
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
>>

sources: {"checked": "2026-09-08", "subagents": "https://learn.chatgpt.com/docs/agent-configuration/subagents", "configuration": "https://learn.chatgpt.com/docs/config-file/config-reference", "mcp": "https://learn.chatgpt.com/docs/extend/mcp?surface=cli"}
</constants>
