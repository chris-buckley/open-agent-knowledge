"""Small typed helpers for direct Python authoring."""

from __future__ import annotations

from collections.abc import Iterable

from oak.node.parts.processes import Act, ValueBinding
from oak.vocabulary import NonBlankLine, Placeholder


class _ActAuthor:
    """Construct the existing Act model in its two authored forms."""

    def __call__(
        self,
        instruction: NonBlankLine,
        *,
        inputs: Iterable[ValueBinding] = (),
        outputs: Iterable[Placeholder] = (),
    ) -> Act:
        """Return one interpreter-native act."""
        return Act(
            instruction=instruction,
            inputs=list(inputs),
            outputs=list(outputs),
        )

    def tool(
        self,
        name: NonBlankLine,
        instruction: NonBlankLine,
        *,
        inputs: Iterable[ValueBinding] = (),
        outputs: Iterable[Placeholder] = (),
    ) -> Act:
        """Return one act bound to an exact supplied tool name."""
        return Act(
            tool=name,
            instruction=instruction,
            inputs=list(inputs),
            outputs=list(outputs),
        )


ACT = _ActAuthor()

__all__ = ["ACT"]
