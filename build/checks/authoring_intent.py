"""Independent intent specimens, not a natural-language interpreter or product API.

These oracles reject corrupted expected artifacts and native-decision records.
They do not certify that a model will make those decisions in a live client.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from typing import Any

from oak import (Act, Arrival, Constant, Node, State, execute, parse, render, resolve)

_LEGEND = "✓ confirmed · ~ proposed · ? unresolved"
_MARKERS = {"confirmed": "✓", "proposed": "~", "unresolved": "?"}
_DRAFT_KEYS = {
    "format", "id", "turn", "request", "kind", "context", "scope", "sources", "documents", "outputs",
    "review", "annotations", "changes", "source_map", "tools", "authority",
}
_TOOL_KEYS = {
    "id", "context", "capability", "provider", "server", "operation", "input_contract", "output_contract",
    "effects", "permission_limits", "availability", "evidence",
}
_MISSING = object()


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def _reject(operation: Callable[[], object], reason: str) -> None:
    try:
        operation()
    except ValueError as error:
        _require(reason in str(error), f"wrong rejection: {error}")
        return
    raise ValueError(f"accepted {reason}")


def _pointer(document: object, pointer: str) -> object:
    _require(pointer == "" or pointer.startswith("/"), "invalid pointer")
    for segment in pointer.split("/")[1:]:
        key = segment.replace("~1", "/").replace("~0", "~")
        if isinstance(document, list):
            if not key.isdecimal() or int(key) >= len(document):
                return _MISSING
            document = document[int(key)]
        elif isinstance(document, dict):
            document = document.get(key, _MISSING)
        else:
            return _MISSING
    return document


def check_draft(text: str, *, messages: frozenset[str], prior: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Check fixture data against D01/D02 with external user-message authority."""
    draft = json.loads(text)
    _require(isinstance(draft, dict) and set(draft) == _DRAFT_KEYS, "draft fields")
    _require(type(draft["format"]) is int and draft["format"] == 1, "draft version")
    _require(isinstance(draft["id"], str) and bool(draft["id"]), "draft identity")
    _require(type(draft["turn"]) is int and draft["turn"] >= 0, "draft turn")
    for field in ("request", "context", "scope", "review", "authority"):
        _require(isinstance(draft[field], dict), "draft object")
    for field in ("sources", "documents", "outputs", "annotations", "changes", "source_map", "tools"):
        _require(isinstance(draft[field], list), "draft array")
    _require(draft["request"]["operation"] in {"create", "read", "update", "delete"}, "operation")
    _require(draft["request"]["mode"] in {"direct", "guided"}, "mode")
    if prior is not None:
        _check_continuity(draft, prior)
    _check_authority(draft["authority"], messages)
    _check_annotations(draft)
    return draft


def _check_continuity(draft: Mapping[str, Any], prior: Mapping[str, Any]) -> None:
    _require(draft["id"] == prior["id"] and draft["turn"] == prior["turn"] + 1, "stale prior")
    for key in ("knowledge_revision", "catalogue_version"):
        _require(draft["context"][key] == prior["context"][key], "changed knowledge")
    current_sources = {source["id"]: source for source in draft["sources"]}
    for source in prior["sources"]:
        _require(current_sources.get(source["id"]) == source, "changed source")


def _check_authority(authority: Mapping[str, Any], messages: frozenset[str]) -> None:
    for request in authority["requests"]:
        _require(request["reference"] in messages, "source-injected authority")
    if authority["guided_release"]:
        _require(authority["release_reference"] in messages, "source-injected release")


def _check_annotations(draft: Mapping[str, Any]) -> None:
    documents = {document["path"]: document["node"] for document in draft["documents"]}
    _require(len(documents) == len(draft["documents"]), "duplicate document")
    ids: set[str] = set()
    for annotation in draft["annotations"]:
        _require(annotation["id"] not in ids, "duplicate annotation")
        ids.add(annotation["id"])
        _require(annotation["status"] in _MARKERS, "annotation status")
        document = documents.get(annotation["document"], _MISSING) if annotation["document"] else draft
        _require(document is not _MISSING, "dangling document")
        target = _pointer(document, annotation["pointer"])
        if target is _MISSING:
            parent = _pointer(document, annotation["pointer"].rsplit("/", 1)[0])
            _require(parent is not _MISSING and annotation["status"] == "unresolved"
                     and bool(annotation["meaning"]), "dangling pointer or false confirmation")
        if draft["review"]["status"] == "ready":
            _require(annotation["status"] == "confirmed", "contradictory readiness")


