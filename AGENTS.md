<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Conditions are typed trees; ALL, ANY, and NOT compose comparisons; ASSERT fails a false condition; FOREACH is sequential; WHILE tests before each bounded iteration; PAR outputs become visible only at JOIN.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
AS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.
Constants hold values that do not change while the knowledge runs.
State holds values that persist and can change while processes run.
Each trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.

Treat AGENTS hierarchy as host scoping, never implicit OAK imports; each scoped AGENTS document owns its named concern.
Keep repository development support in .agents and generated product deliveries in generated; use build/AGENTS.md for product ownership and create no repository or directory README indexes.
Use direct file edits unless the user explicitly requests Computer Use.
Stop and ask the user whenever an active task conflicts with applicable repository knowledge.
Keep durable, confirmed repository meaning in the owning AGENTS document, not platform memory; reference other owners instead of copying detail.
Apply a durable user correction to its owning AGENTS document before continuing; cancel and restart an active lifecycle if its scope or approved inputs change.
Treat Agnostic Prompt Standard material as legacy reference; use interpreter for the consumer, render for a representation, and output for a generated artifact.
Use no em dash or asterisk emphasis in repository documentation.
Use process.name-change for names and .agents/rules/repository-change.oak.md for authorised Git operations.
The host loads this document as constant.execution-source with explicit references mapped to this checkout, supplies globally unique task ids, serializes arrivals, and durably stores only successfully returned state under the host boundary owned by oak/AGENTS.md; these declarations are initial values, not a file to rewrite after each request.
Pin the resolved knowledge graph for each task and restore that graph with its checkpoint on resume; load changed governing documents only for a new task.
The host admits approval inputs only from actual user authorization for that exact task and proposal revision; preserve existing authorization and ask again only when the approved scope changes.
Host tools derive proposal and workspace revisions from exact content, including relevant uncommitted files and dependencies; a model-written revision or evidence string is not proof.
After failed native work, reconcile external effects before retrying; if the workspace differs from its stored revision, cancel and start a new task. Never replay completed phases.
</instructions>

<constants>
owned-concern: "OAK product intent, resumable repository tasks, and scoped AGENTS routing."

product-purpose: "Open Agent Knowledge is a portable standard for expressing knowledge as one compact validated unit."

execution-source: "repository/AGENTS.oak.md"

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

skill-router: CSV<<
topic,path
Pydantic,.agents/skills/pydantic-v2.12/SKILL.md
JSON Schema,.agents/skills/json-schema-2020-12/SKILL.md
JSON-LD,.agents/skills/json-ld/SKILL.md
>>

coding-standard: ".agents/rules/coding-standards.oak.md"

instruction-justification: "Host trust, persistent-state ownership, and global scope invariants apply across independent arrivals and cannot be owned by one action or payload schema."
</constants>

<state>
task-id AS .agents/rules/repository-task.oak.md#schema.task-checkpoint.TASK_ID: ""
task AS .agents/rules/repository-task.oak.md#schema.task-checkpoint.TASK: ""
paths AS .agents/rules/repository-task.oak.md#schema.task-checkpoint.PATHS: ""
constraints AS .agents/rules/repository-task.oak.md#schema.task-checkpoint.CONSTRAINTS: ""
phase AS .agents/rules/repository-task.oak.md#schema.task-checkpoint.PHASE: "idle"
proposal AS .agents/rules/repository-task.oak.md#schema.task-checkpoint.PROPOSAL: ""
proposal-revision AS .agents/rules/repository-task.oak.md#schema.task-checkpoint.PROPOSAL_REVISION: ""
working-revision AS .agents/rules/repository-task.oak.md#schema.task-checkpoint.WORKING_REVISION: ""
approved-revision AS .agents/rules/repository-task.oak.md#schema.task-checkpoint.APPROVED_REVISION: ""
verified-revision AS .agents/rules/repository-task.oak.md#schema.task-checkpoint.VERIFIED_REVISION: ""
evidence AS .agents/rules/repository-task.oak.md#schema.task-checkpoint.EVIDENCE: ""
changed-paths AS .agents/rules/repository-task.oak.md#schema.task-checkpoint.CHANGED_PATHS: ""
</state>

<triggers>
task-started(event="Task requested.", source=interface.task-request, process=process.start-task)
task-resumed(event="Task resumed.", source=interface.task-resume, process=process.resume-task)
task-decided(event="Task decided.", source=interface.task-approval, process=process.decide-task)
task-cancelled(event="Task cancelled.", source=interface.task-cancel, process=process.cancel-task)
status-requested(event="Task status.", source=interface.status-request, process=process.show-task)
name-requested(event="Name requested.", source=interface.name-request, process=process.name-change)
branch-update-requested(
  event="Branch update requested.",
  source=interface.branch-update,
  process=process.update-branch,
)
merge-requested(
  event="Merge requested.",
  source=interface.merge-request,
  process=process.merge-change,
)
branch-merged(
  event="Branch merged.",
  source=interface.merge-receipt,
  process=process.clean-merged-branch,
)
</triggers>

