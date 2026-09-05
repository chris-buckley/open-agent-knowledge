<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
arrival: {"event": "Continue growing the balance.", "count": 2}

initial-state: {"state.current-balance": 100, "state.reflection-target": 800}

expected-states: [{"state.current-balance": 815.04, "state.reflection-target": 6400}, {"state.current-balance": 6642.28, "state.reflection-target": 51200}]

expected-emissions: [{"BALANCE": 815.04, "REFLECTION": "Balance 815.04 passed target 800."}, {"BALANCE": 6642.28, "REFLECTION": "Balance 6642.28 passed target 6400."}]

failure: "A reflection failure after staged growth leaves caller state unchanged and returns no committed result. Host calls are not rolled back."

host: "Exact math.multiply arithmetic and deterministic reflection; two fixture arrivals, not an automatic infinite scheduler."
</constants>