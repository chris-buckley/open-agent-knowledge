<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
AS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
score-kernel AS contracts.oak.md#schema.kernel.KERNEL: [{"encoding": "scaled-identity", "dimension": 8, "coefficients": [2048.0], "indices": []}]

responsibility: "Compute raw weighted bridge values."
</constants>

<processes>
<process id="attend" name="Attend values" input="contracts.oak.md#schema.first-input" output="contracts.oak.md#schema.first-output">
ACT TOOL "tensor.compact.first.v1" input="contracts.oak.md#schema.first-action" output="contracts.oak.md#schema.first-output": Use <QUERY>, <KEY1>, <VALUE1>, <MASK1>, <SCORE> to produce <BRIDGE>, <ALIGN1>. (
  QUERY=$QUERY,
  KEY1=$KEY1,
  VALUE1=$VALUE1,
  MASK1=$MASK1,
  SCORE=$constant.score-kernel,
) -> BRIDGE, ALIGN1
</process>
</processes>