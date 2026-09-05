"""The ordered repository verification checks."""

from __future__ import annotations

from collections.abc import Callable

from build.checks.agents import validate_agents
from build.checks.authoring import validate_authoring_skill
from build.checks.architecture import validate_architecture
from build.checks.compact_syntax import (
    validate_compact_specimens,
    validate_compact_lexing,
    validate_compact_control,
    validate_compact_triggers,
    validate_compact_layout,
)
from build.checks.compact_runtime import (
    validate_compact_short_circuit,
    validate_compact_loop_bounds,
    validate_compact_routing,
    validate_compact_frames,
    validate_compact_relative_targets,
)
from build.checks.coding_standards import validate_coding_standards
from build.checks.context import validate_interpreter_context
from build.checks.evidence import validate_evidence
from build.checks.execution import (
    validate_execution,
    validate_source_routing,
    validate_while,
)
from build.checks.human_examples import validate_human_examples
from build.checks.interfaces import validate_interfaces
from build.checks.metadata import validate_metadata
from build.checks.outputs import validate_outputs
from build.checks.optional_validator import validate_optional_validator
from build.checks.parsing import validate_part_omission
from build.checks.plans import validate_plans
from build.checks.rendering import (
    validate_act_authoring,
    validate_json_ld_style_display,
)
from build.checks.resolution import validate_resolution
from build.checks.shapes import validate_shapes
from build.checks.surfaces import validate_surfaces
from build.checks.text import validate_text_examples
from build.checks.validation import validate_contract_rules

Check = Callable[[], None]

CHECKS: tuple[Check, ...] = (
    validate_compact_specimens,
    validate_compact_lexing,
    validate_compact_control,
    validate_compact_triggers,
    validate_compact_layout,
    validate_compact_short_circuit,
    validate_compact_loop_bounds,
    validate_compact_routing,
    validate_compact_frames,
    validate_compact_relative_targets,
    validate_text_examples,
    validate_metadata,
    validate_resolution,
    validate_interfaces,
    validate_execution,
    validate_interpreter_context,
    validate_evidence,
    validate_while,
    validate_part_omission,
    validate_act_authoring,
    validate_contract_rules,
    validate_source_routing,
    validate_json_ld_style_display,
    validate_human_examples,
    validate_shapes,
    validate_authoring_skill,
    validate_optional_validator,
    validate_plans,
    validate_agents,
    validate_coding_standards,
    validate_surfaces,
    validate_outputs,
    validate_architecture,
)

__all__ = [
    "CHECKS",
    "Check",
]
