"""Flat parallel exploration with in-memory fixtures, never live Codex dispatch.

Run `python -m examples.parallel_exploration.example` in this repository to
refresh the coordinator. The registered demonstration executes the real OAK
worker process through two exact ToolContracts and a bounded test barrier.
"""

from __future__ import annotations

from collections.abc import Mapping
from hashlib import sha256
from pathlib import Path
from threading import Barrier

from pydantic import JsonValue

from oak import (
    ACT, Act, Arrival, Constant, ConstantValue, Emit, ExecutionResult, Interface,
    Join, Node, NonEmpty, Par, Process, Schema, ToolContract, Trigger, Type,
    ValueBinding, execute, parse, render, resolve, where,
)
from oak.execute.models import ActHandler
from examples.bindings import local_bindings
from examples.parallel_exploration.explorer import (
    REQUEST_FIELDS, SCHEMA_EXPLORATION_REQUEST, exploration_report_schema,
    exploration_request_schema, explorer_node,
)
from examples.schemas.shape_gallery import populate_example

runtime_report_schema = Schema(
    id="runtime-report", name="Runtime Report",
    template="<RUNTIME_REPORT>",
    where=[where("RUNTIME_REPORT", Type(of="string"), NonEmpty(),
                 description="one complete populated exploration report, validated by the dispatch boundary")],
)
contract_report_schema = Schema(
    id="contract-report", name="Contract Report",
    template="<CONTRACT_REPORT>",
    where=[where("CONTRACT_REPORT", Type(of="string"), NonEmpty(),
                 description="one complete populated exploration report, validated by the dispatch boundary")],
)
exploration_summary_schema = Schema(
    id="exploration-summary", name="Exploration Summary",
    purpose="Reconcile both reports while preserving uncertainty and evidence limitations.",
    template="## Findings\n<SUMMARY>\n\n## Limitations\n<LIMITATIONS>",
    where=[where("SUMMARY", Type(of="string"), NonEmpty()),
           where("LIMITATIONS", Type(of="string"), NonEmpty())],
)
SCHEMA_RUNTIME_REPORT = f"schema.{runtime_report_schema.id}"
SCHEMA_CONTRACT_REPORT = f"schema.{contract_report_schema.id}"
SCHEMA_EXPLORATION_SUMMARY = f"schema.{exploration_summary_schema.id}"

runtime_question_constant = Constant(id="runtime-question", value="Trace action execution and dataflow.")
contracts_question_constant = Constant(id="contracts-question", value="Trace tool contracts and verification.")
runtime_request_bindings = [
    ValueBinding(placeholder="QUESTION", value=ConstantValue(constant=f"constant.{runtime_question_constant.id}")),
    *local_bindings(("PATHS", "REVISION")),
]
contracts_request_bindings = [
    ValueBinding(placeholder="QUESTION", value=ConstantValue(constant=f"constant.{contracts_question_constant.id}")),
    *local_bindings(("PATHS", "REVISION")),
]
runtime_question = "Investigate <QUESTION> within <PATHS> at <REVISION>; return validated <RUNTIME_REPORT>."
contracts_question = "Investigate <QUESTION> within <PATHS> at <REVISION>; return validated <CONTRACT_REPORT>."
explore_runtime_action = ACT.tool(
    "agent.explore-runtime",
    runtime_question,
    input=SCHEMA_EXPLORATION_REQUEST,
    output=SCHEMA_RUNTIME_REPORT,
    inputs=runtime_request_bindings,
    outputs=["RUNTIME_REPORT"],
)
explore_contracts_action = ACT.tool(
    "agent.explore-contracts",
    contracts_question,
    input=SCHEMA_EXPLORATION_REQUEST,
    output=SCHEMA_CONTRACT_REPORT,
    inputs=contracts_request_bindings,
    outputs=["CONTRACT_REPORT"],
)
parallel_exploration = Par(body=[explore_runtime_action, explore_contracts_action])
join_exploration = Join()
synthesize_exploration_action = ACT(
    "Reconcile <RUNTIME_REPORT> and <CONTRACT_REPORT> for <QUESTION> within <PATHS> at <REVISION>. "
    "Require complete reports for that same revision and scope before synthesis; reject malformed, "
    "blocked or mismatched reports. Preserve disagreements, file-backed evidence and gaps in <SUMMARY> "
    "and <LIMITATIONS>. Reading a test is not running it. Do not invent findings or tool effects.",
    output=SCHEMA_EXPLORATION_SUMMARY,
    inputs=local_bindings((*REQUEST_FIELDS, "RUNTIME_REPORT", "CONTRACT_REPORT")),
    outputs=["SUMMARY", "LIMITATIONS"],
)
emit_exploration = Emit(interface="interface.summary-output")
explore_repository_process = Process(
    id="explore-repository",
    name="Explore repository",
    input=SCHEMA_EXPLORATION_REQUEST,
    body=[parallel_exploration, join_exploration, synthesize_exploration_action, emit_exploration],
)
exploration_requested_trigger = Trigger(
    id="exploration-requested", event="Parallel repository exploration is requested.",
    source="interface.exploration-input", process=f"process.{explore_repository_process.id}",
)
exploration_request_interface = Interface(
    id="exploration-input", flow="receives", schema=SCHEMA_EXPLORATION_REQUEST,
    description="A bounded overall question whose execution and contract aspects can be explored independently.",
)
exploration_summary_interface = Interface(
    id="summary-output", flow="emits", schema=SCHEMA_EXPLORATION_SUMMARY,
    description="A joined, evidence-backed answer, not permission for implementation or proof of live Codex execution.",
)
coordinator_node = Node(
    constants=[runtime_question_constant, contracts_question_constant],
    schemas=[exploration_request_schema, runtime_report_schema, contract_report_schema, exploration_summary_schema],
    triggers=[exploration_requested_trigger], processes=[explore_repository_process],
    interfaces=[exploration_request_interface, exploration_summary_interface],
)
TARGET = Path(__file__).with_suffix(".oak.md")

