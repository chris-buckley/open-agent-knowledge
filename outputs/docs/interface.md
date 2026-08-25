~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Interface: One crossing of information at the active document boundary.
~~~~

~~~~constants
example-1: "<interface id=\"request\" direction=\"in\" schema=\"schema.request-shape\">\nThe request supplied to the document.\n</interface>"

grammar: TEXT<<
surface_interface = ? <interface id="<ID>" direction="<DIRECTION>" schema="<SCHEMA_ID>">
<DESCRIPTION>
</interface> ? ;
>>
~~~~

~~~~schemas
~~~schema;id="interface";name="Interface";purpose="One crossing of information at the active document boundary."
<interface id="<ID>" direction="<DIRECTION>" schema="<SCHEMA_ID>">
<DESCRIPTION>
</interface>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <DIRECTION> is string; is non-empty; The direction across the document boundary..
- <SCHEMA_ID> is string; is non-empty; The local or relative schema target that defines the shape..
- <DESCRIPTION> is string; is non-empty; What the document boundary crossing means..
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
