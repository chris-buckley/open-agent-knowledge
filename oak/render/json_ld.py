"""The compact JSON-LD interchange render with one root context."""

from pydantic import ConfigDict, TypeAdapter
from pydantic_core import PydanticCustomError

from oak.base import Entry
from oak.node.model import Node, Root
from oak.node.parts import (
    AtLeast,
    AtMost,
    Constant,
    Instruction,
    Interface,
    Process,
    Schema,
    State,
    Trigger,
    Where,
)
from oak.vocabulary import IriId

_VOCABULARY_ADAPTER = TypeAdapter(
    IriId,
    config=ConfigDict(strict=True, regex_engine="rust-regex"),
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


def _vocabulary(value: str) -> str:
    vocabulary = _VOCABULARY_ADAPTER.validate_python(value)
    if not vocabulary.endswith(("#", "/", ":")):
        raise PydanticCustomError(
            "invalid_json_ld_vocabulary",
            "JSON-LD vocabulary must end with #, /, or :",
        )
    return vocabulary


def _context(vocabulary: str) -> dict[str, object]:
    return {
        "oak": {"@id": vocabulary, "@prefix": True},
        "xsd": {"@id": "http://www.w3.org/2001/XMLSchema#", "@prefix": True},
        "name": "oak:name",
        "purpose": "oak:purpose",
        "body": "oak:body",
        "when": "oak:when",
        "process": {"@id": "oak:process", "@type": "@id"},
        "consumes": {"@id": "oak:consumes", "@type": "@id", "@container": "@list"},
        "emits": {"@id": "oak:emits", "@type": "@id", "@container": "@list"},
        "steps": {"@id": "oak:step", "@container": "@list"},
        "value": "oak:value",
        "template": {"@id": "oak:template", "@type": "xsd:string"},
        "where": {"@id": "oak:where", "@container": "@list"},
        "placeholder": {"@id": "oak:placeholder", "@type": "xsd:string"},
        "constraints": {"@id": "oak:constraint", "@container": "@list"},
        "examples": {"@id": "oak:example", "@container": "@list"},
        "description": "oak:description",
        "direction": "oak:direction",
        "schema": {"@id": "oak:schema", "@type": "@id"},
        "of": "oak:of",
        "values": {"@id": "oak:values", "@container": "@list"},
        "pattern": "oak:pattern",
        "n": "oak:n",
        "item": "oak:item",
        "separator": "oak:separator",
        "min": "oak:min",
        "max": "oak:max",
        "instructions": {"@id": "oak:instructions", "@container": "@list"},
        "constants": {"@id": "oak:constants", "@container": "@list"},
        "schemas": {"@id": "oak:schemas", "@container": "@list"},
        "state": {"@id": "oak:state", "@container": "@list"},
        "triggers": {"@id": "oak:triggers", "@container": "@list"},
        "processes": {"@id": "oak:processes", "@container": "@list"},
        "interfaces": {"@id": "oak:interfaces", "@container": "@list"},
        "children": {"@id": "oak:children", "@container": "@list"},
    }


def where_id(schema: Schema, placeholder: str) -> str:
    """Return {schema id}/where/{Placeholder}."""
    return f"{schema.id}/where/{placeholder}"


def _constraint(schema: Schema, constraint: object) -> dict[str, object]:
    data = constraint.model_dump(mode="json", exclude={"kind"}, exclude_unset=True)
    if isinstance(constraint, (AtLeast, AtMost)) and isinstance(constraint.value, str):
        data["value"] = {"@id": where_id(schema, constraint.value)}
    return {"@type": f"oak:{_CONSTRAINT_TYPES[constraint.kind]}", **data}


def _where(schema: Schema, where: Where) -> dict[str, object]:
    node: dict[str, object] = {
        "@id": where_id(schema, where.placeholder),
        "@type": "oak:Where",
        "placeholder": where.placeholder,
        "constraints": [_constraint(schema, constraint) for constraint in where.constraints],
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
        "where": [_where(schema, where) for where in schema.where],
    }
    if schema.name is not None:
        node["name"] = schema.name
    if schema.purpose is not None:
        node["purpose"] = schema.purpose
    return node


def _json_literal(value: object) -> dict[str, object]:
    return {"@value": value, "@type": "@json"}


def _entry(entry: Entry) -> dict[str, object]:
    if isinstance(entry, Instruction):
        return {"@id": entry.id, "@type": "oak:Instruction", "body": entry.body}
    if isinstance(entry, Constant):
        return {
            "@id": entry.id,
            "@type": "oak:Constant",
            "name": entry.name,
            "value": _json_literal(entry.value),
        }
    if isinstance(entry, Schema):
        return _schema(entry)
    if isinstance(entry, State):
        return {
            "@id": entry.id,
            "@type": "oak:State",
            "name": entry.name,
            "value": _json_literal(entry.value),
        }
    if isinstance(entry, Trigger):
        return {
            "@id": entry.id,
            "@type": "oak:Trigger",
            "when": entry.when,
            "process": {"@id": entry.process},
        }
    if isinstance(entry, Process):
        node: dict[str, object] = {
            "@id": entry.id,
            "@type": "oak:Process",
            "name": entry.name,
            "steps": list(entry.steps),
        }
        if entry.consumes:
            node["consumes"] = [{"@id": reference} for reference in entry.consumes]
        if entry.emits:
            node["emits"] = [{"@id": reference} for reference in entry.emits]
        return node
    if isinstance(entry, Interface):
        node = {
            "@id": entry.id,
            "@type": "oak:Interface",
            "direction": entry.direction,
            "schema": {"@id": entry.schema_id},
        }
        if entry.description is not None:
            node["description"] = entry.description
        return node
    raise TypeError(f"unsupported entry {type(entry).__name__}")


def _node(node: Node) -> dict[str, object]:
    data: dict[str, object] = {"@id": node.id, "@type": "oak:Node"}
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
            data[field] = [_entry(entry) for entry in entries]
    if node.children:
        data["children"] = [_node(child) for child in node.children]
    return data


def schema_json_ld(schema: Schema, *, vocabulary: str) -> dict[str, object]:
    """Render one schema under one caller-owned vocabulary context."""
    vocabulary = _vocabulary(vocabulary)
    return {"@context": _context(vocabulary), **_schema(schema)}


def node_json_ld(root: Root, *, vocabulary: str) -> dict[str, object]:
    """Render one complete tree with one context at its root."""
    vocabulary = _vocabulary(vocabulary)
    return {"@context": _context(vocabulary), **_node(root)}
