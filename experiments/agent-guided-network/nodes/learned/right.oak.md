<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
AS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
weights AS contracts.oak.md#schema.parameters.W: [[-2.1749343092625217e-06, 9.190219400962963, -7.059557186273047e-06, -4.595108349163652]]

responsibility: "Select the second relation channel for two-hop composition."

trainable: true
</constants>

<processes>
<process id="forward" name="Compute tensor" input="contracts.oak.md#schema.relations" output="contracts.oak.md#schema.right-values">
ACT TOOL "tensor.right.v1" input="contracts.oak.md#schema.right-action" output="contracts.oak.md#schema.right-values": Apply the fixed numerical operator to <X>, <W> to produce <RIGHT>. (
  X=$X,
  W=$constant.weights,
) -> RIGHT
</process>
</processes>