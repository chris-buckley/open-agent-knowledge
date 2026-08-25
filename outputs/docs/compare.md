~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Compare: One strict structural or ordered comparison.
Order only two numbers or two strings without coercion.
~~~~

~~~~constants
example-1: "$state.status equals \"ready\""

grammar: TEXT<<
surface_condition_compare = ? <LEFT> <OPERATOR> <RIGHT> ? ;
>>
~~~~

~~~~schemas
~~~schema;id="condition-compare";name="Compare";purpose="One strict structural or ordered comparison."
<LEFT> <OPERATOR> <RIGHT>

WHERE:
- <LEFT> is string; is non-empty; The value on the left of the comparison..
- <OPERATOR> is string; is non-empty; The strict comparison operator..
- <RIGHT> is string; is non-empty; The value on the right of the comparison..
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
