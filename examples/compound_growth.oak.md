<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and THEN omit $.
Conditions are typed trees; ALL, ANY, and NOT compose comparisons; ASSERT fails a false condition; FOREACH is sequential; WHILE tests before each bounded iteration; PAR outputs become visible only at JOIN.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
State holds values that persist and can change while processes run.
Each trigger contains GIVEN, WHEN, and THEN; WHEN matches first, GIVEN guards it, and THEN selects a process.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
Each interface is one document-boundary crossing: in arrives, out is emitted, and inout does both.

Run this machine continuously: after each cycle commits, apply the same arrival again.
</instructions>

<constants>
growth-rate: 1.05

reflection-step: 8
</constants>

<schemas>
<schema id="scaling" name="Scaling" purpose="Carry one balance and the factor to scale it by.">
Balance: <BALANCE>
Factor: <FACTOR>

WHERE:
- <BALANCE> is number; the balance to scale.
- <FACTOR> is number; the multiplication factor.
</schema>

<schema id="scaled-balance" name="Scaled Balance" purpose="Carry the balance after one multiplication.">
<SCALED_BALANCE>

WHERE:
- <SCALED_BALANCE> is number; the balance after one multiplication.
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
current-balance: 100
reflection-target: 800
</state>

<triggers>
<trigger id="growth-requested">
GIVEN: true
WHEN: "Continue growing the balance."
THEN: process.grow-balance
</trigger>
</triggers>

<processes>
<process id="scale-balance" name="Scale balance" input="schema.scaling" output="schema.scaled-balance">
ACT TOOL "math.multiply": Multiply <BALANCE> by <FACTOR> and round to 2 decimals to produce <SCALED_BALANCE>.
  INPUTS:
    BALANCE = $BALANCE
    FACTOR = $FACTOR
  OUTPUTS: SCALED_BALANCE
</process>

<process id="grow-balance" name="Grow balance">
WHILE $state.current-balance is less than $state.reflection-target LIMIT 60:
  CALL process.scale-balance:
    INPUTS:
      BALANCE = $state.current-balance
      FACTOR = $constant.growth-rate
    OUTPUTS: SCALED_BALANCE
  SET state.current-balance = $SCALED_BALANCE
ACT Reflect on <BALANCE> reaching <TARGET> and produce <REFLECTION>.
  INPUTS:
    BALANCE = $state.current-balance
    TARGET = $state.reflection-target
  OUTPUTS: REFLECTION
CALL process.scale-balance:
  INPUTS:
    BALANCE = $state.current-balance
    FACTOR = $constant.reflection-step
  OUTPUTS: SCALED_BALANCE
SET state.reflection-target = $SCALED_BALANCE
EMIT interface.reflection-output:
  BALANCE = $state.current-balance
  REFLECTION = $REFLECTION
</process>
</processes>

<interfaces>
<interface id="reflection-output" direction="out" schema="schema.reflection">
The reflection written to the chat before the next cycle starts.
</interface>
</interfaces>