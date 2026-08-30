~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Any: At least one child condition must be true in authored order.
Give each ALL or ANY condition at least two children.
~~~~

~~~~constants
example-1: "ANY:\n  $state.status equals \"ready\"\n  $state.override equals true"

grammar: TEXT<<
surface_condition_any = ? ANY:
  <CONDITIONS> ? ;
>>
~~~~

~~~~schemas
~~~schema;id="condition-any";name="Any";purpose="At least one child condition must be true in authored order."
ANY:
  <CONDITIONS>

WHERE:
- <CONDITIONS> is string; is non-empty; The child conditions in authored order..
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
