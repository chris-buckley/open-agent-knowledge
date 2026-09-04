"""Derived interpreter context, expressed only as canonical OAK documents."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
import posixpath
from types import MappingProxyType

from pydantic import JsonValue

from oak.node.model import Node
from oak.node.parts.processes.model import Process
from oak.node.parts.processes.steps import Act, iter_steps
from oak.node.parts.processes.values import LiteralValue, ValueBinding
from oak.node.parts.schemas.model import Schema
from oak.render.selection import render
from oak.resolve.graph import ResolvedGraph
from oak.resolve.references import iter_targets
from oak.vocabulary.text.target_path import split_target


@dataclass(frozen=True, slots=True)
class InterpreterContext:
    """A detached OAK invocation and its source documents, not a new format.

    ``invocation`` selects the generated document. It contains exactly one
    process and one native ACT, with literal inputs and resolved schema paths.
    ``source`` and ``process`` identify the original action's document and
    root-relative process. ``documents`` maps exact paths to canonical OAK.
    Source document boundaries and policy scopes remain distinct. Interpret
    the invocation under the source document instructions; local references in
    those instructions still belong to the source. Do not execute other supplied
    processes or treat the generated request as an import or policy override.
    """

    source: str
    process: str
    invocation: str
    documents: Mapping[str, str]


def _document_closure(graph: ResolvedGraph, sources: Sequence[str]) -> set[str]:
    """Keep whole documents, including all their explicit dependencies."""
    selected: set[str] = set()
    pending = list(sources)
    while pending:
        source = pending.pop()
        if source in selected:
            continue
        if source not in graph.documents:
            raise ValueError(f"context document is not in the resolved graph: {source}")
        selected.add(source)
        for target, expected in iter_targets(graph.documents[source]):
            document, _entry = graph.entry(source, target, expected)
            if document not in selected:
                pending.append(document)
    return selected


def task_context(
    graph: ResolvedGraph,
    process: str | None = None,
    *,
    retain: Sequence[str] = (),
) -> Mapping[str, str]:
    """Render a conservative task view without altering the execution graph.

    With no process, keep the complete graph. An explicit root-relative process
    selects its whole owning document and every transitive document dependency.
    Never prune individual entries: prose may depend on them. ``retain`` names
    additional exact graph document paths required by host-known prose context.
    Keep the full-graph default when those dependencies are not known. Documents
    are not merged or rebased, and this function never loads or scans files.
    """
    if process is None:
        sources = tuple(graph.documents)
    else:
        if split_target(process)[1] != "process":
            raise ValueError("task context requires a process target")
        source, _process = graph.entry(graph.root, process, Process)
        sources = (source,)
    selected = _document_closure(graph, (*sources, *retain))
    return MappingProxyType({
        source: render(graph.documents[source])
        for source in sorted(selected)
    })


def _state_snapshot(
    graph: ResolvedGraph,
    state: Mapping[str, JsonValue] | None,
) -> dict[str, Node]:
    """Copy document meaning and optionally substitute the current OAK state."""
    expected = {
        graph.display_target(source, "state", entry.id)
        for source, node in graph.documents.items()
        for entry in node.state
    }
    if state is not None and set(state) != expected:
        raise ValueError("context state must contain exactly the resolved graph state")
    documents: dict[str, Node] = {}
    for source, node in graph.documents.items():
        data = deepcopy(node.model_dump(mode="python", by_alias=True))
        if state is not None:
            for entry, value in zip(node.state, data["state"], strict=True):
                key = graph.display_target(source, "state", entry.id)
                value["value"] = deepcopy(state[key])
                if entry.schema_id is not None:
                    _document, schema = graph.entry(source, entry.schema_id, Schema)
                    schema.bind_value(entry.placeholder, value["value"])
        documents[source] = Node.model_validate(data)
    return documents


def build_interpreter_context(
    graph: ResolvedGraph,
    process: str,
    step: Act,
    values: Mapping[str, JsonValue],
    *,
    state: Mapping[str, JsonValue] | None = None,
) -> InterpreterContext:
    """Derive one native action request using only existing OAK models.

    The full graph is retained because action prose cannot prove that another
    document is irrelevant. Values are copied into literal bindings, source
    instructions stay in their original scope, and schema targets resolve to their original
    document identities. State is the current transaction snapshot when supplied,
    or the authored initial state otherwise. No host code or model is invoked.
    """
    if split_target(process)[1] != "process":
        raise ValueError("interpreter context requires a process target")
    source, owner = graph.entry(graph.root, process, Process)
    if step.tool is not None:
        raise ValueError("interpreter context requires a native ACT")
    if not any(candidate == step for candidate in iter_steps(owner.steps)):
        raise ValueError("the action does not belong to the selected process")
    if set(values) != {binding.placeholder for binding in step.inputs}:
        raise ValueError("context values must match the action inputs exactly")
    if step.input is not None:
        _document, schema = graph.entry(source, step.input, Schema)
        schema.bind(values)

    documents = _state_snapshot(graph, state)
    directory = posixpath.dirname(source)
    invocation = posixpath.join(directory, "__invocation__.oak.md")
    index = 1
    while invocation in documents:
        invocation = posixpath.join(directory, f"__invocation_{index}__.oak.md")
        index += 1

    def schema_target(target: str | None) -> str | None:
        if target is None:
            return None
        document, schema = graph.entry(source, target, Schema)
        relative = posixpath.relpath(document, directory or ".")
        return f"{relative}#schema.{schema.id}"

    action = Act(
        instruction=step.instruction,
        input=schema_target(step.input),
        output=schema_target(step.output),
        inputs=[
            ValueBinding(
                placeholder=binding.placeholder,
                value=LiteralValue(value=deepcopy(values[binding.placeholder])),
            )
            for binding in step.inputs
        ],
        outputs=list(step.outputs),
    )
    documents[invocation] = Node(
        processes=[Process(
            id="invoke-action",
            name="Invoke action",
            output=action.output,
            steps=[action],
        )],
    )
    return InterpreterContext(
        source=source,
        process=process,
        invocation=invocation,
        documents=MappingProxyType({
            path: render(node) for path, node in sorted(documents.items())
        }),
    )


__all__ = ["InterpreterContext", "build_interpreter_context", "task_context"]
