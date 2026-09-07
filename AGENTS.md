<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Conditions are typed trees; ALL, ANY, and NOT compose comparisons; ASSERT fails a false condition; FOREACH is sequential; WHILE tests before each bounded iteration; PAR outputs become visible only at JOIN.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
Text after `: ` states boundary meaning absent from the interface schema.
AS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
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
owned-concern: "OAK product intent, locally defined repository contracts, resumable tasks, and scoped AGENTS routing."

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

instruction-justification: "Host trust, persistent-state ownership, and global scope invariants apply across independent arrivals and cannot be owned by one action or payload schema."
</constants>

<schemas>
<schema id="repository-task" name="Repository Task" purpose="Retain a new request before read-only preparation, not authorize implementation.">
Task <TASK_ID>: <TASK>
Paths: <PATHS>
Constraints: <CONSTRAINTS>

WHERE:
- <TASK_ID> is string; is non-empty; a host-issued identifier that is never reused.
- <TASK> is string; is non-empty.
- <PATHS> is string; is non-empty; the repository paths within the requested scope.
- <CONSTRAINTS> is string; empty when none apply.
</schema>

<schema id="task-handle" name="Task Handle" purpose="Identify a retained task, the receiving interface chooses status or cancellation.">
Task id: <TASK_ID>

WHERE:
- <TASK_ID> is string; is non-empty.
</schema>

<schema id="resume-request" name="Resume Request" purpose="Advance only the named current resumable checkpoint.">
Resume task <TASK_ID> at <PHASE>.

WHERE:
- <TASK_ID> is string; is non-empty.
- <PHASE> is string; is one of `prepare`, `implement`, `refresh`, `verify`, `report`; the expected checkpoint.
</schema>

<schema id="approval-decision" name="Approval Decision" purpose="Record the user's decision for one exact prepared proposal.">
Task <TASK_ID>, proposal <PROPOSAL_REVISION>: approved <APPROVED>.

WHERE:
- <TASK_ID> is string; is non-empty; the host-issued task identity.
- <PROPOSAL_REVISION> is string; is non-empty; the host-derived identity of the proposal and its input workspace.
- <APPROVED> is boolean; true authorizes this proposal, while false declines it.
</schema>

<schema id="task-checkpoint" name="Task Checkpoint" purpose="Describe the twelve root-owned values restored across serialized arrivals.">
Task <TASK_ID> at <PHASE>: <TASK>
Paths: <PATHS>; constraints: <CONSTRAINTS>
Proposal <PROPOSAL_REVISION>: <PROPOSAL>
Working: <WORKING_REVISION>; approved: <APPROVED_REVISION>; verified: <VERIFIED_REVISION>
Evidence: <EVIDENCE>
Changed paths: <CHANGED_PATHS>

WHERE:
- <TASK_ID> is string; empty before the first task.
- <TASK> is string; the retained request text, empty while idle.
- <PATHS> is string; the retained scope paths, empty while idle.
- <CONSTRAINTS> is string.
- <PHASE> is string; is one of `idle`, `prepare`, `awaiting-approval`, `implement`, `refresh`, `verify`, `report`, `complete`, `cancelled`.
- <PROPOSAL> is string; the prepared proposal text, empty before preparation.
- <PROPOSAL_REVISION> is string; the identity covering that proposal and its input workspace, empty before preparation.
- <WORKING_REVISION> is string; the last successfully checkpointed workspace fingerprint, empty before preparation.
- <APPROVED_REVISION> is string; the authorized proposal identity, empty without approval.
- <VERIFIED_REVISION> is string; the workspace fingerprint covered by evidence, empty before verification.
- <EVIDENCE> is string; empty before verification.
- <CHANGED_PATHS> is string; empty when no changes are recorded.
</schema>

<schema id="task-progress" name="Task Progress" purpose="Report the retained phase and proposal, including initial empty proposal values.">
Task <TASK_ID>: <PHASE>
Proposal <PROPOSAL_REVISION>: <PROPOSAL>

