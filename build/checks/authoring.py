"""Shared-source, scope-safe fusion, delivery, and executable parity checks."""

from __future__ import annotations

import hashlib
import json
from contextlib import redirect_stdout
from io import StringIO
import re
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from unittest.mock import patch

import yaml
from oak import (ACT, Act, Arrival, Constant, ConstantValue, Emit, Instruction,
                 Interface, Node, Process, Schema, State, Trigger, ValueBinding,
                 execute, parse, render, resolve, Type, where)
from build.authoring import ENTRY, PACKAGE, SCRIPT, TARGET, artifacts, skill_documents, tree, validator_module
from build.authoring_guides import GUIDES, RULE_OWNERS, teaching_examples
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
    require(metadata["name"] == PACKAGE.name.removesuffix(".skill") and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata["name"]) is not None, "invalid skill name")
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
    require(actual_files == {path for path in expected if path.is_relative_to(PACKAGE)}, "skill layout contains missing or unowned files")
    _layout_inventory(PACKAGE)
    actual = {ENTRY: validator.oak_body(entry_text, PACKAGE / "SKILL.md").rstrip("\n")}
    for path in GUIDES:
        actual[path] = (PACKAGE / path).read_text(encoding="utf-8").rstrip("\n")
    require(actual == skill_documents(), "skill knowledge differs from its source")
    fused = tree(actual)
    require(render(fused) + "\n" == TARGET.read_text(encoding="utf-8"), "agent is not the exact assembled skill")
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
    require(not schema_guide.schemas, "schema guidance duplicated the complete literal teaching definitions")
    teaching = teaching_examples()
    require(next(c.value for c in fused.constants if c.id.endswith("-teaching")) == teaching,
            "assembled agent lost or changed inert teaching documents")
    for path, example in teaching.items():
        require((PACKAGE / path).read_text() == example + "\n", "teaching example is stale")
        resolve(parse(example), source=path, root=str(PurePosixPath(path).parent), load=teaching.get)
    _retained_teaching(actual, fused, teaching)
    _template_delivery(actual, fused)
    _generation_cleanup()
    _guidance_delivery(actual, fused)
    _teaching_scope(actual, fused, teaching)
    _execution_parity(actual, fused)
    _fusion_rejections()



# Accepted E01 and E03 specimens, independent of the generation owners.
EXPECTED_SKILL_FILES = {
    "SKILL.md", "scripts/validate.py", "references/oak.ebnf",
    "references/00-structure.oak.md", "references/01-schemas.oak.md",
    "references/02-constants.oak.md", "references/03-state.oak.md",
    "references/04-interfaces.oak.md", "references/05-triggers.oak.md",
    "references/06-processes.oak.md", "references/07-instructions.oak.md",
    "guides/authoring.oak.md", "guides/review.oak.md", "guides/validation.oak.md",
    "guides/subagent-orchestration.oak.md", "platforms/codex/adaptor.oak.md",
    "assets/examples/catalog.oak.md", "assets/examples/fixed_knowledge/example.oak.md",
    "assets/examples/shape_gallery/example.oak.md", "assets/examples/shape_writer/example.oak.md",
    "assets/examples/shape_writer/sample.oak.md", "assets/examples/shape_writer/shape_gallery.oak.md",
    "assets/examples/compound_growth/example.oak.md", "assets/examples/compound_growth/sample.oak.md",
    "_template/SKILL.md", "_template/references/.gitkeep", "_template/assets/constants/.gitkeep",
    "_template/assets/schemas/.gitkeep", "_template/guides/.gitkeep", "_template/processes/.gitkeep",
    "_template/scripts/.gitkeep",
}
EXPECTED_SKILL_TREE = """SKILL_TREE:
  SKILL.md→Skill entry point
  references/→Supporting knowledge
  assets/
    constants/→Reusable fixed values
    schemas/→Reusable information shapes
  processes/→OAK workflows
  guides/→Practical guidance
  scripts/→Executable helpers"""
