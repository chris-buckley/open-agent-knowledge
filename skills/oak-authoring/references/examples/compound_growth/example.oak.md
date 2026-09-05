<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Conditions are typed trees; ALL, ANY, and NOT compose comparisons; ASSERT fails a false condition; FOREACH is sequential; WHILE tests before each bounded iteration; PAR outputs become visible only at JOIN.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
Event-backed trigger seeds fill the selected process input schema; each seeded value validates before the process runs.
EMITS publishes one complete instance of its schema.
Text after `: ` states boundary meaning absent from the interface schema.
AS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
State holds values that persist and can change while processes run.
Each trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.

Run this machine continuously: after each cycle commits, apply the same arrival again.
</instructions>

<constants>
growth-rate AS schema.scaling.FACTOR: 1.05

reflection-step AS schema.scaling.FACTOR: 8
</constants>

<schemas>
<schema id="scaling" name="Scaling" purpose="Carry one balance and the factor to scale it by.">
Balance: <BALANCE>
Factor: <FACTOR>

WHERE:
- <BALANCE> is number; is at least 0; the non-negative balance to scale.
- <FACTOR> is number; is at least 1; the multiplication factor.
</schema>

<schema id="scaled-balance" name="Scaled Balance" purpose="Carry the balance after one multiplication.">
<SCALED_BALANCE>

WHERE:
- <SCALED_BALANCE> is number; the balance after one multiplication.
</schema>

<schema id="growth-target" name="Growth Target" purpose="Carry the balance one growth cycle must reach.">
Target: <TARGET>

WHERE:
- <TARGET> is number; is at least 0; the balance the cycle must reach.
</schema>

<schema id="reflection" name="Reflection" purpose="Carry one growth reflection for the chat.">
Balance: <BALANCE>
Reflection: <REFLECTION>

WHERE:
- <BALANCE> is number; the balance at the end of the cycle.
- <REFLECTION> is string; is non-empty; the reflection on this growth cycle.
</schema>
</schemas>

<state>
current-balance AS schema.scaling.BALANCE: 100
reflection-target AS schema.scaling.BALANCE: 800
</state>

<triggers>
growth-requested(
  event="Continue growing the balance.",
  process=process.grow-balance,
  seed=(TARGET=$state.reflection-target),
)
</triggers>

<processes>
<process id="scale-balance" name="Scale balance" input="schema.scaling" output="schema.scaled-balance">
ACT TOOL "math.multiply" input="schema.scaling" output="schema.scaled-balance": Multiply <BALANCE> by <FACTOR> and round to 2 decimals to produce <SCALED_BALANCE>. (
  BALANCE=$BALANCE,
  FACTOR=$FACTOR,
) -> SCALED_BALANCE
</process>

<process id="grow-balance" name="Grow balance" input="schema.growth-target">
WHILE $state.current-balance is less than $TARGET LIMIT 60:
  CALL process.scale-balance (
    BALANCE=$state.current-balance,
    FACTOR=$constant.growth-rate,
  ) -> SCALED_BALANCE
  SET state.current-balance = $SCALED_BALANCE
ACT Reflect on <BALANCE> reaching <TARGET> and produce <REFLECTION>. (
  BALANCE=$state.current-balance,
  TARGET=$TARGET,
) -> REFLECTION
CALL process.scale-balance (
  BALANCE=$state.reflection-target,
  FACTOR=$constant.reflection-step,
) -> SCALED_BALANCE
SET state.reflection-target = $SCALED_BALANCE
EMIT interface.reflection-output (BALANCE=$state.current-balance, REFLECTION=$REFLECTION)
</process>
</processes>

<interfaces>
reflection-output EMITS schema.reflection: "The reflection written to the chat before the next cycle starts."
</interfaces>
