"""The OAK display form for datetimes."""

from oak.vocabulary.datatypes.datetime import DateTime


def datetime_text(value: DateTime) -> str:
    """Render ISO 8601 text and an optional IANA name."""
    text = value.value.isoformat()
    if text.endswith("+00:00"):
        text = text[:-6] + "Z"
    if value.zone is not None:
        text += f" [{value.zone}]"
    return text
