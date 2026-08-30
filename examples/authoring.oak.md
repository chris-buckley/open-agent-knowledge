<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and THEN omit $.
Conditions are typed trees; ALL, ANY, and NOT compose comparisons; ASSERT fails a false condition; FOREACH is sequential; WHILE tests before each bounded iteration; PAR outputs become visible only at JOIN.
State holds values that persist and can change while processes run.
Each trigger contains GIVEN, WHEN, and THEN; WHEN matches first, GIVEN guards it, and THEN selects a process.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
</constants>

<schemas>
</schemas>

<state>
job-id: "job-123"
current-job-status: "pending"
</state>

<triggers>
<trigger id="job-waiting">
GIVEN: true
WHEN: "Wait for the job."
THEN: process.wait-job
</trigger>
</triggers>

<processes>
<process id="wait-job" name="Wait job">
WHILE $state.current-job-status does not equal "complete" LIMIT 3:
  ACT TOOL "jobs.status": Read <JOB_ID> and produce <STATUS>.
    INPUTS:
      JOB_ID = $state.job-id
    OUTPUTS: STATUS
  SET state.current-job-status = $STATUS
ACT Confirm that the job is complete.
</process>
</processes>

<interfaces>
</interfaces>