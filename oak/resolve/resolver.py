"""Explicit loading and validation of one reachable OAK document graph."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from oak.node.index import NodeIndex
from oak.node.model import Node
from oak.node.parts.entry import Entry
from oak.parse.document import parse
from oak.parse.errors import OakParseError
from oak.resolve.contracts import (
    validate_call_cycles,
    validate_contracts,
)
from oak.resolve.errors import raise_resolution
from oak.resolve.graph import ResolvedGraph
from oak.resolve.paths import (
    normalize_source,
    resolve_document,
)
from oak.resolve.references import iter_targets
from oak.vocabulary.text.target_path import (
    is_relative_target,
    split_target,
)

DocumentSource = str | bytes | Node
DocumentLoader = Callable[
    [str],
    DocumentSource | None,
]


def load_document(
    path: str,
    loader: DocumentLoader,
    source: str,
) -> Node:
    """Load and parse one referenced document."""
    loaded = loader(path)

    if loaded is None:
        raise_resolution(
            "external_document_missing",
            source,
            path,
            "explicit loader returned no document",
        )

    if isinstance(loaded, Node):
        return loaded

    try:
        return parse(loaded)

    except OakParseError as error:
        raise_resolution(
            "external_document_invalid",
            source,
            path,
            str(error),
        )


def validate_targets(graph: ResolvedGraph) -> None:
    """Resolve and type-check every target in the graph."""
    for source, node in graph.documents.items():
        for target, expected in iter_targets(node):
            graph.entry(
                source,
                target,
                expected,
            )


def resolve(
    node: Node,
    *,
    source: str | None = None,
    load: DocumentLoader | None = None,
    root: str | None = None,
) -> ResolvedGraph:
    """Resolve every reachable relative target through one explicit loader."""
    relative_exists = any(
        is_relative_target(target)
        for target, _expected in iter_targets(node)
    )

    if source is None:
        if relative_exists:
            raise_resolution(
                "external_reference_without_source",
                None,
                "<relative>",
                "relative targets need a source document path",
            )

        source = "document.oak.md"

    source = normalize_source(source)
    documents: dict[str, Node] = {
        source: node,
    }
    registries: dict[
        str,
        Mapping[str, Entry],
    ] = {
        source: NodeIndex.build(node),
    }
    pending = [source]

    while pending:
        current = pending.pop(0)
        current_node = documents[current]

        for target, _expected in iter_targets(current_node):
            relative, _part, _identifier = split_target(target)

            if relative is None:
                continue

            if load is None:
                raise_resolution(
                    "external_document_missing",
                    current,
                    target,
                    "relative target needs an explicit loader",
                )

            document = resolve_document(
                current,
                relative,
                root,
            )

            if document in documents:
                continue

            loaded = load_document(
                document,
                load,
                current,
            )
            documents[document] = loaded
            registries[document] = NodeIndex.build(loaded)
            pending.append(document)

    graph = ResolvedGraph(
        source,
        documents,
        registries,
    )
    validate_targets(graph)
    validate_contracts(graph)
    validate_call_cycles(graph)
    return graph


__all__ = [
    "DocumentLoader",
    "DocumentSource",
    "resolve",
]
