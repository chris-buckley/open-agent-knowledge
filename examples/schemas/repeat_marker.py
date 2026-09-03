"""The repeat-marker instruction shared by the ported format schemas."""

from __future__ import annotations

from oak import Instruction

repeat_marker_instruction = Instruction(
    id="repeat-marker",
    body="A ... line in a template marks repetition of the pattern above it.",
)
