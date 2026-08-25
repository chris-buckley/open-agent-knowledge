"""The processes part: values, recursive conditions, and ordered steps."""

from __future__ import annotations

from collections import Counter
from typing import Annotated, Literal, Self

from pydantic import AfterValidator, ConfigDict, Field, JsonValue, model_validator
from pydantic_core import PydanticCustomError

from oak.base import DiscriminatedModel, Entry, OakModel
from oak.vocabulary import NonBlankLine, Placeholder, ProcessName, TargetPath
from oak.vocabulary.text.placeholder import placeholders_in
from oak.vocabulary.text.target_path import local_target, typed_target

ConstantTarget = Annotated[TargetPath, AfterValidator(lambda value: typed_target(value, "constant"))]
StateTarget = Annotated[TargetPath, AfterValidator(lambda value: local_target(value, "state"))]
InterfaceTarget = Annotated[TargetPath, AfterValidator(lambda value: local_target(value, "interface"))]
ProcessTarget = Annotated[TargetPath, AfterValidator(lambda value: typed_target(value, "process"))]


class ValueModel(DiscriminatedModel):
    """One tagged source for a process value."""
    discriminator_field = "source"


class LiteralValue(ValueModel):
    """One authored JSON value."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"source": "literal", "value": "critical"}]})
    source: Literal["literal"] = Field(default="literal", description="The process value source discriminator.", examples=["literal"])
    value: JsonValue = Field(description="The authored JSON value.", examples=["critical", 3, {"ready": True}])


class ConstantValue(ValueModel):
    """One value read from a local or relative constant entry."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"source": "constant", "constant": "constant.policy"}]})
    source: Literal["constant"] = Field(default="constant", description="The process value source discriminator.", examples=["constant"])
    constant: ConstantTarget = Field(description="The local or relative constant target to read.", examples=["constant.policy"])


class StateValue(ValueModel):
    """One value read from local state."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"source": "state", "state": "state.status"}]})
    source: Literal["state"] = Field(default="state", description="The process value source discriminator.", examples=["state"])
    state: StateTarget = Field(description="The local state target to read.", examples=["state.status"])


class InterfaceValue(ValueModel):
    """One placeholder value read from one active local input interface."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"source": "interface", "interface": "interface.request", "placeholder": "REQUEST"}]})
    source: Literal["interface"] = Field(default="interface", description="The process value source discriminator.", examples=["interface"])
    interface: InterfaceTarget = Field(description="The active local input interface target to read.", examples=["interface.request"])
    placeholder: Placeholder = Field(description="The interface schema placeholder to read.", examples=["REQUEST"])


class BindingValue(ValueModel):
    """One value read from a visible process-local binding."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"source": "binding", "binding": "RESULT"}]})
    source: Literal["binding"] = Field(default="binding", description="The process value source discriminator.", examples=["binding"])
    binding: Placeholder = Field(description="The visible process-local binding to read.", examples=["RESULT"])


Value = Annotated[LiteralValue | ConstantValue | StateValue | InterfaceValue | BindingValue, Field(discriminator="source")]


class ValueBinding(OakModel):
    """One placeholder bound to one process value."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"placeholder": "REQUEST", "value": {"source": "interface", "interface": "interface.request", "placeholder": "REQUEST"}}]})
    placeholder: Placeholder = Field(description="The placeholder receiving the process value.", examples=["REQUEST"])
    value: Value = Field(description="The process value bound to the placeholder.", examples=[{"source": "literal", "value": "ready"}])


ConditionOperator = Literal["equals", "not_equals", "less_than", "less_than_or_equal", "greater_than", "greater_than_or_equal"]


class ConditionModel(DiscriminatedModel):
    """One tagged recursive condition."""
    discriminator_field = "kind"


