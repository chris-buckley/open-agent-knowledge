"""Runtime routing, process, loop, parallel, and transaction checks."""

from __future__ import annotations

import json

from pydantic import ValidationError

from build.checks.fixtures import contract_schemas, normalise_process
from oak.authoring import ACT
from oak.execute.executor import execute
from oak.execute.models import (
    Arrival,
    Emission,
    ExecutionError,
    ToolContract,
)
from oak.node.model import Node
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes.conditions import All, Compare
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.steps import (
    Act,
    Assert,
    Call,
    Emit,
    Foreach,
    Join,
    Par,
    Set,
    While,
)
from oak.node.parts.processes.values import (
    BindingValue,
    LiteralValue,
    StateValue,
    ValueBinding,
)
from oak.node.parts.schemas.constraints import Type
from oak.node.parts.schemas.model import Schema, where
from oak.node.parts.state import State
from oak.node.parts.triggers import Trigger
from oak.parse.document import parse
from oak.render import render


def validate_execution() -> None:
    """Verify process contracts, parallel work, loops, and emissions."""
    parallel = Node(
        state=[
            State(
                id="done",
                value=False,
            )
        ],
        triggers=[
            Trigger(
                id="run-trigger",
                event="Run parallel work.",
                process="process.run",
            )
        ],
        processes=[
            Process(
                id="run",
                name="Run tools",
                steps=[
                    Par(
                        steps=[
                            Act(
                                tool="tool-a",
                                instruction="Produce <A>.",
                                outputs=["A"],
                            ),
                            Act(
                                tool="tool-b",
                                instruction="Produce <B>.",
                                outputs=["B"],
                            ),
                        ]
                    ),
                    Join(),
                    Assert(
                        condition=All(
                            conditions=[
                                Compare(
                                    left=BindingValue(binding="A"),
                                    operator="not_equals",
                                    right=LiteralValue(value=""),
                                ),
                                Compare(
                                    left=BindingValue(binding="B"),
                                    operator="not_equals",
                                    right=LiteralValue(value=""),
                                ),
                            ]
                        )
                    ),
                    Foreach(
                        binding="ITEM",
                        value=LiteralValue(value=[1, 2]),
                        steps=[
                            Act(
                                instruction="Record <ITEM>.",
                                inputs=[
                                    ValueBinding(
                                        placeholder="ITEM",
                                        value=BindingValue(
                                            binding="ITEM"
                                        ),
                                    )
                                ],
                            )
                        ],
                    ),
                    Set(
                        state="state.done",
                        value=LiteralValue(value=True),
                    ),
                ],
            )
        ],
    )
    tools = {
        "tool-a": ToolContract(
            lambda _step, _values: {"A": "a"},
            frozenset(),
            frozenset({"A"}),
            True,
        ),
        "tool-b": ToolContract(
            lambda _step, _values: {"B": "b"},
            frozenset(),
            frozenset({"B"}),
            True,
        ),
    }
    parallel_execution = execute(
        parallel,
        Arrival(event="Run parallel work."),
        {"state.done": False},
        act=lambda _step, _values: {},
        tools=tools,
    )
    if parallel_execution.state != {"state.done": True}:
        raise RuntimeError(
            "parallel or foreach execution failed"
        )

    raw, normal = contract_schemas()
    contract = Node(
        schemas=[raw, normal],
        triggers=[
            Trigger(
                id="name",
                event="A name arrives.",
                source="interface.request",
                process="process.handle",
            )
        ],
        processes=[
            normalise_process(),
            Process(
                id="handle",
                name="Handle request",
                input="schema.raw-name",
                steps=[
                    Call(
                        process="process.normalise",
                        inputs=[
                            ValueBinding(
                                placeholder="RAW_NAME",
                                value=BindingValue(binding="RAW_NAME"),
                            )
                        ],
                        outputs=["NORMAL_NAME"],
                    ),
                    Emit(interface="interface.result"),
                ],
            ),
        ],
        interfaces=[
            Interface(
                id="request",
                flow="receives",
                schema="schema.raw-name",
            ),
            Interface(
                id="result",
                flow="emits",
                schema="schema.normal-name",
            ),
        ],
    )
    for grouping in ("xml", "markdown"):
        rendered = render(
            contract,
            grouping=grouping,
        )
        if render(
            parse(rendered),
            grouping=grouping,
        ) != rendered:
            raise RuntimeError(
                f"process contract {grouping} "
                "round trip changed text"
            )

    contract_execution = execute(
        contract,
        Arrival(
            interface="interface.request",
            values={"RAW_NAME": " ada "},
        ),
        {},
        act=lambda _step, values: {
            "NORMAL_NAME": values["RAW_NAME"].strip().title()
        },
    )
    if contract_execution.emissions != [
        Emission(
            interface="interface.result",
            values={"NORMAL_NAME": "Ada"},
        )
    ]:
        raise RuntimeError(
            "process contract execution failed"
        )

    try:
        execute(
            contract,
            Arrival(
                interface="interface.request",
                values={"RAW_NAME": "Ada"},
            ),
            {},
            act=lambda _step, _values: {
                "NORMAL_NAME": ""
            },
        )
    except ExecutionError as error:
        if error.code != "invalid_process_output":
            raise RuntimeError(
                "expected invalid_process_output, "
                f"got {error.code}"
            ) from None
    else:
        raise RuntimeError(
            "expected invalid_process_output"
        )


