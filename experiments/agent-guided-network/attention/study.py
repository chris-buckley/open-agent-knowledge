"""Frozen OAK study description for the harder attention extension."""
from pathlib import Path
from oak import Constant, Node, render
from attention.numeric import PROFILE, SHAPES
from attention.learn import METHODS, STEPS, RATE
from attention.task import SEEDS, SPLITS


def text() -> str:
    return render(Node(constants=[
        Constant(id="profile", value=PROFILE),
        Constant(id="design", value="Two sequential single-head scaled dot-product cross-attention blocks with numerical softmax decoding. Not a complete Transformer, not multi-head self-attention."),
        Constant(id="equation", value="softmax(mask((q WQ)(k WK)^T / sqrt(8))) (v WV) WO"),
        Constant(id="parameters", value={"shapes": {k: list(v) for k, v in SHAPES.items()}, "trainable-scalars": 416, "absolute-limit": 64}),
        Constant(id="task", value="Random unit-vector key/value tables. The query equals one first-table key; its value identifies one second-table key, whose random four-class value is the label. Neither target index nor label is an inference input."),
        Constant(id="sampling", value={"seeds": list(SEEDS), "splits": {k: list(v) for k, v in SPLITS.items()},
                                      "normal-valid-lengths": [3, 6], "stress-valid-length": 16, "crowded-angle-radians": .12,
                                      "query-key-dimension": 8, "second-value-dimension": 4}),
        Constant(id="initialisation", value="Query/key matrices are independent Gaussian draws with standard deviation 0.2. Value/output matrices start at identity plus Gaussian noise of standard deviation 0.05 for all treatments."),
        Constant(id="budget", value={"warm-steps": 80, "proposal-cap": 4, "fit-steps-per-proposal": STEPS, "rate": RATE,
                                    "numerical-baseline-steps": 600, "baseline-checkpoint-interval": 25,
                                    "direct-edit-steps": 0, "scale-grid-candidates": 9,
                                    "conversation-tokens": None, "conversation-cost": None}),
        Constant(id="methods", value=list(METHODS)),
        Constant(id="selection", value={"metric": "development cross-entropy", "minimum-improvement": 1e-6,
                                       "maximum-accuracy-drop": .01, "candidate-fitting": "training final labels only",
                                       "direct-sharpen-score-factor": 2, "direct-output-factor": .5}),
        Constant(id="controls", value=["initial", "warm", "600-step Adam with development-selected checkpoints",
                                       "same Adam followed by a fixed nine-candidate attention/output scaling grid",
                                       "four real assistant proposals on seed 7; their methods replayed on seeds 19 and 31",
                                       "post-selection uniform-attention interventions at either block"]),
        Constant(id="information", value="Final training labels are identical for all treatments. Agent diagnostics additionally report aggregate target alignment and attention entropy. Indices are never used as numerical fitting targets. The scale grid has the same permitted matrix-scaling operations; no matched conversation-cost or causal semantic-benefit claim."),
        Constant(id="test-policy", value="Close selection and write all selected snapshot identities before generating final evaluation metrics. Long and crowded splits are stress tests, not development targets. Separation is procedural, not secure isolation from the implementer."),
        Constant(id="uncertainty", value="Three-seed descriptive means and ranges, not independent agent sessions or a superiority test. Cases are independent generated retrieval tasks; paired interventions share cases."),
        Constant(id="export", value={"format": "model.json plus standalone inference.py and hashes", "dependencies": "Python and NumPy",
                                     "atol": 1e-12, "rtol": 1e-12, "decision-rule": "argmax-first",
                                     "checks": "all three test regimes, fresh offline processes, OAK executor parity samples"}),
        Constant(id="pilot", value="Seed 0 only: development accuracy 53.90625% before training and 94.53125% after 80 steps; cross-entropy rises from 0.181818 after warm-up to 0.367197 after 150 more unselected steps. Retain strong checkpoint selection and report calibration independently of accuracy."),
        Constant(id="source", value="Attention Is All You Need, section 3.2.1, https://arxiv.org/html/1706.03762v7; inspected 2026-09-05. The paper supplies attention mathematics, not evidence for agent-guided training."),
    ]))


if __name__ == "__main__":
    Path(__file__).with_suffix(".oak.md").write_text(text())