<processes>
<process id="start-task" name="Start task" input=".agents/rules/repository-task.oak.md#schema.repository-task">
CALL process.require-inactive-task ()
ASSERT $TASK_ID does not equal $state.task-id
  MESSAGE "Task identifiers must not be reused."
SET state.task-id = $TASK_ID
SET state.task = $TASK
SET state.paths = $PATHS
SET state.constraints = $CONSTRAINTS
SET state.proposal = ""
SET state.proposal-revision = ""
SET state.working-revision = ""
SET state.approved-revision = ""
SET state.verified-revision = ""
SET state.evidence = ""
SET state.changed-paths = ""
SET state.phase = "prepare"
CALL process.publish-progress ()
</process>

<process id="resume-task" name="Resume task" input=".agents/rules/repository-task.oak.md#schema.resume-request">
ASSERT $TASK_ID equals $state.task-id
  MESSAGE "Resume targets a different task."
ASSERT $PHASE equals $state.phase
  MESSAGE "Resume targets a stale or inactive checkpoint."
CALL process.read-scoped-knowledge ()
IF $PHASE equals "prepare":
  CALL process.prepare-task ()
ELSE:
  ASSERT ALL(
    $state.approved-revision does not equal "",
    $state.approved-revision equals $state.proposal-revision,
  )
    MESSAGE "The current proposal has no matching approval."
  CALL process.require-revision (EXPECTED_REVISION=$state.working-revision)
  IF $PHASE equals "implement":
    CALL process.implement-repository-task ()
  IF $PHASE equals "refresh":
    CALL process.refresh-repository-deliverables ()
  IF $PHASE equals "verify":
    CALL process.verify-repository-change ()
  IF $PHASE equals "report":
    CALL process.produce-repository-result ()
IF $state.phase does not equal "complete":
  CALL process.publish-progress ()
</process>

<process id="decide-task" name="Decide task" input=".agents/rules/repository-task.oak.md#schema.approval-decision">
ASSERT ALL($TASK_ID equals $state.task-id, $state.phase equals "awaiting-approval")
  MESSAGE "No matching task is awaiting approval."
ASSERT $PROPOSAL_REVISION equals $state.proposal-revision
  MESSAGE "Approval targets a stale proposal."
IF $APPROVED equals true:
  CALL process.require-revision (EXPECTED_REVISION=$state.working-revision)
  SET state.approved-revision = $PROPOSAL_REVISION
  SET state.phase = "implement"
ELSE:
  SET state.approved-revision = ""
  SET state.phase = "cancelled"
CALL process.publish-progress ()
</process>

<process id="cancel-task" name="Cancel task" input=".agents/rules/repository-task.oak.md#schema.task-handle">
ASSERT $TASK_ID equals $state.task-id
  MESSAGE "Cancellation targets a different task."
ASSERT NOT(
  ANY($state.phase equals "idle", $state.phase equals "complete", $state.phase equals "cancelled"),
)
  MESSAGE "Only an active task can be cancelled."
SET state.approved-revision = ""
SET state.phase = "cancelled"
CALL process.publish-progress ()
</process>

<process id="show-task" name="Show task" input=".agents/rules/repository-task.oak.md#schema.task-handle">
ASSERT $TASK_ID equals $state.task-id
  MESSAGE "Status targets a different task."
CALL process.publish-progress ()
</process>

<process id="publish-progress" name="Publish progress">
EMIT interface.progress (
  TASK_ID=$state.task-id,
  PHASE=$state.phase,
  PROPOSAL_REVISION=$state.proposal-revision,
  PROPOSAL=$state.proposal,
)
</process>

<process id="read-scoped-knowledge" name="Read knowledge">
ACT Use <ROUTER> to read the root and every owning AGENTS document before inspecting or changing <PATHS> for <TASK>; read docs/AGENTS.md before creating any persistent plan. (
  ROUTER=$constant.agent-router,
  TASK=$state.task,
  PATHS=$state.paths,
)
</process>