def validate_while() -> None:
    """Verify recursive WHILE rendering and bounded runtime behaviour."""
    recursive = Node(
        state=[
            State(
                id="status",
                value="pending",
            ),
            State(
                id="attempts",
                value=0,
            ),
        ],
        processes=[
            Process(
                id="wait-job",
                name="Wait job",
                steps=[
                    While(
                        condition=All(
                            conditions=[
                                Compare(
                                    left=StateValue(
                                        state="state.status"
                                    ),
                                    operator="not_equals",
                                    right=LiteralValue(
                                        value="complete"
                                    ),
                                ),
                                Compare(
                                    left=StateValue(
                                        state="state.attempts"
                                    ),
                                    operator="less_than",
                                    right=LiteralValue(value=3),
                                ),
                            ]
                        ),
                        limit=3,
                        steps=[
                            Set(
                                state="state.status",
                                value=LiteralValue(
                                    value="complete"
                                ),
                            )
                        ],
                    )
                ],
            )
        ],
    )
    rendered = render(recursive)
    if (
        "WHILE ALL(" not in rendered
        or ") LIMIT 3:" not in rendered
        or render(parse(rendered)) != rendered
    ):
        raise RuntimeError(
            "recursive WHILE render or parse failed"
        )

    linked = json.loads(
        render(
            recursive,
            render="json-ld",
            document=(
                "https://example.org/"
                "oak/while.oak.md"
            ),
            vocabulary="https://example.org/oak#",
        )
    )
    while_step = linked["processes"][0]["steps"][0]
    if not (
        while_step["@type"] == "oak:While"
        and while_step["limit"] == 3
        and while_step["condition"]["@type"] == "oak:All"
        and len(while_step["steps"]) == 1
    ):
        raise RuntimeError("WHILE JSON-LD is wrong")

    progress = Node(
        schemas=[
            Schema(
                id="progress-count",
                template="<NEXT>",
                where=[
                    where(
                        "NEXT",
                        Type(of="integer"),
                    )
                ],
            )
        ],
        state=[
            State(
                id="current-count",
                value=0,
            )
        ],
        triggers=[
            Trigger(
                id="count-requested",
                event="Count to two.",
                process="process.advance-count",
            )
        ],
        processes=[
            Process(
                id="advance-count",
                name="Advance count",
                steps=[
                    While(
                        condition=Compare(
                            left=StateValue(
                                state="state.current-count"
                            ),
                            operator="less_than",
                            right=LiteralValue(value=2),
                        ),
                        limit=3,
                        steps=[
                            ACT.tool(
                                "counter.next",
                                (
                                    "Increment <COUNT> "
                                    "and produce <NEXT>."
                                ),
                                inputs=[
                                    ValueBinding(
                                        placeholder="COUNT",
                                        value=StateValue(
                                            state=(
                                                "state."
                                                "current-count"
                                            )
                                        ),
                                    )
                                ],
                                outputs=["NEXT"],
                            ),
                            Set(
                                state="state.current-count",
                                value=BindingValue(
                                    binding="NEXT"
                                ),
                            ),
                            Emit(
                                interface=(
                                    "interface."
                                    "progress-count-output"
                                ),
                                bindings=[
                                    ValueBinding(
                                        placeholder="NEXT",
                                        value=BindingValue(
                                            binding="NEXT"
                                        ),
                                    )
                                ],
                            ),
                        ],
                    )
                ],
            )
        ],
        interfaces=[
            Interface(
                id="progress-count-output",
                flow="emits",
                schema="schema.progress-count",
            )
        ],
    )
    calls: list[int] = []

    def next_count(_step, values):
        calls.append(values["COUNT"])
        return {
            "NEXT": values["COUNT"] + 1
        }

    tool = ToolContract(
        next_count,
        frozenset({"COUNT"}),
        frozenset({"NEXT"}),
    )
    completed = execute(
        progress,
        Arrival(event="Count to two."),
        {"state.current-count": 0},
        tools={"counter.next": tool},
    )
    if not (
        calls == [0, 1]
        and completed.state["state.current-count"] == 2
        and completed.emissions
        == [
            Emission(
                interface=(
                    "interface."
                    "progress-count-output"
                ),
                values={"NEXT": 1},
            ),
            Emission(
                interface=(
                    "interface."
                    "progress-count-output"
                ),
                values={"NEXT": 2},
            ),
        ]
    ):
        raise RuntimeError(
            "WHILE state, emissions, or "
            "fresh iteration scope is wrong"
        )

    skipped = execute(
        progress,
        Arrival(event="Count to two."),
        {"state.current-count": 2},
        tools={"counter.next": tool},
    )
    if calls != [0, 1] or skipped.emissions:
        raise RuntimeError(
            "WHILE did not test its condition "
            "before the first iteration"
        )

    limited = Node(
        state=[
            State(
                id="status",
                value="pending",
            )
        ],
        triggers=[
            Trigger(
                id="poll-requested",
                event="Poll without progress.",
                process="process.poll-job",
            )
        ],
        processes=[
            Process(
                id="poll-job",
                name="Poll job",
                steps=[
                    While(
                        condition=Compare(
                            left=StateValue(
                                state="state.status"
                            ),
                            operator="not_equals",
                            right=LiteralValue(
                                value="complete"
                            ),
                        ),
                        limit=2,
                        steps=[
                            ACT(
                                "Wait for the next status."
                            )
                        ],
                    )
                ],
            )
        ],
    )
    try:
        execute(
            limited,
            Arrival(
                event="Poll without progress."
            ),
            {"state.status": "pending"},
            act=lambda _step, _values: {},
        )
    except ExecutionError as error:
        if error.code != "while_limit_reached":
            raise RuntimeError(
                "expected while_limit_reached, "
                f"got {error.code}"
            ) from None
    else:
        raise RuntimeError(
            "expected while_limit_reached"
        )


