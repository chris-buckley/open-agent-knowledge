"""The closed set of OAK entry parts."""

from typing import Annotated

from pydantic import Field

from oak.node.parts.constants import Constant, ConstantForm
from oak.node.parts.instructions import Instruction
from oak.node.parts.interfaces import Direction, Interface
from oak.node.parts.processes import (
    Act,
    BindingValue,
    Call,
    Condition,
    ConditionOperator,
    ConstantValue,
    Emit,
    Fail,
    If,
    InterfaceValue,
    LiteralValue,
    Process,
    Set,
    StateValue,
    Step,
    Value,
    ValueBinding,
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
    Instruction | Constant | Schema | State | Trigger | Process | Interface,
    Field(discriminator="part"),
]

__all__ = [
    "Act",
    "AtLeast",
    "AtMost",
    "BindingFailure",
    "BindingValue",
    "Call",
    "Condition",
    "ConditionOperator",
    "Constant",
    "ConstantForm",
    "ConstantValue",
    "Constraint",
    "Direction",
    "Emit",
    "Fail",
    "If",
    "Instruction",
    "Interface",
    "InterfaceValue",
    "Lines",
    "ListOf",
    "LiteralValue",
    "MaxChars",
    "NonEmpty",
    "OneOf",
    "Part",
    "Process",
    "Regex",
    "Schema",
    "SchemaBindingError",
    "Set",
    "State",
    "StateValue",
    "Step",
    "Trigger",
    "Type",
    "Value",
    "ValueBinding",
    "Where",
    "where",
]
