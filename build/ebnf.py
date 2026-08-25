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


def _sequence(prefix: str) -> str:
    return ", blank_line, ".join(f"{prefix}_{part}_part" for part in PART_ORDER)


def _parts(prefix: str) -> list[str]:
    if prefix == "xml":
        return [f'xml_{part}_part = "<{part}>", lf, text_body, "</{part}>" ;' for part in PART_ORDER]
    return [f'markdown_{part}_part = "~~~~{part}", lf, text_body, "~~~~" ;' for part in PART_ORDER]


def grammar() -> str:
    """Return the generated OAK EBNF snapshot."""
    lines = [
        "oak_document = xml_document | markdown_document ;",
        f"xml_document = {_sequence('xml')} ;",
        *_parts("xml"),
        f"markdown_document = {_sequence('markdown')} ;",
        *_parts("markdown"),
        'xml_body_entry = "<", entry_tag, attributes, ">", lf, text_body, "</", entry_tag, ">" ;',
        'markdown_body_entry = "~~~", entry_tag, markdown_attributes, lf, text_body, "~~~" ;',
        'entry_tag = "schema" | "trigger" | "process" | "interface" ;',
        "constant = inline_constant | text_constant | json_constant | csv_constant | yaml_constant ;",
        'inline_constant = slug_id, ": ", json_value ;',
        'text_constant = slug_id, ": TEXT<<", lf, text_body, ">>" ;',
        'json_constant = slug_id, ": JSON<<", lf, json_value, lf, ">>" ;',
        'csv_constant = slug_id, ": CSV<<", lf, csv_body, lf, ">>" ;',
        'yaml_constant = slug_id, ": YAML<<", lf, yaml_body, lf, ">>" ;',
        "json_value = ? one JSON value ? ;",
        "csv_body = ? one CSV header and one or more data rows ? ;",
        "yaml_body = ? one YAML value ? ;",
        "attributes = ? zero or more XML-like string attributes ? ;",
        "markdown_attributes = ? zero or more semicolon JSON-string attributes ? ;",
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
