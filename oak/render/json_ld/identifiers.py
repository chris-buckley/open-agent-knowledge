"""Absolute identifiers for JSON-LD entries and OAK targets."""

from __future__ import annotations

from urllib.parse import urljoin

from oak.node.parts.schemas.model import Schema
from oak.vocabulary.text.target_path import split_target


def entry_id(
    document: str,
    part: str,
    identifier: str,
) -> str:
    """Return the absolute JSON-LD id of one local entry."""
    return (
        f"{document}#"
        f"{part}.{identifier}"
    )


def target_id(
    document: str,
    target: str,
) -> str:
    """Resolve one OAK target path against a document IRI."""
    (
        relative,
        part,
        identifier,
    ) = split_target(target)
    target_document = (
        urljoin(
            document,
            relative,
        )
        if relative is not None
        else document
    )
    return entry_id(
        target_document,
        part,
        identifier,
    )


def where_id(
    document: str,
    schema: Schema,
    placeholder: str,
) -> str:
    """Return the absolute id for one Where."""
    return (
        f"{entry_id(document, 'schema', schema.id)}"
        f"/where/{placeholder}"
    )


__all__ = [
    "entry_id",
    "target_id",
    "where_id",
]
