"""Standalone checks for ids, references, guards, tools, and process flow."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator, Mapping
from itertools import combinations
from typing import Protocol, TypeVar

from pydantic_core import PydanticCustomError

from oak.base import Entry
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
    condition_values,
    step_values,
)
from oak.node.parts.processes import (
    process_visible_bindings,
    validate_act_contract,
    validate_call_contract,
    validate_process_contract,
)
from oak.node.parts.triggers import validate_trigger_contract
from oak.rules import rule_error
from oak.vocabulary.text.target_path import is_relative_target, target_id

if False:
    from oak.node.model import Node

TargetEntry = TypeVar("TargetEntry", bound=Entry)
_STATIC_MISSING = object()


class ToolContractLike(Protocol):
    """The tool contract fields used by graph validation."""

    inputs: frozenset[str]
    outputs: frozenset[str]
    parallel: bool
    input: str | None
    output: str | None


def iter_entries(node: Node) -> Iterator[Entry]:
    """Yield one document's entries in OAK part order."""
    yield from node.instructions
    yield from node.constants
    yield from node.schemas
    yield from node.state
    yield from node.triggers
    yield from node.processes
    yield from node.interfaces


def entry_registry(node: Node) -> dict[str, Entry]:
    """Return one document's unique local entry registry."""
    registry: dict[str, Entry] = {}
    duplicates: set[str] = set()
    for entry in iter_entries(node):
        if entry.id in registry:
            duplicates.add(entry.id)
        else:
            registry[entry.id] = entry
    if duplicates:
        raise PydanticCustomError(
            "duplicate_id",
            "document repeats ids: {ids}",
            {"ids": ", ".join(sorted(duplicates))},
        )
    return registry


def _target(
    registry: Mapping[str, Entry],
    source: Entry,
    path: str,
    expected: type[TargetEntry],
) -> TargetEntry | None:
    if is_relative_target(path):
        return None
    identifier = target_id(path)
    target = registry.get(identifier)
    source_type = type(source).__name__.lower()
    target_type = expected.__name__.lower()
    if target is None:
        raise PydanticCustomError(
            "missing_reference_target",
            "{source_type} {source} targets missing {target_type} {target}",
            {
                "source_type": source_type,
                "source": source.id,
                "target_type": target_type,
                "target": path,
            },
        )
    if not isinstance(target, expected):
        raise PydanticCustomError(
            "wrong_reference_target_type",
            "{source_type} {source} targets {target}, which is not a {target_type}",
            {
                "source_type": source_type,
                "source": source.id,
                "target": path,
                "target_type": target_type,
            },
        )
    return target


def _interface_schema(registry: Mapping[str, Entry], interface: Interface) -> Schema | None:
    return _target(registry, interface, interface.schema_id, Schema)


def _process_schema(
    registry: Mapping[str, Entry],
    process: Process,
    target: str | None,
) -> Schema | None:
    return None if target is None else _target(registry, process, target, Schema)


def _direction_error(process: Process, action: str, interface: Interface) -> None:
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


def _validate_value(registry: Mapping[str, Entry], source: Entry, value: Value) -> None:
    if isinstance(value, ConstantValue):
        _target(registry, source, value.constant, Constant)
        return
    if isinstance(value, StateValue):
        _target(registry, source, value.state, State)
        return
    if not isinstance(value, InterfaceValue):
        return
    if isinstance(source, Process) and source.input is not None:
        raise rule_error(
            "typed_process_interface_read",
            "process {process} has an input schema and reads {interface}",
            {
                "process": source.id,
                "interface": value.interface,
            },
        )
    interface = _target(registry, source, value.interface, Interface)
    if interface is None:
        return
    if interface.direction not in ("in", "inout"):
        if isinstance(source, Process):
            _direction_error(source, "read", interface)
        raise PydanticCustomError(
            "interface_direction_mismatch",
            "{source} cannot read interface {interface} with direction {direction}",
            {
                "source": source.id,
                "interface": interface.id,
                "direction": interface.direction,
            },
        )
    schema = _interface_schema(registry, interface)
    if schema is not None and value.placeholder not in schema.placeholders:
        raise PydanticCustomError(
            "unknown_interface_placeholder",
            "{source} reads placeholder {placeholder} absent from interface {interface} schema {schema}",
            {
                "source": source.id,
                "placeholder": value.placeholder,
                "interface": interface.id,
                "schema": schema.id,
            },
        )


