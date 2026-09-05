<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
AS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
weights AS contracts.oak.md#schema.parameters.W: [[9.190220539460313, -1.6430995847249719e-06, -7.160375319115175e-06, -4.595109457723041]]

responsibility: "Select the first relation channel for two-hop composition."

trainable: true
</constants>

<processes>
<process id="forward" name="Compute tensor" input="contracts.oak.md#schema.relations" output="contracts.oak.md#schema.left-values">
ACT TOOL "tensor.left.v1" input="contracts.oak.md#schema.left-action" output="contracts.oak.md#schema.left-values": Apply the fixed numerical operator to <X>, <W> to produce <LEFT>. (
  X=$X,
  W=$constant.weights,
) -> LEFT
</process>
</processes>