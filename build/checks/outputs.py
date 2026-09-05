"""Generated authoring, grammar, documentation, and freshness checks."""

from __future__ import annotations

from build.checks.fixtures import ROOT


def validate_outputs() -> None:
    """Verify authoring, grammar, documentation, and output path freshness."""
    from build.authoring import artifacts
    from build.docs import documents
    from build.ebnf import grammar

    expected = {
        ROOT / "outputs" / "oak.ebnf": grammar(),
        **artifacts(),
        **{
            ROOT / "outputs" / "docs" / name: text
            for name, text in documents().items()
        },
    }

    for path, text in expected.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            raise RuntimeError(
                "generated output is missing or stale: "
                f"{path}"
            )

    actual = set((ROOT / "outputs" / "docs").glob("*.md"))
    documented = {
        path
        for path in expected
        if path.parent == ROOT / "outputs" / "docs"
    }
    if actual != documented:
        raise RuntimeError("documentation output path set is stale")

    actual_root = {
        path
        for path in (ROOT / "outputs").iterdir()
        if path.is_file() and path.name != "AGENTS.md"
    }
    expected_root = {
        ROOT / "outputs" / "oak.ebnf",
        ROOT / "outputs" / "oak-authoring.oak.md",
    }
    if actual_root != expected_root:
        raise RuntimeError("generated root output path set is stale")


__all__ = [
    "validate_outputs",
]
