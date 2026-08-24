"""Transactional trigger selection and process execution."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from typing import TypeVar

from pydantic import (
    ConfigDict,
    Field,
    JsonValue,
    TypeAdapter,
    ValidationError,
)

from oak.base import Entry, OakModel
from oak.node.graph import iter_entries, iter_nodes
from oak.node.model import Node, Root
from oak.node.parts import (
    Act,
    BindingValue,
    Call,
    Condition,
    Constant,
    ConstantValue,
    Emit,
    Fail,
    If,
    Interface,
    InterfaceValue,
    LiteralValue,
    Process,
    Schema,
    SchemaBindingError,
    Set,
    State,
    StateValue,
    Step,
    Trigger,
    Value,
)
from oak.vocabulary import (
    NonBlankLine,
    Placeholder,
    SlugId,
)

_STRICT = ConfigDict(
    strict=True,
    regex_engine="rust-regex",
)
_STATE_ADAPTER = TypeAdapter(
    dict[SlugId, JsonValue],
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

ActHandler = Callable[
    [Act, Mapping[str, JsonValue]],
    Mapping[str, JsonValue],
]

Target = TypeVar("Target")


class Arrival(OakModel):
    """One trigger arrival and its active input values."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "when": "A command line arrives.",
                    "interfaces": {
                        "stdin": {
                            "COMMAND": "pwd",
                        }
                    },
                }
            ]
        }
    )

    when: NonBlankLine = Field(
        description="The arrival reason matched against trigger text.",
        examples=["A command line arrives."],
    )
    interfaces: dict[
        SlugId,
        dict[Placeholder, JsonValue],
    ] = Field(
        default_factory=dict,
        description="The active input bindings by interface id.",
        examples=[
            {
                "stdin": {
                    "COMMAND": "pwd",
                }
            }
        ],
    )


