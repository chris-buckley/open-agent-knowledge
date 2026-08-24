"""Root graph checks for ids, typed references, guards, and process flow."""

from collections import defaultdict
from collections.abc import Iterator
from itertools import combinations
from typing import TypeVar

from pydantic_core import PydanticCustomError

from oak.base import Entry
from oak.node.model import Node
from oak.node.parts import (
    Act,
    BindingValue,
    Call,
    Condition,
    Constant,
    ConstantValue,
    Emit,
    Fail,
    If,
    Interface,
    InterfaceValue,
    LiteralValue,
    Process,
    Schema,
    SchemaBindingError,
    Set,
    State,
    StateValue,
    Step,
    Trigger,
    Value,
)

TargetEntry = TypeVar("TargetEntry", bound=Entry)
_STATIC_MISSING = object()


def iter_nodes(root: Node) -> Iterator[Node]:
    """Yield the root and every child node in authored order."""
    yield root
    for child in root.children:
        yield from iter_nodes(child)


def iter_entries(node: Node) -> Iterator[Entry]:
    """Yield one node's entries in OAK part order."""
    yield from node.instructions
    yield from node.constants
    yield from node.schemas
    yield from node.state
    yield from node.triggers
    yield from node.processes
    yield from node.interfaces


def _target(
    registry: dict[str, Node | Entry],
    source: Entry,
    target_id: str,
    expected: type[TargetEntry],
) -> TargetEntry:
    source_type = type(source).__name__.lower()
    target_type = expected.__name__.lower()
    target = registry.get(target_id)

    if target is None:
        raise PydanticCustomError(
            "missing_reference_target",
            "{source_type} {source} targets missing {target_type} {target}",
            {
                "source_type": source_type,
                "source": source.id,
                "target_type": target_type,
                "target": target_id,
            },
        )

    if not isinstance(target, expected):
        raise PydanticCustomError(
            "wrong_reference_target_type",
            "{source_type} {source} targets {target}, which is not a {target_type}",
            {
                "source_type": source_type,
                "source": source.id,
                "target": target_id,
                "target_type": target_type,
            },
        )
    return target


def _interface_schema(
    registry: dict[str, Node | Entry],
    interface: Interface,
) -> Schema:
    return _target(registry, interface, interface.schema_id, Schema)


def _direction_error(
    process: Process,
    action: str,
    interface: Interface,
) -> None:
    raise PydanticCustomError(
        "interface_direction_mismatch",
        "process {process} cannot {action} interface {interface} with direction {direction}",
        {
            "process": process.id,
            "action": action,
            "interface": interface.id,
            "direction": interface.direction,
        },
    )


def _validate_value(
    registry: dict[str, Node | Entry],
    process: Process,
    value: Value,
) -> None:
    if isinstance(value, ConstantValue):
        _target(registry, process, value.constant, Constant)
    elif isinstance(value, StateValue):
        _target(registry, process, value.state, State)
    elif isinstance(value, InterfaceValue):
        interface = _target(
            registry,
            process,
            value.interface,
            Interface,
        )
        if interface.direction not in ("in", "inout"):
            _direction_error(process, "read", interface)

        schema = _interface_schema(registry, interface)
        if value.placeholder not in schema.placeholders:
            raise PydanticCustomError(
                "unknown_interface_placeholder",
                "process {process} reads placeholder {placeholder} absent from interface {interface} schema {schema}",
                {
                    "process": process.id,
                    "placeholder": value.placeholder,
                    "interface": interface.id,
                    "schema": schema.id,
                },
            )


def _validate_guard_value(
    registry: dict[str, Node | Entry],
    trigger: Trigger,
    value: Value,
) -> None:
    if isinstance(value, ConstantValue):
        _target(registry, trigger, value.constant, Constant)
    elif isinstance(value, StateValue):
        _target(registry, trigger, value.state, State)
    elif isinstance(value, (InterfaceValue, BindingValue)):
        raise PydanticCustomError(
            "invalid_trigger_guard_value",
            "trigger {trigger} guard cannot read an interface or local binding",
            {"trigger": trigger.id},
        )


def _static_value(
    registry: dict[str, Node | Entry],
    source: Entry,
    value: Value,
) -> object:
    if isinstance(value, LiteralValue):
        return value.value
    if isinstance(value, ConstantValue):
        return _target(
            registry,
            source,
            value.constant,
            Constant,
        ).value
    return _STATIC_MISSING


