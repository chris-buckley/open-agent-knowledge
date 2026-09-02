"""JSON-LD schema, step, and OAK entry encoding."""

from __future__ import annotations

from oak.base import Entry
from oak.node.parts.constants import Constant
from oak.node.parts.instructions import Instruction
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.steps import (
    Act,
    Assert,
    Call,
    Emit,
    Fail,
    Foreach,
    If,
    Join,
    Par,
    Set,
    Step,
    While,
)
from oak.node.parts.schemas.model import (
    Schema,
    Where,
)
from oak.node.parts.state import State
from oak.node.parts.triggers import Trigger
from oak.render.json_ld.identifiers import (
    entry_id,
    target_id,
    where_id,
)
from oak.render.json_ld.values import (
    binding_node,
    condition_node,
    constraint_node,
    json_literal,
    value_node,
)

_STEP_TYPES = {
    "act": "Act",
    "set": "Set",
    "emit": "Emit",
    "if": "If",
    "call": "Call",
    "fail": "Fail",
    "assert": "Assert",
    "foreach": "Foreach",
    "while": "While",
    "par": "Par",
    "join": "Join",
}


def where_node(
    document: str,
    schema: Schema,
    item: Where,
) -> dict[str, object]:
    """Return one schema Where node."""
    node: dict[str, object] = {
        "@id": where_id(
            document,
            schema,
            item.placeholder,
        ),
        "@type": "oak:Where",
        "placeholder": item.placeholder,
        "constraints": [
            constraint_node(
                document,
                schema,
                constraint,
            )
            for constraint in item.constraints
        ],
    }

    if item.examples:
        node["examples"] = list(
            item.examples
        )

    if item.description is not None:
        node["description"] = (
            item.description
        )

    return node


def schema_node(
    document: str,
    schema: Schema,
) -> dict[str, object]:
    """Return one schema entry node."""
    node: dict[str, object] = {
        "@id": entry_id(
            document,
            "schema",
            schema.id,
        ),
        "@type": "oak:Schema",
        "template": schema.template,
        "where": [
            where_node(
                document,
                schema,
                item,
            )
            for item in schema.where
        ],
    }

    if schema.name is not None:
        node["name"] = schema.name

    if schema.purpose is not None:
        node["purpose"] = (
            schema.purpose
        )

    return node


def step_node(
    document: str,
    step: Step,
) -> dict[str, object]:
    """Return one typed process step node."""
    node: dict[str, object] = {
        "@type": (
            "oak:"
            + _STEP_TYPES[
                step.kind
            ]
        )
    }

    if isinstance(
        step,
        Act,
    ):
        node["instruction"] = (
            step.instruction
        )

        if step.tool is not None:
            node["tool"] = step.tool

        if step.input is not None:
            node["input"] = {
                "@id": target_id(
                    document,
                    step.input,
                )
            }

        if step.output is not None:
            node["output"] = {
                "@id": target_id(
                    document,
                    step.output,
                )
            }

        node["inputs"] = [
            binding_node(
                document,
                binding,
            )
            for binding in step.inputs
        ]
        node["outputs"] = list(
            step.outputs
        )

    elif isinstance(
        step,
        Set,
    ):
        node["stateTarget"] = {
            "@id": target_id(
                document,
                step.state,
            )
        }
        node["value"] = value_node(
            document,
            step.value,
        )

    elif isinstance(
        step,
        Emit,
    ):
        node["interface"] = {
            "@id": target_id(
                document,
                step.interface,
            )
        }
        node["bindings"] = [
            binding_node(
                document,
                binding,
            )
            for binding in step.bindings
        ]

    elif isinstance(
        step,
        If,
    ):
        node["condition"] = (
            condition_node(
                document,
                step.condition,
            )
        )
        node["thenSteps"] = [
            step_node(
                document,
                child,
            )
            for child in step.then
        ]

        if step.otherwise is not None:
            node["otherwise"] = [
                step_node(
                    document,
                    child,
                )
                for child in step.otherwise
            ]

    elif isinstance(
        step,
        Call,
    ):
        node["process"] = {
            "@id": target_id(
                document,
                step.process,
            )
        }
        node["inputs"] = [
            binding_node(
                document,
                binding,
            )
            for binding in step.inputs
        ]
        node["outputs"] = list(
            step.outputs
        )

    elif isinstance(
        step,
        Fail,
    ):
        node["message"] = step.message

    elif isinstance(
        step,
        Assert,
    ):
        node["condition"] = (
            condition_node(
                document,
                step.condition,
            )
        )

        if step.message is not None:
            node["message"] = (
                step.message
            )

    elif isinstance(
        step,
        Foreach,
    ):
        node["loopBinding"] = (
            step.binding
        )
        node["value"] = value_node(
            document,
            step.value,
        )
        node["steps"] = [
            step_node(
                document,
                child,
            )
            for child in step.steps
        ]

    elif isinstance(
        step,
        While,
    ):
        node["condition"] = (
            condition_node(
                document,
                step.condition,
            )
        )
        node["limit"] = step.limit
        node["steps"] = [
            step_node(
                document,
                child,
            )
            for child in step.steps
        ]

    elif isinstance(
        step,
        Par,
    ):
        node["steps"] = [
            step_node(
                document,
                child,
            )
            for child in step.steps
        ]

    elif isinstance(
        step,
        Join,
    ):
        pass

    else:
        raise TypeError(
            type(step).__name__
        )

    return node


