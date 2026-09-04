<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and trigger facts omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
Text after `: ` states boundary meaning absent from the interface schema.
Each trigger is one fact group: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.

Return the worker task review unchanged.
</instructions>

<triggers>
trigger.delegation-requested.event := "Delegate the task review."
trigger.delegation-requested.source := interface.review-request
trigger.delegation-requested.process := process.delegate-review
</triggers>

<processes>
<process id="dispatch-review" name="Dispatch review" input="task_reviewer.oak.md#schema.review-request" output="task_reviewer.oak.md#schema.task-review">
ACT TOOL "agent.reviewer" input="task_reviewer.oak.md#schema.review-request" output="task_reviewer.oak.md#schema.task-review": Review <TASK_BRIEF>, <IMPLEMENTATION_REPORT>, and <DIFF> in one worker agent and produce <SPEC_COMPLIANCE>, <STRENGTHS>, <ISSUES>, and <ASSESSMENT>. (TASK_BRIEF=$TASK_BRIEF, IMPLEMENTATION_REPORT=$IMPLEMENTATION_REPORT, DIFF=$DIFF) -> SPEC_COMPLIANCE, STRENGTHS, ISSUES, ASSESSMENT
</process>

<process id="delegate-review" name="Delegate review" input="task_reviewer.oak.md#schema.review-request">
CALL process.dispatch-review (TASK_BRIEF=$TASK_BRIEF, IMPLEMENTATION_REPORT=$IMPLEMENTATION_REPORT, DIFF=$DIFF) -> SPEC_COMPLIANCE, STRENGTHS, ISSUES, ASSESSMENT
EMIT interface.task-review
</process>
</processes>

<interfaces>
review-request RECEIVES task_reviewer.oak.md#schema.review-request: "The review request the coordinator forwards to the worker."
task-review EMITS task_reviewer.oak.md#schema.task-review: "The worker task review returned to the caller."
</interfaces>