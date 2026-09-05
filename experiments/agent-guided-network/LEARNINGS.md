# Learning index

Updated: 6 September 2026.
Scope: Evidence from this experiment, not established properties of general AI.
Intent owner: [EXPERIMENT.md](EXPERIMENT.md).

## Current hypothesis

H06: A capable training agent may directly place, remove, tie, or revise numerical weights so that a smaller agent-free network retains useful capability. Test capability at a measured storage budget, not merely whether an agent edited weights. Hand placement alone does not imply compression.

The user authorised testing this hypothesis on the same branch on 6 September 2026, Brisbane time. [The compression protocol](compression/COMPRESSION.md) defines the next study. Keep new observations here as they become supported; do not revise old results to make a new hypothesis appear confirmed.

## Evidence ledger

| ID | Finding | Status and limit | Evidence |
| --- | --- | --- | --- |
| L001 | An assistant can propose real changes to inline OAK matrices; accepted revisions run without the assistant. | Demonstrated on small synthetic networks, not general intelligence. | [First run](results/first-run/REPORT.md) |
| L002 | A locally sensible correction can harm whole-network performance. | One first-run update was rejected; no universal rule against local learning. | [First-run decisions](results/first-run/REPORT.md#actual-assistant-decisions) |
| L003 | Agent participation has not shown superiority over numerical optimisation. | First-run numerical and concept-fitting controls matched the live agent's accuracy. | [First-run controls](results/first-run/REPORT.md#results) |
| L004 | OAK can own numerical attention projections and export an agent-free inference path. | Two single-head cross-attention modules, 416 scalars; not a full Transformer. | [Attention study](results/attention-run/REPORT.md) |
| L005 | Calibration is different from retrieval accuracy. | The live attention session improved loss without changing any selected answer; a numerical grid matched it. | [Actual attention decisions](results/attention-run/REPORT.md#what-the-assistant-actually-did) |
| L006 | Increasing correct first-hop attention mass can worsen final loss. | Observed on one candidate; does not imply sharp attention is always bad. | [Attention proposals](results/attention-run/REPORT.md#what-the-assistant-actually-did) |
| L007 | The measured network depends on its attention mechanism. | Disabling attention reduced accuracy. This was an inference intervention, not matched retraining or a universal explanation. | [Attention interventions](results/attention-run/REPORT.md#does-attention-actually-matter) |
| L008 | Short-table performance did not imply reliable long or near-distractor retrieval. | Distribution-shift limitation of the tested models. | [Attention results](results/attention-run/REPORT.md#results) |
| L009 | Numerical replay is not another agent trial. | Both earlier studies had one live decision seed and two replay seeds. | [Attention accounting](results/attention-run/REPORT.md#resources-and-reproducibility) |
| L010 | Exact matrix-product folding may remove representation redundancy before learning. | Algebraic proposal: 416 stored coefficients become 144 for this closed graph. Numerical verification pending. | [Compression derivation](compression/COMPRESSION.md#exact-folding) |
| L011 | Smaller task-specific structure is not necessarily preservation of learned behaviour. | A structured replacement must be distinguished from exact folding and from a general AI compression claim. | [Compression hypothesis](compression/COMPRESSION.md#hypothesis-and-verdicts) |

## How to extend this index

Give each finding a stable ID, a falsifiable statement, an observed/proposed/inconclusive status, a scope limit, and a link to immutable run evidence. Record contradictory results and rejected updates. Update the index after a completed observation or study, not on the strength of an agent explanation.

Keep parameter counts, active weights, dtype, metadata, code bytes, and complete deployed bytes separate. Keep one physical assistant, logical node roles, fresh decisions, and deterministic replay separate. Unknown conversation cost remains unknown.

## Questions still open

Does direct agent placement improve the quality-versus-size frontier beyond automatic pruning, tying, and fitting? Does useful compression transfer to less structured tasks? Do independent agent trials reproduce an advantage under matched information and total cost? Neither prior study answers these questions.
