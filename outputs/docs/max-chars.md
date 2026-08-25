~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
MaxChars: The bound value has at most n characters.
~~~~

~~~~constants
example-1: "is at most 160 characters"

grammar: TEXT<<
surface_constraint_max_chars = ? is at most <N> characters ? ;
>>
~~~~

~~~~schemas
~~~schema;id="constraint-max-chars";name="MaxChars";purpose="The bound value has at most n characters."
is at most <N> characters

WHERE:
- <N> is string; is non-empty; The character limit..
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
