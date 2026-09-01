<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and THEN omit $.
Conditions are typed trees; ALL, ANY, and NOT compose comparisons; ASSERT fails a false condition; FOREACH is sequential; WHILE tests before each bounded iteration; PAR outputs become visible only at JOIN.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
Trigger inputs seed the selected process input schema; each seeded value validates before the process runs.
AS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
State holds values that persist and can change while processes run.
Each trigger contains GIVEN, WHEN, and THEN; WHEN matches first, GIVEN guards it, and THEN selects a process.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
Each interface is one document-boundary crossing: in arrives, out is emitted, and inout does both.

Treat the current OAK document as immutable.
Never publish a successor without a valid independent proof.
Preserve every protected invariant across succession.
Request evidence instead of guessing when review support is incomplete.
Keep review, compilation, verification, ratification, and publication separate.
</instructions>

<constants>
current-oak AS schema.governance.CURRENT_OAK: TEXT<<
<instructions>
Preserve exactly one node in every OAK document.
Preserve the closed seven-part OAK structure.
</instructions>
>>

protected-invariants AS schema.governance.PROTECTED_INVARIANTS: TEXT<<
One OAK document contains exactly one node.
The seven OAK parts remain closed.
Every published successor parses, resolves, and round-trips canonically.
>>
</constants>

<schemas>
<schema id="governance" name="Governance" purpose="Constrain the immutable and persistent values that govern succession.">
Current OAK: <CURRENT_OAK>
Protected invariants: <PROTECTED_INVARIANTS>
Revision: <REVISION>
Status: <STATUS>
Pending amendment id: <AMENDMENT_ID>
Pending amendment: <AMENDMENT>
Pending rationale: <RATIONALE>

WHERE:
- <CURRENT_OAK> is string; is non-empty; the current canonical OAK document.
- <PROTECTED_INVARIANTS> is string; is non-empty; the invariants every successor must preserve.
- <REVISION> is integer; is at least 1; the current positive revision.
- <STATUS> is string; is one of `idle`, `reviewing`, `needs-evidence`, `rejected`, `ratified`; the persistent succession status.
- <AMENDMENT_ID> is string; the pending amendment identifier, empty before a proposal.
- <AMENDMENT> is string; the pending amendment, empty before a proposal.
- <RATIONALE> is string; the pending rationale, empty before a proposal.
</schema>

<schema id="amendment-proposal" name="Amendment Proposal" purpose="Carry one amendment proposal into the successor machine.">
Amendment id: <AMENDMENT_ID>
Amendment: <AMENDMENT>
Rationale: <RATIONALE>
Evidence: <EVIDENCE>

WHERE:
- <AMENDMENT_ID> is string; is non-empty; the stable amendment identifier.
- <AMENDMENT> is string; is non-empty; the exact proposed change.
- <RATIONALE> is string; is non-empty; why the proposed change is needed.
- <EVIDENCE> is string; the supplied evidence, empty when none is available.
</schema>

<schema id="amendment-cycle" name="Amendment Cycle" purpose="Carry one new or resumed amendment through succession.">
Amendment id: <AMENDMENT_ID>
Amendment: <AMENDMENT>
Rationale: <RATIONALE>
Evidence: <EVIDENCE>
Resume: <RESUME>

WHERE:
- <AMENDMENT_ID> is string; is non-empty; the stable amendment identifier.
- <AMENDMENT> is string; is non-empty; the exact proposed change.
- <RATIONALE> is string; is non-empty; why the proposed change is needed.
- <EVIDENCE> is string; the supplied review evidence, empty when absent.
- <RESUME> is boolean; whether this cycle resumes a pending amendment.
</schema>

<schema id="evidence-supplement" name="Evidence Supplement" purpose="Carry evidence for the amendment retained in state.">
Amendment id: <AMENDMENT_ID>
Evidence: <EVIDENCE>

WHERE:
- <AMENDMENT_ID> is string; is non-empty; the pending amendment identifier.
- <EVIDENCE> is string; is non-empty; the evidence supplied for the pending amendment.
</schema>

<schema id="accepted-amendment" name="Accepted Amendment" purpose="Carry the independently reviewed amendment into compilation.">
Current OAK: <CURRENT_OAK>
Current revision: <CURRENT_REVISION>
Amendment id: <AMENDMENT_ID>
Amendment: <AMENDMENT>
Rationale: <RATIONALE>
Review findings: <REVIEW_FINDINGS>
Protected invariants: <PROTECTED_INVARIANTS>

WHERE:
- <CURRENT_OAK> is string; is non-empty; the current canonical OAK document.
- <CURRENT_REVISION> is integer; is at least 1; the revision being succeeded.
- <AMENDMENT_ID> is string; is non-empty; the accepted amendment identifier.
- <AMENDMENT> is string; is non-empty; the exact accepted amendment.
- <RATIONALE> is string; is non-empty; why the amendment is needed.
- <REVIEW_FINDINGS> is string; is non-empty; the independent findings that support compilation.
- <PROTECTED_INVARIANTS> is string; is non-empty; the invariants the compiler must preserve.
</schema>

