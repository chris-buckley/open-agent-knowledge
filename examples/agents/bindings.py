"""Binding lists shared by the agent examples."""

from __future__ import annotations

from collections.abc import Sequence

from oak import BindingValue, InterfaceValue, ValueBinding


def local_bindings(placeholders: Sequence[str]) -> list[ValueBinding]:
    """Bind each placeholder to the local binding of the same name."""
    return [ValueBinding(placeholder=name, value=BindingValue(binding=name)) for name in placeholders]


def interface_bindings(interface: str, placeholders: Sequence[str]) -> list[ValueBinding]:
    """Bind each placeholder to the same-named value of one interface."""
    return [
        ValueBinding(placeholder=name, value=InterfaceValue(interface=interface, placeholder=name))
        for name in placeholders
    ]