def validate_source_routing() -> None:
    """Verify exact event and source trigger selection."""
    raw, _normal = contract_schemas()
    routed = Node(
        schemas=[raw],
        state=[
            State(
                id="route",
                value="",
            )
        ],
        triggers=[
            Trigger(
                id="event-routed",
                event="A name arrives.",
                process="process.mark-event",
            ),
            Trigger(
                id="source-routed",
                event="A name arrives by wire.",
                source="interface.request",
                process="process.mark-source",
            ),
        ],
        processes=[
            Process(
                id="mark-event",
                name="Mark event",
                steps=[
                    Set(
                        state="state.route",
                        value=LiteralValue(
                            value="event"
                        ),
                    )
                ],
            ),
            Process(
                id="mark-source",
                name="Mark source",
                input="schema.raw-name",
                steps=[
                    Set(
                        state="state.route",
                        value=LiteralValue(
                            value="source"
                        ),
                    )
                ],
            ),
        ],
        interfaces=[
            Interface(
                id="request",
                flow="receives",
                schema="schema.raw-name",
            )
        ],
    )
    by_event = execute(
        routed,
        Arrival(event="A name arrives."),
        {"state.route": ""},
    )
    by_source = execute(
        routed,
        Arrival(
            interface="interface.request",
            values={"RAW_NAME": "Ada"},
        ),
        {"state.route": ""},
    )
    if (
        by_event.state["state.route"] != "event"
        or by_source.state["state.route"] != "source"
    ):
        raise RuntimeError(
            "arrival routing selected the wrong trigger"
        )

    idle = execute(
        routed,
        Arrival(event="A name arrives by wire."),
        {"state.route": ""},
    )
    if idle.state["state.route"] != "":
        raise RuntimeError(
            "an event arrival fired a source-backed trigger"
        )

    try:
        execute(
            routed,
            Arrival(interface="interface.request"),
            {"state.route": ""},
        )
    except ExecutionError as error:
        if error.code != "invalid_interface_binding":
            raise RuntimeError(
                "expected invalid_interface_binding, "
                f"got {error.code}"
            ) from None
    else:
        raise RuntimeError(
            "a source arrival without its payload executed"
        )

    for values in (
        {},
        {
            "event": "A name arrives.",
            "interface": "interface.request",
        },
    ):
        try:
            Arrival(**values)
        except ValidationError as error:
            if "invalid_arrival_selector" not in {
                str(item["type"])
                for item in error.errors()
            }:
                raise RuntimeError(
                    "expected invalid_arrival_selector, "
                    f"got {error}"
                ) from None
        else:
            raise RuntimeError(
                "an arrival accepted an invalid selector pair"
            )

    try:
        Arrival(
            event="A name arrives.",
            values={"RAW_NAME": "Ada"},
        )
    except ValidationError as error:
        if "event_arrival_values" not in {
            str(item["type"]) for item in error.errors()
        }:
            raise RuntimeError(
                "expected event_arrival_values"
            ) from None
    else:
        raise RuntimeError("an event arrival accepted values")


__all__ = [
    "validate_execution",
    "validate_source_routing",
    "validate_while",
]