TEMPLATE_MARKERS = {
    "SKILL_NAME", "SKILL_DESCRIPTION", "PURPOSE_JSON", "CONSTANT_ENTRIES",
    "INSTRUCTIONS_PART", "SCHEMAS_PART", "STATE_PART", "TRIGGERS_PART", "PROCESSES_PART", "INTERFACES_PART",
}


# Fixed literal identities inspected at Plan 0016's 9956e69 baseline.
_TEACHING_SHA256 = {
    "assets/examples/catalog.oak.md": "013f63280cd38e140bdea3ff6c5f470c568659a56ff4220953ca59834cd5812f",
    "assets/examples/fixed_knowledge/example.oak.md": "9c4b8ca07a8d2dcc8c18d808402517ca9d11e905d18c6e99532f194427f2c337",
    "assets/examples/shape_gallery/example.oak.md": "f8b549a2c1c8f891e43bc976789d514d7f5f147167cded03edb824d53afbbd03",
    "assets/examples/shape_writer/example.oak.md": "aa325263cbf957cc4f7547a4e364c209a870b21d6d0990ec4911b7ce14b817ef",
    "assets/examples/shape_writer/shape_gallery.oak.md": "f8b549a2c1c8f891e43bc976789d514d7f5f147167cded03edb824d53afbbd03",
    "assets/examples/shape_writer/sample.oak.md": "659c5588b290e02ab44477bc0bfa831c9967d576d44251f4a522efdbe47acd32",
    "assets/examples/compound_growth/example.oak.md": "0b0ca898c0ee875b712b674670f09ddb762ce66ee068c823524d79381353809a",
    "assets/examples/compound_growth/sample.oak.md": "ad5fd8853028db0e7bb8e2343dd8c620b996a884c86fb2e903a9c800a5e0010b"
}
_TEMPLATE_SHA256 = "6c5e706344aef4c649256cf57a6842761a7aa3491b4efe5a190fa2e681169c17"


def _retained_teaching(documents: dict[str, str], fused: Node, teaching: dict[str, str]) -> None:
    """Deduplicate delivery knowledge without deleting its complete teaching content."""
    require({name: hashlib.sha256(text.encode()).hexdigest() for name, text in teaching.items()} == _TEACHING_SHA256,
            "complete literal teaching changed from the reviewed corpus")
    gallery = parse(teaching["assets/examples/shape_gallery/example.oak.md"])
    require(gallery.schemas == list(SHAPES), "teaching lost full shape definitions")
    instances = {c.id.removesuffix("-instance"): c.value for c in gallery.constants}
    require(instances == EXPECTED_INSTANCES, "teaching lost populated shape instances")
    require(hashlib.sha256((PACKAGE / "_template/SKILL.md").read_bytes()).hexdigest() == _TEMPLATE_SHA256,
            "literal template changed from the reviewed scaffold")
    for guide in GUIDES:
        node = parse(documents[guide])
        require(not any((node.instructions, node.state, node.triggers, node.processes, node.interfaces)),
                f"supporting knowledge widened operational scope: {guide}")
    from build.agents import ADAPTOR_SOURCE, PACKAGE as AGENT_PACKAGE
    adaptor = ADAPTOR_SOURCE.read_bytes()
    require((PACKAGE / "platforms/codex/adaptor.oak.md").read_bytes() == adaptor,
            "authoring Codex knowledge is not the maintained adaptor")
    require((AGENT_PACKAGE / "adaptors/codex/adaptor.oak.md").read_bytes() == adaptor,
            "agent bundle uses different Codex knowledge")
    source = parse(adaptor.decode())
    for entry in source.constants:
        assembled = [c for c in fused.constants if c.id.endswith("-" + entry.id) and c.value == entry.value]
        require(len(assembled) == 1, f"assembled Codex knowledge lost its single source: {entry.id}")
    structure = parse(documents["references/00-structure.oak.md"])
    parts = next(c.value for c in structure.constants if c.id == "part-responsibilities")
    lifetimes = {row["part"]: row["lifetime"] for row in parts}
    require(lifetimes["constants"] == "whole document use" and lifetimes["state"] == "across arrivals"
            and lifetimes["interfaces"] == "one receive or emission", "part lifetime knowledge changed")
    scopes = next(c.value for c in parse(documents["references/06-processes.oak.md"]).constants if c.id == "scopes")
    require("immutable per frame" in scopes and "Branches/iterations are local." in scopes,
            "deduplication lost frame or child lifetime knowledge")
    # The package lifetime rule stays verbatim in the state guide as well as the assembled agent.
    state_guidance = next(c.value for c in parse(documents["references/03-state.oak.md"]).constants if c.id == "guidance")
    require(next(r.instruction for r in AUTHORING_GUIDANCE if r.id == "separate-lifetimes") in state_guidance,
            "lifetime deduplication lost the state guide's rule")


def _layout_inventory(package: Path) -> None:
    files = {path.relative_to(package).as_posix() for path in package.rglob("*")
             if path.is_file() and "__pycache__" not in path.parts}
    require(files == EXPECTED_SKILL_FILES, "E01: delivered skill file set differs from the accepted layout")
    directories = {parent.as_posix() for name in EXPECTED_SKILL_FILES for parent in PurePosixPath(name).parents
                   if parent != PurePosixPath(".")}
    actual = {path.relative_to(package).as_posix() for path in package.rglob("*")
              if path.is_dir() and "__pycache__" not in path.parts}
    require(actual == directories, "E01: missing or extra skill directories")
    for name in files:
        if name.endswith("/.gitkeep"):
            require((package / name).read_bytes() == b"", "E02: template folders must remain empty")


def _template_body(text: str) -> str:
    require(text.startswith("---\n"), "E02: template metadata is missing")
    _, frontmatter, body = text.split("---\n", 2)
    require(yaml.safe_load(frontmatter) == {"name": "<SKILL_NAME>", "description": "<SKILL_DESCRIPTION>"},
            "E02: template inherited a domain or capability identity")
    markers = re.findall(r"<([A-Z_]+)>", text)
    require(set(markers) == TEMPLATE_MARKERS and len(markers) == len(TEMPLATE_MARKERS),
            "E02: missing, duplicated, or unexpected scaffold marker")
    require(body.count(EXPECTED_SKILL_TREE) == 1 and body.count("SKILL_TREE:") == 1,
            "E03: literal layout notation changed")
    return body


def _template_delivery(documents: dict[str, str], fused: Node) -> None:
    """Populate the actual inert scaffold, then parse and resolve its OAK body."""
    template = (PACKAGE / "_template" / "SKILL.md").read_text(encoding="utf-8")
    _template_body(template)
    authoring = parse(documents["guides/authoring.oak.md"])
    require(next(c.value for c in authoring.constants if c.id == "skill-template") == template,
            "E02: skill guide lost the exact template")
    require(next(c.value for c in fused.constants if c.id.endswith("-skill-template")) == template,
            "E02: assembled agent lost the exact template")
    require(set(documents) == {ENTRY, *GUIDES}, "E02: scaffold or teaching entered the fusion graph")
    rejects(lambda: tree({**documents, "_template/SKILL.md": template}), "unfilled template became active fusion input")
    rejects(lambda: parse(validator_module().oak_body(template, Path("SKILL.md"))), "unfilled scaffold parsed as completed knowledge")

    # This test-only specimen is never delivered as a completed domain skill.
    replacements = {name: "" for name in TEMPLATE_MARKERS}
    replacements.update(SKILL_NAME="fixture-knowledge", SKILL_DESCRIPTION="A temporary verification fixture.",
                        PURPOSE_JSON=json.dumps("Check literal layout preservation."))
    populated = template
    for name, value in replacements.items():
        marker = f"<{name}>\n" if name.endswith("_PART") else f"<{name}>"
        populated = populated.replace(marker, value)
    body = validator_module().oak_body(populated, Path("SKILL.md"))
    node = parse(body)
    require({c.id for c in node.constants} == {"purpose", "layout"}, "E02: scaffold ships extra implementation")
    require(next(c.value for c in node.constants if c.id == "layout") == EXPECTED_SKILL_TREE,
            "E03: layout is not exact literal OAK text")
    require(not any((node.instructions, node.schemas, node.state, node.triggers, node.processes, node.interfaces)),
            "E02: minimal population acquired operational scope")
    require(len(resolve(node).documents) == 1, "E03: displayed paths became imports")
    with TemporaryDirectory(prefix="oak-populated-template-") as temporary:
        path = Path(temporary) / "SKILL.md"
        path.write_text(populated, encoding="utf-8")
        with redirect_stdout(StringIO()) as captured:
            status = validator_module().validate([path], None)
        report = json.loads(captured.getvalue())
        require(status == 0 and report["status"] == "valid" and report["checks"] == ["parse", "resolve"],
                "E02: populated fixture failed optional validator parsing and resolution")
    for grouping in ("xml", "markdown"):
        canonical = render(node, grouping=grouping)
        require(parse(canonical) == node, "E02: population changed across canonical groupings")
    for broken in (
        template.replace("→", " → ", 1), template.replace("SKILL_TREE:", "Skill tree:"),
        template.replace("  assets/", " assets/"), template.replace("<PURPOSE_JSON>", '"domain"'),
        template.replace("<STATE_PART>", "<UNKNOWN_PART>"), template.replace("<STATE_PART>", "<STATE_PART><STATE_PART>"),
        template.replace('name: "<SKILL_NAME>"', 'name: "oak-authoring"'),
    ):
        rejects(lambda: _template_body(broken), "changed template specimen was accepted")
    rejects(lambda: parse(body.replace('purpose: "Check literal layout preservation."', 'purpose: INVALID_JSON')),
            "malformed populated purpose was accepted")


def _generation_cleanup() -> None:
    """Exercise all generator-owned roots without mutating the actual product."""
    from build.authoring import write
    with TemporaryDirectory(prefix="oak-layout-cleanup-") as temporary:
        root = Path(temporary)
        package = root / "generated" / "oak-authoring.skill"
        expected = {package / path.relative_to(PACKAGE): text for path, text in artifacts().items()
                    if path.is_relative_to(PACKAGE)}
        script = package / "scripts" / "validate.py"
        script.parent.mkdir(parents=True)
        script.write_bytes(SCRIPT.read_bytes())
        for directory in ("references", "guides", "assets", "_template", "platforms"):
            obsolete = package / directory / "obsolete" / "stale.txt"
            obsolete.parent.mkdir(parents=True)
            obsolete.write_text("stale")
        cache = package / "scripts" / "__pycache__" / "fixture.pyc"
        cache.parent.mkdir()
        cache.write_bytes(b"cache")
        with patch("build.authoring.PACKAGE", package), patch("build.authoring.ROOT", root), patch("build.authoring.artifacts", return_value=expected):
            write()
            first = {path: path.read_bytes() for path in package.rglob("*") if path.is_file()}
            write()
            require(first == {path: path.read_bytes() for path in package.rglob("*") if path.is_file()},
                    "generation is not byte-stable")
        _layout_inventory(package)
        require(script.read_bytes() == SCRIPT.read_bytes() and cache.read_bytes() == b"cache",
                "cleanup changed the helper or runtime cache")
        for name in ("guides/review.oak.md", "_template/assets/constants/.gitkeep"):
            path = package / name
            original = path.read_bytes()
            path.unlink()
            rejects(lambda: _layout_inventory(package), "missing product file was accepted")
            path.write_bytes(original)
        extra = package / "_template" / "processes" / "unexpected.oak.md"
        extra.write_text("unexpected")
        rejects(lambda: _layout_inventory(package), "unexpected product file was accepted")
        extra.unlink()
        extra.parent.joinpath("empty").mkdir()
        rejects(lambda: _layout_inventory(package), "unexpected empty directory was accepted")


