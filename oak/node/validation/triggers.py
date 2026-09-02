"""Trigger source, seed, guard, and overlap validation."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations

from pydantic_core import PydanticCustomError

from oak.node.index import NodeIndex
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes.conditions import (
    All,
    Compare,
    Condition,
    Not,
)
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.operators import (
    ConditionOperator,
    invert_operator,
    json_equal,
    ordered_pair,
    reverse_operator,
)
from oak.node.parts.processes.values import StateValue
from oak.node.parts.triggers import Trigger
from oak.node.validation.conditions import compare_static, validate_condition
from oak.node.validation.values import (
    STATIC_MISSING,
    process_schema,
    static_value,
    validate_value,
)
from oak.rules.validation import rule_error
from oak.vocabulary.text.target_path import target_id

GuardAtom = tuple[str, ConditionOperator, object]


def validate_trigger_contract(
    trigger: Trigger,
    inputs: set[str] | None,
) -> None:
    """Validate one trigger seed against the selected process input schema."""
    authored = [
        binding.placeholder
        for binding in trigger.seed
    ]

    if inputs is None:
        if authored:
            raise rule_error(
                "trigger_contract_mismatch",
                "trigger {trigger} seeds a process that has no input schema",
                {"trigger": trigger.id},
            )

        return

    if len(authored) == len(inputs) and set(authored) == inputs:
        return

    raise rule_error(
        "trigger_contract_mismatch",
        (
            "trigger {trigger} seeds differ from the process input schema; "
            "missing: {missing}; unused: {unused}"
        ),
        {
            "trigger": trigger.id,
            "missing": (
                ", ".join(
                    sorted(inputs - set(authored))
                )
                or "none"
            ),
            "unused": (
                ", ".join(
                    sorted(set(authored) - inputs)
                )
                or "none"
            ),
        },
    )


def _guard_atom(
    index: NodeIndex,
    trigger: Trigger,
    condition: Compare,
) -> GuardAtom | None:
    if isinstance(condition.left, StateValue):
        static = static_value(
            index,
            trigger,
            condition.right,
        )

        if static is not STATIC_MISSING:
            return (
                target_id(condition.left.state),
                condition.operator,
                static,
            )

    if isinstance(condition.right, StateValue):
        static = static_value(
            index,
            trigger,
            condition.left,
        )

        if static is not STATIC_MISSING:
            return (
                target_id(condition.right.state),
                reverse_operator(condition.operator),
                static,
            )

    return None


def _guard_atoms(
    index: NodeIndex,
    trigger: Trigger,
    condition: Condition,
) -> list[GuardAtom] | None:
    if isinstance(condition, Compare):
        atom = _guard_atom(
            index,
            trigger,
            condition,
        )
        return (
            [atom]
            if atom is not None
            else None
        )

    if isinstance(condition, All):
        result: list[GuardAtom] = []

        for child in condition.conditions:
            child_atoms = _guard_atoms(
                index,
                trigger,
                child,
            )

            if child_atoms is None:
                return None

            result.extend(child_atoms)

        return result

    if isinstance(condition, Not):
        if not isinstance(condition.condition, Compare):
            return None

        atom = _guard_atom(
            index,
            trigger,
            condition.condition,
        )

        if atom is None:
            return None

        state, operator, value = atom
        return [
            (
                state,
                invert_operator(operator),
                value,
            )
        ]

    return None


def _atom_accepts(
    atom: GuardAtom,
    candidate: object,
) -> bool | None:
    _, operator, value = atom

    try:
        return compare_static(
            operator,
            candidate,
            value,
        )

    except PydanticCustomError:
        return None


def _range_bounds(
    atoms: list[GuardAtom],
) -> tuple[
    tuple[object, bool] | None,
    tuple[object, bool] | None,
] | None:
    lower: tuple[object, bool] | None = None
    upper: tuple[object, bool] | None = None

    for _, operator, value in atoms:
        if operator in (
            "greater_than",
            "greater_than_or_equal",
        ):
            inclusive = operator == "greater_than_or_equal"

            if lower is None:
                lower = value, inclusive
                continue

            pair = ordered_pair(
                lower[0],
                value,
            )

            if pair is None:
                return None

            current, candidate = pair

            if (
                candidate > current
                or (
                    candidate == current
                    and not inclusive
                    and lower[1]
                )
            ):
                lower = value, inclusive

            continue

        if operator in (
            "less_than",
            "less_than_or_equal",
        ):
            inclusive = operator == "less_than_or_equal"

            if upper is None:
                upper = value, inclusive
                continue

            pair = ordered_pair(
                upper[0],
                value,
            )

            if pair is None:
                return None

            current, candidate = pair

            if (
                candidate < current
                or (
                    candidate == current
                    and not inclusive
                    and upper[1]
                )
            ):
                upper = value, inclusive

    return lower, upper


def _atoms_conflict(
    left: list[GuardAtom],
    right: list[GuardAtom],
) -> bool:
    states = {
        atom[0]
        for atom in left
    } & {
        atom[0]
        for atom in right
    }

    for state in states:
        combined = [
            atom
            for atom in left + right
            if atom[0] == state
        ]
        equals = [
            atom[2]
            for atom in combined
            if atom[1] == "equals"
        ]

        if equals:
            first = equals[0]

            if any(
                not json_equal(
                    first,
                    value,
                )
                for value in equals[1:]
            ):
                return True

            if any(
                _atom_accepts(
                    atom,
                    first,
                )
                is False
                for atom in combined
            ):
                return True

        bounds = _range_bounds(combined)

        if bounds is None:
            continue

        lower, upper = bounds

        if lower is None or upper is None:
            continue

        pair = ordered_pair(
            lower[0],
            upper[0],
        )

        if pair is None:
            continue

        lower_value, upper_value = pair

        if lower_value > upper_value:
            return True

        if lower_value == upper_value and not (
            lower[1]
            and upper[1]
        ):
            return True

    return False


def _guards_disjoint(
    index: NodeIndex,
    left: Trigger,
    right: Trigger,
) -> bool:
    if left.guard is True or right.guard is True:
        return False

    left_atoms = _guard_atoms(
        index,
        left,
        left.guard,
    )
    right_atoms = _guard_atoms(
        index,
        right,
        right.guard,
    )

    if left_atoms is None or right_atoms is None:
        return False

    return _atoms_conflict(
        left_atoms,
        right_atoms,
    )


def validate_triggers(
    index: NodeIndex,
    triggers: list[Trigger],
) -> None:
    """Validate trigger targets, contracts, guards, and overlap."""
    by_key: dict[
        tuple[str, str],
        list[Trigger],
    ] = defaultdict(list)

    for trigger in triggers:
        process = index.require(
            trigger,
            trigger.process,
            Process,
        )

        for binding in trigger.seed:
            validate_value(
                index,
                trigger,
                binding.value,
            )

        if trigger.source is not None:
            interface = index.require(
                trigger,
                trigger.source,
                Interface,
            )

            if (
                interface is not None
                and interface.direction not in ("in", "inout")
            ):
                raise rule_error(
                    "trigger_source_not_ingress",
                    (
                        "trigger {trigger} source {interface} "
                        "is not an in or inout interface"
                    ),
                    {
                        "trigger": trigger.id,
                        "interface": trigger.source,
                    },
                )

        if process is not None:
            input_schema = process_schema(
                index,
                process,
                process.input,
            )

            if process.input is None or input_schema is not None:
                validate_trigger_contract(
                    trigger,
                    (
                        None
                        if input_schema is None
                        else input_schema.placeholders
                    ),
                )

        if trigger.guard is not True:
            validate_condition(
                index,
                trigger,
                trigger.guard,
            )

        if trigger.source is None:
            by_key[
                (
                    "event",
                    trigger.event,
                )
            ].append(trigger)

        else:
            by_key[
                (
                    "source",
                    trigger.source,
                )
            ].append(trigger)

    for (kind, key), group in by_key.items():
        for left, right in combinations(group, 2):
            if not _guards_disjoint(
                index,
                left,
                right,
            ):
                raise PydanticCustomError(
                    "overlapping_trigger_guards",
                    (
                        "triggers {left} and {right} share {kind} {key} "
                        "without provably disjoint guards"
                    ),
                    {
                        "left": left.id,
                        "right": right.id,
                        "kind": kind,
                        "key": key,
                    },
                )


__all__ = [
    "validate_trigger_contract",
    "validate_triggers",
]
