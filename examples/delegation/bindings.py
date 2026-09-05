"""Shared direct-authoring binding helpers for agent examples."""

from collections.abc import Sequence

from oak import BindingValue, ValueBinding


def local_bindings(placeholders: Sequence[str]) -> list[ValueBinding]:
    """Bind each placeholder to the same-named local process binding."""
    return [
        ValueBinding(
            placeholder=name,
            value=BindingValue(binding=name),
        )
        for name in placeholders
    ]


__all__ = ["local_bindings"]