def _json_equal(left: object, right: object) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(
            _json_equal(a, b) for a, b in zip(left, right, strict=True)
        )
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(
            _json_equal(left[key], right[key]) for key in left
        )
    return type(left) is type(right) and left == right


def _static_value(
    registry: Mapping[str, Entry],
    source: Entry,
    value: Value,
) -> object:
    if isinstance(value, LiteralValue):
        return value.value
    if isinstance(value, ConstantValue):
        constant = _target(registry, source, value.constant, Constant)
        return constant.value if constant is not None else _STATIC_MISSING
    return _STATIC_MISSING


def _same_dynamic_value(left: Value, right: Value) -> bool:
    return (
        type(left) is type(right)
        and isinstance(left, (ConstantValue, StateValue, InterfaceValue, BindingValue))
        and left == right
    )


def _ordered_pair(
    left: object,
    right: object,
) -> tuple[int | float | str, int | float | str] | None:
    if isinstance(left, bool) or isinstance(right, bool):
        return None
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left, right
    if isinstance(left, str) and isinstance(right, str):
        return left, right
    return None


def _compare_static(operator: str, left: object, right: object) -> bool:
    if operator == "equals":
        return _json_equal(left, right)
    if operator == "not_equals":
        return not _json_equal(left, right)
    pair = _ordered_pair(left, right)
    if pair is None:
        raise PydanticCustomError(
            "ordered_comparison_type_mismatch",
            "ordered comparison needs two numbers or two strings",
        )
    a, b = pair
    if operator == "less_than":
        return a < b
    if operator == "less_than_or_equal":
        return a <= b
    if operator == "greater_than":
        return a > b
    if operator == "greater_than_or_equal":
        return a >= b
    raise TypeError(f"unsupported comparison operator {operator}")


def condition_result(
    registry: Mapping[str, Entry],
    source: Entry,
    condition: Condition,
) -> bool | None:
    """Return one statically known condition result when possible."""
    if isinstance(condition, Compare):
        if _same_dynamic_value(condition.left, condition.right):
            if condition.operator == "equals":
                return True
            if condition.operator == "not_equals":
                return False
            return None
        left = _static_value(registry, source, condition.left)
        right = _static_value(registry, source, condition.right)
        if left is _STATIC_MISSING or right is _STATIC_MISSING:
            return None
        return _compare_static(condition.operator, left, right)
    if isinstance(condition, All):
        unknown = False
        for child in condition.conditions:
            result = condition_result(registry, source, child)
            if result is False:
                return False
            if result is None:
                unknown = True
        return None if unknown else True
    if isinstance(condition, Any):
        unknown = False
        for child in condition.conditions:
            result = condition_result(registry, source, child)
            if result is True:
                return True
            if result is None:
                unknown = True
        return None if unknown else False
    if isinstance(condition, Not):
        result = condition_result(registry, source, condition.condition)
        return None if result is None else not result
    raise TypeError(f"unsupported condition {type(condition).__name__}")


def _validate_condition(
    registry: Mapping[str, Entry],
    source: Entry,
    condition: Condition,
) -> None:
    for value in condition_values(condition):
        _validate_value(registry, source, value)
    if not isinstance(condition, Compare):
        return
    left = _static_value(registry, source, condition.left)
    right = _static_value(registry, source, condition.right)
    if (
        condition.operator not in ("equals", "not_equals")
        and left is not _STATIC_MISSING
        and right is not _STATIC_MISSING
        and _ordered_pair(left, right) is None
    ):
        raise PydanticCustomError(
            "ordered_comparison_type_mismatch",
            "ordered comparison needs two numbers or two strings",
        )


