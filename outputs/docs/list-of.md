<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

ListOf: The bound value is items of one datatype joined by one separator.
</instructions>

<constants>
example-1: "is a list of integer joined by `, `"

grammar: TEXT<<
surface_constraint_list_of = ? is a list of <ITEM> joined by `<SEPARATOR>` ? ;
>>
</constants>

<schemas>
<schema id="constraint-list-of" name="ListOf" purpose="The bound value is items of one datatype joined by one separator.">
is a list of <ITEM> joined by `<SEPARATOR>`

WHERE:
- <ITEM> is string; is non-empty; The datatype of every item..
- <SEPARATOR> is string; is non-empty; The text between items..
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
