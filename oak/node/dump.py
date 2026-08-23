"""The internal Pydantic authoring snapshot."""

from oak.node.model import Root


def dump(root: Root) -> dict[str, object]:
    """Return JSON-safe authored data with unset fields omitted."""
    return root.model_dump(mode="json", exclude_unset=True)


def dump_json(root: Root, *, indent: int | None = 2) -> str:
    """Return JSON authored data with unset fields omitted."""
    return root.model_dump_json(exclude_unset=True, indent=indent)
