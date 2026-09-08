<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
request: {"OWNER": "alpha", "INSTANCE": "instances/alpha", "ID": "item-1", "TEXT": "Urgent: review the synthetic item", "POLICY_ID": "priority", "RETENTION": "summary"}

expected: {"category": "match", "reference": "state/history/records/item-1.json", "mode": "summary", "contains-source-text": false}

host: "Repository fixtures use disposable instances and a deterministic normal-file adapter. No live model, user state, installation or external service is involved."
</constants>