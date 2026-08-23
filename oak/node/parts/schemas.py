"""The schemas part: one schema is a verbatim template plus one Where per placeholder."""

from collections import Counter
from collections.abc import Mapping
from functools import lru_cache
from typing import Annotated, Literal, Self

from pydantic import (
    AfterValidator,
    ConfigDict,
    Field,
    FiniteFloat,
    PositiveInt,
    StringConstraints,
    TypeAdapter,
    ValidationError,
    model_validator,
)
from pydantic_core import PydanticCustomError, SchemaError

from oak.base import OakModel
from oak.vocabulary import DATATYPE_ADAPTERS, Datatype, IriId, NonBlankLine, Placeholder
from oak.vocabulary.text.placeholder import placeholders_in

NonEmptyText = Annotated[str, StringConstraints(min_length=1)]
Scalar = str | int | FiniteFloat | bool
Bound = int | FiniteFloat | Placeholder


@lru_cache(maxsize=512)
def rust_regex_adapter(pattern: str) -> TypeAdapter[str]:
    """One compiled rust-regex validator per authored pattern; building it compiles the pattern."""
    return TypeAdapter(
        Annotated[str, StringConstraints(pattern=pattern)],
        config=ConfigDict(strict=True, regex_engine="rust-regex"),
    )


def _compiles(pattern: str) -> str:
    try:
        rust_regex_adapter(pattern)
    except SchemaError as error:
        raise PydanticCustomError("invalid_rust_regex", "rust-regex cannot compile the pattern: {reason}", {"reason": str(error)}) from None
    return pattern


RegexPattern = Annotated[str, StringConstraints(min_length=1), AfterValidator(_compiles)]


class Type(OakModel):
    """The bound value has one datatype from the vocabulary catalog."""

    kind: Literal["type"]
    of: Datatype = Field(description="The datatype name.", examples=["string", "integer", "uri"])

    def check(self, value: object, values: Mapping[str, object]) -> None:
        DATATYPE_ADAPTERS[self.of].validate_python(value)


class OneOf(OakModel):
    """The bound value is one of the listed values."""

    kind: Literal["one_of"]
    values: list[Scalar] = Field(min_length=1, description="The allowed values.", examples=[["draft", "final"]])

    def check(self, value: object, values: Mapping[str, object]) -> None:
        if value not in self.values:
            raise ValueError(f"{value!r} is not one of {self.values!r}")


class Regex(OakModel):
    """The bound value matches one anchored rust-regex pattern."""

    kind: Literal["regex"]
    pattern: RegexPattern = Field(description="The pattern, anchored to the whole string.", examples=["^[0-9]+$"])

    def check(self, value: object, values: Mapping[str, object]) -> None:
        rust_regex_adapter(self.pattern).validate_python(value)


class NonEmpty(OakModel):
    """The bound value has at least one character or item."""

    kind: Literal["non_empty"]

    def check(self, value: object, values: Mapping[str, object]) -> None:
        if not isinstance(value, (str, list)) or len(value) == 0:
            raise ValueError(f"{value!r} is empty")


class MaxChars(OakModel):
    """The bound value has at most n characters."""

    kind: Literal["max_chars"]
    n: PositiveInt = Field(description="The character limit.", examples=[160])

    def check(self, value: object, values: Mapping[str, object]) -> None:
        if not isinstance(value, str) or len(value) > self.n:
            raise ValueError(f"{value!r} exceeds {self.n} characters")


class Lines(OakModel):
    """The bound value has a line count inside the bounds; at least one bound is set."""

    kind: Literal["lines"]
    min: PositiveInt | None = Field(default=None, description="The fewest lines.", examples=[1])
    max: PositiveInt | None = Field(default=None, description="The most lines.", examples=[1])

    @model_validator(mode="after")
    def bounds(self) -> Self:
        if self.min is None and self.max is None:
            raise PydanticCustomError("missing_line_bound", "lines needs min, max, or both")
        if self.min is not None and self.max is not None and self.min > self.max:
            raise PydanticCustomError("invalid_line_bounds", "lines min exceeds max")
        return self

    def check(self, value: object, values: Mapping[str, object]) -> None:
        if not isinstance(value, str):
            raise ValueError(f"{value!r} is not text")
        count = len(value.splitlines())
        if (self.min is not None and count < self.min) or (self.max is not None and count > self.max):
            raise ValueError(f"{count} lines is outside {self.min} to {self.max}")


class ListOf(OakModel):
    """The bound value is items of one datatype joined by one separator."""

    kind: Literal["list_of"]
    item: Datatype = Field(description="The datatype of every item.", examples=["integer"])
    separator: NonEmptyText = Field(description="The text between items.", examples=[", "])

    def check(self, value: object, values: Mapping[str, object]) -> None:
        if not isinstance(value, str):
            raise ValueError(f"{value!r} is not text")
        adapter = DATATYPE_ADAPTERS[self.item]
        for item in value.split(self.separator):
            adapter.validate_json(item) if self.item in ("integer", "number", "boolean") else adapter.validate_python(item)


