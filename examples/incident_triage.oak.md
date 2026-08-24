<instructions>
Use only evidence present in the incident report.
</instructions>

<constants>
ESCALATION_POLICY: "Escalate critical incidents immediately."
</constants>

<schemas>
<schema id="oak:schema/incident-report" name="Incident Report" purpose="Describe the incident evidence supplied for triage.">
Summary: <SUMMARY>
Impact: <IMPACT>

WHERE:
- <SUMMARY> is string; is non-empty; observed incident evidence.
- <IMPACT> is string; is one of `low`, `medium`, `high`; reported impact.
</schema>
<schema id="oak:schema/triage-decision" name="Triage Decision" purpose="Return one evidence-based incident decision.">
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
STATUS: "ready"
</state>

<triggers>
- An incident report arrives for triage. -> oak:process/triage
</triggers>

<processes>
<process id="oak:process/triage" name="Triage an incident">
STEPS:
1. ACT Classify <SUMMARY> with <IMPACT> under <POLICY>, then produce <SEVERITY>, <RATIONALE>, and <NEXT_ACTION>.
   INPUTS:
      - <SUMMARY> = interface oak:interface/report <SUMMARY>.
      - <IMPACT> = interface oak:interface/report <IMPACT>.
      - <POLICY> = constant oak:constant/escalation-policy.
   OUTPUTS: <SEVERITY>, <RATIONALE>, <NEXT_ACTION>.
2. IF binding <SEVERITY> equals "critical":
   THEN:
      1. SET state oak:state/status = "escalated".
   ELSE:
      1. SET state oak:state/status = "triaged".
3. EMIT interface oak:interface/decision:
   - <SEVERITY> = binding <SEVERITY>.
   - <RATIONALE> = binding <RATIONALE>.
   - <NEXT_ACTION> = binding <NEXT_ACTION>.
   - <POLICY> = constant oak:constant/escalation-policy.
</process>
</processes>

<interfaces>
<interface id="oak:interface/report" direction="in" schema="oak:schema/incident-report">
The report supplied for incident triage.
</interface>
<interface id="oak:interface/decision" direction="out" schema="oak:schema/triage-decision">
The triage decision returned to the caller.
</interface>
</interfaces>
