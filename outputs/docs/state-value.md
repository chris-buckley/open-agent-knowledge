~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

StateValue: One value read from local state.
Read and write state only in the active OAK document.
~~~~

~~~~constants
example-1: "$state.status"

grammar: TEXT<<
surface_value_state = ? $<STATE> ? ;
>>
~~~~

~~~~schemas
~~~schema;id="value-state";name="StateValue";purpose="One value read from local state."
$<STATE>

WHERE:
- <STATE> is string; is non-empty; The local state target to read..
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
