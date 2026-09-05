<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
AS binds one constant or state value to one schema placeholder; the value must satisfy that placeholder at resolution and before each state write commits.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
score-kernel AS contracts.oak.md#schema.kernel.KERNEL: [{"encoding": "dense", "dimension": 8, "coefficients": [3.5645733745041346, 0.6739681049127493, 0.4137295305051522, -1.615947351897792, -0.22809019721428206, -0.15602433429265958, 2.910861200147894, -0.4087715900611561, 0.7261043959956314, 5.245576991493091, -0.2850574041227657, 0.8245414170883213, 0.8332844646312797, 0.6735952885636558, -0.23016136232295858, -0.3213708935262606, 0.5975137593678728, -0.13856990724794951, 4.435047326824773, 0.48452374812747256, 2.661829718848499, -1.5181438615973126, 0.8202352973649221, 0.36359265664883433, -2.1056108145938173, 0.001310302432930482, 0.580909895920278, 3.4624827724963296, 1.665639772064433, -0.530534974796984, -1.5403316458246274, 0.7295315428264296, -0.6592481702280798, 0.7810424554793276, 1.338800781353458, 1.4034096462973746, 4.206263524562976, -0.8610400075441932, 0.6386654396086311, -0.7534838838423142, -0.02159768267734081, 0.4275088146016054, -0.19333916620747457, -1.095195384460397, -0.09072819557375356, 4.786880191588583, -0.2763781697459233, -1.885653157467293, 2.293697009745996, 0.4945591551962035, -0.5162765524256714, -1.8351036533209342, 1.48750495559378, -0.2684999917730287, 4.216370426860692, 0.9760530776185818, -0.33588232359832165, 1.0124733718753463, 0.20665395715259036, 0.49340001913560244, -0.8027746757856192, -2.2342340421408835, 1.1241399333327993, 5.089516301130015], "indices": []}]

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