class Emission(OakModel):
    """One validated interface emission."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "interface": "stdout",
                    "values": {
                        "OUTPUT": "/oak",
                    },
                }
            ]
        }
    )

    interface: SlugId = Field(
        description="The output interface id.",
        examples=["stdout"],
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
                    "process": "pwd",
                    "state": {
                        "mode": "open",
                    },
                    "emissions": [
                        {
                            "interface": "stdout",
                            "values": {
                                "OUTPUT": "/oak",
                            },
                        }
                    ],
                }
            ]
        }
    )

    process: SlugId | None = Field(
        default=None,
        description="The selected process, or null when none matched.",
        examples=["pwd"],
    )
    state: dict[SlugId, JsonValue] = Field(
        description="The state after successful completion.",
        examples=[
            {
                "mode": "open",
            }
        ],
    )
    emissions: list[Emission] = Field(
        default_factory=list,
        description="The emissions in execution order.",
        examples=[
            [
                {
                    "interface": "stdout",
                    "values": {
                        "OUTPUT": "/oak",
                    },
                }
            ]
        ],
    )


class ExecutionError(RuntimeError):
    """One runtime failure that discards the transaction."""

    def __init__(
        self,
        code: str,
        message: str,
    ) -> None:
        self.code = code
        self.message = message
        super().__init__(
            f"[{code}] {message}"
        )


def _registry(
    root: Root,
) -> dict[str, Node | Entry]:
    registry: dict[str, Node | Entry] = {}

    for node in iter_nodes(root):
        registry[node.id] = node
        for entry in iter_entries(node):
            registry[entry.id] = entry

    return registry


def _target(
    registry: dict[str, Node | Entry],
    identifier: str,
    expected: type[Target],
) -> Target:
    target = registry.get(identifier)

    if not isinstance(target, expected):
        raise ExecutionError(
            "invalid_runtime_target",
            (
                f"{identifier} is not a "
                f"{expected.__name__.lower()}"
            ),
        )

    return target


def _json_equal(
    left: object,
    right: object,
) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return (
            isinstance(left, bool)
            and isinstance(right, bool)
            and left == right
        )

    if isinstance(left, (int, float)) and isinstance(
        right,
        (int, float),
    ):
        return left == right

    if isinstance(left, list) and isinstance(right, list):
        return (
            len(left) == len(right)
            and all(
                _json_equal(
                    left_item,
                    right_item,
                )
                for left_item, right_item in zip(
                    left,
                    right,
                    strict=True,
                )
            )
        )

    if isinstance(left, dict) and isinstance(right, dict):
        return (
            left.keys() == right.keys()
            and all(
                _json_equal(
                    left[key],
                    right[key],
                )
                for key in left
            )
        )

    return (
        type(left) is type(right)
        and left == right
    )


def _schema_for(
    registry: dict[str, Node | Entry],
    interface: Interface,
) -> Schema:
    return _target(
        registry,
        interface.schema_id,
        Schema,
    )


def _resolve(
    registry: dict[str, Node | Entry],
    value: Value,
    state: dict[str, JsonValue],
    interfaces: dict[
        str,
        dict[str, JsonValue],
    ],
    bindings: dict[str, JsonValue],
) -> JsonValue:
    if isinstance(value, LiteralValue):
        return deepcopy(value.value)

    if isinstance(value, ConstantValue):
        constant = _target(
            registry,
            value.constant,
            Constant,
        )
        return deepcopy(constant.value)

    if isinstance(value, StateValue):
        if value.state not in state:
            raise ExecutionError(
                "missing_state_value",
                f"state {value.state} is absent",
            )
        return deepcopy(
            state[value.state]
        )

    if isinstance(value, InterfaceValue):
        interface_values = interfaces.get(
            value.interface
        )

        if (
            interface_values is None
            or value.placeholder not in interface_values
        ):
            raise ExecutionError(
                "missing_interface_value",
                (
                    f"interface {value.interface} "
                    f"has no {value.placeholder} value"
                ),
            )

        return deepcopy(
            interface_values[value.placeholder]
        )

    if isinstance(value, BindingValue):
        if value.binding not in bindings:
            raise ExecutionError(
                "missing_process_binding",
                f"binding {value.binding} is absent",
            )

        return deepcopy(
            bindings[value.binding]
        )

    raise TypeError(
        f"unsupported process value {type(value).__name__}"
    )


def _condition(
    registry: dict[str, Node | Entry],
    condition: Condition,
    state: dict[str, JsonValue],
    interfaces: dict[
        str,
        dict[str, JsonValue],
    ],
    bindings: dict[str, JsonValue],
) -> bool:
    equal = _json_equal(
        _resolve(
            registry,
            condition.left,
            state,
            interfaces,
            bindings,
        ),
        _resolve(
            registry,
            condition.right,
            state,
            interfaces,
            bindings,
        ),
    )

    return (
        equal
        if condition.operator == "equals"
        else not equal
    )


def _validate_arrival(
    registry: dict[str, Node | Entry],
    arrival: Arrival,
) -> dict[str, dict[str, JsonValue]]:
    active: dict[
        str,
        dict[str, JsonValue],
    ] = {}

    for identifier, values in arrival.interfaces.items():
        interface = _target(
            registry,
            identifier,
            Interface,
        )

        if interface.direction not in ("in", "inout"):
            raise ExecutionError(
                "interface_direction_mismatch",
                (
                    f"interface {identifier} "
                    "cannot receive input"
                ),
            )

        schema = _schema_for(
            registry,
            interface,
        )

        try:
            schema.bind(values)
        except SchemaBindingError as error:
            raise ExecutionError(
                "invalid_interface_binding",
                f"interface {identifier}: {error}",
            ) from None

        active[identifier] = deepcopy(values)

    return active


def _run_steps(
    registry: dict[str, Node | Entry],
    steps: list[Step],
    state: dict[str, JsonValue],
    interfaces: dict[
        str,
        dict[str, JsonValue],
    ],
    emissions: list[Emission],
    bindings: dict[str, JsonValue],
    handler: ActHandler | None,
) -> None:
    for step in steps:
        if isinstance(step, Act):
            if handler is None:
                raise ExecutionError(
                    "act_handler_missing",
                    "an act step needs an act handler",
                )

            inputs = {
                binding.placeholder: _resolve(
                    registry,
                    binding.value,
                    state,
                    interfaces,
                    bindings,
                )
                for binding in step.inputs
            }

            try:
                authored = handler(
                    step,
                    inputs,
                )
                outputs = (
                    _BINDING_ADAPTER.validate_python(
                        dict(authored)
                    )
                )
            except ExecutionError:
                raise
            except Exception as error:
                raise ExecutionError(
                    "act_failed",
                    str(error),
                ) from None

            expected = set(step.outputs)
            supplied = set(outputs)

            if supplied != expected:
                missing = (
                    ", ".join(
                        sorted(expected - supplied)
                    )
                    or "none"
                )
                unused = (
                    ", ".join(
                        sorted(supplied - expected)
                    )
                    or "none"
                )

                raise ExecutionError(
                    "act_output_mismatch",
                    (
                        "act outputs differ; "
                        f"missing: {missing}; "
                        f"unused: {unused}"
                    ),
                )

            bindings.update(
                deepcopy(outputs)
            )

        elif isinstance(step, Set):
            value = _resolve(
                registry,
                step.value,
                state,
                interfaces,
                bindings,
            )
            state[step.state] = (
                _JSON_ADAPTER.validate_python(
                    value
                )
            )

        elif isinstance(step, Emit):
            interface = _target(
                registry,
                step.interface,
                Interface,
            )
            schema = _schema_for(
                registry,
                interface,
            )

            values = {
                binding.placeholder: _resolve(
                    registry,
                    binding.value,
                    state,
                    interfaces,
                    bindings,
                )
                for binding in step.bindings
            }

            try:
                schema.bind(values)
            except SchemaBindingError as error:
                raise ExecutionError(
                    "invalid_emission",
                    (
                        f"interface {step.interface}: "
                        f"{error}"
                    ),
                ) from None

            emissions.append(
                Emission(
                    interface=step.interface,
                    values=deepcopy(values),
                )
            )

        elif isinstance(step, If):
            selected = (
                step.then
                if _condition(
                    registry,
                    step.condition,
                    state,
                    interfaces,
                    bindings,
                )
                else step.otherwise
            )

            if selected is not None:
                _run_steps(
                    registry,
                    selected,
                    state,
                    interfaces,
                    emissions,
                    dict(bindings),
                    handler,
                )

        elif isinstance(step, Call):
            process = _target(
                registry,
                step.process,
                Process,
            )
            _run_steps(
                registry,
                process.steps,
                state,
                interfaces,
                emissions,
                {},
                handler,
            )

        elif isinstance(step, Fail):
            raise ExecutionError(
                "process_failed",
                step.message,
            )

        else:
            raise TypeError(
                (
                    "unsupported process step "
                    f"{type(step).__name__}"
                )
            )


def execute(
    root: Root,
    arrival: Arrival,
    state: Mapping[str, JsonValue],
    *,
    act: ActHandler | None = None,
) -> ExecutionResult:
    """Run one arrival cycle and return committed effects."""
    registry = _registry(root)

    authored_state = {
        entry.id
        for entry in registry.values()
        if isinstance(entry, State)
    }

    try:
        working_state = (
            _STATE_ADAPTER.validate_python(
                dict(state)
            )
        )
    except ValidationError as error:
        raise ExecutionError(
            "invalid_execution_state",
            str(error),
        ) from None

    supplied_state = set(working_state)
    if supplied_state != authored_state:
        missing = (
            ", ".join(
                sorted(
                    authored_state - supplied_state
                )
            )
            or "none"
        )
        unknown = (
            ", ".join(
                sorted(
                    supplied_state - authored_state
                )
            )
            or "none"
        )

        raise ExecutionError(
            "execution_state_mismatch",
            (
                "state differs; "
                f"missing: {missing}; "
                f"unknown: {unknown}"
            ),
        )

    active_interfaces = _validate_arrival(
        registry,
        arrival,
    )
    matches: list[Trigger] = []

    for node in iter_nodes(root):
        for trigger in node.triggers:
            if trigger.when != arrival.when:
                continue

            if (
                trigger.given is None
                or _condition(
                    registry,
                    trigger.given,
                    working_state,
                    active_interfaces,
                    {},
                )
            ):
                matches.append(trigger)

    if len(matches) > 1:
        identifiers = ", ".join(
            trigger.id
            for trigger in matches
        )
        raise ExecutionError(
            "ambiguous_trigger_match",
            (
                "arrival matches triggers "
                f"{identifiers}"
            ),
        )

    if not matches:
        return ExecutionResult(
            state=working_state,
        )

    process = _target(
        registry,
        matches[0].process,
        Process,
    )
    emissions: list[Emission] = []

    _run_steps(
        registry,
        process.steps,
        working_state,
        active_interfaces,
        emissions,
        {},
        act,
    )

    return ExecutionResult(
        process=process.id,
        state=working_state,
        emissions=emissions,
    )
