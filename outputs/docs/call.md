~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Call: One synchronous local or relative process invocation.
Keep the resolved process call graph acyclic.
Keep the local process call graph acyclic.
~~~~

~~~~constants
example-1: "CALL process.finalize"

grammar: TEXT<<
surface_step_call = ? CALL <PROCESS> ? ;
>>
~~~~

~~~~schemas
~~~schema;id="step-call";name="Call";purpose="One synchronous local or relative process invocation."
CALL <PROCESS>

WHERE:
- <PROCESS> is string; is non-empty; The local or relative process target to invoke..
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
