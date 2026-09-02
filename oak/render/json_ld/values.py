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
from oak.node.parts.schemas.constraints import (
    AtLeast,
    AtMost,
    Constraint,
)
from oak.node.parts.schemas.model import Schema
from oak.render.json_ld.identifiers import (
    target_id,
    where_id,
)

_CONSTRAINT_TYPES = {
    "type": "Type",
    "one_of": "OneOf",
    "regex": "Regex",
    "non_empty": "NonEmpty",
    "max_chars": "MaxChars",
    "lines": "Lines",
    "list_of": "ListOf",
    "at_least": "AtLeast",
    "at_most": "AtMost",
}
_VALUE_TYPES = {
    "literal": "LiteralValue",
    "constant": "ConstantValue",
    "state": "StateValue",
    "interface": "InterfaceValue",
    "binding": "BindingValue",
}
_CONDITION_TYPES = {
    "compare": "Compare",
    "all": "All",
    "any": "Any",
    "not": "Not",
}


def json_literal(
    value: object,
) -> dict[str, object]:
    """Return one JSON-LD JSON literal."""
    return {
        "@value": value,
        "@type": "@json",
    }


def constraint_node(
    document: str,
    schema: Schema,
    constraint: Constraint,
) -> dict[str, object]:
    """Return one schema constraint node."""
    fields = constraint.model_dump(
        mode="json",
        exclude={"kind"},
        exclude_unset=True,
    )

    if (
        isinstance(
            constraint,
            (
                AtLeast,
                AtMost,
            ),
        )
        and isinstance(
            constraint.value,
            str,
        )
    ):
        fields["value"] = {
            "@id": where_id(
                document,
                schema,
                constraint.value,
            )
        }

    return {
        "@type": (
            "oak:"
            + _CONSTRAINT_TYPES[
                constraint.kind
            ]
        ),
        **fields,
    }


def value_node(
    document: str,
    value: Value,
) -> dict[str, object]:
    """Return one process value node."""
    node: dict[str, object] = {
        "@type": (
            "oak:"
            + _VALUE_TYPES[
                value.source
            ]
        )
    }

    if isinstance(
        value,
        LiteralValue,
    ):
        node["value"] = json_literal(
            value.value
        )

    elif isinstance(
        value,
        ConstantValue,
    ):
        node["constant"] = {
            "@id": target_id(
                document,
                value.constant,
            )
        }

    elif isinstance(
        value,
        StateValue,
    ):
        node["stateTarget"] = {
            "@id": target_id(
                document,
                value.state,
            )
        }

    elif isinstance(
        value,
        InterfaceValue,
    ):
        node["interface"] = {
            "@id": target_id(
                document,
                value.interface,
            )
        }
        node["placeholder"] = (
            value.placeholder
        )

    elif isinstance(
        value,
        BindingValue,
    ):
        node["binding"] = (
            value.binding
        )

    else:
        raise TypeError(
            type(value).__name__
        )

    return node


def binding_node(
    document: str,
    binding: ValueBinding,
) -> dict[str, object]:
    """Return one process value binding node."""
    return {
        "@type": "oak:ValueBinding",
        "placeholder": (
            binding.placeholder
        ),
        "value": value_node(
            document,
            binding.value,
        ),
    }


def condition_node(
    document: str,
    condition: Condition,
) -> dict[str, object]:
    """Return one recursive condition node."""
    node: dict[str, object] = {
        "@type": (
            "oak:"
            + _CONDITION_TYPES[
                condition.kind
            ]
        )
    }

    if isinstance(
        condition,
        Compare,
    ):
        node.update(
            left=value_node(
                document,
                condition.left,
            ),
            operator=condition.operator,
            right=value_node(
                document,
                condition.right,
            ),
        )

    elif isinstance(
        condition,
        (
            All,
            Any,
        ),
    ):
        node["conditions"] = [
            condition_node(
                document,
                child,
            )
            for child in condition.conditions
        ]

    elif isinstance(
        condition,
        Not,
    ):
        node["condition"] = (
            condition_node(
                document,
                condition.condition,
            )
        )

    else:
        raise TypeError(
            type(condition).__name__
        )

    return node


__all__ = [
    "binding_node",
    "condition_node",
    "constraint_node",
    "json_literal",
    "value_node",
]
