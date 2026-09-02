"""Schema constraint models and datatype-first validation order."""

import json
from collections.abc import Iterable, Mapping
from typing import Annotated, Literal, Self

from pydantic import (
    ConfigDict,
    Field,
    FiniteFloat,
    PositiveInt,
    StringConstraints,
    model_validator,
)

from oak.base import DiscriminatedModel
from oak.rules import rule_error
from oak.vocabulary import (
    DATATYPE_ADAPTERS,
    Datatype,
    NonBlankLine,
    Placeholder,
    RegexPattern,
)
from oak.vocabulary.text.regex_pattern import rust_regex_adapter

NonEmptyText = Annotated[
    str,
    StringConstraints(min_length=1),
]
Scalar = str | int | FiniteFloat | bool
Example = NonBlankLine | int | FiniteFloat | bool
Bound = int | FiniteFloat | Placeholder

_JSON_STRING_DATATYPES = frozenset(
    {
        "string",
        "datetime",
        "uri",
        "path",
    }
)


def _validate_text(
    datatype: Datatype,
    value: str,
) -> object:
    source = (
        json.dumps(value)
        if datatype in _JSON_STRING_DATATYPES
        else value
    )
    return DATATYPE_ADAPTERS[datatype].validate_json(source)


class ConstraintModel(DiscriminatedModel):
    """One tagged schema constraint."""

    discriminator_field = "kind"


class Type(ConstraintModel):
    """The bound value has one datatype from the vocabulary catalog."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "type",
                    "of": "string",
                }
            ]
        }
    )

    kind: Literal["type"] = Field(
        default="type",
        description="The constraint discriminator.",
        examples=["type"],
    )
    of: Datatype = Field(
        description="The datatype name.",
        examples=["string", "integer", "uri"],
    )

    def check(
        self,
        value: object,
        values: Mapping[str, object],
    ) -> None:
        DATATYPE_ADAPTERS[self.of].validate_python(value)

    def check_example(self, value: Example) -> None:
        if isinstance(value, str):
            _validate_text(
                self.of,
                value,
            )
        else:
            self.check(
                value,
                {},
            )


class OneOf(ConstraintModel):
    """The bound value is one of the listed values."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "one_of",
                    "values": [
                        "draft",
                        "final",
                    ],
                }
            ]
        }
    )

    kind: Literal["one_of"] = Field(
        default="one_of",
        description="The constraint discriminator.",
        examples=["one_of"],
    )
    values: list[Scalar] = Field(
        min_length=1,
        description="The allowed values.",
        examples=[
            [
                "draft",
                "final",
            ]
        ],
    )

    def check(
        self,
        value: object,
        values: Mapping[str, object],
    ) -> None:
        if value not in self.values:
            raise ValueError(
                f"{value!r} is not one of {self.values!r}"
            )


class Regex(ConstraintModel):
    """The bound value matches one anchored portable rust-regex pattern."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "regex",
                    "pattern": "^[0-9]+$",
                }
            ]
        }
    )

    kind: Literal["regex"] = Field(
        default="regex",
        description="The constraint discriminator.",
        examples=["regex"],
    )
    pattern: RegexPattern = Field(
        description="The whole-value portable pattern.",
        examples=["^[0-9]+$"],
    )

    def check(
        self,
        value: object,
        values: Mapping[str, object],
    ) -> None:
        rust_regex_adapter(
            self.pattern
        ).validate_python(value)


class NonEmpty(ConstraintModel):
    """The bound value has at least one character or item."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "non_empty",
                }
            ]
        }
    )

    kind: Literal["non_empty"] = Field(
        default="non_empty",
        description="The constraint discriminator.",
        examples=["non_empty"],
    )

    def check(
        self,
        value: object,
        values: Mapping[str, object],
    ) -> None:
        if (
            not isinstance(
                value,
                (
                    str,
                    list,
                ),
            )
            or len(value) == 0
        ):
            raise ValueError(
                f"{value!r} is empty"
            )


