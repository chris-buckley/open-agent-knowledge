"""Private stateless trimming work; no public interface or mutable state is needed."""

from pathlib import Path

from oak import ACT, BindingValue, Node, Process, Schema, Type, ValueBinding, parse, render, where

raw_schema = Schema(
    id="raw", purpose="Supply raw text for trimming without interpreting its public use.",
    template="Raw: <RAW_TEXT>", where=[where("RAW_TEXT", Type(of="string"))],
)
trimmed_schema = Schema(
    id="trimmed", purpose="Return trimmed text, including empty or multiline text.",
    template="Trimmed: <CLEAN_TEXT>", where=[where("CLEAN_TEXT", Type(of="string"))],
)
raw_binding = ValueBinding(placeholder="RAW_TEXT", value=BindingValue(binding="RAW_TEXT"))
trim_action = ACT(
    "Remove leading and trailing whitespace from <RAW_TEXT> to produce <CLEAN_TEXT>.",
    input=f"schema.{raw_schema.id}", output=f"schema.{trimmed_schema.id}",
    inputs=[raw_binding], outputs=["CLEAN_TEXT"],
)
trim_process = Process(
    id="trim", name="Trim text", input=f"schema.{raw_schema.id}", output=f"schema.{trimmed_schema.id}",
    body=[trim_action],
)
worker_node = Node(schemas=[raw_schema, trimmed_schema], processes=[trim_process])
TARGET = Path(__file__).with_suffix(".oak.md")


def build() -> str:
    text = render(worker_node)
    if render(parse(text)) != text:
        raise RuntimeError("private worker did not round-trip")
    return text


def write() -> Path:
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET
