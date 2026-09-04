"""Generated authoring, grammar, documentation, and freshness checks."""

from __future__ import annotations

from build.checks.fixtures import ROOT
from oak.parse.document import parse
from oak.render import render
from oak.rules.guidance import AUTHORING_GUIDANCE

AUTHORING_MAX_BYTES = 18_000


def validate_outputs() -> None:
    """Verify authoring, grammar, documentation, and output path freshness."""
    from build.authoring import authoring, canonical_example, tree
    from build.docs import documents
    from build.ebnf import grammar

    authoring_text = authoring()
    authoring_node = tree()

    if render(parse(authoring_text), grouping="xml") + "\n" != authoring_text:
        raise RuntimeError("authoring output is not canonical XML OAK")

    expected_guidance = [
        guidance.instruction
        for guidance in AUTHORING_GUIDANCE
    ]
    actual_guidance = [
        instruction.body
        for instruction in authoring_node.instructions
    ]
    if actual_guidance != expected_guidance:
        raise RuntimeError("authoring output guidance is stale")

    if any(
        instruction.id.startswith("enforce-")
        for instruction in authoring_node.instructions
    ):
        raise RuntimeError("authoring output contains validator catalog instructions")

    if [constant.id for constant in authoring_node.constants] != [
        "architecture-capsule",
        "oak-ebnf",
        "canonical-oak",
    ]:
        raise RuntimeError("authoring output constants are not compact")

    if [schema.id for schema in authoring_node.schemas] != ["oak-document"]:
        raise RuntimeError("authoring output contains generated model schemas")

    example = canonical_example()
    if authoring_node.constants[-1].value != example:
        raise RuntimeError("authoring output canonical example is stale")

    if "orchestrator-example" in authoring_text:
        raise RuntimeError("authoring output contains the removed extra example")

    authoring_size = len(authoring_text.encode("utf-8"))
    if authoring_size > AUTHORING_MAX_BYTES:
        raise RuntimeError(
            "authoring output exceeds the compact byte limit: "
            f"{authoring_size} > {AUTHORING_MAX_BYTES}"
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
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            raise RuntimeError(
                "generated output is missing or stale: "
                f"{path}"
            )

    actual = set((ROOT / "outputs" / "docs").glob("*.md"))
    documented = {
        path
        for path in expected
        if path.parent == ROOT / "outputs" / "docs"
    }
    if actual != documented:
        raise RuntimeError("documentation output path set is stale")

    actual_root = {
        path
        for path in (ROOT / "outputs").iterdir()
        if path.is_file()
    }
    expected_root = {
        ROOT / "outputs" / "oak.ebnf",
        ROOT / "outputs" / "authoring.md",
    }
    if actual_root != expected_root:
        raise RuntimeError("generated root output path set is stale")


__all__ = [
    "AUTHORING_MAX_BYTES",
    "validate_outputs",
]
