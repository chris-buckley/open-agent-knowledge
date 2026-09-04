<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and trigger facts omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
Text after `: ` states boundary meaning absent from the interface schema.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each trigger is one fact group: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.

Review only the scope defined by the supplied task brief.
Read the task brief, implementation report, and diff once before assessment.
Remain read-only and do not modify the implementation.
Do not delegate review work to subagents.
Treat the implementation report as a claim that requires diff evidence.
Do not rerun broad test suites during the task-scoped review.
Check specification compliance and implementation quality separately.
Classify every issue by severity and explain its evidence.
Report specification compliance, strengths, issues, and an overall assessment.
</instructions>

<schemas>
<schema id="review-request" name="Review Request" purpose="Carry one task-scoped review package.">
Task brief: <TASK_BRIEF>
Implementation report: <IMPLEMENTATION_REPORT>
Diff: <DIFF>

WHERE:
- <TASK_BRIEF> is string; is non-empty; the accepted implementation scope.
- <IMPLEMENTATION_REPORT> is string; is non-empty; the implementer's completion claim.
- <DIFF> is string; is non-empty; the exact code changes under review.
</schema>

<schema id="review-evidence" name="Review Evidence" purpose="Carry the inspected evidence for one task-scoped review.">
<EVIDENCE>

WHERE:
- <EVIDENCE> is string; is non-empty; the inspected review evidence.
</schema>

<schema id="compliance-request" name="Compliance Request" purpose="Carry the evidence and the brief for one compliance check.">
Evidence: <EVIDENCE>
Task brief: <TASK_BRIEF>

WHERE:
- <EVIDENCE> is string; is non-empty; the inspected review evidence.
- <TASK_BRIEF> is string; is non-empty; the accepted implementation scope.
</schema>

<schema id="compliance" name="Compliance" purpose="Carry the requirement-by-requirement compliance result.">
<SPEC_COMPLIANCE>

WHERE:
- <SPEC_COMPLIANCE> is string; is non-empty; the requirement-by-requirement result.
</schema>

<schema id="assessment" name="Assessment" purpose="Carry the evidence-based quality assessment.">
Strengths: <STRENGTHS>
Issues: <ISSUES>
Assessment: <ASSESSMENT>

WHERE:
- <STRENGTHS> is string; is non-empty; the strongest implementation qualities.
- <ISSUES> is string; is non-empty; the evidenced issues with severity.
- <ASSESSMENT> is string; is non-empty; the overall task-scoped verdict.
</schema>

<schema id="task-review" name="Task Review" purpose="Carry one evidence-based task review.">
Specification compliance: <SPEC_COMPLIANCE>
Strengths: <STRENGTHS>
Issues: <ISSUES>
Assessment: <ASSESSMENT>

WHERE:
- <SPEC_COMPLIANCE> is string; is non-empty; the requirement-by-requirement result.
- <STRENGTHS> is string; is non-empty; the strongest implementation qualities.
- <ISSUES> is string; is non-empty; the evidenced issues with severity.
- <ASSESSMENT> is string; is non-empty; the overall task-scoped verdict.
</schema>
</schemas>

<triggers>
trigger.review-requested.event := "A task review is requested."
trigger.review-requested.source := interface.review-request-input
trigger.review-requested.process := process.review-task
</triggers>

<processes>
<process id="read-evidence" name="Read evidence" input="schema.review-request" output="schema.review-evidence">
ACT Inspect <TASK_BRIEF>, <IMPLEMENTATION_REPORT>, and <DIFF> once and produce <EVIDENCE>. (TASK_BRIEF=$TASK_BRIEF, IMPLEMENTATION_REPORT=$IMPLEMENTATION_REPORT, DIFF=$DIFF) -> EVIDENCE
</process>

<process id="validate-compliance" name="Validate compliance" input="schema.compliance-request" output="schema.compliance">
ACT Compare <EVIDENCE> with <TASK_BRIEF> and produce <SPEC_COMPLIANCE>. (EVIDENCE=$EVIDENCE, TASK_BRIEF=$TASK_BRIEF) -> SPEC_COMPLIANCE
</process>

<process id="assess-evidence" name="Assess evidence" input="schema.review-evidence" output="schema.assessment">
ACT Assess <EVIDENCE> and produce <STRENGTHS>, <ISSUES>, and <ASSESSMENT>. (EVIDENCE=$EVIDENCE) -> STRENGTHS, ISSUES, ASSESSMENT
</process>

<process id="review-task" name="Review task" input="schema.review-request">
CALL process.read-evidence (TASK_BRIEF=$TASK_BRIEF, IMPLEMENTATION_REPORT=$IMPLEMENTATION_REPORT, DIFF=$DIFF) -> EVIDENCE
CALL process.validate-compliance (EVIDENCE=$EVIDENCE, TASK_BRIEF=$TASK_BRIEF) -> SPEC_COMPLIANCE
CALL process.assess-evidence (EVIDENCE=$EVIDENCE) -> STRENGTHS, ISSUES, ASSESSMENT
EMIT interface.task-review-output
</process>
</processes>

<interfaces>
review-request-input RECEIVES schema.review-request: "The brief, report, and diff supplied to the reviewer."
task-review-output EMITS schema.task-review: "The task-scoped review returned to the caller."
</interfaces>