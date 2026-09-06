<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
AS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.
State holds values that persist and can change while processes run.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<state>
history AS contracts.oak.md#schema.stored.STORED: [[]]
</state>

<processes>
<process id="recall" name="Recall dialogue" output="contracts.oak.md#schema.histories">
ACT TOOL "dialogue.recall" input="contracts.oak.md#schema.stored" output="contracts.oak.md#schema.histories": Apply the registered numerical operation to <STORED>, <HISTORIES>. (
  STORED=$state.history,
) -> HISTORIES
</process>

<process id="commit" name="Commit dialogue" input="contracts.oak.md#schema.histories-texts-replies">
ACT TOOL "dialogue.commit" input="contracts.oak.md#schema.histories-texts-replies" output="contracts.oak.md#schema.stored": Apply the registered numerical operation to <HISTORIES>, <TEXTS>, <REPLIES>, <STORED>. (
  HISTORIES=$HISTORIES,
  TEXTS=$TEXTS,
  REPLIES=$REPLIES,
) -> STORED
SET state.history = $STORED
</process>
</processes>