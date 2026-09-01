"""The compact JSON-LD interchange render for one OAK document."""

from __future__ import annotations

from typing import Annotated
from urllib.parse import urljoin, urlsplit

from pydantic import ConfigDict, StringConstraints, TypeAdapter
from pydantic_core import PydanticCustomError

from oak.base import Entry
from oak.node.model import Node
from oak.node.parts import (
    Act,
    All,
    Any,
    Assert,
    AtLeast,
    AtMost,
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
    Instruction,
    Interface,
    InterfaceValue,
    Join,
    LiteralValue,
    Not,
    Par,
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
    While,
)
from oak.vocabulary.text.target_path import split_target

AbsoluteIri = Annotated[str, StringConstraints(pattern=r"^[A-Za-z][A-Za-z0-9+.\-]*:[^ \t\r\n]+$")]
_IRI_ADAPTER = TypeAdapter(AbsoluteIri, config=ConfigDict(strict=True, regex_engine="rust-regex"))
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
    "assert": "Assert",
    "foreach": "Foreach",
    "while": "While",
    "par": "Par",
    "join": "Join",
}
_CONDITION_TYPES = {
    "compare": "Compare",
    "all": "All",
    "any": "Any",
    "not": "Not",
}


def _document(value: str) -> str:
    value = _IRI_ADAPTER.validate_python(value)
    parts = urlsplit(value)
    if parts.fragment:
        raise PydanticCustomError("invalid_json_ld_document", "JSON-LD document IRI must not contain a fragment")
    return value


def _vocabulary(value: str) -> str:
    value = _IRI_ADAPTER.validate_python(value)
    if not value.endswith(("#", "/", ":")):
        raise PydanticCustomError("invalid_json_ld_vocabulary", "JSON-LD vocabulary must end with #, /, or :")
    return value


def _context(document: str, vocabulary: str) -> dict[str, object]:
    lists = {
        name: {"@id": f"oak:{name}", "@container": "@list"}
        for name in (
            "instructions",
            "constants",
            "schemas",
            "state",
            "triggers",
            "processes",
            "interfaces",
            "where",
            "constraints",
            "examples",
            "steps",
            "inputs",
            "outputs",
            "bindings",
            "conditions",
            "thenSteps",
            "otherwise",
        )
    }
    ids = {
        name: {"@id": f"oak:{name}", "@type": "@id"}
        for name in (
            "schema",
            "process",
            "then",
            "constant",
            "stateTarget",
            "interface",
            "input",
            "output",
        )
    }
    return {
        "@base": document,
        "oak": {"@id": vocabulary, "@prefix": True},
        "xsd": {"@id": "http://www.w3.org/2001/XMLSchema#", "@prefix": True},
        **lists,
        **ids,
        "name": "oak:name",
        "purpose": "oak:purpose",
        "body": "oak:body",
        "value": "oak:value",
        "form": "oak:form",
        "template": {"@id": "oak:template", "@type": "xsd:string"},
        "placeholder": "oak:placeholder",
        "description": "oak:description",
        "direction": "oak:direction",
        "given": "oak:given",
        "when": "oak:when",
        "kind": "oak:kind",
        "source": "oak:source",
        "operator": "oak:operator",
        "left": "oak:left",
        "right": "oak:right",
        "condition": "oak:condition",
        "instruction": "oak:instruction",
        "tool": "oak:tool",
        "message": "oak:message",
        "binding": "oak:binding",
        "loopBinding": "oak:loopBinding",
        "limit": "oak:limit",
        "of": "oak:of",
        "values": {"@id": "oak:values", "@container": "@list"},
        "pattern": "oak:pattern",
        "n": "oak:n",
        "item": "oak:item",
        "separator": "oak:separator",
        "min": "oak:min",
        "max": "oak:max",
    }


def entry_id(document: str, part: str, identifier: str) -> str:
    """Return the absolute JSON-LD id of one local entry."""
    return f"{document}#{part}.{identifier}"


def target_id(document: str, target: str) -> str:
    """Resolve one OAK target path against a document IRI."""
    relative, part, identifier = split_target(target)
    target_document = urljoin(document, relative) if relative is not None else document
    return entry_id(target_document, part, identifier)


