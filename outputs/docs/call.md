<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Call: One synchronous process invocation with schema-bound inputs and outputs.
Match each call's inputs and outputs to the called process schemas.
Keep the resolved process call graph acyclic.
Keep the local process call graph acyclic.
</instructions>

<constants>
example-1: "CALL process.normalise (RAW_NAME=\" ada \") -> NORMAL_NAME"

grammar: TEXT<<
surface_step_call = ? CALL <PROCESS> (<INPUTS>) -> <OUTPUTS> ? ;
>>
</constants>

<schemas>
<schema id="step-call" name="Call" purpose="One synchronous process invocation with schema-bound inputs and outputs.">
CALL <PROCESS> (<INPUTS>) -> <OUTPUTS>

WHERE:
- <PROCESS> is string; is non-empty; The local or relative process target to invoke..
- <INPUTS> is string; The called process input bindings in authored order..
- <OUTPUTS> is string; The called process outputs promoted to this process..
</schema>
</schemas>
