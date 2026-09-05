<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

If: One recursive condition with a then branch and optional else branch.
Remove a process branch that cannot run.
</instructions>

<constants>
example-1: "IF $state.status equals \"ready\":\n  SET state.status = \"complete\"\nELSE:\n  FAIL \"The state is not ready.\""

syntax-reference: "outputs/oak.ebnf"

grammar: TEXT<<
surface_step_if = if_statement ;
>>
</constants>

<schemas>
<schema id="step-if" name="If" purpose="One recursive condition with a then branch and optional else branch.">
IF <CONDITION>:
  <THEN>
ELSE:
  <OTHERWISE>

WHERE:
- <CONDITION> is string; is non-empty; The recursive condition that selects the branch..
- <THEN> is string; is non-empty; The steps run when the condition is true..
- <OTHERWISE> is string; The steps run when the condition is false..
</schema>
</schemas>
