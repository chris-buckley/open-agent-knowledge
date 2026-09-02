"""Schema binding diagnostics and datatype-first binding evaluation."""

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import ValidationError

from oak.node.parts.schemas.constraints import (
    _BOUND_CONSTRAINTS,
    _validation_order,
)

if TYPE_CHECKING:
    from oak.node.parts.schemas.model import Schema


@dataclass(frozen=True, slots=True)
class BindingFailure:
    """One stable schema binding failure."""

    code: str
    placeholder: str
    message: str

    def __str__(self) -> str:
        return (
            f"[{self.code}] "
            f"{self.placeholder}: "
            f"{self.message}"
        )


class SchemaBindingError(ValueError):
    """Every failure from one complete schema binding."""

    code = "schema_binding_invalid"

    def __init__(
        self,
        failures: Iterable[BindingFailure],
    ) -> None:
        self.failures = tuple(failures)
        super().__init__(
            "\n".join(
                str(failure)
                for failure in self.failures
            )
        )


def _error_message(
    error: ValueError | ValidationError,
) -> str:
    if isinstance(
        error,
        ValidationError,
    ):
        messages = []

        for detail in error.errors(
            include_url=False,
            include_context=False,
            include_input=False,
        ):
            location = ".".join(
                str(part)
                for part in detail["loc"]
            )
            messages.append(
                (
                    f"{location}: {detail['msg']}"
                    if location
                    else detail["msg"]
                )
            )

        return "; ".join(messages)

    return str(error)


def _json_failure(
    placeholder: str,
    value: object,
) -> BindingFailure | None:
    try:
        json.dumps(
            value,
            allow_nan=False,
        )
    except (
        TypeError,
        ValueError,
    ):
        return BindingFailure(
            "invalid_json_value",
            placeholder,
            f"{value!r} is not one JSON value",
        )
    return None


def bind_schema(
    schema: "Schema",
    values: Mapping[str, object],
) -> None:
    """Validate one complete placeholder binding."""
    failures: list[BindingFailure] = []
    expected = schema.placeholders
    supplied = set(values)

    failures.extend(
        BindingFailure(
            "missing_binding",
            name,
            "no value bound",
        )
        for name in sorted(
            expected - supplied
        )
    )
    failures.extend(
        BindingFailure(
            "unknown_binding",
            name,
            "not a placeholder of this schema",
        )
        for name in sorted(
            supplied - expected
        )
    )

    for clause in schema.where:
        if clause.placeholder not in values:
            continue

        failure = _json_failure(
            clause.placeholder,
            values[clause.placeholder],
        )
        if failure is not None:
            failures.append(failure)
            continue

        for constraint in _validation_order(
            clause.constraints
        ):
            if (
                isinstance(
                    constraint,
                    _BOUND_CONSTRAINTS,
                )
                and isinstance(
                    constraint.value,
                    str,
                )
                and constraint.value not in values
            ):
                continue

            try:
                constraint.check(
                    values[clause.placeholder],
                    values,
                )
            except (
                ValueError,
                ValidationError,
            ) as error:
                failures.append(
                    BindingFailure(
                        (
                            "constraint_"
                            f"{constraint.kind}"
                        ),
                        clause.placeholder,
                        _error_message(error),
                    )
                )

    if failures:
        raise SchemaBindingError(failures)


def bind_schema_value(
    schema: "Schema",
    placeholder: str,
    value: object,
) -> None:
    """Validate one value against one schema placeholder."""
    clause = next(
        (
            clause
            for clause in schema.where
            if clause.placeholder == placeholder
        ),
        None,
    )
    if clause is None:
        raise SchemaBindingError(
            [
                BindingFailure(
                    "unknown_binding",
                    placeholder,
                    "not a placeholder of this schema",
                )
            ]
        )

    if clause.references:
        raise SchemaBindingError(
            [
                BindingFailure(
                    "unresolved_binding",
                    placeholder,
                    "constraints reference "
                    + ", ".join(
                        sorted(clause.references)
                    ),
                )
            ]
        )

    failure = _json_failure(
        placeholder,
        value,
    )
    if failure is not None:
        raise SchemaBindingError(
            [failure]
        )

    failures: list[BindingFailure] = []
    values = {
        placeholder: value,
    }
    for constraint in _validation_order(
        clause.constraints
    ):
        try:
            constraint.check(
                value,
                values,
            )
        except (
            ValueError,
            ValidationError,
        ) as error:
            failures.append(
                BindingFailure(
                    (
                        "constraint_"
                        f"{constraint.kind}"
                    ),
                    placeholder,
                    _error_message(error),
                )
            )

    if failures:
        raise SchemaBindingError(failures)


__all__ = [
    "BindingFailure",
    "SchemaBindingError",
]
