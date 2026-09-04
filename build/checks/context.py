"""Native OAK interpreter-context, scope, identity, and isolation checks."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from pydantic import JsonValue

from build.checks.fixtures import contract_schemas
from oak.context import InterpreterContext, build_interpreter_context, task_context
from oak.execute.executor import execute
from oak.execute.models import Arrival, ExecutionError
from oak.node.model import Node
from oak.node.parts.constants import Constant
from oak.node.parts.instructions import Instruction
from oak.node.parts.interfaces import Interface
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.steps import Act, Call, Emit, Foreach, Set
from oak.node.parts.processes.values import BindingValue, LiteralValue, ValueBinding
from oak.node.parts.schemas.binding import SchemaBindingError
from oak.node.parts.state import State
from oak.node.parts.triggers import Trigger
from oak.parse.document import parse
from oak.render.selection import render
from oak.resolve.resolver import resolve


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _fails(action: Callable[[], object], error_type: type[Exception], code: str | None = None) -> None:
    try:
        action()
    except error_type as error:
        if code is not None:
            _require(getattr(error, "code", None) == code, f"unexpected context failure: {error}")
        return
    raise RuntimeError("invalid interpreter context was accepted")


def _fixture() -> tuple[Node, dict[str, Node]]:
    raw, normal = contract_schemas()
    contract = "../schemas/contracts.oak.md#schema."
    worker = Node(
        instructions=[Instruction(id="worker-policy", body="Follow $constant.worker-rule in this document.")],
        constants=[Constant(id="worker-rule", value="Strip outer whitespace only.")],
        state=[State(id="status", schema=contract + "raw-name", placeholder="RAW_NAME", value="idle")],
        processes=[Process(
            id="normalise", name="Normalise name", input=contract + "raw-name", output=contract + "normal-name",
            steps=[
                Set(state="state.status", value=LiteralValue(value="working")),
                Act(instruction="Normalise <RAW_NAME> into <NORMAL_NAME>.",
                    input=contract + "raw-name", output=contract + "normal-name",
                    inputs=[ValueBinding(placeholder="RAW_NAME", value=BindingValue(binding="RAW_NAME"))],
                    outputs=["NORMAL_NAME"]),
                Foreach(binding="ITEM", value=LiteralValue(value=[1, 2]), steps=[
                    Act(instruction="Observe <ITEM>.", inputs=[ValueBinding(
                        placeholder="ITEM", value=BindingValue(binding="ITEM"))]),
                ]),
            ],
        )],
    )
    archive = Node(processes=[Process(id="archive", name="Archive task", steps=[Act(instruction="Archive.")])])
    root_contract = "schemas/contracts.oak.md#schema."
    root = Node(
        instructions=[Instruction(id="root-policy", body="Preserve the full task scope.")],
        triggers=[Trigger(id="requested", event="A name arrives.", source="interface.request", process="process.handle")],
        processes=[
            Process(id="handle", name="Handle request", input=root_contract + "raw-name", steps=[
                Call(process="workers/worker.oak.md#process.normalise",
                     inputs=[ValueBinding(placeholder="RAW_NAME", value=BindingValue(binding="RAW_NAME"))],
                     outputs=["NORMAL_NAME"]),
                Emit(interface="interface.result"),
            ]),
            Process(id="archive-task", name="Archive request", steps=[Call(process="archive.oak.md#process.archive")]),
        ],
        interfaces=[
            Interface(id="request", flow="receives", schema=root_contract + "raw-name"),
            Interface(id="result", flow="emits", schema=root_contract + "normal-name"),
        ],
    )
    return root, {
        "root.oak.md": root,
        "workers/worker.oak.md": worker,
        "schemas/contracts.oak.md": Node(schemas=[raw, normal]),
        "archive.oak.md": archive,
    }


def validate_interpreter_context() -> None:
    """Verify context preparation in real execution, including nested calls."""
    root, documents = _fixture()
    before = {path: render(node) for path, node in documents.items()}
    state = {"workers/worker.oak.md#state.status": "idle"}
    arrival = Arrival(interface="interface.request", values={"RAW_NAME": "  OAK  "})
    requests: list[InterpreterContext] = []

    def interpreter(context: InterpreterContext) -> Mapping[str, JsonValue]:
        requests.append(context)
        _require(context.source == "workers/worker.oak.md", "lost the active document")
        _require(context.process == "workers/worker.oak.md#process.normalise", "lost the calling process")
        _require(set(documents) <= set(context.documents), "runtime silently pruned policy context")
        for text in context.documents.values():
            _require(render(parse(text)) == text, "context is not canonical OAK")
        request = parse(context.documents[context.invocation])
        _require(not request.instructions, "source policy was transplanted into another scope")
        request_graph = resolve(request, source=context.invocation, load=context.documents.get)
        worker = parse(context.documents[context.source])
        _require(worker.state[0].value == "working", "context used stale authored state")
        _require(worker.instructions[0].body == documents[context.source].instructions[0].body,
                 "source policy changed")
        action = request.processes[0].steps[0]
        _require(isinstance(action, Act), "invocation is not an ACT")
        _require(all(isinstance(binding.value, LiteralValue) for binding in action.inputs),
                 "invocation still depends on ambient bindings")
        if action.input is None:
            return {}
        contract_document = request_graph.target_document(context.invocation, action.input)
        _require(contract_document == "schemas/contracts.oak.md", "schema identity was rebased incorrectly")
        values = {binding.placeholder: binding.value.value for binding in action.inputs}
        return {"NORMAL_NAME": str(values["RAW_NAME"]).strip()}

    result = execute(root, arrival, state, source="root.oak.md", load=documents.get, interpreter=interpreter)
    _require(result.emissions[0].values == {"NORMAL_NAME": "OAK"}, "native context handler failed")
    _require(len(requests) == 3, "loop child scopes did not receive context")
    _require(state == {"workers/worker.oak.md#state.status": "idle"}, "context mutated caller state")
    _require({path: render(node) for path, node in documents.items()} == before, "context mutated source meaning")
    _fails(lambda: requests[0].documents.__setitem__("x", "y"), AttributeError)

    _fails(lambda: execute(root, arrival, state, source="root.oak.md", load=documents.get,
                          interpreter=lambda _context: {"NORMAL_NAME": ""}), ExecutionError, "invalid_act_output")
    _fails(lambda: execute(root, arrival, state, source="root.oak.md", load=documents.get,
                          interpreter=lambda _context: {"OTHER": "OAK"}), ExecutionError, "act_output_mismatch")
    _fails(lambda: execute(root, arrival, state, source="root.oak.md", load=documents.get,
                          interpreter=interpreter, act=lambda _step, _values: {}),
           ExecutionError, "ambiguous_act_handler")
    _require(state == {"workers/worker.oak.md#state.status": "idle"}, "failed action leaked staged state")

    graph = resolve(root, source="root.oak.md", load=documents.get)
    selected = task_context(graph, "workers/worker.oak.md#process.normalise")
    _require(set(selected) == {"workers/worker.oak.md", "schemas/contracts.oak.md"}, "task view has wrong closure")
    _require(selected["workers/worker.oak.md"] == before["workers/worker.oak.md"], "task view pruned local prose dependencies")
    _require(set(task_context(graph)) == set(documents), "default context pruned the graph")
    retained = task_context(graph, "workers/worker.oak.md#process.normalise", retain=["root.oak.md"])
    _require(set(retained) == set(documents), "explicit retention lost transitive dependencies")
    _fails(lambda: task_context(graph, retain=["missing.oak.md"]), ValueError)
    _fails(lambda: task_context(graph, "schema.handle"), ValueError)
    step = documents["workers/worker.oak.md"].processes[0].steps[1]
    target = "workers/worker.oak.md#process.normalise"
    _fails(lambda: build_interpreter_context(graph, target, step, {}), ValueError)
    _fails(lambda: build_interpreter_context(graph, target, step, {"RAW_NAME": "ok"}, state={}), ValueError)
    _fails(lambda: build_interpreter_context(graph, target, Act(instruction="Unrelated."), {}), ValueError)
    _fails(lambda: build_interpreter_context(graph, target, Act(tool="tool", instruction="Tool."), {}), ValueError)
    _fails(lambda: build_interpreter_context(
        graph, target, step, {"RAW_NAME": "ok"}, state={"workers/worker.oak.md#state.status": False}),
        SchemaBindingError)
    calls = len(requests)
    _fails(lambda: execute(root, Arrival(interface="interface.request", values={"RAW_NAME": ""}), state,
                          source="root.oak.md", load=documents.get, interpreter=interpreter),
           ExecutionError, "invalid_interface_binding")
    _require(len(requests) == calls, "invalid input reached the interpreter")
    values = {"RAW_NAME": "OAK"}
    request = build_interpreter_context(graph, target, step, values)
    snapshot = dict(request.documents)
    values["RAW_NAME"] = "mutated"
    _require(dict(request.documents) == snapshot, "request retained mutable caller values")

    _validate_identity_and_cycles()


def _validate_identity_and_cycles() -> None:
    """Keep same-named schemas distinct and avoid generated filename collisions."""
    raw, normal = contract_schemas()
    raw = type(raw).model_validate({**raw.model_dump(), "id": "contract"})
    normal = type(normal).model_validate({**normal.model_dump(), "id": "contract"})
    action = Act(
        instruction="Normalise <RAW_NAME> into <NORMAL_NAME>.",
        input="__invocation__.oak.md#schema.contract", output="result.oak.md#schema.contract",
        inputs=[ValueBinding(placeholder="RAW_NAME", value=LiteralValue(value=" OAK "))],
        outputs=["NORMAL_NAME"],
    )
    root = Node(processes=[Process(id="normalise", name="Normalise name", steps=[action])])
    documents = {
        "root.oak.md": root,
        "__invocation__.oak.md": Node(schemas=[raw], processes=[Process(
            id="consult", name="Consult root", steps=[Call(process="root.oak.md#process.normalise")],
        )]),
        "result.oak.md": Node(schemas=[normal]),
    }
    graph = resolve(root, source="root.oak.md", load=documents.get)
    view = task_context(graph, "process.normalise")
    _require(set(view) == set(documents), "document-reference cycle lost context")
    context = build_interpreter_context(graph, "process.normalise", action, {"RAW_NAME": " OAK "})
    _require(context.invocation == "__invocation_1__.oak.md", "generated invocation overwrote a source document")
    request = parse(context.documents[context.invocation])
    resolved = resolve(request, source=context.invocation, load=context.documents.get)
    bound = request.processes[0].steps[0]
    _require(resolved.target_document(context.invocation, bound.input) == "__invocation__.oak.md", "input identity changed")
    _require(resolved.target_document(context.invocation, bound.output) == "result.oak.md", "output identity changed")
    repeated = build_interpreter_context(graph, "process.normalise", action, {"RAW_NAME": " OAK "})
    _require(context.documents == repeated.documents, "context generation is not deterministic")


__all__ = ["validate_interpreter_context"]
