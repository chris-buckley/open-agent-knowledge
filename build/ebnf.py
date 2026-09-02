"""Generate the OAK meta-grammar from text syntax and surfaces."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build.surfaces import surface_grammar
from oak.render.oak.arrangement import PART_ORDER
from oak.surface import SURFACES
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
        return [f'xml_{part}_part = "<{part}>", lf, text_body, "</{part}>" ;' for part in PART_ORDER]
    return [f'markdown_{part}_part = "~~~~{part}", lf, text_body, "~~~~" ;' for part in PART_ORDER]


_BODY_ENTRIES = {
    "xml": 'xml_body_entry = "<", entry_tag, attributes, ">", lf, text_body, "</", entry_tag, ">" ;',
    "markdown": 'markdown_body_entry = "~~~", entry_tag, markdown_attributes, lf, text_body, "~~~" ;',
}

_ATTRIBUTES = {
    "xml": "attributes = ? zero or more XML-like string attributes ? ;",
    "markdown": "markdown_attributes = ? zero or more semicolon JSON-string attributes ? ;",
}


def grammar(groupings: tuple[str, ...] = ("xml", "markdown")) -> str:
    """Return the generated EBNF snapshot for the named groupings."""
    lines = [
        "oak_document = " + " | ".join(f"{grouping}_document" for grouping in groupings) + " ;",
        "(* an empty part is omitted from the render *)",
        *[line for grouping in groupings for line in (*_document(grouping), *_parts(grouping))],
        *[_BODY_ENTRIES[grouping] for grouping in groupings],
        'entry_tag = "schema" | "process" | "interface" ;',
        'trigger_fact = "trigger.", slug_id, ".", trigger_field, " := ", trigger_value ;',
        'trigger_field = "event" | "source" | "guard" | "process" | ( "seed.", placeholder ) ;',
        "trigger_value = ? one field-typed value; a composite guard continues on indented condition lines ? ;",
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
        "",
        SLUG_ID_SYNTAX.production,
        NON_BLANK_LINE_SYNTAX.production,
        PROCESS_NAME_SYNTAX.production,
        PLACEHOLDER_SYNTAX.production,
        DOTTED_PATH_EBNF,
        VALUE_REFERENCE_EBNF,
        ENTRY_PART_EBNF,
        ENTRY_PATH_EBNF,
        RELATIVE_DOCUMENT_PATH_EBNF,
        TARGET_PATH_EBNF,
        REGEX_PATTERN_SYNTAX.production,
        "",
        *(surface_grammar(surface) for surface in SURFACES),
    ]
    return "\n".join(lines) + "\n"


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
