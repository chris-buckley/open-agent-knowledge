<instructions>
$ reads a value; a dotted path starts with its part; a bare $NAME is local to the running process; SET, CALL, and EMIT omit $.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots, and WHERE lines that constrain each slot.
State holds values that persist and can change while processes run.
Each trigger names one arrival reason, an optional state guard, and the process that runs when both match.
Each process is the exact way to do one task; follow its steps in order, top to bottom.
Each interface is one information crossing: in arrives, out is emitted, and inout does both.
Use only evidence present in the incident report.
</instructions>

<constants>
escalation-policy: "Escalate critical incidents immediately."
</constants>

<schemas>
<schema id="incident-report" name="Incident Report" purpose="Describe the incident evidence supplied for triage.">
Summary: <SUMMARY>
Impact: <IMPACT>

WHERE:
- <SUMMARY> is string; is non-empty; observed incident evidence.
- <IMPACT> is string; is one of `low`, `medium`, `high`; reported impact.
</schema>

<schema id="triage-decision" name="Triage Decision" purpose="Return one evidence-based incident decision.">
Severity: <SEVERITY>
Rationale: <RATIONALE>
Next action: <NEXT_ACTION>
Policy: <POLICY>

WHERE:
- <SEVERITY> is string; is one of `low`, `medium`, `high`, `critical`; assigned severity.
- <RATIONALE> is string; is non-empty; is at most 240 characters; brief evidence-based reason.
- <NEXT_ACTION> is string; is non-empty; one immediate action.
- <POLICY> is string; is non-empty; policy applied to the decision.
</schema>
</schemas>

<state>
status: "ready"
</state>

<triggers>
<trigger id="triage-trigger" given='$state.status equals "ready"' when="An incident report arrives for triage." process="triage" />
</triggers>

<processes>
<process id="triage" name="Triage incident">
ACT Classify <SUMMARY> with <IMPACT> under <POLICY>, then produce <SEVERITY>, <RATIONALE>, and <NEXT_ACTION>.
  INPUTS:
    SUMMARY = $interface.report.SUMMARY
    IMPACT = $interface.report.IMPACT
    POLICY = $constant.escalation-policy
  OUTPUTS: SEVERITY, RATIONALE, NEXT_ACTION
IF $SEVERITY equals "critical":
  SET state.status = "escalated"
ELSE:
  SET state.status = "triaged"
EMIT interface.decision:
  SEVERITY = $SEVERITY
  RATIONALE = $RATIONALE
  NEXT_ACTION = $NEXT_ACTION
  POLICY = $constant.escalation-policy
</process>
</processes>

<interfaces>
<interface id="report" direction="in" schema="incident-report">
The report supplied for incident triage.
</interface>

<interface id="decision" direction="out" schema="triage-decision">
The triage decision returned to the caller.
</interface>
</interfaces>
