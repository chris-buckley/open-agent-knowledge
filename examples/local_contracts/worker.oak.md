<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<schemas>
<schema id="raw" purpose="Supply raw text for trimming without interpreting its public use.">
Raw: <RAW_TEXT>

WHERE:
- <RAW_TEXT> is string.
</schema>

<schema id="trimmed" purpose="Return trimmed text, including empty or multiline text.">
Trimmed: <CLEAN_TEXT>

WHERE:
- <CLEAN_TEXT> is string.
</schema>
</schemas>

<processes>
<process id="trim" name="Trim text" input="schema.raw" output="schema.trimmed">
ACT input="schema.raw" output="schema.trimmed": Remove leading and trailing whitespace from <RAW_TEXT> to produce <CLEAN_TEXT>. (
  RAW_TEXT=$RAW_TEXT,
) -> CLEAN_TEXT
</process>
</processes>