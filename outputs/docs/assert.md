~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Assert: One required condition that aborts the transaction when false.
Remove or repair an assertion that is statically false.
Remove an assertion that is statically true.
~~~~

~~~~constants
example-1: "ASSERT $RESULT does not equal \"\"\n  MESSAGE \"The result must not be empty.\""

grammar: TEXT<<
surface_step_assert = ? ASSERT <CONDITION>
MESSAGE <MESSAGE> ? ;
>>
~~~~

~~~~schemas
~~~schema;id="step-assert";name="Assert";purpose="One required condition that aborts the transaction when false."
ASSERT <CONDITION>
MESSAGE <MESSAGE>

WHERE:
- <CONDITION> is string; is non-empty; The required recursive condition..
- <MESSAGE> is string; is non-empty; The optional assertion failure message..
~~~
~~~~

~~~~state
~~~~

~~~~triggers
~~~~

~~~~processes
~~~~

~~~~interfaces
~~~~