def _static_emit_values(
    registry: Mapping[str, Entry],
    process: Process,
    step: Emit,
) -> dict[str, object] | None:
    values: dict[str, object] = {}
    for binding in step.bindings:
        value = _static_value(registry, process, binding.value)
        if value is _STATIC_MISSING:
            return None
        values[binding.placeholder] = value
    return values


def _act_contract(
    registry: Mapping[str, Entry],
    process: Process,
    step: Act,
) -> None:
    input_schema = _process_schema(registry, process, step.input)
    output_schema = _process_schema(registry, process, step.output)
    input_known = step.input is None or input_schema is not None
    output_known = step.output is None or output_schema is not None
    if input_known and output_known:
        validate_act_contract(
            step,
            None if input_schema is None else input_schema.placeholders,
            None if output_schema is None else output_schema.placeholders,
        )


def validate_typed_value(entry: Constant | State, schema: Schema) -> None:
    """Validate one AS-bound entry value against its resolved schema."""
    if entry.placeholder is None:
        return
    source_type = type(entry).__name__.lower()
    try:
        schema.bind_value(entry.placeholder, entry.value)
    except SchemaBindingError as error:
        code = error.failures[0].code
        if code == "unknown_binding":
            raise rule_error(
                "unknown_schema_placeholder",
                "{source_type} {source} binds placeholder {placeholder} absent from schema {schema}",
                {
                    "source_type": source_type,
                    "source": entry.id,
                    "placeholder": entry.placeholder,
                    "schema": schema.id,
                },
            ) from None
        if code == "unresolved_binding":
            raise rule_error(
                "unresolved_schema_binding",
                "{source_type} {source} binds placeholder {placeholder} with a placeholder-valued bound",
                {
                    "source_type": source_type,
                    "source": entry.id,
                    "placeholder": entry.placeholder,
                },
            ) from None
        raise rule_error(
            "invalid_schema_binding",
            "{source_type} {source} value fails schema {schema}: {reason}",
            {
                "source_type": source_type,
                "source": entry.id,
                "schema": schema.id,
                "reason": str(error),
            },
        ) from None


def _validate_typed_entries(
    registry: Mapping[str, Entry],
    node: Node,
) -> None:
    for entry in (*node.constants, *node.state):
        if entry.schema_id is None:
            continue
        schema = _target(registry, entry, entry.schema_id, Schema)
        if schema is not None:
            validate_typed_value(entry, schema)


def _call_contract(
    registry: Mapping[str, Entry],
    source: Process,
    step: Call,
    target: Process,
) -> None:
    input_schema = _process_schema(registry, target, target.input)
    output_schema = _process_schema(registry, target, target.output)
    input_known = target.input is None or input_schema is not None
    output_known = target.output is None or output_schema is not None
    if input_known and output_known:
        validate_call_contract(
            step,
            set() if input_schema is None else input_schema.placeholders,
            set() if output_schema is None else output_schema.placeholders,
        )