class Compare(ConditionModel):
    """One strict structural or ordered comparison."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"kind": "compare", "left": {"source": "state", "state": "state.status"}, "operator": "equals", "right": {"source": "literal", "value": "ready"}}]})
    kind: Literal["compare"] = Field(default="compare", description="The condition discriminator.", examples=["compare"])
    left: Value = Field(description="The value on the left of the comparison.", examples=[{"source": "state", "state": "state.status"}])
    operator: ConditionOperator = Field(description="The strict comparison operator.", examples=["equals", "greater_than"])
    right: Value = Field(description="The value on the right of the comparison.", examples=[{"source": "literal", "value": "ready"}])


class All(ConditionModel):
    """Every child condition must be true in authored order."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"kind": "all", "conditions": [{"kind": "compare", "left": {"source": "state", "state": "state.status"}, "operator": "equals", "right": {"source": "literal", "value": "ready"}}, {"kind": "compare", "left": {"source": "state", "state": "state.count"}, "operator": "greater_than", "right": {"source": "literal", "value": 0}}]}]})
    kind: Literal["all"] = Field(default="all", description="The condition discriminator.", examples=["all"])
    conditions: list[Condition] = Field(description="The child conditions in authored order.", examples=[[]])
    @model_validator(mode="after")
    def length(self) -> Self:
        if len(self.conditions) < 2:
            raise PydanticCustomError("condition_group_too_short", "ALL needs at least two conditions")
        return self


class Any(ConditionModel):
    """At least one child condition must be true in authored order."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"kind": "any", "conditions": [{"kind": "compare", "left": {"source": "state", "state": "state.status"}, "operator": "equals", "right": {"source": "literal", "value": "ready"}}, {"kind": "compare", "left": {"source": "state", "state": "state.override"}, "operator": "equals", "right": {"source": "literal", "value": True}}]}]})
    kind: Literal["any"] = Field(default="any", description="The condition discriminator.", examples=["any"])
    conditions: list[Condition] = Field(description="The child conditions in authored order.", examples=[[]])
    @model_validator(mode="after")
    def length(self) -> Self:
        if len(self.conditions) < 2:
            raise PydanticCustomError("condition_group_too_short", "ANY needs at least two conditions")
        return self


class Not(ConditionModel):
    """One child condition whose result is inverted."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"kind": "not", "condition": {"kind": "compare", "left": {"source": "state", "state": "state.status"}, "operator": "equals", "right": {"source": "literal", "value": "closed"}}}]})
    kind: Literal["not"] = Field(default="not", description="The condition discriminator.", examples=["not"])
    condition: Condition = Field(description="The child condition to invert.", examples=[{"kind": "compare", "left": {"source": "state", "state": "state.status"}, "operator": "equals", "right": {"source": "literal", "value": "closed"}}])


Condition = Annotated[Compare | All | Any | Not, Field(discriminator="kind")]
All.model_rebuild(_types_namespace={"Condition": Condition})
Any.model_rebuild(_types_namespace={"Condition": Condition})
Not.model_rebuild(_types_namespace={"Condition": Condition})


class StepModel(DiscriminatedModel):
    """One tagged process step."""
    discriminator_field = "kind"


