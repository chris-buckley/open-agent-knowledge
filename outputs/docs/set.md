<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Set: One local state write.
Read and write state only in the active OAK document.
</instructions>

<constants>
example-1: "SET state.status = \"complete\""

syntax-reference: "outputs/oak.ebnf"

grammar: TEXT<<
surface_step_set = set_statement ;
>>
</constants>

<schemas>
<schema id="step-set" name="Set" purpose="One local state write.">
SET <STATE> = <VALUE>

WHERE:
- <STATE> is string; is non-empty; The local state target to write..
- <VALUE> is string; is non-empty; The process value written to state..
</schema>
</schemas>
