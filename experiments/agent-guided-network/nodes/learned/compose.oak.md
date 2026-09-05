<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
AS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
weights AS contracts.oak.md#schema.parameters.W: [[1.0]]

responsibility: "Multiply the selected relation matrices to count two-hop support."

trainable: false
</constants>

<processes>
<process id="forward" name="Compute tensor" input="contracts.oak.md#schema.pair" output="contracts.oak.md#schema.counts">
ACT TOOL "tensor.compose.v1" input="contracts.oak.md#schema.compose-action" output="contracts.oak.md#schema.counts": Apply the fixed numerical operator to <LEFT>, <RIGHT>, <W> to produce <COUNT>. (
  LEFT=$LEFT,
  RIGHT=$RIGHT,
  W=$constant.weights,
) -> COUNT
</process>
</processes>