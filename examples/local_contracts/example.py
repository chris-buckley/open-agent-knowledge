"""Local public contracts adapt to explicit private work, not a schema alias.

Run python -m examples.local_contracts.example in the repository, or python
example.py in a copied scenario with OAK installed. The Python host trims text
only: no live model, persistence, transport, or external side effect is claimed.
The whole scenario is self-contained knowledge; example.oak.md alone still needs
worker.oak.md to execute, despite explaining its public boundaries locally.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if (ROOT / "oak").is_dir() and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pydantic import JsonValue
from oak import (
    Act, Arrival, BindingValue, Call, Constant, Emit, ExecutionError, Interface,
    Node, NonEmpty, Lines, Process, Schema, Trigger, Type, ValueBinding,
    execute, parse, render, resolve, where,
)

if __package__:
    from . import worker
else:
    import worker

boundary_constant = Constant(
    id="delivery-boundary",
    value="Public schemas are local. Execution needs worker.oak.md and a trimming host; the complete scenario supplies both as a deterministic demonstration.",
)
text_schema = Schema(
    id="text", purpose="Supply text to turn into a nonempty single-line title.", template="Text: <TEXT>",
    where=[where("TEXT", Type(of="string"), description="text whose outer whitespace will be removed")],
)
title_schema = Schema(
    id="title", purpose="Publish a title only after the public title constraints pass.", template="# <TITLE>",
    where=[where("TITLE", Type(of="string"), NonEmpty(), Lines(max=1), description="the trimmed nonempty single-line title")],
)
raw_binding = ValueBinding(placeholder="RAW_TEXT", value=BindingValue(binding="TEXT"))
title_binding = ValueBinding(placeholder="TITLE", value=BindingValue(binding="CLEAN_TEXT"))
trim_call = Call(process="worker.oak.md#process.trim", inputs=[raw_binding], outputs=["CLEAN_TEXT"])
emit_title = Emit(interface="interface.title-result", bindings=[title_binding])
make_title_process = Process(
    id="make-title", name="Make title", input=f"schema.{text_schema.id}", body=[trim_call, emit_title],
)
text_received_trigger = Trigger(
    id="text-received", event="A title is requested from supplied text.",
    source="interface.title-request", process=f"process.{make_title_process.id}",
)
title_request_interface = Interface(
    id="title-request", flow="receives", schema=f"schema.{text_schema.id}",
    description="Request a trimmed title, not document publication. Blank or multiline results fail without emission.",
)
title_result_interface = Interface(
    id="title-result", flow="emits", schema=f"schema.{title_schema.id}",
    description="Return the validated title to the requester. Emission does not prove host delivery.",
)
title_node = Node(
    constants=[boundary_constant], schemas=[text_schema, title_schema],
    triggers=[text_received_trigger], processes=[make_title_process],
    interfaces=[title_request_interface, title_result_interface],
)
TARGET = Path(__file__).with_suffix(".oak.md")


def demonstration_host(action: Act, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
    if action.instruction != worker.trim_action.instruction:
        raise ValueError("this fixture only implements the declared trimming action")
    raw = values["RAW_TEXT"]
    if not isinstance(raw, str):
        raise TypeError("RAW_TEXT must be a string")
    return {"CLEAN_TEXT": raw.strip()}


def sample() -> Node:
    return Node(constants=[
        Constant(id="request", value={"TEXT": "  Local contracts  "}),
        Constant(id="expected", value={"TITLE": "Local contracts"}),
        Constant(id="host-disclosure", value="Deterministic trimming only; no live model or external delivery."),
    ])


def build() -> str:
    for grouping in ("xml", "markdown"):
        text = render(title_node, grouping=grouping)
        documents = {"example.oak.md": text, "worker.oak.md": render(worker.worker_node, grouping=grouping)}
        parsed = parse(text)
        resolve(parsed, source="example.oak.md", load=documents.get)
        if render(parsed, grouping=grouping) != text:
            raise RuntimeError("public title document did not round-trip")
    return render(title_node)


def run() -> None:
    documents = {name: (TARGET.parent / name).read_text(encoding="utf-8")
                 for name in ("example.oak.md", "worker.oak.md")}
    node = parse(documents["example.oak.md"])
    result = execute(node, Arrival(interface="interface.title-request", values={"TEXT": "  Local contracts  "}), {},
                     source="example.oak.md", load=documents.get, act=demonstration_host)
    if len(result.emissions) != 1 or result.emissions[0].values != {"TITLE": "Local contracts"}:
        raise RuntimeError("public/private title adaptation failed")
    for text in ("   ", "two\nlines"):
        try:
            execute(node, Arrival(interface="interface.title-request", values={"TEXT": text}), {},
                    source="example.oak.md", load=documents.get, act=demonstration_host)
        except ExecutionError:
            continue
        raise RuntimeError("a private-valid result bypassed the public title contract")


def write() -> Path:
    worker.write()
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    TARGET.parent.joinpath("sample.oak.md").write_text(render(sample()), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    write()
    run()
    print("Verified local title contracts and private worker adaptation.")
