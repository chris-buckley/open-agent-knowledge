"""An SOP as an OAK composition: release a new version.

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
    State,
    Trigger,
)

sop = Knowledge(
    id="oak:sop/release",
    interpretation=[Ref(ref="oak:sop/release/stop-on-failure")],
    children=[
        Trigger(
            id="oak:sop/release/on-release-request",
            type="trigger",
            when="a maintainer wants to publish a new version",
            then=Ref(ref="oak:sop/release/run"),
        ),
        Instruction(
            id="oak:sop/release/stop-on-failure",
            type="instruction",
            body="Stop the release when any step fails.",
        ),
        Constant(
            id="oak:sop/release/registry",
            type="constant",
            value="https://pypi.org/",
        ),
        Schema(
            id="oak:sop/release/request-shape",
            type="schema",
            body={
                "type": "object",
                "properties": {
                    "bump": {"enum": ["major", "minor", "patch"]},
                },
                "required": ["bump"],
            },
        ),
        Input(
            id="oak:sop/release/in",
            type="input",
            contract=Ref(ref="oak:sop/release/request-shape"),
        ),
        State(
            id="oak:sop/release/last-released",
            type="state",
            value="0.0.0",
        ),
        Process(
            id="oak:sop/release/run",
            type="process",
            steps=[
                "Run the full test suite.",
                "Raise the version by the requested bump.",
                "Tag the commit with the new version.",
                "Push the tag.",
                "Publish the package to the registry.",
                "Record the new version in the last released state.",
            ],
            uses=[Ref(ref="oak:sop/release/registry")],
        ),
    ],
)

if __name__ == "__main__":
    print(f"sop ok: {sop.id}, {len(sop.children)} children")
