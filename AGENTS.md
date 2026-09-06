<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
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
build/AGENTS.md,"generators, generated products, authoring capability, validator identity, and verification"
examples/AGENTS.md,"practical authoring, naming, decomposition, examples, and sibling renders"
docs/AGENTS.md,"persistent plan creation, plan storage, and completion reports"
>>

agent-line-limit: 500

part-authoring-priority: ["schemas", "constants", "state", "interfaces", "triggers", "processes", "instructions"]

repository-rules: YAML<<
- Read the root and every routed AGENTS document that applies before inspecting or
  changing implementation files.
- Treat AGENTS hierarchy as host scoping and never as implicit OAK imports.
- Treat each scoped AGENTS document as the sole current owner of its named concern.
- Keep repository-development assistance in .agents and generated product deliveries
  in generated; use build/AGENTS.md for product ownership.
- Route every persistent repository plan through docs/AGENTS.md before creating it.
- Use schema.change-description and constant.change-naming-rules when naming work
  branches, commits, or pull requests.
- Apply constant.commit-history-rules when committing, updating branches, merging
  pull requests, or removing branch references.
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

change-type-meanings: CSV<<
type,meaning
feat,new capability or behavior
fix,correction of faulty behavior
refactor,internal restructuring that preserves behavior
perf,performance improvement
docs,"documentation, knowledge, or planning-only change"
test,verification coverage or test correction
build,build tooling or dependency change
ci,continuous integration configuration
chore,repository housekeeping
revert,reversal of an earlier change
>>

change-name-patterns: {"branch": "<TYPE>/<SUMMARY-AS-KEBAB-CASE>", "subject": "<TYPE>(<SCOPE>): <SUMMARY>", "sentence": "<IMPERATIVE_VERB> <OBJECT> [<NECESSARY_QUALIFIER>]"}

change-naming-rules: YAML<<
- Use only approved change types as branch prefixes, never platform, tool, or agent
  names.
- Select the type from schema.change-description using constant.change-type-meanings.
- Apply constant.change-name-patterns to work branches, authored commit subjects,
  and pull request titles. Name the actual change at the scope of that artifact.
- Derive the branch topic from the summary using lowercase words separated by single
  hyphens; put one slash after the type.
- Use a lowercase imperative verb, its object, and only a qualifier needed to identify
  the change. Omit vague summaries and a terminal period.
- Omit the scope and its parentheses from a subject when no useful scope is needed.
- Use ! immediately before the subject colon only for a breaking change, and explain
  the affected contract and migration in the body.
>>

commit-history-rules: YAML<<
- Preserve every original commit and its identity in repository history, including
  after a pull request is merged.
- Merge pull requests with a merge commit. Do not squash or rebase during merging.
- Make corrections and reversals as new commits. Do not amend, squash, rebase, or
  force-push away existing commits.
- Update a work branch from its destination by merging so both histories retain their
  original commits.
- Before deleting merged branch references, verify that the source branch tip is an
  ancestor of the destination branch. Retain the references if that check fails.
>>

coding-standard: ".agents/rules/coding-standards.oak.md"
</constants>

<schemas>
<schema id="change-description" name="Change Description" purpose="Describe one change for branch names, commit subjects, and pull request titles.">
Type: <TYPE>
Scope: <SCOPE>
Summary: <SUMMARY>

WHERE:
- <TYPE> is string; is one of `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `build`, `ci`, `chore`, `revert`; the kind of change.
- <SCOPE> is string; the affected repository area in lowercase kebab-case, empty when omitted.
- <SUMMARY> is string; is non-empty; an imperative verb followed by its object and any necessary qualifier.
</schema>

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
repository-task-requested(
  event="A repository task is requested.",
  source=interface.task-request,
  process=process.perform-repository-task,
)
branch-merged(event="A repository branch is merged.", process=process.clean-merged-branch)
</triggers>

<processes>
<process id="perform-repository-task" name="Perform task" input="schema.repository-task" output="schema.repository-result">
ACT Use <ROUTER> to select and read every scoped AGENTS document that applies to <PATHS> before changing implementation. (
  ROUTER=$constant.agent-router,
  PATHS=$PATHS,
)
ACT For Python work in <PATHS>, read <STANDARD> and its routed topic documents before implementation; apply these defaults after scoped repository contracts. (
  PATHS=$PATHS,
  STANDARD=$constant.coding-standard,
)
ACT Apply <PART_PRIORITY> to represent <TASK>; add authored instructions only after no structured OAK part can carry the meaning. (
  PART_PRIORITY=$constant.part-authoring-priority,
  TASK=$TASK,
)
ACT Apply <RULES> and <CONSTRAINTS> to choose one owner for each concern and implement the smallest complete change for <TASK>. (
  RULES=$constant.repository-rules,
  CONSTRAINTS=$CONSTRAINTS,
  TASK=$TASK,
)
ACT Use <SKILLS> to read matching specialist material before work on formats used by <PATHS>. (
  SKILLS=$constant.skill-router,
  PATHS=$PATHS,
)
ACT Update every affected source, example, output, and scoped AGENTS document for <TASK>, then remove obsolete paths and contracts. (
  TASK=$TASK,
)
ACT Run the complete verification process owned by build/AGENTS.md, inspect the final diff, and search for every replaced identifier, path, format, and contract. ()
ACT output="schema.repository-result": Produce <OUTCOME>, <EVIDENCE>, and <CHANGED_PATHS> for <TASK> under <COMMUNICATION>. (
  TASK=$TASK,
  COMMUNICATION=$constant.communication-contract,
) -> OUTCOME, EVIDENCE, CHANGED_PATHS
EMIT interface.task-result
</process>

<process id="clean-merged-branch" name="Clean branch">
ACT Apply <HISTORY> to delete the merged branch on the remote and locally after a successful merge. (
  HISTORY=$constant.commit-history-rules,
)
</process>
</processes>

<interfaces>
task-request RECEIVES schema.repository-task
task-result EMITS schema.repository-result
</interfaces>