<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
owned-concern: "Codex native artifacts, placement, and evidence limits."

native-defaults: {"sandbox_mode": "read-only", "approval_policy": "never", "web_search": "disabled", "agents": {"enabled": false}}

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
>>

sources: {"checked": "2026-09-07", "subagents": "https://learn.chatgpt.com/docs/agent-configuration/subagents", "configuration": "https://learn.chatgpt.com/docs/config-file/config-reference"}
</constants>
