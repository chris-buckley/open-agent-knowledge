# Experiment evidence status

Recorded: 2026-09-05.

| Item | Status | Evidence |
| --- | --- | --- |
| Intent and design | Recorded | [EXPERIMENT.md](../EXPERIMENT.md) and its supporting contracts. |
| Research attribution | Recorded | [Primary-source register](../research/SOURCES.md). |
| Numerical runtime | Not implemented | No runtime measurement exists. |
| Training integration | Not implemented | No agent-guided update has been run. |
| Dataset and baselines | Not implemented | No scored comparison exists. |
| Agent-free export | Not implemented | No exported artifact or equivalence result exists. |
| Engineering verdict | Not reached | Requires measured training and export evidence. |
| Scientific verdict | Not reached | Requires the predeclared controlled comparisons. |

Documentation checks and repository CI, when reported, verify the design package and repository consistency. They are not evidence that this learning experiment works. Delivery evidence belongs in [the report](../../../docs/plans/0008-agent-guided-network/report.md).

When actual runs exist, create one directory per immutable run under this directory. Include the study configuration and source revisions, data split identities, model/provider identity, seeds, allowed agent context, proposals and decisions, resource accounting, measured results, export checks, and the verdict. Use existing OAK shapes for authored run knowledge and machine-readable measurement outputs where appropriate.

Keep generated large artifacts out of ordinary source commits unless deliberately approved. Use explicit artifact references and content identities when evidence is stored elsewhere. Do not add fictitious run directories, illustrative success metrics, or dummy trained weights.
