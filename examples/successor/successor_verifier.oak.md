<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
Text after `: ` states boundary meaning absent from the interface schema.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.

Verify the candidate independently from the compiler that produced it.
Require the candidate to parse, resolve, and round-trip canonically.
Require every protected invariant and current instruction to remain true.
Require the candidate change to equal the accepted amendment exactly.
Do not alter, ratify, or publish the candidate.
</instructions>

<schemas>
<schema id="successor-verification-request" name="Successor Verification Request" purpose="Carry the current and candidate OAK documents with their governing amendment.">
Current OAK: <CURRENT_OAK>
Candidate OAK: <CANDIDATE_OAK>
Amendment: <AMENDMENT>
Protected invariants: <PROTECTED_INVARIANTS>

WHERE:
- <CURRENT_OAK> is string; is non-empty; the current canonical OAK document.
- <CANDIDATE_OAK> is string; is non-empty; the proposed canonical successor document.
- <AMENDMENT> is string; is non-empty; the exact accepted amendment.
- <PROTECTED_INVARIANTS> is string; is non-empty; the invariants every successor must preserve.
</schema>

<schema id="successor-proof" name="Successor Proof" purpose="Carry the independent machine-verifiable proof for one candidate successor.">
Valid: <VALID>
Parses: <PARSES>
Resolves: <RESOLVES>
Canonical: <CANONICAL>
Invariants preserved: <INVARIANTS_PRESERVED>
Scope exact: <SCOPE_EXACT>
Proof: <PROOF>

WHERE:
- <VALID> is boolean; whether every required proof check passed.
- <PARSES> is boolean; whether the candidate parses as one OAK document.
- <RESOLVES> is boolean; whether every candidate target resolves.
- <CANONICAL> is boolean; whether parsing and rendering reproduces the candidate exactly.
- <INVARIANTS_PRESERVED> is boolean; whether the protected invariants remain true.
- <SCOPE_EXACT> is boolean; whether the amendment explains the complete candidate change.
- <PROOF> is string; is non-empty; the concise evidence for the proof checks.
</schema>
</schemas>

<triggers>
successor-verification-requested(
  event="A successor verification is requested.",
  source=interface.verification-request,
  process=process.verify-successor,
)
</triggers>

<processes>
<process id="verify-successor" name="Verify successor" input="schema.successor-verification-request" output="schema.successor-proof">
ACT TOOL "oak.verify-successor" input="schema.successor-verification-request" output="schema.successor-proof": Verify <CANDIDATE_OAK> against <CURRENT_OAK>, <AMENDMENT>, and <PROTECTED_INVARIANTS>, then produce <VALID>, <PARSES>, <RESOLVES>, <CANONICAL>, <INVARIANTS_PRESERVED>, <SCOPE_EXACT>, and <PROOF>. (
  CURRENT_OAK=$CURRENT_OAK,
  CANDIDATE_OAK=$CANDIDATE_OAK,
  AMENDMENT=$AMENDMENT,
  PROTECTED_INVARIANTS=$PROTECTED_INVARIANTS,
) -> VALID, PARSES, RESOLVES, CANONICAL, INVARIANTS_PRESERVED, SCOPE_EXACT, PROOF
EMIT interface.proof
</process>
</processes>

<interfaces>
verification-request RECEIVES schema.successor-verification-request: "The candidate and governance context supplied by the coordinator."
proof EMITS schema.successor-proof: "The independent proof returned to the successor coordinator."
</interfaces>