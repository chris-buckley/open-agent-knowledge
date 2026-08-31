<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

LiteralValue: One authored JSON value.
</instructions>

<constants>
example-1: "\"critical\""

grammar: TEXT<<
surface_value_literal = ? <VALUE> ? ;
>>
</constants>

<schemas>
<schema id="value-literal" name="LiteralValue" purpose="One authored JSON value.">
<VALUE>

WHERE:
- <VALUE> is string; is non-empty; The authored JSON value..
</schema>
</schemas>
