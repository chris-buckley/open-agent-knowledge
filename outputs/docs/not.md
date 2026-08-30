~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Not: One child condition whose result is inverted.
~~~~

~~~~constants
example-1: "NOT:\n  $state.status equals \"closed\""

grammar: TEXT<<
surface_condition_not = ? NOT:
  <CONDITION> ? ;
>>
~~~~

~~~~schemas
~~~schema;id="condition-not";name="Not";purpose="One child condition whose result is inverted."
NOT:
  <CONDITION>

WHERE:
- <CONDITION> is string; is non-empty; The child condition to invert..
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
