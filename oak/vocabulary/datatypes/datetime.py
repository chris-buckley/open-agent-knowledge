"""An aware datetime with an optional IANA time zone name."""

from datetime import datetime

from pydantic import AwareDatetime, ConfigDict, Field
from pydantic_extra_types.timezone_name import TimeZoneName

from oak.base import OakModel


class DateTime(OakModel):
    """One aware datetime and its optional IANA time zone name."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "value": datetime.fromisoformat(
                        "2026-08-24T17:35:38+10:00"
                    ),
                    "zone": "Australia/Brisbane",
                }
            ]
        }
    )

    value: AwareDatetime = Field(
        description="The datetime with a numeric UTC offset.",
        examples=[
            datetime.fromisoformat("2026-08-24T17:35:38+10:00")
        ],
    )
    zone: TimeZoneName | None = Field(
        default=None,
        description="The optional IANA time zone name.",
        examples=["Australia/Brisbane"],
    )
