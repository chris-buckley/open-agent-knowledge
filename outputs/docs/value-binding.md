<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

ValueBinding: One placeholder bound to one process value.
</instructions>

<constants>
example-1: "REQUEST=$interface.request.REQUEST"

grammar: TEXT<<
surface_value_binding_line = ? <PLACEHOLDER>=<VALUE> ? ;
>>
</constants>

<schemas>
<schema id="value-binding-line" name="ValueBinding" purpose="One placeholder bound to one process value.">
<PLACEHOLDER>=<VALUE>

WHERE:
- <PLACEHOLDER> is string; is non-empty; The placeholder receiving the process value..
- <VALUE> is string; is non-empty; The process value bound to the placeholder..
</schema>
</schemas>
