"""Project model metadata and surface descriptors into generated products."""

from __future__ import annotations

import re

from oak.base import OakModel
from oak.node import Node
from oak.node.parts import (
    Act,
    All,
    Any,
    Assert,
    AtLeast,
    AtMost,
    BindingValue,
    Call,
    Compare,
    Constant,
    ConstantValue,
    Emit,
    Fail,
    Foreach,
    If,
    Instruction,
    Interface,
    InterfaceValue,
    Join,
    Lines,
    ListOf,
    LiteralValue,
    MaxChars,
    NonEmpty,
    Not,
    OneOf,
    Par,
    Process,
    Regex,
    Schema,
    Set,
    State,
    StateValue,
    Trigger,
    Type,
    ValueBinding,
    Where,
    While,
    where,
)
from oak.parse.fragments import parse_fragment
from oak.render.oak.data import (
    constant_text,
    constraint_text,
    named_value_line,
    where_line,
)
from oak.render.oak.groupings import (
    interface_xml,
    process_xml,
    schema_xml,
)
from oak.render.oak.processes import (
    binding_line,
    condition_text,
    process_value_text,
    step_lines,
)
from oak.render.oak.triggers import trigger_body
from oak.surface import SURFACES, Surface

AUTHORABLE_MODELS = (
    Type,
    OneOf,
    Regex,
    NonEmpty,
    MaxChars,
    Lines,
    ListOf,
    AtLeast,
    AtMost,
    Where,
    Schema,
    Instruction,
    Constant,
    State,
    LiteralValue,
    ConstantValue,
    StateValue,
    InterfaceValue,
    BindingValue,
    ValueBinding,
    Compare,
    All,
    Any,
    Not,
    Act,
    Set,
    Emit,
    If,
    Call,
    Fail,
    Assert,
    Foreach,
    While,
    Par,
    Join,
    Process,
    Trigger,
    Interface,
    Node,
)

_BOUNDARY = re.compile(
    r"(?<!^)(?=[A-Z])"
)


def slug(name: str) -> str:
    """Return one lower-kebab generated id."""
    return _BOUNDARY.sub(
        "-",
        name,
    ).replace(
        "_",
        "-",
    ).lower()


def model_schema(
    model: type[OakModel],
) -> dict[str, object]:
    """Return the model definition from generated JSON Schema."""
    schema = model.model_json_schema(
        by_alias=True
    )
    reference = schema.get("$ref")
    definitions = schema.get("$defs")

    if (
        isinstance(reference, str)
        and isinstance(definitions, dict)
        and reference.startswith("#/$defs/")
    ):
        resolved = definitions.get(
            reference[
                len("#/$defs/") :
            ]
        )

        if isinstance(resolved, dict):
            return resolved

    return schema


def model_examples(
    model: type[OakModel],
) -> list[OakModel]:
    """Return every validated model-level example."""
    extra = model.model_config.get(
        "json_schema_extra"
    )
    authored = (
        extra.get("examples")
        if isinstance(extra, dict)
        else None
    )

    if not authored:
        raise RuntimeError(
            f"{model.__name__} has no model examples"
        )

    return [
        model.model_validate(item)
        for item in authored
    ]


def field_description(
    model: type[OakModel],
    name: str,
) -> str:
    """Return one required field description."""
    field = model.model_fields[name]

    if not field.description:
        raise RuntimeError(
            f"{model.__name__}.{name} has no description"
        )

    return field.description


def _guaranteed(
    surface: Surface,
    name: str,
) -> bool:
    """Return whether the surface always renders the field non-empty."""
    if surface.model.model_fields[
        name
    ].is_required():
        return True

    return any(
        field_name == name
        and expected is not None
        for field_name, expected in surface.when
    )


