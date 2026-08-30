~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Type: The bound value has one datatype from the vocabulary catalog.
~~~~

~~~~constants
example-1: "is string"

grammar: TEXT<<
surface_constraint_type = ? is <OF> ? ;
>>
~~~~

~~~~schemas
~~~schema;id="constraint-type";name="Type";purpose="The bound value has one datatype from the vocabulary catalog."
is <OF>

WHERE:
- <OF> is string; is non-empty; The datatype name..
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
