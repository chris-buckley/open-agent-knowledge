<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and trigger facts omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
Text after `: ` states boundary meaning absent from the interface schema.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each trigger is one fact group: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.

Challenge the amendment against the supplied evidence and protected invariants.
Treat the current OAK document and protected invariants as read-only.
Request evidence when the amendment cannot yet be justified.
Reject an amendment that breaks a protected invariant.
Do not compile, ratify, or publish a successor.
</instructions>

<schemas>
<schema id="amendment-review-request" name="Amendment Review Request" purpose="Carry one proposed amendment and the evidence needed to challenge it.">
Current OAK: <CURRENT_OAK>
Amendment id: <AMENDMENT_ID>
Amendment: <AMENDMENT>
Rationale: <RATIONALE>
Evidence: <EVIDENCE>
Protected invariants: <PROTECTED_INVARIANTS>

WHERE:
- <CURRENT_OAK> is string; is non-empty; the current canonical OAK document.
- <AMENDMENT_ID> is string; is non-empty; the stable amendment identifier.
- <AMENDMENT> is string; is non-empty; the exact proposed change.
- <RATIONALE> is string; is non-empty; why the proposed change is needed.
- <EVIDENCE> is string; the supplied implementation or validation evidence, empty when absent.
- <PROTECTED_INVARIANTS> is string; is non-empty; the invariants every successor must preserve.
</schema>

<schema id="amendment-review" name="Amendment Review" purpose="Carry the independent decision and evidence request for one amendment.">
Decision: <DECISION>
Findings: <REVIEW_FINDINGS>
Evidence request: <EVIDENCE_REQUEST>

WHERE:
- <DECISION> is string; is one of `accept`, `reject`, `needs-evidence`; the independent amendment decision.
- <REVIEW_FINDINGS> is string; is non-empty; the evidence-based review findings.
- <EVIDENCE_REQUEST> is string; the missing evidence request, empty when none is needed.
</schema>
</schemas>

<triggers>
trigger.amendment-review-requested.event := "An amendment review is requested."
trigger.amendment-review-requested.source := interface.review-request
trigger.amendment-review-requested.process := process.review-amendment
</triggers>

<processes>
<process id="review-amendment" name="Review amendment" input="schema.amendment-review-request" output="schema.amendment-review">
ACT input="schema.amendment-review-request" output="schema.amendment-review": For <AMENDMENT_ID>, challenge <AMENDMENT> with <RATIONALE> and <EVIDENCE> against <CURRENT_OAK> and <PROTECTED_INVARIANTS>, then produce <DECISION>, <REVIEW_FINDINGS>, and <EVIDENCE_REQUEST>. (CURRENT_OAK=$CURRENT_OAK, AMENDMENT_ID=$AMENDMENT_ID, AMENDMENT=$AMENDMENT, RATIONALE=$RATIONALE, EVIDENCE=$EVIDENCE, PROTECTED_INVARIANTS=$PROTECTED_INVARIANTS) -> DECISION, REVIEW_FINDINGS, EVIDENCE_REQUEST
EMIT interface.review-result
</process>
</processes>

<interfaces>
review-request RECEIVES schema.amendment-review-request: "The amendment package supplied by the successor coordinator."
review-result EMITS schema.amendment-review: "The independent amendment decision returned to the coordinator."
</interfaces>