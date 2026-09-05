<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Lines: The bound value has one positive line-count bound.
Keep a lines minimum at or below its maximum.
Give each lines constraint a minimum, maximum, or both.
</instructions>

<constants>
example-1: "has at most 1 line"

syntax-reference: "outputs/oak.ebnf"

grammar: TEXT<<
surface_constraint_lines = ? has <MIN> to <MAX> lines ? ;
>>
</constants>

<schemas>
<schema id="constraint-lines" name="Lines" purpose="The bound value has one positive line-count bound.">
has <MIN> to <MAX> lines

WHERE:
- <MIN> is string; The fewest lines..
- <MAX> is string; The most lines..
</schema>
</schemas>
