~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Trigger: One GIVEN, WHEN, and THEN signpost to a process.
Do not read an interface or local binding in a trigger guard.
Make equal trigger WHEN values provably disjoint.
Give every non-true trigger guard at least one state read.
~~~~

~~~~constants
example-1: "<trigger id=\"write-oak-trigger\">\nGIVEN: true\nWHEN: \"Source material arrives to write OAK.\"\nTHEN: process.write-oak\n</trigger>"

grammar: TEXT<<
surface_trigger = ? <trigger id="<ID>">
GIVEN: <GIVEN>
WHEN: <WHEN>
THEN: <THEN>
</trigger> ? ;
>>
~~~~

~~~~schemas
~~~schema;id="trigger";name="Trigger";purpose="One GIVEN, WHEN, and THEN signpost to a process."
<trigger id="<ID>">
GIVEN: <GIVEN>
WHEN: <WHEN>
THEN: <THEN>
</trigger>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <GIVEN> is string; is non-empty; True or the recursive state guard checked after WHEN..
- <WHEN> is string; is non-empty; Why the interpreter enters the knowledge..
- <THEN> is string; is non-empty; The local or relative process target selected by the trigger..
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
