<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Conditions are typed trees; ALL, ANY, and NOT compose comparisons; ASSERT fails a false condition; FOREACH is sequential; WHILE tests before each bounded iteration; PAR outputs become visible only at JOIN.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
Text after `: ` states boundary meaning absent from the interface schema.
AS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
State holds values that persist and can change while processes run.
Each trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
capability: "review-items/v1"

host-boundary: "The host serializes arrivals and writers, binds local instance roots, and durably stores only successful returned checkpoints. Shared OAK declarations are initial values, never rewritten after a run. Schema validity is not file or effect verification."
</constants>

<schemas>
<schema id="review-request" purpose="Prepare one review for an explicitly selected owner and local instance.">
Owner: <OWNER>
Instance: <INSTANCE>
Record: <ID>
Text: <TEXT>
Policy: <POLICY_ID>
Retention: <RETENTION>

WHERE:
- <OWNER> is string; matches `^[a-z0-9][a-z0-9\-]{0,63}$`.
- <ID> is string; matches `^[a-z0-9][a-z0-9\-]{0,63}$`.
- <POLICY_ID> is string; matches `^[a-z0-9][a-z0-9\-]{0,63}$`.
- <INSTANCE> is string; is non-empty.
- <TEXT> is string; is non-empty.
- <RETENTION> is string; is one of ``, `full`, `summary`; empty reuses a saved choice and requires a decision when none exists.
</schema>

<schema id="resume-request" purpose="Publish only the pending review belonging to this owner and instance.">
Owner: <OWNER>
Instance: <INSTANCE>
Record: <ID>

WHERE:
- <OWNER> is string; is non-empty.
- <INSTANCE> is string; is non-empty.
- <ID> is string; is non-empty.
</schema>

<schema id="preparation" purpose="Return inspected policy and the actual selected-input fingerprint.">
Term: <TERM>
Retention: <MODE>
Snapshot: <SNAPSHOT>

WHERE:
- <TERM> is string; is non-empty.
- <MODE> is string; is one of `full`, `summary`.
- <SNAPSHOT> is string; is non-empty.
</schema>

<schema id="checkpoint" purpose="Retain the exact pending work across host-driven arrivals.">
Owner: <OWNER>
Instance: <INSTANCE>
Phase: <PHASE>
Record: <ID>
Text: <TEXT>
Policy: <POLICY_ID>
Category: <CATEGORY>
Retention: <MODE>
Snapshot: <SNAPSHOT>

WHERE:
- <OWNER> is string.
- <INSTANCE> is string.
- <ID> is string.
- <TEXT> is string.
- <POLICY_ID> is string.
- <SNAPSHOT> is string.
- <PHASE> is string; is one of `idle`, `prepared`.
- <CATEGORY> is string; is one of ``, `match`, `other`.
- <MODE> is string; is one of ``, `full`, `summary`.
</schema>

<schema id="read-back" purpose="Report the actual file pair after reconciliation and read-back.">
Reference: <REFERENCE>
Digest: <SHA256>
Verified: <VERIFIED>

WHERE:
- <REFERENCE> is string; is non-empty.
- <SHA256> is string; matches `^[0-9a-f]{64}$`.
- <VERIFIED> is boolean.
</schema>

<schema id="review-progress" purpose="Report preparation without claiming record publication.">
Prepared: <ID>

WHERE:
- <ID> is string; is non-empty.
</schema>

<schema id="review-result" purpose="Return a reviewed record only after successful file-pair verification.">
Owner: <OWNER>
Record: <ID>
Category: <CATEGORY>
Reference: <REFERENCE>
Digest: <SHA256>

WHERE:
- <OWNER> is string; is non-empty.
- <ID> is string; is non-empty.
- <REFERENCE> is string; is non-empty.
- <CATEGORY> is string; is one of `match`, `other`.
- <SHA256> is string; matches `^[0-9a-f]{64}$`.
</schema>
</schemas>

<state>
owner AS schema.checkpoint.OWNER: ""
instance AS schema.checkpoint.INSTANCE: ""
phase AS schema.checkpoint.PHASE: "idle"
id AS schema.checkpoint.ID: ""
text AS schema.checkpoint.TEXT: ""
policy-id AS schema.checkpoint.POLICY_ID: ""
category AS schema.checkpoint.CATEGORY: ""
mode AS schema.checkpoint.MODE: ""
snapshot AS schema.checkpoint.SNAPSHOT: ""
</state>

