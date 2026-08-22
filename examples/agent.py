"""An agent as an OAK composition: a commit message writer.

Run this file to author and validate the composition.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "docs"))
from vocabulary_sketch import (
    Constant,
    Input,
    Instruction,
    Knowledge,
    Process,
    Ref,
    Schema,
    Trigger,
)

agent = Knowledge(
    id="oak:agent/commit-writer",
    interpretation=[Ref(ref="oak:agent/commit-writer/one-per-change")],
    children=[
        Trigger(
            id="oak:agent/commit-writer/on-commit-request",
            type="trigger",
            when="the user asks to commit staged changes with a well formed message",
            then=Ref(ref="oak:agent/commit-writer/run"),
        ),
        Instruction(
            id="oak:agent/commit-writer/one-per-change",
            type="instruction",
            body="Write one commit per logical change.",
        ),
        Instruction(
            id="oak:agent/commit-writer/no-secrets",
            type="instruction",
            body="Stop when the diff contains a secret.",
        ),
        Constant(
            id="oak:agent/commit-writer/types",
            type="constant",
            value=["feat", "fix", "docs", "refactor", "test", "chore"],
        ),
        Schema(
            id="oak:agent/commit-writer/message-shape",
            type="schema",
            body={
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "scope": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["type", "description"],
            },
        ),
        Schema(
            id="oak:agent/commit-writer/diff-shape",
            type="schema",
            body={
                "type": "object",
                "properties": {"staged_diff": {"type": "string"}},
                "required": ["staged_diff"],
            },
        ),
        Input(
            id="oak:agent/commit-writer/in",
            type="input",
            contract=Ref(ref="oak:agent/commit-writer/diff-shape"),
        ),
        Process(
            id="oak:agent/commit-writer/run",
            type="process",
            steps=[
                "Review the staged diff.",
                "Group the changes by concern.",
                "Draft one message per group in the message shape.",
                "Commit each group.",
            ],
            uses=[
                Ref(ref="oak:agent/commit-writer/types"),
                Ref(ref="oak:agent/commit-writer/message-shape"),
            ],
        ),
    ],
)

if __name__ == "__main__":
    print(f"agent ok: {agent.id}, {len(agent.children)} children")
