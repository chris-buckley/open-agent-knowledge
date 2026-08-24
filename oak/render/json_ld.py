"""The compact JSON-LD interchange render with one root context."""

from typing import Annotated

from pydantic import (
    ConfigDict,
    StringConstraints,
    TypeAdapter,
)
from pydantic_core import PydanticCustomError

from oak.base import Entry
from oak.node.model import Node, Root
from oak.node.parts import (
    Act,
    AtLeast,
    AtMost,
    BindingValue,
    Call,
    Condition,
    Constant,
    ConstantValue,
    Emit,
    Fail,
    If,
    Instruction,
    Interface,
    InterfaceValue,
    LiteralValue,
    Process,
    Schema,
    Set,
    State,
    StateValue,
    Step,
    Trigger,
    Value,
    ValueBinding,
    Where,
)

AbsoluteIri = Annotated[
    str,
    StringConstraints(
        pattern=r"^[A-Za-z][A-Za-z0-9+.\-]*:[^ \t\r\n]+$"
    ),
]

_IRI_ADAPTER = TypeAdapter(
    AbsoluteIri,
    config=ConfigDict(
        strict=True,
        regex_engine="rust-regex",
    ),
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

_STEP_TYPES = {
    "act": "Act",
    "set": "Set",
    "emit": "Emit",
    "if": "If",
    "call": "Call",
    "fail": "Fail",
}


def _absolute_iri(value: str) -> str:
    return _IRI_ADAPTER.validate_python(value)


def _base(value: str) -> str:
    base = _absolute_iri(value)
    if not base.endswith("/"):
        raise PydanticCustomError(
            "invalid_json_ld_base",
            "JSON-LD base must end with /",
        )
    return base


def _vocabulary(value: str) -> str:
    vocabulary = _absolute_iri(value)
    if not vocabulary.endswith(("#", "/", ":")):
        raise PydanticCustomError(
            "invalid_json_ld_vocabulary",
            "JSON-LD vocabulary must end with #, /, or :",
        )
    return vocabulary


def _context(
    base: str,
    vocabulary: str,
) -> dict[str, object]:
    return {
        "@base": base,
        "oak": {
            "@id": vocabulary,
            "@prefix": True,
        },
        "xsd": {
            "@id": "http://www.w3.org/2001/XMLSchema#",
            "@prefix": True,
        },
        "name": "oak:name",
        "purpose": "oak:purpose",
        "body": "oak:body",
        "when": "oak:when",
        "given": "oak:given",
        "process": {
            "@id": "oak:process",
            "@type": "@id",
        },
        "value": "oak:value",
        "template": {
            "@id": "oak:template",
            "@type": "xsd:string",
        },
        "where": {
            "@id": "oak:where",
            "@container": "@list",
        },
        "placeholder": {
            "@id": "oak:placeholder",
            "@type": "xsd:string",
        },
        "constraints": {
            "@id": "oak:constraint",
            "@container": "@list",
        },
        "examples": {
            "@id": "oak:example",
            "@container": "@list",
        },
        "description": "oak:description",
        "direction": "oak:direction",
        "schema": {
            "@id": "oak:schema",
            "@type": "@id",
        },
        "of": "oak:of",
        "values": {
            "@id": "oak:values",
            "@container": "@list",
        },
        "pattern": "oak:pattern",
        "n": "oak:n",
        "item": "oak:item",
        "separator": "oak:separator",
        "min": "oak:min",
        "max": "oak:max",
        "instruction": "oak:instruction",
        "inputs": {
            "@id": "oak:inputs",
            "@container": "@list",
        },
        "outputs": {
            "@id": "oak:outputs",
            "@container": "@list",
        },
        "bindings": {
            "@id": "oak:bindings",
            "@container": "@list",
        },
        "condition": "oak:condition",
        "left": "oak:left",
        "operator": "oak:operator",
        "right": "oak:right",
        "then": {
            "@id": "oak:then",
            "@container": "@list",
        },
        "otherwise": {
            "@id": "oak:otherwise",
            "@container": "@list",
        },
        "message": "oak:message",
        "constant": {
            "@id": "oak:constant",
            "@type": "@id",
        },
        "state": {
            "@id": "oak:state",
            "@type": "@id",
        },
        "interface": {
            "@id": "oak:interface",
            "@type": "@id",
        },
        "binding": {
            "@id": "oak:binding",
            "@type": "xsd:string",
        },
        "steps": {
            "@id": "oak:steps",
            "@container": "@list",
        },
        "instructions": {
            "@id": "oak:instructions",
            "@container": "@list",
        },
        "constants": {
            "@id": "oak:constants",
            "@container": "@list",
        },
        "schemas": {
            "@id": "oak:schemas",
            "@container": "@list",
        },
        "triggers": {
            "@id": "oak:triggers",
            "@container": "@list",
        },
        "processes": {
            "@id": "oak:processes",
            "@container": "@list",
        },
        "interfaces": {
            "@id": "oak:interfaces",
            "@container": "@list",
        },
        "children": {
            "@id": "oak:children",
            "@container": "@list",
        },
    }


def where_id(
    schema: Schema,
    placeholder: str,
) -> str:
    """Return the relative id for one Where."""
    return f"{schema.id}/where/{placeholder}"


def _constraint(
    schema: Schema,
    constraint: object,
) -> dict[str, object]:
    data = constraint.model_dump(
        mode="json",
        exclude={"kind"},
        exclude_unset=True,
    )

    if (
        isinstance(constraint, (AtLeast, AtMost))
        and isinstance(constraint.value, str)
    ):
        data["value"] = {
            "@id": where_id(
                schema,
                constraint.value,
            )
        }

    return {
        "@type": f"oak:{_CONSTRAINT_TYPES[constraint.kind]}",
        **data,
    }


def _where(
    schema: Schema,
    where: Where,
) -> dict[str, object]:
    node: dict[str, object] = {
        "@id": where_id(
            schema,
            where.placeholder,
        ),
        "@type": "oak:Where",
        "placeholder": where.placeholder,
        "constraints": [
            _constraint(schema, constraint)
            for constraint in where.constraints
        ],
    }

    if where.examples:
        node["examples"] = list(where.examples)

    if where.description is not None:
        node["description"] = where.description

    return node


def _schema(schema: Schema) -> dict[str, object]:
    node: dict[str, object] = {
        "@id": schema.id,
        "@type": "oak:Schema",
        "template": schema.template,
        "where": [
            _where(schema, item)
            for item in schema.where
        ],
    }

    if schema.name is not None:
        node["name"] = schema.name

    if schema.purpose is not None:
        node["purpose"] = schema.purpose

    return node


def _json_literal(value: object) -> dict[str, object]:
    return {
        "@value": value,
        "@type": "@json",
    }


def _value(value: Value) -> dict[str, object]:
    node: dict[str, object] = {
        "@type": f"oak:{_VALUE_TYPES[value.source]}"
    }

    if isinstance(value, LiteralValue):
        node["value"] = _json_literal(value.value)

    elif isinstance(value, ConstantValue):
        node["constant"] = {
            "@id": value.constant,
        }

    elif isinstance(value, StateValue):
        node["state"] = {
            "@id": value.state,
        }

    elif isinstance(value, InterfaceValue):
        node["interface"] = {
            "@id": value.interface,
        }
        node["placeholder"] = value.placeholder

    elif isinstance(value, BindingValue):
        node["binding"] = value.binding

    else:
        raise TypeError(
            f"unsupported process value {type(value).__name__}"
        )

    return node


def _value_binding(
    binding: ValueBinding,
) -> dict[str, object]:
    return {
        "@type": "oak:ValueBinding",
        "placeholder": binding.placeholder,
        "value": _value(binding.value),
    }


def _condition(
    condition: Condition,
) -> dict[str, object]:
    return {
        "@type": "oak:Condition",
        "left": _value(condition.left),
        "operator": condition.operator,
        "right": _value(condition.right),
    }


def _step(step: Step) -> dict[str, object]:
    node: dict[str, object] = {
        "@type": f"oak:{_STEP_TYPES[step.kind]}"
    }

    if isinstance(step, Act):
        node["instruction"] = step.instruction
        node["inputs"] = [
            _value_binding(binding)
            for binding in step.inputs
        ]
        node["outputs"] = list(step.outputs)

    elif isinstance(step, Set):
        node["state"] = {
            "@id": step.state,
        }
        node["value"] = _value(step.value)

    elif isinstance(step, Emit):
        node["interface"] = {
            "@id": step.interface,
        }
        node["bindings"] = [
            _value_binding(binding)
            for binding in step.bindings
        ]

    elif isinstance(step, If):
        node["condition"] = _condition(step.condition)
        node["then"] = [
            _step(child)
            for child in step.then
        ]
        if step.otherwise is not None:
            node["otherwise"] = [
                _step(child)
                for child in step.otherwise
            ]

    elif isinstance(step, Call):
        node["process"] = {
            "@id": step.process,
        }

    elif isinstance(step, Fail):
        node["message"] = step.message

    else:
        raise TypeError(
            f"unsupported process step {type(step).__name__}"
        )

    return node


def _entry(entry: Entry) -> dict[str, object]:
    if isinstance(entry, Instruction):
        return {
            "@id": entry.id,
            "@type": "oak:Instruction",
            "body": entry.body,
        }

    if isinstance(entry, Constant):
        return {
            "@id": entry.id,
            "@type": "oak:Constant",
            "value": _json_literal(entry.value),
        }

    if isinstance(entry, Schema):
        return _schema(entry)

    if isinstance(entry, State):
        return {
            "@id": entry.id,
            "@type": "oak:State",
            "value": _json_literal(entry.value),
        }

    if isinstance(entry, Trigger):
        node: dict[str, object] = {
            "@id": entry.id,
            "@type": "oak:Trigger",
            "when": entry.when,
            "process": {
                "@id": entry.process,
            },
        }
        if entry.given is not None:
            node["given"] = _condition(entry.given)
        return node

    if isinstance(entry, Process):
        return {
            "@id": entry.id,
            "@type": "oak:Process",
            "name": entry.name,
            "steps": [
                _step(step)
                for step in entry.steps
            ],
        }

    if isinstance(entry, Interface):
        node = {
            "@id": entry.id,
            "@type": "oak:Interface",
            "direction": entry.direction,
            "schema": {
                "@id": entry.schema_id,
            },
        }
        if entry.description is not None:
            node["description"] = entry.description
        return node

    raise TypeError(
        f"unsupported entry {type(entry).__name__}"
    )


def _node(node: Node) -> dict[str, object]:
    data: dict[str, object] = {
        "@id": node.id,
        "@type": "oak:Node",
    }

    for field in (
        "instructions",
        "constants",
        "schemas",
        "state",
        "triggers",
        "processes",
        "interfaces",
    ):
        entries = getattr(node, field)
        if entries:
            data[field] = [
                _entry(entry)
                for entry in entries
            ]

    if node.children:
        data["children"] = [
            _node(child)
            for child in node.children
        ]

    return data


def schema_json_ld(
    schema: Schema,
    *,
    base: str,
    vocabulary: str,
) -> dict[str, object]:
    """Render one schema under one base and vocabulary context."""
    base = _base(base)
    vocabulary = _vocabulary(vocabulary)
    return {
        "@context": _context(
            base,
            vocabulary,
        ),
        **_schema(schema),
    }


def node_json_ld(
    root: Root,
    *,
    base: str,
    vocabulary: str,
) -> dict[str, object]:
    """Render one complete tree with one root context."""
    base = _base(base)
    vocabulary = _vocabulary(vocabulary)
    return {
        "@context": _context(
            base,
            vocabulary,
        ),
        **_node(root),
    }
