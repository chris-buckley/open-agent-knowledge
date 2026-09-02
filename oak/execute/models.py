"""Public models, handlers, and adapters for one execution cycle."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Annotated, Self

from pydantic import (
    AfterValidator,
    ConfigDict,
    Field,
    JsonValue,
    TypeAdapter,
    model_validator,
)
from pydantic_core import PydanticCustomError

from oak.base import OakModel
from oak.node.parts.processes.steps import Act
from oak.vocabulary import NonBlankLine, Placeholder, TargetPath
from oak.vocabulary.text.target_path import typed_target

_STRICT = ConfigDict(
    strict=True,
    regex_engine="rust-regex",
)
_STATE_ADAPTER = TypeAdapter(
    dict[TargetPath, JsonValue],
    config=_STRICT,
)
_BINDING_ADAPTER = TypeAdapter(
    dict[Placeholder, JsonValue],
    config=_STRICT,
)
_JSON_ADAPTER = TypeAdapter(
    JsonValue,
    config=_STRICT,
)
InterfaceArrivalTarget = Annotated[
    TargetPath,
    AfterValidator(
        lambda value: typed_target(
            value,
            "interface",
        )
    ),
]

ActHandler = Callable[
    [
        Act,
        Mapping[str, JsonValue],
    ],
    Mapping[str, JsonValue],
]
ToolHandler = Callable[
    [
        Act,
        Mapping[str, JsonValue],
    ],
    Mapping[str, JsonValue],
]


@dataclass(frozen=True, slots=True)
class ToolContract:
    """One exact host tool contract and handler."""

    handler: ToolHandler
    inputs: frozenset[str]
    outputs: frozenset[str]
    parallel: bool = False
    input: str | None = None
    output: str | None = None


class Arrival(OakModel):
    """One outside occurrence: an event text or one ingress interface arrival."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "event": "A command line arrives.",
                    "interfaces": {
                        "interface.stdin": {
                            "COMMAND": "pwd",
                        }
                    },
                },
                {
                    "source": "interface.stdin",
                    "interfaces": {
                        "interface.stdin": {
                            "COMMAND": "pwd",
                        }
                    },
                },
            ]
        }
    )

    event: NonBlankLine | None = Field(
        default=None,
        description="The event text matched exactly against source-less triggers.",
        examples=["A command line arrives."],
    )
    source: InterfaceArrivalTarget | None = Field(
        default=None,
        description="The ingress interface matched exactly against source-backed triggers.",
        examples=["interface.stdin"],
    )
    interfaces: dict[
        InterfaceArrivalTarget,
        dict[Placeholder, JsonValue],
    ] = Field(
        default_factory=dict,
        description="The active input bindings by root-relative interface target.",
        examples=[
            {
                "interface.stdin": {
                    "COMMAND": "pwd",
                }
            }
        ],
    )

    @model_validator(mode="after")
    def one_selector(self) -> Self:
        if (self.event is None) == (self.source is None):
            raise PydanticCustomError(
                "invalid_arrival_selector",
                "an arrival needs exactly one of event or source",
            )
        return self


class Emission(OakModel):
    """One validated interface emission."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "interface": "interface.stdout",
                    "values": {
                        "OUTPUT": "/oak",
                    },
                }
            ]
        }
    )

    interface: InterfaceArrivalTarget = Field(
        description="The root-relative output interface target.",
        examples=["interface.stdout"],
    )
    values: dict[Placeholder, JsonValue] = Field(
        description="The validated schema bindings.",
        examples=[
            {
                "OUTPUT": "/oak",
            }
        ],
    )


class ExecutionResult(OakModel):
    """The committed result of one arrival cycle."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "process": "process.pwd",
                    "state": {
                        "state.mode": "open",
                    },
                    "emissions": [
                        {
                            "interface": "interface.stdout",
                            "values": {
                                "OUTPUT": "/oak",
                            },
                        }
                    ],
                }
            ]
        }
    )

    process: TargetPath | None = Field(
        default=None,
        description="The selected root-relative process target, or null.",
        examples=["process.pwd"],
    )
    state: dict[TargetPath, JsonValue] = Field(
        description="The committed state by root-relative target.",
        examples=[
            {
                "state.mode": "open",
            }
        ],
    )
    emissions: list[Emission] = Field(
        default_factory=list,
        description="The committed emissions in execution order.",
        examples=[
            [
                {
                    "interface": "interface.stdout",
                    "values": {
                        "OUTPUT": "/oak",
                    },
                }
            ]
        ],
    )


class ExecutionError(RuntimeError):
    """One runtime failure that discards staged OAK effects."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        suppressed: tuple[str, ...] = (),
    ) -> None:
        self.code = code
        self.message = message
        self.suppressed = suppressed
        suffix = (
            ""
            if not suppressed
            else "; suppressed: "
            + " | ".join(suppressed)
        )
        super().__init__(
            f"[{code}] {message}{suffix}"
        )


__all__ = [
    "ActHandler",
    "Arrival",
    "Emission",
    "ExecutionError",
    "ExecutionResult",
    "InterfaceArrivalTarget",
    "ToolContract",
    "ToolHandler",
]
