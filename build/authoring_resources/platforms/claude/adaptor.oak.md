<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
owned-concern: "Claude Code native authoring artifacts, placement and evidence limits."

authoring-profile: {"name": "oak-authoring", "description": "Create, read, update or delete OAK; clarify intent only when useful.", "model": "inherit", "permissionMode": "default", "disallowedTools": ["Agent"]}

mapping: YAML<<
- Use one Markdown agent definition with exactly the authoring-profile frontmatter,
  then the identical complete standalone OAK body. No sibling instruction dependency,
  tools allowlist, skills preload, MCP registry or platform-specific behavior fork.
- 'Optional manual placement: project .claude/agents/oak-authoring.md or personal
  ~/.claude/agents/oak-authoring.md. Check collisions and project trust; no installation
  is performed. Claude Code can select the main-session definition using claude --agent
  oak-authoring.'
- Return guided views, full draft and next useful decision to the parent. Child AskUserQuestion
  is filtered; do not assume direct questioning, wait/poll, spawn children or silently
  drop prior state. Inherit model, use default permissions and disallow Agent as requested
  defaults. Parent live permission modes can override defaults.
- Host owns configured tools/MCP servers, transport, credentials, permissions, persistence
  and effects. Discovery is read-only within actual authority. Configuration and documentation
  do not prove availability or enforce universal isolation. Consumer requirements
  are separate from authoring-host tools.
- Native tests are offline format/body/fixture acceptance, not live certification,
  installation, model-performance evidence or supplied infrastructure.
>>

sources: {"checked": "2026-09-08", "subagents": "https://code.claude.com/docs/en/sub-agents", "mcp": "https://code.claude.com/docs/en/mcp", "skills": "https://agentskills.io/specification"}
</constants>