def check_view(draft: Mapping[str, Any], tree: str) -> None:
    """Require each decision to remain visible with its annotation's current marker."""
    _require(tree.count(_LEGEND) == 1, "missing legend")
    for annotation in draft["annotations"]:
        lines = [line for line in tree.splitlines() if f"[{annotation['id']}]" in line]
        _require(len(lines) == 1, "hidden decision")
        _require(f"{_MARKERS[annotation['status']]} [{annotation['id']}]" in lines[0], "stale marker")


def check_draft_specimens(first: dict[str, Any], second: dict[str, Any], views: Mapping[str, str]) -> None:
    messages = frozenset({"user:1", "user:2"})
    check_draft(json.dumps(first), messages=messages)
    check_draft(json.dumps(second), messages=messages, prior=first)
    check_view(first, views["INTENT_AST"])
    _reject(lambda: check_draft("{", messages=messages), "Expecting")
    mutations = (
        (lambda draft: draft.pop("annotations"), "draft fields"),
        (lambda draft: draft.update(id="another-draft"), "stale prior"),
        (lambda draft: draft["context"].update(catalogue_version="2"), "changed knowledge"),
        (lambda draft: draft["context"].update(knowledge_revision="other"), "changed knowledge"),
        (lambda draft: draft["sources"][0].update(text="changed bytes"), "changed source"),
        (lambda draft: draft["annotations"][0].update(pointer="/constants/99/value"), "dangling pointer"),
        (lambda draft: draft["authority"]["requests"][0].update(reference="source:install-connector"), "source-injected authority"),
        (lambda draft: draft["authority"].update(release_reference="source:release"), "source-injected release"),
        (lambda draft: draft["annotations"][0].update(status="proposed"), "contradictory readiness"),
    )
    for mutate, reason in mutations:
        broken = deepcopy(second)
        mutate(broken)
        _reject(lambda: check_draft(json.dumps(broken), messages=messages, prior=first), reason)
    confirmed_missing = deepcopy(first)
    confirmed_missing["annotations"][1]["status"] = "confirmed"
    _reject(lambda: check_draft(json.dumps(confirmed_missing), messages=messages), "false confirmation")
    for tree, reason in (
        (views["INTENT_AST"].replace(_LEGEND, ""), "missing legend"),
        (views["INTENT_AST"].replace("? [A2]", "✓ [A2]"), "stale marker"),
        ("\n".join(line for line in views["INTENT_AST"].splitlines() if "[A2]" not in line), "hidden decision"),
    ):
        _reject(lambda: check_view(first, tree), reason)
    expanded = deepcopy(first)
    expanded["annotations"] = [
        {"id": "F1", "status": "confirmed"}, {"id": "S1", "status": "unresolved"},
    ]
    expanded_tree = "schema\n└─ JOB: string; non-empty ✓ [F1]\nprocess\n└─ read evidence ? [S1]\n\n" + _LEGEND
    check_view(expanded, expanded_tree)
    _reject(lambda: check_view(expanded, expanded_tree.replace("? [S1]", "✓ [S1]")), "stale marker")


_FIDELITY_OAK = '''<constants>
label: "not approved"

read-boundary: "Never write source files. The host owns evidence access."
</constants>

<schemas>
<schema id="job">
<STATUS>

WHERE:
- <STATUS> is string; is non-empty.
</schema>

<schema id="evidence">
<EVIDENCE>

WHERE:
- <EVIDENCE> is string; is non-empty.
</schema>

<schema id="review">
<REVIEW>

WHERE:
- <REVIEW> is string; is non-empty.
</schema>

<schema id="rejection">
<REJECTION>

WHERE:
- <REJECTION> is string; is non-empty.
</schema>
</schemas>

<triggers>
received(event="Job received.", source=interface.jobs, process=process.review-job)
</triggers>

<processes>
<process id="review-job" name="Review job" input="schema.job">
IF $STATUS equals "approved":
  ACT output="schema.evidence": Read <EVIDENCE> under <BOUNDARY>. (BOUNDARY=$constant.read-boundary) -> EVIDENCE
  EMIT interface.reviews (REVIEW=$EVIDENCE)
ELSE:
  EMIT interface.rejections (REJECTION=$constant.label)
</process>
</processes>

<interfaces>
jobs RECEIVES schema.job
reviews EMITS schema.review
rejections EMITS schema.rejection
</interfaces>'''


