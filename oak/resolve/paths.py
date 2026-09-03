"""POSIX document-path normalization and display."""

from __future__ import annotations

import posixpath

from oak.resolve.errors import raise_resolution
from oak.vocabulary.text.target_path import split_target


def normalize_source(source: str) -> str:
    """Return one normalized source document path."""
    if (
        "\\" in source
        or "\x00" in source
        or "?" in source
        or "#" in source
    ):
        raise_resolution(
            "invalid_document_path",
            source,
            source,
            "source path must be a clean POSIX path",
        )

    normalized = posixpath.normpath(source)

    if normalized in ("", ".", "..") or source.endswith("/"):
        raise_resolution(
            "invalid_document_path",
            source,
            source,
            "source path must identify one .oak.md document",
        )

    if not normalized.endswith(".oak.md"):
        raise_resolution(
            "invalid_document_path",
            source,
            source,
            "source path must end in .oak.md",
        )

    return normalized


def resolve_document(
    source: str,
    relative: str,
    root: str | None,
) -> str:
    """Resolve one relative document path within the optional root."""
    target = posixpath.normpath(
        posixpath.join(
            posixpath.dirname(source),
            relative,
        )
    )

    if root is not None:
        root_path = posixpath.normpath(root)

        try:
            common = posixpath.commonpath(
                (
                    root_path,
                    target,
                )
            )
        except ValueError:
            common = ""

        if common != root_path:
            raise_resolution(
                "invalid_document_path",
                source,
                relative,
                "relative target escapes the allowed root",
            )

    return target


def target_document(
    source: str,
    target: str,
) -> str:
    """Return the normalized document selected by one target."""
    relative, _part, _identifier = split_target(target)

    if relative is None:
        return source

    return posixpath.normpath(
        posixpath.join(
            posixpath.dirname(source),
            relative,
        )
    )


def display_target(
    root: str,
    document: str,
    part: str,
    identifier: str,
) -> str:
    """Return one target relative to the root document."""
    if document == root:
        return f"{part}.{identifier}"

    relative = posixpath.relpath(
        document,
        posixpath.dirname(root),
    )
    return f"{relative}#{part}.{identifier}"


__all__ = [
    "display_target",
    "normalize_source",
    "resolve_document",
    "target_document",
]
