<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Where: One placeholder, its constraints, examples, and description.
Make every WHERE example satisfy its local constraints.
Do not give examples to a WHERE entry with placeholder-valued bounds.
</instructions>

<constants>
example-1: "- <OUTLINE_TITLE> is string; title for the outline."

grammar: TEXT<<
surface_where = ? - <PLACEHOLDER> <CONSTRAINTS> <EXAMPLES> <DESCRIPTION>. ? ;
>>
</constants>

<schemas>
<schema id="where" name="Where" purpose="One placeholder, its constraints, examples, and description.">
- <PLACEHOLDER> <CONSTRAINTS> <EXAMPLES> <DESCRIPTION>.

WHERE:
- <PLACEHOLDER> is string; is non-empty; The bare placeholder name..
- <CONSTRAINTS> is string; is non-empty; The constraints every bound value must satisfy..
- <EXAMPLES> is string; Values that satisfy every locally resolvable constraint..
- <DESCRIPTION> is string; What the placeholder holds, in one line..
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
