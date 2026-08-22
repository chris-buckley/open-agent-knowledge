"""Reference sketch of the OAK vocabulary as Pydantic v2 models.

This file supports docs/PRD.md. It is a reference, not the implementation.
"""
from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

Id = Annotated[
    str,
    Field(min_length=1, pattern=r"^[A-Za-z][A-Za-z0-9+.-]*:[^\s]+$"),
]  # absolute IRI shape, independent of file placement
Text = Annotated[str, Field(min_length=1)]


class Strict(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_default=True,
        allow_inf_nan=False,
    )


class Ref(Strict):
    ref: Id


class BaseNode(Strict):
    id: Id


class Instruction(BaseNode):
    type: Literal["instruction"]
    body: Text  # rule the interpreter must follow


class Constant(BaseNode):
    type: Literal["constant"]
    value: JsonValue  # same in every use


class Schema(BaseNode):
    type: Literal["schema"]
    body: dict[str, JsonValue]  # schema, template, or format


class Trigger(BaseNode):
    type: Literal["trigger"]
    when: Text  # why the interpreter enters
    then: Ref | None = None  # process to follow when matched


class State(BaseNode):
    type: Literal["state"]
    value: JsonValue = None


class Process(BaseNode):
    type: Literal["process"]
    steps: list[Text] = Field(min_length=1)  # order is meaningful
    uses: list[Ref] = Field(default_factory=list)


class Input(BaseNode):
    type: Literal["input"]
    contract: Ref  # must reference a schema


Node = Annotated[
    Instruction | Constant | Schema | Trigger | State | Process | Input,
    Field(discriminator="type"),
]


class Composition(Strict):
    """Nested structure. Containment comes from children, not from links."""

    id: Id
    interpretation: list[Ref] = Field(default_factory=list)  # instructions read first
    children: list[Node | Composition] = Field(default_factory=list)


class Knowledge(Composition):
    """The authored root. Derives the flat registry and runs the graph checks."""

    @model_validator(mode="after")
    def validate_graph(self) -> Knowledge:
        ids: set[str] = set()
        nodes: dict[str, BaseNode] = {}
        compositions: list[Composition] = []
        stack: list[Composition | BaseNode] = [self]
        while stack:
            item = stack.pop()
            if item.id in ids:
                raise ValueError(f"duplicate id: {item.id}")
            ids.add(item.id)
            if isinstance(item, Composition):
                compositions.append(item)
                stack.extend(item.children)
            else:
                nodes[item.id] = item

        def require(ref: Ref, expected: tuple[type[BaseNode], ...], source: str) -> None:
            target = nodes.get(ref.ref)
            if target is None:
                raise ValueError(f"{source} references missing node: {ref.ref}")
            if not isinstance(target, expected):
                names = " or ".join(model.__name__ for model in expected)
                raise ValueError(f"{source} must reference {names}: {ref.ref}")

        for composition in compositions:
            for ref in composition.interpretation:
                require(ref, (Instruction,), f"{composition.id}.interpretation")
        for node in nodes.values():
            if isinstance(node, Trigger) and node.then is not None:
                require(node.then, (Process,), f"{node.id}.then")
            elif isinstance(node, Process):
                for ref in node.uses:
                    require(ref, (Constant, Schema), f"{node.id}.uses")
            elif isinstance(node, Input):
                require(node.contract, (Schema,), f"{node.id}.contract")
        return self


Composition.model_rebuild()
Knowledge.model_rebuild()
