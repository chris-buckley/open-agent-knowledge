"""Use the same OAK task through a direct host and an OAK-context host.

Both adapters are deterministic Python demonstrations, not live model calls.
A model integration can consume the same named OAK documents without inventing
another task format. The executor still validates the returned schema instance.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pydantic import JsonValue

from oak import (
    ACT, Act, Arrival, BindingValue, Emit, Instruction, Interface,
    InterpreterContext, LiteralValue, Node, NonEmpty, OneOf, Process, Schema,
    Trigger, Type, ValueBinding, execute, parse, render, resolve, where,
)

SCHEMA_TITLE = "schema.title"
SCHEMA_REVIEW = "schema.review"
PROCESS_REVIEW_TITLE = "process.review-title"
INTERFACE_TITLE_INPUT = "interface.title-input"
INTERFACE_REVIEW_OUTPUT = "interface.review-output"
PLACEHOLDER_TITLE = "TITLE"
PLACEHOLDER_VERDICT = "VERDICT"
PLACEHOLDER_REASON = "REASON"

review_instructions = [Instruction(
    id="review-policy", body="Reject empty or whitespace-only titles; accept other titles without rewriting them.",
)]
title_schema = Schema(
    id="title", name="Title", purpose="Carry a title that may need rejection.", template="Title: <TITLE>",
    where=[where(PLACEHOLDER_TITLE, Type(of="string"), description="the unmodified title to assess")],
)
review_schema = Schema(
    id="review", name="Review", purpose="Carry the title decision and its reason.",
    template="## <VERDICT>\n\n<REASON>",
    where=[
        where(PLACEHOLDER_VERDICT, Type(of="string"), OneOf(values=["accept", "reject"]),
              description="whether the title is acceptable"),
        where(PLACEHOLDER_REASON, Type(of="string"), NonEmpty(), description="the reason for the decision"),
    ],
)
review_title_process = Process(
    id="review-title", name="Review title", input=SCHEMA_TITLE, output=SCHEMA_REVIEW,
    steps=[
        ACT("Assess <TITLE> under the title policy and produce <VERDICT> and <REASON>.",
            input=SCHEMA_TITLE, output=SCHEMA_REVIEW,
            inputs=[ValueBinding(placeholder=PLACEHOLDER_TITLE, value=BindingValue(binding=PLACEHOLDER_TITLE))],
            outputs=[PLACEHOLDER_VERDICT, PLACEHOLDER_REASON]),
        Emit(interface=INTERFACE_REVIEW_OUTPUT),
    ],
)
title_requested_trigger = Trigger(
    id="title-requested", event="A title needs review.", source=INTERFACE_TITLE_INPUT, process=PROCESS_REVIEW_TITLE,
)
title_input_interface = Interface(id="title-input", flow="receives", schema=SCHEMA_TITLE)
review_output_interface = Interface(id="review-output", flow="emits", schema=SCHEMA_REVIEW)

review_node = Node(
    instructions=review_instructions,
    schemas=[title_schema, review_schema],
    triggers=[title_requested_trigger],
    processes=[review_title_process],
    interfaces=[title_input_interface, review_output_interface],
)
TARGET = Path(__file__).with_suffix(".oak.md")


def direct_host(_action: Act, values: Mapping[str, JsonValue]) -> Mapping[str, JsonValue]:
    """Apply this example's title policy through the existing direct callback."""
    title = values[PLACEHOLDER_TITLE]
    if not isinstance(title, str):
        raise TypeError("TITLE must be a string")
    accepted = bool(title.strip())
    return {
        PLACEHOLDER_VERDICT: "accept" if accepted else "reject",
        PLACEHOLDER_REASON: "The title has content." if accepted else "The title is blank.",
    }


def context_host(context: InterpreterContext) -> Mapping[str, JsonValue]:
    """Read the standard OAK invocation instead of another task representation."""
    source = parse(context.documents[context.source])
    if [item.body for item in source.instructions] != [item.body for item in review_instructions]:
        raise ValueError("this demonstration host only implements the supplied title policy")
    invocation = parse(context.documents[context.invocation])
    resolve(invocation, source=context.invocation, load=context.documents.get)
    action = invocation.processes[0].steps[0]
    if not isinstance(action, Act) or any(not isinstance(item.value, LiteralValue) for item in action.inputs):
        raise ValueError("expected one fully bound native ACT")
    return direct_host(action, {item.placeholder: item.value.value for item in action.inputs})


def run() -> None:
    """Check both host adapters against the same unchanged authored node."""
    for title in ("", "   ", "OAK"):
        arrival = Arrival(interface=INTERFACE_TITLE_INPUT, values={PLACEHOLDER_TITLE: title})
        direct = execute(review_node, arrival, {}, act=direct_host)
        contextual = execute(review_node, arrival, {}, interpreter=context_host)
        if direct != contextual:
            raise RuntimeError("host adapters disagreed on the same OAK task")


def build() -> str:
    """Render, parse, resolve, and round-trip the authored task."""
    text = render(review_node)
    parsed = parse(text)
    resolve(parsed)
    if render(parsed) != text:
        raise RuntimeError("interpreter-context example did not round-trip")
    return text


def write() -> Path:
    """Write the canonical sibling snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    run()
    print(f"wrote {write()}")
