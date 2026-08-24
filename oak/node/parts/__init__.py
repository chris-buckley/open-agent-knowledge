"""The closed set of OAK entry parts."""

from typing import Annotated

from pydantic import Field

from oak.node.parts.constants import Constant
from oak.node.parts.instructions import Instruction
from oak.node.parts.interfaces import Direction, Interface
from oak.node.parts.processes import Process
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
    "AtLeast",
    "AtMost",
    "BindingFailure",
    "Constant",
    "Constraint",
    "Direction",
    "Instruction",
    "Interface",
    "Lines",
    "ListOf",
    "MaxChars",
    "NonEmpty",
    "OneOf",
    "Part",
    "Process",
    "Regex",
    "Schema",
    "SchemaBindingError",
    "State",
    "Trigger",
    "Type",
    "Where",
    "where",
]
