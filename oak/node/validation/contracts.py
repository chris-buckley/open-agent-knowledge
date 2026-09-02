"""Transport-neutral emit-contract and directed-cycle algorithms."""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping
from dataclasses import dataclass
from typing import TypeVar

from oak.node.parts.schemas.binding import SchemaBindingError
from oak.node.parts.schemas.model import Schema

CycleNode = TypeVar(
    "CycleNode",
    bound=Hashable,
)


@dataclass(frozen=True, slots=True)
class EmitContractResult:
    """The structural or static-value failure of one resolved emit contract."""

    missing: tuple[str, ...] = ()
    unused: tuple[str, ...] = ()
    binding_error: SchemaBindingError | None = None

    @property
    def placeholders_match(self) -> bool:
        """Return whether the authored and schema placeholder sets match."""
        return not self.missing and not self.unused


def inspect_emit_contract(
    schema: Schema,
    placeholders: Iterable[str],
    values: Mapping[str, object] | None,
) -> EmitContractResult:
    """Inspect one emit against its looked-up schema and static values."""
    authored = set(placeholders)
    expected = schema.placeholders
    missing = tuple(
        sorted(
            expected - authored
        )
    )
    unused = tuple(
        sorted(
            authored - expected
        )
    )

    if missing or unused:
        return EmitContractResult(
            missing=missing,
            unused=unused,
        )

    if values is None:
        return EmitContractResult()

    try:
        schema.bind(values)

    except SchemaBindingError as error:
        return EmitContractResult(
            binding_error=error,
        )

    return EmitContractResult()


def find_cycle(
    edges: Mapping[
        CycleNode,
        Iterable[CycleNode],
    ],
) -> list[CycleNode] | None:
    """Return the first directed cycle in mapping and edge iteration order."""
    state: dict[
        CycleNode,
        int,
    ] = {}
    stack: list[CycleNode] = []

    def visit(
        current: CycleNode,
    ) -> list[CycleNode] | None:
        state[current] = 1
        stack.append(current)

        for target in edges.get(
            current,
            (),
        ):
            target_state = state.get(
                target,
                0,
            )

            if target_state == 0:
                cycle = visit(target)

                if cycle is not None:
                    return cycle

            elif target_state == 1:
                start = stack.index(target)
                return stack[start:] + [target]

        stack.pop()
        state[current] = 2
        return None

    for source in edges:
        if state.get(source, 0) != 0:
            continue

        cycle = visit(source)

        if cycle is not None:
            return cycle

    return None


__all__ = [
    "EmitContractResult",
    "find_cycle",
    "inspect_emit_contract",
]
