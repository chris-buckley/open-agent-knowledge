"""Top-level OAK source normalization and document parsing."""

from __future__ import annotations

from collections.abc import Callable

from pydantic import ValidationError

from oak.node import Node
from oak.node.structure import PART_ORDER
from oak.parse.data import (
    parse_constants,
    parse_instructions,
    parse_state,
)
from oak.parse.errors import (
    OakParseError,
    ParseError,
    ParseFailure,
)
from oak.parse.grouping import (
    GroupingName,
    infer_grouping,
    split_parts,
)
from oak.parse.interfaces import parse_interfaces
from oak.parse.processes import parse_processes
from oak.parse.schemas import parse_schemas
from oak.parse.triggers import parse_triggers


def source_text(source: str | bytes) -> str:
    """Decode UTF-8 and normalize line endings to LF."""
    if isinstance(source, bytes):
        try:
            source = source.decode("utf-8")
        except UnicodeDecodeError as error:
            raise OakParseError(
                (
                    ParseFailure(
                        "invalid_utf8",
                        "$",
                        None,
                        str(error),
                    ),
                )
            ) from None

    return source.replace(
        "\r\n",
        "\n",
    ).replace(
        "\r",
        "\n",
    )


def validation_failures(
    error: ValidationError,
) -> list[ParseFailure]:
    """Translate Pydantic details into stable parse failures."""
    result = []

    for detail in error.errors(
        include_url=False,
        include_context=False,
        include_input=False,
    ):
        path = ".".join(
            str(part)
            for part in detail["loc"]
        ) or "$"
        result.append(
            ParseFailure(
                str(detail["type"]),
                path,
                None,
                detail["msg"],
            )
        )

    return result


def parse(
    source: str | bytes,
    *,
    grouping: GroupingName | None = None,
) -> Node:
    """Parse one OAK document and run every standalone model check."""
    text = source_text(source)

    if not text:
        return Node()

    failures: list[ParseFailure] = []

    try:
        grouping = (
            grouping
            or infer_grouping(text)
        )
        parts = split_parts(
            text,
            grouping,
        )

    except ParseError as error:
        raise OakParseError(
            (error.failure,)
        ) from None

    part_parsers: dict[
        str,
        Callable[
            [list[str], int],
            object,
        ],
    ] = {
        "instructions": parse_instructions,
        "constants": parse_constants,
        "schemas": lambda body, start: parse_schemas(
            body,
            start,
            grouping,
        ),
        "state": parse_state,
        "triggers": parse_triggers,
        "processes": lambda body, start: parse_processes(
            body,
            start,
            grouping,
        ),
        "interfaces": lambda body, start: parse_interfaces(
            body,
            start,
            grouping,
        ),
    }

    data: dict[str, object] = {}

    for part in PART_ORDER:
        if part not in parts:
            continue

        body, start = parts[part]

        try:
            data[part] = part_parsers[part](
                body,
                start,
            )
        except ParseError as error:
            failures.append(
                error.failure
            )
        except ValidationError as error:
            failures.extend(
                validation_failures(error)
            )

    if failures:
        raise OakParseError(failures)

    try:
        return Node.model_validate(data)
    except ValidationError as error:
        raise OakParseError(
            validation_failures(error)
        ) from None


def parse_oak(
    source: str | bytes,
    *,
    grouping: GroupingName | None = None,
) -> Node:
    """Parse one OAK document."""
    return parse(
        source,
        grouping=grouping,
    )


__all__ = [
    "parse",
    "parse_oak",
]