<triggers>
review-requested(
  event="A review is requested.",
  source=interface.request,
  process=process.prepare-review,
)
review-resumed(
  event="A prepared review is resumed.",
  source=interface.resume,
  process=process.publish-review,
)
</triggers>

<processes>
<process id="prepare-review" name="Prepare review" input="schema.review-request">
ASSERT $state.phase equals "idle"
  MESSAGE "A review is already pending."
ASSERT ANY($state.owner equals "", $state.owner equals $OWNER)
  MESSAGE "The checkpoint belongs to another owner."
ASSERT ANY($state.instance equals "", $state.instance equals $INSTANCE)
  MESSAGE "The checkpoint belongs to another instance."
ACT output="schema.preparation": Bind <OWNER>/<CAPABILITY> to explicit <INSTANCE> under <MEMORY>. Reuse saved retention or require an actual first-use <RETENTION> choice. Verify actual Git exclusions and tracked status, read only <POLICY_ID> through its index, refuse a reused <ID>, and return <TERM>, <MODE> and observed <SNAPSHOT>. Never overwrite an existing instance or use the shared source path as its root. (
  OWNER=$OWNER,
  INSTANCE=$INSTANCE,
  ID=$ID,
  POLICY_ID=$POLICY_ID,
  RETENTION=$RETENTION,
  CAPABILITY=$constant.capability,
  MEMORY=$memory.oak.md#constant.workflow,
) -> TERM, MODE, SNAPSHOT
CALL classifier.oak.md#process.classify (TEXT=$TEXT, TERM=$TERM) -> CATEGORY
SET state.owner = $OWNER
SET state.instance = $INSTANCE
SET state.id = $ID
SET state.text = $TEXT
SET state.policy-id = $POLICY_ID
SET state.category = $CATEGORY
SET state.mode = $MODE
SET state.snapshot = $SNAPSHOT
SET state.phase = "prepared"
EMIT interface.progress (ID=$ID)
</process>

<process id="publish-review" name="Publish review" input="schema.resume-request">
ASSERT $state.phase equals "prepared"
  MESSAGE "No prepared review can resume."
ASSERT $state.owner equals $OWNER
  MESSAGE "Resume targets a different owner."
ASSERT $state.instance equals $INSTANCE
  MESSAGE "Resume targets a different instance."
ASSERT $state.id equals $ID
  MESSAGE "Resume targets a different id."
ACT output="schema.read-back": Reconcile and publish pending <ID> for <OWNER>/<CAPABILITY> in <INSTANCE> under <MEMORY>. Check <SNAPSHOT>, one writer, <POLICY_ID> and saved <MODE>. Write the JSON record for <TEXT>/<CATEGORY> before its stable CSV index row; resume an exact orphan or verify an exact published pair without rewriting it. Preserve pending and tool-owned records. Return <REFERENCE>, computed <SHA256> and <VERIFIED> from actual read-back; an unknown conflict must fail. (
  OWNER=$state.owner,
  INSTANCE=$state.instance,
  ID=$state.id,
  TEXT=$state.text,
  POLICY_ID=$state.policy-id,
  CATEGORY=$state.category,
  MODE=$state.mode,
  SNAPSHOT=$state.snapshot,
  CAPABILITY=$constant.capability,
  MEMORY=$memory.oak.md#constant.workflow,
) -> REFERENCE, SHA256, VERIFIED
ASSERT $VERIFIED equals true
  MESSAGE "Record read-back did not pass."
EMIT interface.result (
  OWNER=$state.owner,
  ID=$state.id,
  CATEGORY=$state.category,
  REFERENCE=$REFERENCE,
  SHA256=$SHA256,
)
SET state.phase = "idle"
SET state.id = ""
SET state.text = ""
SET state.policy-id = ""
SET state.category = ""
SET state.mode = ""
SET state.snapshot = ""
</process>
</processes>

<interfaces>
request RECEIVES schema.review-request: "Prepare only this owner and instance, without publishing a completed review."
resume RECEIVES schema.resume-request: "Resume this exact pending review; completion is rejected if identity or inputs changed."
progress EMITS schema.review-progress: "The host persists the returned checkpoint before acknowledging preparation."
result EMITS schema.review-result: "Return a verified record reference; delivery and external effects remain host responsibilities."
</interfaces>