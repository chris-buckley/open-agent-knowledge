~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

InterfaceValue: One placeholder value read from one active local input interface.
Read and emit interfaces only in the active OAK document.
Read only in or inout interfaces and emit only out or inout interfaces.
Read a placeholder present in the interface schema.
~~~~

~~~~constants
example-1: "$interface.request.REQUEST"

grammar: TEXT<<
surface_value_interface = ? $<INTERFACE>.<PLACEHOLDER> ? ;
>>
~~~~

~~~~schemas
~~~schema;id="value-interface";name="InterfaceValue";purpose="One placeholder value read from one active local input interface."
$<INTERFACE>.<PLACEHOLDER>

WHERE:
- <INTERFACE> is string; is non-empty; The active local input interface target to read..
- <PLACEHOLDER> is string; is non-empty; The interface schema placeholder to read..
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
