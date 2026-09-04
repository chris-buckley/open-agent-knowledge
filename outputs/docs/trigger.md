<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Trigger: One outside event routed to one process.
Use interfaces only in the active OAK document.
Do not read a local binding in a trigger guard.
Do not read a local binding in a trigger seed.
Make equal trigger events and equal trigger sources provably disjoint.
Select a process with an input schema from a source-backed trigger.
Use the same resolved schema for a receive source and selected process input.
Give a source-backed trigger no seeds.
Bind each event-selected process input placeholder exactly once in trigger seeds.
Give every non-true trigger guard at least one state read.
Select only a local RECEIVES interface as a trigger source.
</instructions>

<constants>
example-1: "trigger.write-oak-trigger.event := \"Source material arrives to write OAK.\"\ntrigger.write-oak-trigger.process := process.write-oak"

grammar: TEXT<<
surface_trigger = ? trigger.<ID>.event := <EVENT>
trigger.<ID>.source := <SOURCE>
trigger.<ID>.guard := <GUARD>
trigger.<ID>.process := <PROCESS>
trigger.<ID>.seed.<SEED> ? ;
>>
</constants>

<schemas>
<schema id="trigger" name="Trigger" purpose="One outside event routed to one process.">
trigger.<ID>.event := <EVENT>
trigger.<ID>.source := <SOURCE>
trigger.<ID>.guard := <GUARD>
trigger.<ID>.process := <PROCESS>
trigger.<ID>.seed.<SEED>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <EVENT> is string; is non-empty; The semantic signpost matched exactly when the trigger has no source..
- <SOURCE> is string; The optional local RECEIVES interface whose arrival fires the trigger..
- <GUARD> is string; True or the recursive state guard checked after the match..
- <PROCESS> is string; is non-empty; The local or relative process target selected by the trigger..
- <SEED> is string; The event-backed seed bindings that fill the selected process input schema..
</schema>
</schemas>
