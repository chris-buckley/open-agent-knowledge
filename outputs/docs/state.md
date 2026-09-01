<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

State: One JSON value that can change while the interpreter runs.
Give a schema binding both a schema target and a placeholder.
Make every schema-bound value satisfy its placeholder constraints.
Bind a placeholder present in the selected schema.
Do not bind a placeholder that has a placeholder-valued bound.
</instructions>

<constants>
example-1: "status: \"ready\""

grammar: TEXT<<
surface_state = ? <ID> AS <SCHEMA_ID>.<PLACEHOLDER>: <VALUE> ? ;
>>
</constants>

<schemas>
<schema id="state" name="State" purpose="One JSON value that can change while the interpreter runs.">
<ID> AS <SCHEMA_ID>.<PLACEHOLDER>: <VALUE>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <SCHEMA_ID> is string; The optional local or relative schema target whose placeholder constrains every value..
- <PLACEHOLDER> is string; The schema placeholder every value must satisfy..
- <VALUE> is string; is non-empty; The JSON value that can change..
</schema>
</schemas>