class Act(StepModel):
    """One interpreter-native or exact named-tool action."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"kind": "act", "instruction": "Turn <REQUEST> into <RESULT>.", "inputs": [{"placeholder": "REQUEST", "value": {"source": "interface", "interface": "interface.request", "placeholder": "REQUEST"}}], "outputs": ["RESULT"]}, {"kind": "act", "tool": "mcp__docs__search", "instruction": "Find <QUERY> and return <RESULT>.", "inputs": [{"placeholder": "QUERY", "value": {"source": "literal", "value": "OAK"}}], "outputs": ["RESULT"]}]})
    kind: Literal["act"] = Field(default="act", description="The process step discriminator.", examples=["act"])
    tool: NonBlankLine | None = Field(default=None, description="The exact host tool name, or null for interpreter-native work.", examples=["mcp__docs__search"])
    instruction: NonBlankLine = Field(description="The action the interpreter or exact tool performs.", examples=["Turn <REQUEST> into <RESULT>."])
    inputs: list[ValueBinding] = Field(default_factory=list, description="The action input bindings in authored order.", examples=[[{"placeholder": "REQUEST", "value": {"source": "interface", "interface": "interface.request", "placeholder": "REQUEST"}}]])
    outputs: list[Placeholder] = Field(default_factory=list, description="The immutable local bindings the action must produce.", examples=[["RESULT"]])
    @model_validator(mode="after")
    def placeholders(self) -> Self:
        input_names = [item.placeholder for item in self.inputs]
        output_names = list(self.outputs)
        duplicate_inputs = sorted(name for name, count in Counter(input_names).items() if count > 1)
        duplicate_outputs = sorted(name for name, count in Counter(output_names).items() if count > 1)
        if duplicate_inputs:
            raise PydanticCustomError("duplicate_act_input", "act repeats input placeholders: {placeholders}", {"placeholders": ", ".join(duplicate_inputs)})
        if duplicate_outputs:
            raise PydanticCustomError("duplicate_act_output", "act repeats output placeholders: {placeholders}", {"placeholders": ", ".join(duplicate_outputs)})
        overlap = sorted(set(input_names) & set(output_names))
        if overlap:
            raise PydanticCustomError("act_binding_overlap", "act uses placeholders as both inputs and outputs: {placeholders}", {"placeholders": ", ".join(overlap)})
        declared = set(input_names) | set(output_names)
        used = placeholders_in(self.instruction)
        missing = sorted(used - declared)
        unused = sorted(declared - used)
        if missing or unused:
            raise PydanticCustomError("act_placeholder_mismatch", "act instruction and bindings differ; missing: {missing}; unused: {unused}", {"missing": ", ".join(missing) or "none", "unused": ", ".join(unused) or "none"})
        return self


class Set(StepModel):
    """One local state write."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"kind": "set", "state": "state.status", "value": {"source": "literal", "value": "complete"}}]})
    kind: Literal["set"] = Field(default="set", description="The process step discriminator.", examples=["set"])
    state: StateTarget = Field(description="The local state target to write.", examples=["state.status"])
    value: Value = Field(description="The process value written to state.", examples=[{"source": "literal", "value": "complete"}])


class Emit(StepModel):
    """One schema instance emitted through one local output interface."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"kind": "emit", "interface": "interface.result", "bindings": [{"placeholder": "RESULT", "value": {"source": "binding", "binding": "RESULT"}}]}]})
    kind: Literal["emit"] = Field(default="emit", description="The process step discriminator.", examples=["emit"])
    interface: InterfaceTarget = Field(description="The local output interface target.", examples=["interface.result"])
    bindings: list[ValueBinding] = Field(min_length=1, description="One value binding for each interface schema placeholder.", examples=[[{"placeholder": "RESULT", "value": {"source": "binding", "binding": "RESULT"}}]])
    @model_validator(mode="after")
    def placeholders(self) -> Self:
        names = [item.placeholder for item in self.bindings]
        duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
        if duplicates:
            raise PydanticCustomError("duplicate_emit_placeholder", "emit repeats placeholders: {placeholders}", {"placeholders": ", ".join(duplicates)})
        return self


class If(StepModel):
    """One recursive condition with a then branch and optional else branch."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"kind": "if", "condition": {"kind": "compare", "left": {"source": "state", "state": "state.status"}, "operator": "equals", "right": {"source": "literal", "value": "ready"}}, "then": [{"kind": "set", "state": "state.status", "value": {"source": "literal", "value": "complete"}}], "otherwise": [{"kind": "fail", "message": "The state is not ready."}]}]})
    kind: Literal["if"] = Field(default="if", description="The process step discriminator.", examples=["if"])
    condition: Condition = Field(description="The recursive condition that selects the branch.", examples=[{"kind": "compare", "left": {"source": "state", "state": "state.status"}, "operator": "equals", "right": {"source": "literal", "value": "ready"}}])
    then: list[Step] = Field(min_length=1, description="The steps run when the condition is true.", examples=[[{"kind": "fail", "message": "Example failure."}]])
    otherwise: list[Step] | None = Field(default=None, min_length=1, description="The steps run when the condition is false.", examples=[[{"kind": "fail", "message": "Example failure."}]])


class Call(StepModel):
    """One synchronous local or relative process invocation."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"kind": "call", "process": "process.finalize"}, {"kind": "call", "process": "../shared/processes.oak.md#process.finalize"}]})
    kind: Literal["call"] = Field(default="call", description="The process step discriminator.", examples=["call"])
    process: ProcessTarget = Field(description="The local or relative process target to invoke.", examples=["process.finalize"])


class Fail(StepModel):
    """One explicit process failure."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"kind": "fail", "message": "The result is empty."}]})
    kind: Literal["fail"] = Field(default="fail", description="The process step discriminator.", examples=["fail"])
    message: NonBlankLine = Field(description="The failure message.", examples=["The result is empty."])


