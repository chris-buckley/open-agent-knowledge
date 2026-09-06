"""Statement-body contracts, independent encodings, and flat example assembly."""

from __future__ import annotations

import ast
from collections.abc import Callable
from importlib import import_module
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

import oak
from build.checks.fixtures import normalized
from examples.catalog import SCENARIOS
from oak import (
    ACT, Assert, BindingValue, Call, Compare, Constant, Emit, Fail, Foreach, If,
    Instruction, Interface, Join, LiteralValue, Node, Par, Process, Schema,
    Set, State, StateValue, Statement, Type, ValueBinding, While, node_json_ld, parse,
    render, resolve, where,
)
from oak.node.parts.processes.statements import StatementModel, iter_statements
from oak.surface import SURFACES

_STATEMENT = TypeAdapter(Statement)
_KINDS = {"act", "set", "emit", "if", "call", "fail", "assert", "foreach", "while", "par", "join"}
_BODY_TYPES = (Process, Foreach, While, Par)
_TRUE = Compare(left=LiteralValue(value=True), operator="equals", right=LiteralValue(value=True))
_FALSE = Compare(left=LiteralValue(value=True), operator="equals", right=LiteralValue(value=False))
_LITERAL = {"steps": [{"kind": "while", "steps": ["literal"]}], "thenSteps": "data", "body": "text"}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _reject(operation: Callable[[], object], code: str | None = None) -> None:
    try:
        operation()
    except ValidationError as error:
        if code is not None:
            _require(code in {item["type"] for item in error.errors()}, f"missing rejection {code}: {error}")
        return
    raise RuntimeError("invalid statement body was accepted")


def _specimen() -> Node:
    """Exercise every variant without using model examples as expected results."""
    observed = ACT("Observe.")
    helper = Process(id="help", name="Help task", body=[observed])
    payload_schema = Schema(id="payload", template="<DATA>", where=[where("DATA", Type(of="string"))])
    item_value = BindingValue(binding="ITEM")
    item_binding = ValueBinding(placeholder="ITEM", value=item_value)
    item_action = ACT("Observe <ITEM>.", inputs=[item_binding])
    loop = Foreach(binding="ITEM", value=LiteralValue(value=[1, 2]), body=[item_action])
    first_tool = ACT.tool("first", "Observe first.")
    second_tool = ACT.tool("second", "Observe second.")
    parallel = Par(body=[first_tool, second_tool])
    branch_condition = Compare(left=StateValue(state="state.status"), operator="equals", right=LiteralValue(value="done"))
    branch = If(condition=branch_condition, then=[loop, parallel, Join()], otherwise=[Fail(message="Not selected.")])
    cycle_condition = Compare(left=StateValue(state="state.status"), operator="equals", right=LiteralValue(value="ready"))
    cycle = While(condition=cycle_condition, limit=2, body=[observed])
    literal_action = ACT("Observe <DATA>.", inputs=[ValueBinding(placeholder="DATA", value=LiteralValue(value=_LITERAL))])
    body = [
        literal_action,
        Set(state="state.status", value=LiteralValue(value="done")),
        branch,
        cycle,
        Call(process="process.help"),
        Assert(condition=branch_condition),
        Emit(interface="interface.result", bindings=[ValueBinding(placeholder="DATA", value=LiteralValue(value="done"))]),
    ]
    main = Process(id="run", name="Run task", body=body)
    return Node(
        instructions=[Instruction(id="policy", body="Keep the scope.")],
        constants=[Constant(id="literal-data", value=_LITERAL)],
        schemas=[payload_schema],
        state=[State(id="status", value="ready")],
        processes=[helper, main],
        interfaces=[Interface(id="result", flow="emits", schema="schema.payload")],
    )


