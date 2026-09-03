"""OAK, JSON-LD, controlled-style, and authoring-helper verification."""

from __future__ import annotations

import json

from build.checks.fixtures import contract_schemas, normalise_process
from build.checks.text import validate_display_values
from oak.authoring import ACT
from oak.node.model import Node
from oak.node.parts.instructions import Instruction
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.steps import Act, Call
from oak.node.parts.processes.values import (
    InterfaceValue,
    LiteralValue,
    StateValue,
    ValueBinding,
)
from oak.parse.fragments import parse_fragment
from oak.render import render
from oak.render.oak.processes import step_lines


def validate_act_authoring() -> None:
    """Verify direct ACT authoring and every canonical binding suffix."""
    native = ACT(
        "Classify <REPORT> and produce <SEVERITY>.",
        inputs=[
            ValueBinding(
                placeholder="REPORT",
                value=InterfaceValue(
                    interface="interface.report",
                    placeholder="REPORT",
                ),
            )
        ],
        outputs=["SEVERITY"],
    )
    exact = ACT.tool(
        "jobs.status",
        "Read <JOB_ID> and produce <STATUS>.",
        inputs=[
            ValueBinding(
                placeholder="JOB_ID",
                value=StateValue(
                    state="state.job-id"
                ),
            )
        ],
        outputs=["STATUS"],
    )

    if (
        not isinstance(native, Act)
        or native.tool is not None
    ):
        raise RuntimeError(
            "ACT did not return one interpreter-native Act"
        )

    if (
        not isinstance(exact, Act)
        or exact.tool != "jobs.status"
    ):
        raise RuntimeError(
            "ACT.tool did not return one exact named-tool Act"
        )

    if (
        hasattr(ACT, "infer")
        or hasattr(ACT, "use")
    ):
        raise RuntimeError(
            "ACT exposes a forbidden helper"
        )

    if "\n".join(
        step_lines(native)
    ) != (
        "ACT Classify <REPORT> and produce <SEVERITY>. "
        "(REPORT=$interface.report.REPORT) -> SEVERITY"
    ):
        raise RuntimeError(
            "ACT changed interpreter-native OAK syntax"
        )

    if "\n".join(
        step_lines(exact)
    ) != (
        'ACT TOOL "jobs.status": '
        "Read <JOB_ID> and produce <STATUS>. "
        "(JOB_ID=$state.job-id) -> STATUS"
    ):
        raise RuntimeError(
            "ACT.tool changed exact named-tool OAK syntax"
        )

    combinations = (
        (
            ACT("Wait."),
            "ACT Wait. ()",
        ),
        (
            ACT(
                "Read <NOTE>.",
                inputs=[
                    ValueBinding(
                        placeholder="NOTE",
                        value=LiteralValue(value=1),
                    )
                ],
            ),
            "ACT Read <NOTE>. (NOTE=1)",
        ),
        (
            ACT(
                "Produce <NOTE>.",
                outputs=["NOTE"],
            ),
            "ACT Produce <NOTE>. () -> NOTE",
        ),
        (
            Call(
                process="process.run"
            ),
            "CALL process.run ()",
        ),
        (
            ACT(
                "Produce <NOTE>.",
                output="schema.note",
                outputs=["NOTE"],
            ),
            (
                'ACT output="schema.note": '
                "Produce <NOTE>. () -> NOTE"
            ),
        ),
        (
            ACT.tool(
                "jobs.status",
                "Read <JOB_ID> and produce <STATUS>.",
                input="schema.job",
                output="schema.status",
                inputs=[
                    ValueBinding(
                        placeholder="JOB_ID",
                        value=StateValue(
                            state="state.job-id"
                        ),
                    )
                ],
                outputs=["STATUS"],
            ),
            (
                'ACT TOOL "jobs.status" '
                'input="schema.job" '
                'output="schema.status": '
                "Read <JOB_ID> and produce <STATUS>. "
                "(JOB_ID=$state.job-id) -> STATUS"
            ),
        ),
    )

    for step, expected in combinations:
        line = "\n".join(
            step_lines(step)
        )

        if line != expected:
            raise RuntimeError(
                f"suffix render changed: {line}"
            )

        parsed = parse_fragment(
            type(step),
            line,
            path="suffix",
        )

        if (
            parsed.model_dump()
            != step.model_dump()
        ):
            raise RuntimeError(
                f"suffix parse changed: {line}"
            )


def validate_json_ld_style_display() -> None:
    """Verify process JSON-LD, controlled wording, and value display."""
    raw, normal = contract_schemas()
    contract = Node(
        schemas=[
            raw,
            normal,
        ],
        processes=[
            normalise_process(),
            Process(
                id="handle",
                name="Handle request",
                steps=[
                    Call(
                        process="process.normalise",
                        inputs=[
                            ValueBinding(
                                placeholder="RAW_NAME",
                                value=LiteralValue(
                                    value="Ada"
                                ),
                            )
                        ],
                        outputs=["NORMAL_NAME"],
                    )
                ],
            ),
        ],
    )
    linked = json.loads(
        render(
            contract,
            render="json-ld",
            document=(
                "https://example.org/"
                "oak/contract.oak.md"
            ),
            vocabulary="https://example.org/oak#",
        )
    )
    normalise, handle = linked["processes"]
    call = handle["steps"][0]

    if not (
        linked.get("@id")
        == (
            "https://example.org/"
            "oak/contract.oak.md"
        )
        and normalise["input"]["@id"].endswith(
            "#schema.raw-name"
        )
        and normalise["output"]["@id"].endswith(
            "#schema.normal-name"
        )
        and call["process"]["@id"].endswith(
            "#process.normalise"
        )
        and call["outputs"] == ["NORMAL_NAME"]
    ):
        raise RuntimeError(
            "JSON-LD process contract is wrong"
        )

    styled = render(
        Node(
            instructions=[
                Instruction(
                    id="wording",
                    body="Utilize the exact command.",
                )
            ]
        ),
        style="asd-ste100-9",
    )

    if "Use the exact command." not in styled:
        raise RuntimeError(
            "controlled style failed"
        )

    validate_display_values()


__all__ = [
    "validate_act_authoring",
    "validate_json_ld_style_display",
]
