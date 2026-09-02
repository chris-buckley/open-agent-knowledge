"""Exact named-tool contract and parallel-permission validation."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING, Protocol

from pydantic_core import PydanticCustomError

from oak.node.parts.processes.steps import (
    Act,
    Foreach,
    If,
    Par,
    Step,
    While,
)

if TYPE_CHECKING:
    from oak.node.model import Node


class ToolContractLike(Protocol):
    """The tool contract fields used by node validation."""

    inputs: frozenset[str]
    outputs: frozenset[str]
    parallel: bool
    input: str | None
    output: str | None


def _walk_steps(
    steps: list[Step],
    *,
    parallel: bool = False,
) -> Iterator[tuple[Step, bool]]:
    for step in steps:
        yield step, parallel

        if isinstance(step, If):
            yield from _walk_steps(
                step.then,
                parallel=parallel,
            )

            if step.otherwise is not None:
                yield from _walk_steps(
                    step.otherwise,
                    parallel=parallel,
                )

        elif isinstance(step, Foreach):
            yield from _walk_steps(
                step.steps,
                parallel=parallel,
            )

        elif isinstance(step, While):
            yield from _walk_steps(
                step.steps,
                parallel=parallel,
            )

        elif isinstance(step, Par):
            yield from _walk_steps(
                step.steps,
                parallel=True,
            )


def validate_tools(
    node: Node,
    tools: Mapping[str, ToolContractLike],
) -> None:
    """Validate exact tool names, contracts, and parallel permission."""
    for process in node.processes:
        for step, parallel in _walk_steps(process.steps):
            if not isinstance(step, Act) or step.tool is None:
                continue

            contract = tools.get(step.tool)

            if contract is None:
                raise PydanticCustomError(
                    "unknown_tool",
                    "process {process} names unknown tool {tool}",
                    {
                        "process": process.id,
                        "tool": step.tool,
                    },
                )

            authored_inputs = frozenset(
                binding.placeholder
                for binding in step.inputs
            )
            authored_outputs = frozenset(step.outputs)

            if (
                authored_inputs != contract.inputs
                or authored_outputs != contract.outputs
                or step.input != contract.input
                or step.output != contract.output
            ):
                raise PydanticCustomError(
                    "tool_contract_mismatch",
                    "process {process} act contract differs from tool {tool}",
                    {
                        "process": process.id,
                        "tool": step.tool,
                    },
                )

            if parallel and not contract.parallel:
                raise PydanticCustomError(
                    "tool_parallelism_unknown",
                    "process {process} uses tool {tool} in PAR without parallel permission",
                    {
                        "process": process.id,
                        "tool": step.tool,
                    },
                )


__all__ = [
    "ToolContractLike",
    "validate_tools",
]
