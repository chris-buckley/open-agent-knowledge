"""Pydantic model, field, example, and metadata verification."""

from __future__ import annotations

from typing import Annotated

from pydantic import create_model

from build.surfaces import (
    AUTHORABLE_MODELS,
    model_examples,
    model_schema,
)
from oak.base import OakModel
from oak.execute.models import Arrival, Emission, ExecutionResult
from oak.vocabulary.datatypes.datetime import DateTime
from oak.vocabulary.datatypes.quantity import Quantity

METADATA_MODELS = (
    *AUTHORABLE_MODELS,
    Quantity,
    DateTime,
    Arrival,
    Emission,
    ExecutionResult,
)


def _field_model(
    model: type[OakModel],
    name: str,
) -> type[OakModel]:
    field = model.model_fields[name]
    annotation = (
        Annotated[
            field.annotation,
            *field.metadata,
        ]
        if field.metadata
        else field.annotation
    )
    return create_model(
        f"{model.__name__}{name.title()}Example",
        __base__=OakModel,
        value=(annotation, ...),
    )


def validate_metadata() -> None:
    """Validate model metadata and every declared model and field example."""
    for model in METADATA_MODELS:
        schema = model_schema(model)

        if not schema.get("title") or not schema.get("description"):
            raise RuntimeError(
                f"{model.__name__} lacks title or description"
            )

        model_examples(model)

        for name, field in model.model_fields.items():
            if not field.description:
                raise RuntimeError(
                    f"{model.__name__}.{name} has no description"
                )

            if not field.examples:
                raise RuntimeError(
                    f"{model.__name__}.{name} has no examples"
                )

            example_model = _field_model(model, name)

            for example in field.examples:
                example_model.model_validate({"value": example})


__all__ = [
    "METADATA_MODELS",
    "validate_metadata",
]
