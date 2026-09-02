"""Local process values, typed entries, and interface direction checks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic_core import PydanticCustomError

from oak.base import Entry
from oak.node.index import NodeIndex
from oak.node.parts.constants import Constant
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.values import (
    ConstantValue,
    InterfaceValue,
    LiteralValue,
    StateValue,
    Value,
)
from oak.node.parts.schemas.binding import SchemaBindingError
from oak.node.parts.schemas.model import Schema
from oak.node.parts.state import State
from oak.rules import rule_error

if TYPE_CHECKING:
    from oak.node.model import Node

STATIC_MISSING = object()


def interface_schema(
    index: NodeIndex,
    interface: Interface,
) -> Schema | None:
    """Return one local interface schema, or null for a relative schema."""
    return index.require(
        interface,
        interface.schema_id,
        Schema,
    )


def process_schema(
    index: NodeIndex,
    process: Process,
    target: str | None,
) -> Schema | None:
    """Return one local process schema, or null when absent or relative."""
    if target is None:
        return None

    return index.require(
        process,
        target,
        Schema,
    )


def direction_error(
    process: Process,
    action: str,
    interface: Interface,
) -> None:
    """Raise the stable process interface-direction error."""
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


def validate_value(
    index: NodeIndex,
    source: Entry,
    value: Value,
) -> None:
    """Validate one process value's local target and interface contract."""
    if isinstance(value, ConstantValue):
        index.require(
            source,
            value.constant,
            Constant,
        )
        return

    if isinstance(value, StateValue):
        index.require(
            source,
            value.state,
            State,
        )
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

    interface = index.require(
        source,
        value.interface,
        Interface,
    )

    if interface is None:
        return

    if interface.direction not in ("in", "inout"):
        if isinstance(source, Process):
            direction_error(
                source,
                "read",
                interface,
            )

        raise PydanticCustomError(
            "interface_direction_mismatch",
            "{source} cannot read interface {interface} with direction {direction}",
            {
                "source": source.id,
                "interface": interface.id,
                "direction": interface.direction,
            },
        )

    schema = interface_schema(
        index,
        interface,
    )

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


def static_value(
    index: NodeIndex,
    source: Entry,
    value: Value,
) -> object:
    """Return one statically known literal or constant value."""
    if isinstance(value, LiteralValue):
        return value.value

    if isinstance(value, ConstantValue):
        constant = index.require(
            source,
            value.constant,
            Constant,
        )
        return (
            constant.value
            if constant is not None
            else STATIC_MISSING
        )

    return STATIC_MISSING


def validate_typed_value(
    entry: Constant | State,
    schema: Schema,
) -> None:
    """Validate one AS-bound entry value against its resolved schema."""
    if entry.placeholder is None:
        return

    source_type = type(entry).__name__.lower()

    try:
        schema.bind_value(
            entry.placeholder,
            entry.value,
        )

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


def validate_typed_entries(
    index: NodeIndex,
    node: Node,
) -> None:
    """Validate every local schema-bound constant and state entry."""
    for entry in (*node.constants, *node.state):
        if entry.schema_id is None:
            continue

        schema = index.require(
            entry,
            entry.schema_id,
            Schema,
        )

        if schema is not None:
            validate_typed_value(
                entry,
                schema,
            )


__all__ = [
    "STATIC_MISSING",
    "direction_error",
    "interface_schema",
    "process_schema",
    "static_value",
    "validate_typed_entries",
    "validate_typed_value",
    "validate_value",
]
