<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

NonEmpty: The bound value has at least one character or item.
</instructions>

<constants>
example-1: "is non-empty"

grammar: TEXT<<
surface_constraint_non_empty = ? is non-empty ? ;
>>
</constants>

<schemas>
<schema id="constraint-non-empty" name="NonEmpty" purpose="The bound value has at least one character or item.">
is non-empty

WHERE:
</schema>
</schemas>

<state>
</state>

<triggers>
</triggers>

<processes>
</processes>

<interfaces>
</interfaces>