def _validate_steps(
    registry: Mapping[str, Entry],
    process: Process,
    steps: list[Step],
) -> None:
    for step in steps:
        for value in step_values(step):
            _validate_value(registry, process, value)
        if isinstance(step, Set):
            _target(registry, process, step.state, State)
            continue
        if isinstance(step, Emit):
            interface = _target(registry, process, step.interface, Interface)
            if interface is None:
                continue
            if interface.direction not in ("out", "inout"):
                _direction_error(process, "emit", interface)
            schema = _interface_schema(registry, interface)
            if schema is None:
                continue
            authored = {binding.placeholder for binding in step.bindings}
            expected = schema.placeholders
            if authored != expected:
                raise PydanticCustomError(
                    "emit_schema_binding_mismatch",
                    (
                        "process {process} emit bindings differ from interface "
                        "{interface} schema; missing: {missing}; unused: {unused}"
                    ),
                    {
                        "process": process.id,
                        "interface": interface.id,
                        "missing": ", ".join(sorted(expected - authored)) or "none",
                        "unused": ", ".join(sorted(authored - expected)) or "none",
                    },
                )
            static_values = _static_emit_values(registry, process, step)
            if static_values is not None:
                try:
                    schema.bind(static_values)
                except SchemaBindingError as error:
                    raise PydanticCustomError(
                        "invalid_static_schema_binding",
                        (
                            "process {process} emits an invalid static binding "
                            "through interface {interface}: {reason}"
                        ),
                        {
                            "process": process.id,
                            "interface": interface.id,
                            "reason": str(error),
                        },
                    ) from None
            continue
        if isinstance(step, If):
            _validate_condition(registry, process, step.condition)
            result = condition_result(registry, process, step.condition)
            if result is False:
                raise PydanticCustomError(
                    "dead_process_branch",
                    "process {process} has an IF THEN branch that cannot run",
                    {"process": process.id},
                )
            if result is True and step.otherwise is not None:
                raise PydanticCustomError(
                    "dead_process_branch",
                    "process {process} has an ELSE branch that cannot run",
                    {"process": process.id},
                )
            _validate_steps(registry, process, step.then)
            if step.otherwise is not None:
                _validate_steps(registry, process, step.otherwise)
            continue
        if isinstance(step, Assert):
            _validate_condition(registry, process, step.condition)
            result = condition_result(registry, process, step.condition)
            if result is False:
                raise PydanticCustomError(
                    "assertion_always_fails",
                    "process {process} has an assertion that is statically false",
                    {"process": process.id},
                )
            if result is True:
                raise PydanticCustomError(
                    "redundant_assertion",
                    "process {process} has an assertion that is statically true",
                    {"process": process.id},
                )
            continue
        if isinstance(step, While):
            _validate_condition(registry, process, step.condition)
            if condition_result(registry, process, step.condition) is False:
                raise PydanticCustomError(
                    "dead_process_branch",
                    "process {process} has a WHILE body that cannot run",
                    {"process": process.id},
                )
            _validate_steps(registry, process, step.steps)
            continue
        if isinstance(step, Foreach):
            _validate_steps(registry, process, step.steps)
            continue
        if isinstance(step, Par):
            for child in step.steps:
                if isinstance(child, Act):
                    for binding in child.inputs:
                        _validate_value(registry, process, binding.value)
                    _act_contract(registry, process, child)
            continue
        if isinstance(step, Call):
            target = _target(registry, process, step.process, Process)
            if target is not None:
                _call_contract(registry, process, step, target)
            continue
        if isinstance(step, Act):
            _act_contract(registry, process, step)
            continue
        if isinstance(step, (Fail, Join)):
            continue
        raise TypeError(f"unsupported process step {type(step).__name__}")


def _validate_process_contract(
    registry: Mapping[str, Entry],
    process: Process,
) -> None:
    input_schema = _process_schema(registry, process, process.input)
    output_schema = _process_schema(registry, process, process.output)
    input_known = process.input is None or input_schema is not None
    output_known = process.output is None or output_schema is not None
    if not input_known:
        return
    inputs = set() if input_schema is None else input_schema.placeholders
    if output_known:
        validate_process_contract(
            process,
            inputs,
            set() if output_schema is None else output_schema.placeholders,
        )
    else:
        process_visible_bindings(process, inputs)


def _calls(steps: list[Step]) -> Iterator[str]:
    for step in steps:
        if isinstance(step, Call) and not is_relative_target(step.process):
            yield target_id(step.process)
            continue
        if isinstance(step, If):
            yield from _calls(step.then)
            if step.otherwise is not None:
                yield from _calls(step.otherwise)
            continue
        if isinstance(step, Foreach):
            yield from _calls(step.steps)
            continue
        if isinstance(step, While):
            yield from _calls(step.steps)


def _validate_call_graph(processes: list[Process]) -> None:
    graph = {process.id: list(_calls(process.steps)) for process in processes}
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


def _invert_operator(operator: str) -> str | None:
    return {
        "equals": "not_equals",
        "not_equals": "equals",
        "less_than": "greater_than_or_equal",
        "less_than_or_equal": "greater_than",
        "greater_than": "less_than_or_equal",
        "greater_than_or_equal": "less_than",
    }.get(operator)