# These named in-memory files are fixture data, not observations of OAK source files.
FIXTURE_DOCUMENTS = {
    "fixture/AGENTS.md": "Inspect fixture data only. Change nothing. Do not run tests.\n",
    "fixture/runtime.txt": "ACT dispatches an exact registered tool.\nJOIN exposes the two independent reports.\n",
    "fixture/contracts.txt": "Validate input and output bindings.\nReject a failed branch before synthesis.\n",
}
FIXTURE_PATHS = "\n".join(FIXTURE_DOCUMENTS)
FIXTURE_QUESTIONS = {
    "Trace action execution and dataflow.": "fixture/runtime.txt",
    "Trace tool contracts and verification.": "fixture/contracts.txt",
}


def fixture_revision() -> str:
    """Observe the fixture snapshot, independently of the requested revision."""
    digest = sha256()
    for name, text in sorted(FIXTURE_DOCUMENTS.items()):
        digest.update(name.encode() + b"\0" + text.encode() + b"\0")
    return "fixture-sha256:" + digest.hexdigest()


FIXTURE_REQUEST = {
    "QUESTION": "Explain fixture dispatch and contract checks.",
    "PATHS": FIXTURE_PATHS,
    "REVISION": fixture_revision(),
}
REPOSITORY_QUESTION = (
    "Trace how a tool-backed ACT is authored, validated, resolved, and executed in OAK.\n"
    "Identify its governing contracts, implementation owners, demonstrations, and\n"
    "verification gaps. Cite the inspected files. Change nothing."
)
REPOSITORY_REQUEST = {
    "QUESTION": REPOSITORY_QUESTION,
    "PATHS": "AGENTS.md\n.agents/rules/\noak/\nbuild/\nexamples/",
    "REVISION": "9956e6998869fcfbd84067eec0d6303273a54174",
}
NATIVE_PARENT_REQUEST = (
    "Use two oak-explorer instances in parallel on open-agent-knowledge at revision "
    "9956e6998869fcfbd84067eec0d6303273a54174 within AGENTS.md, .agents/rules/, oak/, build/ and examples/. "
    "Give one action execution/dataflow and the other tool contracts/verification. Both must read complete "
    "applicable AGENTS at that revision before other inspection, change nothing, and return their full report. "
    "Wait for both; do not accept blocked, malformed or wrong-revision results as success. Reconcile findings, "
    "citations and gaps in one answer. This is a native-parent usage example, not a claim that Codex runs "
    "the Python OAK executor or that the illustrative agent.explore-* tools are Codex built-ins."
)


def sample() -> Node:
    """Complete sample inputs and fixture content; none is a live repository receipt."""
    exploration_request_schema.bind(REPOSITORY_REQUEST)
    exploration_request_schema.bind(FIXTURE_REQUEST)
    return Node(constants=[
        Constant(id="repository-request", value=REPOSITORY_REQUEST),
        Constant(id="native-parent-request", form="text", value=NATIVE_PARENT_REQUEST),
        Constant(id="fixture-request", value=FIXTURE_REQUEST),
        Constant(id="fixture-documents", form="json", value=FIXTURE_DOCUMENTS),
        Constant(id="evidence-boundary", value=(
            "The repository request and native-parent prompt are examples, not executed work. "
            "Repository fixtures inspect only the supplied in-memory fixture files, not OAK source or native clients. "
            "The two ToolContracts exist only in example.py. No live runtime or permission enforcement is delivered."
        )),
    ])


