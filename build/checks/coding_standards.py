"""Verify modular Python knowledge without claiming that style or example code was executed."""

from __future__ import annotations

import ast
from collections import Counter
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from typing import Final, cast

from pydantic import JsonValue

from build.checks.fixtures import ROOT
from oak import Constant, Node, parse, render, resolve

_ENTRY: Final = "coding-standards.oak.md"
_SOURCE_ROOT: Final = ".agents/rules"
_RULE_FIELDS: Final = frozenset({"section", "title", "requirements", "examples", "tables"})
_EXAMPLE_FIELDS: Final = frozenset({"id", "section", "topic", "language", "scope"})


def validate_coding_standards() -> None:
    """Check routing, canonical knowledge, source coverage, shapes, and rejected inputs."""
    rule_directory = ROOT / _SOURCE_ROOT
    documents = _read_documents(rule_directory)
    _validate_documents(documents)
    _validate_rejections(documents)
    _validate_shapes(documents)
    root_node = parse((ROOT / "AGENTS.md").read_text(encoding="utf-8"))
    if _constant(root_node, "coding-standard").value != f"{_SOURCE_ROOT}/{_ENTRY}":
        raise ValueError("root coding-standard route is stale")
    if (rule_directory / "coding-standards.md").exists():
        raise ValueError("the obsolete Markdown standard remains")


def _read_documents(rule_directory: Path) -> dict[str, str]:
    paths = (rule_directory / _ENTRY, *sorted((rule_directory / "python").glob("*.oak.md")))
    directories = (rule_directory, rule_directory / "python")
    if any(directory.is_symlink() for directory in directories) or any(path.is_symlink() for path in paths):
        raise ValueError("Python knowledge must not use symbolic links")
    return {path.relative_to(rule_directory).as_posix(): path.read_text(encoding="utf-8") for path in paths}


def _constant(node: Node, identifier: str) -> Constant:
    for constant in node.constants:
        if constant.id == identifier:
            return constant
    raise ValueError(f"missing constant.{identifier}")


def _text(value: JsonValue) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("expected non-empty knowledge text")
    return value


def _strings(value: JsonValue) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError("expected a knowledge list")
    return tuple(_text(item) for item in value)


def _rows(value: JsonValue) -> tuple[dict[str, JsonValue], ...]:
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise ValueError("expected knowledge records")
    return tuple(cast(dict[str, JsonValue], row) for row in value)


def _topic_paths(node: Node) -> tuple[str, ...]:
    paths: list[str] = []
    for row in _rows(_constant(node, "topic-router").value):
        if set(row) != {"path", "concern"}:
            raise ValueError("topic router columns differ")
        source = _text(row["path"])
        path = PurePosixPath(source)
        if path.parts[:1] != ("python",) or len(path.parts) != 2 or not source.endswith(".oak.md"):
            raise ValueError("unsafe Python topic path")
        if source != path.as_posix() or "\\" in source:
            raise ValueError("unsafe Python topic path")
        _text(row["concern"])
        paths.append(source)
    if not paths or len(paths) != len(set(paths)):
        raise ValueError("topic routes must be non-empty and unique")
    return tuple(paths)


def _validate_table(table: Mapping[str, JsonValue]) -> None:
    if set(table) != {"columns", "rows"}:
        raise ValueError("table fields differ")
    columns = _strings(table["columns"])
    rows = table["rows"]
    if not columns or not isinstance(rows, list):
        raise ValueError("invalid knowledge table")
    for row in rows:
        if len(_strings(row)) != len(columns):
            raise ValueError("table row width differs")


def _validate_rules(node: Node) -> tuple[str, ...]:
    sections: list[str] = []
    references: list[str] = []
    for rule in _rows(_constant(node, "rules").value):
        if set(rule) != _RULE_FIELDS:
            raise ValueError("rule fields differ")
        sections.append(_text(rule["section"]))
        _text(rule["title"])
        if not _strings(rule["requirements"]) and not rule["examples"]:
            raise ValueError("a rule has no requirements or teaching")
        references.extend(_strings(rule["examples"]))
        for table in _rows(rule["tables"]):
            _validate_table(table)
    _validate_examples(node, tuple(references), tuple(sections))
    return tuple(sections)


