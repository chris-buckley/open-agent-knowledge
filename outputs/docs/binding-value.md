~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
BindingValue: One value read from a visible process-local binding.
~~~~

~~~~constants
example-1: "$RESULT"

grammar: TEXT<<
surface_value_binding = ? $<BINDING> ? ;
>>
~~~~

~~~~schemas
~~~schema;id="value-binding";name="BindingValue";purpose="One value read from a visible process-local binding."
$<BINDING>

WHERE:
- <BINDING> is string; is non-empty; The visible process-local binding to read..
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
