~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

State: One JSON value that can change while the interpreter runs.
~~~~

~~~~constants
example-1: "status: \"ready\""

grammar: TEXT<<
surface_state = ? <ID>: <VALUE> ? ;
>>
~~~~

~~~~schemas
~~~schema;id="state";name="State";purpose="One JSON value that can change while the interpreter runs."
<ID>: <VALUE>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The JSON value that can change..
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