<schema id="candidate-successor" name="Candidate Successor" purpose="Carry the compiled candidate before independent verification.">
<CANDIDATE_OAK>

WHERE:
- <CANDIDATE_OAK> is string; is non-empty; the compiled candidate OAK document.
</schema>

<schema id="successor-publication" name="Successor Publication" purpose="Publish one canonical successor only together with its amendment and proof.">
Decision: <DECISION>
Prior revision: <PRIOR_REVISION>
Next revision: <NEXT_REVISION>
Amendment id: <AMENDMENT_ID>
Amendment: <AMENDMENT>
Rationale: <RATIONALE>
Successor OAK: <CANDIDATE_OAK>
Valid: <VALID>
Parses: <PARSES>
Resolves: <RESOLVES>
Canonical: <CANONICAL>
Invariants preserved: <INVARIANTS_PRESERVED>
Scope exact: <SCOPE_EXACT>
Proof: <PROOF>

WHERE:
- <DECISION> is string; is one of `accept`; the ratified amendment decision.
- <PRIOR_REVISION> is integer; is at least 1; the revision that the successor replaces.
- <NEXT_REVISION> is integer; is at least 2; the published successor revision.
- <AMENDMENT_ID> is string; is non-empty; the ratified amendment identifier.
- <AMENDMENT> is string; is non-empty; the exact amendment implemented by the successor.
- <RATIONALE> is string; is non-empty; why the amendment was accepted.
- <CANDIDATE_OAK> is string; is non-empty; the canonical successor OAK document.
- <VALID> is boolean; is one of `true`; whether every required proof check passed.
- <PARSES> is boolean; is one of `true`; whether the successor parses as one OAK document.
- <RESOLVES> is boolean; is one of `true`; whether every successor target resolves.
- <CANONICAL> is boolean; is one of `true`; whether the successor round-trips exactly.
- <INVARIANTS_PRESERVED> is boolean; is one of `true`; whether every protected invariant remains true.
- <SCOPE_EXACT> is boolean; is one of `true`; whether the amendment explains the complete change.
- <PROOF> is string; is non-empty; the independent evidence carried with the successor.
</schema>
</schemas>

<state>
current-revision AS schema.governance.REVISION: 13
review-status AS schema.governance.STATUS: "idle"
pending-amendment-id AS schema.governance.AMENDMENT_ID: ""
pending-amendment AS schema.governance.AMENDMENT: ""
pending-rationale AS schema.governance.RATIONALE: ""
</state>

<triggers>
<trigger id="amendment-proposed">
GIVEN: true
WHEN: "An amendment is proposed."
THEN: process.govern-succession (AMENDMENT_ID=$interface.amendment-input.AMENDMENT_ID, AMENDMENT=$interface.amendment-input.AMENDMENT, RATIONALE=$interface.amendment-input.RATIONALE, EVIDENCE=$interface.amendment-input.EVIDENCE, RESUME=false)
</trigger>

<trigger id="evidence-supplied">
GIVEN: $state.review-status equals "needs-evidence"
WHEN: "Evidence for the pending amendment is supplied."
THEN: process.govern-succession (AMENDMENT_ID=$interface.evidence-input.AMENDMENT_ID, AMENDMENT=$state.pending-amendment, RATIONALE=$state.pending-rationale, EVIDENCE=$interface.evidence-input.EVIDENCE, RESUME=true)
</trigger>
</triggers>

<processes>
<process id="dispatch-review" name="Dispatch review" input="amendment_reviewer.oak.md#schema.amendment-review-request" output="amendment_reviewer.oak.md#schema.amendment-review">
ACT TOOL "agent.amendment-reviewer" input="amendment_reviewer.oak.md#schema.amendment-review-request" output="amendment_reviewer.oak.md#schema.amendment-review": For <AMENDMENT_ID>, challenge <AMENDMENT> with <RATIONALE> and <EVIDENCE> against <CURRENT_OAK> and <PROTECTED_INVARIANTS>, then produce <DECISION>, <REVIEW_FINDINGS>, and <EVIDENCE_REQUEST>. (CURRENT_OAK=$CURRENT_OAK, AMENDMENT_ID=$AMENDMENT_ID, AMENDMENT=$AMENDMENT, RATIONALE=$RATIONALE, EVIDENCE=$EVIDENCE, PROTECTED_INVARIANTS=$PROTECTED_INVARIANTS) -> DECISION, REVIEW_FINDINGS, EVIDENCE_REQUEST
</process>

<process id="dispatch-verification" name="Dispatch verification" input="successor_verifier.oak.md#schema.successor-verification-request" output="successor_verifier.oak.md#schema.successor-proof">
ACT TOOL "agent.successor-verifier" input="successor_verifier.oak.md#schema.successor-verification-request" output="successor_verifier.oak.md#schema.successor-proof": Verify <CANDIDATE_OAK> against <CURRENT_OAK>, <AMENDMENT>, and <PROTECTED_INVARIANTS>, then produce <VALID>, <PARSES>, <RESOLVES>, <CANONICAL>, <INVARIANTS_PRESERVED>, <SCOPE_EXACT>, and <PROOF>. (CURRENT_OAK=$CURRENT_OAK, CANDIDATE_OAK=$CANDIDATE_OAK, AMENDMENT=$AMENDMENT, PROTECTED_INVARIANTS=$PROTECTED_INVARIANTS) -> VALID, PARSES, RESOLVES, CANONICAL, INVARIANTS_PRESERVED, SCOPE_EXACT, PROOF
</process>

