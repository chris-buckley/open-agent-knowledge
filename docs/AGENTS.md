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

plan-authoring-rules: ["use the referenced SMEAC schema as the default for every new saved plan", "populate the format as a Markdown planning brief rather than copying its schema definition", "retain Situation, Mission, Execution, Admin and Logistics, and Command and Signal in that order", "give execution tasks unique stable identifiers such as P01.01 and explicit success criteria, evidence requirements, and transition gates", "record any user authorisation gate separately from plan readiness", "keep each plan focused on its named change, omitting completed preparatory housekeeping from its narrative, task list, and directory views", "apply the phase layout owned by examples/AGENTS.md", "preserve the original formats of the named historical plans and do not extend that exception to new plans"]

preamble-first-plan: 18

preamble-rules: ["for plans from preamble-first-plan, put all plan metadata in one leading YAML frontmatter mapping", "use the SMEAC title, prepared and classification fields; quote and escape scalar values when YAML requires it", "keep plan identity, readiness, publication, authorisation and execution status in frontmatter when relevant", "start the body with one populated Intent section before Situation, preserving the five numbered SMEAC sections", "keep intent substantive and distinct from metadata or implementation approval", "preserve older plan formats and all their existing verification gates"]

phase-maintenance-rules: YAML<<
- When an active plan's scope, architecture, deliverables or verification changes,
  update its phases, objectives, key tasks, dependencies, success criteria and transition
  triggers to cover the complete current plan.
- Preserve stable task identifiers and evidence-backed completion status. Add or revise
  pending work, and check phase coverage before calling the plan implementation-ready.
>>

state-comparison-rules: YAML<<
- Use the State Comparisons subsection of Mission when supplied examples or a visible
  before-and-after result clarify a new or active plan. Omit it when no comparison
  is useful; do not retrofit completed records.
- Give each comparison a stable E01-style identifier, a short name, authority, current
  state, desired state, and acceptance criteria using the referenced SMEAC schema.
- Show the observed current state and intended desired state together. State when
  an artifact is absent or the baseline is unknown instead of inventing a starting
  point.
- Preserve agreed specimen text and formatting in fenced blocks. Link larger specimens
  from the plan's evidence directory and label their role as expected or observed.
- Mark accepted completion criteria required and explanatory examples illustrative.
  State exactly what must match, what may vary, and how the comparison is verified.
- Cite required comparison identifiers in execution success criteria and record their
  observed verification in the completion report. A populated example is not proof
  of implementation or authorisation to perform it.
>>

directory-change-first-plan: 16

directory-change-reopened-plans: []

directory-change-rules: YAML<<
- Require Mission's Directory Changes for new plans from directory-change-first-plan
  and for older plans explicitly named in directory-change-reopened-plans. Preserve
  historical records and all their existing checks.
- Use the owning SMEAC template's baseline, current and planned text trees, legend,
  ownership and verification fields. Place the subsection before State Comparisons.
- Show affected files with change markers, purposes and source-to-output ownership.
  Identify move sources, retain removed leaves, and expand affected directories; ellipses
  must not conceal intended changes.
- Label an unknown baseline honestly. For no file changes, state the reason and use
  the template's no-change wording in both views rather than inventing a tree.
- Check populated fields and paired fences prospectively; independently compare the
  final diagram with actual changed paths. A valid diagram does not prove delivery.
- Reject unfilled SMEAC placeholders in prose and fenced directory views.
>>

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
ACT Apply <PREAMBLE> to new plans under the prospective plan-number boundary. (
  PREAMBLE=$constant.preamble-rules,
)
ACT Apply <PHASES> as an active plan evolves and before declaring it implementation-ready. (
  PHASES=$constant.phase-maintenance-rules,
)
ACT Apply <COMPARISONS> when recording intended changes and their completion evidence. (
  COMPARISONS=$constant.state-comparison-rules,
)
ACT Apply <DIRECTORIES> to applicable plans and their final changed-path review. (
  DIRECTORIES=$constant.directory-change-rules,
)
ACT Apply <RULES> before changing status, checkboxes, evidence, or verdict. (
  RULES=$constant.history-rules,
)
ACT Read a historical plan only when the user or active task names it. ()
</process>
</processes>