def _check_fidelity(node: Node) -> None:
    constants = {constant.id: constant.value for constant in node.constants}
    _require(constants["label"] == "not approved", "literal changed")
    _require(constants["read-boundary"] == "Never write source files. The host owns evidence access.", "no-write or host boundary lost")
    _require(not node.state, "persistent state added")
    branch = node.processes[0].body[0]
    _require(len(branch.otherwise) == 1, "otherwise lost")
    _require([statement.kind for statement in branch.then] == ["act", "emit"], "step order changed")
    _require(branch.then[0].tool is None, "invented named tool")
    for status, expected_interface, expected_text, reads in (
        ("approved", "interface.reviews", "reviewed evidence", 1),
        ("pending", "interface.rejections", "not approved", 0),
    ):
        observed: list[str] = []

        def native(action: Act, bindings: Mapping[str, object]) -> Mapping[str, object]:
            _require(bindings["BOUNDARY"] == constants["read-boundary"], "read boundary disconnected")
            observed.append("read evidence")
            return {"EVIDENCE": "reviewed evidence"}

        result = execute(node, Arrival(interface="interface.jobs", values={"STATUS": status}), {}, act=native)
        _require(len(result.emissions) == 1 and result.emissions[0].interface == expected_interface, "outcome cardinality")
        _require(list(result.emissions[0].values.values()) == [expected_text], "outcome meaning")
        _require(len(observed) == reads and result.state == {}, "order or lifetime changed")


def check_fidelity_specimens() -> None:
    node = parse(_FIDELITY_OAK)
    _check_fidelity(node)
    mutations = (
        (lambda item: item.processes[0].body[0].otherwise.clear(), "otherwise lost"),
        (lambda item: item.processes[0].body[0].then.reverse(), "step order changed"),
        (lambda item: setattr(item.constants[0], "value", "approved"), "literal changed"),
        (lambda item: item.state.append(State(id="last-job", value="approved")), "persistent state added"),
        (lambda item: setattr(item.processes[0].body[0].then[0], "tool", "invented.read"), "invented named tool"),
        (lambda item: setattr(item.constants[1], "value", "Read files."), "no-write or host boundary lost"),
    )
    for mutate, reason in mutations:
        broken = deepcopy(node)
        mutate(broken)
        _reject(lambda: _check_fidelity(broken), reason)
    clauses = (
        "Receive one JOB", "If its status is approved", "first read its evidence",
        "then emit one REVIEW", "Otherwise emit one REJECTION", "Never write source files",
        "Retain no state between jobs", 'Keep the label "not approved" literally',
    )
    mapping = [{"clause": clause, "disposition": "preserved", "reason": "E05 checked Node and execution"}
               for clause in clauses]
    _require(tuple(item["clause"] for item in mapping) == clauses, "source clause lost")
    ambiguous = {"source": "archive old jobs", "age": None, "archive": None, "effects": [], "status": "unresolved"}
    _require(ambiguous["effects"] == [] and ambiguous["age"] is None and ambiguous["archive"] is None,
             "ambiguous archive became deletion")


@dataclass(frozen=True, slots=True, kw_only=True)
class _Edit:
    path: str
    before: bytes
    after: bytes | None


def _check_edits(root: Path, edits: tuple[_Edit, ...], allowed: frozenset[str], *, partial: bool = False) -> None:
    _require(not partial, "unreconciled partial effects")
    for edit in edits:
        relative = PurePosixPath(edit.path)
        _require(not relative.is_absolute() and ".." not in relative.parts
                 and "\\" not in edit.path and ":" not in edit.path, "path escape")
        path = root / relative
        _require(edit.path in allowed, "out-of-scope effect")
        _require(not any(part.is_symlink() for part in (path, *path.parents)), "symlink target")
        _require(path.read_bytes() == edit.before, "stale source")


