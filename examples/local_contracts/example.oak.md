<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
Text after `: ` states boundary meaning absent from the interface schema.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
delivery-boundary: "Public schemas are local. Execution needs worker.oak.md and a trimming host; the complete scenario supplies both as a deterministic demonstration."
</constants>

<schemas>
<schema id="text" purpose="Supply text to turn into a nonempty single-line title.">
Text: <TEXT>

WHERE:
- <TEXT> is string; text whose outer whitespace will be removed.
</schema>

<schema id="title" purpose="Publish a title only after the public title constraints pass.">
# <TITLE>

WHERE:
- <TITLE> is string; is non-empty; has at most 1 line; the trimmed nonempty single-line title.
</schema>
</schemas>

<triggers>
text-received(
  event="A title is requested from supplied text.",
  source=interface.title-request,
  process=process.make-title,
)
</triggers>

<processes>
<process id="make-title" name="Make title" input="schema.text">
CALL worker.oak.md#process.trim (RAW_TEXT=$TEXT) -> CLEAN_TEXT
EMIT interface.title-result (TITLE=$CLEAN_TEXT)
</process>
</processes>

<interfaces>
title-request RECEIVES schema.text: "Request a trimmed title, not document publication. Blank or multiline results fail without emission."
title-result EMITS schema.title: "Return the validated title to the requester. Emission does not prove host delivery."
</interfaces>