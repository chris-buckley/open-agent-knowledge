"""TargetPath: one local entry or one relative document entry target."""

import re
from typing import Annotated

from pydantic import AfterValidator, StringConstraints
from pydantic_core import PydanticCustomError

from oak.vocabulary.text.slug_id import SLUG_ID_SYNTAX

ENTRY_PARTS = (
    "instruction",
    "constant",
    "schema",
    "state",
    "trigger",
    "process",
    "interface",
)

_ENTRY_PART = "|".join(
    ENTRY_PARTS
)
_ENTRY_BODY = (
    rf"(?:{_ENTRY_PART})\."
    rf"{SLUG_ID_SYNTAX.body}"
)
DOCUMENT_PATH_BODY = r"[A-Za-z0-9._/-]+\.oak\.md"
TARGET_PATH_PATTERN = (
    rf"^(?:{DOCUMENT_PATH_BODY}#)?"
    rf"{_ENTRY_BODY}$"
)
TARGET_PATH_EBNF = (
    "target_path = entry_path | "
    "relative_document_path, \"#\", entry_path ;"
)
ENTRY_PATH_EBNF = (
    "entry_path = entry_part, \".\", slug_id ;"
)
ENTRY_PART_EBNF = (
    "entry_part = "
    + " | ".join(
        f'"{part}"'
        for part in ENTRY_PARTS
    )
    + " ;"
)
RELATIVE_DOCUMENT_PATH_EBNF = (
    "relative_document_path = "
    "? one relative POSIX path of letters, digits, "
    '".", "_", "-", and "/" ending in .oak.md ? ;'
)

_ENTRY_RE = re.compile(
    rf"^(?P<part>{_ENTRY_PART})\."
    rf"(?P<id>{SLUG_ID_SYNTAX.body})$"
)


_DOCUMENT_RE = re.compile(r"[A-Za-z0-9._/-]+")


def _document_path(value: str) -> str:
    if (
        _DOCUMENT_RE.fullmatch(value) is None
        or "//" in value
        or value.startswith("/")
        or not value.endswith(".oak.md")
        or value.endswith(("/.", "/.."))
    ):
        raise PydanticCustomError(
            "invalid_document_path",
            (
                "document path must be one relative POSIX path of "
                'letters, digits, ".", "_", "-", and "/" '
                "ending in .oak.md"
            ),
        )

    return value


def _target_path(value: str) -> str:
    document, marker, entry = value.rpartition("#")

    if marker:
        _document_path(document)
    else:
        entry = value

    if _ENTRY_RE.fullmatch(entry) is None:
        raise PydanticCustomError(
            "invalid_document_path",
            "target path has an invalid part-qualified entry path",
        )

    return value


TargetPath = Annotated[
    str,
    StringConstraints(
        min_length=3,
        pattern=TARGET_PATH_PATTERN,
    ),
    AfterValidator(_target_path),
]


def split_target(
    value: str,
) -> tuple[str | None, str, str]:
    """Return document path, part, and id from one target path."""
    document, marker, entry = value.rpartition("#")
    local = entry if marker else value
    match = _ENTRY_RE.fullmatch(local)

    if match is None:
        raise ValueError(
            f"invalid target path {value}"
        )

    return (
        document if marker else None,
        match.group("part"),
        match.group("id"),
    )


def target_document(
    value: str,
) -> str | None:
    """Return the authored relative document path."""
    return split_target(value)[0]


def target_part(
    value: str,
) -> str:
    """Return the target part."""
    return split_target(value)[1]


def target_id(
    value: str,
) -> str:
    """Return the target entry id."""
    return split_target(value)[2]


def is_relative_target(
    value: str,
) -> bool:
    """Return whether the target names another document."""
    return target_document(value) is not None


def typed_target(
    value: str,
    expected: str,
) -> str:
    """Require one target part."""
    if target_part(value) != expected:
        raise PydanticCustomError(
            "wrong_reference_target_type",
            (
                "target {target} is not in "
                "the {expected} part"
            ),
            {
                "target": value,
                "expected": expected,
            },
        )

    return value


def local_target(
    value: str,
    expected: str,
) -> str:
    """Require one local target of one part."""
    typed_target(
        value,
        expected,
    )

    if not is_relative_target(value):
        return value

    code = (
        "external_state_reference"
        if expected == "state"
        else "external_interface_reference"
    )
    raise PydanticCustomError(
        code,
        "{expected} target must stay in the active document",
        {
            "expected": expected,
        },
    )
