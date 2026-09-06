<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Process: One named ordered way to do a task.
Do not redefine a visible immutable process binding.
Make every process output schema placeholder visible after successful completion.
Select a process with an input schema from a source-backed trigger.
Use the same resolved schema for a receive source and selected process input.
Read only a visible prior process-local binding.
Remove a process step after a path that always fails.
</instructions>

<constants>
statement-body-migration: {"python": "Import Statement instead of Step. Process, Foreach, While, and Par take body instead of steps. If keeps then and otherwise. StatementModel, iter_statements, statement_values, and statements modules replace the corresponding step names without forwarding aliases.", "models": "Model dumps and JSON Schema use ordinary body arrays. Old steps fields, including mixed steps/body input, are rejected.", "json-ld": "Process, Foreach, While, and Par encode body as an explicit @list object. Instruction.body remains a string with no global list container. The ordered then term replaces thenSteps; otherwise is unchanged.", "unchanged": "OAK keywords, grouping delimiters, literal JSON keys, operation kinds, schema identities, execution scope, and stable diagnostic codes are unchanged. This is not Python or JSON-LD wire compatibility."}

example-1: "<process id=\"normalise\" name=\"Normalise name\" input=\"schema.raw-name\" output=\"schema.normal-name\">\nACT Normalise <RAW_NAME> into <NORMAL_NAME>. (RAW_NAME=$RAW_NAME) -> NORMAL_NAME\n</process>"

syntax-reference: "outputs/oak.ebnf"

grammar: TEXT<<
surface_process = ? <process id="<ID>" name="<NAME>" input="<INPUT>" output="<OUTPUT>">
<BODY>
</process> ? ;
>>
</constants>

<schemas>
<schema id="process" name="Process" purpose="One named ordered way to do a task.">
<process id="<ID>" name="<NAME>" input="<INPUT>" output="<OUTPUT>">
<BODY>
</process>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <NAME> is string; is non-empty; The two-word process display name..
- <INPUT> is string; The optional schema that defines initial local bindings..
- <OUTPUT> is string; The optional schema that defines successful local outputs..
- <BODY> is string; is non-empty; The typed process statement body in authored order..
</schema>
</schemas>
