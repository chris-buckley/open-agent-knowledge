<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

While: One bounded pre-test loop over a recursive condition.
Remove a process branch that cannot run.
</instructions>

<constants>
example-1: "WHILE $state.status does not equal \"complete\" LIMIT 10:\n  SET state.status = \"complete\""

grammar: TEXT<<
surface_step_while = ? WHILE <CONDITION> LIMIT <LIMIT>:
  <STEPS> ? ;
>>
</constants>

<schemas>
<schema id="step-while" name="While" purpose="One bounded pre-test loop over a recursive condition.">
WHILE <CONDITION> LIMIT <LIMIT>:
  <STEPS>

WHERE:
- <CONDITION> is string; is non-empty; The recursive condition tested before every iteration..
- <LIMIT> is string; is non-empty; The hard maximum number of iterations..
- <STEPS> is string; is non-empty; The steps run in one fresh child binding scope per iteration..
</schema>
</schemas>
