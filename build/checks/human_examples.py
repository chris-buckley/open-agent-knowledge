"""Committed human-authored example execution and snapshot verification."""

from __future__ import annotations


def validate_human_examples() -> None:
    """Build every committed example and compare its checked-in render."""
    from examples.agents import (
        amendment_reviewer,
        compound_growth,
        delegation,
        implementer,
        interpreter_context,
        successor,
        successor_verifier,
        task_reviewer,
    )
    from examples.schemas import (
        api_coverage_table,
        code_changes,
        code_map,
        docs_index,
        error,
        hierarchical_outline,
        ideation_list,
        link_manifest,
        process_execution_table,
        smeac_plan,
        verification,
    )

    examples = (
        amendment_reviewer,
        compound_growth,
        delegation,
        implementer,
        interpreter_context,
        successor_verifier,
        successor,
        task_reviewer,
        api_coverage_table,
        code_changes,
        code_map,
        docs_index,
        error,
        hierarchical_outline,
        ideation_list,
        link_manifest,
        process_execution_table,
        smeac_plan,
        verification,
    )

    interpreter_context.run()

    for module in examples:
        rendered = module.build()
        target = module.TARGET

        if (
            not target.is_file()
            or target.read_text(
                encoding="utf-8"
            )
            != rendered
        ):
            raise RuntimeError(
                "example snapshot is missing or stale: "
                f"{target}"
            )


__all__ = [
    "validate_human_examples",
]