<process id="prepare-task" name="Prepare task">
CALL process.read-python-standard ()
CALL process.read-specialist-skills ()
CALL process.select-knowledge-parts ()
CALL process.select-dependencies ()
CALL process.observe-revision () -> OBSERVED_REVISION
ACT output=".agents/rules/repository-task.oak.md#schema.task-proposal": Prepare one complete, read-only proposal for <TASK> within <PATHS> and <CONSTRAINTS>, identifying each owner and required source, example, output and verification change. Choose the smallest complete long-term design, not deferred product phases or planned replacements. Include only explicitly named compatibility contracts and consumers. Have host tools derive <PROPOSAL_REVISION> from <TASK_ID>, these inputs, <OBSERVED_REVISION> and the exact <PROPOSAL>; publish the architecture before implementation. (
  TASK_ID=$state.task-id,
  TASK=$state.task,
  PATHS=$state.paths,
  CONSTRAINTS=$state.constraints,
  OBSERVED_REVISION=$OBSERVED_REVISION,
) -> PROPOSAL, PROPOSAL_REVISION
CALL process.require-revision (EXPECTED_REVISION=$OBSERVED_REVISION)
SET state.proposal = $PROPOSAL
SET state.proposal-revision = $PROPOSAL_REVISION
SET state.working-revision = $OBSERVED_REVISION
SET state.phase = "awaiting-approval"
</process>

<process id="read-python-standard" name="Read standard">
ACT For Python work in <PATHS>, read <STANDARD> and its routed topics before implementation; apply those defaults after scoped repository contracts. (
  PATHS=$state.paths,
  STANDARD=$constant.coding-standard,
)
</process>

<process id="read-specialist-skills" name="Read skills">
ACT Use <SKILLS> to read the matching specialist material before work on formats used by <PATHS>. (
  SKILLS=$constant.skill-router,
  PATHS=$state.paths,
)
</process>

<process id="select-knowledge-parts" name="Select parts">
ACT Apply <PRIORITY> to place the meaning of <TASK> in justified structured parts; author instructions only when no structured part can carry it. (
  PRIORITY=$constant.part-authoring-priority,
  TASK=$state.task,
)
</process>

<process id="select-dependencies" name="Select dependencies">
ACT Inspect existing dependencies for <TASK> before adding code or packages. Check library documentation and types before concluding a capability is absent; prefer maintained libraries when they reduce complexity or improve reliability. (
  TASK=$state.task,
)
</process>

<process id="observe-revision" name="Observe revision" output=".agents/rules/repository-task.oak.md#schema.revision-reading">
ACT output=".agents/rules/repository-task.oak.md#schema.revision-reading": Use host tools to fingerprint the actual <PATHS> and their relevant dependencies, including governing knowledge and uncommitted content. Return the same <OBSERVED_REVISION> for unchanged content. (
  PATHS=$state.paths,
) -> OBSERVED_REVISION
</process>

<process id="require-revision" name="Check revision" input=".agents/rules/repository-task.oak.md#schema.expected-revision">
CALL process.observe-revision () -> OBSERVED_REVISION
ASSERT $OBSERVED_REVISION equals $EXPECTED_REVISION
  MESSAGE "The workspace changed; reconcile effects before retrying preparation or starting a new task."
</process>

<process id="implement-repository-task" name="Implement task">
ACT output=".agents/rules/repository-task.oak.md#schema.change-receipt": Implement the complete approved <PROPOSAL> for <TASK_ID> under <CONSTRAINTS> in <PATHS>. Preserve unrelated work; use the smallest implementation that satisfies every applicable contract and do not defer part of the requested product change. Use the stable operation identity <TASK_ID> plus implement to reconcile any prior external effects before retrying. Return the host-observed final <REVISION> and complete <CHANGED_PATHS>. (
  TASK_ID=$state.task-id,
  PROPOSAL=$state.proposal,
  PATHS=$state.paths,
  CONSTRAINTS=$state.constraints,
) -> REVISION, CHANGED_PATHS
CALL process.require-revision (EXPECTED_REVISION=$REVISION)
SET state.working-revision = $REVISION
SET state.changed-paths = $CHANGED_PATHS
SET state.phase = "refresh"
</process>

<process id="refresh-repository-deliverables" name="Refresh deliverables">
ACT output=".agents/rules/repository-task.oak.md#schema.change-receipt": Complete every affected architecture record, source, example, generated output and scoped AGENTS update for <TASK_ID> and <TASK> under <PROPOSAL>. Remove obsolete names, paths, formats, contracts and support material in this task. Record durable validated lessons with their exact owners. Reconcile prior effects using <TASK_ID> plus refresh; return the observed <REVISION> and complete <CHANGED_PATHS>, including <PRIOR_PATHS>. (
  TASK_ID=$state.task-id,
  TASK=$state.task,
  PROPOSAL=$state.proposal,
  PRIOR_PATHS=$state.changed-paths,
) -> REVISION, CHANGED_PATHS
CALL process.require-revision (EXPECTED_REVISION=$REVISION)
SET state.working-revision = $REVISION
SET state.changed-paths = $CHANGED_PATHS
SET state.phase = "verify"
</process>

