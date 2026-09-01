<instructions>
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
</instructions>

<schemas>
<schema id="error" name="Error" purpose="Carry one single-line reason when a requested shape cannot be produced.">
Error: <REASON>

WHERE:
- <REASON> is string; is one line; is at most 160 characters; why the requested shape cannot be produced.
</schema>
</schemas>