def _indexed_examples(node: Node, sections: tuple[str, ...]) -> tuple[str, ...]:
    index = _rows(_constant(node, "example-index").value)
    indexed: list[str] = []
    for row in index:
        if set(row) != _EXAMPLE_FIELDS or _text(row["section"]) not in sections:
            raise ValueError("invalid example index")
        indexed.append(_text(row["id"]))
        for field in ("topic", "language", "scope"):
            _text(row[field])
    _validate_example_owners(node, index)
    return tuple(indexed)


def _validate_example_owners(node: Node, index: tuple[dict[str, JsonValue], ...]) -> None:
    owners = {
        reference: rule["section"]
        for rule in _rows(_constant(node, "rules").value)
        for reference in _strings(rule["examples"])
    }
    for row in index:
        if owners.get("constant." + _text(row["id"])) != row["section"]:
            raise ValueError("example section ownership differs")


def _validate_examples(node: Node, references: tuple[str, ...], sections: tuple[str, ...]) -> None:
    example_constants = {constant.id: constant for constant in node.constants if constant.form == "text"}
    if not references:
        if example_constants:
            raise ValueError("unreferenced code example")
        return
    indexed = _indexed_examples(node, sections)
    expected = Counter("constant." + identifier for identifier in indexed)
    if Counter(references) != expected or any(count != 1 for count in expected.values()):
        raise ValueError("example reference coverage differs")
    if set(indexed) != set(example_constants):
        raise ValueError("example literal coverage differs")
    for constant in example_constants.values():
        _text(constant.value)


def _validate_documents(documents: Mapping[str, str]) -> None:
    entry = parse(documents[_ENTRY])
    if set(documents) != {_ENTRY, *_topic_paths(entry)}:
        raise ValueError("topic route coverage differs")
    owners = [_validate_document(source, text) for source, text in documents.items()]
    _validate_section_coverage(entry, owners)
    sources = {f"{_SOURCE_ROOT}/{source}": text for source, text in documents.items()}
    graph = resolve(entry, source=f"{_SOURCE_ROOT}/{_ENTRY}", load=sources.get, root=_SOURCE_ROOT)
    if set(graph.documents) != set(sources):
        raise ValueError("resolved topic closure differs")


def _validate_document(source: str, text: str) -> tuple[str, tuple[str, ...]]:
    node = parse(text)
    if render(node) != text:
        raise ValueError(f"noncanonical Python knowledge: {source}")
    if node.instructions or node.state or node.triggers or node.interfaces:
        raise ValueError("Python standards must not add hidden policy or mutable execution state")
    if source != _ENTRY and node.processes:
        raise ValueError("topic modules contain fixed knowledge and shapes only")
    concern = _text(_constant(node, "owned-concern").value)
    sections = _validate_rules(node)
    _validate_round_trip(node)
    return concern, sections


def _validate_section_coverage(entry: Node, owners: list[tuple[str, tuple[str, ...]]]) -> None:
    concerns = [concern for concern, _ in owners]
    sections = [section for _, owned_sections in owners for section in owned_sections]
    if len(concerns) != len(set(concerns)) or len(sections) != len(set(sections)):
        raise ValueError("duplicate Python knowledge owner or section")
    original = [section for section in sections if not section.startswith("refinement-")]
    if Counter(original) != Counter(_strings(_constant(entry, "source-sections").value)):
        raise ValueError("source section coverage differs")


def _validate_round_trip(node: Node) -> None:
    for grouping in ("xml", "markdown"):
        rendered = render(node, grouping=grouping)
        if parse(rendered, grouping=grouping) != node:
            raise ValueError("Python knowledge changed during round-trip")


def _changed_constant(documents: Mapping[str, str], source: str, identifier: str, value: JsonValue) -> dict[str, str]:
    changed = dict(documents)
    node = parse(changed[source])
    _constant(node, identifier).value = value
    changed[source] = render(node)
    return changed


def _expect_rejection(documents: Mapping[str, str], reason: str) -> None:
    try:
        _validate_documents(documents)
    except ValueError as error:
        if reason not in str(error):
            raise RuntimeError(f"expected rejection {reason!r}, got {error}") from error
    else:
        raise RuntimeError(f"invalid Python knowledge was accepted: {reason}")


