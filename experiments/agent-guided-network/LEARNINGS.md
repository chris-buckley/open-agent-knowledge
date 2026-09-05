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
| L010 | Exact matrix-product folding may remove representation redundancy before learning. | Verified on 12,288 cases: 416 stored coefficients become 144, maximum probability difference 4.72e-15; exact decisions on tested cases. | [Compression evidence](results/compression-run/REPORT.md#exact-compression-before-learning) |
| L011 | Smaller task-specific structure is not necessarily preservation of learned behaviour. | A structured replacement must be distinguished from exact folding and from a general AI compression claim. | [Compression hypothesis](compression/COMPRESSION.md#hypothesis-and-verdicts) |
| L012 | Structured direct placement produces a three-gain task replacement with 100% accuracy on three tested regimes. | Three independent stored coefficients expand to 20 nonzeros; task structure is supplied. This is not fidelity-preserving compression of general AI. | [Compression results](results/compression-run/REPORT.md#results) |
| L013 | A four-candidate non-agent search finds exactly the same compact model. | The entire selected-model benefit is matched; no agent-specific advantage established. | [Controls](results/compression-run/REPORT.md#results) |
| L014 | A larger search can select a worse out-of-distribution model on nearly equal development losses. | Observed for this fixed grid, not a universal result about search budgets. | [Grid and stress results](results/compression-run/REPORT.md#results) |
| L015 | This task admits an exact zero-learned-parameter solution. | The nearest-key algorithm solves all tested cases; problem structure, not latent general intelligence, explains much of the compression opportunity. | [Algorithmic control](results/compression-run/REPORT.md#data-and-controls) |
| L016 | Coefficient reduction overstates complete deployment reduction here. | 138.67 times fewer coefficients corresponds to 1.84 times smaller actual export; same-runtime comparison is 1.27 times. | [Byte accounting](results/compression-run/REPORT.md#storage-is-not-just-coefficient-count) |
| L017 | Better stress accuracy can coexist with worse probabilistic loss. | Three gains reach 61.78% on harder stress cases, but loss 2.341369 exceeds the teacher's 1.531828. | [Stress failure](results/compression-run/REPORT.md#results) |
| L018 | Fresh decisions across data seeds are not independent agent trials. | Seven actual proposals were made in one shared conversation; two later seeds deliberately transfer the first seed's selected gains. | [Live decisions](results/compression-run/REPORT.md#live-proposal-ledger) |

## How to extend this index

Give each finding a stable ID, a falsifiable statement, an observed/proposed/inconclusive status, a scope limit, and a link to immutable run evidence. Record contradictory results and rejected updates. Update the index after a completed observation or study, not on the strength of an agent explanation.

Keep parameter counts, active weights, dtype, metadata, code bytes, and complete deployed bytes separate. Keep one physical assistant, logical node roles, fresh decisions, and deterministic replay separate. Unknown conversation cost remains unknown.

## Questions still open

Does direct agent placement improve the quality-versus-size frontier beyond automatic pruning, tying, and fitting? Does useful compression transfer to less structured tasks? Do independent agent trials reproduce an advantage under matched information and total cost? The compression study confirms a compact task-specific solution but its structured non-agent control matches it. Independent-agent and general-AI compression claims remain open.
