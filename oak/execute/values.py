"""Runtime value resolution, condition evaluation, and schema checks."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy

from pydantic import JsonValue

from oak.execute.context import ExecutionContext, ProcessFrame
from oak.execute.models import ExecutionError
from oak.node.parts.constants import Constant
from oak.node.parts.processes.conditions import All, Any, Compare, Condition, Not
from oak.node.parts.processes.operators import (
    OrderedComparisonTypeError,
    compare_values,
)
from oak.node.parts.processes.values import (
    BindingValue,
    ConstantValue,
    LiteralValue,
    StateValue,
    Value,
)
from oak.node.parts.schemas.binding import SchemaBindingError
from oak.node.parts.schemas.model import Schema
from oak.node.parts.state import State
from oak.vocabulary.text.target_path import target_id


def _constant_value(context: ExecutionContext, frame: ProcessFrame, value: ConstantValue) -> JsonValue:
    _target_document, constant = context.graph.entry(frame.document, value.constant, Constant)
    return deepcopy(constant.value)


def _state_value(context: ExecutionContext, frame: ProcessFrame, value: StateValue) -> JsonValue:
    identifier = target_id(value.state)
    key = context.graph.display_target(frame.document, "state", identifier)

    if key not in context.state:
        raise ExecutionError("missing_state_value", f"state {key} is absent")

    return deepcopy(context.state[key])


def _binding_value(frame: ProcessFrame, value: BindingValue) -> JsonValue:
    if value.binding not in frame.bindings:
        raise ExecutionError("missing_process_binding", f"binding {value.binding} is absent")

    return deepcopy(frame.bindings[value.binding])


def resolve_value(context: ExecutionContext, frame: ProcessFrame, value: Value) -> JsonValue:
    """Resolve one process value in the current transaction and frame."""
    match value:
        case LiteralValue():
            return deepcopy(value.value)

        case ConstantValue():
            return _constant_value(context, frame, value)

        case StateValue():
            return _state_value(context, frame, value)

        case BindingValue():
            return _binding_value(frame, value)

    raise TypeError(type(value).__name__)


def _compare(context: ExecutionContext, frame: ProcessFrame, condition: Compare) -> bool:
    left = resolve_value(context, frame, condition.left)
    right = resolve_value(context, frame, condition.right)

    try:
        return compare_values(condition.operator, left, right)

    except OrderedComparisonTypeError as error:
        raise ExecutionError("ordered_comparison_type_mismatch", str(error)) from None


def evaluate_condition(context: ExecutionContext, frame: ProcessFrame, condition: Condition) -> bool:
    """Evaluate one recursive condition with authored short-circuit order."""
    match condition:
        case Compare():
            return _compare(context, frame, condition)

        case All():
            return all(evaluate_condition(context, frame, child) for child in condition.conditions)

        case Any():
            return any(evaluate_condition(context, frame, child) for child in condition.conditions)

        case Not():
            return not evaluate_condition(context, frame, condition.condition)

    raise TypeError(type(condition).__name__)


def resolved_schema(context: ExecutionContext, document: str, target: str | None) -> Schema | None:
    """Return one resolved optional schema."""
    if target is None:
        return None

    _schema_document, schema = context.graph.entry(document, target, Schema)
    return schema


def validate_schema_values(
    context: ExecutionContext,
    document: str,
    target: str | None,
    values: Mapping[str, JsonValue],
    code: str,
) -> None:
    """Validate one binding mapping against one optional schema."""
    schema = resolved_schema(context, document, target)

    if schema is None:
        return

    try:
        schema.bind(values)

    except SchemaBindingError as error:
        raise ExecutionError(code, f"{target}: {error}") from None


def validate_state_value(
    context: ExecutionContext,
    document: str,
    entry: State,
    value: JsonValue,
    key: str,
) -> None:
    """Validate one state value against its optional schema binding."""
    schema = resolved_schema(context, document, entry.schema_id)

    if schema is None or entry.placeholder is None:
        return

    try:
        schema.bind_value(entry.placeholder, value)

    except SchemaBindingError as error:
        raise ExecutionError("invalid_state_value", f"state {key}: {error}") from None


__all__ = [
    "evaluate_condition",
    "resolve_value",
    "resolved_schema",
    "validate_schema_values",
    "validate_state_value",
]
