"""Schema and Where models with local structural validation."""

from collections import Counter
from collections.abc import Iterable, Mapping
from typing import Literal, Self

from pydantic import ConfigDict, Field, ValidationError, model_validator

from oak.base import Entry, OakModel
from oak.node.parts.schemas.binding import (
    _error_message,
    bind_schema,
    bind_schema_value,
)
from oak.node.parts.schemas.constraints import (
    _BOUND_CONSTRAINTS,
    _validation_order,
    Constraint,
    Example,
    NonEmptyText,
    Type,
)
from oak.rules.validation import rule_error
from oak.vocabulary import NonBlankLine, Placeholder
from oak.vocabulary.text.placeholder import placeholders_in


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
        description="Values that satisfy every locally resolvable constraint.",
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
            and isinstance(
                constraint.value,
                str,
            )
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
                    if isinstance(
                        constraint,
                        Type,
                    ):
                        constraint.check_example(
                            example
                        )
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
        bind_schema(
            self,
            values,
        )

    def bind_value(
        self,
        placeholder: str,
        value: object,
    ) -> None:
        """Validate one value against one schema placeholder."""
        bind_schema_value(
            self,
            placeholder,
            value,
        )


__all__ = [
    "Schema",
    "Where",
    "where",
]
