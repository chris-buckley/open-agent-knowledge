"""The ordered repository verification checks."""

from __future__ import annotations

from collections.abc import Callable

from build.checks.agents import validate_agents
from build.checks.architecture import validate_architecture
from build.checks.execution import (
    validate_execution,
    validate_source_routing,
    validate_while,
)
from build.checks.human_examples import validate_human_examples
from build.checks.interfaces import validate_interfaces
from build.checks.metadata import validate_metadata
from build.checks.outputs import validate_outputs
from build.checks.parsing import validate_part_omission
from build.checks.rendering import (
    validate_act_authoring,
    validate_json_ld_style_display,
)
from build.checks.resolution import validate_resolution
from build.checks.surfaces import validate_surfaces
from build.checks.text import validate_text_examples
from build.checks.validation import validate_contract_rules

Check = Callable[[], None]

CHECKS: tuple[Check, ...] = (
    validate_text_examples,
    validate_metadata,
    validate_resolution,
    validate_interfaces,
    validate_execution,
    validate_while,
    validate_part_omission,
    validate_act_authoring,
    validate_contract_rules,
    validate_source_routing,
    validate_json_ld_style_display,
    validate_human_examples,
    validate_agents,
    validate_surfaces,
    validate_outputs,
    validate_architecture,
)

__all__ = [
    "CHECKS",
    "Check",
]