def _reverse_operator(operator: str) -> str:
    return {
        "equals": "equals",
        "not_equals": "not_equals",
        "less_than": "greater_than",
        "less_than_or_equal": "greater_than_or_equal",
        "greater_than": "less_than",
        "greater_than_or_equal": "less_than_or_equal",
    }[operator]


def _guard_atom(
    registry: Mapping[str, Entry],
    trigger: Trigger,
    condition: Compare,
) -> tuple[str, str, object] | None:
    if isinstance(condition.left, StateValue):
        static = _static_value(registry, trigger, condition.right)
        if static is not _STATIC_MISSING:
            return target_id(condition.left.state), condition.operator, static
    if isinstance(condition.right, StateValue):
        static = _static_value(registry, trigger, condition.left)
        if static is not _STATIC_MISSING:
            return (
                target_id(condition.right.state),
                _reverse_operator(condition.operator),
                static,
            )
    return None


def _guard_atoms(
    registry: Mapping[str, Entry],
    trigger: Trigger,
    condition: Condition,
) -> list[tuple[str, str, object]] | None:
    if isinstance(condition, Compare):
        atom = _guard_atom(registry, trigger, condition)
        return [atom] if atom is not None else None
    if isinstance(condition, All):
        result: list[tuple[str, str, object]] = []
        for child in condition.conditions:
            child_atoms = _guard_atoms(registry, trigger, child)
            if child_atoms is None:
                return None
            result.extend(child_atoms)
        return result
    if isinstance(condition, Not):
        if not isinstance(condition.condition, Compare):
            return None
        atom = _guard_atom(registry, trigger, condition.condition)
        if atom is None:
            return None
        state, operator, value = atom
        inverse = _invert_operator(operator)
        return None if inverse is None else [(state, inverse, value)]
    return None


def _atom_accepts(atom: tuple[str, str, object], candidate: object) -> bool | None:
    _, operator, value = atom
    try:
        return _compare_static(operator, candidate, value)
    except PydanticCustomError:
        return None


def _range_bounds(
    atoms: list[tuple[str, str, object]],
) -> tuple[tuple[object, bool] | None, tuple[object, bool] | None] | None:
    lower: tuple[object, bool] | None = None
    upper: tuple[object, bool] | None = None
    for _, operator, value in atoms:
        if operator in ("greater_than", "greater_than_or_equal"):
            inclusive = operator == "greater_than_or_equal"
            if lower is None:
                lower = value, inclusive
                continue
            pair = _ordered_pair(lower[0], value)
            if pair is None:
                return None
            current, candidate = pair
            if candidate > current or (candidate == current and not inclusive and lower[1]):
                lower = value, inclusive
            continue
        if operator in ("less_than", "less_than_or_equal"):
            inclusive = operator == "less_than_or_equal"
            if upper is None:
                upper = value, inclusive
                continue
            pair = _ordered_pair(upper[0], value)
            if pair is None:
                return None
            current, candidate = pair
            if candidate < current or (candidate == current and not inclusive and upper[1]):
                upper = value, inclusive
    return lower, upper


def _atoms_conflict(
    left: list[tuple[str, str, object]],
    right: list[tuple[str, str, object]],
) -> bool:
    states = {atom[0] for atom in left} & {atom[0] for atom in right}
    for state in states:
        combined = [atom for atom in left + right if atom[0] == state]
        equals = [atom[2] for atom in combined if atom[1] == "equals"]
        if equals:
            first = equals[0]
            if any(not _json_equal(first, value) for value in equals[1:]):
                return True
            if any(_atom_accepts(atom, first) is False for atom in combined):
                return True
        bounds = _range_bounds(combined)
        if bounds is None:
            continue
        lower, upper = bounds
        if lower is None or upper is None:
            continue
        pair = _ordered_pair(lower[0], upper[0])
        if pair is None:
            continue
        lower_value, upper_value = pair
        if lower_value > upper_value:
            return True
        if lower_value == upper_value and not (lower[1] and upper[1]):
            return True
    return False