class Assert(StepModel):
    """One required condition that aborts the transaction when false."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"kind": "assert", "condition": {"kind": "compare", "left": {"source": "binding", "binding": "RESULT"}, "operator": "not_equals", "right": {"source": "literal", "value": ""}}, "message": "The result must not be empty."}]})
    kind: Literal["assert"] = Field(default="assert", description="The process step discriminator.", examples=["assert"])
    condition: Condition = Field(description="The required recursive condition.", examples=[{"kind": "compare", "left": {"source": "binding", "binding": "RESULT"}, "operator": "not_equals", "right": {"source": "literal", "value": ""}}])
    message: NonBlankLine | None = Field(default=None, description="The optional assertion failure message.", examples=["The result must not be empty."])


class Foreach(StepModel):
    """One deterministic sequential iteration over a JSON list."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"kind": "foreach", "binding": "ITEM", "value": {"source": "literal", "value": ["a", "b"]}, "steps": [{"kind": "act", "instruction": "Transform <ITEM> into <RESULT>.", "inputs": [{"placeholder": "ITEM", "value": {"source": "binding", "binding": "ITEM"}}], "outputs": ["RESULT"]}]}]})
    kind: Literal["foreach"] = Field(default="foreach", description="The process step discriminator.", examples=["foreach"])
    binding: Placeholder = Field(description="The immutable loop binding.", examples=["ITEM"])
    value: Value = Field(description="The process value that must resolve to a JSON list.", examples=[{"source": "literal", "value": ["a", "b"]}])
    steps: list[Step] = Field(min_length=1, description="The sequential iteration steps.", examples=[[{"kind": "fail", "message": "Example failure."}]])


class Par(StepModel):
    """One deterministic group of exact named-tool acts."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"kind": "par", "steps": [{"kind": "act", "tool": "tool-a", "instruction": "Produce <A>.", "outputs": ["A"]}, {"kind": "act", "tool": "tool-b", "instruction": "Produce <B>.", "outputs": ["B"]}]}]})
    kind: Literal["par"] = Field(default="par", description="The process step discriminator.", examples=["par"])
    steps: list[Step] = Field(min_length=1, description="The exact named-tool acts launched in authored order.", examples=[[{"kind": "act", "tool": "tool-a", "instruction": "Produce <A>.", "outputs": ["A"]}]])
    @model_validator(mode="after")
    def parallel_steps(self) -> Self:
        acts: list[Act] = []
        for step in self.steps:
            if not isinstance(step, Act) or step.tool is None:
                raise PydanticCustomError("parallel_step_not_tool_act", "PAR contains a step that is not an exact named-tool act")
            acts.append(step)
        outputs = [output for act in acts for output in act.outputs]
        duplicates = sorted(name for name, count in Counter(outputs).items() if count > 1)
        if duplicates:
            raise PydanticCustomError("parallel_output_collision", "PAR repeats outputs: {outputs}", {"outputs": ", ".join(duplicates)})
        return self


class Join(StepModel):
    """The barrier immediately after one parallel group."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"kind": "join"}]})
    kind: Literal["join"] = Field(default="join", description="The process step discriminator.", examples=["join"])


Step = Annotated[Act | Set | Emit | If | Call | Fail | Assert | Foreach | Par | Join, Field(discriminator="kind")]
If.model_rebuild(_types_namespace={"Step": Step, "Condition": Condition})
Foreach.model_rebuild(_types_namespace={"Step": Step})
Par.model_rebuild(_types_namespace={"Step": Step})


def condition_values(condition: Condition) -> list[Value]:
    """Return every process value read by one recursive condition."""
    if isinstance(condition, Compare):
        return [condition.left, condition.right]
    if isinstance(condition, (All, Any)):
        return [value for child in condition.conditions for value in condition_values(child)]
    if isinstance(condition, Not):
        return condition_values(condition.condition)
    raise TypeError(f"unsupported condition {type(condition).__name__}")


