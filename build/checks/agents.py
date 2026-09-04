"""Scoped canonical OAK AGENTS graph checks."""

from __future__ import annotations

import re
from pathlib import Path
import unicodedata

from build.checks.fixtures import ROOT
from oak.parse import OakParseError, parse
from oak.render import render

AGENT_PATHS = (
    "AGENTS.md",
    "oak/AGENTS.md",
    "oak/node/AGENTS.md",
    "oak/resolve/AGENTS.md",
    "oak/execute/AGENTS.md",
    "build/AGENTS.md",
    "examples/AGENTS.md",
    "outputs/AGENTS.md",
    "docs/AGENTS.md",
)

MAX_AGENT_LINES = 500

_SCOPED_PATHS = AGENT_PATHS[1:]
_SKIPPED_ROOTS = {".agents", ".git", "legacy-snapshot-aps"}
_TEXT_SUFFIXES = {".ebnf", ".md", ".py", ".toml", ".txt", ".yml", ".yaml"}
_ROUTE_PATH = re.compile(r"`([^`]+/AGENTS\.md)`")
_OWNER_PREFIX = "This document owns "
_REMOVED_PRD = Path("docs") / ("PRD" + ".md")
_REMOVED_MANUALS = (
    Path("docs") / ("architecture"),
    Path("docs") / ("guides"),
)
_REMOVED_CHECK = Path("build") / "checks" / ("documentation" + ".py")
_OBSOLETE_TEXT = (
    (Path("docs") / "architecture").as_posix() + "/",
    (Path("docs") / "guides").as_posix() + "/",
    _REMOVED_PRD.as_posix(),
    (Path("docs") / ("README" + ".md")).as_posix(),
    _REMOVED_CHECK.as_posix(),
    "read-" + "prd",
    "Read the product " + "requirements before work.",
)


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _repository_agent_paths() -> tuple[str, ...]:
    paths: list[str] = []
    for path in ROOT.rglob("AGENTS.md"):
        relative = path.relative_to(ROOT)
        if relative.parts[0] in _SKIPPED_ROOTS:
            continue
        paths.append(relative.as_posix())
    return tuple(sorted(paths))


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


def _normal_instruction(body: str) -> str:
    normalized = unicodedata.normalize("NFKC", body)
    return " ".join(normalized.casefold().split())


def _ancestor_agent_paths(path: str) -> tuple[str, ...]:
    relative = Path(path)
    ancestors = ["AGENTS.md"]
    directories = relative.parts[:-1]
    for size in range(1, len(directories) + 1):
        candidate = (Path(*directories[:size]) / "AGENTS.md").as_posix()
        if candidate in AGENT_PATHS and candidate != path:
            ancestors.append(candidate)
    return tuple(ancestors)


def validate_agents() -> None:
    """Verify scoped ownership, routing, canonical OAK, and no duplication."""
    discovered = _repository_agent_paths()
    if discovered != tuple(sorted(AGENT_PATHS)):
        raise RuntimeError(
            "repository-owned AGENTS path set is stale: "
            f"expected {tuple(sorted(AGENT_PATHS))}, got {discovered}"
        )

    nodes = {}
    for name in AGENT_PATHS:
        path = ROOT / name
        text = path.read_text(encoding="utf-8")

        line_count = len(text.splitlines())
        if line_count > MAX_AGENT_LINES:
            raise RuntimeError(
                f"{name} has {line_count} lines; maximum is {MAX_AGENT_LINES}"
            )

        if "\N{EM DASH}" in text:
            raise RuntimeError(f"{name} contains an em dash")
        if "**" in text:
            raise RuntimeError(f"{name} contains asterisk emphasis")

        try:
            node = parse(text, grouping="xml")
        except OakParseError as error:
            raise RuntimeError(f"{name} is not valid OAK: {error}") from None

        if any(
            (
                node.constants,
                node.schemas,
                node.state,
                node.triggers,
                node.processes,
                node.interfaces,
            )
        ):
            raise RuntimeError(f"{name} must use the instructions part only")

        canonical = render(node, grouping="xml")
        if canonical != text:
            raise RuntimeError(f"{name} is not canonical XML-grouped OAK")

        bodies = [instruction.body for instruction in node.instructions]
        if not bodies or not bodies[0].startswith(_OWNER_PREFIX):
            raise RuntimeError(f"{name} first instruction must state its sole owner")
        if sum(body.startswith(_OWNER_PREFIX) for body in bodies) != 1:
            raise RuntimeError(f"{name} must contain one ownership instruction")
        nodes[name] = node

    root_bodies = [instruction.body for instruction in nodes["AGENTS.md"].instructions]
    routed: list[str] = []
    for body in root_bodies:
        routed.extend(_ROUTE_PATH.findall(body))

    if tuple(sorted(routed)) != tuple(sorted(_SCOPED_PATHS)):
        raise RuntimeError(
            "root AGENTS router path set is stale: "
            f"expected {tuple(sorted(_SCOPED_PATHS))}, got {tuple(sorted(routed))}"
        )

    for name in _SCOPED_PATHS:
        route_lines = [body for body in root_bodies if f"`{name}`" in body]
        if len(route_lines) != 1:
            raise RuntimeError(f"root AGENTS router must name {name} once")
        if route_lines[0][0] not in {"├", "│", "└"} or "Read" not in route_lines[0]:
            raise RuntimeError(f"root AGENTS route for {name} is not a tree entry")

    normalized_by_path = {
        name: {
            _normal_instruction(instruction.body): instruction.body
            for instruction in node.instructions
        }
        for name, node in nodes.items()
    }

    for name in _SCOPED_PATHS:
        child = normalized_by_path[name]
        for ancestor in _ancestor_agent_paths(name):
            overlap = set(child) & set(normalized_by_path[ancestor])
            if overlap:
                repeated = child[next(iter(overlap))]
                raise RuntimeError(
                    f"{name} repeats ancestor instruction from {ancestor}: {repeated}"
                )

    seen: dict[str, tuple[str, str]] = {}
    for name in AGENT_PATHS:
        for instruction in nodes[name].instructions:
            normalized = _normal_instruction(instruction.body)
            previous = seen.get(normalized)
            if previous is not None:
                previous_path, previous_body = previous
                raise RuntimeError(
                    "duplicate scoped AGENTS instruction: "
                    f"{previous_path}: {previous_body} == {name}: {instruction.body}"
                )
            seen[normalized] = (name, instruction.body)

    for removed in (*_REMOVED_MANUALS, _REMOVED_PRD, _REMOVED_CHECK):
        if (ROOT / removed).exists():
            raise RuntimeError(f"obsolete documentation owner remains: {removed}")

    docs_entries = {path.name for path in (ROOT / "docs").iterdir()}
    if docs_entries != {"AGENTS.md", "plans"}:
        raise RuntimeError(
            "docs must contain only AGENTS.md and plans: "
            f"got {tuple(sorted(docs_entries))}"
        )

    readmes = []
    for path in ROOT.rglob("README.md"):
        relative = path.relative_to(ROOT)
        if relative.parts[0] in _SKIPPED_ROOTS:
            continue
        readmes.append(relative.as_posix())
    if readmes:
        raise RuntimeError(f"README indexes are forbidden: {tuple(sorted(readmes))}")

    for path in _current_text_files():
        text = path.read_text(encoding="utf-8")
        for obsolete in _OBSOLETE_TEXT:
            if obsolete in text:
                raise RuntimeError(
                    f"current file retains obsolete text {obsolete!r}: {_relative(path)}"
                )


__all__ = [
    "AGENT_PATHS",
    "MAX_AGENT_LINES",
    "validate_agents",
]
