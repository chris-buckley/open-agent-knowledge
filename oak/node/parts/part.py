"""The closed discriminated union of the seven OAK parts."""

from typing import Annotated

from pydantic import Field

from oak.node.parts.constants import Constant
from oak.node.parts.instructions import Instruction
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes.model import Process
from oak.node.parts.schemas.model import Schema
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