def surface_schema(
    surface: Surface,
) -> Schema:
    """Project one authored surface into one OAK schema."""
    metadata = model_schema(
        surface.model
    )
    title = metadata.get("title")
    description = metadata.get(
        "description"
    )

    if not isinstance(title, str) or not title:
        raise RuntimeError(
            f"{surface.model.__name__} has no title"
        )

    if (
        not isinstance(description, str)
        or not description
    ):
        raise RuntimeError(
            f"{surface.model.__name__} has no description"
        )

    rendered = [
        field
        for field in surface.fields
        if field.role == "rendered"
    ]

    return Schema(
        id=surface.id,
        name=(
            title
            if len(
                [
                    item
                    for item in SURFACES
                    if item.model is surface.model
                ]
            )
            == 1
            else f"{title} {surface.id}"
        ),
        purpose=description,
        template=surface.shape,
        where=[
            where(
                field.placeholder,
                Type(of="string"),
                *(
                    [NonEmpty()]
                    if _guaranteed(
                        surface,
                        field.name,
                    )
                    else []
                ),
                description=field_description(
                    surface.model,
                    field.name,
                ),
            )
            for field in rendered
            if field.placeholder is not None
        ],
    )


def _instance(
    surface: Surface,
) -> OakModel:
    matches = [
        instance
        for instance in model_examples(
            surface.model
        )
        if surface.matches(instance)
    ]

    if not matches:
        raise RuntimeError(
            f"{surface.id} has no matching model example"
        )

    return matches[0]


def surface_example(
    surface: Surface,
    *,
    grouping: str = "xml",
) -> str:
    """Render one canonical example of one surface."""
    instance = _instance(surface)

    if isinstance(instance, Node):
        from oak.render import render

        return render(
            instance,
            grouping=grouping,
        )

    if isinstance(instance, Instruction):
        return instance.body

    if isinstance(instance, Constant):
        return constant_text(instance)

    if isinstance(instance, Schema):
        return schema_xml(instance)

    if isinstance(instance, State):
        return named_value_line(instance)

    if isinstance(instance, Trigger):
        return trigger_body(instance)

    if isinstance(instance, Process):
        return process_xml(instance)

    if isinstance(instance, Interface):
        return interface_xml(instance)

    if isinstance(
        instance,
        (
            Type,
            OneOf,
            Regex,
            NonEmpty,
            MaxChars,
            Lines,
            ListOf,
            AtLeast,
            AtMost,
        ),
    ):
        return constraint_text(instance)

    if isinstance(instance, Where):
        return where_line(instance)

    if isinstance(
        instance,
        (
            LiteralValue,
            ConstantValue,
            StateValue,
            InterfaceValue,
            BindingValue,
        ),
    ):
        return process_value_text(instance)

    if isinstance(instance, ValueBinding):
        return binding_line(instance)

    if isinstance(
        instance,
        (
            Compare,
            All,
            Any,
            Not,
        ),
    ):
        return condition_text(instance)

    if isinstance(
        instance,
        (
            Act,
            Set,
            Emit,
            If,
            Call,
            Fail,
            Assert,
            Foreach,
            While,
            Par,
            Join,
        ),
    ):
        return "\n".join(
            step_lines(instance)
        )

    raise TypeError(
        type(instance).__name__
    )


def parse_surface(
    surface: Surface,
    text: str,
    *,
    grouping: str = "xml",
) -> OakModel:
    """Parse one rendered surface through the intentional fragment API."""
    return parse_fragment(
        surface.model,
        text,
        grouping=grouping,
        path=surface.id,
    )


def surface_grammar(
    surface: Surface,
) -> str:
    """Return one generated EBNF surface production."""
    escaped = surface.shape.replace(
        "?",
        "??",
    )
    return (
        f"surface_{surface.id.replace('-', '_')} "
        f"= ? {escaped} ? ;"
    )


def model_surfaces(
    model: type[OakModel],
) -> tuple[Surface, ...]:
    """Return every surface for one authorable model."""
    return tuple(
        surface
        for surface in SURFACES
        if surface.model is model
    )


def all_surface_schemas() -> list[Schema]:
    """Return every generated surface schema."""
    return [
        surface_schema(surface)
        for surface in SURFACES
    ]


def surface_instance(
    surface: Surface,
) -> OakModel:
    """Return the validated model example selected by one surface."""
    return _instance(surface)
