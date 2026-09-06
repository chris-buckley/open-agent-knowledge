<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
AS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
score-kernel AS contracts.oak.md#schema.kernel.KERNEL: [{"encoding": "dense", "dimension": 8, "coefficients": [9.797243062749466, -2.9913607185128033, -0.36257699595580967, 5.319401855787276, 4.994725569738312, 1.107842823454575, 0.08238294497191745, -7.165410393439303, 0.18310165787970167, 23.052245375552708, -4.474374917829444, -1.4417154426006018, 3.604069254687692, 0.5974735424632268, -5.762293880225936, 5.641880946961369, -1.7873836369254108, -4.45474573237482, 15.816721782144043, -6.759997184839018, -1.9593298265691383, -4.309406926550498, -9.037735860161494, -2.101086413977018, -2.0618847226366754, -0.9716265247266416, -2.9302517874759633, 10.414114229182104, 1.6246155650681693, -1.35097173829681, -0.3391884840094688, 4.151836632529389, 5.535140907189541, 8.048291942520903, -2.50105205488504, 2.447875977635874, 7.896188209647404, -4.129407752054803, -0.5597205578455549, -3.4712210964082275, 4.175597563171134, 0.10621485276520375, -3.4126673565094405, 1.5954196547896202, -5.6929724420284336, 13.141128489037625, -2.8653353119843277, 4.631214387902986, -2.5488074123940407, 0.7837647287598208, -8.410916938497783, -6.273115876399747, -0.575015580873214, -1.6022263274801056, 13.183136415967752, -6.396792889445576, -4.047904321455339, 2.936207524527903, -2.7766162519999456, 2.663782919323258, -3.8338861357104843, 5.64749273290272, -5.975821246822202, 14.458638972225664], "indices": []}]

output-kernel AS contracts.oak.md#schema.kernel.KERNEL: [{"encoding": "dense", "dimension": 4, "coefficients": [3.531331160399302, -0.7443770052247322, -0.7116369558707748, -1.4638538162998005, -1.1538458622394434, 2.933411635540717, -1.0162316255181798, -0.7176256276084803, -1.1367220996153309, -1.2852407413358344, 3.999603827560866, -0.9940014192262165, -0.7835632958097244, -1.2445593817323215, -0.9276003996971982, 3.3706676896381067], "indices": []}]

responsibility: "Match the raw bridge and transform class evidence."
</constants>

<processes>
<process id="attend" name="Attend values" input="contracts.oak.md#schema.second-input" output="contracts.oak.md#schema.second-output">
ACT TOOL "tensor.compact.second.v1" input="contracts.oak.md#schema.second-action" output="contracts.oak.md#schema.second-output": Use <BRIDGE>, <KEY2>, <VALUE2>, <MASK2>, <SCORE>, <OUTPUT> to produce <LOGITS>, <ALIGN2>. (
  BRIDGE=$BRIDGE,
  KEY2=$KEY2,
  VALUE2=$VALUE2,
  MASK2=$MASK2,
  SCORE=$constant.score-kernel,
  OUTPUT=$constant.output-kernel,
) -> LOGITS, ALIGN2
</process>
</processes>