def entry_node(
    document: str,
    entry: Entry,
) -> dict[str, object]:
    """Return one OAK entry node."""
    if isinstance(
        entry,
        Instruction,
    ):
        return {
            "@id": entry_id(
                document,
                "instruction",
                entry.id,
            ),
            "@type": "oak:Instruction",
            "body": entry.body,
        }

    if isinstance(
        entry,
        Constant,
    ):
        node: dict[str, object] = {
            "@id": entry_id(
                document,
                "constant",
                entry.id,
            ),
            "@type": "oak:Constant",
            "form": entry.form,
            "value": json_literal(
                entry.value
            ),
        }

        if entry.schema_id is not None:
            node["schema"] = {
                "@id": target_id(
                    document,
                    entry.schema_id,
                )
            }
            node["placeholder"] = (
                entry.placeholder
            )

        return node

    if isinstance(
        entry,
        Schema,
    ):
        return schema_node(
            document,
            entry,
        )

    if isinstance(
        entry,
        State,
    ):
        node = {
            "@id": entry_id(
                document,
                "state",
                entry.id,
            ),
            "@type": "oak:State",
            "value": json_literal(
                entry.value
            ),
        }

        if entry.schema_id is not None:
            node["schema"] = {
                "@id": target_id(
                    document,
                    entry.schema_id,
                )
            }
            node["placeholder"] = (
                entry.placeholder
            )

        return node

    if isinstance(
        entry,
        Trigger,
    ):
        node = {
            "@id": entry_id(
                document,
                "trigger",
                entry.id,
            ),
            "@type": "oak:Trigger",
            "event": entry.event,
        }

        if entry.source is not None:
            node["source"] = {
                "@id": target_id(
                    document,
                    entry.source,
                )
            }

        if entry.guard is not True:
            node["guard"] = (
                condition_node(
                    document,
                    entry.guard,
                )
            )

        node["process"] = {
            "@id": target_id(
                document,
                entry.process,
            )
        }

        if entry.seed:
            node["seed"] = [
                binding_node(
                    document,
                    binding,
                )
                for binding in entry.seed
            ]

        return node

    if isinstance(
        entry,
        Process,
    ):
        node = {
            "@id": entry_id(
                document,
                "process",
                entry.id,
            ),
            "@type": "oak:Process",
            "name": entry.name,
            "steps": [
                step_node(
                    document,
                    step,
                )
                for step in entry.steps
            ],
        }

        if entry.input is not None:
            node["input"] = {
                "@id": target_id(
                    document,
                    entry.input,
                )
            }

        if entry.output is not None:
            node["output"] = {
                "@id": target_id(
                    document,
                    entry.output,
                )
            }

        return node

    if isinstance(
        entry,
        Interface,
    ):
        node = {
            "@id": entry_id(
                document,
                "interface",
                entry.id,
            ),
            "@type": "oak:Interface",
            "direction": entry.direction,
            "schema": {
                "@id": target_id(
                    document,
                    entry.schema_id,
                )
            },
        }

        if entry.description is not None:
            node["description"] = (
                entry.description
            )

        return node

    raise TypeError(
        type(entry).__name__
    )


__all__ = [
    "entry_node",
    "schema_node",
    "step_node",
    "where_node",
]
