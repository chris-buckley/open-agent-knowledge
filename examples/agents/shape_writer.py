"""Explain a small change through a table, decision, outline, and code file.

The deterministic host below handles one declared fixture only, not arbitrary
requests or live model inference. The OAK process carries typed values; the
example host presents them through the referenced schema templates.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pydantic import JsonValue
from oak import ACT, Act, Arrival, Call, Emit, Instruction, Interface, Node, NonEmpty, Process, Schema, Trigger, Type, execute, parse, render, resolve, where
from examples.agents.bindings import local_bindings
from examples.schemas.shape_gallery import EXPECTED_INSTANCES, SAMPLE_BINDINGS, SHAPES, populate_example, shape_gallery_node

SCHEMA_REQUEST = "schema.change-request"
SCHEMA_COMPARISON = "../schemas/shape_gallery.oak.md#schema.option-comparison"
SCHEMA_DECISION = "../schemas/shape_gallery.oak.md#schema.decision-brief"
SCHEMA_OUTLINE = "../schemas/shape_gallery.oak.md#schema.work-outline"
SCHEMA_FILE = "../schemas/shape_gallery.oak.md#schema.code-file"
PROCESS_COMPARE_OPTIONS = "process.compare-options"
PROCESS_DECIDE_CHANGE = "process.decide-change"
PROCESS_PLAN_CHANGE = "process.plan-change"
PROCESS_WRITE_FILE = "process.write-file"
PROCESS_PREPARE_CHANGE = "process.prepare-change"
INTERFACE_REQUEST = "interface.request"
INTERFACE_COMPARISON = "interface.comparison"
INTERFACE_DECISION = "interface.decision"
INTERFACE_OUTLINE = "interface.outline"
INTERFACE_FILE = "interface.file"
PLACEHOLDER_REQUEST = "REQUEST"
PLACEHOLDERS_COMPARISON = ["CRITERION", "CURRENT", "PROPOSED"]
PLACEHOLDERS_DECISION = ["DECISION", "RATIONALE"]
PLACEHOLDERS_OUTLINE = ["GOAL", "STEP", "CHECK"]
PLACEHOLDERS_FILE = ["FILE_PATH", "CODE"]
SOURCE = "examples/agents/shape_writer.oak.md"
TARGET = Path(__file__).with_suffix(".oak.md")
SAMPLE_REQUEST = "Reject blank task titles with one Python predicate."

change_request_schema = Schema(
    id="change-request", template="<REQUEST>",
    where=[where(PLACEHOLDER_REQUEST, Type(of="string"), NonEmpty())],
)
compare_options_process = Process(
    id="compare-options", name="Compare options", input=SCHEMA_REQUEST, output=SCHEMA_COMPARISON,
    steps=[ACT(
        "Compare current and proposed behaviour for <REQUEST>; produce <CRITERION>, <CURRENT>, and <PROPOSED>.",
        input=SCHEMA_REQUEST, output=SCHEMA_COMPARISON,
        inputs=local_bindings([PLACEHOLDER_REQUEST]), outputs=PLACEHOLDERS_COMPARISON,
    )],
)
decide_change_process = Process(
    id="decide-change", name="Decide change", input=SCHEMA_COMPARISON, output=SCHEMA_DECISION,
    steps=[ACT(
        "For <CRITERION>, weigh <CURRENT> against <PROPOSED> and produce <DECISION> and <RATIONALE>.",
        input=SCHEMA_COMPARISON, output=SCHEMA_DECISION,
        inputs=local_bindings(PLACEHOLDERS_COMPARISON), outputs=PLACEHOLDERS_DECISION,
    )],
)
plan_change_process = Process(
    id="plan-change", name="Plan change", input=SCHEMA_DECISION, output=SCHEMA_OUTLINE,
    steps=[ACT(
        "Plan <DECISION> under <RATIONALE>; produce one <GOAL>, implementation <STEP>, and nested <CHECK>.",
        input=SCHEMA_DECISION, output=SCHEMA_OUTLINE,
        inputs=local_bindings(PLACEHOLDERS_DECISION), outputs=PLACEHOLDERS_OUTLINE,
    )],
)
write_file_process = Process(
    id="write-file", name="Write file", input=SCHEMA_OUTLINE, output=SCHEMA_FILE,
    steps=[ACT(
        "Implement <STEP> for <GOAL> and <CHECK>; produce <FILE_PATH> and complete Python <CODE>.",
        input=SCHEMA_OUTLINE, output=SCHEMA_FILE,
        inputs=local_bindings(PLACEHOLDERS_OUTLINE), outputs=PLACEHOLDERS_FILE,
    )],
)
prepare_change_process = Process(
    id="prepare-change", name="Prepare change", input=SCHEMA_REQUEST,
    steps=[
        Call(process=PROCESS_COMPARE_OPTIONS, inputs=local_bindings([PLACEHOLDER_REQUEST]), outputs=PLACEHOLDERS_COMPARISON),
        Emit(interface=INTERFACE_COMPARISON),
        Call(process=PROCESS_DECIDE_CHANGE, inputs=local_bindings(PLACEHOLDERS_COMPARISON), outputs=PLACEHOLDERS_DECISION),
        Emit(interface=INTERFACE_DECISION),
        Call(process=PROCESS_PLAN_CHANGE, inputs=local_bindings(PLACEHOLDERS_DECISION), outputs=PLACEHOLDERS_OUTLINE),
        Emit(interface=INTERFACE_OUTLINE),
        Call(process=PROCESS_WRITE_FILE, inputs=local_bindings(PLACEHOLDERS_OUTLINE), outputs=PLACEHOLDERS_FILE),
        Emit(interface=INTERFACE_FILE),
    ],
)
change_requested_trigger = Trigger(
    id="change-requested", event="A small code change needs explanation.",
    source=INTERFACE_REQUEST, process=PROCESS_PREPARE_CHANGE,
)
request_interface = Interface(id="request", flow="receives", schema=SCHEMA_REQUEST)
comparison_interface = Interface(id="comparison", flow="emits", schema=SCHEMA_COMPARISON)
decision_interface = Interface(id="decision", flow="emits", schema=SCHEMA_DECISION)
outline_interface = Interface(id="outline", flow="emits", schema=SCHEMA_OUTLINE)
file_interface = Interface(id="file", flow="emits", schema=SCHEMA_FILE)

shape_writer_node = Node(
    instructions=[Instruction(id="keep-scope", body="Keep the proposed change limited to the supplied request.")],
    schemas=[change_request_schema],
    triggers=[change_requested_trigger],
    processes=[compare_options_process, decide_change_process, plan_change_process, write_file_process, prepare_change_process],
    interfaces=[request_interface, comparison_interface, decision_interface, outline_interface, file_interface],
)


def documents() -> dict[str, str]:
    """Supply only the exact authored document dependency, without scanning."""
    return {"examples/schemas/shape_gallery.oak.md": render(shape_gallery_node)}


def fixture_host(action: Act, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
    """Return the next shape only for this explicitly supported fixture."""
    inputs = ({PLACEHOLDER_REQUEST: SAMPLE_REQUEST}, *[SAMPLE_BINDINGS[schema.id] for schema in SHAPES[:-1]])
    for schema, expected in zip(SHAPES, inputs, strict=True):
        if action.output == f"../schemas/shape_gallery.oak.md#schema.{schema.id}":
            if dict(values) != expected:
                raise ValueError("this demonstration host only implements the declared sample")
            return dict(SAMPLE_BINDINGS[schema.id])
    raise ValueError("unexpected demonstration action")


def run() -> tuple[str, ...]:
    """Execute the real OAK pipeline, then present its four validated emissions."""
    result = execute(
        shape_writer_node,
        Arrival(interface=INTERFACE_REQUEST, values={PLACEHOLDER_REQUEST: SAMPLE_REQUEST}),
        {}, act=fixture_host, source=SOURCE, load=documents().get,
    )
    graph = resolve(shape_writer_node, source=SOURCE, load=documents().get)
    if [item.interface for item in result.emissions] != [
        INTERFACE_COMPARISON, INTERFACE_DECISION, INTERFACE_OUTLINE, INTERFACE_FILE,
    ]:
        raise RuntimeError("shape writer emitted the wrong boundary instances")
    texts = []
    for emission in result.emissions:
        _, interface = graph.entry(graph.root, emission.interface, Interface)
        _, schema = graph.entry(graph.root, interface.schema_id, Schema)
        texts.append(populate_example(schema, emission.values))
    if tuple(texts) != tuple(EXPECTED_INSTANCES[schema.id] for schema in SHAPES):
        raise RuntimeError("shape writer did not preserve the referenced layouts")
    return tuple(texts)


def build() -> str:
    """Render and resolve the real cross-document example in both groupings."""
    for grouping in ("xml", "markdown"):
        text = render(shape_writer_node, grouping=grouping)
        parsed = parse(text)
        resolve(parsed, source=SOURCE, load=documents().get)
        if render(parsed, grouping=grouping) != text:
            raise RuntimeError(f"shape writer did not round-trip through {grouping}")
    return render(shape_writer_node)


def write() -> Path:
    """Write the canonical sibling OAK document."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
    print("\n\n".join(run()))
