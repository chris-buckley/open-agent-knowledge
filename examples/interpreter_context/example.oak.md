<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.

Reject empty or whitespace-only titles; accept other titles without rewriting them.
</instructions>

<schemas>
<schema id="title" name="Title" purpose="Carry a title that may need rejection.">
Title: <TITLE>

WHERE:
- <TITLE> is string; the unmodified title to assess.
</schema>

<schema id="review" name="Review" purpose="Carry the title decision and its reason.">
## <VERDICT>

<REASON>

WHERE:
- <VERDICT> is string; is one of `accept`, `reject`; whether the title is acceptable.
- <REASON> is string; is non-empty; the reason for the decision.
</schema>
</schemas>

<triggers>
title-requested(
  event="A title needs review.",
  source=interface.title-input,
  process=process.review-title,
)
</triggers>

<processes>
<process id="review-title" name="Review title" input="schema.title" output="schema.review">
ACT input="schema.title" output="schema.review": Assess <TITLE> under the title policy and produce <VERDICT> and <REASON>. (
  TITLE=$TITLE,
) -> VERDICT, REASON
EMIT interface.review-output
</process>
</processes>

<interfaces>
title-input RECEIVES schema.title
review-output EMITS schema.review
</interfaces>