class MaxChars(ConstraintModel):
    """The bound value has at most n characters."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "max_chars",
                    "n": 160,
                }
            ]
        }
    )

    kind: Literal["max_chars"] = Field(
        default="max_chars",
        description="The constraint discriminator.",
        examples=["max_chars"],
    )
    n: PositiveInt = Field(
        description="The character limit.",
        examples=[160],
    )

    def check(
        self,
        value: object,
        values: Mapping[str, object],
    ) -> None:
        if (
            not isinstance(
                value,
                str,
            )
            or len(value) > self.n
        ):
            raise ValueError(
                f"{value!r} exceeds {self.n} characters"
            )


class Lines(ConstraintModel):
    """The bound value has one positive line-count bound."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "lines",
                    "max": 1,
                }
            ]
        }
    )

    kind: Literal["lines"] = Field(
        default="lines",
        description="The constraint discriminator.",
        examples=["lines"],
    )
    min: PositiveInt | None = Field(
        default=None,
        description="The fewest lines.",
        examples=[1],
    )
    max: PositiveInt | None = Field(
        default=None,
        description="The most lines.",
        examples=[1],
    )

    @model_validator(mode="after")
    def bounds(self) -> Self:
        if (
            self.min is None
            and self.max is None
        ):
            raise rule_error(
                "missing_line_bound",
                "lines needs min, max, or both",
            )

        if (
            self.min is not None
            and self.max is not None
            and self.min > self.max
        ):
            raise rule_error(
                "invalid_line_bounds",
                "lines min exceeds max",
            )

        return self

    def check(
        self,
        value: object,
        values: Mapping[str, object],
    ) -> None:
        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                f"{value!r} is not text"
            )

        count = len(
            value.splitlines()
        )
        if (
            self.min is not None
            and count < self.min
        ) or (
            self.max is not None
            and count > self.max
        ):
            raise ValueError(
                f"{count} lines is outside "
                f"{self.min} to {self.max}"
            )


class ListOf(ConstraintModel):
    """The bound value is items of one datatype joined by one separator."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "list_of",
                    "item": "integer",
                    "separator": ", ",
                }
            ]
        }
    )

    kind: Literal["list_of"] = Field(
        default="list_of",
        description="The constraint discriminator.",
        examples=["list_of"],
    )
    item: Datatype = Field(
        description="The datatype of every item.",
        examples=["integer"],
    )
    separator: NonEmptyText = Field(
        description="The text between items.",
        examples=[", "],
    )

    def check(
        self,
        value: object,
        values: Mapping[str, object],
    ) -> None:
        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                f"{value!r} is not text"
            )

        for item in value.split(
            self.separator
        ):
            _validate_text(
                self.item,
                item,
            )


def _bound(
    value: object,
    values: Mapping[str, object],
) -> int | float:
    resolved = (
        values.get(value)
        if isinstance(
            value,
            str,
        )
        else value
    )

    if (
        isinstance(
            value,
            str,
        )
        and value not in values
    ):
        raise ValueError(
            f"{value} has no bound value"
        )

    if (
        isinstance(
            resolved,
            bool,
        )
        or not isinstance(
            resolved,
            (
                int,
                float,
            ),
        )
    ):
        raise ValueError(
            f"{value!r} is not a number"
        )

    return resolved


class AtLeast(ConstraintModel):
    """The bound value is at least a number or another placeholder value."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "at_least",
                    "value": 1,
                }
            ]
        }
    )

    kind: Literal["at_least"] = Field(
        default="at_least",
        description="The constraint discriminator.",
        examples=["at_least"],
    )
    value: Bound = Field(
        description="A number or a placeholder of the same schema.",
        examples=[
            1,
            "LINE_FROM",
        ],
    )

    def check(
        self,
        value: object,
        values: Mapping[str, object],
    ) -> None:
        if _bound(
            value,
            values,
        ) < _bound(
            self.value,
            values,
        ):
            raise ValueError(
                f"{value!r} is below {self.value!r}"
            )


class AtMost(ConstraintModel):
    """The bound value is at most a number or another placeholder value."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "at_most",
                    "value": 160,
                }
            ]
        }
    )

    kind: Literal["at_most"] = Field(
        default="at_most",
        description="The constraint discriminator.",
        examples=["at_most"],
    )
    value: Bound = Field(
        description="A number or a placeholder of the same schema.",
        examples=[
            160,
            "LINE_TO",
        ],
    )

    def check(
        self,
        value: object,
        values: Mapping[str, object],
    ) -> None:
        if _bound(
            value,
            values,
        ) > _bound(
            self.value,
            values,
        ):
            raise ValueError(
                f"{value!r} is above {self.value!r}"
            )


Constraint = Annotated[
    Type
    | OneOf
    | Regex
    | NonEmpty
    | MaxChars
    | Lines
    | ListOf
    | AtLeast
    | AtMost,
    Field(discriminator="kind"),
]

_BOUND_CONSTRAINTS = (
    AtLeast,
    AtMost,
)


def _validation_order(
    constraints: Iterable[Constraint],
) -> list[Constraint]:
    constraints = list(constraints)
    return [
        item
        for item in constraints
        if isinstance(
            item,
            Type,
        )
    ] + [
        item
        for item in constraints
        if not isinstance(
            item,
            Type,
        )
    ]


__all__ = [
    "AtLeast",
    "AtMost",
    "Bound",
    "Constraint",
    "ConstraintModel",
    "Example",
    "Lines",
    "ListOf",
    "MaxChars",
    "NonEmpty",
    "NonEmptyText",
    "OneOf",
    "Regex",
    "Scalar",
    "Type",
]