def step_values(step: Step) -> list[Value]:
    """Return every value read directly by one step."""
    if isinstance(step, Act):
        return [binding.value for binding in step.inputs]
    if isinstance(step, Set):
        return [step.value]
    if isinstance(step, Emit):
        return [binding.value for binding in step.bindings]
    if isinstance(step, (If, Assert)):
        return condition_values(step.condition)
    if isinstance(step, Foreach):
        return [step.value]
    if isinstance(step, Par):
        return [binding.value for child in step.steps if isinstance(child, Act) for binding in child.inputs]
    return []


def _check_value(value: Value, visible: set[str]) -> None:
    if isinstance(value, BindingValue) and value.binding not in visible:
        raise PydanticCustomError("unbound_process_binding", "process reads unbound local binding {binding}", {"binding": value.binding})


def _validate_bindings(steps: list[Step], visible: set[str]) -> None:
    pending: set[str] | None = None
    for step in steps:
        if pending is not None and not isinstance(step, Join):
            raise PydanticCustomError("parallel_join_not_adjacent", "a step occurs between PAR and JOIN")
        for value in step_values(step):
            _check_value(value, visible)
        if isinstance(step, Act):
            redefined = sorted(set(step.outputs) & visible)
            if redefined:
                raise PydanticCustomError("process_binding_redefined", "process redefines visible local bindings: {bindings}", {"bindings": ", ".join(redefined)})
            visible.update(step.outputs)
        elif isinstance(step, If):
            _validate_bindings(step.then, set(visible))
            if step.otherwise is not None:
                _validate_bindings(step.otherwise, set(visible))
        elif isinstance(step, Foreach):
            if step.binding in visible:
                raise PydanticCustomError("foreach_binding_redefined", "FOREACH redefines visible binding {binding}", {"binding": step.binding})
            if isinstance(step.value, LiteralValue) and not isinstance(step.value.value, list):
                raise PydanticCustomError("foreach_source_not_list", "FOREACH literal source is not a list")
            _validate_bindings(step.steps, visible | {step.binding})
        elif isinstance(step, Par):
            outputs = {output for child in step.steps if isinstance(child, Act) for output in child.outputs}
            redefined = sorted(outputs & visible)
            if redefined:
                raise PydanticCustomError("process_binding_redefined", "PAR redefines visible local bindings: {bindings}", {"bindings": ", ".join(redefined)})
            pending = outputs
        elif isinstance(step, Join):
            if pending is None:
                raise PydanticCustomError("join_without_par", "JOIN has no immediately preceding PAR")
            visible.update(pending)
            pending = None
    if pending is not None:
        raise PydanticCustomError("parallel_join_missing", "PAR has no following JOIN")


def _sequence_always_fails(steps: list[Step]) -> bool:
    for index, step in enumerate(steps):
        always_fails = isinstance(step, Fail)
        if isinstance(step, If):
            always_fails = _sequence_always_fails(step.then) and step.otherwise is not None and _sequence_always_fails(step.otherwise)
        if always_fails:
            if index + 1 < len(steps):
                raise PydanticCustomError("unreachable_process_step", "a process step follows a path that always fails")
            return True
    return False


class Process(Entry):
    """One named ordered way to do a task."""
    model_config = ConfigDict(json_schema_extra={"examples": [{"part": "processes", "id": "write-oak", "name": "Write OAK", "steps": [{"kind": "act", "instruction": "Write the knowledge."}]}, {"part": "processes", "id": "parallel-search", "name": "Search sources", "steps": [{"kind": "par", "steps": [{"kind": "act", "tool": "tool-a", "instruction": "Produce <A>.", "outputs": ["A"]}, {"kind": "act", "tool": "tool-b", "instruction": "Produce <B>.", "outputs": ["B"]}]}, {"kind": "join"}]}]})
    part: Literal["processes"] = Field(default="processes", description="The entry part discriminator.", examples=["processes"])
    name: ProcessName = Field(description="The two-word process display name.", examples=["Write OAK", "Route command"])
    steps: list[Step] = Field(min_length=1, description="The typed process steps in authored order.", examples=[[{"kind": "act", "instruction": "Write the knowledge."}]])
    @model_validator(mode="after")
    def control_flow(self) -> Self:
        _validate_bindings(self.steps, set())
        _sequence_always_fails(self.steps)
        return self
