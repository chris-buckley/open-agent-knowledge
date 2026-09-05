<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
owned-concern: "Accepted change plans and completion reports as repository history."

record-types: CSV<<
record,purpose
plan,"record one accepted change, implementation checks, and completion standard"
report,"record outcome, evidence, changed paths, and final verdict"
>>

plan-format: "examples/schemas/smeac_plan.oak.md"

plan-authoring-rules: ["use the SMEAC format for every new numbered plan in docs/plans", "populate the format as a Markdown planning brief rather than copying its schema definition", "retain Situation, Mission, Execution, Admin and Logistics, and Command and Signal in that order", "give execution tasks stable checkbox identifiers and explicit success criteria, evidence requirements, and transition gates", "record any user authorisation gate separately from plan readiness", "leave completed historical plans in their original format"]

history-rules: ["plans are active only while their named change is in progress", "completed plans and reports are historical evidence, not current architecture", "historical references remain unchanged when they were correct at completion", "a plan becomes complete only after every applicable checkbox passes"]
</constants>

<processes>
<process id="maintain-history" name="Maintain history">
ACT Use <RECORDS> to choose the correct numbered plan or matching completion report. (
  RECORDS=$constant.record-types,
)
ACT Use <FORMAT> and <PLAN_RULES> when preparing a new plan. (
  FORMAT=$constant.plan-format,
  PLAN_RULES=$constant.plan-authoring-rules,
)
ACT Apply <RULES> before changing status, checkboxes, evidence, or verdict. (
  RULES=$constant.history-rules,
)
ACT Read a historical plan only when the user or active task names it. ()
</process>
</processes>