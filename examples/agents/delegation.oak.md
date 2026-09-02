<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and trigger facts omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
Trigger seeds fill the selected process input schema; each seeded value validates before the process runs.
A source-backed trigger fires on an arrival at its exact interface; its event text stays the semantic signpost.
Each trigger is one fact group: event carries the meaning, an optional source names the exact ingress interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
Each interface is one document-boundary crossing: in arrives, out is emitted, and inout does both.

Return the worker task review unchanged.
</instructions>

<triggers>
trigger.delegation-requested.event := "Delegate the task review."
trigger.delegation-requested.source := interface.review-request-input
trigger.delegation-requested.process := process.delegate-review
trigger.delegation-requested.seed.TASK_BRIEF := $interface.review-request-input.TASK_BRIEF
trigger.delegation-requested.seed.IMPLEMENTATION_REPORT := $interface.review-request-input.IMPLEMENTATION_REPORT
trigger.delegation-requested.seed.DIFF := $interface.review-request-input.DIFF
</triggers>

<processes>
<process id="dispatch-review" name="Dispatch review" input="task_reviewer.oak.md#schema.review-request" output="task_reviewer.oak.md#schema.task-review">
ACT TOOL "agent.reviewer" input="task_reviewer.oak.md#schema.review-request" output="task_reviewer.oak.md#schema.task-review": Review <TASK_BRIEF>, <IMPLEMENTATION_REPORT>, and <DIFF> in one worker agent and produce <SPEC_COMPLIANCE>, <STRENGTHS>, <ISSUES>, and <ASSESSMENT>. (TASK_BRIEF=$TASK_BRIEF, IMPLEMENTATION_REPORT=$IMPLEMENTATION_REPORT, DIFF=$DIFF) -> SPEC_COMPLIANCE, STRENGTHS, ISSUES, ASSESSMENT
</process>

<process id="delegate-review" name="Delegate review" input="task_reviewer.oak.md#schema.review-request">
CALL process.dispatch-review (TASK_BRIEF=$TASK_BRIEF, IMPLEMENTATION_REPORT=$IMPLEMENTATION_REPORT, DIFF=$DIFF) -> SPEC_COMPLIANCE, STRENGTHS, ISSUES, ASSESSMENT
EMIT interface.task-review-output (SPEC_COMPLIANCE=$SPEC_COMPLIANCE, STRENGTHS=$STRENGTHS, ISSUES=$ISSUES, ASSESSMENT=$ASSESSMENT)
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