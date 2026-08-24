"""Generate the OAK meta-grammar."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak.render.oak.arrangement import PART_ORDER
from oak.vocabulary.text.dotted_path import DOTTED_PATH_SYNTAX
from oak.vocabulary.text.non_blank_line import NON_BLANK_LINE_SYNTAX
from oak.vocabulary.text.placeholder import PLACEHOLDER_SYNTAX
from oak.vocabulary.text.process_name import PROCESS_NAME_SYNTAX
from oak.vocabulary.text.regex_pattern import REGEX_PATTERN_SYNTAX
from oak.vocabulary.text.slug_id import SLUG_ID_SYNTAX
from oak.vocabulary.text.value_reference import VALUE_REFERENCE_SYNTAX

TARGET = ROOT / "outputs" / "oak.ebnf"
_TEXT_RULES = (
    SLUG_ID_SYNTAX,
    NON_BLANK_LINE_SYNTAX,
    PROCESS_NAME_SYNTAX,
    PLACEHOLDER_SYNTAX,
    DOTTED_PATH_SYNTAX,
    VALUE_REFERENCE_SYNTAX,
    REGEX_PATTERN_SYNTAX,
)


def _sequence(prefix: str) -> str:
    return ", blank_line, ".join(
        f"{prefix}_{part}_part"
        for part in PART_ORDER
    )


def _parts(prefix: str) -> list[str]:
    if prefix == "xml":
        return [
            (
                f'xml_{part}_part = "<{part}>", lf, '
                f'text_body, "</{part}>" ;'
            )
            for part in PART_ORDER
        ]

    return [
        (
            f'markdown_{part}_part = "~~~~{part}", lf, '
            f'text_body, "~~~~" ;'
        )
        for part in PART_ORDER
    ]


def grammar() -> str:
    """Return the generated OAK EBNF snapshot."""
    lines = [
        "oak_document = xml_node | markdown_node ;",
        (
            "xml_node = xml_parts, { blank_line, \"<node>\", lf, "
            "xml_node, lf, \"</node>\" } ;"
        ),
        f"xml_parts = {_sequence('xml')} ;",
        *_parts("xml"),
        (
            "markdown_node = markdown_parts, "
            "{ blank_line, markdown_node_block } ;"
        ),
        f"markdown_parts = {_sequence('markdown')} ;",
        *_parts("markdown"),
        (
            "markdown_node_block = markdown_node_fence, \"node\", lf, "
            "markdown_node, lf, markdown_node_fence ;"
        ),
        'markdown_node_fence = "~~~~~", { "~" } ;',
        (
            "constant = inline_constant | text_constant | json_constant | "
            "csv_constant | yaml_constant ;"
        ),
        'inline_constant = slug_id, ": ", json_value ;',
        (
            'text_constant = slug_id, ": TEXT<<", lf, text_body, ">>" ;'
        ),
        (
            'json_constant = slug_id, ": JSON<<", lf, json_value, lf, ">>" ;'
        ),
        (
            'csv_constant = slug_id, ": CSV<<", lf, csv_body, lf, ">>" ;'
        ),
        (
            'yaml_constant = slug_id, ": YAML<<", lf, yaml_body, lf, ">>" ;'
        ),
        "json_value = ? one JSON value ? ;",
        "csv_body = ? one CSV header and one or more data rows ? ;",
        "yaml_body = ? one YAML value ? ;",
        "text_body = { text_line, lf } ;",
        "text_line = ? any character except CR or LF ? ;",
        "blank_line = lf, lf ;",
        "lf = ? U+000A LINE FEED ? ;",
        "",
        *(rule.production for rule in _TEXT_RULES),
    ]
    return "\n".join(lines) + "\n"


def ebnf_text() -> str:
    """Return the generated OAK EBNF snapshot."""
    return grammar()


def write() -> Path:
    """Write the generated grammar snapshot."""
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        grammar(),
        encoding="utf-8",
        newline="\n",
    )
    return TARGET


def build() -> Path:
    """Write the generated grammar snapshot."""
    return write()


if __name__ == "__main__":
    print(f"wrote {write()}")
