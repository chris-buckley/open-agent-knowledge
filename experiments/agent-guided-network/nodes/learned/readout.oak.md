<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
AS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
weights AS contracts.oak.md#schema.parameters.W: [[10.18380287884895, -21.806520636539624, -5.588550566565185]]

responsibility: "Score support while suppressing explicitly vetoed entity pairs."

trainable: true
</constants>

<processes>
<process id="forward" name="Compute tensor" input="contracts.oak.md#schema.evidence" output="contracts.oak.md#schema.probabilities">
ACT TOOL "tensor.readout.v1" input="contracts.oak.md#schema.readout-action" output="contracts.oak.md#schema.probabilities": Apply the fixed numerical operator to <COUNT>, <X>, <W> to produce <PROB>. (
  COUNT=$COUNT,
  X=$X,
  W=$constant.weights,
) -> PROB
</process>
</processes>