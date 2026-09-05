<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

AtMost: The bound value is at most a number or another placeholder value.
</instructions>

<constants>
example-1: "is at most 160"

syntax-reference: "outputs/oak.ebnf"

grammar: TEXT<<
surface_constraint_at_most = ? is at most <VALUE> ? ;
>>
</constants>

<schemas>
<schema id="constraint-at-most" name="AtMost" purpose="The bound value is at most a number or another placeholder value.">
is at most <VALUE>

WHERE:
- <VALUE> is string; is non-empty; A number or a placeholder of the same schema..
</schema>
</schemas>
