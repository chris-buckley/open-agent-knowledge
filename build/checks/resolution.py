"""Local and cross-document resolution verification."""

from __future__ import annotations

from build.checks.fixtures import contract_schemas, normalise_process
from oak.node.model import Node
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.steps import Act, Call, Emit
from oak.node.parts.processes.values import BindingValue, LiteralValue, ValueBinding
from oak.node.parts.schemas.constraints import Type
from oak.node.parts.schemas.model import Schema, where
from oak.node.parts.triggers import Trigger
from oak.resolve.errors import ResolutionError
from oak.resolve.resolver import resolve


def validate_resolution() -> None:
    """Verify reachable documents and resolved schema and process contracts."""
    shared = Node(
        schemas=[
            Schema(
                id="shared",
                template="<VALUE>",
                where=[where("VALUE", Type(of="string"))],
            )
        ]
    )
    root = Node(
        triggers=[
            Trigger(
                id="shared-arrived",
                event="A shared value arrives.",
                source="interface.shared",
                process="process.read-shared",
            )
        ],
        processes=[
            Process(
                id="read-shared",
                name="Read shared",
                input="shared.oak.md#schema.shared",
                steps=[
                    Act(
                        instruction="Read <VALUE>.",
                        inputs=[
                            ValueBinding(
                                placeholder="VALUE",
                                value=BindingValue(binding="VALUE"),
                            )
                        ],
                    )
                ],
            ),
            Process(
                id="emit-shared",
                name="Emit shared",
                input="shared.oak.md#schema.shared",
                steps=[Emit(interface="interface.shared-output")],
            ),
        ],
        interfaces=[
            Interface(
                id="shared",
                flow="receives",
                schema="shared.oak.md#schema.shared",
            ),
            Interface(
                id="shared-output",
                flow="emits",
                schema="shared.oak.md#schema.shared",
            ),
        ],
    )
    graph = resolve(
        root,
        source="root.oak.md",
        load=lambda path: shared if path == "shared.oak.md" else None,
    )
    _document, schema = graph.entry(
        "root.oak.md",
        "shared.oak.md#schema.shared",
        Schema,
    )
    if schema.id != "shared":
        raise RuntimeError("resolution selected the wrong schema")

    raw, normal = contract_schemas()
    target = Node(
        schemas=[raw, normal],
        processes=[normalise_process()],
    )
    caller = Node(
        processes=[
            Process(
                id="handle",
                name="Handle request",
                steps=[
                    Call(
                        process="target.oak.md#process.normalise",
                        inputs=[
                            ValueBinding(
                                placeholder="RAW_NAME",
                                value=LiteralValue(value="Ada"),
                            )
                        ],
                        outputs=["NORMAL_NAME"],
                    )
                ],
            )
        ]
    )

    def loader(path: str) -> Node | None:
        return target if path == "target.oak.md" else None

    resolve(caller, source="root.oak.md", load=loader)

    failures = (
        (
            "call_contract_mismatch",
            Node(
                processes=[
                    Process(
                        id="handle",
                        name="Handle request",
                        steps=[
                            Call(process="target.oak.md#process.normalise")
                        ],
                    )
                ]
            ),
        ),
        (
            "trigger_contract_mismatch",
            Node(
                triggers=[
                    Trigger(
                        id="invalid",
                        event="A name arrives.",
                        process="target.oak.md#process.normalise",
                    )
                ]
            ),
        ),
        (
            "source_trigger_schema_mismatch",
            Node(
                interfaces=[
                    Interface(
                        id="request",
                        flow="receives",
                        schema="target.oak.md#schema.raw-name",
                    )
                ],
                triggers=[
                    Trigger(
                        id="request-arrived",
                        event="A request arrives.",
                        source="interface.request",
                        process="process.read-normal",
                    )
                ],
                processes=[
                    Process(
                        id="read-normal",
                        name="Read normal",
                        input="target.oak.md#schema.normal-name",
                        steps=[
                            Act(
                                instruction="Read <NORMAL_NAME>.",
                                inputs=[
                                    ValueBinding(
                                        placeholder="NORMAL_NAME",
                                        value=BindingValue(
                                            binding="NORMAL_NAME"
                                        ),
                                    )
                                ],
                            )
                        ],
                    )
                ],
            ),
        ),
        (
            "emit_schema_binding_mismatch",
            Node(
                interfaces=[
                    Interface(
                        id="result",
                        flow="emits",
                        schema="target.oak.md#schema.normal-name",
                    )
                ],
                processes=[
                    Process(
                        id="emit-result",
                        name="Emit result",
                        steps=[
                            Act(
                                instruction="Produce <WRONG>.",
                                outputs=["WRONG"],
                            ),
                            Emit(
                                interface="interface.result",
                                bindings=[
                                    ValueBinding(
                                        placeholder="WRONG",
                                        value=BindingValue(binding="WRONG"),
                                    )
                                ],
                            ),
                        ],
                    )
                ],
            ),
        ),
        (
            "invalid_static_schema_binding",
            Node(
                interfaces=[
                    Interface(
                        id="result",
                        flow="emits",
                        schema="target.oak.md#schema.normal-name",
                    )
                ],
                processes=[
                    Process(
                        id="emit-blank",
                        name="Emit blank",
                        steps=[
                            Emit(
                                interface="interface.result",
                                bindings=[
                                    ValueBinding(
                                        placeholder="NORMAL_NAME",
                                        value=LiteralValue(value=""),
                                    )
                                ],
                            )
                        ],
                    )
                ],
            ),
        ),
    )

    for code, invalid in failures:
        try:
            resolve(invalid, source="root.oak.md", load=loader)
        except ResolutionError as error:
            if error.code != code:
                raise RuntimeError(
                    f"expected {code}, got {error.code}"
                ) from None
        else:
            raise RuntimeError(f"expected {code}")

    relative_contract = Node(
        processes=[
            Process(
                id="invalid",
                name="Build result",
                input="target.oak.md#schema.raw-name",
                output="target.oak.md#schema.normal-name",
                steps=[
                    Act(
                        instruction="Read <RAW_NAME>.",
                        inputs=[
                            ValueBinding(
                                placeholder="RAW_NAME",
                                value=BindingValue(binding="RAW_NAME"),
                            )
                        ],
                    )
                ],
            )
        ]
    )
    try:
        resolve(relative_contract, source="root.oak.md", load=loader)
    except ResolutionError as error:
        if error.code != "process_output_binding_mismatch":
            raise RuntimeError(
                "expected process_output_binding_mismatch, "
                f"got {error.code}"
            ) from None
    else:
        raise RuntimeError("expected process_output_binding_mismatch")


__all__ = ["validate_resolution"]
