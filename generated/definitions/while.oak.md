<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

While: One bounded pre-test loop over a recursive condition.
Remove a process branch that cannot run.
</instructions>

<constants>
example-1: "WHILE $state.status does not equal \"complete\" LIMIT 10:\n  SET state.status = \"complete\""

syntax-reference: "generated/oak.ebnf"

grammar: TEXT<<
surface_statement_while = while_statement ;
>>
</constants>

<schemas>
<schema id="statement-while" name="While" purpose="One bounded pre-test loop over a recursive condition.">
WHILE <CONDITION> LIMIT <LIMIT>:
  <BODY>

WHERE:
- <CONDITION> is string; is non-empty; The recursive condition tested before every iteration..
- <LIMIT> is string; is non-empty; The hard maximum number of iterations..
- <BODY> is string; is non-empty; The statements run in one fresh child binding scope per iteration..
</schema>
</schemas>
