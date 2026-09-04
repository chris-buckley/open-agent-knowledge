<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and trigger facts omit $.
Conditions are typed trees; ALL, ANY, and NOT compose comparisons; ASSERT fails a false condition; FOREACH is sequential; WHILE tests before each bounded iteration; PAR outputs become visible only at JOIN.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
Text after `: ` states boundary meaning absent from the interface schema.
AS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each trigger is one fact group: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.

Read the task brief and supplied context before implementation.
Ask focused questions before implementation when a requirement is unclear.
Implement only the requested scope and preserve exact requirements.
Do not delegate implementation to subagents.
Keep code organized around clear responsibilities.
Escalate when the task exceeds the available evidence or capability.
Run relevant tests and verification before completion.
Review the completed changes against the task before reporting.
Report status, changes, verification, commit, and review findings.
</instructions>

<constants>
commit-convention: "type(scope): imperative summary"

required-check AS ../schemas/verification.oak.md#schema.verification.CHECK: "implementation-checks-v1"
</constants>

<schemas>
<schema id="task-request" name="Task Request" purpose="Carry one implementation task and its working context.">
Task brief: <TASK_BRIEF>
Context: <CONTEXT>

WHERE:
- <TASK_BRIEF> is string; is non-empty; the exact requested implementation.
- <CONTEXT> is string; is non-empty; the supplied repository and task context.
</schema>

<schema id="implementation-plan" name="Implementation Plan" purpose="Carry one implementation plan with its questions resolved.">
<PLAN>

WHERE:
- <PLAN> is string; is non-empty; the ready implementation plan.
</schema>

<schema id="changeset" name="Changeset" purpose="Carry the implemented code changes.">
<CHANGESET>

WHERE:
- <CHANGESET> is string; is non-empty; the implemented code changes.
</schema>

<schema id="candidate" name="Candidate" purpose="Carry one host-created immutable work snapshot.">
Candidate: <CANDIDATE>
Revision: <REVISION>

WHERE:
- <CANDIDATE> is string; is non-empty; the host-owned immutable snapshot to verify and commit.
- <REVISION> is string; matches `^[0-9a-f]{64}$`; the snapshot SHA-256 digest computed by the host.
</schema>

<schema id="planned-changeset" name="Planned Changeset" purpose="Carry the implemented changes with the plan they must satisfy.">
Plan: <PLAN>
Changeset: <CHANGESET>

WHERE:
- <PLAN> is string; is non-empty; the ready implementation plan.
- <CHANGESET> is string; is non-empty; the implemented code changes.
</schema>

<schema id="review-findings" name="Review Findings" purpose="Carry the self-review findings for one changeset.">
<FINDINGS>

WHERE:
- <FINDINGS> is string; is non-empty; the self-review findings.
</schema>

<schema id="reviewed-changeset" name="Reviewed Changeset" purpose="Carry the implemented changes with the findings to apply.">
Changeset: <CHANGESET>
Findings: <FINDINGS>

WHERE:
- <CHANGESET> is string; is non-empty; the implemented code changes.
- <FINDINGS> is string; is non-empty; the self-review findings.
</schema>

<schema id="completion" name="Completion" purpose="Carry the revised work and status after findings are applied.">
Status: <STATUS>
Summary: <SUMMARY>
Revised changeset: <REVISED_CHANGESET>

WHERE:
- <STATUS> is string; is one of `complete`, `blocked`; the completion status.
- <SUMMARY> is string; is non-empty; the implemented changes.
- <REVISED_CHANGESET> is string; is non-empty; the work after applying review findings.
</schema>

<schema id="verified-changeset" name="Verified Changeset" purpose="Carry one candidate with revision-linked verification and its commit convention.">
Candidate: <CANDIDATE>
Revision: <REVISION>
Subject: <VERIFIED_SUBJECT>
Revision: <VERIFIED_REVISION>
Check: <CHECK>
Passed: <PASSED>
Evidence: <EVIDENCE>
Commit convention: <COMMIT_CONVENTION>

WHERE:
- <CANDIDATE> is string; is non-empty; the host-owned immutable snapshot to verify and commit.
- <REVISION> is string; matches `^[0-9a-f]{64}$`; the snapshot SHA-256 digest computed by the host.
- <VERIFIED_SUBJECT> is string; is non-empty; the subject actually inspected by the verifier.
- <VERIFIED_REVISION> is string; matches `^[0-9a-f]{64}$`; the SHA-256 digest of the immutable snapshot actually checked.
- <CHECK> is string; is non-empty; the versioned check definition actually performed.
- <PASSED> is boolean; the observed check result, not a confidence estimate.
- <EVIDENCE> is string; is non-empty; the host-recorded evidence location, whose existence the host must establish.
- <COMMIT_CONVENTION> is string; is non-empty; the required commit message convention.
</schema>

