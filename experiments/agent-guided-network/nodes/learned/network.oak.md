<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
Constants hold values that do not change while the knowledge runs.
Each trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
profile: "oak-two-hop-v1"

input-shape: ["batch", 4, 4, 3]

dtype: "float64"

threshold: 0.5
</constants>

<triggers>
request(event="Numerical relation tensors arrive.", source=interface.input, process=process.infer)
</triggers>

<processes>
<process id="infer" name="Infer relations" input="contracts.oak.md#schema.relations" output="contracts.oak.md#schema.probabilities">
CALL left.oak.md#process.forward (X=$X) -> LEFT
CALL right.oak.md#process.forward (X=$X) -> RIGHT
CALL compose.oak.md#process.forward (LEFT=$LEFT, RIGHT=$RIGHT) -> COUNT
CALL readout.oak.md#process.forward (COUNT=$COUNT, X=$X) -> PROB
EMIT interface.output
</process>
</processes>

<interfaces>
input RECEIVES contracts.oak.md#schema.relations
output EMITS contracts.oak.md#schema.probabilities
</interfaces>