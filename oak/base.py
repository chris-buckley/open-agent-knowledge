"""Shared OAK models: strict, closed, Rust regex, and identified entries."""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema

from oak.vocabulary import IriId


def _field_title(name: str, _field: object) -> str:
    return name.replace("_", " ").title()


class OakModel(BaseModel):
    """Every OAK model validates strictly and rejects unknown fields."""

    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        regex_engine="rust-regex",
        allow_inf_nan=False,
        validate_default=True,
        field_title_generator=_field_title,
    )


class DiscriminatedModel(OakModel):
    """A direct authoring model whose emitted JSON Schema requires its tag."""

    discriminator_field: ClassVar[str]

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        schema = handler.resolve_ref_schema(handler(core_schema))
        field = cls.discriminator_field
        if field in cls.model_fields:
            required = schema.setdefault("required", [])
            if field not in required:
                required.insert(0, field)
        return schema


class Entry(DiscriminatedModel):
    """The fields shared by every entry."""

    discriminator_field = "part"

    id: IriId = Field(
        description="The entry id, unique across the tree.",
        examples=["oak:entry/example"],
    )
