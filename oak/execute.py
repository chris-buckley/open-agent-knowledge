"""Transactional trigger selection and process execution across one resolved graph."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from concurrent.futures import Future, ThreadPoolExecutor
from copy import deepcopy
from dataclasses import dataclass
from typing import Annotated

from pydantic import AfterValidator, ConfigDict, Field, JsonValue, TypeAdapter, ValidationError

from oak.base import OakModel
from oak.node import Node
from oak.node.graph import validate_tools
from oak.node.parts import (
    Act,
    All,
    Any,
    Assert,
    BindingValue,
    Call,
    Compare,
    Condition,
    Constant,
    ConstantValue,
    Emit,
    Fail,
    Foreach,
    If,
    Interface,
    InterfaceValue,
    Join,
    LiteralValue,
    Not,
    Par,
    Process,
    Schema,
    SchemaBindingError,
    Set,
    State,
    StateValue,
    Step,
    Trigger,
    Value,
    While,
)
from oak.resolve import DocumentLoader, ResolvedGraph, resolve
from oak.vocabulary import NonBlankLine, Placeholder, TargetPath
from oak.vocabulary.text.target_path import target_id, typed_target

_STRICT = ConfigDict(strict=True, regex_engine="rust-regex")
_STATE_ADAPTER = TypeAdapter(dict[TargetPath, JsonValue], config=_STRICT)
_BINDING_ADAPTER = TypeAdapter(dict[Placeholder, JsonValue], config=_STRICT)
_JSON_ADAPTER = TypeAdapter(JsonValue, config=_STRICT)
InterfaceArrivalTarget = Annotated[TargetPath, AfterValidator(lambda value: typed_target(value, "interface"))]

ActHandler = Callable[[Act, Mapping[str, JsonValue]], Mapping[str, JsonValue]]
ToolHandler = Callable[[Act, Mapping[str, JsonValue]], Mapping[str, JsonValue]]


@dataclass(frozen=True, slots=True)
class ToolContract:
    """One exact host tool contract and handler."""

    handler: ToolHandler
    inputs: frozenset[str]
    outputs: frozenset[str]
    parallel: bool = False
    input: str | None = None
    output: str | None = None


class Arrival(OakModel):
    """One trigger arrival and its active input values."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "when": "A command line arrives.",
                    "interfaces": {
                        "interface.stdin": {
                            "COMMAND": "pwd",
                        }
                    },
                }
            ]
        }
    )

    when: NonBlankLine = Field(
        description="The arrival reason matched against trigger WHEN text.",
        examples=["A command line arrives."],
    )
    interfaces: dict[InterfaceArrivalTarget, dict[Placeholder, JsonValue]] = Field(
        default_factory=dict,
        description="The active input bindings by root-relative interface target.",
        examples=[{"interface.stdin": {"COMMAND": "pwd"}}],
    )


class Emission(OakModel):
    """One validated interface emission."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "interface": "interface.stdout",
                    "values": {"OUTPUT": "/oak"},
                }
            ]
        }
    )

    interface: InterfaceArrivalTarget = Field(
        description="The root-relative output interface target.",
        examples=["interface.stdout"],
    )
    values: dict[Placeholder, JsonValue] = Field(
        description="The validated schema bindings.",
        examples=[{"OUTPUT": "/oak"}],
    )


class ExecutionResult(OakModel):
    """The committed result of one arrival cycle."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "process": "process.pwd",
                    "state": {"state.mode": "open"},
                    "emissions": [
                        {
                            "interface": "interface.stdout",
                            "values": {"OUTPUT": "/oak"},
                        }
                    ],
                }
            ]
        }
    )

    process: TargetPath | None = Field(
        default=None,
        description="The selected root-relative process target, or null.",
        examples=["process.pwd"],
    )
    state: dict[TargetPath, JsonValue] = Field(
        description="The committed state by root-relative target.",
        examples=[{"state.mode": "open"}],
    )
    emissions: list[Emission] = Field(
        default_factory=list,
        description="The committed emissions in execution order.",
        examples=[[{"interface": "interface.stdout", "values": {"OUTPUT": "/oak"}}]],
    )


