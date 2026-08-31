<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Foreach: One deterministic sequential iteration over a JSON list.
Use a new loop binding that does not shadow a visible binding.
Give FOREACH a value that resolves to a JSON list.
</instructions>

<constants>
example-1: "FOREACH ITEM IN [\"a\", \"b\"]:\n  ACT Transform <ITEM> into <RESULT>. (ITEM=$ITEM) -> RESULT"

grammar: TEXT<<
surface_step_foreach = ? FOREACH <BINDING> IN <VALUE>:
  <STEPS> ? ;
>>
</constants>

<schemas>
<schema id="step-foreach" name="Foreach" purpose="One deterministic sequential iteration over a JSON list.">
FOREACH <BINDING> IN <VALUE>:
  <STEPS>

WHERE:
- <BINDING> is string; is non-empty; The immutable loop binding..
- <VALUE> is string; is non-empty; The process value that must resolve to a JSON list..
- <STEPS> is string; is non-empty; The sequential iteration steps..
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