<process id="verify-repository-change" name="Verify change">
ACT output=".agents/rules/repository-task.oak.md#schema.verification-receipt": Run the complete verification process owned by build/AGENTS.md for <TASK_ID>, inspect the final diff, search for replaced identifiers, paths, formats and contracts, and check the <LIMIT> line bound. Return observed <EVIDENCE>, the exact verified <REVISION>, and whether every applicable check <PASSED>. (
  TASK_ID=$state.task-id,
  LIMIT=$constant.agent-line-limit,
) -> REVISION, EVIDENCE, PASSED
ASSERT $PASSED equals true
  MESSAGE "Required verification checks did not pass."
ASSERT $REVISION equals $state.working-revision
  MESSAGE "Verification does not cover the current checkpoint."
CALL process.require-revision (EXPECTED_REVISION=$REVISION)
SET state.verified-revision = $REVISION
SET state.evidence = $EVIDENCE
SET state.phase = "report"
</process>

<process id="produce-repository-result" name="Produce result">
ASSERT ALL(
  $state.verified-revision equals $state.working-revision,
  $state.evidence does not equal "",
)
  MESSAGE "Completion requires evidence for the current revision."
ACT output=".agents/rules/repository-task.oak.md#schema.task-outcome": Produce <OUTCOME> for completed <TASK> from observed <EVIDENCE> and <CHANGED_PATHS>. Lead with the outcome, use short plain sentences, state uncertainty directly, and avoid jargon, filler, praise and repetition. Compose only the response; do not change repository files. (
  TASK=$state.task,
  EVIDENCE=$state.evidence,
  CHANGED_PATHS=$state.changed-paths,
) -> OUTCOME
CALL process.require-revision (EXPECTED_REVISION=$state.verified-revision)
SET state.phase = "complete"
EMIT interface.task-result (
  TASK_ID=$state.task-id,
  OUTCOME=$OUTCOME,
  EVIDENCE=$state.evidence,
  CHANGED_PATHS=$state.changed-paths,
)
</process>

<process id="name-change" name="Name change" input=".agents/rules/repository-change.oak.md#schema.change-description" output=".agents/rules/repository-change.oak.md#schema.change-name">
CALL .agents/rules/repository-change.oak.md#process.name-change (
  TYPE=$TYPE,
  SCOPE=$SCOPE,
  SUMMARY=$SUMMARY,
  BREAKING=$BREAKING,
  MIGRATION=$MIGRATION,
) -> BRANCH, SUBJECT, BODY
EMIT interface.name-result
</process>

<process id="require-inactive-task" name="Check inactivity">
ASSERT ANY(
  $state.phase equals "idle",
  $state.phase equals "complete",
  $state.phase equals "cancelled",
)
  MESSAGE "Finish or cancel the active task before starting another task or independent Git operation."
</process>

<process id="update-branch" name="Update branch" input=".agents/rules/repository-change.oak.md#schema.branch-targets">
CALL process.require-inactive-task ()
CALL .agents/rules/repository-change.oak.md#process.update-branch (
  REMOTE=$REMOTE,
  SOURCE=$SOURCE,
  DESTINATION=$DESTINATION,
)
</process>

<process id="merge-change" name="Merge change" input=".agents/rules/repository-change.oak.md#schema.branch-targets">
CALL process.require-inactive-task ()
CALL .agents/rules/repository-change.oak.md#process.merge-change (
  REMOTE=$REMOTE,
  SOURCE=$SOURCE,
  DESTINATION=$DESTINATION,
)
</process>

<process id="clean-merged-branch" name="Clean branch" input=".agents/rules/repository-change.oak.md#schema.branch-targets">
CALL process.require-inactive-task ()
CALL .agents/rules/repository-change.oak.md#process.clean-merged-branch (
  REMOTE=$REMOTE,
  SOURCE=$SOURCE,
  DESTINATION=$DESTINATION,
)
</process>
</processes>

<interfaces>
task-request RECEIVES .agents/rules/repository-task.oak.md#schema.repository-task
task-resume RECEIVES .agents/rules/repository-task.oak.md#schema.resume-request
task-approval RECEIVES .agents/rules/repository-task.oak.md#schema.approval-decision
task-cancel RECEIVES .agents/rules/repository-task.oak.md#schema.task-handle
status-request RECEIVES .agents/rules/repository-task.oak.md#schema.task-handle
progress EMITS .agents/rules/repository-task.oak.md#schema.task-progress
task-result EMITS .agents/rules/repository-task.oak.md#schema.repository-result
name-request RECEIVES .agents/rules/repository-change.oak.md#schema.change-description
name-result EMITS .agents/rules/repository-change.oak.md#schema.change-name
branch-update RECEIVES .agents/rules/repository-change.oak.md#schema.branch-targets
merge-request RECEIVES .agents/rules/repository-change.oak.md#schema.branch-targets
merge-receipt RECEIVES .agents/rules/repository-change.oak.md#schema.branch-targets
</interfaces>