def _validate_rejections(documents: Mapping[str, str]) -> None:
    entry = documents[_ENTRY]
    layout = documents["python/layout.oak.md"]
    missing = dict(documents)
    missing.pop("python/layout.oak.md")
    _expect_rejection(missing, "route coverage")
    _expect_rejection({**documents, "python/unrouted.oak.md": layout}, "route coverage")
    _expect_rejection({**documents, "python/layout.oak.md": layout + "\n"}, "noncanonical")
    escaping = entry.replace("python/naming.oak.md", "../naming.oak.md")
    _expect_rejection({**documents, _ENTRY: escaping}, "unsafe")
    unresolved = entry.replace("#constant.rules", "#constant.missing", 1)
    _expect_rejection({**documents, _ENTRY: unresolved}, "external_entry_missing")
    _validate_rejected_rules(documents)
    _validate_rejected_examples(documents)
    _validate_rejected_symlink(entry)


def _validate_rejected_rules(documents: Mapping[str, str]) -> None:
    source = "python/dependencies.oak.md"
    rules = deepcopy(_rows(_constant(parse(documents[source]), "rules").value))
    missing = _changed_constant(documents, source, "rules", list(rules[:-1]))
    _expect_rejection(missing, "section coverage")
    rules[1]["section"] = rules[0]["section"]
    duplicate = _changed_constant(documents, source, "rules", list(rules))
    _expect_rejection(duplicate, "duplicate")
    malformed = _changed_constant(documents, source, "rules", "not records")
    _expect_rejection(malformed, "knowledge records")


def _validate_rejected_examples(documents: Mapping[str, str]) -> None:
    source = "python/layout.oak.md"
    empty = _changed_constant(documents, source, "example-3-6-1", "")
    _expect_rejection(empty, "non-empty knowledge text")
    index = deepcopy(_rows(_constant(parse(documents[source]), "example-index").value))
    index[0]["section"] = index[1]["section"]
    swapped = _changed_constant(documents, source, "example-index", list(index))
    _expect_rejection(swapped, "ownership differs")
    index[0]["section"] = 3.6
    numeric = _changed_constant(documents, source, "example-index", list(index))
    _expect_rejection(numeric, "non-empty knowledge text")


def _validate_rejected_symlink(entry: str) -> None:
    with TemporaryDirectory(prefix="oak-python-rules-") as temporary:
        directory = Path(temporary)
        target = directory / "target.oak.md"
        target.write_text(entry, encoding="utf-8")
        (directory / _ENTRY).symlink_to(target)
        try:
            _read_documents(directory)
        except ValueError as error:
            if "symbolic" not in str(error):
                raise
        else:
            raise RuntimeError("symbolic Python knowledge was accepted")


def _validate_shapes(documents: Mapping[str, str]) -> None:
    layout = parse(documents["python/layout.oak.md"])
    before = _text(_constant(layout, "example-literal-whitespace-before").value)
    after = _text(_constant(layout, "example-literal-whitespace-after").value)
    before_assignment, = ast.parse(before).body
    after_assignment, = ast.parse(after).body
    if not isinstance(before_assignment, ast.Assign) or not isinstance(after_assignment, ast.Assign):
        raise ValueError("literal whitespace examples must each contain one assignment")
    expected = "Balance: <BALANCE>\nFactor: <FACTOR>"
    if ast.literal_eval(before_assignment.value) != expected or ast.literal_eval(after_assignment.value) != expected:
        raise ValueError("literal whitespace example changed its independent expected text")
    comparison = parse(documents["python/documentation.oak.md"]).schemas[0]
    comparison.bind({
        "POINT": "Literal whitespace", "PROVIDES": "Identical template bytes", "BEFORE": before, "AFTER": after,
    })
    complexity = parse(documents["python/verification.oak.md"]).schemas[0]
    complexity.bind({
        "FUNCTION": "example", "BEFORE": 1, "AFTER": 1, "METHOD": "schema fixture, not a measurement",
        "EXTRACTED": "none", "VERIFICATION": "not run; this checks the report shape only",
    })
