"""Generated authoring, grammar, documentation, and freshness checks."""

from __future__ import annotations

from build.checks.fixtures import ROOT
from oak.parse.document import parse
from oak.render import render
from oak.rules.guidance import (
    ACT_GUIDANCE,
    DECOMPOSITION_GUIDANCE,
    DELEGATION_GUIDANCE,
    ENTRY_ID_GUIDANCE,
    NAMING_GUIDANCE,
)


def validate_outputs() -> None:
    """Verify authoring, grammar, documentation, and output path freshness."""
    from build.authoring import authoring, tree
    from build.docs import documents
    from build.ebnf import grammar

    authoring_text = authoring()

    if (
        render(
            parse(authoring_text),
            grouping="xml",
        )
        + "\n"
        != authoring_text
    ):
        raise RuntimeError(
            "authoring output is not canonical XML OAK"
        )

    bodies = [
        instruction.body
        for instruction in tree().instructions
    ]

    for guidance in (
        *ENTRY_ID_GUIDANCE,
        *NAMING_GUIDANCE,
        *DECOMPOSITION_GUIDANCE,
        *ACT_GUIDANCE,
        *DELEGATION_GUIDANCE,
    ):
        if bodies.count(
            guidance.instruction
        ) != 1:
            raise RuntimeError(
                "authoring output does not contain guidance "
                f"exactly once: {guidance.id}"
            )

    expected = {
        ROOT / "outputs" / "oak.ebnf": grammar(),
        ROOT / "outputs" / "authoring.md": authoring_text,
        **{
            ROOT / "outputs" / "docs" / name: text
            for name, text in documents().items()
        },
    }

    for path, text in expected.items():
        if (
            not path.is_file()
            or path.read_text(
                encoding="utf-8"
            )
            != text
        ):
            raise RuntimeError(
                "generated output is missing or stale: "
                f"{path}"
            )

    actual = set(
        (
            ROOT
            / "outputs"
            / "docs"
        ).glob("*.md")
    )
    documented = {
        path
        for path in expected
        if path.parent
        == ROOT / "outputs" / "docs"
    }

    if actual != documented:
        raise RuntimeError(
            "documentation output path set is stale"
        )

    actual_root = {
        path
        for path in (
            ROOT
            / "outputs"
        ).iterdir()
        if path.is_file()
    }
    expected_root = {
        ROOT / "outputs" / "oak.ebnf",
        ROOT / "outputs" / "authoring.md",
    }

    if actual_root != expected_root:
        raise RuntimeError(
            "generated root output path set is stale"
        )


__all__ = [
    "validate_outputs",
]
