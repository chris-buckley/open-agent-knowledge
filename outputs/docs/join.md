<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Join: The barrier immediately after one parallel group.
Put JOIN immediately after one PAR.
Put no step between PAR and JOIN.
</instructions>

<constants>
example-1: "JOIN"

grammar: TEXT<<
surface_step_join = ? JOIN ? ;
>>
</constants>

<schemas>
<schema id="step-join" name="Join" purpose="The barrier immediately after one parallel group.">
JOIN

WHERE:
</schema>
</schemas>
