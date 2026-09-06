"""Independent EBNF content, presentation, source-coverage and delivery checks."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from hashlib import sha256
import json
import re

from build._ebnf_layout import _format_production, _outer_parts
from build.checks.ebnf_fixtures import (
    DUPLICATE_SPECIMENS, FOREACH_SPECIMEN, GROUPING_FINGERPRINTS, HEADINGS,
    SOURCE_FINGERPRINT, STATEMENT_SPECIMEN, TRIGGER_SPECIMEN, VALUE_SPECIMEN,
    WIDTH_EXCEPTIONS,
)
from build.checks.fixtures import ROOT
from build.ebnf import (
    _arrange, _CONVENTION_SECTIONS, _Production, _source_productions,
    _STRUCTURAL_CONVENTIONS, ebnf_text, grammar,
)
from build.surfaces import surface_grammar
from oak import parse
from oak.surface import SURFACES
from oak.surface.syntax import EXPRESSION_CONVENTIONS

# This reader is independent of the presentation scanner. Complete literal tokens,
# including internal whitespace and escaped question marks, remain indivisible.
_TOKEN = re.compile(
    r'(?P<comment>\(\*[\s\S]*?\*\))'
    r'|(?P<literal>"(?:\\.|[^"\\])*")'
    r'|(?P<class>\? \[[^\n]*?\] \?)'
    r'|(?P<special>\?(?:\?\?|[^?])*\?)'
    r'|(?P<name>[a-z][a-z0-9_]*)'
    r'|(?P<punct>[=;,|()\[\]{}])'
    r'|(?P<space>\s+)'
    r'|(?P<invalid>.)',
    re.DOTALL,
)
_DEFINITION = re.compile(r"([a-z][a-z0-9_]*)\s*=")
_DEFAULT = ("xml", "markdown")
_PLACEMENT = {
    "lexical": ("01. Lexical tokens and whitespace", "02. Values, targets and bindings"),
    "values": ("02. Values, targets and bindings", "03. Conditions"),
    "conditions": ("03. Conditions", "04. Part contents"),
    "triggers": ("Triggers", "Processes"),
    "processes": ("Processes", "Interfaces"),
}


def _productions(text: str) -> list[tuple[str, ...]]:
    """Read documented tokens, not OAK syntax or general EBNF semantics."""
    records: list[tuple[str, ...]] = []
    tokens: list[str] = []
    for match in _TOKEN.finditer(text):
        kind, token = match.lastgroup, match[0]
        if kind == "invalid":
            raise ValueError(f"Unexpected EBNF text: {token!r}")
        if kind in ("space", "comment"):
            continue
        tokens.append(token)
        if token == ";":
            if len(tokens) < 4 or tokens[1] != "=":
                raise ValueError("EBNF definition needs a name, equals sign and body")
            records.append(tuple(tokens))
            tokens = []
    if tokens:
        raise ValueError("Unterminated EBNF definition")
    return records


def _fingerprint(records: object) -> str:
    encoded = json.dumps(records, ensure_ascii=False, separators=(",", ":")).encode()
    return sha256(encoded).hexdigest()


def _check_content(text: str, groupings: tuple[str, ...]) -> None:
    tokens = _productions(text)
    if _fingerprint(sorted(tokens)) != GROUPING_FINGERPRINTS[groupings]:
        raise ValueError("EBNF production content changed from the reviewed baseline")
    counts = Counter(production[0] for production in tokens)
    if {name: count for name, count in counts.items() if count > 1} != {"constant_target": 2}:
        raise ValueError("EBNF baseline duplicate multiplicity changed")


def _check_layout(text: str) -> None:
    headings = re.findall(r"^\(\* ([^\n]*?)(?: \*\))?$", text, re.MULTILINE)
    if tuple(title for title in headings if title in HEADINGS or re.match(r"[0-9]{2}\.", title)) != HEADINGS:
        raise ValueError("EBNF section order changed")
    for specimen in (VALUE_SPECIMEN, TRIGGER_SPECIMEN, STATEMENT_SPECIMEN, FOREACH_SPECIMEN):
        if specimen not in text:
            raise ValueError("EBNF required layout specimen changed")
    if not text.endswith("\n") or text.endswith("\n\n") or "\r" in text:
        raise ValueError("EBNF needs LF text and exactly one final LF")
    _check_width(text)
    _check_note_placement(text)
    _check_surface_placement(text)


def _check_width(text: str) -> None:
    for line in text.splitlines():
        if len(line) > 100:
            definition = _DEFINITION.match(line)
            if definition is None or definition[1] not in WIDTH_EXCEPTIONS:
                raise ValueError("EBNF exceeds soft width outside an opaque exception")


def _check_note_placement(text: str) -> None:
    names = {tokens[0] for tokens in _productions(text)}
    if tuple(sorted(_STRUCTURAL_CONVENTIONS)) != (0, 1, 3, 4, 6, 7, 8):
        raise ValueError("EBNF structural convention coverage changed")
    for index, (owner, note) in enumerate(zip(_CONVENTION_SECTIONS, EXPRESSION_CONVENTIONS, strict=True)):
        if index in _STRUCTURAL_CONVENTIONS:
            if not set(_STRUCTURAL_CONVENTIONS[index]) <= names:
                raise ValueError("EBNF structural convention lost its production evidence")
            continue
        start, end = _PLACEMENT[owner]
        section = text.split("(* " + start, 1)[1].split("(* " + end, 1)[0]
        if note not in " ".join(section.split()):
            raise ValueError(f"EBNF note is misplaced: {owner}: {note}")


def _check_surface_placement(text: str) -> None:
    owners = {
        "value": "02. Values, targets and bindings", "condition": "03. Conditions",
        "constraint": "Schemas", "where": "Schemas", "schema": "Schemas",
        "instruction": "Instructions", "constant": "Constants", "state": "State",
        "trigger": "Triggers", "act": "Processes", "statement": "Processes",
        "process": "Processes", "interface": "Interfaces", "node": "06. Complete document",
    }
    headings = [(text.index("(* " + heading), heading) for heading in HEADINGS]
    for surface in SURFACES:
        definition = "surface_" + surface.id.replace("-", "_") + " ="
        position = text.index(definition)
        section = max((offset, name) for offset, name in headings if offset < position)[1]
        if section != owners[surface.id.split("-", 1)[0]]:
            raise ValueError(f"EBNF surface is misplaced: {surface.id}")


def _check_sources() -> None:
    records = _source_productions(_DEFAULT)
    observed = sorted((record.source, _productions(record.text)[0]) for record in records)
    if _fingerprint(observed) != SOURCE_FINGERPRINT:
        raise ValueError("EBNF source-qualified occurrence inventory changed")
    if Counter(_productions(grammar())) != Counter(tokens for _, tokens in observed):
        raise ValueError("EBNF layout lost or rewrote a source occurrence")
    for surface in SURFACES:
        source = _productions(surface_grammar(surface))[0]
        if source not in _productions(grammar()):
            raise ValueError(f"EBNF surface is missing: {surface.id}")


def _check_groupings(text: str, groupings: tuple[str, ...]) -> None:
    names = {tokens[0] for tokens in _productions(text)}
    for grouping in _DEFAULT:
        selected = grouping in groupings
        if (grouping + "_body_entry" in names) != selected:
            raise ValueError("EBNF wrapper selection changed")
    entry = next(tokens for tokens in _productions(text) if tokens[0] == "oak_document")
    if tuple(token for token in entry[2:] if token.endswith("_document")) != tuple(
        grouping + "_document" for grouping in groupings
    ):
        raise ValueError("EBNF caller-supplied grouping order changed")
    _check_grouping_order(text, groupings)


def _check_grouping_order(text: str, groupings: tuple[str, ...]) -> None:
    for previous, following in zip(groupings, groupings[1:]):
        for suffix in ("_instructions_part =", "_document = ["):
            if text.index(previous + suffix) >= text.index(following + suffix):
                raise ValueError("EBNF wrapper or document placement order changed")


def _expect_rejection(check: Callable[[], object], reason: str) -> None:
    try:
        check()
    except ValueError as error:
        if reason not in str(error):
            raise RuntimeError(f"Expected {reason!r}, received {error}") from error
        return
    raise RuntimeError(f"EBNF corruption was accepted: {reason}")


def _check_corruptions(text: str) -> None:
    variants = (
        text.replace('    | fail_statement\n', '', 1),
        text.replace('    | while_statement\n    | assert_statement',
                     '    | assert_statement\n    | while_statement', 1),
        text.replace('process_statement =\n', 'renamed_statement =\n', 1),
        text.replace('"process", "=", process_target', '"process", ":", process_target', 1),
        text.replace('"does not equal"', '"does  not equal"', 1),
        text.replace(FOREACH_SPECIMEN, FOREACH_SPECIMEN.replace('  <BODY>', '    <BODY>'), 1),
        text.replace(DUPLICATE_SPECIMENS[0] + '\n', '', 1),
        text + DUPLICATE_SPECIMENS[0] + '\n',
    )
    for corrupted in variants:
        if corrupted == text:
            raise RuntimeError("EBNF negative fixture did not mutate its subject")
        _expect_rejection(lambda: _check_content(corrupted, _DEFAULT), "production content")
    layouts = (
        text.replace('(* 03. Conditions *)', '(* 03. Wrong section *)', 1),
        text.replace('process_value   =', 'process_value =', 1),
        text.replace('      if_statement', '    if_statement', 1),
        text.rstrip('\n'), text + '\n', text.replace('\n', '\r\n'),
        text.replace('(* 03. Conditions *)', '(* 07. Extra section *)\n(* 03. Conditions *)'),
        text.replace('WHILE requires LIMIT and one positive decimal integer literal;', 'WHILE requires LIMIT;'),
        text.replace(FOREACH_SPECIMEN + '\n', '').replace('(* State *)', FOREACH_SPECIMEN + '\n(* State *)'),
    )
    for corrupted in layouts:
        _expect_rejection(lambda: _check_layout(corrupted), "EBNF")
    records = _source_productions(_DEFAULT)
    unknown = _Production(source="surface.unassigned:surface_unassigned", text='surface_unassigned = "x" ;')
    for invalid in ((*records, unknown), (*records, records[0])):
        _expect_rejection(lambda: _arrange(invalid, _DEFAULT), "Unassigned EBNF source occurrences")
    _expect_rejection(lambda: _arrange(records[1:], _DEFAULT), "needs source occurrences")


def _check_literals() -> None:
    quoted = r'quoted = "pipe|comma,semi;quote\"question?", { "x", [ "[", "]" ] } | "other" ;'
    long_quoted = quoted.replace('"other"', '"' + 'literal,|; ' * 12 + '"')
    special = 'special = ? comma, pipe| semi; quote" escaped??\n  <BODY> (* literal *) ? ;'
    for source in (quoted, long_quoted, special):
        formatted = _format_production(source)
        if _productions(source) != _productions(formatted):
            raise RuntimeError("EBNF fixture literals changed")
    if _format_production(special) != special:
        raise RuntimeError("EBNF descriptive body was reformatted")
    for surface in SURFACES:
        projected = surface_grammar(surface)
        if ' = ? ' in projected and _format_production(projected) != projected:
            raise RuntimeError(f"EBNF opaque surface changed: {surface.id}")
    for invalid, reason in (('"open', 'terminal is not closed'), ('[ "x"', 'group is not closed'),
                            ('[ "x" }', 'delimiters do not match')):
        _expect_rejection(lambda: _outer_parts(invalid, ','), reason)
    _expect_rejection(lambda: _format_production('invalid = "x"'), 'final semicolon')


def _check_deliveries() -> None:
    expected = grammar()
    for path in ('generated/oak.ebnf', 'generated/oak-authoring.skill/references/oak.ebnf'):
        if (ROOT / path).read_bytes() != expected.encode():
            raise ValueError(f"EBNF delivery differs: {path}")
    for path in ('generated/oak-authoring.skill/references/00-structure.oak.md', 'generated/oak-authoring.oak.md'):
        node = parse((ROOT / path).read_text(encoding="utf-8"))
        values = [entry.value for entry in node.constants
                  if entry.id == 'oak-ebnf' or entry.id.endswith('-oak-ebnf')]
        if values != [expected.rstrip('\n')]:
            raise ValueError(f"EBNF embedded delivery differs: {path}")
    for path, limit in (('generated/oak-authoring.skill/SKILL.md', 10_000), ('generated/oak-authoring.oak.md', 64_000)):
        if len((ROOT / path).read_bytes()) > limit:
            raise ValueError(f"EBNF delivery exceeds existing budget: {path}")


def validate_ebnf() -> None:
    """Verify layout without granting EBNF authority over OAK validation."""
    _check_sources()
    for groupings in GROUPING_FINGERPRINTS:
        text = grammar(groupings)
        _check_content(text, groupings)
        _check_layout(text)
        _check_groupings(text, groupings)
        if text != grammar(groupings):
            raise RuntimeError("EBNF generation is nondeterministic")
    if ebnf_text() != grammar():
        raise RuntimeError("EBNF default callable contracts differ")
    _check_corruptions(grammar())
    _check_literals()
    _check_deliveries()