<schema id="commit" name="Commit" purpose="Identify the commit and the exact snapshot it contains.">
Commit: <COMMIT>
Committed revision: <COMMITTED_REVISION>

WHERE:
- <COMMIT> is string; matches `^[0-9a-f]{7,40}$`; the resulting commit hash.
- <COMMITTED_REVISION> is string; matches `^[0-9a-f]{64}$`; the snapshot digest actually committed by the host.
</schema>

<schema id="implementation-report" name="Implementation Report" purpose="Carry the completed implementer report and exact verification subject.">
Status: <STATUS>
Summary: <SUMMARY>
Candidate: <CANDIDATE>
Revision: <REVISION>
Subject: <VERIFIED_SUBJECT>
Revision: <VERIFIED_REVISION>
Check: <CHECK>
Passed: <PASSED>
Evidence: <EVIDENCE>
Commit: <COMMIT>
Findings: <FINDINGS>

WHERE:
- <STATUS> is string; is one of `complete`; the complete status.
- <SUMMARY> is string; is non-empty; the implemented changes.
- <CANDIDATE> is string; is non-empty; the host-owned immutable snapshot to verify and commit.
- <REVISION> is string; matches `^[0-9a-f]{64}$`; the snapshot SHA-256 digest computed by the host.
- <VERIFIED_SUBJECT> is string; is non-empty; the subject actually inspected by the verifier.
- <VERIFIED_REVISION> is string; matches `^[0-9a-f]{64}$`; the SHA-256 digest of the immutable snapshot actually checked.
- <CHECK> is string; is non-empty; the versioned check definition actually performed.
- <PASSED> is boolean; the observed check result, not a confidence estimate.
- <EVIDENCE> is string; is non-empty; the host-recorded evidence location, whose existence the host must establish.
- <COMMIT> is string; matches `^[0-9a-f]{7,40}$`; the resulting commit hash.
- <FINDINGS> is string; is non-empty; the self-review findings.
</schema>

<schema id="escalation" name="Escalation" purpose="Carry the blocked outcome and its findings to the caller.">
Status: <STATUS>
Summary: <SUMMARY>
Findings: <FINDINGS>

WHERE:
- <STATUS> is string; is one of `blocked`; the blocked status.
- <SUMMARY> is string; is non-empty; the work state when blocked.
- <FINDINGS> is string; is non-empty; the self-review findings.
</schema>
</schemas>

<triggers>
trigger.implementation-requested.event := "An implementation task arrives."
trigger.implementation-requested.source := interface.task-request-input
trigger.implementation-requested.process := process.implement-task
</triggers>

<processes>
<process id="plan-task" name="Plan task" input="schema.task-request" output="schema.implementation-plan">
ACT Read <TASK_BRIEF> with <CONTEXT> and produce <DRAFT_PLAN> and <QUESTIONS>. (TASK_BRIEF=$TASK_BRIEF, CONTEXT=$CONTEXT) -> DRAFT_PLAN, QUESTIONS
ACT Resolve <QUESTIONS> into <DRAFT_PLAN> and produce <PLAN>. (QUESTIONS=$QUESTIONS, DRAFT_PLAN=$DRAFT_PLAN) -> PLAN
</process>

<process id="implement-plan" name="Implement plan" input="schema.implementation-plan" output="schema.changeset">
ACT Implement <PLAN> exactly and produce <CHANGESET>. (PLAN=$PLAN) -> CHANGESET
</process>

<process id="snapshot-changeset" name="Snapshot changeset" input="schema.changeset" output="schema.candidate">
ACT TOOL "changes.snapshot" input="schema.changeset" output="schema.candidate": Freeze <CHANGESET>, including all verification-relevant inputs, as immutable <CANDIDATE> and compute its SHA-256 <REVISION>. (CHANGESET=$CHANGESET) -> CANDIDATE, REVISION
</process>

<process id="test-changeset" name="Test changeset" input="schema.candidate" output="../schemas/verification.oak.md#schema.verification">
ACT TOOL "checks.verify-changeset" input="schema.candidate" output="../schemas/verification.oak.md#schema.verification": Inspect immutable <CANDIDATE> requested at <REVISION>; run the versioned implementation checks and record actual <VERIFIED_SUBJECT>, <VERIFIED_REVISION>, <CHECK>, <PASSED>, and <EVIDENCE>. (CANDIDATE=$CANDIDATE, REVISION=$REVISION) -> VERIFIED_SUBJECT, VERIFIED_REVISION, CHECK, PASSED, EVIDENCE
</process>

