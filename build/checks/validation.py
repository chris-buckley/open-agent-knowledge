"""Node, process, trigger, act, and schema contract verification."""

from __future__ import annotations

from decimal import Decimal
from typing import Callable

from pydantic import ValidationError

from build.checks.fixtures import contract_schemas, normalise_process
from oak.node.model import Node
from oak.node.parts.constants import Constant
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.steps import Act, Call, Emit
from oak.node.parts.processes.values import (
    BindingValue,
    LiteralValue,
    ValueBinding,
)
from oak.node.parts.schemas.binding import SchemaBindingError
from oak.node.parts.schemas.constraints import AtLeast, Type
from oak.node.parts.schemas.model import Schema, where
from oak.node.parts.triggers import Trigger
from oak.vocabulary.datatypes.quantity import Quantity
from oak.vocabulary.units import Unit


def _expect_rule(
    code: str,
    author: Callable[[], object],
) -> None:
    """Require one authoring callback to raise the named rule code."""
    try:
        author()

    except ValidationError as error:
        if code not in {
            str(item["type"])
            for item in error.errors()
        }:
            raise RuntimeError(
                f"expected {code}, got {error}"
            ) from None

        return

    raise RuntimeError(
        f"expected {code}"
    )


def validate_contract_rules() -> None:
    """Verify local trigger, process, act, interface, and schema rules."""
    raw, normal = contract_schemas()

    def trigger_seed_mismatch() -> None:
        Node(
            schemas=[
                raw,
                normal,
            ],
            triggers=[
                Trigger(
                    id="invalid",
                    event="A name arrives.",
                    process="process.normalise",
                )
            ],
            processes=[
                normalise_process()
            ],
        )

    def trigger_event_overlap() -> None:
        Node(
            schemas=[
                raw,
                normal,
            ],
            triggers=[
                Trigger(
                    id="first",
                    event="A name arrives.",
                    process="process.handle",
                ),
                Trigger(
                    id="second",
                    event="A name arrives.",
                    process="process.handle",
                ),
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

    def output_missing() -> None:
        Node(
            schemas=[
                raw,
                normal,
            ],
            processes=[
                Process(
                    id="normalise",
                    name="Normalise name",
                    input="schema.raw-name",
                    output="schema.normal-name",
                    steps=[
                        Act(
                            instruction="Read <RAW_NAME>.",
                            inputs=[
                                ValueBinding(
                                    placeholder="RAW_NAME",
                                    value=BindingValue(
                                        binding="RAW_NAME"
                                    ),
                                )
                            ],
                        )
                    ],
                )
            ],
        )

    def call_mismatch() -> None:
        Node(
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
                            process="process.normalise"
                        )
                    ],
                ),
            ],
        )

    def act_mismatch() -> None:
        Node(
            schemas=[
                raw,
                normal,
            ],
            processes=[
                Process(
                    id="read-name",
                    name="Read name",
                    steps=[
                        Act(
                            input="schema.raw-name",
                            instruction="Read <NOTE>.",
                            inputs=[
                                ValueBinding(
                                    placeholder="NOTE",
                                    value=LiteralValue(
                                        value="x"
                                    ),
                                )
                            ],
                        )
                    ],
                )
            ],
        )

    def typed_constant_invalid() -> None:
        Node(
            schemas=[raw],
            constants=[
                Constant(
                    id="fixed-name",
                    schema="schema.raw-name",
                    placeholder="RAW_NAME",
                    value=5,
                )
            ],
        )

    def typed_constant_unknown() -> None:
        Node(
            schemas=[raw],
            constants=[
                Constant(
                    id="fixed-name",
                    schema="schema.raw-name",
                    placeholder="MISSING",
                    value="Ada",
                )
            ],
        )

    def incomplete_binding() -> None:
        Constant(
            id="fixed-name",
            schema="schema.raw-name",
            value="Ada",
        )

    def reserved_instruction() -> None:
        Act(
            instruction=(
                'input="schema.fake": '
                "Say <X>."
            ),
            inputs=[
                ValueBinding(
                    placeholder="X",
                    value=LiteralValue(
                        value="hi"
                    ),
                )
            ],
        )

    def trigger_binding_read() -> None:
        Trigger(
            id="invalid",
            event="A name arrives.",
            process="process.normalise",
            seed=[
                ValueBinding(
                    placeholder="RAW_NAME",
                    value=BindingValue(
                        binding="RAW_NAME"
                    ),
                )
            ],
        )

    def trigger_source_emit() -> None:
        Node(
            schemas=[raw, normal],
            interfaces=[
                Interface(
                    id="name-result",
                    flow="emits",
                    schema="schema.raw-name",
                )
            ],
            triggers=[
                Trigger(
                    id="invalid",
                    event="A name arrives.",
                    source="interface.name-result",
                    process="process.normalise",
                )
            ],
            processes=[normalise_process()],
        )

    def trigger_source_overlap() -> None:
        Node(
            schemas=[raw, normal],
            interfaces=[
                Interface(
                    id="name",
                    flow="receives",
                    schema="schema.raw-name",
                )
            ],
            triggers=[
                Trigger(
                    id="first",
                    event="A name arrives.",
                    source="interface.name",
                    process="process.normalise",
                ),
                Trigger(
                    id="second",
                    event="Another name arrives.",
                    source="interface.name",
                    process="process.normalise",
                ),
            ],
            processes=[normalise_process()],
        )

    def source_trigger_seed() -> None:
        Trigger(
            id="invalid",
            event="A name arrives.",
            source="interface.name",
            process="process.normalise",
            seed=[
                ValueBinding(
                    placeholder="RAW_NAME",
                    value=LiteralValue(value="Ada"),
                )
            ],
        )

    def source_process_without_input() -> None:
        Node(
            schemas=[raw],
            interfaces=[
                Interface(
                    id="name",
                    flow="receives",
                    schema="schema.raw-name",
                )
            ],
            triggers=[
                Trigger(
                    id="invalid",
                    event="A name arrives.",
                    source="interface.name",
                    process="process.handle",
                )
            ],
            processes=[
                Process(
                    id="handle",
                    name="Handle request",
                    steps=[Act(instruction="Handle the request.")],
                )
            ],
        )

    def source_schema_mismatch() -> None:
        Node(
            schemas=[raw, normal],
            interfaces=[
                Interface(
                    id="name",
                    flow="receives",
                    schema="schema.raw-name",
                )
            ],
            triggers=[
                Trigger(
                    id="invalid",
                    event="A name arrives.",
                    source="interface.name",
                    process="process.read-normal",
                )
            ],
            processes=[
                Process(
                    id="read-normal",
                    name="Read normal",
                    input="schema.normal-name",
                    steps=[
                        Act(
                            instruction="Read <NORMAL_NAME>.",
                            inputs=[
                                ValueBinding(
                                    placeholder="NORMAL_NAME",
                                    value=BindingValue(binding="NORMAL_NAME"),
                                )
                            ],
                        )
                    ],
                )
            ],
        )

    def emit_through_receive() -> None:
        Node(
            schemas=[raw],
            interfaces=[
                Interface(
                    id="name",
                    flow="receives",
                    schema="schema.raw-name",
                )
            ],
            processes=[
                Process(
                    id="echo-name",
                    name="Echo name",
                    input="schema.raw-name",
                    steps=[Emit(interface="interface.name")],
                )
            ],
        )

    def inferred_emit_missing() -> None:
        Node(
            schemas=[normal],
            interfaces=[
                Interface(
                    id="normal-result",
                    flow="emits",
                    schema="schema.normal-name",
                )
            ],
            processes=[
                Process(
                    id="emit-name",
                    name="Emit name",
                    steps=[Emit(interface="interface.normal-result")],
                )
            ],
        )

    scaling = Schema(
        id="scaling",
        template="<BALANCE> times <FACTOR>",
        where=[
            where(
                "BALANCE",
                Type(of="number"),
            ),
            where(
                "FACTOR",
                Type(of="number"),
                AtLeast(value="BALANCE"),
            ),
        ],
    )

    try:
        scaling.bind_value(
            "FACTOR",
            0,
        )

    except SchemaBindingError as error:
        if (
            error.failures[0].code
            != "unresolved_binding"
        ):
            raise RuntimeError(
                "expected unresolved_binding, "
                f"got {error}"
            ) from None

    else:
        raise RuntimeError(
            "bind_value accepted a "
            "placeholder-valued bound"
        )

    floor = Schema(
        id="floor",
        template="<VALUE>",
        where=[
            where(
                "VALUE",
                AtLeast(value=0),
            )
        ],
    )

    try:
        floor.bind_value(
            "VALUE",
            float("nan"),
        )

    except SchemaBindingError as error:
        if (
            error.failures[0].code
            != "invalid_json_value"
        ):
            raise RuntimeError(
                "expected invalid_json_value, "
                f"got {error}"
            ) from None

    else:
        raise RuntimeError(
            "bind_value accepted a "
            "non-JSON value"
        )

    mass = Schema(
        id="mass",
        template="<MASS>",
        where=[
            where(
                "MASS",
                Type(of="quantity"),
            )
        ],
    )
    mass.bind(
        {
            "MASS": {
                "value": "10",
                "unit": "kg",
            }
        }
    )

    try:
        mass.bind(
            {
                "MASS": Quantity(
                    value=Decimal("10"),
                    unit=Unit.KILOGRAM,
                )
            }
        )

    except SchemaBindingError as error:
        if (
            error.failures[0].code
            != "invalid_json_value"
        ):
            raise RuntimeError(
                "expected invalid_json_value, "
                f"got {error}"
            ) from None

    else:
        raise RuntimeError(
            "bind accepted a "
            "non-JSON quantity value"
        )

    _expect_rule(
        "trigger_contract_mismatch",
        trigger_seed_mismatch,
    )
    _expect_rule(
        "overlapping_trigger_guards",
        trigger_event_overlap,
    )
    _expect_rule(
        "process_output_binding_mismatch",
        output_missing,
    )
    _expect_rule(
        "call_contract_mismatch",
        call_mismatch,
    )
    _expect_rule(
        "act_schema_mismatch",
        act_mismatch,
    )
    _expect_rule(
        "invalid_schema_binding",
        typed_constant_invalid,
    )
    _expect_rule(
        "unknown_schema_placeholder",
        typed_constant_unknown,
    )
    _expect_rule(
        "incomplete_schema_binding",
        incomplete_binding,
    )
    _expect_rule(
        "invalid_act_instruction",
        reserved_instruction,
    )
    _expect_rule(
        "invalid_trigger_seed_value",
        trigger_binding_read,
    )
    _expect_rule(
        "trigger_source_not_receive",
        trigger_source_emit,
    )
    _expect_rule(
        "overlapping_trigger_guards",
        trigger_source_overlap,
    )
    _expect_rule(
        "source_trigger_seed",
        source_trigger_seed,
    )
    _expect_rule(
        "source_trigger_process_input",
        source_process_without_input,
    )
    _expect_rule(
        "source_trigger_schema_mismatch",
        source_schema_mismatch,
    )
    _expect_rule(
        "emit_target_not_emit",
        emit_through_receive,
    )
    _expect_rule(
        "inferred_emit_binding_mismatch",
        inferred_emit_missing,
    )


__all__ = [
    "validate_contract_rules",
]
