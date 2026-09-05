<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
profile: "oak-compact-attention-v1"

hypothesis: "Agent-chosen direct placement may retain capability at lower numerical storage than non-agent compression. Changing weights alone is not compression."

teacher: "One fixed previously selected seed-7 attention model from baseline commit 01093746154ef972842df1c1c0f298101921b579; no new teacher-training seeds."

sampling: {"seeds": [107, 223, 331], "cases-per-regime": {"train": 192, "dev": 192, "test": 1024}, "regimes": {"short": [6, null], "long": [16, null], "crowded": [16, 0.12], "extreme": [32, 0.04]}, "seed-prefix": 20260906, "train-and-dev-regimes": ["short", "long", "crowded"], "test-regimes": ["short", "long", "crowded", "extreme"]}

families: {"projected-teacher": 416, "folded-dense": 144, "diagonal": 20, "scaled-identity": 3, "sparse-fractions": [0.25, 0.5], "sparse-counts": [36, 72], "dtype": "float64", "maximum-coefficient": 8192.0}

fitting: {"steps-per-family": 200, "rate": 0.05, "checkpoint-interval": 20, "families": ["dense", "diagonal", "scaled-identity"], "labels": "final training labels only", "initialisation": "projection of the same folded teacher"}

search: {"matched-grid": [32.0, 128.0, 512.0, 2048.0], "matched-candidates": 4, "strong-grid": [8.0, 32.0, 128.0, 512.0, 2048.0, 8192.0], "strong-candidates": 36, "output-gain": 8.0, "shared-prior": "Aligned equal-key retrieval and supplied one-hot class values; no learned coordinate transform is needed by the task."}

agent: {"physical-proposers": 1, "shared-conversation": true, "live-data-seeds": [107, 223, 331], "maximum-proposals-per-seed": 4, "allowed": ["diagonal projection", "three explicit positive gains"], "agent-gradient-steps": 0, "language-model-tokens": null, "language-model-cost": null}

acceptance: {"per-regime-teacher-accuracy-drop": 0.01, "mean-teacher-loss-increase": 0.02, "rule": "Require fewer coefficients and a smaller model file than teacher. Require no more coefficients than incumbent. For equal counts require mean development loss improvement above 1e-6; for fewer counts require capability floor."}

selection: "Evaluate controls on development only. Record each agent proposal before applying it. Close all seed selections and serialize model identities before final test generation. Any new reasoning after testing belongs to a new study."

controls: ["416-coefficient teacher", "exact 144-coefficient folding", "magnitude pruning", "diagonal projection", "three fitted parameter families", "four-candidate structured grid", "36-candidate structured grid", "zero-learned-parameter exact nearest-key algorithm"]

storage: "Report numerical coefficient counts and float64 payload separately from expanded nonzeros, sparse uint16-equivalent index bytes, canonical OAK bytes, actual model JSON bytes, runtime bytes, and complete export bytes. Interpreter dependencies are disclosed, not counted as bundled bytes."

inference: "The compact runtime contains only numeric attention, decoding, and bounded kernel encodings. The zero-parameter task algorithm is a separate labelled evaluation control, never an export fallback."

uncertainty: "Paired 95% descriptive bootstrap intervals for fixed predictions against strong-grid control, 2000 resamples per seed/regime. Not a population estimate over independent agents; three data seeds share one teacher and one assistant."

tolerance: {"fold-and-export-atol": 1e-10, "fold-and-export-rtol": 1e-10, "argmax": "require exact agreement on sampled fold/export cases; near ties remain a limitation"}
</constants>