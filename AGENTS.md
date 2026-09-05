<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and trigger facts omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each trigger is one fact group: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
owned-concern: "OAK product intent, repository-wide operating knowledge, and scoped AGENTS routing."

product-purpose: "Open Agent Knowledge is a portable standard for expressing knowledge as one compact validated unit."

agent-router: CSV<<
path,concern
oak/AGENTS.md,"package representation, syntax, parsing, rendering, vocabulary, surfaces, rules, and public API"
oak/node/AGENTS.md,"document, node, parts, values, schemas, and same-document validation"
oak/resolve/AGENTS.md,"target paths, loading, graph resolution, and cross-document contracts"
oak/execute/AGENTS.md,"arrivals, processes, tools, state, emissions, failures, and transactions"
build/AGENTS.md,"generators, checks, freshness, generated reference, and authoring prompt"
examples/AGENTS.md,"practical authoring, naming, decomposition, examples, and sibling renders"
outputs/AGENTS.md,generated artifacts and regeneration ownership
docs/AGENTS.md,accepted plans and completion reports as history
skills/AGENTS.md,"portable authoring capability, skill packaging, scope-safe fusion, and optional validator identity"
>>

agent-line-limit: 500

part-authoring-priority: ["schemas", "constants", "state", "interfaces", "triggers", "processes", "instructions"]

repository-rules: YAML<<
- Read the root and every routed AGENTS document that applies before inspecting or
  changing implementation files.
- Treat AGENTS hierarchy as host scoping and never as implicit OAK imports.
- Treat each scoped AGENTS document as the sole current owner of its named concern.
- Keep repository-development assistance in .agents and distributable skill products
  in skills.
- Do not create repository or directory README indexes.
- Update architecture, implementation, examples, and generated outputs in one pass
  when the concern requires them.
- Choose the smallest implementation that preserves every applicable contract.
- Delete obsolete names, paths, formats, contracts, and support material in the same
  task.
- Add compatibility only for an explicitly named contract and consumer.
- Store durable repository meaning in the owning AGENTS document rather than platform
  memory.
- Stop and ask the user when the active task conflicts with applicable repository
  knowledge.
- Do not split one requested product change into deferred phases.
- Show proposed architecture to the user before writing it unless the user approved
  it in the active task.
- Treat Agnostic Prompt Standard material as legacy reference rather than OAK source
  content.
- Use interpreter for the consumer of OAK knowledge, render for one document representation,
  and output for one generated artifact.
- Use existing dependencies before adding code or packages.
- Check library documentation and types before assuming that a capability is absent.
- Prefer maintained libraries when they reduce complexity or improve reliability.
- Make architectural decisions for the long term rather than as planned replacements.
- Apply a durable user correction to its owning AGENTS document before continuing.
- Write only confirmed information relevant to the owned concern and point to the
  exact owner instead of copying detail.
- Use no em dash or asterisk emphasis in repository documentation.
- Confirm every applicable repository contract before reporting completion.
>>

skill-router: CSV<<
topic,path
Pydantic,.agents/skills/pydantic-v2.12/SKILL.md
JSON Schema,.agents/skills/json-schema-2020-12/SKILL.md
JSON-LD,.agents/skills/json-ld/SKILL.md
>>

communication-contract: YAML<<
- Lead with the answer or outcome.
- Use short plain sentences.
- State uncertainty directly.
- Avoid jargon, filler, praise, and repetition.
>>
</constants>

<schemas>
<schema id="repository-task" name="Repository Task" purpose="Carry one requested repository change and its constraints.">
Task: <TASK>
Paths: <PATHS>
Constraints: <CONSTRAINTS>

WHERE:
- <TASK> is string; is non-empty; the requested repository outcome.
- <PATHS> is string; is non-empty; the affected or inspected repository paths.
- <CONSTRAINTS> is string; task-specific constraints, empty when none are supplied.
</schema>

<schema id="repository-result" name="Repository Result" purpose="Carry the completed repository outcome and verification evidence.">
Outcome: <OUTCOME>
Evidence: <EVIDENCE>
Changed paths: <CHANGED_PATHS>

WHERE:
- <OUTCOME> is string; is non-empty; the completed task outcome.
- <EVIDENCE> is string; is non-empty; the checks and review evidence.
- <CHANGED_PATHS> is string; the changed paths, empty for read-only work.
</schema>
</schemas>

<triggers>
trigger.repository-task-requested.event := "A repository task is requested."
trigger.repository-task-requested.source := interface.task-request
trigger.repository-task-requested.process := process.perform-repository-task

trigger.branch-merged.event := "A repository branch is merged."
trigger.branch-merged.process := process.clean-merged-branch
</triggers>

<processes>
<process id="perform-repository-task" name="Perform task" input="schema.repository-task" output="schema.repository-result">
ACT Use <ROUTER> to select and read every scoped AGENTS document that applies to <PATHS> before changing implementation. (ROUTER=$constant.agent-router, PATHS=$PATHS)
ACT Apply <PART_PRIORITY> to represent <TASK>; add authored instructions only after no structured OAK part can carry the meaning. (PART_PRIORITY=$constant.part-authoring-priority, TASK=$TASK)
ACT Apply <RULES> and <CONSTRAINTS> to choose one owner for each concern and implement the smallest complete change for <TASK>. (RULES=$constant.repository-rules, CONSTRAINTS=$CONSTRAINTS, TASK=$TASK)
ACT Use <SKILLS> to read matching specialist material before work on formats used by <PATHS>. (SKILLS=$constant.skill-router, PATHS=$PATHS)
ACT Update every affected source, example, output, and scoped AGENTS document for <TASK>, then remove obsolete paths and contracts. (TASK=$TASK)
ACT Run the complete verification process owned by build/AGENTS.md, inspect the final diff, and search for every replaced identifier, path, format, and contract. ()
ACT output="schema.repository-result": Produce <OUTCOME>, <EVIDENCE>, and <CHANGED_PATHS> for <TASK> under <COMMUNICATION>. (TASK=$TASK, COMMUNICATION=$constant.communication-contract) -> OUTCOME, EVIDENCE, CHANGED_PATHS
EMIT interface.task-result
</process>

<process id="clean-merged-branch" name="Clean branch">
ACT Delete the merged branch on the remote and locally after a successful merge. ()
</process>
</processes>

<interfaces>
task-request RECEIVES schema.repository-task
task-result EMITS schema.repository-result
</interfaces>