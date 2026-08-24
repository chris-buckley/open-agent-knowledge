"""Validate every declared model and field example."""

from typing import Annotated

from pydantic import create_model

from oak.base import OakModel
from oak.node import Node, Root
from oak.node.parts import (
    AtLeast,
    AtMost,
    Constant,
    Instruction,
    Interface,
    Lines,
    ListOf,
    MaxChars,
    NonEmpty,
    OneOf,
    Process,
    Regex,
    Schema,
    State,
    Trigger,
    Type,
    Where,
)

MODELS = (
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
    Trigger,
    Process,
    Interface,
    Node,
    Root,
)


def validate_examples() -> None:
    """Raise when a model or field example is missing or invalid."""
    for model in MODELS:
        extra = model.model_config.get("json_schema_extra")
        examples = extra.get("examples") if isinstance(extra, dict) else None
        if not examples:
            raise RuntimeError(f"{model.__name__} has no model examples")
        for index, example in enumerate(examples):
            try:
                model.model_validate(example)
            except Exception as error:
                raise RuntimeError(
                    f"{model.__name__} model example {index} is invalid: {error}"
                ) from error

        for name, field in model.model_fields.items():
            if not field.description:
                raise RuntimeError(f"{model.__name__}.{name} has no description")
            if not field.examples:
                raise RuntimeError(f"{model.__name__}.{name} has no examples")
            annotation = (
                Annotated[field.annotation, *field.metadata]
                if field.metadata
                else field.annotation
            )
            example_model = create_model(
                f"{model.__name__}{name.title()}Example",
                __base__=OakModel,
                value=(annotation, ...),
            )
            for index, example in enumerate(field.examples):
                try:
                    example_model.model_validate({"value": example})
                except Exception as error:
                    raise RuntimeError(
                        f"{model.__name__}.{name} example {index} is invalid: {error}"
                    ) from error


if __name__ == "__main__":
    validate_examples()
