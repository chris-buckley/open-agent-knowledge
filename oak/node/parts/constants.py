"""The constants part."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, JsonValue, model_validator

from oak.node.parts.entry import Entry
from oak.node.parts.interfaces import SchemaTarget
from oak.rules.validation import rule_error
from oak.vocabulary.text.placeholder import Placeholder

ConstantForm = Literal["inline", "text", "json", "csv", "yaml"]


class Constant(Entry):
    """One value that stays the same during use."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "part": "constants",
                    "id": "default-time-zone",
                    "value": "Z",
                },
                {
                    "part": "constants",
                    "id": "repository-tree",
                    "form": "text",
                    "value": "oak\n└── SKILL.md",
                },
                {
                    "part": "constants",
                    "id": "api-config",
                    "form": "json",
                    "value": {
                        "retries": 3,
                        "timeout_ms": 2000,
                    },
                },
                {
                    "part": "constants",
                    "id": "service-table",
                    "form": "csv",
                    "value": [
                        {
                            "service": "billing",
                            "enabled": True,
                        }
                    ],
                },
                {
                    "part": "constants",
                    "id": "deployment-config",
                    "form": "yaml",
                    "value": {
                        "region": "ap-southeast-2",
                        "replicas": 2,
                    },
                },
            ]
        }
    )

    part: Literal["constants"] = Field(
        default="constants",
        description="The entry part discriminator.",
        examples=["constants"],
    )
    form: ConstantForm = Field(
        default="inline",
        description="The OAK constant form.",
        examples=["inline", "text", "json", "csv", "yaml"],
    )
    schema_id: SchemaTarget | None = Field(
        default=None,
        alias="schema",
        title="Schema",
        description="The optional local or relative schema target whose placeholder constrains the value.",
        examples=["schema.scaling"],
    )
    placeholder: Placeholder | None = Field(
        default=None,
        description="The schema placeholder the value must satisfy.",
        examples=["FACTOR"],
    )
    value: JsonValue = Field(
        description="The value that stays the same.",
        examples=[
            "Z",
            "oak\n└── SKILL.md",
            {"enabled": True},
            [{"service": "billing", "enabled": True}],
        ],
    )

    @model_validator(mode="after")
    def valid_binding(self) -> Self:
        if (self.schema_id is None) != (self.placeholder is None):
            raise rule_error(
                "incomplete_schema_binding",
                "a schema binding needs both a schema target and a placeholder",
            )
        return self

    @model_validator(mode="after")
    def valid_form(self) -> Self:
        if self.form == "text" and not isinstance(self.value, str):
            raise rule_error(
                "invalid_text_constant",
                "a text constant value must be a string",
            )

        if self.form != "csv":
            return self

        if not isinstance(self.value, list) or not self.value:
            raise rule_error(
                "invalid_csv_constant",
                "a CSV constant value must be a non-empty list of rows",
            )

        if not all(isinstance(row, dict) for row in self.value):
            raise rule_error(
                "invalid_csv_constant",
                "each CSV constant row must be an object",
            )

        rows = self.value
        first = rows[0]
        if not isinstance(first, dict):
            return self

        columns = list(first)
        if not columns:
            raise rule_error(
                "invalid_csv_constant",
                "a CSV constant must have at least one column",
            )

        expected = set(columns)
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                continue

            if set(row) != expected:
                raise rule_error(
                    "csv_column_mismatch",
                    "CSV row {index} has different columns",
                    {"index": index},
                )

            if any(
                isinstance(cell, (list, dict))
                for cell in row.values()
            ):
                raise rule_error(
                    "invalid_csv_cell",
                    "CSV row {index} contains a non-scalar cell",
                    {"index": index},
                )

        return self