def where_id(document: str, schema: Schema, placeholder: str) -> str:
    """Return the absolute id for one Where."""
    return f"{entry_id(document, 'schema', schema.id)}/where/{placeholder}"


def _json_literal(value: object) -> dict[str, object]:
    return {"@value": value, "@type": "@json"}


def _constraint(document: str, schema: Schema, constraint: object) -> dict[str, object]:
    data = constraint.model_dump(mode="json", exclude={"kind"}, exclude_unset=True)
    if isinstance(constraint, (AtLeast, AtMost)) and isinstance(constraint.value, str):
        data["value"] = {"@id": where_id(document, schema, constraint.value)}
    return {"@type": f"oak:{_CONSTRAINT_TYPES[constraint.kind]}", **data}


def _where(document: str, schema: Schema, item: Where) -> dict[str, object]:
    node: dict[str, object] = {
        "@id": where_id(document, schema, item.placeholder),
        "@type": "oak:Where",
        "placeholder": item.placeholder,
        "constraints": [_constraint(document, schema, constraint) for constraint in item.constraints],
    }
    if item.examples:
        node["examples"] = list(item.examples)
    if item.description is not None:
        node["description"] = item.description
    return node


def _schema(document: str, schema: Schema) -> dict[str, object]:
    node: dict[str, object] = {
        "@id": entry_id(document, "schema", schema.id),
        "@type": "oak:Schema",
        "template": schema.template,
        "where": [_where(document, schema, item) for item in schema.where],
    }
    if schema.name is not None:
        node["name"] = schema.name
    if schema.purpose is not None:
        node["purpose"] = schema.purpose
    return node


def _value(document: str, value: Value) -> dict[str, object]:
    node: dict[str, object] = {"@type": f"oak:{_VALUE_TYPES[value.source]}"}
    if isinstance(value, LiteralValue):
        node["value"] = _json_literal(value.value)
    elif isinstance(value, ConstantValue):
        node["constant"] = {"@id": target_id(document, value.constant)}
    elif isinstance(value, StateValue):
        node["stateTarget"] = {"@id": target_id(document, value.state)}
    elif isinstance(value, InterfaceValue):
        node["interface"] = {"@id": target_id(document, value.interface)}
        node["placeholder"] = value.placeholder
    elif isinstance(value, BindingValue):
        node["binding"] = value.binding
    else:
        raise TypeError(type(value).__name__)
    return node


def _binding(document: str, binding: ValueBinding) -> dict[str, object]:
    return {"@type": "oak:ValueBinding", "placeholder": binding.placeholder, "value": _value(document, binding.value)}


def _condition(document: str, condition: Condition) -> dict[str, object]:
    node: dict[str, object] = {"@type": f"oak:{_CONDITION_TYPES[condition.kind]}"}
    if isinstance(condition, Compare):
        node.update(left=_value(document, condition.left), operator=condition.operator, right=_value(document, condition.right))
    elif isinstance(condition, (All, Any)):
        node["conditions"] = [_condition(document, child) for child in condition.conditions]
    elif isinstance(condition, Not):
        node["condition"] = _condition(document, condition.condition)
    else:
        raise TypeError(type(condition).__name__)
    return node


