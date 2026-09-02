"""Public JSON-LD rendering of nodes and schemas."""

from __future__ import annotations

from oak.node.model import Node
from oak.node.parts.schemas.model import Schema
from oak.node.structure import PART_ORDER
from oak.render.json_ld.context import (
    document_iri,
    json_ld_context,
    vocabulary_iri,
)
from oak.render.json_ld.entries import (
    entry_node,
    schema_node,
)


def node_json_ld(
    node: Node,
    *,
    document: str,
    vocabulary: str,
) -> dict[str, object]:
    """Render one OAK document with one root context."""
    document = document_iri(document)
    vocabulary = vocabulary_iri(
        vocabulary
    )
    document_node: dict[str, object] = {
        "@context": json_ld_context(
            document,
            vocabulary,
        ),
        "@id": document,
        "@type": "oak:Node",
    }

    for field in PART_ORDER:
        entries = getattr(
            node,
            field,
        )

        if entries:
            document_node[field] = [
                entry_node(
                    document,
                    entry,
                )
                for entry in entries
            ]

    return document_node


def schema_json_ld(
    schema: Schema,
    *,
    document: str,
    vocabulary: str,
) -> dict[str, object]:
    """Render one schema under one document and vocabulary context."""
    document = document_iri(document)
    vocabulary = vocabulary_iri(
        vocabulary
    )
    return {
        "@context": json_ld_context(
            document,
            vocabulary,
        ),
        **schema_node(
            document,
            schema,
        ),
    }


__all__ = [
    "node_json_ld",
    "schema_json_ld",
]
