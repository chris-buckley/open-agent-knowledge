"""Generate the OAK meta-grammar from text syntax and surfaces."""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
import sys
from textwrap import fill

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build._ebnf_layout import _format_group
from build.surfaces import surface_grammar
from oak.node.structure import PART_ORDER
from oak.surface import SURFACES
from oak.surface.syntax import EXPRESSION_CONVENTIONS, EXPRESSION_GRAMMAR
from oak.node.parts.processes.operators import OPERATOR_TEXT
from oak.vocabulary.text.dotted_path import DOTTED_PATH_EBNF
from oak.vocabulary.text.non_blank_line import NON_BLANK_LINE_SYNTAX
from oak.vocabulary.text.placeholder import PLACEHOLDER_SYNTAX
from oak.vocabulary.text.process_name import PROCESS_NAME_SYNTAX
from oak.vocabulary.text.regex_pattern import REGEX_PATTERN_SYNTAX
from oak.vocabulary.text.slug_id import SLUG_ID_SYNTAX
from oak.vocabulary.text.target_path import ENTRY_PART_EBNF, ENTRY_PATH_EBNF, RELATIVE_DOCUMENT_PATH_EBNF, TARGET_PATH_EBNF
from oak.vocabulary.text.value_reference import VALUE_REFERENCE_EBNF

TARGET = ROOT / "outputs" / "oak.ebnf"


def _document(prefix: str) -> list[str]:
    lines = [f"{prefix}_document = [ {prefix}_parts_from_{PART_ORDER[0]} ] ;"]
    for index, part in enumerate(PART_ORDER):
        name = f"{prefix}_parts_from_{part}"
        if index + 1 < len(PART_ORDER):
            successor = f"{prefix}_parts_from_{PART_ORDER[index + 1]}"
            lines.append(f"{name} = {prefix}_{part}_part, [ blank_line, {successor} ] | {successor} ;")
        else:
            lines.append(f"{name} = {prefix}_{part}_part ;")
    return lines


def _parts(prefix: str) -> list[str]:
    if prefix == "xml":
        return [
            f'xml_{part}_part = "<{part}>", lf, text_body, "</{part}>" ;'
            for part in PART_ORDER
        ]
    return [
        f'markdown_{part}_part = "~~~~{part}", lf, text_body, "~~~~" ;'
        for part in PART_ORDER
    ]


_BODY_ENTRIES = {
    "xml": 'xml_body_entry = "<", entry_tag, attributes, ">", lf, text_body, "</", entry_tag, ">" ;',
    "markdown": 'markdown_body_entry = "~~~", entry_tag, markdown_attributes, lf, text_body, "~~~" ;',
}

_ATTRIBUTES = {
    "xml": "attributes = ? zero or more XML-like string attributes ? ;",
    "markdown": "markdown_attributes = ? zero or more semicolon JSON-string attributes ? ;",
}


@dataclass(frozen=True, slots=True, kw_only=True)
class _Production:
    source: str
    text: str


def _records(owner: str, productions: Iterable[str]) -> tuple[_Production, ...]:
    return tuple(_Production(source=owner + ":" + text.partition(" = ")[0], text=text)
                 for text in productions)


def _source_productions(groupings: tuple[str, ...]) -> tuple[_Production, ...]:
    """Retain every source-qualified occurrence, including the baseline duplicate."""
    scaffold = [
        "oak_document = " + " | ".join(f"{grouping}_document" for grouping in groupings) + " ;",
        *[line for grouping in groupings for line in (*_document(grouping), *_parts(grouping))],
        *[_BODY_ENTRIES[grouping] for grouping in groupings],
        'entry_tag = "schema" | "process" ;',
        'comparison_operator = ' + ' | '.join('"' + text + '"' for text in OPERATOR_TEXT.values()) + ' ;',
        "constant = inline_constant | text_constant | json_constant | csv_constant | yaml_constant ;",
        'inline_constant = slug_id, [ as_clause ], ": ", json_value ;',
        'text_constant = slug_id, [ as_clause ], ": TEXT<<", lf, text_body, ">>" ;',
        'json_constant = slug_id, [ as_clause ], ": JSON<<", lf, json_value, lf, ">>" ;',
        'csv_constant = slug_id, [ as_clause ], ": CSV<<", lf, csv_body, lf, ">>" ;',
        'yaml_constant = slug_id, [ as_clause ], ": YAML<<", lf, yaml_body, lf, ">>" ;',
        'state_entry = slug_id, [ as_clause ], ": ", json_value ;',
        'as_clause = " AS ", schema_placeholder_path ;',
        'schema_placeholder_path = [ relative_document_path, "#" ], "schema", ".", slug_id, ".", placeholder ;',
        "json_value = ? one JSON value ? ;",
        "csv_body = ? one CSV header and one or more data rows ? ;",
        "yaml_body = ? one YAML value ? ;",
        *[_ATTRIBUTES[grouping] for grouping in groupings],
        "text_body = { text_line, lf } ;",
        "text_line = ? any character except CR or LF ? ;",
        "blank_line = lf, lf ;",
        "lf = ? U+000A LINE FEED ? ;",
    ]
    vocabulary = (
        ("SLUG_ID_SYNTAX", SLUG_ID_SYNTAX.production),
        ("NON_BLANK_LINE_SYNTAX", NON_BLANK_LINE_SYNTAX.production),
        ("PROCESS_NAME_SYNTAX", PROCESS_NAME_SYNTAX.production),
        ("PLACEHOLDER_SYNTAX", PLACEHOLDER_SYNTAX.production),
        ("REGEX_PATTERN_SYNTAX", REGEX_PATTERN_SYNTAX.production),
        ("DOTTED_PATH_EBNF", DOTTED_PATH_EBNF),
        ("VALUE_REFERENCE_EBNF", VALUE_REFERENCE_EBNF),
        ("ENTRY_PART_EBNF", ENTRY_PART_EBNF),
        ("ENTRY_PATH_EBNF", ENTRY_PATH_EBNF),
        ("RELATIVE_DOCUMENT_PATH_EBNF", RELATIVE_DOCUMENT_PATH_EBNF),
        ("TARGET_PATH_EBNF", TARGET_PATH_EBNF),
    )
    records = list(_records("scaffold", scaffold))
    records.extend(_records("expression", EXPRESSION_GRAMMAR))
    for owner, text in vocabulary:
        records.extend(_records("vocabulary." + owner, text.splitlines()))
    for surface in SURFACES:
        records.extend(_records("surface." + surface.id, (surface_grammar(surface),)))
    return tuple(records)



