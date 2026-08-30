<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and THEN omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
Each trigger contains GIVEN, WHEN, and THEN; WHEN matches first, GIVEN guards it, and THEN selects a process.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
Each interface is one document-boundary crossing: in arrives, out is emitted, and inout does both.

Return the worker task review unchanged.
</instructions>

<constants>
</constants>

<schemas>
</schemas>

<state>
</state>

<triggers>
<trigger id="delegation-requested">
GIVEN: true
WHEN: "Delegate the task review."
THEN: process.delegate-review
</trigger>
</triggers>

<processes>
<process id="dispatch-review" name="Dispatch review" input="task_reviewer.oak.md#schema.review-request" output="task_reviewer.oak.md#schema.task-review">
ACT TOOL "agent.reviewer": Review <TASK_BRIEF>, <IMPLEMENTATION_REPORT>, and <DIFF> in one worker agent and produce <SPEC_COMPLIANCE>, <STRENGTHS>, <ISSUES>, and <ASSESSMENT>.
  INPUTS:
    TASK_BRIEF = $TASK_BRIEF
    IMPLEMENTATION_REPORT = $IMPLEMENTATION_REPORT
    DIFF = $DIFF
  OUTPUTS: SPEC_COMPLIANCE, STRENGTHS, ISSUES, ASSESSMENT
</process>

<process id="delegate-review" name="Delegate review">
CALL process.dispatch-review:
  INPUTS:
    TASK_BRIEF = $interface.review-request-input.TASK_BRIEF
    IMPLEMENTATION_REPORT = $interface.review-request-input.IMPLEMENTATION_REPORT
    DIFF = $interface.review-request-input.DIFF
  OUTPUTS: SPEC_COMPLIANCE, STRENGTHS, ISSUES, ASSESSMENT
EMIT interface.task-review-output:
  SPEC_COMPLIANCE = $SPEC_COMPLIANCE
  STRENGTHS = $STRENGTHS
  ISSUES = $ISSUES
  ASSESSMENT = $ASSESSMENT
</process>
</processes>

<interfaces>
<interface id="review-request-input" direction="in" schema="task_reviewer.oak.md#schema.review-request">
The review request the coordinator forwards to the worker.
</interface>

<interface id="task-review-output" direction="out" schema="task_reviewer.oak.md#schema.task-review">
The worker task review returned to the caller.
</interface>
</interfaces>