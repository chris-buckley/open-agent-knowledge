"""Manual documentation routing and migration freshness checks."""

from __future__ import annotations

from pathlib import Path
import re

from build.checks.fixtures import ROOT
from oak.parse.document import parse
from oak.render import render

ROUTED_DOCUMENTS = (
    "docs/architecture/overview.md",
    "docs/architecture/document.md",
    "docs/architecture/graph.md",
    "docs/architecture/validation.md",
    "docs/architecture/execution.md",
    "docs/architecture/representation.md",
    "docs/architecture/repository.md",
    "docs/guides/authoring.md",
)

_REMOVED_PRD = Path("docs") / ("PRD" + ".md")
_REMOVED_INDEXES = (
    Path("README" + ".md"),
    Path("docs") / ("README" + ".md"),
)
_OBSOLETE_TEXT = (
    _REMOVED_PRD.as_posix(),
    _REMOVED_INDEXES[1].as_posix(),
    "read-" + "prd",
    "Read the product " + "requirements before work.",
)
_EXAMPLE_FENCE = "```oak\n"
_FENCE_CLOSE = "\n```"
_MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_TEXT_SUFFIXES = {".ebnf", ".md", ".py", ".toml", ".txt"}
_SKIPPED_ROOTS = {".git", "legacy-snapshot-aps"}


def _current_text_files() -> tuple[Path, ...]:
    files: list[Path] = []

    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in _TEXT_SUFFIXES:
            continue
        relative = path.relative_to(ROOT)
        if relative.parts[0] in _SKIPPED_ROOTS:
            continue
        if relative.parts[:2] == ("docs", "plans"):
            continue
        if "__pycache__" in relative.parts:
            continue
        files.append(path)

    return tuple(sorted(files))


def _single_oak_example(text: str) -> str:
    if text.count(_EXAMPLE_FENCE) != 1:
        raise RuntimeError("authoring guide must contain exactly one OAK example")

    start = text.index(_EXAMPLE_FENCE) + len(_EXAMPLE_FENCE)
    end = text.find(_FENCE_CLOSE, start)
    if end < 0:
        raise RuntimeError("authoring guide OAK example fence is not closed")
    return text[start:end]


def validate_documentation() -> None:
    """Verify routed manuals, removed PRD references, and the guide example."""
    from build.authoring import canonical_example

    for name in ROUTED_DOCUMENTS:
        if not (ROOT / name).is_file():
            raise RuntimeError(f"required documentation is missing: {name}")

    actual_routes = {
        path.relative_to(ROOT).as_posix()
        for directory in (
            ROOT / "docs" / "architecture",
            ROOT / "docs" / "guides",
        )
        for path in directory.glob("*.md")
    }
    expected_routes = set(ROUTED_DOCUMENTS)
    if actual_routes != expected_routes:
        raise RuntimeError("documentation router path set is stale")

    if (ROOT / _REMOVED_PRD).exists():
        raise RuntimeError(f"{_REMOVED_PRD} remains after architecture migration")

    for index_path in _REMOVED_INDEXES:
        if (ROOT / index_path).exists():
            raise RuntimeError(f"README index is forbidden: {index_path}")

    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    for name in ROUTED_DOCUMENTS:
        relative = Path(name).relative_to("docs")
        if any(part not in agents for part in relative.parts):
            raise RuntimeError(f"AGENTS.md router omits {name}")

    for path in _current_text_files():
        text = path.read_text(encoding="utf-8")
        for obsolete in _OBSOLETE_TEXT:
            if obsolete in text:
                raise RuntimeError(
                    f"current file retains obsolete documentation text {obsolete!r}: "
                    f"{path.relative_to(ROOT)}"
                )

    manuals = [
        ROOT / "AGENTS.md",
        *(ROOT / name for name in ROUTED_DOCUMENTS),
    ]
    for path in manuals:
        text = path.read_text(encoding="utf-8")
        if "\N{EM DASH}" in text:
            raise RuntimeError(
                "documentation contains an em dash: "
                f"{path.relative_to(ROOT)}"
            )
        if "**" in text:
            raise RuntimeError(
                f"documentation contains asterisk emphasis: {path.relative_to(ROOT)}"
            )

        for target in _MARKDOWN_LINK.findall(text):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            linked = (path.parent / target.split("#", 1)[0]).resolve()
            if not linked.exists():
                raise RuntimeError(
                    "documentation link target is missing: "
                    f"{path.relative_to(ROOT)} -> {target}"
                )

    guide = (ROOT / "docs" / "guides" / "authoring.md").read_text(
        encoding="utf-8"
    )
    example = _single_oak_example(guide)
    if example != canonical_example():
        raise RuntimeError(
            "authoring guide example differs from the prompt example"
        )
    if render(parse(example), grouping="xml") != example:
        raise RuntimeError("authoring guide example is not canonical XML OAK")


__all__ = [
    "ROUTED_DOCUMENTS",
    "validate_documentation",
]
