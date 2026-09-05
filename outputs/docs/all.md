<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

All: Every child condition must be true in authored order.
Give each ALL or ANY condition at least two children.
</instructions>

<constants>
example-1: "ALL($state.status equals \"ready\", $state.count is greater than 0)"

syntax-reference: "outputs/oak.ebnf"

grammar: TEXT<<
surface_condition_all = all_condition ;
>>
</constants>

<schemas>
<schema id="condition-all" name="All" purpose="Every child condition must be true in authored order.">
ALL(<CONDITIONS>)

WHERE:
- <CONDITIONS> is string; is non-empty; The child conditions in authored order..
</schema>
</schemas>
