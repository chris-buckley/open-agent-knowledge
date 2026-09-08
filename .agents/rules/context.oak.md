<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
owned-concern: "Stateless repository knowledge preparation, specialist routing, and dependency assessment."

skill-router: CSV<<
topic,path
Pydantic,.agents/skills/pydantic-v2.12/SKILL.md
JSON Schema,.agents/skills/json-schema-2020-12/SKILL.md
JSON-LD,.agents/skills/json-ld/SKILL.md
>>

adaptor-router: {"Codex native agent artifacts": "build/authoring_resources/platforms/codex/adaptor.oak.md", "Claude native agent artifacts": "build/authoring_resources/platforms/claude/adaptor.oak.md"}

coding-standard: ".agents/rules/coding-standards.oak.md"
</constants>

<schemas>
<schema id="context-request" name="Context Request" purpose="Supply the repository task and paths for read-only context preparation.">
Task: <TASK>
Paths: <PATHS>

WHERE:
- <TASK> is string; is non-empty.
- <PATHS> is string; is non-empty.
</schema>
</schemas>

<processes>
<process id="read" name="Read knowledge" input="schema.context-request">
ACT Use <ROUTER> to read the root and every owning AGENTS document before inspecting or changing <PATHS> for <TASK>; read docs/AGENTS.md before creating any persistent plan. (
  ROUTER=$../../AGENTS.oak.md#constant.agent-router,
  TASK=$TASK,
  PATHS=$PATHS,
)
</process>

<process id="read-python-standard" name="Read standard" input="schema.context-request">
ACT For Python work in <PATHS>, read <STANDARD> and its routed topics before implementation; apply those defaults after scoped repository contracts. (
  PATHS=$PATHS,
  STANDARD=$constant.coding-standard,
)
</process>

<process id="read-specialist-skills" name="Read skills" input="schema.context-request">
ACT Use <SKILLS> and <ADAPTORS> to read the matching specialist and native-artifact knowledge before work on <PATHS>; adaptor paths provide knowledge, not executable host capabilities. (
  SKILLS=$constant.skill-router,
  ADAPTORS=$constant.adaptor-router,
  PATHS=$PATHS,
)
</process>

<process id="select-knowledge-parts" name="Select parts" input="schema.context-request">
ACT Apply <PRIORITY> to place the meaning of <TASK> in justified structured parts; author instructions only when no structured part can carry it. (
  PRIORITY=$../../AGENTS.oak.md#constant.part-authoring-priority,
  TASK=$TASK,
)
</process>

<process id="select-dependencies" name="Select dependencies" input="schema.context-request">
ACT Inspect existing dependencies for <TASK> before adding code or packages. Check library documentation and types before concluding a capability is absent; prefer maintained libraries when they reduce complexity or improve reliability. (
  TASK=$TASK,
)
</process>

<process id="prepare" name="Prepare context" input="schema.context-request">
CALL process.read-python-standard (TASK=$TASK, PATHS=$PATHS)
CALL process.read-specialist-skills (TASK=$TASK, PATHS=$PATHS)
CALL process.select-knowledge-parts (TASK=$TASK, PATHS=$PATHS)
CALL process.select-dependencies (TASK=$TASK, PATHS=$PATHS)
</process>
</processes>