class ExecutionError(RuntimeError):
    """One runtime failure that discards staged OAK effects."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        suppressed: tuple[str, ...] = (),
    ) -> None:
        self.code = code
        self.message = message
        self.suppressed = suppressed
        suffix = "" if not suppressed else "; suppressed: " + " | ".join(suppressed)
        super().__init__(f"[{code}] {message}{suffix}")


def _json_equal(left: object, right: object) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(_json_equal(a, b) for a, b in zip(left, right, strict=True))
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(_json_equal(left[key], right[key]) for key in left)
    return type(left) is type(right) and left == right


def _resolve_value(
    graph: ResolvedGraph,
    document: str,
    value: Value,
    state: dict[str, JsonValue],
    interfaces: Mapping[tuple[str, str], Mapping[str, JsonValue]],
    bindings: Mapping[str, JsonValue],
) -> JsonValue:
    if isinstance(value, LiteralValue):
        return deepcopy(value.value)
    if isinstance(value, ConstantValue):
        _target_document, constant = graph.entry(document, value.constant, Constant)
        return deepcopy(constant.value)
    if isinstance(value, StateValue):
        identifier = target_id(value.state)
        key = graph.display_target(document, "state", identifier)
        if key not in state:
            raise ExecutionError("missing_state_value", f"state {key} is absent")
        return deepcopy(state[key])
    if isinstance(value, InterfaceValue):
        identifier = target_id(value.interface)
        values = interfaces.get((document, identifier))
        if values is None or value.placeholder not in values:
            raise ExecutionError("missing_interface_value", f"interface {identifier} has no {value.placeholder} value")
        return deepcopy(values[value.placeholder])
    if isinstance(value, BindingValue):
        if value.binding not in bindings:
            raise ExecutionError("missing_process_binding", f"binding {value.binding} is absent")
        return deepcopy(bindings[value.binding])
    raise TypeError(type(value).__name__)


def _ordered(operator: str, left: object, right: object) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        raise ExecutionError("ordered_comparison_type_mismatch", "ordered comparison needs two numbers or two strings")
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        a, b = left, right
    elif isinstance(left, str) and isinstance(right, str):
        a, b = left, right
    else:
        raise ExecutionError("ordered_comparison_type_mismatch", "ordered comparison needs two numbers or two strings")
    return {
        "less_than": a < b,
        "less_than_or_equal": a <= b,
        "greater_than": a > b,
        "greater_than_or_equal": a >= b,
    }[operator]


def _condition(
    graph: ResolvedGraph,
    document: str,
    condition: Condition,
    state: dict[str, JsonValue],
    interfaces: Mapping[tuple[str, str], Mapping[str, JsonValue]],
    bindings: Mapping[str, JsonValue],
) -> bool:
    if isinstance(condition, Compare):
        left = _resolve_value(graph, document, condition.left, state, interfaces, bindings)
        right = _resolve_value(graph, document, condition.right, state, interfaces, bindings)
        if condition.operator == "equals":
            return _json_equal(left, right)
        if condition.operator == "not_equals":
            return not _json_equal(left, right)
        return _ordered(condition.operator, left, right)
    if isinstance(condition, All):
        for child in condition.conditions:
            if not _condition(graph, document, child, state, interfaces, bindings):
                return False
        return True
    if isinstance(condition, Any):
        for child in condition.conditions:
            if _condition(graph, document, child, state, interfaces, bindings):
                return True
        return False
    if isinstance(condition, Not):
        return not _condition(graph, document, condition.condition, state, interfaces, bindings)
    raise TypeError(type(condition).__name__)


def _invoke(
    step: Act,
    values: Mapping[str, JsonValue],
    act: ActHandler | None,
    tools: Mapping[str, ToolContract],
) -> dict[str, JsonValue]:
    handler: ActHandler | ToolHandler | None
    if step.tool is None:
        handler = act
        if handler is None:
            raise ExecutionError("act_handler_missing", "an interpreter-native act needs an act handler")
    else:
        contract = tools.get(step.tool)
        if contract is None:
            raise ExecutionError("unknown_tool", f"tool {step.tool} is absent")
        handler = contract.handler
    try:
        authored = handler(step, values)
        outputs = _BINDING_ADAPTER.validate_python(dict(authored))
    except ExecutionError:
        raise
    except Exception as error:
        raise ExecutionError("act_failed" if step.tool is None else "tool_failed", str(error)) from None
    expected = set(step.outputs)
    supplied = set(outputs)
    if supplied != expected:
        raise ExecutionError(
            "act_output_mismatch",
            "act outputs differ; missing: "
            + (", ".join(sorted(expected - supplied)) or "none")
            + "; unused: "
            + (", ".join(sorted(supplied - expected)) or "none"),
        )
    return deepcopy(outputs)


def _parallel(
    graph: ResolvedGraph,
    document: str,
    step: Par,
    state: dict[str, JsonValue],
    interfaces: Mapping[tuple[str, str], Mapping[str, JsonValue]],
    bindings: Mapping[str, JsonValue],
    tools: Mapping[str, ToolContract],
) -> list[dict[str, JsonValue]]:
    acts = [child for child in step.steps if isinstance(child, Act)]
    prepared = [
        {
            binding.placeholder: _resolve_value(graph, document, binding.value, state, interfaces, bindings)
            for binding in child.inputs
        }
        for child in acts
    ]
    for child, values in zip(acts, prepared, strict=True):
        _validate_act_values(graph, document, child.input, values, "invalid_act_input")
    futures: list[Future[dict[str, JsonValue]]] = []
    with ThreadPoolExecutor(max_workers=len(acts)) as executor:
        for child, values in zip(acts, prepared, strict=True):
            futures.append(executor.submit(_invoke, child, values, None, tools))
        results: list[dict[str, JsonValue] | None] = []
        failures: list[str] = []
        for child, future in zip(acts, futures, strict=True):
            try:
                result = future.result()
                _validate_act_values(graph, document, child.output, result, "invalid_act_output")
                results.append(result)
            except Exception as error:
                results.append(None)
                failures.append(str(error))
    if failures:
        raise ExecutionError("parallel_failed", failures[0], suppressed=tuple(failures[1:]))
    return [result for result in results if result is not None]


def _schema(
    graph: ResolvedGraph,
    document: str,
    target: str | None,
) -> Schema | None:
    if target is None:
        return None
    _schema_document, schema = graph.entry(document, target, Schema)
    return schema


def _validate_act_values(
    graph: ResolvedGraph,
    document: str,
    target: str | None,
    values: Mapping[str, JsonValue],
    code: str,
) -> None:
    schema = _schema(graph, document, target)
    if schema is None:
        return
    try:
        schema.bind(values)
    except SchemaBindingError as error:
        raise ExecutionError(code, f"{target}: {error}") from None


def _validate_state_value(
    graph: ResolvedGraph,
    document: str,
    entry: State,
    value: JsonValue,
    key: str,
) -> None:
    schema = _schema(graph, document, entry.schema_id)
    if schema is None or entry.placeholder is None:
        return
    try:
        schema.bind_value(entry.placeholder, value)
    except SchemaBindingError as error:
        raise ExecutionError("invalid_state_value", f"state {key}: {error}") from None


def _run_process(
    graph: ResolvedGraph,
    document: str,
    process: Process,
    inputs: Mapping[str, JsonValue],
    state: dict[str, JsonValue],
    interfaces: Mapping[tuple[str, str], Mapping[str, JsonValue]],
    emissions: list[Emission],
    act: ActHandler | None,
    tools: Mapping[str, ToolContract],
) -> dict[str, JsonValue]:
    input_schema = _schema(graph, document, process.input)
    if input_schema is None:
        if inputs:
            raise ExecutionError("invalid_process_input", f"process {process.id} has no input schema")
    else:
        try:
            input_schema.bind(inputs)
        except SchemaBindingError as error:
            raise ExecutionError("invalid_process_input", f"process {process.id}: {error}") from None
    bindings = deepcopy(dict(inputs))
    _run_steps(graph, document, process.steps, state, interfaces, emissions, bindings, act, tools)
    output_schema = _schema(graph, document, process.output)
    if output_schema is None:
        return {}
    names = [item.placeholder for item in output_schema.where]
    outputs = {name: deepcopy(bindings[name]) for name in names if name in bindings}
    try:
        output_schema.bind(outputs)
    except SchemaBindingError as error:
        raise ExecutionError("invalid_process_output", f"process {process.id}: {error}") from None
    return outputs


def _run_steps(
    graph: ResolvedGraph,
    document: str,
    steps: list[Step],
    state: dict[str, JsonValue],
    interfaces: Mapping[tuple[str, str], Mapping[str, JsonValue]],
    emissions: list[Emission],
    bindings: dict[str, JsonValue],
    act: ActHandler | None,
    tools: Mapping[str, ToolContract],
) -> None:
    pending: list[dict[str, JsonValue]] | None = None
    for step in steps:
        if isinstance(step, Act):
            values = {
                binding.placeholder: _resolve_value(graph, document, binding.value, state, interfaces, bindings)
                for binding in step.inputs
            }
            _validate_act_values(graph, document, step.input, values, "invalid_act_input")
            outputs = _invoke(step, values, act, tools)
            _validate_act_values(graph, document, step.output, outputs, "invalid_act_output")
            bindings.update(outputs)
        elif isinstance(step, Set):
            identifier = target_id(step.state)
            _state_document, entry = graph.entry(document, step.state, State)
            key = graph.display_target(document, "state", identifier)
            resolved = _JSON_ADAPTER.validate_python(
                _resolve_value(graph, document, step.value, state, interfaces, bindings)
            )
            _validate_state_value(graph, _state_document, entry, resolved, key)
            state[key] = resolved
        elif isinstance(step, Emit):
            identifier = target_id(step.interface)
            _interface_document, interface = graph.entry(document, step.interface, Interface)
            _schema_document, schema = graph.entry(document, interface.schema_id, Schema)
            values = {
                binding.placeholder: _resolve_value(graph, document, binding.value, state, interfaces, bindings)
                for binding in step.bindings
            }
            try:
                schema.bind(values)
            except SchemaBindingError as error:
                raise ExecutionError("invalid_emission", f"interface {identifier}: {error}") from None
            emissions.append(
                Emission(
                    interface=graph.display_target(document, "interface", identifier),
                    values=deepcopy(values),
                )
            )
        elif isinstance(step, If):
            selected = step.then if _condition(graph, document, step.condition, state, interfaces, bindings) else step.otherwise
            if selected is not None:
                _run_steps(graph, document, selected, state, interfaces, emissions, dict(bindings), act, tools)
        elif isinstance(step, Call):
            values = {
                binding.placeholder: _resolve_value(graph, document, binding.value, state, interfaces, bindings)
                for binding in step.inputs
            }
            target_document, process = graph.entry(document, step.process, Process)
            outputs = _run_process(
                graph,
                target_document,
                process,
                values,
                state,
                interfaces,
                emissions,
                act,
                tools,
            )
            for name in step.outputs:
                bindings[name] = deepcopy(outputs[name])
        elif isinstance(step, Fail):
            raise ExecutionError("process_failed", step.message)
        elif isinstance(step, Assert):
            if not _condition(graph, document, step.condition, state, interfaces, bindings):
                raise ExecutionError("assertion_failed", step.message or "process assertion failed")
        elif isinstance(step, Foreach):
            items = _resolve_value(graph, document, step.value, state, interfaces, bindings)
            if not isinstance(items, list):
                raise ExecutionError("foreach_source_not_list", "FOREACH value is not a JSON list")
            for item in items:
                local = dict(bindings)
                local[step.binding] = deepcopy(item)
                _run_steps(graph, document, step.steps, state, interfaces, emissions, local, act, tools)
        elif isinstance(step, While):
            for _iteration in range(step.limit):
                if not _condition(
                    graph,
                    document,
                    step.condition,
                    state,
                    interfaces,
                    bindings,
                ):
                    break
                _run_steps(
                    graph,
                    document,
                    step.steps,
                    state,
                    interfaces,
                    emissions,
                    dict(bindings),
                    act,
                    tools,
                )
            else:
                if _condition(
                    graph,
                    document,
                    step.condition,
                    state,
                    interfaces,
                    bindings,
                ):
                    raise ExecutionError(
                        "while_limit_reached",
                        f"WHILE condition remains true after {step.limit} iterations",
                    )
        elif isinstance(step, Par):
            pending = _parallel(graph, document, step, state, interfaces, bindings, tools)
        elif isinstance(step, Join):
            if pending is None:
                raise ExecutionError("join_without_par", "JOIN has no pending PAR")
            for result in pending:
                bindings.update(result)
            pending = None
        else:
            raise TypeError(type(step).__name__)
    if pending is not None:
        raise ExecutionError("parallel_join_missing", "PAR has no JOIN")


def _active_interfaces(graph: ResolvedGraph, arrival: Arrival) -> dict[tuple[str, str], dict[str, JsonValue]]:
    active: dict[tuple[str, str], dict[str, JsonValue]] = {}
    for target, values in arrival.interfaces.items():
        document, interface = graph.entry(graph.root, target, Interface)
        if interface.direction not in ("in", "inout"):
            raise ExecutionError("interface_direction_mismatch", f"interface {target} cannot receive input")
        _schema_document, schema = graph.entry(document, interface.schema_id, Schema)
        try:
            schema.bind(values)
        except SchemaBindingError as error:
            raise ExecutionError("invalid_interface_binding", f"interface {target}: {error}") from None
        active[(document, interface.id)] = deepcopy(values)
    return active


def _authored_state(graph: ResolvedGraph) -> dict[str, JsonValue]:
    return {
        graph.display_target(document, "state", entry.id): deepcopy(entry.value)
        for document, node in graph.documents.items()
        for entry in node.state
    }


def execute(
    node: Node,
    arrival: Arrival,
    state: Mapping[str, JsonValue],
    *,
    act: ActHandler | None = None,
    tools: Mapping[str, ToolContract] | None = None,
    source: str | None = None,
    load: DocumentLoader | None = None,
    root: str | None = None,
) -> ExecutionResult:
    """Run one arrival cycle and commit state and emissions on success."""
    graph = resolve(node, source=source, load=load, root=root)
    tool_registry = tools or {}
    for document in graph.documents.values():
        try:
            validate_tools(document, tool_registry)
        except Exception as error:
            code = getattr(error, "type", None) or getattr(error, "code", None) or "tool_validation_failed"
            raise ExecutionError(str(code), str(error)) from None
    try:
        working_state = _STATE_ADAPTER.validate_python(dict(state))
    except ValidationError as error:
        raise ExecutionError("invalid_execution_state", str(error)) from None
    expected_state = set(_authored_state(graph))
    supplied_state = set(working_state)
    if supplied_state != expected_state:
        raise ExecutionError(
            "execution_state_mismatch",
            "state differs; missing: "
            + (", ".join(sorted(expected_state - supplied_state)) or "none")
            + "; unknown: "
            + (", ".join(sorted(supplied_state - expected_state)) or "none"),
        )
    for document, graph_node in graph.documents.items():
        for entry in graph_node.state:
            if entry.schema_id is None:
                continue
            key = graph.display_target(document, "state", entry.id)
            _validate_state_value(graph, document, entry, working_state[key], key)
    active = _active_interfaces(graph, arrival)
    matches: list[Trigger] = []
    for trigger in node.triggers:
        if trigger.when != arrival.when:
            continue
        if trigger.given is True or _condition(graph, graph.root, trigger.given, working_state, active, {}):
            matches.append(trigger)
    if len(matches) > 1:
        raise ExecutionError("ambiguous_trigger_match", "arrival matches triggers " + ", ".join(item.id for item in matches))
    if not matches:
        return ExecutionResult(state=working_state)
    process_document, process = graph.entry(graph.root, matches[0].then, Process)
    seeded = {
        binding.placeholder: _resolve_value(graph, graph.root, binding.value, working_state, active, {})
        for binding in matches[0].inputs
    }
    emissions: list[Emission] = []
    _run_process(
        graph,
        process_document,
        process,
        seeded,
        working_state,
        active,
        emissions,
        act,
        tool_registry,
    )
    return ExecutionResult(
        process=graph.display_target(process_document, "process", process.id),
        state=working_state,
        emissions=emissions,
    )
