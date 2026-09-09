"""Indexed-memory contracts shared by the synthetic stateful package."""

from pathlib import Path

from oak import Constant, Node, NonEmpty, OneOf, Schema, Type, parse, render, where
from build.skill_template import MEMORY_RULES

configuration_schema = Schema(
    id="configuration", purpose="Identify one instance and its saved decision for future records.",
    template='{"version": <VERSION>, "owner": "<OWNER>", "capability": "<CAPABILITY>", "retention": "<MODE>"}',
    where=[where("VERSION", Type(of="integer"), OneOf(values=[1])),
           where("OWNER", Type(of="string"), NonEmpty()), where("CAPABILITY", Type(of="string"), NonEmpty()),
           where("MODE", Type(of="string"), OneOf(values=["full", "summary"]))],
)
index_row_schema = Schema(
    id="index-row", purpose="Name one authoritative record using containing-index-relative resolution.",
    template="id,name,reference\n<ID>,<NAME>,<REFERENCE>",
    where=[where(name, Type(of="string"), NonEmpty()) for name in ("ID", "NAME", "REFERENCE")],
)
policy_schema = Schema(
    id="policy", purpose="Validate one agent-owned synthetic policy record before applying it.",
    template='{"version": <VERSION>, "owner": "<OWNER>", "capability": "<CAPABILITY>", "id": "<ID>", "writer": "<WRITER>", "term": "<TERM>"}',
    where=[where("VERSION", Type(of="integer"), OneOf(values=[1])),
           *[where(name, Type(of="string"), NonEmpty()) for name in ("OWNER", "CAPABILITY", "ID", "TERM")],
           where("WRITER", Type(of="string"), OneOf(values=["agent"]))],
)
memory_node = Node(constants=[
    Constant(id="workflow", form="yaml", value=list(MEMORY_RULES)),
    Constant(id="record-contract", value=(
        "History records are JSON with version=1, owner, capability, id, writer=agent, category, instance-relative policy reference, "
        "policy_sha256, source_sha256 and mode. Full also retains source text. A policy record has version=1, "
        "owner, capability, id, writer=agent and term. State/runs records contain pending OAK checkpoints; "
        "records marked writer=tool are protected. These are example contracts, not OAK datatypes.")),
    Constant(id="recovery", value=(
        "Keep the pending checkpoint after failure. Compare the prepared source/index identities before writing. "
        "An exact orphan record may receive its missing index entry. An exact already-published pair needs "
        "read-back only. A differing record, index row, policy or writer must stop without a success result. "
        "Persist successfully returned OAK state before acknowledging progress.")),
], schemas=[configuration_schema, index_row_schema, policy_schema])
TARGET = Path(__file__).with_suffix(".oak.md")


def build() -> str:
    text = render(memory_node)
    if render(parse(text)) != text:
        raise RuntimeError("memory contracts changed during rendering")
    return text


def write() -> Path:
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET
