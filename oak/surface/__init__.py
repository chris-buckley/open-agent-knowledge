"""Public authored-surface descriptors and deterministic lookups."""

from __future__ import annotations

from oak.surface.model import FieldRole, Surface, SurfaceField
from oak.surface.registry import (
    SURFACES,
    SURFACES_BY_ID,
    entry_surface,
    surface_for,
    surfaces_for_model,
)

__all__ = [
    "FieldRole",
    "SURFACES",
    "SURFACES_BY_ID",
    "Surface",
    "SurfaceField",
    "entry_surface",
    "surface_for",
    "surfaces_for_model",
]
