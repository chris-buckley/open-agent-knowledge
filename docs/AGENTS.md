<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
owned-concern: "Persistent repository plan creation, storage, lifecycle, and completion reports as history."

record-types: CSV<<
record,purpose
plan,"record one accepted change, implementation checks, and completion standard"
report,"record outcome, evidence, changed paths, and final verdict"
>>

plan-format: "examples/schemas/smeac_plan.oak.md"

plan-root: "docs/plans"

plan-storage-rules: ["use one directory named with a unique four-digit numeric id and a short kebab-case topic", "allocate the next unused numeric id and keep the directory name stable throughout the work", "store the intended work and task state in plan.md", "add report.md for the delivered outcome and verification evidence", "create an evidence directory only when supporting files are needed", "keep brief conversational planning outside the persistent plan layout"]

historical-plan-formats: ["0000-repository-refactor", "0001-interface-flow", "0002-architecture-documentation", "0003-scoped-oak-agents", "0004-native-interpreter-context", "0005-shape-first-schemas"]

plan-authoring-rules: ["use the referenced SMEAC schema as the default for every new saved plan", "populate the format as a Markdown planning brief rather than copying its schema definition", "retain Situation, Mission, Execution, Admin and Logistics, and Command and Signal in that order", "give execution tasks unique stable identifiers such as P01.01 and explicit success criteria, evidence requirements, and transition gates", "record any user authorisation gate separately from plan readiness", "apply the phase layout owned by examples/AGENTS.md", "preserve the original formats of the named historical plans and do not extend that exception to new plans"]

history-rules: ["plans are active only while their named change is in progress", "completed plans and reports are historical evidence, not current architecture", "preserve recorded claims and historical path snapshots when moving records, and repair navigational links", "a plan becomes complete only after every applicable checkbox passes"]
</constants>

<processes>
<process id="maintain-history" name="Maintain history">
ACT Use <RECORDS> to choose the correct numbered plan or matching completion report. (
  RECORDS=$constant.record-types,
)
ACT Use <ROOT> and <STORAGE> to place each persistent plan and its supporting records. (
  ROOT=$constant.plan-root,
  STORAGE=$constant.plan-storage-rules,
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