<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
profile: "oak-attention-two-hop-v1"

design: "Two sequential single-head scaled dot-product cross-attention blocks with numerical softmax decoding. Not a complete Transformer, not multi-head self-attention."

equation: "softmax(mask((q WQ)(k WK)^T / sqrt(8))) (v WV) WO"

parameters: {"shapes": {"first-query": [8, 8], "first-key": [8, 8], "first-value": [8, 8], "first-output": [8, 8], "second-query": [8, 8], "second-key": [8, 8], "second-value": [4, 4], "second-output": [4, 4]}, "trainable-scalars": 416, "absolute-limit": 64}

task: "Random unit-vector key/value tables. The query equals one first-table key; its value identifies one second-table key, whose random four-class value is the label. Neither target index nor label is an inference input."

sampling: {"seeds": [7, 19, 31], "splits": {"train": [512, 6, 1000], "dev": [256, 6, 2000], "test": [512, 6, 3000], "long": [512, 16, 4000], "crowded": [512, 16, 5000]}, "normal-valid-lengths": [3, 6], "stress-valid-length": 16, "crowded-angle-radians": 0.12, "query-key-dimension": 8, "second-value-dimension": 4}

initialisation: "Query/key matrices are independent Gaussian draws with standard deviation 0.2. Value/output matrices start at identity plus Gaussian noise of standard deviation 0.05 for all treatments."

budget: {"warm-steps": 80, "proposal-cap": 4, "fit-steps-per-proposal": 150, "rate": 0.025, "numerical-baseline-steps": 600, "baseline-checkpoint-interval": 25, "direct-edit-steps": 0, "scale-grid-candidates": 9, "conversation-tokens": null, "conversation-cost": null}

methods: ["joint", "first", "second", "sharpen-first", "sharpen-second", "sharpen-both", "soften-both", "cool-output", "sharpen-both-direct"]

selection: {"metric": "development cross-entropy", "minimum-improvement": 1e-06, "maximum-accuracy-drop": 0.01, "candidate-fitting": "training final labels only", "direct-sharpen-score-factor": 2, "direct-output-factor": 0.5}

controls: ["initial", "warm", "600-step Adam with development-selected checkpoints", "same Adam followed by a fixed nine-candidate attention/output scaling grid", "four real assistant proposals on seed 7; their methods replayed on seeds 19 and 31", "post-selection uniform-attention interventions at either block"]

information: "Final training labels are identical for all treatments. Agent diagnostics additionally report aggregate target alignment and attention entropy. Indices are never used as numerical fitting targets. The scale grid has the same permitted matrix-scaling operations; no matched conversation-cost or causal semantic-benefit claim."

test-policy: "Close selection and write all selected snapshot identities before generating final evaluation metrics. Long and crowded splits are stress tests, not development targets. Separation is procedural, not secure isolation from the implementer."

uncertainty: "Three-seed descriptive means and ranges, not independent agent sessions or a superiority test. Cases are independent generated retrieval tasks; paired interventions share cases."

export: {"format": "model.json plus standalone inference.py and hashes", "dependencies": "Python and NumPy", "atol": 1e-12, "rtol": 1e-12, "decision-rule": "argmax-first", "checks": "all three test regimes, fresh offline processes, OAK executor parity samples"}

pilot: "Seed 0 only: development accuracy 53.90625% before training and 94.53125% after 80 steps; cross-entropy rises from 0.181818 after warm-up to 0.367197 after 150 more unselected steps. Retain strong checkpoint selection and report calibration independently of accuracy."

source: "Attention Is All You Need, section 3.2.1, https://arxiv.org/html/1706.03762v7; inspected 2026-09-05. The paper supplies attention mathematics, not evidence for agent-guided training."
</constants>