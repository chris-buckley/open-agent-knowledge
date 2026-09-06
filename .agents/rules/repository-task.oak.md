<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
</instructions>

<constants>
owned-concern: "Typed requests, checkpoints, receipts, and results for the root repository task lifecycle."
</constants>

<schemas>
<schema id="repository-task" name="Repository Task">
Task id: <TASK_ID>
Task: <TASK>
Paths: <PATHS>
Constraints: <CONSTRAINTS>

WHERE:
- <TASK_ID> is string; is non-empty; a host-issued identifier that is never reused.
- <TASK> is string; is non-empty.
- <PATHS> is string; is non-empty.
- <CONSTRAINTS> is string; empty when none apply.
</schema>

<schema id="task-handle" name="Task Handle">
Task id: <TASK_ID>

WHERE:
- <TASK_ID> is string; is non-empty.
</schema>

<schema id="resume-request" name="Resume Request">
Task id: <TASK_ID>
Phase: <PHASE>

WHERE:
- <TASK_ID> is string; is non-empty.
- <PHASE> is string; is one of `prepare`, `implement`, `refresh`, `verify`, `report`; the expected checkpoint.
</schema>

<schema id="approval-decision" name="Approval Decision">
Task id: <TASK_ID>
Proposal revision: <PROPOSAL_REVISION>
Approved: <APPROVED>

WHERE:
- <TASK_ID> is string; is non-empty.
- <PROPOSAL_REVISION> is string; is non-empty.
- <APPROVED> is boolean.
</schema>

<schema id="task-checkpoint" name="Task Checkpoint">
Task id: <TASK_ID>
Task: <TASK>
Paths: <PATHS>
Constraints: <CONSTRAINTS>
Phase: <PHASE>
Proposal: <PROPOSAL>
Proposal revision: <PROPOSAL_REVISION>
Working revision: <WORKING_REVISION>
Approved revision: <APPROVED_REVISION>
Verified revision: <VERIFIED_REVISION>
Evidence: <EVIDENCE>
Changed paths: <CHANGED_PATHS>

WHERE:
- <TASK_ID> is string; empty before the first task.
- <TASK> is string; empty while idle.
- <PATHS> is string; empty while idle.
- <CONSTRAINTS> is string.
- <PHASE> is string; is one of `idle`, `prepare`, `awaiting-approval`, `implement`, `refresh`, `verify`, `report`, `complete`, `cancelled`.
- <PROPOSAL> is string; empty before preparation.
- <PROPOSAL_REVISION> is string; empty before preparation.
- <WORKING_REVISION> is string; empty before preparation.
- <APPROVED_REVISION> is string; empty without approval.
- <VERIFIED_REVISION> is string; empty before verification.
- <EVIDENCE> is string; empty before verification.
- <CHANGED_PATHS> is string; empty when no changes are recorded.
</schema>

<schema id="task-progress" name="Task Progress">
Task id: <TASK_ID>
Phase: <PHASE>
Proposal revision: <PROPOSAL_REVISION>
Proposal: <PROPOSAL>

WHERE:
- <TASK_ID> is string; is non-empty.
- <PHASE> is string; is non-empty.
- <PROPOSAL_REVISION> is string.
- <PROPOSAL> is string.
</schema>

<schema id="task-proposal" name="Task Proposal">
Proposal: <PROPOSAL>
Proposal revision: <PROPOSAL_REVISION>

WHERE:
- <PROPOSAL> is string; is non-empty; the complete proposed scope and architecture.
- <PROPOSAL_REVISION> is string; is non-empty; a host-derived identity covering the task, proposal and input workspace revision.
</schema>

<schema id="revision-reading" name="Revision Reading">
Observed revision: <OBSERVED_REVISION>

WHERE:
- <OBSERVED_REVISION> is string; is non-empty; the host-observed current workspace fingerprint.
</schema>

<schema id="expected-revision" name="Expected Revision">
Expected revision: <EXPECTED_REVISION>

WHERE:
- <EXPECTED_REVISION> is string; is non-empty.
</schema>

<schema id="change-receipt" name="Change Receipt">
Revision: <REVISION>
Changed paths: <CHANGED_PATHS>

WHERE:
- <REVISION> is string; is non-empty; the observed workspace fingerprint after work.
- <CHANGED_PATHS> is string; the complete task change set, empty for read-only work.
</schema>

<schema id="verification-receipt" name="Verification Receipt">
Revision: <REVISION>
Evidence: <EVIDENCE>
Passed: <PASSED>

WHERE:
- <REVISION> is string; is non-empty; the exact verified workspace fingerprint.
- <EVIDENCE> is string; is non-empty; observed results from the complete verification process.
- <PASSED> is boolean; whether every applicable check passed.
</schema>

<schema id="task-outcome" name="Task Outcome">
Outcome: <OUTCOME>

WHERE:
- <OUTCOME> is string; is non-empty.
</schema>

<schema id="repository-result" name="Repository Result">
Task id: <TASK_ID>
Outcome: <OUTCOME>
Evidence: <EVIDENCE>
Changed paths: <CHANGED_PATHS>

WHERE:
- <TASK_ID> is string; is non-empty.
- <OUTCOME> is string; is non-empty.
- <EVIDENCE> is string; is non-empty.
- <CHANGED_PATHS> is string.
</schema>
</schemas>