<process id="govern-succession" name="Govern succession" input="schema.amendment-cycle">
IF $RESUME equals true:
  THEN:
    ASSERT $AMENDMENT_ID equals $state.pending-amendment-id
      MESSAGE "The evidence does not match the pending amendment."
SET state.pending-amendment-id = $AMENDMENT_ID
SET state.pending-amendment = $AMENDMENT
SET state.pending-rationale = $RATIONALE
SET state.review-status = "reviewing"
CALL process.dispatch-review (CURRENT_OAK=$constant.current-oak, AMENDMENT_ID=$AMENDMENT_ID, AMENDMENT=$AMENDMENT, RATIONALE=$RATIONALE, EVIDENCE=$EVIDENCE, PROTECTED_INVARIANTS=$constant.protected-invariants) -> DECISION, REVIEW_FINDINGS, EVIDENCE_REQUEST
IF $DECISION equals "accept":
  THEN:
    ACT TOOL "oak.compile-successor" input="schema.accepted-amendment" output="schema.candidate-successor": Apply <AMENDMENT_ID>: <AMENDMENT> with <RATIONALE> and <REVIEW_FINDINGS> to <CURRENT_OAK> at <CURRENT_REVISION> while preserving <PROTECTED_INVARIANTS>, then produce <CANDIDATE_OAK>. (CURRENT_OAK=$constant.current-oak, CURRENT_REVISION=$state.current-revision, AMENDMENT_ID=$AMENDMENT_ID, AMENDMENT=$AMENDMENT, RATIONALE=$RATIONALE, REVIEW_FINDINGS=$REVIEW_FINDINGS, PROTECTED_INVARIANTS=$constant.protected-invariants) -> CANDIDATE_OAK
    CALL process.dispatch-verification (CURRENT_OAK=$constant.current-oak, CANDIDATE_OAK=$CANDIDATE_OAK, AMENDMENT=$AMENDMENT, PROTECTED_INVARIANTS=$constant.protected-invariants) -> VALID, PARSES, RESOLVES, CANONICAL, INVARIANTS_PRESERVED, SCOPE_EXACT, PROOF
    ASSERT $VALID equals true
      MESSAGE "The successor proof is not valid."
    ASSERT $PARSES equals true
      MESSAGE "The successor does not parse."
    ASSERT $RESOLVES equals true
      MESSAGE "The successor does not resolve."
    ASSERT $CANONICAL equals true
      MESSAGE "The successor is not canonical."
    ASSERT $INVARIANTS_PRESERVED equals true
      MESSAGE "The successor breaks a protected invariant."
    ASSERT $SCOPE_EXACT equals true
      MESSAGE "The successor contains an unexplained change."
    ACT Advance <CURRENT_REVISION> and produce <PRIOR_REVISION> and <NEXT_REVISION>. (CURRENT_REVISION=$state.current-revision) -> PRIOR_REVISION, NEXT_REVISION
    SET state.current-revision = $NEXT_REVISION
    SET state.review-status = "ratified"
    EMIT interface.successor-output (DECISION=$DECISION, AMENDMENT_ID=$AMENDMENT_ID, AMENDMENT=$AMENDMENT, RATIONALE=$RATIONALE, PRIOR_REVISION=$PRIOR_REVISION, NEXT_REVISION=$NEXT_REVISION, CANDIDATE_OAK=$CANDIDATE_OAK, VALID=$VALID, PARSES=$PARSES, RESOLVES=$RESOLVES, CANONICAL=$CANONICAL, INVARIANTS_PRESERVED=$INVARIANTS_PRESERVED, SCOPE_EXACT=$SCOPE_EXACT, PROOF=$PROOF)
  ELSE:
    IF $DECISION equals "needs-evidence":
      THEN:
        SET state.review-status = "needs-evidence"
      ELSE:
        SET state.review-status = "rejected"
    EMIT interface.review-outcome-output (DECISION=$DECISION, REVIEW_FINDINGS=$REVIEW_FINDINGS, EVIDENCE_REQUEST=$EVIDENCE_REQUEST)
</process>
</processes>

<interfaces>
<interface id="amendment-input" direction="in" schema="schema.amendment-proposal">
The proposed amendment, rationale, and available evidence.
</interface>

<interface id="evidence-input" direction="in" schema="schema.evidence-supplement">
The evidence supplied for the amendment retained in state.
</interface>

<interface id="review-outcome-output" direction="out" schema="amendment_reviewer.oak.md#schema.amendment-review">
The independent decision returned when succession does not proceed.
</interface>

<interface id="successor-output" direction="out" schema="schema.successor-publication">
The canonical successor published only together with its proof.
</interface>
</interfaces>