"""Render selection with OAK defaults."""

from __future__ import annotations

import json
from typing import Literal

from oak.defaults import DEFAULT_GROUPING, DEFAULT_RENDER, DEFAULT_STYLE
from oak.node.model import Node
from oak.render.json_ld import node_json_ld, schema_json_ld
from oak.render.oak import GroupingName, StyleName, node_markdown, node_xml, schema_markdown, schema_xml

RenderName = Literal["oak", "json-ld"]


def render(
    node: Node,
    *,
    render: RenderName | None = None,
    grouping: GroupingName | None = None,
    style: StyleName | None = None,
    document: str | None = None,
    vocabulary: str | None = None,
) -> str:
    """Render one OAK document with defaults for unset choices."""
    render_name = render or DEFAULT_RENDER
    if render_name == "oak":
        if document is not None or vocabulary is not None:
            raise ValueError("document and vocabulary apply only to JSON-LD")
        grouping_name = grouping or DEFAULT_GROUPING
        style_name = style or DEFAULT_STYLE
        if grouping_name == "xml":
            return node_xml(node, style=style_name)
        if grouping_name == "markdown":
            return node_markdown(node, style=style_name)
        raise ValueError(f"unknown OAK grouping {grouping_name}")
    if render_name == "json-ld":
        if grouping is not None or style is not None:
            raise ValueError("grouping and style apply only to OAK")
        if document is None or vocabulary is None:
            raise ValueError("JSON-LD needs document and vocabulary")
        return json.dumps(node_json_ld(node, document=document, vocabulary=vocabulary), ensure_ascii=False, indent=2)
    raise ValueError(f"unknown render {render_name}")


__all__ = [
    "GroupingName",
    "RenderName",
    "StyleName",
    "node_json_ld",
    "node_markdown",
    "node_xml",
    "render",
    "schema_json_ld",
    "schema_markdown",
    "schema_xml",
]
