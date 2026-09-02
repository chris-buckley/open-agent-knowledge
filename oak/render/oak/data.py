"""Schema, constant, and state text rendering."""

from __future__ import annotations

import csv
import io
import json

import yaml

from oak.node.parts.constants import Constant
from oak.node.parts.schemas.constraints import (
    AtLeast,
    AtMost,
    Constraint,
    Lines,
    ListOf,
    MaxChars,
    NonEmpty,
    OneOf,
    Regex,
    Type,
)
from oak.node.parts.schemas.model import Where
from oak.node.parts.state import State
from oak.surface.registry import surface_for
from oak.vocabulary.text.placeholder import token

WHERE_HEADING = "WHERE:"
WHERE_ENTRY_PREFIX = "- "
WHERE_DETAIL_SEPARATOR = "; "


def _scalar(
    value: str | int | float | bool,
) -> str:
    return (
        value
        if isinstance(value, str)
        else json.dumps(
            value,
            ensure_ascii=False,
        )
    )


def _bound(
    value: int | float | str,
) -> str:
    return (
        token(value)
        if isinstance(value, str)
        else _scalar(value)
    )


def _lines(
    constraint: Lines,
) -> str:
    if (
        constraint.min is not None
        and constraint.max is not None
    ):
        if constraint.min == constraint.max == 1:
            return "is one line"

        if constraint.min == constraint.max:
            return (
                f"has {constraint.min} lines"
            )

        return (
            f"has {constraint.min} to "
            f"{constraint.max} lines"
        )

    if constraint.max is not None:
        return (
            "has at most 1 line"
            if constraint.max == 1
            else (
                f"has at most "
                f"{constraint.max} lines"
            )
        )

    return (
        f"has at least "
        f"{constraint.min} lines"
    )


def constraint_text(
    constraint: Constraint,
) -> str:
    """Return the OAK text for one schema constraint."""
    surface_for(constraint)

    match constraint:
        case Type():
            return f"is {constraint.of}"

        case OneOf():
            return (
                "is one of "
                + ", ".join(
                    f"`{_scalar(value)}`"
                    for value in constraint.values
                )
            )

        case Regex():
            return (
                f"matches "
                f"`{constraint.pattern}`"
            )

        case NonEmpty():
            return "is non-empty"

        case MaxChars():
            return (
                f"is at most "
                f"{constraint.n} characters"
            )

        case Lines():
            return _lines(constraint)

        case ListOf():
            return (
                f"is a list of {constraint.item} "
                f"joined by `{constraint.separator}`"
            )

        case AtLeast():
            return (
                f"is at least "
                f"{_bound(constraint.value)}"
            )

        case AtMost():
            return (
                f"is at most "
                f"{_bound(constraint.value)}"
            )

    raise TypeError(
        "unsupported constraint "
        f"{type(constraint).__name__}"
    )


def where_line(
    where: Where,
) -> str:
    """Return one dense line for a schema placeholder."""
    surface_for(where)
    body = WHERE_DETAIL_SEPARATOR.join(
        constraint_text(item)
        for item in where.constraints
    )

    if where.examples:
        body += (
            " (e.g. "
            + ", ".join(
                f"`{_scalar(example)}`"
                for example in where.examples
            )
            + ")"
        )

    if where.description is not None:
        body += (
            WHERE_DETAIL_SEPARATOR
            + where.description
        )

    return (
        WHERE_ENTRY_PREFIX
        + token(where.placeholder)
        + " "
        + body
        + "."
    )


def value_text(
    value: object,
    *,
    indent: int | None = None,
) -> str:
    """Return canonical JSON text."""
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=indent,
    )


def _binding_head(
    entry: Constant | State,
) -> str:
    if entry.schema_id is None:
        return entry.id

    return (
        f"{entry.id} AS "
        f"{entry.schema_id}."
        f"{entry.placeholder}"
    )


def _block(
    head: str,
    form: str,
    body: str,
) -> str:
    if any(
        line == ">>"
        for line in body.splitlines()
    ):
        raise ValueError(
            f"constant {head} body "
            "contains the closing line >>"
        )

    separator = (
        ""
        if body.endswith("\n")
        else "\n"
    )
    return (
        f"{head}: {form}<<\n"
        f"{body}{separator}>>"
    )


def _csv_body(
    value: list[dict[str, object]],
) -> str:
    stream = io.StringIO(
        newline=""
    )
    writer = csv.DictWriter(
        stream,
        fieldnames=list(value[0]),
        lineterminator="\n",
    )
    writer.writeheader()

    for row in value:
        writer.writerow(
            {
                key: (
                    json.dumps(
                        cell,
                        ensure_ascii=False,
                    )
                    if not isinstance(
                        cell,
                        str,
                    )
                    else cell
                )
                for key, cell in row.items()
            }
        )

    return stream.getvalue().rstrip(
        "\n"
    )


def constant_text(
    constant: Constant,
) -> str:
    """Return one inline or block constant entry."""
    surface_for(constant)
    head = _binding_head(constant)

    if constant.form == "inline":
        return (
            f"{head}: "
            f"{value_text(constant.value)}"
        )

    if constant.form == "text":
        if not isinstance(
            constant.value,
            str,
        ):
            raise TypeError(
                "a text constant must contain text"
            )

        return _block(
            head,
            "TEXT",
            constant.value,
        )

    if constant.form == "json":
        return _block(
            head,
            "JSON",
            value_text(
                constant.value,
                indent=2,
            ),
        )

    if constant.form == "csv":
        if not isinstance(
            constant.value,
            list,
        ):
            raise TypeError(
                "a CSV constant must contain rows"
            )

        return _block(
            head,
            "CSV",
            _csv_body(constant.value),
        )

    if constant.form == "yaml":
        body = yaml.safe_dump(
            constant.value,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        ).rstrip("\n")
        return _block(
            head,
            "YAML",
            body,
        )

    raise TypeError(
        "unsupported constant form "
        f"{constant.form}"
    )


def named_value_line(
    entry: State,
) -> str:
    """Return one state value line."""
    surface_for(entry)
    return (
        f"{_binding_head(entry)}: "
        f"{value_text(entry.value)}"
    )


__all__ = [
    "WHERE_DETAIL_SEPARATOR",
    "WHERE_ENTRY_PREFIX",
    "WHERE_HEADING",
    "constant_text",
    "constraint_text",
    "named_value_line",
    "value_text",
    "where_line",
]
