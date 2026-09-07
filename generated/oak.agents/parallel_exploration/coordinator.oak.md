<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Conditions are typed trees; ALL, ANY, and NOT compose comparisons; ASSERT fails a false condition; FOREACH is sequential; WHILE tests before each bounded iteration; PAR outputs become visible only at JOIN.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
Text after `: ` states boundary meaning absent from the interface schema.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
runtime-question: "Trace action execution and dataflow."

contracts-question: "Trace tool contracts and verification."
</constants>

<schemas>
<schema id="exploration-request" name="Exploration Request" purpose="Bound one read-only investigation. A requested revision is not observed evidence.">
Question: <QUESTION>
Paths: <PATHS>
Requested revision: <REVISION>

WHERE:
- <QUESTION> is string; is non-empty; the bounded question to answer.
- <PATHS> is string; is non-empty; newline-separated repository-relative path scope, not permission to read elsewhere.
- <REVISION> is string; is non-empty; the requested immutable snapshot identity, verify it before substantive inspection.
</schema>

<schema id="runtime-report" name="Runtime Report">
<RUNTIME_REPORT>

WHERE:
- <RUNTIME_REPORT> is string; is non-empty; one complete populated exploration report, validated by the dispatch boundary.
</schema>

<schema id="contract-report" name="Contract Report">
<CONTRACT_REPORT>

WHERE:
- <CONTRACT_REPORT> is string; is non-empty; one complete populated exploration report, validated by the dispatch boundary.
</schema>

<schema id="exploration-summary" name="Exploration Summary" purpose="Reconcile both reports while preserving uncertainty and evidence limitations.">
## Findings
<SUMMARY>

## Limitations
<LIMITATIONS>

WHERE:
- <SUMMARY> is string; is non-empty.
- <LIMITATIONS> is string; is non-empty.
</schema>
</schemas>

<triggers>
exploration-requested(
  event="Parallel repository exploration is requested.",
  source=interface.exploration-input,
  process=process.explore-repository,
)
</triggers>

<processes>
<process id="explore-repository" name="Explore repository" input="schema.exploration-request">
PAR:
  ACT TOOL "agent.explore-runtime" input="schema.exploration-request" output="schema.runtime-report": Investigate <QUESTION> within <PATHS> at <REVISION>; return validated <RUNTIME_REPORT>. (
    QUESTION=$constant.runtime-question,
    PATHS=$PATHS,
    REVISION=$REVISION,
  ) -> RUNTIME_REPORT
  ACT TOOL "agent.explore-contracts" input="schema.exploration-request" output="schema.contract-report": Investigate <QUESTION> within <PATHS> at <REVISION>; return validated <CONTRACT_REPORT>. (
    QUESTION=$constant.contracts-question,
    PATHS=$PATHS,
    REVISION=$REVISION,
  ) -> CONTRACT_REPORT
JOIN
ACT output="schema.exploration-summary": Reconcile <RUNTIME_REPORT> and <CONTRACT_REPORT> for <QUESTION> within <PATHS> at <REVISION>. Require complete reports for that same revision and scope before synthesis; reject malformed, blocked or mismatched reports. Preserve disagreements, file-backed evidence and gaps in <SUMMARY> and <LIMITATIONS>. Reading a test is not running it. Do not invent findings or tool effects. (
  QUESTION=$QUESTION,
  PATHS=$PATHS,
  REVISION=$REVISION,
  RUNTIME_REPORT=$RUNTIME_REPORT,
  CONTRACT_REPORT=$CONTRACT_REPORT,
) -> SUMMARY, LIMITATIONS
EMIT interface.summary-output
</process>
</processes>

<interfaces>
exploration-input RECEIVES schema.exploration-request: "A bounded overall question whose execution and contract aspects can be explored independently."
summary-output EMITS schema.exploration-summary: "A joined, evidence-backed answer, not permission for implementation or proof of live Codex execution."
</interfaces>