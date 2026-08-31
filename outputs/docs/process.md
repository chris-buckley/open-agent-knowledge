<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Process: One named ordered way to do a task.
Do not redefine a visible immutable process binding.
Make every process output schema placeholder visible after successful completion.
Read only a visible prior process-local binding.
Remove a process step after a path that always fails.
</instructions>

<constants>
example-1: "<process id=\"normalise\" name=\"Normalise name\" input=\"schema.raw-name\" output=\"schema.normal-name\">\nACT Normalise <RAW_NAME> into <NORMAL_NAME>. (RAW_NAME=$RAW_NAME) -> NORMAL_NAME\n</process>"

grammar: TEXT<<
surface_process = ? <process id="<ID>" name="<NAME>" input="<INPUT>" output="<OUTPUT>">
<STEPS>
</process> ? ;
>>
</constants>

<schemas>
<schema id="process" name="Process" purpose="One named ordered way to do a task.">
<process id="<ID>" name="<NAME>" input="<INPUT>" output="<OUTPUT>">
<STEPS>
</process>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <NAME> is string; is non-empty; The two-word process display name..
- <INPUT> is string; The optional schema that defines initial local bindings..
- <OUTPUT> is string; The optional schema that defines successful local outputs..
- <STEPS> is string; is non-empty; The typed process steps in authored order..
</schema>
</schemas>