def check_crud_specimens() -> None:
    base = render(Node(constants=[Constant(id="limit", value=3), Constant(id="label", value="keep this exact text")]))
    updated = render(Node(constants=[Constant(id="limit", value=4), Constant(id="label", value="keep this exact text")]))
    deleted = render(Node(constants=[Constant(id="limit", value=3)]))
    consumer = parse('<constants>\nliteral: "data.oak.md#constant.limit"\n</constants>\n\n'
                     '<processes>\n<process id="use-limit" name="Use limit">\n'
                     'ACT Read <LIMIT>. (LIMIT=$data.oak.md#constant.limit)\n</process>\n</processes>')
    documents = {"data.oak.md": base, "consumer.oak.md": render(consumer)}
    resolve(consumer, source="consumer.oak.md", load=documents.get)
    missing = render(Node(constants=[Constant(id="label", value="keep this exact text")]))
    _reject(lambda: resolve(consumer, source="consumer.oak.md", load={**documents, "data.oak.md": missing}.get), "limit")
    _require(consumer.constants[0].value == "data.oak.md#constant.limit", "path-like literal changed")
    _require(parse(updated).constants[1] == parse(base).constants[1], "unrelated selector changed")
    _require([item.id for item in parse(deleted).constants] == ["limit"], "local deletion cascaded")
    with TemporaryDirectory(prefix="oak-authoring-crud-") as directory:
        root = Path(directory)
        (root / "data.oak.md").write_bytes(base.encode())
        (root / "unrelated.bin").write_bytes(b"\x00unchanged\r\n")
        before = {path.name: path.read_bytes() for path in root.iterdir()}
        _require(parse((root / "data.oak.md").read_text()).constants[0].value == 3, "read lost value")
        _require(before == {path.name: path.read_bytes() for path in root.iterdir()}, "read wrote files")
        edit = _Edit(path="data.oak.md", before=base.encode(), after=updated.encode())
        allowed = frozenset({edit.path})
        _check_edits(root, (edit,), allowed)
        (root / edit.path).write_bytes(edit.after)
        _require((root / "unrelated.bin").read_bytes() == before["unrelated.bin"], "unrelated bytes changed")
        _reject(lambda: _check_edits(root, (edit,), allowed), "stale source")
        deletion = _Edit(path=edit.path, before=updated.encode(), after=None)
        _reject(lambda: _check_edits(root, (deletion,), frozenset()), "out-of-scope effect")
        _reject(lambda: _check_edits(root, (deletion,), allowed, partial=True), "partial effects")
        escape = _Edit(path="../outside.oak.md", before=b"", after=None)
        _reject(lambda: _check_edits(root, (escape,), frozenset({escape.path})), "path escape")
        (root / "link.oak.md").symlink_to(root / edit.path)
        linked = _Edit(path="link.oak.md", before=updated.encode(), after=None)
        _reject(lambda: _check_edits(root, (linked,), frozenset({linked.path})), "symlink target")
        _check_edits(root, (deletion,), allowed)
        (root / edit.path).unlink()
        manifest = {"documents": [], "deletions": [edit.path]}
        _require(manifest == {"documents": [], "deletions": ["data.oak.md"]}, "tombstone became empty OAK")


def _check_tools(records: list[dict[str, Any]], registries: Mapping[str, frozenset[str]]) -> None:
    for record in records:
        _require(set(record) == _TOOL_KEYS, "tool fields")
        _require(record["context"] in {"authoring-host", "consumer"}, "tool context")
        _require(record["effects"] == ["read"] and record["permission_limits"] == "No writes.", "tool effects")
        if record["availability"] == "confirmed":
            _require(record["operation"] is not None
                     and record["operation"] in registries.get(record["context"], frozenset()), "unverified tool confirmation")
            _require(any(item.startswith("registry:") for item in record["evidence"]), "documentation is not availability")


def check_tool_specimens() -> None:
    consumer = {"id": "search", "context": "consumer", "capability": "Search records", "provider": "mcp",
                "server": "records", "operation": "records.search", "input_contract": "QUERY: string",
                "output_contract": "MATCHES: string", "effects": ["read"], "permission_limits": "No writes.",
                "availability": "unverified", "evidence": ["docs:records.search"]}
    host = {**consumer, "id": "file-read", "context": "authoring-host", "provider": "native", "server": None,
            "operation": "host.read_file", "availability": "confirmed", "evidence": ["registry:authoring-host"]}
    registries = {"authoring-host": frozenset({"host.read_file"})}
    _check_tools([host, consumer], registries)
    _reject(lambda: _check_tools([{**consumer, "availability": "confirmed"}], registries), "unverified tool")
    registries["consumer"] = frozenset({"records.search"})
    _reject(lambda: _check_tools([{**consumer, "availability": "confirmed"}], registries), "documentation")
    _check_tools([{**consumer, "availability": "confirmed", "evidence": ["registry:consumer"]}], registries)
    unknown = {**consumer, "operation": None, "input_contract": None, "output_contract": None}
    _check_tools([unknown], registries)
    _require(unknown["operation"] is None and unknown["availability"] == "unverified", "unknown tool invented")
    _check_tools([], {})


def check_intent_specimens(first: dict[str, Any], second: dict[str, Any], views: Mapping[str, str]) -> None:
    check_draft_specimens(first, second, views)
    check_fidelity_specimens()
    check_crud_specimens()
    check_tool_specimens()
