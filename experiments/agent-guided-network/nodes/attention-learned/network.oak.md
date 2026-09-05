<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
Constants hold values that do not change while the knowledge runs.
Each trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
profile: "oak-attention-two-hop-v1"

dtype: "float64"

decoder: "argmax-first"

length-limit: 64
</constants>

<triggers>
request(
  event="A two-hop numerical retrieval request arrives.",
  source=interface.input,
  process=process.infer,
)
</triggers>

<processes>
<process id="infer" name="Retrieve classes" input="contracts.oak.md#schema.input" output="contracts.oak.md#schema.prediction">
CALL attention.oak.md#process.attend (
  QUERY=$QUERY,
  KEY1=$KEY1,
  VALUE1=$VALUE1,
  MASK1=$MASK1,
) -> BRIDGE, ALIGN1
CALL attention-readout.oak.md#process.attend (
  BRIDGE=$BRIDGE,
  KEY2=$KEY2,
  VALUE2=$VALUE2,
  MASK2=$MASK2,
) -> LOGITS, ALIGN2
ACT TOOL "tensor.softmax.v1" input="contracts.oak.md#schema.decode" output="contracts.oak.md#schema.prediction": Normalise class <LOGITS> to <PROB>. (
  LOGITS=$LOGITS,
) -> PROB
EMIT interface.output
</process>
</processes>

<interfaces>
input RECEIVES contracts.oak.md#schema.input
output EMITS contracts.oak.md#schema.prediction
</interfaces>