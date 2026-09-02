"""Surface descriptor models and field-classification builders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from oak.base import OakModel

FieldRole = Literal[
    "rendered",
    "fixed",
    "omitted",
    "generated",
]
_PRESENT = object()


@dataclass(frozen=True, slots=True)
class SurfaceField:
    """One model field classification in one authored text variant."""

    name: str
    role: FieldRole
    placeholder: str | None = None


@dataclass(frozen=True, slots=True)
class Surface:
    """One concrete authored text variant."""

    id: str
    model: type[OakModel]
    shape: str
    fields: tuple[SurfaceField, ...]
    part: str | None = None
    tag: str | None = None
    when: tuple[
        tuple[str, object],
        ...,
    ] = ()

    def matches(
        self,
        value: OakModel,
    ) -> bool:
        """Return whether this descriptor selects one model value."""
        return type(value) is self.model and all(
            (
                getattr(value, name) is not None
                if expected is _PRESENT
                else getattr(value, name) == expected
            )
            for name, expected in self.when
        )


def _fields(
    model: type[OakModel],
    *,
    rendered: tuple[str, ...] = (),
    fixed: tuple[str, ...] = (),
    omitted: tuple[str, ...] = (),
    generated: tuple[str, ...] = (),
) -> tuple[SurfaceField, ...]:
    roles: dict[
        str,
        FieldRole,
    ] = {}

    for role, names in (
        ("rendered", rendered),
        ("fixed", fixed),
        ("omitted", omitted),
        ("generated", generated),
    ):
        for name in names:
            if name in roles:
                raise RuntimeError(
                    f"{model.__name__}.{name} is classified twice"
                )

            roles[name] = role

    missing = (
        set(model.model_fields)
        - set(roles)
    )
    unknown = (
        set(roles)
        - set(model.model_fields)
    )

    if missing or unknown:
        raise RuntimeError(
            f"{model.__name__} surface fields differ; "
            f"missing={sorted(missing)} unknown={sorted(unknown)}"
        )

    return tuple(
        SurfaceField(
            name=name,
            role=roles[name],
            placeholder=(
                name.upper()
                if roles[name] == "rendered"
                else None
            ),
        )
        for name in model.model_fields
    )


def _surface(
    identifier: str,
    model: type[OakModel],
    shape: str,
    *,
    rendered: tuple[str, ...] = (),
    fixed: tuple[str, ...] = (),
    omitted: tuple[str, ...] = (),
    generated: tuple[str, ...] = (),
    part: str | None = None,
    tag: str | None = None,
    when: tuple[
        tuple[str, object],
        ...,
    ] = (),
) -> Surface:
    return Surface(
        id=identifier,
        model=model,
        shape=shape,
        fields=_fields(
            model,
            rendered=rendered,
            fixed=fixed,
            omitted=omitted,
            generated=generated,
        ),
        part=part,
        tag=tag,
        when=when,
    )


__all__ = [
    "FieldRole",
    "Surface",
    "SurfaceField",
]
