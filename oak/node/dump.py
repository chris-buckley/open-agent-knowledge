"""The internal Pydantic programmatic snapshot."""

from oak.node.model import Node


def dump(node: Node) -> dict[str, object]:
    """Return JSON-safe authored data with unset fields omitted."""
    return node.model_dump(
        mode="json",
        by_alias=True,
        exclude_unset=True,
    )


def dump_json(node: Node, *, indent: int | None = 2) -> str:
    """Return JSON authored data with unset fields omitted."""
    return node.model_dump_json(
        by_alias=True,
        exclude_unset=True,
        indent=indent,
    )
