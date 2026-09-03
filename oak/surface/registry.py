"""The explicit ordered surface registry, indexes, and lookups."""

from __future__ import annotations

from oak.base import OakModel
from oak.surface.constraints import CONSTRAINT_SURFACES
from oak.surface.entries import (
    ENTRY_SURFACES_AFTER_PROCESSES,
    ENTRY_SURFACES_BEFORE_PROCESSES,
)
from oak.surface.model import Surface
from oak.surface.processes import PROCESS_SURFACES

SURFACES = (
    *CONSTRAINT_SURFACES,
    *ENTRY_SURFACES_BEFORE_PROCESSES,
    *PROCESS_SURFACES,
    *ENTRY_SURFACES_AFTER_PROCESSES,
)

SURFACES_BY_ID = {
    surface.id: surface
    for surface in SURFACES
}

if len(SURFACES_BY_ID) != len(SURFACES):
    raise RuntimeError(
        "surface ids are not unique"
    )


def surfaces_for_model(
    model: type[OakModel],
) -> tuple[Surface, ...]:
    """Return every concrete surface for one model."""
    return tuple(
        surface
        for surface in SURFACES
        if surface.model is model
    )


def surface_for(
    value: OakModel,
) -> Surface:
    """Return the one descriptor selected by a model value."""
    matches = [
        surface
        for surface in SURFACES
        if surface.matches(value)
    ]

    if len(matches) != 1:
        raise RuntimeError(
            f"{type(value).__name__} selects {len(matches)} surfaces: "
            + ", ".join(
                surface.id
                for surface in matches
            )
        )

    return matches[0]


def entry_surface(
    tag: str,
) -> Surface:
    """Return the one body-entry descriptor for a tag."""
    matches = [
        surface
        for surface in SURFACES
        if surface.tag == tag
    ]

    if len(matches) != 1:
        raise RuntimeError(
            f"entry tag {tag} selects {len(matches)} surfaces"
        )

    return matches[0]


__all__ = [
    "SURFACES",
    "SURFACES_BY_ID",
    "entry_surface",
    "surface_for",
    "surfaces_for_model",
]
