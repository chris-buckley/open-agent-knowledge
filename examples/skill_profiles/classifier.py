"""A reusable stateless operation with explicit supplied policy and no file effects."""

from pathlib import Path

from oak import ACT, BindingValue, Node, NonEmpty, OneOf, Process, Schema, Type, ValueBinding, parse, render, where

item_schema = Schema(
    id="item", purpose="Classify supplied text against one supplied term.",
    template="Text: <TEXT>\nTerm: <TERM>",
    where=[where("TEXT", Type(of="string"), NonEmpty()), where("TERM", Type(of="string"), NonEmpty())],
)
category_schema = Schema(
    id="category", purpose="Return whether the supplied term occurs in the text.", template="Category: <CATEGORY>",
    where=[where("CATEGORY", Type(of="string"), OneOf(values=["match", "other"]))],
)
classify_action = ACT(
    "Classify <TEXT> as match when it contains <TERM> case-insensitively, otherwise other. Return <CATEGORY> without reading or writing files.",
    input="schema.item", output="schema.category",
    inputs=[ValueBinding(placeholder=name, value=BindingValue(binding=name)) for name in ("TEXT", "TERM")],
    outputs=["CATEGORY"],
)
classify_process = Process(
    id="classify", name="Classify item", input="schema.item", output="schema.category", body=[classify_action],
)
classifier_node = Node(schemas=[item_schema, category_schema], processes=[classify_process])
TARGET = Path(__file__).with_suffix(".oak.md")


def build() -> str:
    text = render(classifier_node)
    if render(parse(text)) != text:
        raise RuntimeError("classifier changed during rendering")
    return text


def write() -> Path:
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET
