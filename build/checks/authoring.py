"""Shared-source, scope-safe fusion, delivery, and executable parity checks."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory

import yaml
from oak import (ACT, Act, Arrival, Constant, ConstantValue, Emit, Instruction,
                 Interface, Node, Process, Schema, State, Trigger, ValueBinding,
                 execute, parse, render, resolve, Type, where)
from build.authoring import ENTRY, PACKAGE, SCRIPT, TARGET, artifacts, skill_documents, tree, validator_module
from build.authoring_guides import GUIDES, RULE_OWNERS, populated_examples, teaching_examples
from build.fusion import fuse
from build.checks.fixtures import ROOT
from examples.schemas.shape_gallery import EXPECTED_INSTANCES, SHAPES
from oak.rules import AUTHORING_GUIDANCE

SKILL_ENTRY_MAX_BYTES = 10_000
AGENT_MAX_BYTES = 64_000


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rejects(operation, message: str) -> None:
    try:
        operation()
    except (ValueError, RuntimeError):
        return
    raise RuntimeError(message)


def validate_authoring_skill() -> None:
    """Check the actual packaged documents, not an independent prompt fixture."""
    validator = validator_module()
    entry_text = (PACKAGE / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(entry_text.split("---\n", 2)[1])
    require(set(metadata) == {"name", "description", "metadata"}, "nonstandard skill metadata")
    require(metadata["name"] == PACKAGE.name and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata["name"]) is not None, "invalid skill name")
    require(0 < len(metadata["description"]) <= 1024, "invalid skill description")
    require(all(isinstance(value, str) for value in metadata["metadata"].values()), "skill metadata must use string values")
    require(metadata["metadata"]["version"] == validator.SKILL_VERSION, "skill version drift")
    require(metadata["metadata"]["oak-revision"] == validator.REVISION, "skill revision drift")
    require(re.fullmatch(r"[0-9a-f]{40}", validator.REVISION) is not None, "validator is not pinned to a commit")
    require(validator.package_digest(ROOT / "oak") == validator.SOURCE_SHA256, "validator source pin is stale")
    require(hashlib.sha256((ROOT / "pyproject.toml").read_bytes()).hexdigest() == validator.PROJECT_SHA256, "validator dependencies pin is stale")
    require(len(entry_text.encode()) <= SKILL_ENTRY_MAX_BYTES and len(entry_text.splitlines()) <= 500, "skill entry is not focused")
    require(len(TARGET.read_bytes()) <= AGENT_MAX_BYTES, "standalone agent exceeds its reviewed budget")

    expected = artifacts()
    actual_files = {path for path in PACKAGE.rglob("*") if path.is_file() and "__pycache__" not in path.parts}
    require(actual_files == {path for path in expected if path.is_relative_to(PACKAGE)} | {SCRIPT}, "skill layout contains missing or unowned files")
    require(not (PACKAGE / "assets").exists(), "unused skill assets")
    actual = {ENTRY: validator.oak_body(entry_text, PACKAGE / "SKILL.md").rstrip("\n")}
    for name in GUIDES:
        path = f"references/{name}.oak.md"
        actual[path] = (PACKAGE / path).read_text(encoding="utf-8").rstrip("\n")
    require(actual == skill_documents(), "skill knowledge differs from its source")
    fused = tree(actual)
    require(render(fused, grouping="markdown") + "\n" == TARGET.read_text(encoding="utf-8"), "agent is not the exact assembled skill")
    require(len(resolve(fused).documents) == 1, "standalone agent has an external dependency")
    for text in (*actual.values(), render(fused)):
        node = parse(text)
        for grouping in ("xml", "markdown"):
            canonical = render(node, grouping=grouping)
            require(render(parse(canonical), grouping=grouping) == canonical, "fusion changed canonical meaning")
    require(not fused.state, "stateless authoring acquired unjustified state")
    require(len(fused.instructions) == 0 and len(fused.triggers) == 2 and len(fused.interfaces) == 2, "fusion widened policy or arrival scope")
    require(next(c.value for c in fused.constants if c.id.endswith("-validator-script")) + "\n" == SCRIPT.read_text(), "standalone helper drift")
    owners = [key for group in RULE_OWNERS for key in group]
    require(len(set(owners)) == len(owners) and set(owners) == {r.id for r in AUTHORING_GUIDANCE}, "authoring rules lost their single guide owner")
    schema_guide = parse(actual["references/01-schemas.oak.md"])
    require(schema_guide.schemas == list(SHAPES), "shape definitions drifted")
    require(next(c.value for c in schema_guide.constants if c.id == "populated-shapes") == populated_examples(), "populated examples drifted")
    teaching = teaching_examples()
    require(next(c.value for c in fused.constants if c.id.endswith("-teaching")) == teaching,
            "assembled agent lost or changed inert teaching documents")
    for path, example in teaching.items():
        require((PACKAGE / path).read_text() == example + "\n", "teaching example is stale")
        resolve(parse(example), source=path, root=str(PurePosixPath(path).parent), load=teaching.get)
    _teaching_scope(actual, fused, teaching)
    _execution_parity(actual, fused)
    _fusion_rejections()



def _teaching_scope(documents: dict[str, str], fused: Node, teaching: dict[str, str]) -> None:
    """Actual exported files close locally; embedded operational examples stay inert."""
    from build.checks.human_examples import validate_closed_bundle
    from examples.catalog import core
    with TemporaryDirectory(prefix="oak-skill-teaching-") as temporary:
        root = Path(temporary)
        for path in teaching:
            destination = root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((PACKAGE / path).read_bytes())
        for scenario in core():
            validate_closed_bundle(root / "references" / "examples" / scenario.name)
    def unexpected_action(*args):
        raise RuntimeError("an embedded example became active")
    for path, text in teaching.items():
        example = parse(text)
        if example.instructions or example.state or example.triggers or example.processes or example.interfaces:
            rejects(lambda: tree({**documents, "references/unsafe-example.oak.md": text}),
                    "operational teaching was accepted as active fusion knowledge")
        for trigger in example.triggers:
            if trigger.source is None:
                result = execute(fused, Arrival(event=trigger.event), {}, act=unexpected_action)
                require(not result.emissions and not result.state and result.process is None,
                        "embedded example arrival changed authoring behavior")


def _execution_parity(documents: dict[str, str], fused: Node) -> None:
    """Native host fixtures prove dataflow parity, not arbitrary model quality."""
    candidate = teaching_examples()["references/examples/fixed_knowledge/example.oak.md"]
    original = parse(documents[ENTRY])
    scenarios = (
        (False, False, False, "unused"),
        (True, False, False, "passed parse and resolution"),
        (True, True, False, "Programmatic validation was not performed (installation declined)."),
        (True, True, True, "passed parse and resolution after approved installation"),
        (True, False, False, "Programmatic validation was not performed (validator unavailable)."),
    )
    for requested, installation_required, approved, status in scenarios:
        results = []
        traces = []
        for node, source, load in ((original, ENTRY, documents.get), (fused, None, None)):
            trace = []
            def host(action: Act, values):
                trace.append((action.instruction, dict(values), tuple(action.outputs)))
                if action.outputs == ["SOURCE", "VALIDATE"]:
                    return {"SOURCE": "The service is Task board; the title limit is 120.", "VALIDATE": requested}
                if action.outputs == ["INSTALL_REQUIRED", "REPORT"]:
                    return {"INSTALL_REQUIRED": installation_required, "REPORT": status}
                if action.outputs == ["APPROVED"]:
                    return {"APPROVED": approved}
                if action.outputs == ["OAK", "VALIDATION"]:
                    require(values["ALLOW_INSTALL"] == (installation_required and approved), "installation permission was invented")
                    return {"OAK": values["CANDIDATE"], "VALIDATION": status}
                if action.outputs == ["CANDIDATE"]:
                    return {"CANDIDATE": candidate}
                return {name: "fixture design" for name in action.outputs}
            result = execute(node, Arrival(event="OAK authoring is requested for supplied source material."), {}, act=host, source=source, load=load)
            require(len(result.emissions) == 1 and result.emissions[0].values["OAK"] == candidate, "authoring fixture did not deliver one document")
            require(any("HELPER" in values for _, values, _ in trace) == requested, "unrequested validation work ran")
            require(any(outputs == ("APPROVED",) for _, _, outputs in trace) == (requested and installation_required), "consent was not requested at the right boundary")
            if requested and installation_required and not approved:
                require(result.emissions[0].values["VALIDATION"] == status, "declined installation blocked authoring")
                require(not any("ALLOW_INSTALL" in values for _, values, _ in trace), "declined installation reached the installer")
            results.append(result.emissions)
            traces.append(trace)
            typed = execute(node, Arrival(interface="interface.authoring-input", values={"SOURCE": "The service is Task board; the title limit is 120.", "VALIDATE": requested}), {}, act=host, source=source, load=load)
            require(typed.emissions == result.emissions, "typed and natural arrivals differ")
        require(results[0] == results[1] and traces[0] == traces[1], "skill and agent behavior differ")


def _fusion_rejections() -> None:
    schema = Schema(id="message", template="<MSG>", where=[where("MSG", Type(of="string"))])
    # Targets in model fields are rewritten; identical-looking user data is not.
    root = Node(
        constants=[Constant(id="literal", value="shared.oak.md#constant.rules")],
        state=[State(id="remembered", schema="shared.oak.md#schema.message", placeholder="MSG", value="ready")],
        triggers=[Trigger(id="requested", event="Requested.", process="process.respond")],
        processes=[Process(id="respond", name="Respond message", output="shared.oak.md#schema.message", steps=[
            ACT("Use <A> and <B> to produce <MSG>.", output="shared.oak.md#schema.message", inputs=[
                ValueBinding(placeholder="A", value=ConstantValue(constant="shared.oak.md#constant.rules")),
                ValueBinding(placeholder="B", value=ConstantValue(constant="other.oak.md#constant.rules")),
            ], outputs=["MSG"]), Emit(interface="interface.answer")])],
        interfaces=[Interface(id="answer", flow="emits", schema="shared.oak.md#schema.message")],
    )
    shared = Node(constants=[Constant(id="rules", value="first")], schemas=[schema])
    other = Node(constants=[Constant(id="rules", value="second")])
    docs = {"entry.oak.md": render(root), "shared.oak.md": render(shared), "other.oak.md": render(other)}
    fused = fuse(docs, entry="entry.oak.md")
    require(fused.constants[0].value == root.constants[0].value, "literal payload was rewritten")
    require(fused.state[0].schema_id == fused.interfaces[0].schema_id == fused.processes[0].output, "resolved schema identity was not preserved")
    require([c.value for c in fused.constants[1:]] == ["second", "first"], "same-id definitions were collapsed")
    rejects(lambda: fuse({k: v for k, v in docs.items() if k != "shared.oak.md"}, entry="entry.oak.md"), "missing target accepted")
    rejects(lambda: fuse({**docs, "unused.oak.md": render(Node(constants=[Constant(id="unused", value=True)]))}, entry="entry.oak.md"), "unreferenced document accepted")
    for field, entries in (
        ("instructions", [Instruction(id="policy", body="Protect this document scope.")]),
        ("state", [State(id="counter", value=0)]),
        ("processes", [Process(id="act", name="Perform action", steps=[ACT("Act.")])]),
        ("interfaces", [Interface(id="boundary", flow="emits", schema="schema.message")]),
    ):
        data = shared.model_dump(by_alias=True)
        data[field] = [entry.model_dump(by_alias=True) for entry in entries]
        unsafe = Node.model_validate(data)
        rejects(lambda: fuse({**docs, "shared.oak.md": render(unsafe)}, entry="entry.oak.md"), f"supporting {field} scope was widened")
    rejects(lambda: fuse({"../entry.oak.md": render(root)}, entry="../entry.oak.md"), "path escape accepted")
    collision = root.model_dump(by_alias=True)
    collision["constants"].append(Constant(id="guide-1-rules", value="collision").model_dump(by_alias=True))
    rejects(lambda: fuse({**docs, "entry.oak.md": render(Node.model_validate(collision))}, entry="entry.oak.md"), "namespace collision accepted")