def _json_equal(left: object, right: object) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return (
            isinstance(left, bool)
            and isinstance(right, bool)
            and left == right
        )

    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right

    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(
            _json_equal(left_item, right_item)
            for left_item, right_item in zip(left, right, strict=True)
        )

    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(
            _json_equal(left[key], right[key])
            for key in left
        )

    return type(left) is type(right) and left == right


def _condition_result(
    registry: dict[str, Node | Entry],
    process: Process,
    step: If,
) -> bool | None:
    left = step.condition.left
    right = step.condition.right

    if (
        type(left) is type(right)
        and isinstance(
            left,
            (
                ConstantValue,
                StateValue,
                InterfaceValue,
                BindingValue,
            ),
        )
        and left == right
    ):
        equal = True
    else:
        left_value = _static_value(registry, process, left)
        right_value = _static_value(registry, process, right)
        if (
            left_value is _STATIC_MISSING
            or right_value is _STATIC_MISSING
        ):
            return None
        equal = _json_equal(left_value, right_value)

    return (
        equal
        if step.condition.operator == "equals"
        else not equal
    )


def _guard_constraint(
    registry: dict[str, Node | Entry],
    trigger: Trigger,
    condition: Condition,
) -> tuple[str, str, object] | None:
    left = condition.left
    right = condition.right

    if isinstance(left, StateValue):
        static = _static_value(registry, trigger, right)
        if static is not _STATIC_MISSING:
            return left.state, condition.operator, static

    if isinstance(right, StateValue):
        static = _static_value(registry, trigger, left)
        if static is not _STATIC_MISSING:
            return right.state, condition.operator, static

    return None


def _guards_disjoint(
    registry: dict[str, Node | Entry],
    left: Trigger,
    right: Trigger,
) -> bool:
    if left.given is None or right.given is None:
        return False

    left_constraint = _guard_constraint(
        registry,
        left,
        left.given,
    )
    right_constraint = _guard_constraint(
        registry,
        right,
        right.given,
    )
    if left_constraint is None or right_constraint is None:
        return False

    left_state, left_operator, left_value = left_constraint
    right_state, right_operator, right_value = right_constraint
    if left_state != right_state:
        return False

    equal_values = _json_equal(left_value, right_value)
    if left_operator == right_operator == "equals":
        return not equal_values

    return left_operator != right_operator and equal_values


def _validate_trigger_guards(
    registry: dict[str, Node | Entry],
    triggers: list[Trigger],
) -> None:
    by_when: dict[str, list[Trigger]] = defaultdict(list)

    for trigger in triggers:
        _target(
            registry,
            trigger,
            trigger.process,
            Process,
        )
        if trigger.given is not None:
            _validate_guard_value(
                registry,
                trigger,
                trigger.given.left,
            )
            _validate_guard_value(
                registry,
                trigger,
                trigger.given.right,
            )
        by_when[trigger.when].append(trigger)

    for when, group in by_when.items():
        for left, right in combinations(group, 2):
            if not _guards_disjoint(registry, left, right):
                raise PydanticCustomError(
                    "overlapping_trigger_guards",
                    "triggers {left} and {right} share when {when} without provably disjoint guards",
                    {
                        "left": left.id,
                        "right": right.id,
                        "when": when,
                    },
                )


def _static_emit_values(
    registry: dict[str, Node | Entry],
    process: Process,
    step: Emit,
) -> dict[str, object] | None:
    values: dict[str, object] = {}
    for binding in step.bindings:
        value = _static_value(
            registry,
            process,
            binding.value,
        )
        if value is _STATIC_MISSING:
            return None
        values[binding.placeholder] = value
    return values