def _step(document: str, step: Step) -> dict[str, object]:
    node: dict[str, object] = {"@type": f"oak:{_STEP_TYPES[step.kind]}"}
    if isinstance(step, Act):
        node["instruction"] = step.instruction
        if step.tool is not None:
            node["tool"] = step.tool
        if step.input is not None:
            node["input"] = {"@id": target_id(document, step.input)}
        if step.output is not None:
            node["output"] = {"@id": target_id(document, step.output)}
        node["inputs"] = [_binding(document, binding) for binding in step.inputs]
        node["outputs"] = list(step.outputs)
    elif isinstance(step, Set):
        node["stateTarget"] = {"@id": target_id(document, step.state)}
        node["value"] = _value(document, step.value)
    elif isinstance(step, Emit):
        node["interface"] = {"@id": target_id(document, step.interface)}
        node["bindings"] = [_binding(document, binding) for binding in step.bindings]
    elif isinstance(step, If):
        node["condition"] = _condition(document, step.condition)
        node["thenSteps"] = [_step(document, child) for child in step.then]
        if step.otherwise is not None:
            node["otherwise"] = [_step(document, child) for child in step.otherwise]
    elif isinstance(step, Call):
        node["process"] = {"@id": target_id(document, step.process)}
        node["inputs"] = [_binding(document, binding) for binding in step.inputs]
        node["outputs"] = list(step.outputs)
    elif isinstance(step, Fail):
        node["message"] = step.message
    elif isinstance(step, Assert):
        node["condition"] = _condition(document, step.condition)
        if step.message is not None:
            node["message"] = step.message
    elif isinstance(step, Foreach):
        node["loopBinding"] = step.binding
        node["value"] = _value(document, step.value)
        node["steps"] = [_step(document, child) for child in step.steps]
    elif isinstance(step, While):
        node["condition"] = _condition(document, step.condition)
        node["limit"] = step.limit
        node["steps"] = [_step(document, child) for child in step.steps]
    elif isinstance(step, Par):
        node["steps"] = [_step(document, child) for child in step.steps]
    elif isinstance(step, Join):
        pass
    else:
        raise TypeError(type(step).__name__)
    return node


def _entry(document: str, entry: Entry) -> dict[str, object]:
    if isinstance(entry, Instruction):
        return {"@id": entry_id(document, "instruction", entry.id), "@type": "oak:Instruction", "body": entry.body}
    if isinstance(entry, Constant):
        node: dict[str, object] = {"@id": entry_id(document, "constant", entry.id), "@type": "oak:Constant", "form": entry.form, "value": _json_literal(entry.value)}
        if entry.schema_id is not None:
            node["schema"] = {"@id": target_id(document, entry.schema_id)}
            node["placeholder"] = entry.placeholder
        return node
    if isinstance(entry, Schema):
        return _schema(document, entry)
    if isinstance(entry, State):
        node = {"@id": entry_id(document, "state", entry.id), "@type": "oak:State", "value": _json_literal(entry.value)}
        if entry.schema_id is not None:
            node["schema"] = {"@id": target_id(document, entry.schema_id)}
            node["placeholder"] = entry.placeholder
        return node
    if isinstance(entry, Trigger):
        node = {
            "@id": entry_id(document, "trigger", entry.id),
            "@type": "oak:Trigger",
            "given": True if entry.given is True else _condition(document, entry.given),
            "when": entry.when,
            "then": {"@id": target_id(document, entry.then)},
        }
        if entry.inputs:
            node["inputs"] = [_binding(document, binding) for binding in entry.inputs]
        return node
    if isinstance(entry, Process):
        node: dict[str, object] = {
            "@id": entry_id(document, "process", entry.id),
            "@type": "oak:Process",
            "name": entry.name,
            "steps": [_step(document, step) for step in entry.steps],
        }
        if entry.input is not None:
            node["input"] = {"@id": target_id(document, entry.input)}
        if entry.output is not None:
            node["output"] = {"@id": target_id(document, entry.output)}
        return node
    if isinstance(entry, Interface):
        node = {
            "@id": entry_id(document, "interface", entry.id),
            "@type": "oak:Interface",
            "direction": entry.direction,
            "schema": {"@id": target_id(document, entry.schema_id)},
        }
        if entry.description is not None:
            node["description"] = entry.description
        return node
    raise TypeError(type(entry).__name__)


def node_json_ld(node: Node, *, document: str, vocabulary: str) -> dict[str, object]:
    """Render one OAK document with one root context."""
    document = _document(document)
    vocabulary = _vocabulary(vocabulary)
    data: dict[str, object] = {
        "@context": _context(document, vocabulary),
        "@id": document,
        "@type": "oak:Node",
    }
    for field in ("instructions", "constants", "schemas", "state", "triggers", "processes", "interfaces"):
        entries = getattr(node, field)
        if entries:
            data[field] = [_entry(document, entry) for entry in entries]
    return data


def schema_json_ld(schema: Schema, *, document: str, vocabulary: str) -> dict[str, object]:
    """Render one schema under one document and vocabulary context."""
    document = _document(document)
    vocabulary = _vocabulary(vocabulary)
    return {"@context": _context(document, vocabulary), **_schema(document, schema)}
