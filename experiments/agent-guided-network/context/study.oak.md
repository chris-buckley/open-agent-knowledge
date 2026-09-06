<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
profile: "oak-context-questions-v1"

settings: {"seeds": [101, 202, 303], "arms": ["log", "log-questions", "context", "context-questions"], "train_episodes": 2400, "development_per_regime": 128, "test_per_regime": 256, "blocks": 4, "steps_per_block": 400, "batch": 48, "learning_rate": 0.003, "auxiliary_weight": 0.3, "max_live_proposals": 2, "min_gain": 0.01, "max_regression": 0.03, "width": 24, "context_rows": 6, "reads": 2, "max_events": 64, "max_words": 12, "max_reply": 8, "readiness": 0.85, "teacher": "one shared-context assistant", "inference": "numerical only"}

boundaries: "Fresh reconstruction; unchanged prior protocol. Main reply loss in all arms; auxiliary arms receive extra state labels only during training. All arms retain the event log. Context adds parameters. Final tests stay closed until every selection is fixed."
</constants>