def _validate_steps(
    registry: dict[str, Node | Entry],
    process: Process,
    steps: list[Step],
) -> None:
    for step in steps:
        if isinstance(step, Act):
            for binding in step.inputs:
                _validate_value(
                    registry,
                    process,
                    binding.value,
                )

        elif isinstance(step, Set):
            _target(
                registry,
                process,
                step.state,
                State,
            )
            _validate_value(
                registry,
                process,
                step.value,
            )

        elif isinstance(step, Emit):
            interface = _target(
                registry,
                process,
                step.interface,
                Interface,
            )
            if interface.direction not in ("out", "inout"):
                _direction_error(process, "emit", interface)

            schema = _interface_schema(registry, interface)
            authored = {
                binding.placeholder
                for binding in step.bindings
            }
            expected = schema.placeholders
            if authored != expected:
                raise PydanticCustomError(
                    "emit_schema_binding_mismatch",
                    "process {process} emit bindings differ from interface {interface} schema; missing: {missing}; unused: {unused}",
                    {
                        "process": process.id,
                        "interface": interface.id,
                        "missing": (
                            ", ".join(sorted(expected - authored))
                            or "none"
                        ),
                        "unused": (
                            ", ".join(sorted(authored - expected))
                            or "none"
                        ),
                    },
                )

            for binding in step.bindings:
                _validate_value(
                    registry,
                    process,
                    binding.value,
                )

            static_values = _static_emit_values(
                registry,
                process,
                step,
            )
            if static_values is not None:
                try:
                    schema.bind(static_values)
                except SchemaBindingError as error:
                    raise PydanticCustomError(
                        "invalid_static_schema_binding",
                        "process {process} emits an invalid static binding through interface {interface}: {reason}",
                        {
                            "process": process.id,
                            "interface": interface.id,
                            "reason": str(error),
                        },
                    ) from None

        elif isinstance(step, If):
            _validate_value(
                registry,
                process,
                step.condition.left,
            )
            _validate_value(
                registry,
                process,
                step.condition.right,
            )

            result = _condition_result(
                registry,
                process,
                step,
            )
            if result is False:
                raise PydanticCustomError(
                    "dead_process_branch",
                    "process {process} has an if then branch that cannot run",
                    {"process": process.id},
                )
            if result is True and step.otherwise is not None:
                raise PydanticCustomError(
                    "dead_process_branch",
                    "process {process} has an if otherwise branch that cannot run",
                    {"process": process.id},
                )

            _validate_steps(
                registry,
                process,
                step.then,
            )
            if step.otherwise is not None:
                _validate_steps(
                    registry,
                    process,
                    step.otherwise,
                )

        elif isinstance(step, Call):
            _target(
                registry,
                process,
                step.process,
                Process,
            )

        elif isinstance(step, Fail):
            continue

        else:
            raise TypeError(
                f"unsupported process step {type(step).__name__}"
            )


def _calls(steps: list[Step]) -> Iterator[str]:
    for step in steps:
        if isinstance(step, Call):
            yield step.process
        elif isinstance(step, If):
            yield from _calls(step.then)
            if step.otherwise is not None:
                yield from _calls(step.otherwise)


def _validate_call_graph(processes: list[Process]) -> None:
    graph = {
        process.id: list(_calls(process.steps))
        for process in processes
    }
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(process_id: str) -> None:
        state[process_id] = 1
        stack.append(process_id)

        for target in graph[process_id]:
            target_state = state.get(target, 0)
            if target_state == 0:
                visit(target)
            elif target_state == 1:
                start = stack.index(target)
                cycle = stack[start:] + [target]
                raise PydanticCustomError(
                    "process_call_cycle",
                    "process call cycle: {cycle}",
                    {"cycle": " -> ".join(cycle)},
                )

        stack.pop()
        state[process_id] = 2

    for process in processes:
        if state.get(process.id, 0) == 0:
            visit(process.id)


def validate_graph(root: Node) -> None:
    """Reject duplicate ids, invalid references, guards, and process graphs."""
    registry: dict[str, Node | Entry] = {}
    duplicates: set[str] = set()
    nodes = list(iter_nodes(root))

    for node in nodes:
        for item in (node, *iter_entries(node)):
            if item.id in registry:
                duplicates.add(item.id)
            else:
                registry[item.id] = item

    if duplicates:
        raise PydanticCustomError(
            "duplicate_id",
            "tree repeats ids: {ids}",
            {"ids": ", ".join(sorted(duplicates))},
        )

    triggers = [
        trigger
        for node in nodes
        for trigger in node.triggers
    ]
    _validate_trigger_guards(registry, triggers)

    for node in nodes:
        for interface in node.interfaces:
            _interface_schema(registry, interface)

    processes = [
        process
        for node in nodes
        for process in node.processes
    ]
    for process in processes:
        _validate_steps(
            registry,
            process,
            process.steps,
        )

    _validate_call_graph(processes)
