"""The closed set of OAK entry parts."""

from typing import Annotated

from pydantic import Field

from oak.node.parts.constants import Constant, ConstantForm
from oak.node.parts.instructions import Instruction
from oak.node.parts.interfaces import Direction, Interface, SchemaTarget
from oak.node.parts.processes import (
    Act,
    All,
    Any,
    Assert,
    BindingValue,
    Call,
    Compare,
    Condition,
    ConditionOperator,
    ConstantTarget,
    ConstantValue,
    Emit,
    Fail,
    Foreach,
    If,
    InterfaceTarget,
    InterfaceValue,
    Join,
    LiteralValue,
    Not,
    Par,
    Process,
    ProcessTarget,
    Set,
    StateTarget,
    StateValue,
    Step,
    Value,
    ValueBinding,
    While,
    condition_values,
    step_values,
)
from oak.node.parts.schemas import (
    AtLeast,
    AtMost,
    BindingFailure,
    Constraint,
    Lines,
    ListOf,
    MaxChars,
    NonEmpty,
    OneOf,
    Regex,
    Schema,
    SchemaBindingError,
    Type,
    Where,
    where,
)
from oak.node.parts.state import State
from oak.node.parts.triggers import Trigger

Part = Annotated[
    Instruction
    | Constant
    | Schema
    | State
    | Trigger
    | Process
    | Interface,
    Field(discriminator="part"),
]

__all__ = [
    "Act",
    "All",
    "Any",
    "Assert",
    "AtLeast",
    "AtMost",
    "BindingFailure",
    "BindingValue",
    "Call",
    "Compare",
    "Condition",
    "ConditionOperator",
    "Constant",
    "ConstantForm",
    "ConstantTarget",
    "ConstantValue",
    "Constraint",
    "Direction",
    "Emit",
    "Fail",
    "Foreach",
    "If",
    "Instruction",
    "Interface",
    "InterfaceTarget",
    "InterfaceValue",
    "Join",
    "Lines",
    "ListOf",
    "LiteralValue",
    "MaxChars",
    "NonEmpty",
    "Not",
    "OneOf",
    "Par",
    "Part",
    "Process",
    "ProcessTarget",
    "Regex",
    "Schema",
    "SchemaBindingError",
    "SchemaTarget",
    "Set",
    "State",
    "StateTarget",
    "StateValue",
    "Step",
    "Trigger",
    "Type",
    "Value",
    "ValueBinding",
    "Where",
    "While",
    "condition_values",
    "step_values",
    "where",
]
