<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
owned-concern: "Experiment containment, design records, evidence status, and promotion boundaries."

experiment-layout: "Each experiment has one kebab-case directory with EXPERIMENT.md as its intent and design record; supporting directories contain substantive contracts or evidence rather than empty scaffolding."

experiment-evidence: ["distinguish a proposed mechanism from an implemented mechanism and a measured result", "record the tested source revision and resource budget with each experimental verdict", "keep an untested hypothesis out of established OAK product claims"]

experiment-boundary: "Experiments may use existing OAK contracts but do not redefine the standard or become distributable skills without a separately accepted product change."

experiment-records: "Keep experimental intent in the experiment directory and implementation task state in the plan location owned by docs/AGENTS.md."
</constants>

<processes>
<process id="maintain-experiment" name="Maintain experiment">
ACT Apply <LAYOUT> when creating or extending an experiment directory. (
  LAYOUT=$constant.experiment-layout,
)
ACT Apply <EVIDENCE> to experiment status, observations, and conclusions. (
  EVIDENCE=$constant.experiment-evidence,
)
ACT Apply <BOUNDARY> before promoting an experiment into a supported product. (
  BOUNDARY=$constant.experiment-boundary,
)
ACT Apply <RECORDS> to separate scientific design from implementation history. (
  RECORDS=$constant.experiment-records,
)
</process>
</processes>