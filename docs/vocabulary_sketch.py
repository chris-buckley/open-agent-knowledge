"""Reference sketch of the OAK vocabulary as Pydantic v2 models.

This file supports docs/PRD.md. It is a reference, not the implementation.
"""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Id = Annotated[str, Field(min_length=1, pattern=r"^[a-z][a-z0-9./-]*$")]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Ref(Strict):
    ref: Id  # points at any node id


class BaseNode(Strict):
    id: Id  # stable identity, survives moving
    title: str | None = None


class Instruction(BaseNode):
    type: Literal["instruction"]
    body: str  # rule the interpreter must follow


class Constant(BaseNode):
    type: Literal["constant"]
    value: str | int | float | bool  # same in every use


class Schema(BaseNode):
    type: Literal["schema"]
    body: dict  # schema, template, or format


class Trigger(BaseNode):
    type: Literal["trigger"]
    when: str  # why the interpreter looks at this


class State(BaseNode):
    type: Literal["state"]
    value: str | int | float | bool | None = None


class Process(BaseNode):
    type: Literal["process"]
    steps: list[str]  # exact way to do the task
    uses: list[Ref] = []  # constants and schemas it draws on


class Input(BaseNode):
    type: Literal["input"]
    contract: Ref  # expected shape, defined beforehand


Node = Annotated[
    Instruction | Constant | Schema | Trigger | State | Process | Input,
    Field(discriminator="type"),
]


class Knowledge(Strict):
    """The composite: a directory in the knowledge tree."""

    id: Id
    interpretation: list[Ref] = []  # instructions the interpreter reads first
    children: list["Node | Knowledge"] = []


Knowledge.model_rebuild()
