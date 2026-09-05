<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Regex: The bound value matches one anchored portable rust-regex pattern.
</instructions>

<constants>
example-1: "matches `^[0-9]+$`"

syntax-reference: "outputs/oak.ebnf"

grammar: TEXT<<
surface_constraint_regex = ? matches `<PATTERN>` ? ;
>>
</constants>

<schemas>
<schema id="constraint-regex" name="Regex" purpose="The bound value matches one anchored portable rust-regex pattern.">
matches `<PATTERN>`

WHERE:
- <PATTERN> is string; is non-empty; The whole-value portable pattern..
</schema>
</schemas>