def _comment(text: str) -> str:
    return "(* " + "\n".join(fill(line, width=94) for line in text.splitlines()) + " *)"


# Ordinals refer to the unchanged, pinned package's convention tuple. Structural
# claims already expressed by these productions need no second prose definition.
_CONVENTION_SECTIONS = (
    "conditions", "conditions", "conditions", "processes", "processes", "processes",
    "processes", "lexical", "values", "triggers", "triggers", "triggers", "triggers",
    "lexical", "lexical", "values", "values", "values", "values",
)
_STRUCTURAL_CONVENTIONS = {
    0: ("condition", "if_statement", "while_statement", "assert_statement", "trigger_field"),
    1: ("all_condition", "any_condition", "not_condition"),
    3: ("if_statement", "while_statement", "suite", "indent"),
    4: ("if_statement", "suite", "dedent", "logical_nl"),
    6: ("assert_statement", "indent", "dedent"),
    7: ("logical_nl", "suite", "condition", "binding_list"),
    8: ("binding_list", "all_condition", "any_condition", "not_condition", "trigger_declaration", "json_value"),
}


def _notes(section: str, extra: str = "") -> str:
    notes = [text for index, (owner, text) in enumerate(zip(
        _CONVENTION_SECTIONS, EXPRESSION_CONVENTIONS, strict=True,
    )) if owner == section and index not in _STRUCTURAL_CONVENTIONS]
    if extra:
        notes.append(extra)
    return _comment("\n".join(notes))