WHERE:
- <TASK_ID> is string; is non-empty.
- <PHASE> is string; is non-empty.
- <PROPOSAL_REVISION> is string.
- <PROPOSAL> is string.
</schema>

<schema id="task-proposal" name="Task Proposal" purpose="Return the complete read-only proposal and its host-derived approval identity.">
Proposal <PROPOSAL_REVISION>: <PROPOSAL>

WHERE:
- <PROPOSAL> is string; is non-empty; the complete proposed scope and architecture.
- <PROPOSAL_REVISION> is string; is non-empty; a host-derived identity covering the task, proposal and input workspace revision.
</schema>

<schema id="revision-reading" name="Revision Reading" purpose="Report an observed content fingerprint, never a model-assigned revision.">
Observed revision: <OBSERVED_REVISION>

WHERE:
- <OBSERVED_REVISION> is string; is non-empty; the host-observed current workspace fingerprint.
</schema>

<schema id="expected-revision" name="Expected Revision" purpose="Require the observed workspace to match a retained content fingerprint.">
Expected revision: <EXPECTED_REVISION>

WHERE:
- <EXPECTED_REVISION> is string; is non-empty.
</schema>

<schema id="change-receipt" name="Change Receipt" purpose="Return the observed workspace and complete change set after one work phase.">
Revision <REVISION>; changed paths: <CHANGED_PATHS>

WHERE:
- <REVISION> is string; is non-empty; the observed workspace fingerprint after work.
- <CHANGED_PATHS> is string; the complete task change set, empty for read-only work.
</schema>

<schema id="verification-receipt" name="Verification Receipt" purpose="Report checks actually run against the exact workspace revision.">
Revision <REVISION>; passed: <PASSED>
Evidence: <EVIDENCE>

WHERE:
- <REVISION> is string; is non-empty; the exact verified workspace fingerprint.
- <EVIDENCE> is string; is non-empty; observed results from the complete verification process.
- <PASSED> is boolean; whether every applicable check passed.
</schema>

<schema id="task-outcome" name="Task Outcome" purpose="Compose the final user response from retained verification and changed paths.">
Outcome: <OUTCOME>

WHERE:
- <OUTCOME> is string; is non-empty.
</schema>

<schema id="repository-result" name="Repository Result" purpose="Publish completion only after matching revision checks and nonempty evidence.">
Task <TASK_ID>: <OUTCOME>
Evidence: <EVIDENCE>
Changed paths: <CHANGED_PATHS>

WHERE:
- <TASK_ID> is string; is non-empty.
- <OUTCOME> is string; is non-empty.
- <EVIDENCE> is string; is non-empty.
- <CHANGED_PATHS> is string.
</schema>

<schema id="change-description" name="Change Description" purpose="Supply the facts for naming a change, not permission to perform Git operations.">
Type <TYPE>, scope <SCOPE>: <SUMMARY>
Breaking: <BREAKING>
Migration: <MIGRATION>

