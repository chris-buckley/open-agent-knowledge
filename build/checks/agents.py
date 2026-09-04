"""Scoped structured OAK AGENTS graph checks."""

from __future__ import annotations

import json
from pathlib import Path
import unicodedata

from build.checks.fixtures import ROOT
from oak.node.model import Node
from oak.node.parts.constants import Constant
from oak.node.parts.processes.steps import Act, Assert, Fail, iter_steps
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
_REMOVED_PRD = Path("docs") / ("PRD" + ".md")
_REMOVED_MANUALS = (
    Path("docs") / "architecture",
    Path("docs") / "guides",
)
_REMOVED_CHECK = Path("build") / "checks" / ("documentation" + ".py")
_OBSOLETE_TEXT = (
    (Path("docs") / "architecture").as_posix() + "/",
    (Path("docs") / "guides").as_posix() + "/",
    _REMOVED_PRD.as_posix(),
    (Path("docs") / ("README" + ".md")).as_posix(),
    _REMOVED_CHECK.as_posix(),
    "Use only the " + "instructions part in repository-owned `AGENTS.md` files.",
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


def _normal_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    return " ".join(normalized.casefold().split())


def _constant(node: Node, identifier: str) -> Constant:
    matches = [item for item in node.constants if item.id == identifier]
    if len(matches) != 1:
        raise RuntimeError(f"expected one constant.{identifier}, got {len(matches)}")
    return matches[0]


def _ancestor_agent_paths(path: str) -> tuple[str, ...]:
    relative = Path(path)
    ancestors = ["AGENTS.md"]
    directories = relative.parts[:-1]
    for size in range(1, len(directories) + 1):
        candidate = (Path(*directories[:size]) / "AGENTS.md").as_posix()
        if candidate in AGENT_PATHS and candidate != path:
            ancestors.append(candidate)
    return tuple(ancestors)


def _claims(node: Node) -> dict[str, str]:
    """Return normalized authored claims without generated interpretation text."""
    claims: dict[str, str] = {}

    def add(kind: str, text: str) -> None:
        normalized = _normal_text(text)
        if normalized:
            claims[f"{kind}:{normalized}"] = text

    for instruction in node.instructions:
        add("instruction", instruction.body)

    for constant in node.constants:
        value = json.dumps(
            constant.value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        add("constant", value)

    for schema in node.schemas:
        if schema.name is not None:
            add("schema-name", schema.name)
        if schema.purpose is not None:
            add("schema-purpose", schema.purpose)
        add("schema-template", schema.template)
        for where in schema.where:
            if where.description is not None:
                add("where-description", where.description)

    for trigger in node.triggers:
        add("trigger-event", trigger.event)

    for process in node.processes:
        for step in iter_steps(process.steps):
            if isinstance(step, Act):
                add("act", step.instruction)
            elif isinstance(step, (Assert, Fail)):
                add("failure", step.message)

    for interface in node.interfaces:
        if interface.description is not None:
            add("interface-description", interface.description)

    return claims


def _validate_instruction_last_policy(name: str, node: Node) -> None:
    if not any(
        (
            node.constants,
            node.schemas,
            node.state,
            node.triggers,
            node.processes,
            node.interfaces,
        )
    ):
        raise RuntimeError(f"{name} has no structured OAK knowledge")

    justification = [
        item
        for item in node.constants
        if item.id == "instruction-justification"
    ]
    if node.instructions:
        if len(justification) != 1:
            raise RuntimeError(
                f"{name} uses authored instructions without one "
                "constant.instruction-justification"
            )
        value = justification[0].value
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(f"{name} has an empty instruction justification")
    elif justification:
        raise RuntimeError(f"{name} has an unused instruction justification")


def validate_agents() -> None:
    """Verify scoped ownership, structured-first OAK, routing, and no duplication."""
    discovered = _repository_agent_paths()
    expected = tuple(sorted(AGENT_PATHS))
    if discovered != expected:
        raise RuntimeError(
            "repository-owned AGENTS path set is stale: "
            f"expected {expected}, got {discovered}"
        )

    nodes: dict[str, Node] = {}
    concerns: dict[str, str] = {}

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

        canonical = render(node, grouping="xml")
        if canonical != text:
            raise RuntimeError(f"{name} is not canonical XML-grouped OAK")

        _validate_instruction_last_policy(name, node)

        if not node.constants:
            raise RuntimeError(f"{name} must define structured constants")
        owner = node.constants[0]
        if owner.id != "owned-concern":
            raise RuntimeError(f"{name} first constant must be owned-concern")
        if owner.form != "inline" or not isinstance(owner.value, str) or not owner.value:
            raise RuntimeError(f"{name} owned-concern must be one inline string")
        if owner.value in concerns.values():
            raise RuntimeError(f"{name} repeats another owned concern: {owner.value}")
        concerns[name] = owner.value

        if not node.processes:
            raise RuntimeError(f"{name} must define at least one operating process")

        nodes[name] = node

    root = nodes["AGENTS.md"]
    priority = _constant(root, "part-authoring-priority").value
    if priority != [
        "schemas",
        "constants",
        "state",
        "interfaces",
        "triggers",
        "processes",
        "instructions",
    ]:
        raise RuntimeError("root part-authoring-priority is stale")
    if priority[-1] != "instructions" or len(set(priority)) != 7:
        raise RuntimeError("instructions must be last in the complete part priority")

    line_limit = _constant(root, "agent-line-limit").value
    if line_limit != MAX_AGENT_LINES:
        raise RuntimeError("root line limit and build line limit differ")

    router = _constant(root, "agent-router")
    if router.form != "csv" or not isinstance(router.value, list):
        raise RuntimeError("root agent-router must be one CSV constant")
    rows = router.value
    if any(set(row) != {"path", "concern"} for row in rows if isinstance(row, dict)):
        raise RuntimeError("root agent-router columns are stale")
    routed = [row["path"] for row in rows if isinstance(row, dict)]
    if tuple(routed) != _SCOPED_PATHS:
        raise RuntimeError(
            "root AGENTS router path order is stale: "
            f"expected {_SCOPED_PATHS}, got {tuple(routed)}"
        )
    if len({row["concern"] for row in rows if isinstance(row, dict)}) != len(rows):
        raise RuntimeError("root AGENTS router repeats a concern")

    if [schema.id for schema in root.schemas] != [
        "repository-task",
        "repository-result",
    ]:
        raise RuntimeError("root repository schemas are stale")
    if [trigger.id for trigger in root.triggers] != [
        "repository-task-requested",
        "branch-merged",
    ]:
        raise RuntimeError("root repository triggers are stale")
    if [process.id for process in root.processes] != [
        "perform-repository-task",
        "clean-merged-branch",
    ]:
        raise RuntimeError("root repository processes are stale")
    if [interface.id for interface in root.interfaces] != [
        "task-request",
        "task-result",
    ]:
        raise RuntimeError("root repository interfaces are stale")

    claims_by_path = {name: _claims(node) for name, node in nodes.items()}
    seen: dict[str, tuple[str, str]] = {}
    for name in AGENT_PATHS:
        for key, claim in claims_by_path[name].items():
            previous = seen.get(key)
            if previous is not None:
                previous_path, previous_claim = previous
                raise RuntimeError(
                    "duplicate scoped AGENTS claim: "
                    f"{previous_path}: {previous_claim} == {name}: {claim}"
                )
            seen[key] = (name, claim)

    for name in _SCOPED_PATHS:
        child = claims_by_path[name]
        for ancestor in _ancestor_agent_paths(name):
            overlap = set(child) & set(claims_by_path[ancestor])
            if overlap:
                key = next(iter(overlap))
                raise RuntimeError(
                    f"{name} repeats ancestor claim from {ancestor}: {child[key]}"
                )

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
