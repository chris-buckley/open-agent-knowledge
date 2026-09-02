"""The identified base shared by every OAK entry."""

from pydantic import Field

from oak.base import DiscriminatedModel
from oak.vocabulary.text.slug_id import SlugId


class Entry(DiscriminatedModel):
    """The fields shared by every entry."""

    discriminator_field = "part"

    id: SlugId = Field(
        description="The entry id, unique in its OAK document.",
        examples=["example"],
    )
