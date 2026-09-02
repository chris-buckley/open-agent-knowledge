"""Small typed helpers for direct Python authoring."""

from __future__ import annotations

from collections.abc import Iterable

from oak.node.parts.interfaces import SchemaTarget
from oak.node.parts.processes.steps import Act
from oak.node.parts.processes.values import ValueBinding
from oak.vocabulary.text.non_blank_line import NonBlankLine
from oak.vocabulary.text.placeholder import Placeholder


class _ActAuthor:
    """Construct the existing Act model in its two authored forms."""

    def __call__(
        self,
        instruction: NonBlankLine,
        *,
        input: SchemaTarget | None = None,
        output: SchemaTarget | None = None,
        inputs: Iterable[ValueBinding] = (),
        outputs: Iterable[Placeholder] = (),
    ) -> Act:
        """Return one interpreter-native act."""
        return Act(
            input=input,
            output=output,
            instruction=instruction,
            inputs=list(inputs),
            outputs=list(outputs),
        )

    def tool(
        self,
        name: NonBlankLine,
        instruction: NonBlankLine,
        *,
        input: SchemaTarget | None = None,
        output: SchemaTarget | None = None,
        inputs: Iterable[ValueBinding] = (),
        outputs: Iterable[Placeholder] = (),
    ) -> Act:
        """Return one act bound to an exact supplied tool name."""
        return Act(
            tool=name,
            input=input,
            output=output,
            instruction=instruction,
            inputs=list(inputs),
            outputs=list(outputs),
        )


ACT = _ActAuthor()

__all__ = ["ACT"]
