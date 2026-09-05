"""Interface flow surface, contract, and runtime verification."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import get_args

from pydantic import TypeAdapter, ValidationError

from oak.execute import Arrival, Emission, ExecutionError, ToolContract, execute
from oak.node.interpretation import (
    BUILT_IN_INSTRUCTIONS,
    INFERRED_EMIT_INSTRUCTION,
    INTERFACE_DESCRIPTION_INSTRUCTION,
    TRIGGER_SOURCE_INSTRUCTION,
)
from oak.node.model import Node
from oak.node.parts.interfaces import (
    INTERFACE_FLOWS,
    INTERFACE_FLOW_BY_KEYWORD,
    INTERFACE_FLOW_BY_NAME,
    Interface,
    InterfaceFlow,
)
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.conditions import Compare
from oak.node.parts.processes.steps import (
    Act,
    Assert,
    Call,
    Emit,
    Foreach,
    If,
    Join,
    Par,
    Set,
    While,
)
from oak.node.parts.processes.values import (
    BindingValue,
    LiteralValue,
    StateValue,
    Value,
    ValueBinding,
)
from oak.node.parts.schemas.constraints import Type
from oak.node.parts.schemas.model import Schema, where
from oak.node.parts.state import State
from oak.node.parts.triggers import Trigger
from oak.parse import OakParseError, parse
from oak.parse.fragments import parse_fragment
from oak.parse.values import parse_value
from oak.render import render
from oak.render.oak.interfaces import interface_text
from oak.resolve import ResolutionError, resolve
from oak.surface.registry import surfaces_for_model
from oak.vocabulary.text.value_reference import ValueReference


def _schema(identifier: str, placeholder: str) -> Schema:
    return Schema(
        id=identifier,
        template=f"<{placeholder}>",
        where=[where(placeholder, Type(of="string"))],
    )


def _expect_validation(code: str, author: Callable[[], object]) -> None:
    try:
        author()
    except ValidationError as error:
        codes = {str(detail["type"]) for detail in error.errors()}
        if code not in codes:
            raise RuntimeError(f"expected {code}, got {sorted(codes)}") from None
        return
    raise RuntimeError(f"expected {code}")


def _expect_parse(code: str | None, text: str) -> None:
    try:
        parse(text)
    except OakParseError as error:
        if code is not None and code not in {failure.code for failure in error.failures}:
            raise RuntimeError(f"expected {code}, got {error}") from None
        return
    raise RuntimeError("invalid interface text parsed successfully")


def _contract_node(*, description: bool = True) -> Node:
    request = _schema("request-shape", "REQUEST")
    result = _schema("result-shape", "RESULT")
    receive = Interface(
        id="request-input",
        flow="receives",
        schema="schema.request-shape",
    )
    publish = Interface(
        id="result-output",
        flow="emits",
        schema="schema.result-shape",
        description=(
            "Returned only to the coordinator."
            if description
            else None
        ),
    )
    process = Process(
        id="answer-request",
        name="Answer request",
        input="schema.request-shape",
        output="schema.result-shape",
        steps=[
            Act(
                instruction="Turn <REQUEST> into <RESULT>.",
                inputs=[
                    ValueBinding(
                        placeholder="REQUEST",
                        value=BindingValue(binding="REQUEST"),
                    )
                ],
                outputs=["RESULT"],
            ),
            Emit(interface="interface.result-output"),
        ],
    )
    return Node(
        schemas=[request, result],
        triggers=[
            Trigger(
                id="request-arrived",
                event="A request arrives.",
                source="interface.request-input",
                process="process.answer-request",
            )
        ],
        processes=[process],
        interfaces=[receive, publish],
    )


def validate_interface_registry() -> None:
    """Verify one closed registry drives models, surfaces, text, and instructions."""
    model_flows = tuple(get_args(InterfaceFlow))
    registry_flows = tuple(item.flow for item in INTERFACE_FLOWS)
    registry_keywords = tuple(item.keyword for item in INTERFACE_FLOWS)
    surfaces = surfaces_for_model(Interface)
    surface_flows = tuple(surface.when[0][1] for surface in surfaces)

    if not (
        model_flows == registry_flows == surface_flows == ("receives", "emits")
        and registry_keywords == ("RECEIVES", "EMITS")
        and tuple(INTERFACE_FLOW_BY_NAME) == registry_flows
        and tuple(INTERFACE_FLOW_BY_KEYWORD) == registry_keywords
        and len(INTERFACE_FLOWS) == len(INTERFACE_FLOW_BY_NAME)
        and len(INTERFACE_FLOWS) == len(INTERFACE_FLOW_BY_KEYWORD)
    ):
        raise RuntimeError("interface flow registries differ")

    for definition, surface in zip(INTERFACE_FLOWS, surfaces, strict=True):
        example = Interface(
            id="boundary",
            flow=definition.flow,
            schema="schema.shape",
        )
        if (
            definition.keyword not in surface.shape
            or interface_text(example)
            != f"boundary {definition.keyword} schema.shape"
            or definition.instruction not in BUILT_IN_INSTRUCTIONS
        ):
            raise RuntimeError(
                f"interface flow {definition.flow} is not consistently registered"
            )


def validate_interface_surface() -> None:
    """Verify terse interface rendering, descriptions, and both groupings."""
    node = _contract_node()
    xml = render(node, grouping="xml")
    markdown = render(node, grouping="markdown")
    expected = (
        "request-input RECEIVES schema.request-shape\n"
        "result-output EMITS schema.result-shape: "
        '"Returned only to the coordinator."'
    )
    xml_body = xml.split("<interfaces>\n", 1)[1].split("\n</interfaces>", 1)[0]
    markdown_body = markdown.split("~~~~interfaces\n", 1)[1].split("\n~~~~", 1)[0]

    if xml_body != expected or markdown_body != expected or xml_body != markdown_body:
        raise RuntimeError("interface grouping bodies differ")
    if "<interface " in xml or "~~~interface;" in markdown or "\n\n" in xml_body:
        raise RuntimeError("interface entry wrappers or blank separators remain")
    if parse(xml) != node or parse(markdown) != node:
        raise RuntimeError("interface grouping round trip changed the node")

    without_description = _contract_node(description=False)
    text = render(without_description)
    if "result-output EMITS schema.result-shape:" in text:
        raise RuntimeError("absent interface description rendered a colon")

    failures = (
        (
            "interface_separator",
            "<interfaces>\na RECEIVES schema.a\n\nb EMITS schema.b\n</interfaces>",
        ),
        ("interface_flow", "<interfaces>\na SENDS schema.a\n</interfaces>"),
        (None, "<interfaces>\na RECEIVES schema.\n</interfaces>"),
        (
            "interface_description",
            "<interfaces>\na RECEIVES schema.a: not-json\n</interfaces>",
        ),
        (
            "interface_schema",
            "<interfaces>\na RECEIVES schema.a extra\n</interfaces>",
        ),
        (
            "interface_flow",
            '<interfaces>\n<interface id="a" direction="in" schema="schema.a">\n</interface>\n</interfaces>',
        ),
        (
            None,
            '~~~~interfaces\n~~~interface;id="a";direction="in";schema="schema.a"\n~~~\n~~~~',
        ),
    )
    for code, source in failures:
        _expect_parse(code, source)

    _expect_validation(
        "missing",
        lambda: Interface.model_validate(
            {
                "part": "interfaces",
                "id": "legacy",
                "direction": "in",
                "schema": "schema.shape",
            }
        ),
    )
    for legacy_flow in ("in", "out", "inout"):
        _expect_validation(
            "literal_error",
            lambda legacy_flow=legacy_flow: Interface(
                id="legacy",
                flow=legacy_flow,
                schema="schema.shape",
            ),
        )


def validate_interface_instructions() -> None:
    """Verify each feature-selected interface instruction and stripping."""
    receive_line = INTERFACE_FLOW_BY_NAME["receives"].instruction
    emit_line = INTERFACE_FLOW_BY_NAME["emits"].instruction
    feature_lines = (
        receive_line,
        TRIGGER_SOURCE_INSTRUCTION,
        emit_line,
        INFERRED_EMIT_INSTRUCTION,
        INTERFACE_DESCRIPTION_INSTRUCTION,
    )

    request = _schema("request-shape", "REQUEST")
    result = _schema("result-shape", "RESULT")
    receive = Interface(
        id="request-input",
        flow="receives",
        schema="schema.request-shape",
    )
    emit = Interface(
        id="result-output",
        flow="emits",
        schema="schema.result-shape",
    )
    source_process = Process(
        id="read-request",
        name="Read request",
        input="schema.request-shape",
        steps=[
            Act(
                instruction="Read <REQUEST>.",
                inputs=[
                    ValueBinding(
                        placeholder="REQUEST",
                        value=BindingValue(binding="REQUEST"),
                    )
                ],
            )
        ],
    )
    explicit_process = Process(
        id="publish-result",
        name="Publish result",
        steps=[
            Act(instruction="Produce <RESULT>.", outputs=["RESULT"]),
            Emit(
                interface="interface.result-output",
                bindings=[
                    ValueBinding(
                        placeholder="RESULT",
                        value=BindingValue(binding="RESULT"),
                    )
                ],
            ),
        ],
    )
    inferred_process = explicit_process.model_copy(
        update={
            "id": "infer-result",
            "name": "Infer result",
            "steps": [
                explicit_process.steps[0],
                Emit(interface="interface.result-output"),
            ],
        }
    )

    cases = (
        (Node(), (0, 0, 0, 0, 0)),
        (
            Node(schemas=[request], interfaces=[receive]),
            (1, 0, 0, 0, 0),
        ),
        (
            Node(
                schemas=[request],
                triggers=[
                    Trigger(
                        id="request-arrived",
                        event="A request arrives.",
                        source="interface.request-input",
                        process="process.read-request",
                    )
                ],
                processes=[source_process],
                interfaces=[receive],
            ),
            (1, 1, 0, 0, 0),
        ),
        (
            Node(
                schemas=[result],
                processes=[explicit_process],
                interfaces=[emit],
            ),
            (0, 0, 1, 0, 0),
        ),
        (
            Node(
                schemas=[result],
                processes=[inferred_process],
                interfaces=[emit],
            ),
            (0, 0, 1, 1, 0),
        ),
        (
            Node(
                schemas=[request],
                interfaces=[
                    receive.model_copy(
                        update={"description": "Accepted from the coordinator."}
                    )
                ],
            ),
            (1, 0, 0, 0, 1),
        ),
        (_contract_node(), (1, 1, 1, 1, 1)),
    )
    for node, counts in cases:
        lines = render(node).splitlines()
        actual = tuple(lines.count(line) for line in feature_lines)
        if actual != counts:
            raise RuntimeError(
                f"generated interface instruction counts differ: {actual} != {counts}"
            )

    authored = _contract_node().model_copy(update={"instructions": []})
    if parse(render(authored)).instructions:
        raise RuntimeError("generated instructions became authored instructions")


def validate_interface_execution() -> None:
    """Verify event seeds, receive handoff, inferred emits, and projection."""
    source = _contract_node()
    seen: list[dict[str, object]] = []

    def answer(_step: Act, values: dict[str, object]) -> dict[str, object]:
        seen.append(dict(values))
        return {"RESULT": str(values["REQUEST"]).upper()}

    result = execute(
        source,
        Arrival(
            interface="interface.request-input",
            values={"REQUEST": "hello"},
        ),
        {},
        act=answer,
    )
    if seen != [{"REQUEST": "hello"}] or result.emissions != [
        Emission(
            interface="interface.result-output",
            values={"RESULT": "HELLO"},
        )
    ]:
        raise RuntimeError("receive payload handoff or inferred emission failed")

    request = _schema("event-request", "REQUEST")
    event_node = Node(
        schemas=[request],
        triggers=[
            Trigger(
                id="event-arrived",
                event="Run the event.",
                process="process.read-event",
                seed=[
                    ValueBinding(
                        placeholder="REQUEST",
                        value=LiteralValue(value="seeded"),
                    )
                ],
            )
        ],
        processes=[
            Process(
                id="read-event",
                name="Read event",
                input="schema.event-request",
                steps=[
                    Act(
                        instruction="Read <REQUEST>.",
                        inputs=[
                            ValueBinding(
                                placeholder="REQUEST",
                                value=BindingValue(binding="REQUEST"),
                            )
                        ],
                    )
                ],
            )
        ],
    )
    event_seen: list[dict[str, object]] = []
    execute(
        event_node,
        Arrival(event="Run the event."),
        {},
        act=lambda _step, values: event_seen.append(dict(values)) or {},
    )
    if event_seen != [{"REQUEST": "seeded"}]:
        raise RuntimeError("event-backed trigger seed changed")

    projected = Node(
        schemas=[_schema("published-result", "RESULT")],
        triggers=[
            Trigger(
                id="publish-requested",
                event="Publish a result.",
                process="process.publish-result",
            )
        ],
        processes=[
            Process(
                id="publish-result",
                name="Publish result",
                steps=[
                    Act(
                        instruction="Produce <FINAL_RESULT>.",
                        outputs=["FINAL_RESULT"],
                    ),
                    Emit(
                        interface="interface.published-result-output",
                        bindings=[
                            ValueBinding(
                                placeholder="RESULT",
                                value=BindingValue(binding="FINAL_RESULT"),
                            )
                        ],
                    ),
                ],
            )
        ],
        interfaces=[
            Interface(
                id="published-result-output",
                flow="emits",
                schema="schema.published-result",
            )
        ],
    )
    projected_result = execute(
        projected,
        Arrival(event="Publish a result."),
        {},
        act=lambda _step, _values: {"FINAL_RESULT": "done"},
    )
    if projected_result.emissions[0].values != {"RESULT": "done"}:
        raise RuntimeError("explicit emit projection failed")

    try:
        Arrival(event="Run.", values={"X": 1})
    except ValidationError as error:
        if "event_arrival_values" not in {str(item["type"]) for item in error.errors()}:
            raise RuntimeError("event values used the wrong error") from None
    else:
        raise RuntimeError("event arrival accepted values")

    for invalid in (
        {},
        {"event": "Run.", "interface": "interface.input"},
        {"source": "interface.input", "interfaces": {}},
    ):
        try:
            Arrival.model_validate(invalid)
        except ValidationError:
            pass
        else:
            raise RuntimeError("invalid or legacy arrival shape was accepted")

    try:
        execute(
            source,
            Arrival(interface="interface.request-input", values={}),
            {},
            act=answer,
        )
    except ExecutionError as error:
        if error.code != "invalid_interface_binding":
            raise RuntimeError("incomplete receive used the wrong error") from None
    else:
        raise RuntimeError("incomplete receive instance was accepted")


def validate_interface_resolution() -> None:
    """Verify relative schema identity and exact source contracts."""
    shared = Node(
        schemas=[
            _schema("shared-request", "REQUEST"),
            _schema("shared-result", "RESULT"),
        ]
    )
    root = Node(
        triggers=[
            Trigger(
                id="request-arrived",
                event="A request arrives.",
                source="interface.request-input",
                process="process.answer-request",
            )
        ],
        processes=[
            Process(
                id="answer-request",
                name="Answer request",
                input="shared.oak.md#schema.shared-request",
                steps=[
                    Act(
                        instruction="Read <REQUEST> and produce <RESULT>.",
                        inputs=[
                            ValueBinding(
                                placeholder="REQUEST",
                                value=BindingValue(binding="REQUEST"),
                            )
                        ],
                        outputs=["RESULT"],
                    ),
                    Emit(interface="interface.result-output"),
                ],
            )
        ],
        interfaces=[
            Interface(
                id="request-input",
                flow="receives",
                schema="shared.oak.md#schema.shared-request",
            ),
            Interface(
                id="result-output",
                flow="emits",
                schema="shared.oak.md#schema.shared-result",
            ),
        ],
    )
    load = lambda path: shared if path == "shared.oak.md" else None
    resolve(root, source="root.oak.md", load=load)

    different = root.model_copy(
        update={
            "processes": [
                Process(
                    id="answer-request",
                    name="Answer request",
                    input="shared.oak.md#schema.shared-result",
                    steps=[
                        Act(
                            instruction="Read <RESULT>.",
                            inputs=[
                                ValueBinding(
                                    placeholder="RESULT",
                                    value=BindingValue(binding="RESULT"),
                                )
                            ],
                        )
                    ],
                )
            ]
        }
    )
    try:
        resolve(different, source="root.oak.md", load=load)
    except ResolutionError as error:
        if error.code != "source_trigger_schema_mismatch":
            raise RuntimeError("resolved source mismatch used the wrong error") from None
    else:
        raise RuntimeError("resolved source schema mismatch was accepted")

    left = Node(schemas=[_schema("shared", "REQUEST")])
    right = Node(
        schemas=[_schema("shared", "REQUEST")],
        processes=[
            Process(
                id="read-request",
                name="Read request",
                input="schema.shared",
                steps=[
                    Act(
                        instruction="Read <REQUEST>.",
                        inputs=[
                            ValueBinding(
                                placeholder="REQUEST",
                                value=BindingValue(binding="REQUEST"),
                            )
                        ],
                    )
                ],
            )
        ],
    )
    cross_document = Node(
        triggers=[
            Trigger(
                id="request-arrived",
                event="A request arrives.",
                source="interface.request-input",
                process="right.oak.md#process.read-request",
            )
        ],
        interfaces=[
            Interface(
                id="request-input",
                flow="receives",
                schema="left.oak.md#schema.shared",
            )
        ],
    )
    try:
        resolve(
            cross_document,
            source="root.oak.md",
            load=lambda path: {
                "left.oak.md": left,
                "right.oak.md": right,
            }.get(path),
        )
    except ResolutionError as error:
        if error.code != "source_trigger_schema_mismatch":
            raise RuntimeError(
                "cross-document source mismatch used the wrong error"
            ) from None
    else:
        raise RuntimeError(
            "equal schema ids in different documents were treated as identical"
        )


def validate_interface_rejections() -> None:
    """Verify obsolete values and unsafe source or emit contracts are rejected."""
    request = _schema("request-shape", "REQUEST")
    result = _schema("result-shape", "RESULT")

    _expect_validation(
        "source_trigger_seed",
        lambda: Trigger(
            id="invalid",
            event="A request arrives.",
            source="interface.request-input",
            process="process.answer-request",
            seed=[
                ValueBinding(
                    placeholder="REQUEST",
                    value=LiteralValue(value="x"),
                )
            ],
        ),
    )

    def source_node(flow: str, process_input: str | None) -> Node:
        return Node(
            schemas=[request, result],
            triggers=[
                Trigger(
                    id="request-arrived",
                    event="A request arrives.",
                    source="interface.request-input",
                    process="process.answer-request",
                )
            ],
            processes=[
                Process(
                    id="answer-request",
                    name="Answer request",
                    input=process_input,
                    steps=[Act(instruction="Answer the request.")],
                )
            ],
            interfaces=[
                Interface(
                    id="request-input",
                    flow=flow,
                    schema="schema.request-shape",
                )
            ],
        )

    _expect_validation(
        "trigger_source_not_receive",
        lambda: source_node("emits", "schema.request-shape"),
    )
    _expect_validation(
        "source_trigger_process_input",
        lambda: source_node("receives", None),
    )
    _expect_validation(
        "source_trigger_schema_mismatch",
        lambda: source_node("receives", "schema.result-shape"),
    )

    _expect_validation(
        "emit_target_not_emit",
        lambda: Node(
            schemas=[request],
            processes=[
                Process(
                    id="emit-request",
                    name="Emit request",
                    input="schema.request-shape",
                    steps=[Emit(interface="interface.request-input")],
                )
            ],
            interfaces=[
                Interface(
                    id="request-input",
                    flow="receives",
                    schema="schema.request-shape",
                )
            ],
        ),
    )
    _expect_validation(
        "inferred_emit_binding_mismatch",
        lambda: Node(
            schemas=[result],
            processes=[
                Process(
                    id="emit-result",
                    name="Emit result",
                    steps=[Emit(interface="interface.result-output")],
                )
            ],
            interfaces=[
                Interface(
                    id="result-output",
                    flow="emits",
                    schema="schema.result-shape",
                )
            ],
        ),
    )

    def explicit(bindings: list[ValueBinding]) -> Node:
        return Node(
            schemas=[result],
            processes=[
                Process(
                    id="emit-result",
                    name="Emit result",
                    steps=[
                        Act(
                            instruction="Produce <RESULT> and <EXTRA>.",
                            outputs=["RESULT", "EXTRA"],
                        ),
                        Emit(
                            interface="interface.result-output",
                            bindings=bindings,
                        ),
                    ],
                )
            ],
            interfaces=[
                Interface(
                    id="result-output",
                    flow="emits",
                    schema="schema.result-shape",
                )
            ],
        )

    pair = Schema(
        id="pair-result",
        template="<FIRST> <SECOND>",
        where=[
            where("FIRST", Type(of="string")),
            where("SECOND", Type(of="string")),
        ],
    )
    _expect_validation(
        "emit_schema_binding_mismatch",
        lambda: Node(
            schemas=[pair],
            processes=[
                Process(
                    id="emit-pair",
                    name="Emit pair",
                    steps=[
                        Act(
                            instruction="Produce <FIRST>.",
                            outputs=["FIRST"],
                        ),
                        Emit(
                            interface="interface.pair-output",
                            bindings=[
                                ValueBinding(
                                    placeholder="FIRST",
                                    value=BindingValue(binding="FIRST"),
                                )
                            ],
                        ),
                    ],
                )
            ],
            interfaces=[
                Interface(
                    id="pair-output",
                    flow="emits",
                    schema="schema.pair-result",
                )
            ],
        ),
    )
    _expect_validation(
        "emit_schema_binding_mismatch",
        lambda: explicit(
            [
                ValueBinding(
                    placeholder="RESULT",
                    value=BindingValue(binding="RESULT"),
                ),
                ValueBinding(
                    placeholder="EXTRA",
                    value=BindingValue(binding="EXTRA"),
                ),
            ]
        ),
    )
    _expect_validation(
        "duplicate_emit_placeholder",
        lambda: Emit(
            interface="interface.result-output",
            bindings=[
                ValueBinding(
                    placeholder="RESULT",
                    value=LiteralValue(value="one"),
                ),
                ValueBinding(
                    placeholder="RESULT",
                    value=LiteralValue(value="two"),
                ),
            ],
        ),
    )
    _expect_parse(
        "emit_empty_bindings",
        '<processes>\n<process id="emit-result" name="Emit result">\nEMIT interface.result-output ()\n</process>\n</processes>',
    )

    value_adapter = TypeAdapter(Value)
    reference_adapter = TypeAdapter(ValueReference)
    for author in (
        lambda: value_adapter.validate_python(
            {
                "source": "interface",
                "interface": "interface.request-input",
                "placeholder": "REQUEST",
            }
        ),
        lambda: reference_adapter.validate_python(
            "$interface.request-input.REQUEST"
        ),
        lambda: parse_value(
            "$interface.request-input.REQUEST",
            "value",
            1,
        ),
    ):
        try:
            author()
        except (ValidationError, ValueError):
            pass
        else:
            raise RuntimeError("ambient interface value was accepted")

    fragments = (
        (Act, "ACT Read <X>. (X=$interface.i.X)"),
        (Set, "SET state.x = $interface.i.X"),
        (Emit, "EMIT interface.o (X=$interface.i.X)"),
        (Call, "CALL process.p (X=$interface.i.X)"),
        (Assert, "ASSERT $interface.i.X equals 1"),
        (Foreach, 'FOREACH ITEM IN $interface.i.X:\n  FAIL "stop"'),
        (If, 'IF $interface.i.X equals 1:\n  FAIL "stop"'),
        (While, 'WHILE $interface.i.X equals 1 LIMIT 1:\n  FAIL "stop"'),
        (
            Par,
            'PAR:\n  ACT TOOL "tool": Read <X>. (X=$interface.i.X)',
        ),
    )
    for model, text in fragments:
        try:
            parse_fragment(model, text)
        except (ValidationError, ValueError):
            pass
        else:
            raise RuntimeError(f"{model.__name__} accepted an interface value")


def validate_interface_scope() -> None:
    """Verify inferred emit scope in branches, loops, and parallel joins."""
    result_schema = _schema("scope-result", "RESULT")
    result_interface = Interface(
        id="scope-result-output",
        flow="emits",
        schema="schema.scope-result",
    )

    branch = Node(
        schemas=[result_schema],
        state=[State(id="branch-enabled", value=True)],
        triggers=[
            Trigger(
                id="branch-requested",
                event="Run the branch.",
                process="process.run-branch",
            )
        ],
        processes=[
            Process(
                id="run-branch",
                name="Run branch",
                steps=[
                    If(
                        condition=Compare(
                            left=StateValue(state="state.branch-enabled"),
                            operator="equals",
                            right=LiteralValue(value=True),
                        ),
                        then=[
                            Act(
                                instruction="Produce <RESULT>.",
                                outputs=["RESULT"],
                            ),
                            Emit(interface="interface.scope-result-output"),
                        ],
                    )
                ],
            )
        ],
        interfaces=[result_interface],
    )
    branch_result = execute(
        branch,
        Arrival(event="Run the branch."),
        {"state.branch-enabled": True},
        act=lambda _step, _values: {"RESULT": "branch"},
    )
    if branch_result.emissions[0].values != {"RESULT": "branch"}:
        raise RuntimeError("branch inferred emit scope failed")

    item_schema = _schema("scope-item", "ITEM")
    loop = Node(
        schemas=[item_schema],
        triggers=[
            Trigger(
                id="loop-requested",
                event="Run the loop.",
                process="process.run-loop",
            )
        ],
        processes=[
            Process(
                id="run-loop",
                name="Run loop",
                steps=[
                    Foreach(
                        binding="ITEM",
                        value=LiteralValue(value=["a", "b"]),
                        steps=[Emit(interface="interface.scope-item-output")],
                    )
                ],
            )
        ],
        interfaces=[
            Interface(
                id="scope-item-output",
                flow="emits",
                schema="schema.scope-item",
            )
        ],
    )
    loop_result = execute(loop, Arrival(event="Run the loop."), {})
    if [item.values for item in loop_result.emissions] != [
        {"ITEM": "a"},
        {"ITEM": "b"},
    ]:
        raise RuntimeError("FOREACH inferred emit scope failed")

    bounded = Node(
        schemas=[result_schema],
        state=[State(id="iteration", value=0)],
        triggers=[
            Trigger(
                id="while-requested",
                event="Run the while.",
                process="process.run-while",
            )
        ],
        processes=[
            Process(
                id="run-while",
                name="Run while",
                steps=[
                    Act(
                        instruction="Produce <RESULT>.",
                        outputs=["RESULT"],
                    ),
                    While(
                        condition=Compare(
                            left=StateValue(state="state.iteration"),
                            operator="less_than",
                            right=LiteralValue(value=1),
                        ),
                        limit=1,
                        steps=[
                            Emit(interface="interface.scope-result-output"),
                            Set(
                                state="state.iteration",
                                value=LiteralValue(value=1),
                            ),
                        ],
                    ),
                ],
            )
        ],
        interfaces=[result_interface],
    )
    while_result = execute(
        bounded,
        Arrival(event="Run the while."),
        {"state.iteration": 0},
        act=lambda _step, _values: {"RESULT": "while"},
    )
    if while_result.emissions[0].values != {"RESULT": "while"}:
        raise RuntimeError("WHILE inferred emit scope failed")

    parallel = Node(
        schemas=[result_schema],
        triggers=[
            Trigger(
                id="parallel-requested",
                event="Run parallel work.",
                process="process.run-parallel",
            )
        ],
        processes=[
            Process(
                id="run-parallel",
                name="Run parallel",
                steps=[
                    Par(
                        steps=[
                            Act(
                                tool="result.tool",
                                instruction="Produce <RESULT>.",
                                outputs=["RESULT"],
                            )
                        ]
                    ),
                    Join(),
                    Emit(interface="interface.scope-result-output"),
                ],
            )
        ],
        interfaces=[result_interface],
    )
    parallel_result = execute(
        parallel,
        Arrival(event="Run parallel work."),
        {},
        tools={
            "result.tool": ToolContract(
                lambda _step, _values: {"RESULT": "parallel"},
                frozenset(),
                frozenset({"RESULT"}),
                True,
            )
        },
    )
    if parallel_result.emissions[0].values != {"RESULT": "parallel"}:
        raise RuntimeError("PAR/JOIN inferred emit scope failed")


def validate_interface_json_ld() -> None:
    """Verify interface flow and inferred emit JSON-LD projections."""
    linked = json.loads(
        render(
            _contract_node(),
            render="json-ld",
            document="https://example.org/interface.oak.md",
            vocabulary="https://example.org/oak#",
        )
    )
    interfaces = linked["interfaces"]
    if [item["flow"] for item in interfaces] != ["receives", "emits"]:
        raise RuntimeError("JSON-LD interface flows are wrong")
    if "direction" in linked.get("@context", {}) or "flow" not in linked["@context"]:
        raise RuntimeError("JSON-LD context retains interface direction")
    emit = linked["processes"][0]["steps"][-1]
    if "bindings" in emit:
        raise RuntimeError("inferred emit JSON-LD contains empty bindings")


def validate_interfaces() -> None:
    """Run all interface-flow product checks."""
    validate_interface_registry()
    validate_interface_surface()
    validate_interface_instructions()
    validate_interface_execution()
    validate_interface_resolution()
    validate_interface_rejections()
    validate_interface_scope()
    validate_interface_json_ld()


__all__ = ["validate_interfaces"]
