~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
Process: One named ordered way to do a task.
Do not redefine a visible immutable process binding.
Read only a visible prior process-local binding.
Remove a process step after a path that always fails.
~~~~

~~~~constants
example-1: "<process id=\"write-oak\" name=\"Write OAK\">\nACT Write the knowledge.\n</process>"

grammar: TEXT<<
surface_process = ? <process id="<ID>" name="<NAME>">
<STEPS>
</process> ? ;
>>
~~~~

~~~~schemas
~~~schema;id="process";name="Process";purpose="One named ordered way to do a task."
<process id="<ID>" name="<NAME>">
<STEPS>
</process>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <NAME> is string; is non-empty; The two-word process display name..
- <STEPS> is string; is non-empty; The typed process steps in authored order..
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
