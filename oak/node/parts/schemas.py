"""The schemas part: one template and one Where per placeholder."""

import json
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Annotated, Literal, Self

from pydantic import (
    ConfigDict,
    Field,
    FiniteFloat,
    PositiveInt,
    StringConstraints,
    ValidationError,
    model_validator,
)

from oak.base import DiscriminatedModel, Entry, OakModel
from oak.rules import rule_error
from oak.vocabulary import (
    DATATYPE_ADAPTERS,
    Datatype,
    NonBlankLine,
    Placeholder,
    RegexPattern,
)
from oak.vocabulary.text.placeholder import placeholders_in
from oak.vocabulary.text.regex_pattern import rust_regex_adapter

NonEmptyText = Annotated[str, StringConstraints(min_length=1)]
Scalar = str | int | FiniteFloat | bool
Example = NonBlankLine | int | FiniteFloat | bool
Bound = int | FiniteFloat | Placeholder

_JSON_STRING_DATATYPES = frozenset(
    {"string", "datetime", "uri", "path"}
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
            _validate_text(self.of, value)
        else:
            self.check(value, {})


class OneOf(ConstraintModel):
    """The bound value is one of the listed values."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "kind": "one_of",
                    "values": ["draft", "final"],
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
        examples=[["draft", "final"]],
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
        rust_regex_adapter(self.pattern).validate_python(value)


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
            not isinstance(value, (str, list))
            or len(value) == 0
        ):
            raise ValueError(f"{value!r} is empty")


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
        if not isinstance(value, str) or len(value) > self.n:
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
        if self.min is None and self.max is None:
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
        if not isinstance(value, str):
            raise ValueError(f"{value!r} is not text")

        count = len(value.splitlines())
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
        if not isinstance(value, str):
            raise ValueError(f"{value!r} is not text")

        for item in value.split(self.separator):
            _validate_text(self.item, item)


def _bound(
    value: object,
    values: Mapping[str, object],
) -> int | float:
    resolved = (
        values.get(value)
        if isinstance(value, str)
        else value
    )

    if isinstance(value, str) and value not in values:
        raise ValueError(f"{value} has no bound value")

    if (
        isinstance(resolved, bool)
        or not isinstance(resolved, (int, float))
    ):
        raise ValueError(f"{value!r} is not a number")

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
        examples=[1, "LINE_FROM"],
    )

    def check(
        self,
        value: object,
        values: Mapping[str, object],
    ) -> None:
        if _bound(value, values) < _bound(self.value, values):
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
        examples=[160, "LINE_TO"],
    )

    def check(
        self,
        value: object,
        values: Mapping[str, object],
    ) -> None:
        if _bound(value, values) > _bound(self.value, values):
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

_BOUND_CONSTRAINTS = (AtLeast, AtMost)


def _validation_order(
    constraints: Iterable[Constraint],
) -> list[Constraint]:
    constraints = list(constraints)
    return [
        item
        for item in constraints
        if isinstance(item, Type)
    ] + [
        item
        for item in constraints
        if not isinstance(item, Type)
    ]


class Where(OakModel):
    """One placeholder, its constraints, examples, and description."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "placeholder": "OUTLINE_TITLE",
                    "constraints": [
                        {
                            "kind": "type",
                            "of": "string",
                        }
                    ],
                    "description": "title for the outline",
                }
            ]
        }
    )

    placeholder: Placeholder = Field(
        description="The bare placeholder name.",
        examples=["OUTLINE_TITLE"],
    )
    constraints: list[Constraint] = Field(
        min_length=1,
        description="The constraints every bound value must satisfy.",
        examples=[
            [
                {
                    "kind": "type",
                    "of": "string",
                }
            ],
            [
                {
                    "kind": "regex",
                    "pattern": "^[0-9]+$",
                }
            ],
        ],
    )
    examples: list[Example] = Field(
        default_factory=list,
        description=(
            "Values that satisfy every locally resolvable constraint."
        ),
        examples=[["1.1", "1.2"]],
    )
    description: NonBlankLine | None = Field(
        default=None,
        description="What the placeholder holds, in one line.",
        examples=["title for the outline"],
    )

    @property
    def references(self) -> set[str]:
        """Return every placeholder referenced by a bound constraint."""
        return {
            constraint.value
            for constraint in self.constraints
            if isinstance(
                constraint,
                _BOUND_CONSTRAINTS,
            )
            and isinstance(constraint.value, str)
        }

    @model_validator(mode="after")
    def valid_examples(self) -> Self:
        if self.examples and self.references:
            raise rule_error(
                "unresolved_where_example",
                (
                    "examples cannot resolve placeholder-valued "
                    "bounds: {placeholders}"
                ),
                {
                    "placeholders": ", ".join(
                        sorted(self.references)
                    )
                },
            )

        for index, example in enumerate(self.examples):
            for constraint in _validation_order(
                self.constraints
            ):
                try:
                    if isinstance(constraint, Type):
                        constraint.check_example(example)
                    else:
                        constraint.check(
                            example,
                            {
                                self.placeholder: example,
                            },
                        )
                except (
                    ValueError,
                    ValidationError,
                ) as error:
                    raise rule_error(
                        "invalid_where_example",
                        (
                            "example {index} for {placeholder} "
                            "fails {kind}: {reason}"
                        ),
                        {
                            "index": index,
                            "placeholder": self.placeholder,
                            "kind": constraint.kind,
                            "reason": _error_message(error),
                        },
                    ) from None

        return self


