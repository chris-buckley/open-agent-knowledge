<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

AtLeast: The bound value is at least a number or another placeholder value.
</instructions>

<constants>
example-1: "is at least 1"

grammar: TEXT<<
surface_constraint_at_least = ? is at least <VALUE> ? ;
>>
</constants>

<schemas>
<schema id="constraint-at-least" name="AtLeast" purpose="The bound value is at least a number or another placeholder value.">
is at least <VALUE>

WHERE:
- <VALUE> is string; is non-empty; A number or a placeholder of the same schema..
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
