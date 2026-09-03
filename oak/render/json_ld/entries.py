"""JSON-LD schema, step, and OAK entry encoding."""

from __future__ import annotations

from oak.node.parts.constants import Constant
from oak.node.parts.entry import Entry
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
from oak.node.parts.schemas.model import Schema, Where
from oak.node.parts.state import State
from oak.node.parts.triggers import Trigger
from oak.render.json_ld.identifiers import entry_id, target_id, where_id
from oak.render.json_ld.values import (
    binding_node,
    condition_node,
    constraint_node,
    json_literal,
    value_node,
)

Fields = dict[str, object]

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



def _target_reference(document: str, target: str) -> Fields:
    return {"@id": target_id(document, target)}


def where_node(document: str, schema: Schema, where: Where) -> Fields:
    """Return one schema Where node."""
    node: Fields = {
        "@id": where_id(document, schema, where.placeholder),
        "@type": "oak:Where",
        "placeholder": where.placeholder,
        "constraints": [
            constraint_node(document, schema, constraint)
            for constraint in where.constraints
        ],
    }

    if where.examples:
        node["examples"] = list(where.examples)

    if where.description is not None:
        node["description"] = where.description

    return node


def schema_node(document: str, schema: Schema) -> Fields:
    """Return one schema entry node."""
    node: Fields = {
        "@id": entry_id(document, "schema", schema.id),
        "@type": "oak:Schema",
        "template": schema.template,
        "where": [where_node(document, schema, where) for where in schema.where],
    }

    if schema.name is not None:
        node["name"] = schema.name

    if schema.purpose is not None:
        node["purpose"] = schema.purpose

    return node


def _act_fields(document: str, step: Act) -> Fields:
    fields: Fields = {"instruction": step.instruction}

    if step.tool is not None:
        fields["tool"] = step.tool

    if step.input is not None:
        fields["input"] = _target_reference(document, step.input)

    if step.output is not None:
        fields["output"] = _target_reference(document, step.output)

    fields["inputs"] = [binding_node(document, binding) for binding in step.inputs]
    fields["outputs"] = list(step.outputs)
    return fields


def _if_fields(document: str, step: If) -> Fields:
    fields: Fields = {
        "condition": condition_node(document, step.condition),
        "thenSteps": [step_node(document, child) for child in step.then],
    }

    if step.otherwise is not None:
        fields["otherwise"] = [step_node(document, child) for child in step.otherwise]

    return fields


def _assert_fields(document: str, step: Assert) -> Fields:
    fields: Fields = {"condition": condition_node(document, step.condition)}

    if step.message is not None:
        fields["message"] = step.message

    return fields


def _step_fields(document: str, step: Step) -> Fields:
    match step:
        case Act():
            return _act_fields(document, step)

        case Set():
            return {
                "stateTarget": _target_reference(document, step.state),
                "value": value_node(document, step.value),
            }

        case Emit():
            return {
                "interface": _target_reference(document, step.interface),
                "bindings": [binding_node(document, binding) for binding in step.bindings],
            }

        case If():
            return _if_fields(document, step)

        case Call():
            return {
                "process": _target_reference(document, step.process),
                "inputs": [binding_node(document, binding) for binding in step.inputs],
                "outputs": list(step.outputs),
            }

        case Fail():
            return {"message": step.message}

        case Assert():
            return _assert_fields(document, step)

        case Foreach():
            return {
                "loopBinding": step.binding,
                "value": value_node(document, step.value),
                "steps": [step_node(document, child) for child in step.steps],
            }

        case While():
            return {
                "condition": condition_node(document, step.condition),
                "limit": step.limit,
                "steps": [step_node(document, child) for child in step.steps],
            }

        case Par():
            return {"steps": [step_node(document, child) for child in step.steps]}

        case Join():
            return {}

    raise TypeError(type(step).__name__)


def step_node(document: str, step: Step) -> Fields:
    """Return one typed process step node."""
    return {
        "@type": "oak:" + _STEP_TYPES[step.kind],
        **_step_fields(document, step),
    }


def _instruction_node(document: str, entry: Instruction) -> Fields:
    return {
        "@id": entry_id(document, "instruction", entry.id),
        "@type": "oak:Instruction",
        "body": entry.body,
    }


def _constant_node(document: str, entry: Constant) -> Fields:
    node: Fields = {
        "@id": entry_id(document, "constant", entry.id),
        "@type": "oak:Constant",
        "form": entry.form,
        "value": json_literal(entry.value),
    }

    if entry.schema_id is not None:
        node["schema"] = _target_reference(document, entry.schema_id)
        node["placeholder"] = entry.placeholder

    return node


def _state_node(document: str, entry: State) -> Fields:
    node: Fields = {
        "@id": entry_id(document, "state", entry.id),
        "@type": "oak:State",
        "value": json_literal(entry.value),
    }

    if entry.schema_id is not None:
        node["schema"] = _target_reference(document, entry.schema_id)
        node["placeholder"] = entry.placeholder

    return node


def _trigger_node(document: str, entry: Trigger) -> Fields:
    node: Fields = {
        "@id": entry_id(document, "trigger", entry.id),
        "@type": "oak:Trigger",
        "event": entry.event,
    }

    if entry.source is not None:
        node["source"] = _target_reference(document, entry.source)

    if entry.guard is not True:
        node["guard"] = condition_node(document, entry.guard)

    node["process"] = _target_reference(document, entry.process)

    if entry.seed:
        node["seed"] = [binding_node(document, binding) for binding in entry.seed]

    return node


def _process_node(document: str, entry: Process) -> Fields:
    node: Fields = {
        "@id": entry_id(document, "process", entry.id),
        "@type": "oak:Process",
        "name": entry.name,
        "steps": [step_node(document, step) for step in entry.steps],
    }

    if entry.input is not None:
        node["input"] = _target_reference(document, entry.input)

    if entry.output is not None:
        node["output"] = _target_reference(document, entry.output)

    return node


def _interface_node(document: str, entry: Interface) -> Fields:
    node: Fields = {
        "@id": entry_id(document, "interface", entry.id),
        "@type": "oak:Interface",
        "direction": entry.direction,
        "schema": _target_reference(document, entry.schema_id),
    }

    if entry.description is not None:
        node["description"] = entry.description

    return node


def entry_node(document: str, entry: Entry) -> Fields:
    """Return one OAK entry node."""
    match entry:
        case Instruction():
            return _instruction_node(document, entry)

        case Constant():
            return _constant_node(document, entry)

        case Schema():
            return schema_node(document, entry)

        case State():
            return _state_node(document, entry)

        case Trigger():
            return _trigger_node(document, entry)

        case Process():
            return _process_node(document, entry)

        case Interface():
            return _interface_node(document, entry)

    raise TypeError(type(entry).__name__)


__all__ = [
    "entry_node",
    "schema_node",
    "step_node",
    "where_node",
]
