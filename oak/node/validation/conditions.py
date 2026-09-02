"""Static condition evaluation and ordered-operand validation."""

from pydantic_core import PydanticCustomError

from oak.node.index import NodeIndex
from oak.node.parts.entry import Entry
from oak.node.parts.processes.conditions import (
    All,
    Any,
    Compare,
    Condition,
    Not,
    condition_values,
)
from oak.node.parts.processes.operators import (
    ConditionOperator,
    OrderedComparisonTypeError,
    compare_values,
    ordered_pair,
)
from oak.node.parts.processes.values import (
    BindingValue,
    ConstantValue,
    InterfaceValue,
    StateValue,
    Value,
)
from oak.node.validation.values import (
    STATIC_MISSING,
    static_value,
    validate_value,
)


def _same_dynamic_value(
    left: Value,
    right: Value,
) -> bool:
    return (
        type(left) is type(right)
        and isinstance(
            left,
            (
                ConstantValue,
                StateValue,
                InterfaceValue,
                BindingValue,
            ),
        )
        and left == right
    )


def compare_static(
    operator: ConditionOperator,
    left: object,
    right: object,
) -> bool:
    """Evaluate one statically known comparison with stable diagnostics."""
    try:
        return compare_values(
            operator,
            left,
            right,
        )

    except OrderedComparisonTypeError as error:
        raise PydanticCustomError(
            "ordered_comparison_type_mismatch",
            str(error),
        ) from None


def _static_compare(index: NodeIndex, source: Entry, condition: Compare) -> bool | None:
    if _same_dynamic_value(condition.left, condition.right):
        if condition.operator == "equals":
            return True

        if condition.operator == "not_equals":
            return False

        return None

    left = static_value(index, source, condition.left)
    right = static_value(index, source, condition.right)

    if left is STATIC_MISSING or right is STATIC_MISSING:
        return None

    return compare_static(condition.operator, left, right)


def _static_all(index: NodeIndex, source: Entry, condition: All) -> bool | None:
    unknown = False

    for child in condition.conditions:
        decision = condition_result(index, source, child)

        if decision is False:
            return False

        if decision is None:
            unknown = True

    return None if unknown else True


def _static_any(index: NodeIndex, source: Entry, condition: Any) -> bool | None:
    unknown = False

    for child in condition.conditions:
        decision = condition_result(index, source, child)

        if decision is True:
            return True

        if decision is None:
            unknown = True

    return None if unknown else False


def condition_result(
    index: NodeIndex,
    source: Entry,
    condition: Condition,
) -> bool | None:
    """Return one statically known condition result when possible."""
    match condition:
        case Compare():
            return _static_compare(index, source, condition)

        case All():
            return _static_all(index, source, condition)

        case Any():
            return _static_any(index, source, condition)

        case Not():
            decision = condition_result(index, source, condition.condition)
            return None if decision is None else not decision

    raise TypeError(f"unsupported condition {type(condition).__name__}")


def validate_condition(
    index: NodeIndex,
    source: Entry,
    condition: Condition,
) -> None:
    """Validate every value and ordered comparison in one condition."""
    for value in condition_values(condition):
        validate_value(
            index,
            source,
            value,
        )

    if not isinstance(condition, Compare):
        return

    left = static_value(
        index,
        source,
        condition.left,
    )
    right = static_value(
        index,
        source,
        condition.right,
    )

    if (
        condition.operator not in ("equals", "not_equals")
        and left is not STATIC_MISSING
        and right is not STATIC_MISSING
        and ordered_pair(left, right) is None
    ):
        raise PydanticCustomError(
            "ordered_comparison_type_mismatch",
            "ordered comparison needs two numbers or two strings",
        )


__all__ = [
    "compare_static",
    "condition_result",
    "validate_condition",
]
