<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<schemas>
<schema id="item" purpose="Classify supplied text against one supplied term.">
Text: <TEXT>
Term: <TERM>

WHERE:
- <TEXT> is string; is non-empty.
- <TERM> is string; is non-empty.
</schema>

<schema id="category" purpose="Return whether the supplied term occurs in the text.">
Category: <CATEGORY>

WHERE:
- <CATEGORY> is string; is one of `match`, `other`.
</schema>
</schemas>

<processes>
<process id="classify" name="Classify item" input="schema.item" output="schema.category">
ACT input="schema.item" output="schema.category": Classify <TEXT> as match when it contains <TERM> case-insensitively, otherwise other. Return <CATEGORY> without reading or writing files. (
  TEXT=$TEXT,
  TERM=$TERM,
) -> CATEGORY
</process>
</processes>