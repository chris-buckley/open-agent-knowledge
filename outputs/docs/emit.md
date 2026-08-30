~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Emit: One schema instance emitted through one local output interface.
Bind each emitted placeholder once.
Bind every interface schema placeholder exactly once when emitting.
Read and emit interfaces only in the active OAK document.
Read only in or inout interfaces and emit only out or inout interfaces.
Make every statically known emission satisfy its interface schema.
~~~~

~~~~constants
example-1: "EMIT interface.result:\n  RESULT = $RESULT"

grammar: TEXT<<
surface_step_emit = ? EMIT <INTERFACE>:
  <BINDINGS> ? ;
>>
~~~~

~~~~schemas
~~~schema;id="step-emit";name="Emit";purpose="One schema instance emitted through one local output interface."
EMIT <INTERFACE>:
  <BINDINGS>

WHERE:
- <INTERFACE> is string; is non-empty; The local output interface target..
- <BINDINGS> is string; is non-empty; One value binding for each interface schema placeholder..
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
