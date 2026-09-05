<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Interface: One identified one-way crossing at the active document boundary.
Target only an EMITS interface from EMIT.
Use interfaces only in the active OAK document.
Use the same resolved schema for a receive source and selected process input.
Select only a local RECEIVES interface as a trigger source.
</instructions>

<constants>
example-1: "request RECEIVES schema.request-shape"

example-2: "result EMITS ../shared/contracts.oak.md#schema.result-shape: \"Returned only to the coordinator.\""

syntax-reference: "outputs/oak.ebnf"

grammar: TEXT<<
surface_interface_receives = ? <ID> RECEIVES <SCHEMA_ID>: <DESCRIPTION> ? ;
surface_interface_emits = ? <ID> EMITS <SCHEMA_ID>: <DESCRIPTION> ? ;
>>
</constants>

<schemas>
<schema id="interface-receives" name="Interface interface-receives" purpose="One identified one-way crossing at the active document boundary.">
<ID> RECEIVES <SCHEMA_ID>: <DESCRIPTION>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <SCHEMA_ID> is string; is non-empty; The local or relative schema target that defines the instance..
- <DESCRIPTION> is string; Boundary meaning absent from the interface id and schema..
</schema>

<schema id="interface-emits" name="Interface interface-emits" purpose="One identified one-way crossing at the active document boundary.">
<ID> EMITS <SCHEMA_ID>: <DESCRIPTION>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <SCHEMA_ID> is string; is non-empty; The local or relative schema target that defines the instance..
- <DESCRIPTION> is string; Boundary meaning absent from the interface id and schema..
</schema>
</schemas>