def _guidance_delivery(documents: dict[str, str], fused: Node) -> None:
    """Every rule reaches its sole guide and the assembled capability unchanged."""
    rules = {rule.id: rule.instruction for rule in AUTHORING_GUIDANCE}
    require(len(rules) == len(AUTHORING_GUIDANCE), "duplicate authoring rule id")
    for rule in ("describe-action-roles", "distinguish-action-promises"):
        require(rule in RULE_OWNERS[GUIDES.index("references/06-processes.oak.md")], "statement guidance lost its process guide owner")
    for rule, owner in (
        ("own-boundary-contracts", "references/04-interfaces.oak.md"),
        ("explain-boundary-contracts", "references/04-interfaces.oak.md"),
        ("disclose-completeness", "references/00-structure.oak.md"),
        ("adapt-external-contracts", "references/06-processes.oak.md"),
    ):
        require(rule in RULE_OWNERS[GUIDES.index(owner)], "contract guidance lost its semantic owner")
    delivered = []
    for guide, keys in sorted(zip(GUIDES, RULE_OWNERS, strict=True)):
        node = parse(documents[guide])
        guidance = next((c.value for c in node.constants if c.id == "guidance"), None)
        if not keys:
            require(guidance is None, f"{guide} acquired redundant package guidance")
            continue
        require(guidance == [rules[key] for key in keys], f"{guide} guidance differs from its source")
        delivered.extend(guidance)
    assembled = [text for c in fused.constants if c.id.endswith("-guidance") for text in c.value]
    require(assembled == delivered, "assembled guidance differs from the exact skill guides")
    require(len(set(delivered)) == len(delivered), "duplicate authored guidance claims")


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
            validate_closed_bundle(root / "assets" / "examples" / scenario.name)
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
    candidate = teaching_examples()["assets/examples/fixed_knowledge/example.oak.md"]
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
                if "TEMPLATE" in values:
                    require(values["TEMPLATE"] == (PACKAGE / "_template" / "SKILL.md").read_text(), "template routing changed literal knowledge")
                    require("Unfilled scaffolding is inert." in values["TEMPLATE_USE"], "template routing lost its inert boundary")
                if action.outputs == ["DESIGN_1"]:
                    require(values["TEACHING"] == teaching_examples(), "schema design lost complete literal teaching")
                if action.outputs == ["DESIGN_6"]:
                    orchestration = parse(documents["guides/subagent-orchestration.oak.md"])
                    codex = parse(documents["platforms/codex/adaptor.oak.md"])
                    expected = {"ORCHESTRATION": next(c.value for c in orchestration.constants if c.id == "orchestration"),
                                "DELEGATION": next(c.value for c in orchestration.constants if c.id == "guidance"),
                                "CODEX": next(c.value for c in codex.constants if c.id == "mapping"),
                                "DEFAULTS": next(c.value for c in codex.constants if c.id == "native-defaults")}
                    require({key: values[key] for key in expected} == expected, "delegation or native configuration routing changed")
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
            require(sum("TEMPLATE" in values for _, values, _ in trace) == 1, "template use was not routed exactly once")
            require(sum("TEACHING" in values for _, values, _ in trace) == 2, "teaching must reach schema design and review")
            require(sum("ORCHESTRATION" in values for _, values, _ in trace) == 1, "orchestration must reach process design once")
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
        processes=[Process(id="respond", name="Respond message", output="shared.oak.md#schema.message", body=[
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
        ("processes", [Process(id="act", name="Perform action", body=[ACT("Act.")])]),
        ("interfaces", [Interface(id="boundary", flow="emits", schema="schema.message")]),
    ):
        data = shared.model_dump(by_alias=True)
        data[field] = [entry.model_dump(by_alias=True) for entry in entries]
        unsafe = Node.model_validate(data)
        rejects(lambda: fuse({**docs, "shared.oak.md": render(unsafe)}, entry="entry.oak.md"), f"supporting {field} scope was widened")
    rejects(lambda: fuse({"../entry.oak.md": render(root)}, entry="../entry.oak.md"), "path escape accepted")
    collision = root.model_dump(by_alias=True)
    collision["constants"].append(Constant(id="g1-rules", value="collision").model_dump(by_alias=True))
    rejects(lambda: fuse({**docs, "entry.oak.md": render(Node.model_validate(collision))}, entry="entry.oak.md"), "namespace collision accepted")