<process id="review-changeset" name="Review changeset" input="schema.planned-changeset" output="schema.review-findings">
ACT Review <CHANGESET> against <PLAN> and produce <FINDINGS>. (CHANGESET=$CHANGESET, PLAN=$PLAN) -> FINDINGS
</process>

<process id="apply-findings" name="Apply findings" input="schema.reviewed-changeset" output="schema.completion">
ACT Apply <FINDINGS> to <CHANGESET> and produce <REVISED_CHANGESET>, <SUMMARY>, and <STATUS>. (FINDINGS=$FINDINGS, CHANGESET=$CHANGESET) -> REVISED_CHANGESET, SUMMARY, STATUS
</process>

<process id="commit-changeset" name="Commit changeset" input="schema.verified-changeset" output="schema.commit">
ASSERT $VERIFIED_SUBJECT equals $CANDIDATE
  MESSAGE "The evidence belongs to another candidate."
ASSERT $VERIFIED_REVISION equals $REVISION
  MESSAGE "The evidence belongs to another revision."
ASSERT $CHECK equals $constant.required-check
  MESSAGE "The evidence does not cover the required checks."
ASSERT $PASSED equals true
  MESSAGE "The required checks failed."
ACT TOOL "changes.commit-verified" input="schema.verified-changeset" output="schema.commit": Reject drift before any side effect; commit exactly immutable <CANDIDATE> at <REVISION> with <COMMIT_CONVENTION> using <VERIFIED_SUBJECT>, <VERIFIED_REVISION>, <CHECK>, <PASSED>, and <EVIDENCE>, then return <COMMIT> and <COMMITTED_REVISION>. (CANDIDATE=$CANDIDATE, REVISION=$REVISION, VERIFIED_SUBJECT=$VERIFIED_SUBJECT, VERIFIED_REVISION=$VERIFIED_REVISION, CHECK=$CHECK, PASSED=$PASSED, EVIDENCE=$EVIDENCE, COMMIT_CONVENTION=$COMMIT_CONVENTION) -> COMMIT, COMMITTED_REVISION
ASSERT $COMMITTED_REVISION equals $REVISION
  MESSAGE "The host committed a different revision; external effects cannot be rolled back by OAK."
</process>

<process id="implement-task" name="Implement task" input="schema.task-request">
CALL process.plan-task (TASK_BRIEF=$TASK_BRIEF, CONTEXT=$CONTEXT) -> PLAN
CALL process.implement-plan (PLAN=$PLAN) -> CHANGESET
CALL process.review-changeset (PLAN=$PLAN, CHANGESET=$CHANGESET) -> FINDINGS
CALL process.apply-findings (CHANGESET=$CHANGESET, FINDINGS=$FINDINGS) -> REVISED_CHANGESET, SUMMARY, STATUS
IF $STATUS equals "blocked":
  THEN:
    EMIT interface.escalation-output (STATUS=$STATUS, SUMMARY=$SUMMARY, FINDINGS=$FINDINGS)
  ELSE:
    CALL process.snapshot-changeset (CHANGESET=$REVISED_CHANGESET) -> CANDIDATE, REVISION
    CALL process.test-changeset (CANDIDATE=$CANDIDATE, REVISION=$REVISION) -> VERIFIED_SUBJECT, VERIFIED_REVISION, CHECK, PASSED, EVIDENCE
    CALL process.commit-changeset (CANDIDATE=$CANDIDATE, REVISION=$REVISION, VERIFIED_SUBJECT=$VERIFIED_SUBJECT, VERIFIED_REVISION=$VERIFIED_REVISION, CHECK=$CHECK, PASSED=$PASSED, EVIDENCE=$EVIDENCE, COMMIT_CONVENTION=$constant.commit-convention) -> COMMIT, COMMITTED_REVISION
    EMIT interface.implementation-report-output (STATUS=$STATUS, SUMMARY=$SUMMARY, CANDIDATE=$CANDIDATE, REVISION=$REVISION, VERIFIED_SUBJECT=$VERIFIED_SUBJECT, VERIFIED_REVISION=$VERIFIED_REVISION, CHECK=$CHECK, PASSED=$PASSED, EVIDENCE=$EVIDENCE, COMMIT=$COMMIT, FINDINGS=$FINDINGS)
</process>
</processes>

<interfaces>
task-request-input RECEIVES schema.task-request: "The task and context supplied to the implementer."
implementation-report-output EMITS schema.implementation-report: "The implementer's final status and evidence."
escalation-output EMITS schema.escalation: "The blocked outcome returned instead of a commit."
</interfaces>