def where(
    placeholder: Placeholder,
    *constraints: Constraint,
    examples: Iterable[Example] = (),
    description: NonBlankLine | None = None,
) -> Where:
    """Author one Where without repeated field names."""
    return Where(
        placeholder=placeholder,
        constraints=list(constraints),
        examples=list(examples),
        description=description,
    )


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
    if isinstance(error, ValidationError):
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
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError):
        return BindingFailure(
            "invalid_json_value",
            placeholder,
            f"{value!r} is not one JSON value",
        )
    return None


class Schema(Entry):
    """One reusable information shape with one Where per placeholder."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "part": "schemas",
                    "id": "outline",
                    "name": "Hierarchical Outline",
                    "purpose": "Generate a numbered outline.",
                    "template": "## <OUTLINE_TITLE>\n",
                    "where": [
                        {
                            "placeholder": "OUTLINE_TITLE",
                            "constraints": [
                                {
                                    "kind": "type",
                                    "of": "string",
                                }
                            ],
                        }
                    ],
                }
            ]
        }
    )

    part: Literal["schemas"] = Field(
        default="schemas",
        description="The entry part discriminator.",
        examples=["schemas"],
    )
    name: NonBlankLine | None = Field(
        default=None,
        description="The display name.",
        examples=["Hierarchical Outline"],
    )
    purpose: NonBlankLine | None = Field(
        default=None,
        description="What the information shape is for.",
        examples=[
            "Generate a semantic multilevel numbered outline."
        ],
    )
    template: NonEmptyText = Field(
        description=(
            "The literal shape with variable parts written "
            "as <PLACEHOLDER>."
        ),
        examples=[
            "## <OUTLINE_TITLE>\n\n"
            "<STATEMENT>\n"
            "…\n"
        ],
    )
    where: list[Where] = Field(
        default_factory=list,
        description=(
            "One Where per distinct template placeholder, "
            "in authored order."
        ),
        examples=[
            [
                {
                    "placeholder": "OUTLINE_TITLE",
                    "constraints": [
                        {
                            "kind": "type",
                            "of": "string",
                        }
                    ],
                }
            ]
        ],
    )

    @property
    def placeholders(self) -> set[str]:
        """Return every distinct placeholder delimited in the template."""
        return placeholders_in(self.template)

    @model_validator(mode="after")
    def links(self) -> Self:
        names = [
            item.placeholder
            for item in self.where
        ]
        duplicates = sorted(
            name
            for name, count in Counter(names).items()
            if count > 1
        )

        if duplicates:
            raise rule_error(
                "duplicate_where_placeholder",
                "where repeats {placeholders}",
                {
                    "placeholders": ", ".join(
                        duplicates
                    )
                },
            )

        in_template = self.placeholders
        in_where = set(names)
        missing = sorted(
            in_template - in_where
        )
        unknown = sorted(
            in_where - in_template
        )

        if missing or unknown:
            raise rule_error(
                "placeholder_where_mismatch",
                (
                    "template and where placeholders differ; "
                    "missing: {missing}; unused: {unused}"
                ),
                {
                    "missing": (
                        ", ".join(missing)
                        or "none"
                    ),
                    "unused": (
                        ", ".join(unknown)
                        or "none"
                    ),
                },
            )

        references = (
            set().union(
                *(
                    item.references
                    for item in self.where
                )
            )
            if self.where
            else set()
        )
        dangling = sorted(
            references - in_template
        )

        if dangling:
            raise rule_error(
                "unknown_constraint_placeholder",
                "constraints reference {placeholders}",
                {
                    "placeholders": ", ".join(
                        dangling
                    )
                },
            )

        return self

    def bind(
        self,
        values: Mapping[str, object],
    ) -> None:
        """Validate one complete placeholder binding."""
        failures: list[BindingFailure] = []
        expected = self.placeholders
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

        for item in self.where:
            if item.placeholder not in values:
                continue

            failure = _json_failure(
                item.placeholder,
                values[item.placeholder],
            )
            if failure is not None:
                failures.append(failure)
                continue

            for constraint in _validation_order(
                item.constraints
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
                        values[item.placeholder],
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
                            item.placeholder,
                            _error_message(error),
                        )
                    )

        if failures:
            raise SchemaBindingError(failures)

    def bind_value(
        self,
        placeholder: str,
        value: object,
    ) -> None:
        """Validate one value against one schema placeholder."""
        entry = next(
            (
                item
                for item in self.where
                if item.placeholder == placeholder
            ),
            None,
        )
        if entry is None:
            raise SchemaBindingError(
                [
                    BindingFailure(
                        "unknown_binding",
                        placeholder,
                        "not a placeholder of this schema",
                    )
                ]
            )

        if entry.references:
            raise SchemaBindingError(
                [
                    BindingFailure(
                        "unresolved_binding",
                        placeholder,
                        "constraints reference "
                        + ", ".join(
                            sorted(entry.references)
                        ),
                    )
                ]
            )

        failure = _json_failure(placeholder, value)
        if failure is not None:
            raise SchemaBindingError([failure])

        failures: list[BindingFailure] = []
        values = {placeholder: value}
        for constraint in _validation_order(
            entry.constraints
        ):
            try:
                constraint.check(value, values)
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
