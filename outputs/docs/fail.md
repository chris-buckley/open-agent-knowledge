~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Fail: One explicit process failure.
~~~~

~~~~constants
example-1: "FAIL \"The result is empty.\""

grammar: TEXT<<
surface_step_fail = ? FAIL <MESSAGE> ? ;
>>
~~~~

~~~~schemas
~~~schema;id="step-fail";name="Fail";purpose="One explicit process failure."
FAIL <MESSAGE>

WHERE:
- <MESSAGE> is string; is non-empty; The failure message..
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
