"""Document parsing, part omission, and grouping verification."""

from __future__ import annotations

from build.checks.fixtures import normalized
from oak.node.model import Node
from oak.node.parts.instructions import Instruction
from oak.node.parts.state import State
from oak.parse.document import parse
from oak.parse.errors import OakParseError
from oak.render import render

_MARKDOWN_FENCE = "~" * 4


def validate_part_omission() -> None:
    """Verify empty, sparse, ordered, and separated OAK parts."""
    if (
        render(
            Node(),
            grouping="xml",
        )
        != ""
        or render(
            Node(),
            grouping="markdown",
        )
        != ""
    ):
        raise RuntimeError(
            "empty node must render as one empty document"
        )

    if parse("").model_dump() != Node().model_dump():
        raise RuntimeError(
            "empty document must parse as one empty node"
        )

    single = Node(
        instructions=[
            Instruction(
                id="record",
                body="Record the mode.",
            )
        ]
    )
    sparse = Node(
        state=[
            State(
                id="mode",
                value="idle",
            )
        ]
    )
    state_preamble = (
        "State holds values that persist "
        "and can change while processes run."
    )
    expected_renders = {
        (
            "single",
            "xml",
        ): (
            "<instructions>\n"
            "Record the mode.\n"
            "</instructions>"
        ),
        (
            "single",
            "markdown",
        ): (
            f"{_MARKDOWN_FENCE}instructions\n"
            "Record the mode.\n"
            f"{_MARKDOWN_FENCE}"
        ),
        (
            "sparse",
            "xml",
        ): (
            "<instructions>\n"
            f"{state_preamble}\n"
            "</instructions>\n\n"
            "<state>\n"
            'mode: "idle"\n'
            "</state>"
        ),
        (
            "sparse",
            "markdown",
        ): (
            f"{_MARKDOWN_FENCE}instructions\n"
            f"{state_preamble}\n"
            f"{_MARKDOWN_FENCE}\n\n"
            f"{_MARKDOWN_FENCE}state\n"
            'mode: "idle"\n'
            f"{_MARKDOWN_FENCE}"
        ),
    }

    for name, node in (
        (
            "single",
            single,
        ),
        (
            "sparse",
            sparse,
        ),
    ):
        for grouping in (
            "xml",
            "markdown",
        ):
            rendered = render(
                node,
                grouping=grouping,
            )

            if rendered != expected_renders[
                name,
                grouping,
            ]:
                raise RuntimeError(
                    f"{name} {grouping} render changed"
                )

            if normalized(
                parse(rendered)
            ) != normalized(node):
                raise RuntimeError(
                    f"{name} {grouping} parse changed"
                )

    invalid_documents = (
        (
            (
                "<state>\n"
                'mode: "idle"\n'
                "</state>\n\n"
                "<constants>\n"
                "limit: 1\n"
                "</constants>"
            ),
            "part_order",
        ),
        (
            (
                "<state>\n"
                'mode: "idle"\n'
                "</state>\n\n"
                "<state>\n"
                'mode: "idle"\n'
                "</state>"
            ),
            "part_order",
        ),
        (
            (
                "<constants>\n"
                "limit: 1\n"
                "</constants>\n"
                "<state>\n"
                'mode: "idle"\n'
                "</state>"
            ),
            "part_separator",
        ),
    )

    for source, code in invalid_documents:
        try:
            parse(source)

        except OakParseError as error:
            if error.failures[0].code != code:
                raise RuntimeError(
                    f"expected {code}, got "
                    f"{error.failures[0].code}"
                ) from None

        else:
            raise RuntimeError(
                f"expected {code}"
            )


__all__ = [
    "validate_part_omission",
]
