"""Stable records for validation rules and authoring guidance."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthoringRule:
    """One stable validator instruction."""

    code: str
    instruction: str
    models: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class GuidanceRule:
    """One generated instruction for authoring OAK."""

    id: str
    instruction: str


__all__ = [
    "AuthoringRule",
    "GuidanceRule",
]