def _validate_named_construction() -> None:
    named_action = ACT("Observe.")
    named = Process(id="observe", name="Observe task", body=[named_action])
    inline = Process(id="observe", name="Observe task", body=[ACT("Observe.")])
    _require(named == inline, "naming a statement changed the model")
    _require(render(Node(processes=[named])) == render(Node(processes=[inline])), "named construction changed text")
    node = _specimen()
    statements = list(iter_statements(node.processes[-1].body))
    _require({item.kind for item in statements} == _KINDS, "statement union or traversal lost a variant")
    _require([item.kind for item in statements] == [
        "act", "set", "if", "foreach", "act", "par", "act", "act", "join", "fail",
        "while", "act", "call", "assert", "emit",
    ], "recursive traversal changed order")
    for statement in statements:
        _require(isinstance(statement, StatementModel), "a variant lost its tagged base")
        _require(_STATEMENT.validate_python(statement.model_dump()) == statement, "statement did not validate")
    for grouping in ("xml", "markdown"):
        text = render(node, grouping=grouping)
        parsed = parse(text)
        resolve(parsed)
        _require(normalized(parsed) == normalized(node), "round-trip changed body meaning")
        _require(render(parsed, grouping=grouping) == text, "round-trip changed body text")
        _require(parsed.constants[0].value == _LITERAL, "literal keys were migrated")
        _require(parsed.processes[-1].body[0].inputs[0].value.value == _LITERAL, "literal binding keys changed")


def _validate_body_rejections() -> None:
    fixtures = (
        (Process, {"id": "run", "name": "Run task"}, [{"kind": "act", "instruction": "Observe."}]),
        (Foreach, {"binding": "ITEM", "value": {"source": "literal", "value": [1]}}, [{"kind": "act", "instruction": "Observe."}]),
        (While, {"condition": _FALSE, "limit": 1}, [{"kind": "act", "instruction": "Observe."}]),
        (Par, {}, [{"kind": "act", "tool": "first", "instruction": "Observe."}]),
    )
    for model, fields, body in fixtures:
        valid = {**fields, "body": body}
        instance = model.model_validate(valid)
        _require(isinstance(instance.model_dump()["body"], list), "model body is not an ordinary list")
        _require(not hasattr(instance, "steps"), "legacy attribute remains")
        for invalid in (fields, {**fields, "body": []}, {**fields, "body": None}, {**fields, "body": "Observe."}):
            _reject(lambda invalid=invalid, model=model: model.model_validate(invalid))
        for invalid in ({**fields, "steps": body}, {**valid, "steps": body}, {**valid, "steps": None}):
            _reject(lambda invalid=invalid, model=model: model.model_validate(invalid), "extra_forbidden")
        for malformed in ([{"kind": "unknown"}], [{"kind": "act"}], ["Observe."]):
            _reject(lambda malformed=malformed, fields=fields, model=model: model.model_validate({**fields, "body": malformed}))
        for mode in ("validation", "serialization"):
            schema = model.model_json_schema(mode=mode)
            if "$ref" in schema:
                schema = schema["$defs"][schema["$ref"].split("/")[-1]]
            _require("body" in schema["required"] and "steps" not in schema["properties"], "JSON Schema exposes old fields")
            _require(schema["properties"]["body"]["minItems"] == 1, "body lost its nonempty constraint")
    nested = {"id": "run", "name": "Run task", "body": [{"kind": "while", "condition": _FALSE, "limit": 1, "steps": [{"kind": "act", "instruction": "Observe."}]}]}
    _reject(lambda: Process.model_validate(nested), "extra_forbidden")
    _reject(lambda: Par(body=[ACT("Native.")]), "parallel_step_not_tool_act")
    _reject(lambda: Process(id="run", name="Run task", body=[Join()]))
    _reject(lambda: Process(id="run", name="Run task", body=[Par(body=[ACT.tool("first", "Observe.")])]))
    _reject(lambda: If(condition=_TRUE, then=[]))
    _reject(lambda: If(condition=_TRUE, then=[ACT("Observe.")], otherwise=[]))
    _reject(lambda: While(condition=_TRUE, limit=0, body=[ACT("Observe.")]))


def _validate_removed_api() -> None:
    for module in (oak, import_module("oak.node.parts"), import_module("oak.node.parts.processes"), import_module("oak.node.parts.processes.statements")):
        for name in ("Step", "StepModel", "iter_steps", "step_values"):
            _require(not hasattr(module, name), f"legacy export remains: {module.__name__}.{name}")
    for old in ("oak.node.parts.processes.steps", "oak.parse.steps", "oak.execute.steps"):
        try:
            import_module(old)
        except ModuleNotFoundError as error:
            _require(error.name == old, "legacy module failed for an unrelated reason")
        else:
            raise RuntimeError(f"legacy forwarding module remains: {old}")
    for surface in SURFACES:
        _require(not surface.id.startswith("step-"), "old surface id remains")
        if surface.model in _BODY_TYPES:
            _require("<BODY>" in surface.shape and "<STEPS>" not in surface.shape, "surface body slot drift")
    _require(set(If.model_fields) == {"kind", "condition", "then", "otherwise"}, "IF branch fields changed")


