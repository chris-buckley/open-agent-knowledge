<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

OneOf: The bound value is one of the listed values.
</instructions>

<constants>
example-1: "is one of `draft`, `final`"

syntax-reference: "outputs/oak.ebnf"

grammar: TEXT<<
surface_constraint_one_of = ? is one of <VALUES> ? ;
>>
</constants>

<schemas>
<schema id="constraint-one-of" name="OneOf" purpose="The bound value is one of the listed values.">
is one of <VALUES>

WHERE:
- <VALUES> is string; is non-empty; The allowed values..
</schema>
</schemas>
