# Experiment evidence status

Recorded: 2026-09-05.

The [first run report](first-run/REPORT.md) records an actual sequential-assistant feasibility experiment, not simulated agents. Four proposals were made on seed 7; three were accepted. Two more seeds ran numerical replay, not additional assistant sessions.

| Item | Status | Evidence |
| --- | --- | --- |
| Numerical OAK graph | Implemented, four computational modules | ../nodes/initial and ../nodes/learned |
| Assistant matrix updates | Measured, three accepted and one rejected | first-run/7/proposals and first-run/7/decisions |
| Controlled numerical comparisons | Small subset completed | [Raw results](first-run/final.json) |
| Agent-free export | All three selected networks passed isolated execution | Export evidence in raw results |
| Reproducibility | Complete fresh numerical replay matched | Replay command in EXPERIMENT.md |
| Engineering verdict | Demonstrated on the specified synthetic task | [Measured report](first-run/REPORT.md) |
| Scientific advantage | Not demonstrated | Strong numerical-only baseline is competitive; budgets and supervision differ |
| Hundred-node and independent-agent studies | Not run | Remain open research questions |

Code and study hashes, data identities, proposals, observations, decisions, selected network hashes, environment, and numerical results are retained under first-run. The actual complete run's snapshots and standalone exports can be regenerated using the recorded replay command. The representative initial and learned seed-7 OAK snapshots are committed as inspectable source documents.

Repository CI is separate from scientific evidence. The [delivery report](../../../docs/plans/0009-agent-guided-network/report.md) records publication checks. No result establishes the correctness of all possible predictions or an advantage attributable to semantic agent understanding.
