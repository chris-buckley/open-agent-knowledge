<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
AS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.
State holds values that persist and can change while processes run.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<state>
hidden AS contracts.oak.md#schema.hidden.HIDDEN: [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
previous AS contracts.oak.md#schema.token.TOKEN: [1]
tape AS contracts.oak.md#schema.tape.TAPE: [[]]
</state>

<processes>
<process id="start" name="Start dialogue" input="contracts.oak.md#schema.state-previous-tape">
SET state.hidden = $STATE
SET state.previous = $PREVIOUS
SET state.tape = $TAPE
</process>

<process id="next-word" name="Next word" input="contracts.oak.md#schema.memory-mask-embedding">
CALL attention.oak.md#process.attend (MEMORY=$MEMORY, MASK=$MASK, STATE=$state.hidden) -> CONTEXT
CALL decoder.oak.md#process.decode (
  CONTEXT=$CONTEXT,
  EMBEDDING=$EMBEDDING,
  STATE=$state.hidden,
  PREVIOUS=$state.previous,
) -> NEWSTATE
CALL readout.oak.md#process.readout (
  STATE=$NEWSTATE,
  CONTEXT=$CONTEXT,
  TAPE=$state.tape,
) -> NEWPREVIOUS, NEWTAPE
SET state.hidden = $NEWSTATE
SET state.previous = $NEWPREVIOUS
SET state.tape = $NEWTAPE
</process>

<process id="finish" name="Finish dialogue" output="contracts.oak.md#schema.replies">
ACT TOOL "dialogue.finish" input="contracts.oak.md#schema.tape" output="contracts.oak.md#schema.replies": Apply the registered numerical operation to <TAPE>, <REPLIES>. (
  TAPE=$state.tape,
) -> REPLIES
</process>
</processes>