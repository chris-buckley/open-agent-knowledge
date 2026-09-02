"""JSON-LD literals, constraints, values, bindings, and conditions."""

from __future__ import annotations

from oak.node.parts.processes.conditions import (
    All,
    Any,
    Compare,
    Condition,
    Not,
)
from oak.node.parts.processes.values import (
    BindingValue,
    ConstantValue,
    InterfaceValue,
    LiteralValue,
    StateValue,
    Value,
    ValueBinding,
)
from oak.node.parts.schemas.constraints import AtLeast, AtMost, Constraint
from oak.node.parts.schemas.model import Schema
from oak.render.json_ld.identifiers import target_id, where_id

Fields = dict[str, object]


def _oak_type(model: object) -> str:
    return f"oak:{type(model).__name__}"


def json_literal(value: object) -> Fields:
    """Return one JSON-LD JSON literal."""
    return {"@value": value, "@type": "@json"}


def constraint_node(document: str, schema: Schema, constraint: Constraint) -> Fields:
    """Return one schema constraint node."""
    fields = constraint.model_dump(mode="json", exclude={"kind"}, exclude_unset=True)

    if isinstance(constraint, (AtLeast, AtMost)) and isinstance(constraint.value, str):
        fields["value"] = {"@id": where_id(document, schema, constraint.value)}

    return {"@type": _oak_type(constraint), **fields}


def _value_fields(document: str, value: Value) -> Fields:
    match value:
        case LiteralValue():
            return {"value": json_literal(value.value)}

        case ConstantValue():
            return {"constant": {"@id": target_id(document, value.constant)}}

        case StateValue():
            return {"stateTarget": {"@id": target_id(document, value.state)}}

        case InterfaceValue():
            return {
                "interface": {"@id": target_id(document, value.interface)},
                "placeholder": value.placeholder,
            }

        case BindingValue():
            return {"binding": value.binding}

    raise TypeError(type(value).__name__)


def value_node(document: str, value: Value) -> Fields:
    """Return one process value node."""
    return {"@type": _oak_type(value), **_value_fields(document, value)}


def binding_node(document: str, binding: ValueBinding) -> Fields:
    """Return one process value binding node."""
    return {
        "@type": _oak_type(binding),
        "placeholder": binding.placeholder,
        "value": value_node(document, binding.value),
    }


def _condition_fields(document: str, condition: Condition) -> Fields:
    match condition:
        case Compare():
            return {
                "left": value_node(document, condition.left),
                "operator": condition.operator,
                "right": value_node(document, condition.right),
            }

        case All() | Any():
            return {
                "conditions": [
                    condition_node(document, child) for child in condition.conditions
                ],
            }

        case Not():
            return {"condition": condition_node(document, condition.condition)}

    raise TypeError(type(condition).__name__)


def condition_node(document: str, condition: Condition) -> Fields:
    """Return one recursive condition node."""
    return {"@type": _oak_type(condition), **_condition_fields(document, condition)}


__all__ = [
    "binding_node",
    "condition_node",
    "constraint_node",
    "json_literal",
    "value_node",
]
