<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Node: One complete idless set of the seven OAK parts.
Use each entry id once in one OAK document.
Target an entry that exists in the current OAK document.
Target the part required by the typed reference field.
</instructions>

<constants>
example-1: "<instructions>\nUse the supplied schema.\n</instructions>"

grammar: TEXT<<
surface_node = ? <instructions>
<INSTRUCTIONS>
</instructions>

<constants>
<CONSTANTS>
</constants>

<schemas>
<SCHEMAS>
</schemas>

<state>
<STATE>
</state>

<triggers>
<TRIGGERS>
</triggers>

<processes>
<PROCESSES>
</processes>

<interfaces>
<INTERFACES>
</interfaces> ? ;
>>
</constants>

<schemas>
<schema id="node" name="Node" purpose="One complete idless set of the seven OAK parts.">
<instructions>
<INSTRUCTIONS>
</instructions>

<constants>
<CONSTANTS>
</constants>

<schemas>
<SCHEMAS>
</schemas>

<state>
<STATE>
</state>

<triggers>
<TRIGGERS>
</triggers>

<processes>
<PROCESSES>
</processes>

<interfaces>
<INTERFACES>
</interfaces>

WHERE:
- <INSTRUCTIONS> is string; The node instructions in authored order..
- <CONSTANTS> is string; The node constants in authored order..
- <SCHEMAS> is string; The node schemas in authored order..
- <STATE> is string; The node state values in authored order..
- <TRIGGERS> is string; The node triggers in authored order..
- <PROCESSES> is string; The node processes in authored order..
- <INTERFACES> is string; The node interfaces in authored order..
</schema>
</schemas>