def _validate_json_ld_bodies() -> None:
    encoded = node_json_ld(_specimen(), document="https://example.org/task", vocabulary="https://example.org/oak#")
    context = encoded["@context"]
    _require(context["body"] == "oak:body", "instruction body became a list container")
    _require("steps" not in context and "thenSteps" not in context, "legacy structural context remains")
    _require(context["then"] == {"@id": "oak:then", "@container": "@list"}, "then lost ordered semantics")
    _require(context["otherwise"] == {"@id": "oak:otherwise", "@container": "@list"}, "otherwise lost ordered semantics")
    _require(encoded["instructions"][0]["body"] == "Keep the scope.", "instruction text changed")
    _require(encoded["constants"][0]["value"] == {"@value": _LITERAL, "@type": "@json"}, "JSON literal changed")
    action = {"@type": "oak:Act", "instruction": "Observe.", "inputs": [], "outputs": []}
    # Independent expected encoding, not another invocation of the encoder.
    _require(encoded["processes"][0]["body"] == {"@list": [action]}, "process body is not an explicit ordered list")
    body = encoded["processes"][1]["body"]["@list"]
    _require([item["@type"] for item in body] == ["oak:Act", "oak:Set", "oak:If", "oak:While", "oak:Call", "oak:Assert", "oak:Emit"], "JSON-LD process order changed")
    branch = body[2]
    _require([item["@type"] for item in branch["then"]] == ["oak:Foreach", "oak:Par", "oak:Join"], "branch order changed")
    _require(branch["otherwise"] == [{"@type": "oak:Fail", "message": "Not selected."}], "else branch changed")
    _require(branch["then"][1]["body"] == {"@list": [
        {"@type": "oak:Act", "tool": "first", "instruction": "Observe first.", "inputs": [], "outputs": []},
        {"@type": "oak:Act", "tool": "second", "instruction": "Observe second.", "inputs": [], "outputs": []},
    ]}, "parallel body order changed")
    _require(body[3]["body"] == {"@list": [action]}, "while body changed")
    _require(branch["then"][0]["body"]["@list"][0]["instruction"] == "Observe <ITEM>.", "foreach body lost its action")
    _require(body[0]["inputs"][0]["value"]["value"] == {"@value": _LITERAL, "@type": "@json"}, "action data was structurally renamed")


def _flat_assembly(source: str) -> None:
    """Check the accepted assembly contract, not a general indentation metric."""
    for statement in ast.parse(source).body:
        if not isinstance(statement, ast.Assign) or not isinstance(statement.value, ast.Call):
            continue
        call = statement.value
        if not isinstance(call.func, ast.Name) or call.func.id not in {"Process", "While", "Foreach", "Par", "If"}:
            continue
        for keyword in call.keywords:
            if keyword.arg not in {"body", "then", "otherwise"} or isinstance(keyword.value, ast.Constant):
                continue
            if not isinstance(keyword.value, ast.List) or not all(isinstance(child, ast.Name) for child in keyword.value.elts):
                raise ValueError(f"{call.func.id}.{keyword.arg} must assemble named statements")


def _validate_flat_examples() -> None:
    for scenario in SCENARIOS:
        for module in scenario.modules:
            _flat_assembly(Path(module.__file__).read_text(encoding="utf-8"))
    _flat_assembly('work = Process(body=[review_action, emit_review])')
    for invalid in ('work = Process(body=[ACT("Review.")])', 'loop = While(body=[Set(state="state.status")])', 'branch = If(then=[Emit(interface="interface.result")])'):
        try:
            _flat_assembly(invalid)
        except ValueError:
            continue
        raise RuntimeError("inline statement fixture passed the flat authoring check")


def validate_statement_bodies() -> None:
    _validate_named_construction()
    _validate_body_rejections()
    _validate_removed_api()
    _validate_json_ld_bodies()
    _validate_flat_examples()


__all__ = ["validate_statement_bodies"]