def observe_fixture(_action: Act, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
    """A deterministic native-ACT stand-in with explicit, inspectable input data."""
    question = values["QUESTION"]
    if not isinstance(question, str) or question not in FIXTURE_QUESTIONS:
        raise ValueError("unknown fixture assignment")
    if values["PATHS"] != FIXTURE_PATHS:
        raise ValueError("fixture scope differs from its declared documents")
    name = FIXTURE_QUESTIONS[question]
    return {
        "STATUS": "complete", "INSPECTED_REVISION": fixture_revision(),
        "FINDINGS": FIXTURE_DOCUMENTS[name].rstrip("\n"),
        "EVIDENCE": f"{name}:1-2 (in-memory fixture, not repository evidence)",
        "COVERAGE": f"fixture/AGENTS.md:1 and {name}:1-2; all supplied fixture governing text read.",
        "GAPS": "No live model, native permissions, actual repository inspection or test execution was evaluated.",
    }


def completed_report(report: Mapping[str, JsonValue], request: Mapping[str, JsonValue]) -> str:
    """Validate the worker emission before promoting it through the caller's contract."""
    exploration_report_schema.bind(report)
    if any(report[name] != request[name] for name in REQUEST_FIELDS):
        raise ValueError("worker changed its request identity or scope")
    if report["STATUS"] != "complete":
        raise ValueError("worker exploration is blocked")
    if report["INSPECTED_REVISION"] != request["REVISION"]:
        raise ValueError("worker inspected a different revision")
    if any(not isinstance(report[name], str) or not report[name].strip()
           for name in ("FINDINGS", "EVIDENCE", "COVERAGE")):
        raise ValueError("complete worker report lacks findings, evidence or coverage")
    return populate_example(exploration_report_schema, report)


def fixture_tools(*, grouping: str = "xml", gate: Barrier | None = None,
                  worker_act: ActHandler = observe_fixture) -> dict[str, ToolContract]:
    """Register two explicit output mappings to one worker, without a Codex adapter."""
    worker = parse(render(explorer_node, grouping=grouping), grouping=grouping)

    def dispatch(action: Act, request: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
        if gate is not None:
            gate.wait(timeout=5)
        result = execute(worker, Arrival(interface="interface.exploration-input", values=dict(request)),
                         {}, act=worker_act)
        if len(result.emissions) != 1 or result.emissions[0].interface != "interface.exploration-output":
            raise ValueError("worker must emit exactly one exploration report")
        return {action.outputs[0]: completed_report(result.emissions[0].values, request)}

    return {
        "agent.explore-runtime": ToolContract(
            dispatch, frozenset(REQUEST_FIELDS), frozenset(("RUNTIME_REPORT",)),
            parallel=True, input=SCHEMA_EXPLORATION_REQUEST, output=SCHEMA_RUNTIME_REPORT,
        ),
        "agent.explore-contracts": ToolContract(
            dispatch, frozenset(REQUEST_FIELDS), frozenset(("CONTRACT_REPORT",)),
            parallel=True, input=SCHEMA_EXPLORATION_REQUEST, output=SCHEMA_CONTRACT_REPORT,
        ),
    }


def synthesize_fixture(_action: Act, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
    """Reconcile known fixture reports, not arbitrary model-generated findings."""
    if any(values[name] != FIXTURE_REQUEST[name] for name in REQUEST_FIELDS):
        raise ValueError("synthesis received a different fixture request")
    for binding, question in (("RUNTIME_REPORT", "Trace action execution and dataflow."),
                              ("CONTRACT_REPORT", "Trace tool contracts and verification.")):
        request = {**FIXTURE_REQUEST, "QUESTION": question}
        observations = observe_fixture(_action, request)
        expected = completed_report({**request, **observations}, request)
        if values[binding] != expected:
            raise ValueError("synthesis received an invalid or mismatched fixture report")
    return {
        "SUMMARY": "Exact dispatch and JOIN: fixture/runtime.txt:1-2. Binding validation and failure: fixture/contracts.txt:1-2.",
        "LIMITATIONS": "Deterministic in-memory fixtures only; no live Codex, permission enforcement, or repository test execution.",
    }


def run(*, grouping: str = "xml") -> ExecutionResult:
    """Exercise real OAK PAR/JOIN with two synchronized deterministic workers."""
    node = parse(render(coordinator_node, grouping=grouping), grouping=grouping)
    return execute(node, Arrival(interface="interface.exploration-input", values=dict(FIXTURE_REQUEST)), {},
                   tools=fixture_tools(grouping=grouping, gate=Barrier(2)), act=synthesize_fixture)


def build() -> str:
    for grouping in ("xml", "markdown"):
        text = render(coordinator_node, grouping=grouping)
        parsed = parse(text, grouping=grouping)
        resolve(parsed)
        if render(parsed, grouping=grouping) != text:
            raise RuntimeError(f"coordinator did not round-trip through {grouping}")
    return render(coordinator_node)


def write() -> Path:
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
