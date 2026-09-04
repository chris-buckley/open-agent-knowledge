<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Instruction: One rule the interpreter must follow.
</instructions>

<constants>
example-1: "Read the architecture overview before work."

grammar: TEXT<<
surface_instruction = ? <BODY> ? ;
>>
</constants>

<schemas>
<schema id="instruction" name="Instruction" purpose="One rule the interpreter must follow.">
<BODY>

WHERE:
- <BODY> is string; is non-empty; One directive or declarative rule..
</schema>
</schemas>