def _arrange(productions: Iterable[_Production], groupings: tuple[str, ...]) -> str:
    """Place every occurrence once; refuse unassigned or multiply assigned sources."""
    pending: dict[str, deque[str]] = defaultdict(deque)
    for production in productions:
        pending[production.source].append(production.text)

    def group(owner: str, names: str, *, alignment: int = 0) -> str:
        keys = [owner + ":" + name for name in names.split()]
        missing = [key for key in keys if not pending[key]]
        if missing:
            raise ValueError(f"EBNF layout needs source occurrences: {missing}")
        return _format_group([pending[key].popleft() for key in keys], alignment)

    def surface(identifier: str) -> str:
        return group("surface." + identifier, "surface_" + identifier.replace("-", "_"))

    def surfaces(identifiers: str) -> str:
        return "\n".join(surface(identifier) for identifier in identifiers.split())

    def vocabulary(owner: str, names: str) -> str:
        return group("vocabulary." + owner, names)

    sections = [
        _comment("Scope and notation\nSyntax, not validation or host evaluation.\n"
                 "?...? is descriptive; opaque rules may exceed width 100."),
        _comment("01. Lexical tokens and whitespace\nSpace words; punctuation acts unquoted at its depth."),
        group("scaffold", "lf blank_line text_line text_body"),
        group("expression", "logical_nl indent dedent positive_integer json_string"),
        _notes("lexical"),
        "\n".join((
            vocabulary("SLUG_ID_SYNTAX", "slug_id"),
            vocabulary("NON_BLANK_LINE_SYNTAX", "non_blank_line"),
            vocabulary("PROCESS_NAME_SYNTAX", "process_name"),
            vocabulary("PLACEHOLDER_SYNTAX", "placeholder"),
            vocabulary("REGEX_PATTERN_SYNTAX", "regex_pattern"),
        )),
        _comment("02. Values, targets and bindings\n$ adjoins targets; JSON owns spacing/delimiters."),
        group("scaffold", "json_value"),
        group("expression", "process_value value_target", alignment=len("output_bindings")),
        group("expression", "value_binding binding_list output_bindings", alignment=len("output_bindings")),
        _notes("values"),
        group("expression", "constant_target process_target local_state_target local_interface_target"),
        vocabulary("DOTTED_PATH_EBNF", "dotted_path"),
        vocabulary("ENTRY_PART_EBNF", "entry_part"),
        vocabulary("ENTRY_PATH_EBNF", "entry_path"),
        vocabulary("RELATIVE_DOCUMENT_PATH_EBNF", "relative_document_path"),
        vocabulary("TARGET_PATH_EBNF", "target_path"),
        vocabulary("VALUE_REFERENCE_EBNF", "value_reference constant_target state_target"),
        group("scaffold", "as_clause schema_placeholder_path"),
        surfaces("value-literal value-constant value-state value-binding value-binding-line"),
        _comment("03. Conditions"),
        group("expression", "condition comparison all_condition any_condition not_condition"),
        group("scaffold", "comparison_operator"),
        _notes("conditions"),
        surfaces("condition-compare condition-all condition-any condition-not"),
        _comment("04. Part contents"),
        _comment("Instructions"), surface("instruction"),
        _comment("Constants"),
        group("scaffold", "constant inline_constant text_constant json_constant csv_constant yaml_constant"),
        group("scaffold", "csv_body yaml_body"),
        surfaces("constant-inline constant-text constant-json constant-csv constant-yaml"),
        _comment("Schemas"), surface("schema"), surface("where"),
        surfaces("constraint-type constraint-one-of constraint-regex constraint-non-empty constraint-max-chars "
                 "constraint-lines constraint-list-of constraint-at-least constraint-at-most"),
        _comment("State"), group("scaffold", "state_entry"), surface("state"),
        _comment("Triggers"),
        group("expression", "trigger_declaration"), group("expression", "trigger_field"),
        _notes("triggers", "Decode events to nonblank single lines. Guards read state; no empty EMIT bindings."),
        surface("trigger"),
        _comment("Processes"),
        group("expression", "process_statement"), group("expression", "suite"),
        _notes("processes"),
    ]
    for kind in ("if", "while", "assert", "call", "emit", "set", "fail"):
        statement = group("expression", kind + "_statement")
        aliases = ("statement-emit-inferred", "statement-emit-explicit") if kind == "emit" else ("statement-" + kind,)
        sections.append("\n".join([statement, *(surface(identifier) for identifier in aliases)]))
    sections.extend([
        _comment("Descriptive surfaces:"),
        surfaces("act-native act-tool statement-foreach statement-par statement-join process"),
        _comment("Interfaces"), surface("interface-receives"), surface("interface-emits"),
        *_grouping_sections(groupings, group),
        surface("node"),
    ])
    if unassigned := [key for key, texts in pending.items() if texts]:
        raise ValueError(f"Unassigned EBNF source occurrences: {unassigned}")
    return _join_sections(sections)


def _grouping_sections(groupings: tuple[str, ...], group: Callable[[str, str], str]) -> list[str]:
    sections = [_comment("05. XML and Markdown grouping"), group("scaffold", "entry_tag")]
    for grouping in groupings:
        sections.extend([
            group("scaffold", " ".join(f"{grouping}_{part}_part" for part in PART_ORDER)),
            group("scaffold", grouping + "_body_entry"),
            group("scaffold", "attributes" if grouping == "xml" else "markdown_attributes"),
        ])
    sections.extend([_comment("06. Complete document\nOmit empty parts."), group("scaffold", "oak_document")])
    for grouping in groupings:
        sections.append(group("scaffold", " ".join(line.partition(" = ")[0] for line in _document(grouping))))
    return sections


def _join_sections(sections: list[str]) -> str:
    headings = {_comment(title) for title in (
        *[part.title() for part in PART_ORDER], "03. Conditions", "04. Part contents",
        "05. XML and Markdown grouping", "Descriptive surfaces:",
    )}
    return "".join(section + ("\n" if section in headings else "\n\n")
                   for section in sections).rstrip("\n") + "\n"



def grammar(groupings: tuple[str, ...] = ("xml", "markdown")) -> str:
    """Return the generated EBNF snapshot for the named groupings."""
    return _arrange(_source_productions(groupings), groupings)


def ebnf_text() -> str:
    """Return the generated grammar snapshot."""
    return grammar()


def write() -> Path:
    """Write the generated grammar snapshot."""
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(grammar(), encoding="utf-8", newline="\n")
    return TARGET


def build() -> Path:
    """Write the generated grammar snapshot."""
    return write()


if __name__ == "__main__":
    print(f"wrote {write()}")