def _guards_disjoint(
    registry: Mapping[str, Entry],
    left: Trigger,
    right: Trigger,
) -> bool:
    if left.given is True or right.given is True:
        return False
    left_atoms = _guard_atoms(registry, left, left.given)
    right_atoms = _guard_atoms(registry, right, right.given)
    if left_atoms is None or right_atoms is None:
        return False
    return _atoms_conflict(left_atoms, right_atoms)


def _validate_triggers(
    registry: Mapping[str, Entry],
    triggers: list[Trigger],
) -> None:
    by_when: dict[str, list[Trigger]] = defaultdict(list)
    for trigger in triggers:
        process = _target(registry, trigger, trigger.then, Process)
        for binding in trigger.inputs:
            _validate_value(registry, trigger, binding.value)
        if process is not None:
            input_schema = _process_schema(registry, process, process.input)
            if process.input is None or input_schema is not None:
                validate_trigger_contract(
                    trigger,
                    None if input_schema is None else input_schema.placeholders,
                )
        if trigger.given is not True:
            _validate_condition(registry, trigger, trigger.given)
        by_when[trigger.when].append(trigger)
    for when, group in by_when.items():
        for left, right in combinations(group, 2):
            if not _guards_disjoint(registry, left, right):
                raise PydanticCustomError(
                    "overlapping_trigger_guards",
                    (
                        "triggers {left} and {right} share WHEN {when} "
                        "without provably disjoint guards"
                    ),
                    {"left": left.id, "right": right.id, "when": when},
                )


def _walk_steps(
    steps: list[Step],
    *,
    parallel: bool = False,
) -> Iterator[tuple[Step, bool]]:
    for step in steps:
        yield step, parallel
        if isinstance(step, If):
            yield from _walk_steps(step.then, parallel=parallel)
            if step.otherwise is not None:
                yield from _walk_steps(step.otherwise, parallel=parallel)
        elif isinstance(step, Foreach):
            yield from _walk_steps(step.steps, parallel=parallel)
        elif isinstance(step, While):
            yield from _walk_steps(step.steps, parallel=parallel)
        elif isinstance(step, Par):
            yield from _walk_steps(step.steps, parallel=True)


def validate_tools(
    node: Node,
    tools: Mapping[str, ToolContractLike],
) -> None:
    """Validate exact tool names, contracts, and parallel permission."""
    for process in node.processes:
        for step, parallel in _walk_steps(process.steps):
            if not isinstance(step, Act) or step.tool is None:
                continue
            contract = tools.get(step.tool)
            if contract is None:
                raise PydanticCustomError(
                    "unknown_tool",
                    "process {process} names unknown tool {tool}",
                    {"process": process.id, "tool": step.tool},
                )
            authored_inputs = frozenset(binding.placeholder for binding in step.inputs)
            authored_outputs = frozenset(step.outputs)
            if (
                authored_inputs != contract.inputs
                or authored_outputs != contract.outputs
                or step.input != contract.input
                or step.output != contract.output
            ):
                raise PydanticCustomError(
                    "tool_contract_mismatch",
                    "process {process} act contract differs from tool {tool}",
                    {"process": process.id, "tool": step.tool},
                )
            if parallel and not contract.parallel:
                raise PydanticCustomError(
                    "tool_parallelism_unknown",
                    "process {process} uses tool {tool} in PAR without parallel permission",
                    {"process": process.id, "tool": step.tool},
                )


def validate_graph(node: Node) -> None:
    """Reject invalid ids, local references, guards, and process flow."""
    registry = entry_registry(node)
    for interface in node.interfaces:
        _interface_schema(registry, interface)
    _validate_typed_entries(registry, node)
    for process in node.processes:
        _validate_process_contract(registry, process)
    _validate_triggers(registry, node.triggers)
    for process in node.processes:
        _validate_steps(registry, process, process.steps)
    _validate_call_graph(node.processes)
