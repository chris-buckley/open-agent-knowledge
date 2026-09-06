"""One frozen OAK study definition; no test data is evaluated here."""
from pathlib import Path

from oak import Constant, Node, render

from compression.numeric import PROFILE
from compression.task import REGIMES, SAMPLE_COUNTS, SEEDS

GAIN_GRID = (8.0, 32.0, 128.0, 512.0, 2048.0, 8192.0)
MATCHED_GRID = (32.0, 128.0, 512.0, 2048.0)
FIT_STEPS = 200
FIT_RATE = 0.05
PROPOSAL_CAP = 4
ACCURACY_MARGIN = 0.01
LOSS_MARGIN = 0.02


def text() -> str:
    return render(Node(constants=[
        Constant(id="profile", value=PROFILE),
        Constant(id="hypothesis", value="Agent-chosen direct placement may retain capability at lower numerical storage than non-agent compression. Changing weights alone is not compression."),
        Constant(id="teacher", value="One fixed previously selected seed-7 attention model from baseline commit 01093746154ef972842df1c1c0f298101921b579; no new teacher-training seeds."),
        Constant(id="sampling", value={"seeds": list(SEEDS), "cases-per-regime": SAMPLE_COUNTS,
            "regimes": {name: list(recipe) for name, recipe in REGIMES.items()}, "seed-prefix": 20260906,
            "train-and-dev-regimes": ["short", "long", "crowded"], "test-regimes": list(REGIMES)}),
        Constant(id="families", value={"projected-teacher": 416, "folded-dense": 144, "diagonal": 20,
            "scaled-identity": 3, "sparse-fractions": [0.25, 0.5], "sparse-counts": [36, 72],
            "dtype": "float64", "maximum-coefficient": 8192.0}),
        Constant(id="fitting", value={"steps-per-family": FIT_STEPS, "rate": FIT_RATE,
            "checkpoint-interval": 20, "families": ["dense", "diagonal", "scaled-identity"],
            "labels": "final training labels only", "initialisation": "projection of the same folded teacher"}),
        Constant(id="search", value={"matched-grid": list(MATCHED_GRID), "matched-candidates": 4,
            "strong-grid": list(GAIN_GRID), "strong-candidates": 36, "output-gain": 8.0,
            "shared-prior": "Aligned equal-key retrieval and supplied one-hot class values; no learned coordinate transform is needed by the task."}),
        Constant(id="agent", value={"physical-proposers": 1, "shared-conversation": True, "live-data-seeds": list(SEEDS),
            "maximum-proposals-per-seed": PROPOSAL_CAP, "allowed": ["diagonal projection", "three explicit positive gains"],
            "agent-gradient-steps": 0, "language-model-tokens": None, "language-model-cost": None}),
        Constant(id="acceptance", value={"per-regime-teacher-accuracy-drop": ACCURACY_MARGIN,
            "mean-teacher-loss-increase": LOSS_MARGIN,
            "rule": "Require fewer coefficients and a smaller model file than teacher. Require no more coefficients than incumbent. For equal counts require mean development loss improvement above 1e-6; for fewer counts require capability floor."}),
        Constant(id="selection", value="Evaluate controls on development only. Record each agent proposal before applying it. Close all seed selections and serialize model identities before final test generation. Any new reasoning after testing belongs to a new study."),
        Constant(id="controls", value=["416-coefficient teacher", "exact 144-coefficient folding", "magnitude pruning",
            "diagonal projection", "three fitted parameter families", "four-candidate structured grid", "36-candidate structured grid",
            "zero-learned-parameter exact nearest-key algorithm"]),
        Constant(id="storage", value="Report numerical coefficient counts and float64 payload separately from expanded nonzeros, sparse uint16-equivalent index bytes, canonical OAK bytes, actual model JSON bytes, runtime bytes, and complete export bytes. Interpreter dependencies are disclosed, not counted as bundled bytes."),
        Constant(id="inference", value="The compact runtime contains only numeric attention, decoding, and bounded kernel encodings. The zero-parameter task algorithm is a separate labelled evaluation control, never an export fallback."),
        Constant(id="uncertainty", value="Paired 95% descriptive bootstrap intervals for fixed predictions against strong-grid control, 2000 resamples per seed/regime. Not a population estimate over independent agents; three data seeds share one teacher and one assistant."),
        Constant(id="tolerance", value={"fold-and-export-atol": 1e-10, "fold-and-export-rtol": 1e-10,
            "argmax": "require exact agreement on sampled fold/export cases; near ties remain a limitation"}),
    ]))


if __name__ == "__main__":
    Path(__file__).with_suffix(".oak.md").write_text(text(), encoding="utf-8")
