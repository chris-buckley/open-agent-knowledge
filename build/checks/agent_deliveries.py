"""Offline artifact and parallel contract checks, not native Codex certification."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import replace
from threading import Barrier, Lock
from pathlib import Path

from pydantic import JsonValue, ValidationError

from oak import ACT, Act, Arrival, ExecutionError, ExecutionResult, Node, Par, ToolContract, SchemaBindingError, execute, parse, render
from oak.execute.models import ActHandler
from examples.parallel_exploration import example, explorer

_EXPECTED_SUMMARY = {
    "SUMMARY": "Exact dispatch and JOIN: fixture/runtime.txt:1-2. Binding validation and failure: fixture/contracts.txt:1-2.",
    "LIMITATIONS": "Deterministic in-memory fixtures only; no live Codex, permission enforcement, or repository test execution.",
}
_EXPECTED_FINDINGS = {
    "Trace action execution and dataflow.": "ACT dispatches an exact registered tool.\nJOIN exposes the two independent reports.",
    "Trace tool contracts and verification.": "Validate input and output bindings.\nReject a failed branch before synthesis.",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _reject(operation: Callable[[], object], reason: str) -> None:
    try:
        operation()
    except (ValueError, RuntimeError, ValidationError, SchemaBindingError) as error:
        if reason not in str(error):
            raise RuntimeError(f"expected {reason!r}, received {error}") from error
        return
    raise RuntimeError(f"invalid exploration accepted: {reason}")


def _arrive(node: Node, tools: Mapping[str, ToolContract], act: ActHandler) -> ExecutionResult:
    return execute(node, Arrival(interface="interface.exploration-input", values=dict(example.FIXTURE_REQUEST)),
                   {}, tools=tools, act=act)


def _parallel_success(grouping: str) -> None:
    node = parse(render(example.coordinator_node, grouping=grouping), grouping=grouping)
    body = node.processes[0].body
    _require([step.kind for step in body] == ["par", "join", "act", "emit"], "PAR/JOIN/synthesis order changed")
    _require([child.tool for child in body[0].body] == ["agent.explore-runtime", "agent.explore-contracts"],
             "exact parallel registrations changed")
    gate, lock = Barrier(2), Lock()
    entered: list[str] = []
    finished: list[str] = []
    received: dict[str, dict[str, JsonValue]] = {}

    def observe(action: Act, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
        question = str(values["QUESTION"])
        with lock:
            entered.append(question)
            received[question] = deepcopy(dict(values))
        gate.wait(timeout=5)  # A sequential executor cannot pass.
        observations = example.observe_fixture(action, values)
        _require(observations["FINDINGS"] == _EXPECTED_FINDINGS[question], "fixture findings changed")
        with lock:
            finished.append(question)
        return observations

    synthesis_calls: list[dict[str, JsonValue]] = []

    def synthesize(action: Act, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
        _require(len(entered) == len(finished) == 2, "synthesis ran before both workers finished")
        _require(set(values) == {*explorer.REQUEST_FIELDS, "RUNTIME_REPORT", "CONTRACT_REPORT"},
                 "joined bindings leaked or collided")
        _require("fixture/runtime.txt:1-2" in str(values["RUNTIME_REPORT"]), "runtime output was swapped")
        _require("fixture/contracts.txt:1-2" in str(values["CONTRACT_REPORT"]), "contract output was swapped")
        synthesis_calls.append(dict(values))
        return example.synthesize_fixture(action, values)

    result = _arrive(node, example.fixture_tools(grouping=grouping, worker_act=observe), synthesize)
    _require(len(result.emissions) == len(synthesis_calls) == 1, "joined result count changed")
    _require(result.emissions[0].interface == "interface.summary-output", "wrong output interface")
    _require(dict(result.emissions[0].values) == _EXPECTED_SUMMARY, "fixture summary differs from independent expectation")
    _require(set(entered) == set(_EXPECTED_FINDINGS), "workers received the same assignment")
    for request in received.values():
        _require(request["PATHS"] == example.FIXTURE_REQUEST["PATHS"], "worker scope changed")
        _require(request["REVISION"] == example.fixture_revision(), "worker snapshot changed")
    _require(result.state == {}, "stateless exploration acquired state")


def _parallel_rejections(grouping: str) -> None:
    node = parse(render(example.coordinator_node, grouping=grouping), grouping=grouping)
    synthesis_calls: list[dict[str, JsonValue]] = []

    def synthesize(action: Act, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
        synthesis_calls.append(dict(values))
        return example.synthesize_fixture(action, values)

    mutations = (
        ("wrong revision", {"INSPECTED_REVISION": "different-revision"}),
        ("blocked", {"STATUS": "blocked", "GAPS": "Fixture context unavailable."}),
        ("invalid status", {"STATUS": "invented"}),
        ("missing evidence", {"EVIDENCE": ""}),
        ("blank evidence", {"EVIDENCE": "  "}),
        ("wrong type", {"FINDINGS": 123}),
        ("extra value", {"EXTRA": "not declared"}),
    )
    for label, mutation in mutations:
        def observe(action: Act, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
            report = dict(example.observe_fixture(action, values))
            if values["QUESTION"] == "Trace action execution and dataflow.":
                report.update(mutation)
            return report
        _reject(lambda: _arrive(node, example.fixture_tools(grouping=grouping, worker_act=observe), synthesize),
                "parallel_failed")
        _require(not synthesis_calls, f"{label} reached successful synthesis")

    def missing(action: Act, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
        report = dict(example.observe_fixture(action, values))
        del report["COVERAGE"]
        return report

    def failed(_action: Act, _values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
        raise ValueError("fixture worker failed")

    for handler in (missing, failed):
        _reject(lambda: _arrive(node, example.fixture_tools(grouping=grouping, worker_act=handler), synthesize),
                "parallel_failed")
        _require(not synthesis_calls, "worker failure reached synthesis")

    tools = example.fixture_tools(grouping=grouping)
    first = "agent.explore-runtime"
    for returned in ({}, {"RUNTIME_REPORT": "", "EXTRA": "undeclared"}, {"RUNTIME_REPORT": 3}):
        changed = {**tools, first: replace(tools[first], handler=lambda _a, _v: returned)}
        _reject(lambda: _arrive(node, changed, synthesize), "parallel_failed")
    _require(not synthesis_calls, "invalid outer tool output reached synthesis")
    for changed, reason in (({first: tools[first]}, "unknown_tool"),
                            ({**tools, first: replace(tools[first], parallel=False)}, "tool_parallelism_unknown"),
                            ({**tools, first: replace(tools[first], outputs=frozenset(("OTHER",)))}, "tool_contract_mismatch")):
        _reject(lambda: _arrive(node, changed, synthesize), reason)
    _require(not synthesis_calls, "invalid registry reached synthesis")
    arrival = Arrival(interface="interface.exploration-input", values={**example.FIXTURE_REQUEST, "REVISION": ""})
    _reject(lambda: execute(node, arrival, {}, tools=tools, act=synthesize), "invalid_interface_binding")


def _worker_rejections() -> None:
    request = {**example.FIXTURE_REQUEST, "QUESTION": "Trace action execution and dataflow."}
    result = execute(explorer.explorer_node, Arrival(interface="interface.exploration-input", values=request),
                     {}, act=example.observe_fixture)
    original = result.emissions[0].values
    for patch, reason in (({"REVISION": "other"}, "request identity"),
                          ({"PATHS": "outside"}, "request identity"),
                          ({"QUESTION": "another assignment"}, "request identity"),
                          ({"STATUS": "blocked"}, "blocked"),
                          ({"INSPECTED_REVISION": "other"}, "different revision")):
        _reject(lambda: example.completed_report({**original, **patch}, request), reason)
    blocked = {"STATUS": "blocked", "INSPECTED_REVISION": "", "FINDINGS": "", "EVIDENCE": "",
               "COVERAGE": "", "GAPS": "No read tools available."}
    result = execute(explorer.explorer_node, Arrival(interface="interface.exploration-input", values=request),
                     {}, act=lambda _a, _v: blocked)
    _require(result.emissions[0].values["STATUS"] == "blocked", "blocked worker invented success")
    _reject(lambda: execute(explorer.explorer_node, Arrival(interface="interface.exploration-input", values=request),
                            {}, act=lambda _a, _v: {**blocked, "GAPS": ""}), "assertion_failed")
    _reject(lambda: execute(explorer.explorer_node, Arrival(interface="interface.exploration-input", values=request), {}),
            "act_handler_missing")
    first = example.explore_runtime_action
    _reject(lambda: Par(body=[first, first]), "parallel_output_collision")
    _reject(lambda: Par(body=[first, ACT("Do native work.")]), "parallel")
    missing_join = example.coordinator_node.model_dump(mode="python", by_alias=True)
    del missing_join["processes"][0]["body"][1]
    _reject(lambda: Node.model_validate(missing_join), "join")


def validate_parallel_exploration() -> None:
    """Verify deterministic overlap and all-or-fail contracts in both groupings."""
    for grouping in ("xml", "markdown"):
        _parallel_success(grouping)
        _parallel_rejections(grouping)
    _worker_rejections()


_BUNDLE_FILES = {
    "parallel_exploration/coordinator.oak.md",
    "parallel_exploration/explorer.oak.md",
    "parallel_exploration/sample.oak.md",
    "parallel_exploration/codex/.codex/agents/oak-explorer.toml",
    "adaptors/codex/adaptor.oak.md",
}
_NATIVE_DEFAULTS = {"sandbox_mode": "read-only", "approval_policy": "never",
                    "web_search": "disabled", "agents": {"enabled": False}}


def _native_contract(text: str, worker: str) -> None:
    import tomllib
    native = tomllib.loads(text)
    agents = native.get("agents")
    _require(isinstance(agents, dict) and set(agents) == {"enabled"} and type(agents["enabled"]) is bool,
             "native metadata needs a boolean agents.enabled")
    expected = {"name": "oak-explorer",
                "description": "Read-only repository exploration with revision-bound findings, file evidence, coverage and gaps.",
                "developer_instructions": worker, **_NATIVE_DEFAULTS}
    _require(native == expected, "native metadata, defaults or embedding differ")
    from oak import resolve
    _require(len(resolve(parse(native["developer_instructions"])).documents) == 1, "native worker is not locally complete")


def _bundle_contract(root: Path, expected: Mapping[str, bytes]) -> None:
    paths = list(root.rglob("*"))
    _require(not root.is_symlink() and not any(path.is_symlink() for path in paths), "bundle contains a symbolic link")
    actual = {path.relative_to(root).as_posix(): path.read_bytes() for path in paths if path.is_file()}
    _require(set(actual) == _BUNDLE_FILES, "bundle file set differs")
    _require(actual == expected, "bundle bytes differ from source")
    directories = {parent.as_posix() for name in expected for parent in Path(name).parents if parent != Path('.')}
    _require({path.relative_to(root).as_posix() for path in paths if path.is_dir()} == directories,
             "bundle directory set differs")
    _native_contract(actual["parallel_exploration/codex/.codex/agents/oak-explorer.toml"].decode(),
                     actual["parallel_exploration/explorer.oak.md"].decode())


def _native_rejections(worker: str) -> None:
    import json
    import tomllib
    from build.agents import native_agent
    text = native_agent(worker, _NATIVE_DEFAULTS)
    _native_contract(text, worker)
    for sample in ("", "\nstart\n", "quote ' and double \"", "triple ''' and \"\"\"",
                   "C:\\path\\n\nΩ 🌳\tend\n", "\x00\x08\x0c\x7f\r\n"):
        decoded = tomllib.loads(native_agent(sample, _NATIVE_DEFAULTS))
        _require(decoded["developer_instructions"] == sample, "TOML escaping lost literal bytes")
    _reject(lambda: native_agent(worker, {**_NATIVE_DEFAULTS, "tools": []}), "Codex defaults")
    native = tomllib.loads(text)
    changes = ({"name": "explorer"}, {"description": ""}, {"developer_instructions": worker[:-1]},
               {"developer_instructions": "Read the worker from another file."}, {"tools": ["read"]},
               {"sandbox_mode": "workspace-write"}, {"agents": {"enabled": True}}, {"agents": {"enabled": 0}})
    for changed in changes:
        corrupted = {**native, **changed}
        # Inline object values use TOML tables rather than a second config grammar.
        lines = [f"{key} = {json.dumps(value, ensure_ascii=False)}" for key, value in corrupted.items() if key != "agents"]
        lines += ["[agents]", "enabled = " + json.dumps(corrupted["agents"]["enabled"])]
        _reject(lambda: _native_contract("\n".join(lines), worker), "native metadata")
    _reject(lambda: _native_contract(text.replace('name = "oak-explorer"\n', ""), worker), "native metadata")
    _reject(lambda: _native_contract(text + "[agents]\nenabled = false\n", worker), "twice")


def _bundle_rejections(expected: Mapping[str, bytes]) -> None:
    from tempfile import TemporaryDirectory
    from build.generated import write_generated
    with TemporaryDirectory(prefix="oak-agent-rejections-") as temporary:
        root = Path(temporary)
        generated, bundle = root / "generated", root / "generated" / "oak.agents"
        products = {bundle / name: content.decode() for name, content in expected.items()}
        write_generated(products, root=generated, owned=bundle)
        _bundle_contract(bundle, expected)
        sentinel = generated / "maintained.txt"
        sentinel.write_text("other generator owns this")
        target = bundle / "parallel_exploration/explorer.oak.md"
        for mutation in ("missing", "stale", "extra", "directory"):
            if mutation == "missing":
                target.unlink()
            elif mutation == "stale":
                target.write_text("stale")
            elif mutation == "extra":
                (bundle / "run.py").write_text("raise RuntimeError('must never run')")
            else:
                (bundle / "unused").mkdir()
            _reject(lambda: _bundle_contract(bundle, expected), "bundle")
            write_generated(products, root=generated, owned=bundle)
            _bundle_contract(bundle, expected)
        original = target.read_bytes()
        target.unlink()
        target.symlink_to(sentinel)
        _reject(lambda: _bundle_contract(bundle, expected), "symbolic link")
        _reject(lambda: write_generated(products, root=generated, owned=bundle), "symbolic link")
        _require(sentinel.read_text() == "other generator owns this", "generator overwrote another owner")
        target.unlink()
        target.write_bytes(original)
        _reject(lambda: write_generated({bundle / ".." / "escape": "no"}, root=generated, owned=bundle), "outside")
        _bundle_contract(bundle, expected)


def _detached_bundle() -> None:
    import shutil
    from tempfile import TemporaryDirectory
    from build.agents import PACKAGE
    from build.checks.fixtures import ROOT
    from build.checks.outputs import _run_isolated
    script = '''
import importlib.abc, pathlib, sys, tomllib
root = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(root / 'runtime'))
class RejectSources(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in ('build', 'examples'):
            raise RuntimeError('detached artifact imported repository source')
sys.meta_path.insert(0, RejectSources())
def refuse_network(event, args):
    if event.startswith('socket.'):
        raise RuntimeError('detached artifact attempted network')
sys.addaudithook(refuse_network)
from oak import parse, render, resolve
bundle = root / 'oak.agents'
scenario = bundle / 'parallel_exploration'
for path in bundle.rglob('*.oak.md'):
    text = path.read_text()
    node = parse(text)
    assert render(node) == text.rstrip('\\n')
    assert len(resolve(node).documents) == 1
native = tomllib.loads((root / 'native-only' / 'oak-explorer.toml').read_text())
assert native['developer_instructions'] == (scenario / 'explorer.oak.md').read_text()
assert len(resolve(parse(native['developer_instructions'])).documents) == 1
assert {p.name for p in (root / 'native-only').iterdir()} == {'oak-explorer.toml'}
assert not (root / '.agents').exists()
assert not (root / 'build').exists()
'''
    with TemporaryDirectory(prefix="oak-agent-detached-") as temporary:
        root = Path(temporary)
        shutil.copytree(ROOT / "oak", root / "runtime" / "oak", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(PACKAGE, root / "oak.agents")
        (root / "native-only").mkdir()
        shutil.copyfile(PACKAGE / "parallel_exploration/codex/.codex/agents/oak-explorer.toml",
                        root / "native-only" / "oak-explorer.toml")
        _run_isolated(script, root)



def _adaptor_rejections() -> None:
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
    from build.agents import ADAPTOR_SOURCE, adaptor_node
    from oak import Instruction
    original = ADAPTOR_SOURCE.read_bytes()
    with TemporaryDirectory(prefix="oak-adaptor-rejections-") as temporary:
        root = Path(temporary)
        owner = root / "source"
        owner.mkdir()
        source = owner / "adaptor.oak.md"
        source.write_bytes(original)
        with patch("build.agents.ROOT", root), patch("build.agents.ADAPTOR_SOURCE", source):
            node = adaptor_node()
            widened = Node(constants=node.constants, instructions=[Instruction(id="scope", body="Widen the agent scope.")])
            source.write_text(render(widened), encoding="utf-8")
            _reject(adaptor_node, "constants and schemas only")
            source.unlink()
            outside = root / "outside.oak.md"
            outside.write_bytes(original)
            source.symlink_to(outside)
            _reject(adaptor_node, "symbolic link")
            source.unlink()
            source.write_bytes(original)
        alias = root / "linked-source"
        alias.symlink_to(owner, target_is_directory=True)
        with patch("build.agents.ROOT", root), patch("build.agents.ADAPTOR_SOURCE", alias / source.name):
            _reject(adaptor_node, "symbolic link")
        _require(source.read_bytes() == outside.read_bytes() == original, "rejected adaptor source was modified")

def validate_agent_deliveries() -> None:
    """Check native artifacts, literal identity, safety, detached closure and fixture behavior."""
    from build.agents import ADAPTOR_SOURCE, PACKAGE, artifacts
    expected = {path.relative_to(PACKAGE).as_posix(): text.encode() for path, text in artifacts().items()}
    _bundle_contract(PACKAGE, expected)
    _require(expected["adaptors/codex/adaptor.oak.md"] == ADAPTOR_SOURCE.read_bytes(), "adaptor copy differs")
    _native_rejections(explorer.build())
    _adaptor_rejections()
    _bundle_rejections(expected)
    _detached_bundle()
    validate_parallel_exploration()
