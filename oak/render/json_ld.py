"""The JSON-LD render: ids become @id, kinds become @type, ordered values become @list."""

from pydantic import ConfigDict, TypeAdapter
from pydantic_core import PydanticCustomError

from oak.node.parts.schemas import AtLeast, AtMost, Schema, Where
from oak.vocabulary import IriId

_VOCABULARY_ADAPTER = TypeAdapter(
    IriId,
    config=ConfigDict(strict=True, regex_engine="rust-regex"),
)

_TYPE_NAMES = {
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


def _term(vocabulary: str, name: str) -> str:
    return vocabulary + name


def _context(vocabulary: str) -> dict:
    return {
        "xsd": {"@id": "http://www.w3.org/2001/XMLSchema#", "@prefix": True},
        "name": _term(vocabulary, "name"),
        "purpose": _term(vocabulary, "purpose"),
        "template": {"@id": _term(vocabulary, "template"), "@type": "xsd:string"},
        "where": {"@id": _term(vocabulary, "where"), "@container": "@list"},
        "placeholder": {"@id": _term(vocabulary, "placeholder"), "@type": "xsd:string"},
        "constraints": {"@id": _term(vocabulary, "constraint"), "@container": "@list"},
        "examples": {"@id": _term(vocabulary, "example"), "@container": "@list"},
        "description": _term(vocabulary, "description"),
        "of": _term(vocabulary, "of"),
        "values": _term(vocabulary, "values"),
        "pattern": _term(vocabulary, "pattern"),
        "n": _term(vocabulary, "n"),
        "item": _term(vocabulary, "item"),
        "separator": _term(vocabulary, "separator"),
        "min": _term(vocabulary, "min"),
        "max": _term(vocabulary, "max"),
        "value": _term(vocabulary, "value"),
    }


def where_id(schema: Schema, placeholder: str) -> str:
    """The Where id derived from the complete schema id and placeholder."""
    return f"{schema.id}/where/{placeholder}"


def _constraint(schema: Schema, constraint, vocabulary: str) -> dict:
    data = constraint.model_dump(mode="json", exclude={"kind"}, exclude_unset=True)
    if isinstance(constraint, (AtLeast, AtMost)) and isinstance(constraint.value, str):
        data["value"] = {"@id": where_id(schema, constraint.value)}
    return {"@type": _term(vocabulary, _TYPE_NAMES[constraint.kind]), **data}


def _where(schema: Schema, where: Where, vocabulary: str) -> dict:
    node = {
        "@id": where_id(schema, where.placeholder),
        "@type": _term(vocabulary, "Where"),
        "placeholder": where.placeholder,
        "constraints": [_constraint(schema, constraint, vocabulary) for constraint in where.constraints],
    }
    if where.examples:
        node["examples"] = list(where.examples)
    if where.description is not None:
        node["description"] = where.description
    return node


def schema_json_ld(schema: Schema, *, vocabulary: str) -> dict:
    """One schema as compact JSON-LD under one caller-owned vocabulary base."""
    vocabulary = _vocabulary(vocabulary)
    node: dict = {
        "@context": _context(vocabulary),
        "@id": schema.id,
        "@type": _term(vocabulary, "Schema"),
    }
    node.update(schema.model_dump(mode="json", include={"name", "purpose", "template"}, exclude_unset=True))
    node["where"] = [_where(schema, where, vocabulary) for where in schema.where]
    return node