WHERE:
- <TYPE> is string; is one of `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `build`, `ci`, `chore`, `revert`.
- <SCOPE> is string; the lowercase kebab-case area, empty when omitted.
- <SUMMARY> is string; is non-empty; an imperative verb, object and necessary qualifier.
- <BREAKING> is boolean; whether a supported contract changes.
- <MIGRATION> is string; the affected contract and migration, required for breaking changes.
</schema>

<schema id="change-name" name="Change Name" purpose="Return a proposed branch name and commit message without changing Git history.">
Branch <BRANCH>; commit <SUBJECT>
<BODY>

WHERE:
- <BRANCH> is string; is non-empty; is one line.
- <SUBJECT> is string; is non-empty; is one line.
- <BODY> is string; the explanation and migration, empty when unnecessary.
</schema>

<schema id="branch-targets" name="Branch Targets" purpose="Identify the remote and branch pair, the receiving interface defines the operation.">
Remote <REMOTE>: source <SOURCE>, destination <DESTINATION>

WHERE:
- <REMOTE> is string; is non-empty; the host-authorized Git remote.
- <SOURCE> is string; is non-empty; the work branch whose tip is updated, merged, or checked for cleanup.
- <DESTINATION> is string; is non-empty; the integration branch used for update, merge, or ancestry verification.
</schema>
</schemas>

<state>
task-id AS schema.task-checkpoint.TASK_ID: ""
task AS schema.task-checkpoint.TASK: ""
paths AS schema.task-checkpoint.PATHS: ""
constraints AS schema.task-checkpoint.CONSTRAINTS: ""
phase AS schema.task-checkpoint.PHASE: "idle"
proposal AS schema.task-checkpoint.PROPOSAL: ""
proposal-revision AS schema.task-checkpoint.PROPOSAL_REVISION: ""
working-revision AS schema.task-checkpoint.WORKING_REVISION: ""
approved-revision AS schema.task-checkpoint.APPROVED_REVISION: ""
verified-revision AS schema.task-checkpoint.VERIFIED_REVISION: ""
evidence AS schema.task-checkpoint.EVIDENCE: ""
changed-paths AS schema.task-checkpoint.CHANGED_PATHS: ""
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
<process id="start-task" name="Start task" input="schema.repository-task">
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

<process id="resume-task" name="Resume task" input="schema.resume-request">
ASSERT $TASK_ID equals $state.task-id
  MESSAGE "Resume targets a different task."
ASSERT $PHASE equals $state.phase
  MESSAGE "Resume targets a stale or inactive checkpoint."
CALL .agents/rules/context.oak.md#process.read (TASK=$state.task, PATHS=$state.paths)
IF $PHASE equals "prepare":
  CALL process.prepare-task ()
ELSE:
  ASSERT $state.approved-revision does not equal ""
    MESSAGE "The current proposal has no approval."
  ASSERT $state.approved-revision equals $state.proposal-revision
    MESSAGE "Approval does not match the current proposal."
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

<process id="decide-task" name="Decide task" input="schema.approval-decision">
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

<process id="cancel-task" name="Cancel task" input="schema.task-handle">
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

<process id="show-task" name="Show task" input="schema.task-handle">
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

<process id="prepare-task" name="Prepare task">
CALL .agents/rules/context.oak.md#process.prepare (TASK=$state.task, PATHS=$state.paths)
CALL process.observe-revision () -> OBSERVED_REVISION
ACT output="schema.task-proposal": Prepare one complete, read-only proposal for <TASK> within <PATHS> and <CONSTRAINTS>, identifying each owner and required source, example, output and verification change. Choose the smallest complete long-term design, not deferred product phases or planned replacements. Include only explicitly named compatibility contracts and consumers. Have host tools derive <PROPOSAL_REVISION> from <TASK_ID>, these inputs, <OBSERVED_REVISION> and the exact <PROPOSAL>; publish the architecture before implementation. Keep all root interface and lifecycle schemas local to AGENTS.md, including checkpoint and receipt definitions; delegate only separately owned work. (
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

<process id="observe-revision" name="Observe revision" output="schema.revision-reading">
ACT output="schema.revision-reading": Use host tools to fingerprint the actual <PATHS> and their relevant dependencies, including governing knowledge and uncommitted content. Return the same <OBSERVED_REVISION> for unchanged content. (
  PATHS=$state.paths,
) -> OBSERVED_REVISION
</process>

<process id="require-revision" name="Check revision" input="schema.expected-revision">
CALL process.observe-revision () -> OBSERVED_REVISION
ASSERT $OBSERVED_REVISION equals $EXPECTED_REVISION
  MESSAGE "The workspace changed; reconcile effects before retrying preparation or starting a new task."
</process>

<process id="implement-repository-task" name="Implement task">
ACT output="schema.change-receipt": Implement the complete approved <PROPOSAL> for <TASK_ID> under <CONSTRAINTS> in <PATHS>. Preserve unrelated work; use the smallest implementation that satisfies every applicable contract and do not defer part of the requested product change. Use the stable operation identity <TASK_ID> plus implement to reconcile any prior external effects before retrying. Return the host-observed final <REVISION> and complete <CHANGED_PATHS>. (
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
ACT output="schema.change-receipt": Complete every affected architecture record, source, example, generated output and scoped AGENTS update for <TASK_ID> and <TASK> under <PROPOSAL>. Remove obsolete names, paths, formats, contracts and support material in this task. Record durable validated lessons with their exact owners. Reconcile prior effects using <TASK_ID> plus refresh; return the observed <REVISION> and complete <CHANGED_PATHS>, including <PRIOR_PATHS>. (
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
ACT output="schema.verification-receipt": Run the complete verification process owned by build/AGENTS.md for <TASK_ID>, inspect the final diff, search for replaced identifiers, paths, formats and contracts, and check the <LIMIT> line bound. Return observed <EVIDENCE>, the exact verified <REVISION>, and whether every applicable check <PASSED>. (
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
ASSERT $state.verified-revision equals $state.working-revision
  MESSAGE "Completion requires verification of the current revision."
ASSERT $state.evidence does not equal ""
  MESSAGE "Completion requires nonempty verification evidence."
ACT output="schema.task-outcome": Produce <OUTCOME> for completed <TASK> from observed <EVIDENCE> and <CHANGED_PATHS>. Lead with the outcome, use short plain sentences, state uncertainty directly, and avoid jargon, filler, praise and repetition. Compose only the response; do not change repository files. (
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

<process id="name-change" name="Name change" input="schema.change-description" output="schema.change-name">
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

<process id="update-branch" name="Update branch" input="schema.branch-targets">
CALL process.require-inactive-task ()
CALL .agents/rules/repository-change.oak.md#process.update-branch (
  REMOTE=$REMOTE,
  SOURCE=$SOURCE,
  DESTINATION=$DESTINATION,
)
</process>

<process id="merge-change" name="Merge change" input="schema.branch-targets">
CALL process.require-inactive-task ()
CALL .agents/rules/repository-change.oak.md#process.merge-change (
  REMOTE=$REMOTE,
  SOURCE=$SOURCE,
  DESTINATION=$DESTINATION,
)
</process>

<process id="clean-merged-branch" name="Clean branch" input="schema.branch-targets">
CALL process.require-inactive-task ()
CALL .agents/rules/repository-change.oak.md#process.clean-merged-branch (
  REMOTE=$REMOTE,
  SOURCE=$SOURCE,
  DESTINATION=$DESTINATION,
)
</process>
</processes>

<interfaces>
task-request RECEIVES schema.repository-task: "A host-identified user request; retain it for preparation only when no task is active."
task-resume RECEIVES schema.resume-request: "Continue one matching checkpoint without replaying completed work; implementation phases require approval."
task-approval RECEIVES schema.approval-decision: "A host-authenticated user decision; approval permits subsequent implementation, while refusal cancels the task."
task-cancel RECEIVES schema.task-handle: "Cancel the matching active task and clear approval; do not undo external effects."
status-request RECEIVES schema.task-handle: "Report the matching retained task without advancing its phase or granting authorization."
progress EMITS schema.task-progress: "Return the committed checkpoint and pending proposal to the requester; this is not completion evidence."
task-result EMITS schema.repository-result: "Return the verified task outcome, evidence, and changed paths; the host owns delivery."
name-request RECEIVES schema.change-description: "Request change names only, without permission to create a branch, commit, or merge."
name-result EMITS schema.change-name: "Return naming suggestions through the local public contract after the external naming process."
branch-update RECEIVES schema.branch-targets: "Request an authorized work-branch update from its destination while the lifecycle is inactive."
merge-request RECEIVES schema.branch-targets: "Request an authorized merge commit from source to destination while no task is active."
merge-receipt RECEIVES schema.branch-targets: "A host-confirmed completed merge; permit ancestry-checked cleanup, not another merge, while inactive."
</interfaces>