def _bound(value: Bound, values: Mapping[str, object]) -> int | float:
    resolved = values[value] if isinstance(value, str) else value
    if isinstance(resolved, bool) or not isinstance(resolved, (int, float)):
        raise ValueError(f"{value!r} is not a number")
    return resolved


class AtLeast(OakModel):
    """The bound value is at least a number or the value bound to another placeholder of the same schema."""

    kind: Literal["at_least"]
    value: Bound = Field(description="A number or a placeholder of the same schema.", examples=[1, "LINE_FROM"])

    def check(self, value: object, values: Mapping[str, object]) -> None:
        if _bound(value, values) < _bound(self.value, values):  # type: ignore[arg-type]
            raise ValueError(f"{value!r} is below {self.value!r}")


class AtMost(OakModel):
    """The bound value is at most a number or the value bound to another placeholder of the same schema."""

    kind: Literal["at_most"]
    value: Bound = Field(description="A number or a placeholder of the same schema.", examples=[160, "LINE_TO"])

    def check(self, value: object, values: Mapping[str, object]) -> None:
        if _bound(value, values) > _bound(self.value, values):  # type: ignore[arg-type]
            raise ValueError(f"{value!r} is above {self.value!r}")


Constraint = Annotated[
    Type | OneOf | Regex | NonEmpty | MaxChars | Lines | ListOf | AtLeast | AtMost,
    Field(discriminator="kind"),
]


class Where(OakModel):
    """One placeholder of the template, its constraints in authored order, and an optional description."""

    placeholder: Placeholder = Field(description="The bare placeholder name.", examples=["OUTLINE_TITLE"])
    constraints: list[Constraint] = Field(
        min_length=1,
        description="The constraints every bound value must satisfy.",
        examples=[[{"kind": "type", "of": "string"}], [{"kind": "regex", "pattern": "^[0-9]+$"}]],
    )
    examples: list[NonBlankLine] = Field(
        default_factory=list,
        description="Values that satisfy the constraints.",
        examples=[["1.1", "1.2"]],
    )
    description: NonBlankLine | None = Field(
        default=None,
        description="What the placeholder holds, in one line.",
        examples=["title for the outline"],
    )

    @property
    def references(self) -> set[str]:
        """Every placeholder a constraint of this Where refers to."""
        return {c.value for c in self.constraints if isinstance(c, (AtLeast, AtMost)) and isinstance(c.value, str)}


class Schema(OakModel):
    """One output contract: the literal output as a template and one Where per placeholder."""

    id: IriId = Field(description="The entry id, unique across the tree.", examples=["oak:schema/outline"])
    name: NonBlankLine | None = Field(default=None, description="The display name.", examples=["Hierarchical Outline"])
    purpose: NonBlankLine | None = Field(
        default=None,
        description="What the output is for.",
        examples=["Generate a semantic multilevel numbered outline."],
    )
    template: NonEmptyText = Field(
        description="The literal output, each variable part written as <PLACEHOLDER>; other < is literal.",
        examples=["## <OUTLINE_TITLE>\n\n<LEVEL_1_NUMBER> <STATEMENT>\n...\n"],
    )
    where: list[Where] = Field(
        default_factory=list,
        description="One Where per distinct template placeholder, in authored order.",
        examples=[[{"placeholder": "OUTLINE_TITLE", "constraints": [{"kind": "type", "of": "string"}]}]],
    )

    @property
    def placeholders(self) -> set[str]:
        """Every distinct placeholder the template delimits."""
        return placeholders_in(self.template)

    @model_validator(mode="after")
    def links(self) -> Self:
        names = [w.placeholder for w in self.where]
        duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
        if duplicates:
            raise PydanticCustomError("duplicate_where_placeholder", "where repeats {placeholders}", {"placeholders": ", ".join(duplicates)})
        in_template = self.placeholders
        missing = sorted(in_template - set(names))
        unknown = sorted(set(names) - in_template)
        if missing or unknown:
            raise PydanticCustomError(
                "placeholder_where_mismatch",
                "template and where placeholders differ; missing: {missing}; unused: {unused}",
                {"missing": ", ".join(missing) or "none", "unused": ", ".join(unknown) or "none"},
            )
        dangling = sorted(set().union(set(), *(w.references for w in self.where)) - in_template)
        if dangling:
            raise PydanticCustomError("unknown_constraint_placeholder", "constraints reference {placeholders}", {"placeholders": ", ".join(dangling)})
        return self

    def bind(self, values: Mapping[str, object]) -> None:
        """Validate the values an interpreter binds to the placeholders; raise one ValueError listing every failure."""
        failures: list[str] = []
        expected = self.placeholders
        failures += [f"{name}: no value bound" for name in sorted(expected - set(values))]
        failures += [f"{name}: not a placeholder of this schema" for name in sorted(set(values) - expected)]
        for where in self.where:
            if where.placeholder not in values:
                continue
            for constraint in where.constraints:
                try:
                    constraint.check(values[where.placeholder], values)
                except (ValueError, ValidationError, KeyError) as error:
                    failures.append(f"{where.placeholder}: {constraint.kind}: {error}")
        if failures:
            raise ValueError("\n".join(failures))
