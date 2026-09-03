"""JSON-LD IRI validation and ordered context construction."""

from __future__ import annotations

from typing import Annotated
from urllib.parse import urlsplit

from pydantic import (
    ConfigDict,
    StringConstraints,
    TypeAdapter,
)
from pydantic_core import PydanticCustomError

AbsoluteIri = Annotated[
    str,
    StringConstraints(
        pattern=(
            r"^[A-Za-z]"
            r"[A-Za-z0-9+.\-]*:"
            r"[^ \t\r\n]+$"
        )
    ),
]
_IRI_ADAPTER = TypeAdapter(
    AbsoluteIri,
    config=ConfigDict(
        strict=True,
        regex_engine="rust-regex",
    ),
)


def document_iri(
    value: str,
) -> str:
    """Validate one fragment-free absolute document IRI."""
    value = _IRI_ADAPTER.validate_python(
        value
    )
    parts = urlsplit(value)

    if parts.fragment:
        raise PydanticCustomError(
            "invalid_json_ld_document",
            (
                "JSON-LD document IRI "
                "must not contain a fragment"
            ),
        )

    return value


def vocabulary_iri(
    value: str,
) -> str:
    """Validate one absolute vocabulary namespace IRI."""
    value = _IRI_ADAPTER.validate_python(
        value
    )

    if not value.endswith(
        (
            "#",
            "/",
            ":",
        )
    ):
        raise PydanticCustomError(
            "invalid_json_ld_vocabulary",
            (
                "JSON-LD vocabulary must end "
                "with #, /, or :"
            ),
        )

    return value


def json_ld_context(
    document: str,
    vocabulary: str,
) -> dict[str, object]:
    """Return the compact ordered OAK JSON-LD context."""
    lists = {
        name: {
            "@id": f"oak:{name}",
            "@container": "@list",
        }
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
            "seed",
            "conditions",
            "thenSteps",
            "otherwise",
        )
    }
    ids = {
        name: {
            "@id": f"oak:{name}",
            "@type": "@id",
        }
        for name in (
            "schema",
            "process",
            "constant",
            "stateTarget",
            "interface",
            "input",
            "output",
        )
    }
    return {
        "@base": document,
        "oak": {
            "@id": vocabulary,
            "@prefix": True,
        },
        "xsd": {
            "@id": (
                "http://www.w3.org/"
                "2001/XMLSchema#"
            ),
            "@prefix": True,
        },
        **lists,
        **ids,
        "name": "oak:name",
        "purpose": "oak:purpose",
        "body": "oak:body",
        "value": "oak:value",
        "form": "oak:form",
        "template": {
            "@id": "oak:template",
            "@type": "xsd:string",
        },
        "placeholder": "oak:placeholder",
        "description": "oak:description",
        "direction": "oak:direction",
        "event": "oak:event",
        "guard": "oak:guard",
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
    }


__all__ = [
    "AbsoluteIri",
    "document_iri",
    "json_ld_context",
    "vocabulary_iri",
]
