"""Offline authoring contracts and deterministic native-action fixtures, not clients."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import tomllib
from unittest.mock import patch

import yaml

from oak import ACT, Act, Arrival, Constant, Node, Process, State, execute, parse, render, resolve
from build.authoring import ENTRY, PACKAGE, TARGET, artifacts, skill_documents, tree
from build.authoring_platforms import (CATALOGUE_SOURCE, CLAUDE_SOURCE, CODEX_SOURCE,
    RESOURCE_PATHS, claude_authoring, codex_authoring, profile, resource_node)
from build.checks.authoring_intent import check_draft, check_intent_specimens, check_view

DESCRIPTION = "Create, read, update or delete OAK; clarify intent only when useful."
LEGEND = "✓ confirmed · ~ proposed · ? unresolved"
KINDS = ("agent", "single-shot-prompt", "compact-knowledge", "agents-md", "skill", "stateful-skill")
PROCESS_IDS = (
    "capture-request", "author-document", "author-turn", "route-request", "determine-artifact-kind",
    "establish-tool-context", "transform-source", "maintain-draft-ast", "review-draft", "elicit-intent",
    "dispatch-operation", "create-oak", "read-oak", "update-oak", "delete-oak", "render-and-validate",
    "apply-changes", "compose-response", "publish-response", "finish-response",
)
VIEW_FIELDS = ("UNDERSTANDING", "INTENT_AST", "CHANGES", "NEXT_DECISION", "READINESS")
EMPTY_MANIFEST = '{"documents":[],"deletions":[]}'
NO_EFFECTS = '{"status":"not-requested","paths":[],"unresolved":[]}'
CATALOGUE_CASES = (
    ("reviewer role", "agent"), ("role prompt", "agent"),
    ("bounded classifier", "single-shot-prompt"), ("classification instructions", "single-shot-prompt"),
    ("fixed facts", "compact-knowledge"), ("notes", "compact-knowledge"),
    ("scoped conventions", "agents-md"), ("repository rules", "agents-md"),
    ("reusable procedure", "skill"), ("procedure notes", "skill"),
    ("recurring queue worker", "stateful-skill"), ("recurring-work description", "stateful-skill"),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rejects(operation: Callable[[], object], reason: str) -> None:
    try:
        operation()
    except (ValueError, RuntimeError) as error:
        require(reason in str(error), f"expected {reason!r}, received {error}")
        return
    raise RuntimeError(f"accepted invalid authoring contract: {reason}")


def native_bodies(products: Mapping[Path, str]) -> tuple[str, str]:
    codex_path = PACKAGE / "platforms/codex/templates/.codex/agents/oak-authoring.toml"
    claude_path = PACKAGE / "platforms/claude/templates/.claude/agents/oak-authoring.md"
    codex = tomllib.loads(products[codex_path])
    require(set(codex) == {"name", "description", "developer_instructions", "agents"}, "Codex metadata key drift")
    require(codex["name"] == "oak-authoring" and codex["description"] == DESCRIPTION,
            "Codex authoring identity drift")
    require(codex["agents"] == {"enabled": False} and type(codex["agents"]["enabled"]) is bool,
            "Codex authoring delegation default drift")
    text = products[claude_path]
    require(text.startswith("---\n"), "Claude frontmatter is missing")
    header, body = text[4:].split("---\n\n", 1)
    require(yaml.safe_load(header) == {"name": "oak-authoring", "description": DESCRIPTION,
            "model": "inherit", "permissionMode": "default", "disallowedTools": ["Agent"]},
            "Claude metadata drift")
    require(codex["developer_instructions"] == body == products[TARGET], "native bodies differ from shared S")
    return codex["developer_instructions"], body


def _resource_contracts() -> None:
    catalogue = resource_node(CATALOGUE_SOURCE)
    values = {item.id: item.value for item in catalogue.constants}
    require(set(values) == {"catalogue-version", "artifact-kinds"} and values["catalogue-version"] == "1",
            "catalogue identity drift")
    kinds = values["artifact-kinds"]
    require([item["id"] for item in kinds] == list(KINDS), "catalogue ids/order drift")
    for item in kinds:
        require(set(item) == {"id", "purpose", "structure", "state", "delivery", "questions"}, "kind fields drift")
        require(all(isinstance(item[key], str) and item[key] for key in ("id", "purpose", "structure", "state", "delivery")),
                "empty kind guidance")
        require(isinstance(item["questions"], list) and all(isinstance(q, str) and q for q in item["questions"]),
                "invalid kind questions")
    require({kind for _, kind in CATALOGUE_CASES} == set(KINDS) and len(CATALOGUE_CASES) == 12,
            "scratch/source catalogue acceptance cases lost")
    # These are independent expected request/kind pairs, not a natural-language classifier.
    for source in RESOURCE_PATHS:
        node = resource_node(source)
        require(not any((node.instructions, node.state, node.processes, node.triggers, node.interfaces)),
                "resource acquired operational scope")
        require(len(resolve(node).documents) == 1, "resource acquired an external import")
    originals = {source: (Path(__file__).resolve().parents[2] / source).read_bytes() for source in RESOURCE_PATHS}
    with TemporaryDirectory(prefix="oak-authoring-resources-") as directory:
        root = Path(directory)
        for source, content in originals.items():
            path = root / source
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        with patch("build.authoring_platforms.ROOT", root):
            rejects(lambda: resource_node(Path("../escape.oak.md")), "unregistered")
            path = root / CODEX_SOURCE
            path.write_bytes(originals[CODEX_SOURCE].replace(b'"sandbox_mode": "read-only"', b'"sandbox_mode":"read-only"'))
            rejects(lambda: resource_node(CODEX_SOURCE), "canonical")
            path.write_text("not OAK", encoding="utf-8")
            rejects(lambda: resource_node(CODEX_SOURCE), "")
            path.unlink()
            outside = root / "outside.oak.md"
            outside.write_bytes(originals[CODEX_SOURCE])
            path.symlink_to(outside)
            rejects(lambda: resource_node(CODEX_SOURCE), "symbolic link")
            path.unlink()
            path.write_bytes(originals[CODEX_SOURCE])
            owner = path.parent
            moved = owner.with_name("real-codex")
            owner.rename(moved)
            owner.symlink_to(moved, target_is_directory=True)
            rejects(lambda: resource_node(CODEX_SOURCE), "symbolic link")
            require(outside.read_bytes() == originals[CODEX_SOURCE], "rejected resource was changed")


def _native_contracts() -> None:
    products = artifacts()
    bodies = native_bodies(products)
    for body in bodies:
        require(render(parse(body)) + "\n" == body, "native body not canonical")
        require(len(resolve(parse(body)).documents) == 1, "native body not standalone")
    codex_profile = profile(resource_node(CODEX_SOURCE), "authoring-profile")
    claude_profile = profile(resource_node(CLAUDE_SOURCE), "authoring-profile")
    _native_file_template(codex_profile)
    _local_agent_files(products)
    samples = ("", "one line", "\n", "雪 ✓ \\ path\n", '"quotes" and \'\'\' triples\n',
               "\x00\x1f\x7f\t\n", "---\nname: not metadata\n---\n", "no final newline")
    for sample in samples:
        codex = tomllib.loads(codex_authoring(sample, codex_profile))
        claude = claude_authoring(sample, claude_profile)[4:].split("---\n\n", 1)
        require(codex["developer_instructions"] == claude[1] == sample, "native serializer changed literal bytes")
    for key, value in (("sandbox_mode", "danger-full-access"), ("model", "other"), ("tools", ["all"]),
                       ("description", ""), ("agents", {"enabled": True}), ("agents", {"enabled": 0})):
        rejects(lambda: codex_authoring("body", {**codex_profile, key: value}), "profile")
    for key, value in (("permissionMode", "bypassPermissions"), ("tools", ["all"]), ("model", "other"),
                       ("disallowedTools", []), ("description", ""), ("skills", ["anything"])):
        rejects(lambda: claude_authoring("body", {**claude_profile, key: value}), "profile")
    broken = dict(products)
    codex_path = PACKAGE / "platforms/codex/templates/.codex/agents/oak-authoring.toml"
    broken[codex_path] = broken[codex_path].replace("enabled = false", "enabled = true")
    rejects(lambda: native_bodies(broken), "default drift")


def _native_file_template(metadata: Mapping[str, object]) -> None:
    """The inert file specimen must decode like the actual native serializer."""
    node = resource_node(CODEX_SOURCE)
    template = next(constant.value for constant in node.constants if constant.id == "native-file-template")
    slots = re.findall(r"<TOML_[A-Z_]+>", template)
    require(set(slots) == {"<TOML_NAME>", "<TOML_DESCRIPTION>", "<TOML_OAK_BODY>"}
            and len(slots) == 3, "native TOML specimen has missing or duplicate fields")
    sample = 'Complete OAK body\nwith "quotes", Unicode 雪 and literal <TOML_NAME>.\n'
    bindings = {"<TOML_NAME>": metadata["name"], "<TOML_DESCRIPTION>": metadata["description"],
                "<TOML_OAK_BODY>": sample}
    populated = re.sub(r"<TOML_[A-Z_]+>", lambda match: json.dumps(bindings[match[0]], ensure_ascii=False), template)
    require(tomllib.loads(populated) == tomllib.loads(codex_authoring(sample, metadata)),
            "native TOML specimen changes metadata scope or the OAK body")


def _local_agent_files(products: Mapping[Path, str]) -> None:
    """Keep the repository registration aligned with all current authoring knowledge."""
    root = Path(__file__).resolve().parents[2]
    copy = root / ".agents/agents/oak-authoring.oak.md"
    require(copy.is_file() and copy.read_bytes() == products[TARGET].encode("utf-8"),
            "refresh the local agent copy from generated/oak-authoring.oak.md")
    registration = root / ".codex/agents/oak-authoring.toml"
    expected_target = "../../generated/oak-authoring.skill/platforms/codex/templates/.codex/agents/oak-authoring.toml"
    require(registration.is_symlink() and registration.readlink().as_posix() == expected_target,
            "local Codex registration needs its portable relative symlink")
    native = PACKAGE / "platforms/codex/templates/.codex/agents/oak-authoring.toml"
    require(registration.resolve() == native.resolve() and registration.read_bytes() == products[native].encode("utf-8"),
            "local Codex registration is stale or targets a different native agent")


def _workflow_contracts() -> None:
    documents = skill_documents()
    node = parse(documents[ENTRY])
    require(tuple(p.id for p in node.processes) == PROCESS_IDS, "conceptual process inventory drift")
    require({s.id for s in node.schemas} == {"authoring-request", "authoring-result", "authoring-turn", "conversation-result"},
            "root public contracts drift")
    require(len(node.triggers) == 3 and len(node.interfaces) == 4, "public arrival count drift")
    require(not node.state and not node.instructions, "authoring acquired policy or stored state")
    require(len(resolve(node, source=ENTRY, load=documents.get).documents) == 16, "incomplete shared closure")
    require(len(resolve(tree(documents)).documents) == 1, "incomplete fused closure")
    guides = parse(documents["guides/authoring.oak.md"])
    schema = next(item for item in guides.schemas if item.id == "draft-response")
    require(set(schema.placeholders) == {"DRAFT", *VIEW_FIELDS}, "composition return shape drift")
    compose = next(process for process in node.processes if process.id == "compose-response")
    require(compose.output == "guides/authoring.oak.md#schema.draft-response", "composition must return exactly six new bindings")
    broken = deepcopy(node)
    next(process for process in broken.processes if process.id == "compose-response").output = "schema.conversation-result"
    rejects(lambda: tree({**documents, ENTRY: render(broken)}), "output missing")
    statements = next(p.body for p in node.processes if p.id == "author-turn")
    require([s.process for s in statements[:6]] == ["process." + name for name in (
        "route-request", "determine-artifact-kind", "establish-tool-context", "transform-source", "maintain-draft-ast", "review-draft")],
        "preparation order drift")
    context = next(item.value for item in guides.constants if item.id == "draft-contract")
    require(context["draft"]["format"] == 1 and "No credentials" in context["envelope"], "JSON data contract drift")
    presentation = next(item.value for item in guides.constants if item.id == "presentation")
    require(any(LEGEND in item for item in presentation), "persistent status legend missing")
    require(any("expanded fields" in item and "steps" in item for item in presentation), "expanded statuses missing")
    require(any("never wait" in item for item in presentation), "parent-mediated return missing")


def validate_authoring_agent() -> None:
    """Independent source, format and graph checks, excluding any live-client claim."""
    _resource_contracts()
    _native_contracts()
    _workflow_contracts()
    documents = skill_documents()
    exercise_authoring_fixtures(documents, tree(documents))


# Independent approved E02 specimens, copied as test inputs, not build authority.
_FACT_DRAFT = {'format': 1,
 'id': 'fact-card-1',
 'turn': 1,
 'request': {'text': 'Help me work out a compact fact card for Cedar. It needs support hours, but I '
                     'have not chosen them yet.',
             'operation': 'create',
             'mode': 'guided',
             'purpose': 'Develop a compact fact card, then produce it when agreed.',
             'channel': 'conversation'},
 'kind': 'compact-knowledge',
 'context': {'knowledge_revision': 'specimen:0017-v1',
             'catalogue_version': '1',
             'authoring_host': 'specimen native interpreter',
             'consumer': 'general OAK interpreter',
             'evidence': ['user:1'],
             'installation_consent': [],
             'validation_requested': False,
             'validation_required': False},
 'scope': {'documents': ['facts.oak.md'],
           'selectors': [],
           'destination': 'response',
           'effects': [],
           'reference_boundary': []},
 'sources': [{'id': 'user-1',
              'identity': None,
              'locator': 'user:1',
              'text': 'Help me work out a compact fact card for Cedar. It needs support hours, but I '
                      'have not chosen them yet.',
              'read': 'complete'}],
 'documents': [{'path': 'facts.oak.md',
                'node': {'constants': [{'id': 'service-name', 'value': 'Cedar'},
                                       {'id': 'support-hours'},
                                       {'id': 'timezone', 'value': 'UTC'}]}}],
 'outputs': [{'path': 'facts.oak.md', 'format': 'oak', 'document': 'facts.oak.md', 'source': None}],
 'review': {'status': 'blocked',
            'blockers': ['A2', 'A3'],
            'basis': ['user:1'],
            'checks': [{'name': 'intent review',
                        'method': 'native semantic review',
                        'status': 'failed',
                        'subject': 'fact-card-1 turn 1',
                        'evidence': 'A2 lacks a value and A3 is an unaccepted proposal.',
                        'exit_code': None}]},
 'annotations': [{'id': 'A1',
                  'document': 'facts.oak.md',
                  'pointer': '/constants/0',
                  'status': 'confirmed',
                  'meaning': 'Service name is Cedar.',
                  'question': '',
                  'evidence': ['user:1']},
                 {'id': 'A2',
                  'document': 'facts.oak.md',
                  'pointer': '/constants/1/value',
                  'status': 'unresolved',
                  'meaning': 'Support hours are required but not chosen.',
                  'question': 'Which support hours should the card state?',
                  'evidence': ['user:1']},
                 {'id': 'A3',
                  'document': 'facts.oak.md',
                  'pointer': '/constants/2',
                  'status': 'proposed',
                  'meaning': 'UTC is proposed as the timezone; it is not a fact.',
                  'question': 'Which timezone applies to those hours?',
                  'evidence': []},
                 {'id': 'A4',
                  'document': '',
                  'pointer': '/tools',
                  'status': 'confirmed',
                  'meaning': 'This fact card needs no tools.',
                  'question': '',
                  'evidence': ['user:1']}],
 'changes': [{'op': 'add',
              'annotation': 'A1',
              'document': 'facts.oak.md',
              'pointer': '/constants/0',
              'before': '',
              'after': 'Service name Cedar confirmed.'},
             {'op': 'add',
              'annotation': 'A2',
              'document': 'facts.oak.md',
              'pointer': '/constants/1',
              'before': '',
              'after': 'Support hours required; value unresolved.'},
             {'op': 'add',
              'annotation': 'A3',
              'document': 'facts.oak.md',
              'pointer': '/constants/2',
              'before': '',
              'after': 'UTC proposed, not confirmed.'}],
 'source_map': [{'source': 'user-1',
                 'clause': 'service name',
                 'document': 'facts.oak.md',
                 'annotations': ['A1'],
                 'disposition': 'preserved',
                 'reason': 'Exact supplied name.'},
                {'source': 'user-1',
                 'clause': 'support hours not chosen',
                 'document': 'facts.oak.md',
                 'annotations': ['A2'],
                 'disposition': 'unresolved',
                 'reason': 'Do not fabricate a value.'}],
 'tools': [],
 'authority': {'requests': [{'reference': 'user:1',
                             'purpose': 'Develop a fact card.',
                             'documents': ['facts.oak.md'],
                             'selectors': [],
                             'effects': []}],
               'guided_release': False,
               'release_reference': ''}}
_FACT_VIEWS = {'UNDERSTANDING': 'You want a compact fact card for Cedar; support hours still need a value.',
 'INTENT_AST': 'facts.oak.md [compact-knowledge]\n'
               '├─ constants                         # Fixed facts\n'
               '│  ├─ service-name: Cedar ✓ [A1]\n'
               '│  ├─ support-hours: ? [A2]\n'
               '│  └─ timezone: UTC ~ [A3]\n'
               '└─ tools: none ✓ [A4]\n'
               '\n'
               '✓ confirmed · ~ proposed · ? unresolved',
 'CHANGES': 'Created the same initial model from your request. UTC is a proposal, not an adopted fact.',
 'NEXT_DECISION': 'A2/A3: What support hours and timezone should the card state? These determine the '
                  'two remaining constant values.',
 'READINESS': 'Blocked on A2 and A3. Guided output has not been released; no artifacts or file effects '
              'were produced.'}


def _fact_draft(*, complete: bool = False) -> dict:
    draft = deepcopy(_FACT_DRAFT)
    if complete:
        draft["turn"] = 2
        request = "Use 09:00-17:00 and Australia/Brisbane. I am happy with that; produce the fact card."
        draft["request"]["text"] = request
        draft["documents"][0]["node"]["constants"][1]["value"] = "09:00-17:00"
        draft["documents"][0]["node"]["constants"][2]["value"] = "Australia/Brisbane"
        draft["sources"].append({"id": "user-2", "identity": None, "locator": "user:2", "text": request, "read": "complete"})
        draft["changes"] = []
        for annotation, value in ((draft["annotations"][1], "09:00-17:00"), (draft["annotations"][2], "Australia/Brisbane")):
            before = annotation["meaning"]
            annotation.update(status="confirmed", meaning=value, question="", evidence=["user:2"])
            draft["changes"].append({"op": "confirm", "annotation": annotation["id"], "document": annotation["document"],
                "pointer": annotation["pointer"], "before": before, "after": value})
        draft["source_map"][1].update(disposition="preserved", reason="User:2 supplied the previously missing hours.")
        draft["source_map"].append({"source": "user-2", "clause": request, "document": "facts.oak.md", "annotations": ["A2", "A3"],
            "disposition": "preserved", "reason": "Exact supplied values and actual guided release."})
        draft["authority"].update(guided_release=True, release_reference="user:2")
        draft["authority"]["requests"].append({"reference": "user:2", "purpose": "Produce the agreed fact card.",
            "documents": ["facts.oak.md"], "selectors": [], "effects": []})
        draft["review"] = {"status": "ready", "blockers": [], "basis": ["user:1", "user:2"], "checks": []}
    return draft


def _fixture_views(draft: dict) -> dict[str, str]:
    if draft["review"]["status"] == "blocked":
        return dict(_FACT_VIEWS)
    facts = draft["documents"][0]["node"].get("constants", [])
    lines = ["facts.oak.md [compact-knowledge]", "├─ constants  # Fixed facts"]
    for index, fact in enumerate(facts):
        lines.append(f"│  {'└─' if index == len(facts)-1 else '├─'} {fact['id']}: {fact.get('value', '?')} ✓ [A{index+1}]")
    lines.extend(("└─ tools: none ✓ [A4]", "", LEGEND))
    return {"UNDERSTANDING": "The agreed values are ready.", "INTENT_AST": "\n".join(lines),
            "CHANGES": "A2 and A3 are now confirmed; A1 and A4 retain their meaning.",
            "NEXT_DECISION": "", "READINESS": "Meaning ready; actual effects and checks are reported separately."}


def _simulate(node, draft: dict, *, source=None, load=None, prior="", legacy=False,
              requested=False, validation="not-requested", consent=False, deliverable=True,
              authorised=True, arrival_event=False, response_views=None):
    """Supply deterministic native decisions to test OAK dataflow, not language quality.

    No helper, installation, file write or client is performed by this fixture.
    Its separate observed_calls list explicitly describes simulated helper decisions.
    """
    work = deepcopy(draft)
    work["request"]["channel"] = "legacy" if legacy else "conversation"
    work["context"]["validation_requested"] = requested
    work["context"]["installation_consent"] = ["fixture:separate-consent"] if consent else []
    encoded = json.dumps(work, ensure_ascii=False, sort_keys=True)
    trace = []
    observed_calls = []
    ready = work["review"]["status"] == "ready"
    if legacy and len(work["outputs"]) != 1:
        ready = False
    manifest = {"documents": [], "deletions": []}
    if ready and work["request"]["operation"] != "read":
        for document in work["documents"]:
            manifest["documents"].append({"path": document["path"], "content": render(Node.model_validate(document["node"])) + "\n"})
    manifest_text = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
    validation_text = "Programmatic validation was not performed (not requested)." if not requested else "Simulated fixture validation: " + validation
    deferred_validation = "Programmatic validation was not performed (not requested)." if not requested else "Programmatic validation was not performed (not ready or released)."

    def native(action: Act, values):
        output = tuple(action.outputs)
        trace.append((output, deepcopy(dict(values))))
        if output == ("SOURCE", "VALIDATE"):
            return {"SOURCE": work["request"]["text"], "VALIDATE": requested}
        if output == ("WORK", "OPERATION", "GUIDED"):
            require(values["REQUEST"] == work["request"]["text"] and values["PRIOR"] == prior, "request/prior changed")
            if prior:
                previous = json.loads(prior)
                require(previous["id"] == work["id"] and previous["turn"] + 1 == work["turn"], "continuity changed")
            return {"WORK": encoded, "OPERATION": work["request"]["operation"], "GUIDED": work["request"]["mode"] == "guided"}
        if output in (("KIND_DRAFT",), ("TOOL_DRAFT",), ("MAPPED_DRAFT",), ("UPDATED_DRAFT",)):
            require(values["WORK"] == encoded, "a preparation stage lost the complete draft")
            if output == ("KIND_DRAFT",):
                require([item["id"] for item in values["KINDS"]] == list(KINDS), "catalogue was changed in transit")
            if output == ("UPDATED_DRAFT",):
                from build.authoring_guides import teaching_examples, TEMPLATE_ENTRY
                from build.skill_template import extension_node
                require(values["TEACHING"] == teaching_examples() and values["TEMPLATE"] == TEMPLATE_ENTRY,
                        "maintain-draft lost complete inert teaching or template")
                require(values["EXTENSION"] == render(extension_node()), "maintain-draft lost selected extension knowledge")
            return {output[0]: encoded}
        if output == ("REVIEWED", "READY"):
            require(values["WORK"] == encoded, "review received a different model")
            return {"REVIEWED": encoded, "READY": ready}
        if "PERMITTED" in output:
            is_read = work["request"]["operation"] == "read"
            released = work["request"]["mode"] != "guided" or work["authority"]["guided_release"]
            return {"GATED": encoded, "PERMITTED": authorised and released and (ready or is_read),
                    "DEFERRED_EFFECTS": NO_EFFECTS, "DEFERRED_VALIDATION": deferred_validation}
        if output == ("RENDERED", "ARTIFACTS", "VALIDATION", "DELIVERABLE"):
            require(values["WORK"] == encoded, "render received an unreviewed model")
            if requested and validation != "missing-execution":
                observed_calls.append("helper --without-install (simulated)")
                if validation == "permission-required" and consent:
                    observed_calls.append("helper --allow-install (simulated, separately authorised)")
            return {"RENDERED": encoded, "ARTIFACTS": manifest_text, "VALIDATION": validation_text, "DELIVERABLE": deliverable}
        if output == ("EFFECTS",):
            require(deliverable and authorised and ready, "non-deliverable work reached apply-changes")
            require(values["ARTIFACTS"] == manifest_text and values["WORK"] == encoded, "effects received different artifacts")
            return {"EFFECTS": NO_EFFECTS}
        if output == ("DRAFT", *VIEW_FIELDS):
            require(values["WORK"] == encoded, "composition invented a second model")
            return {"DRAFT": encoded, **(response_views or _fixture_views(work))}
        if output == ("LEGACY", "OAK"):
            published = json.loads(values["ARTIFACTS"])
            use_legacy = legacy and deliverable and len(published["documents"]) == 1
            return {"LEGACY": use_legacy, "OAK": published["documents"][0]["content"] if use_legacy else ""}
        raise RuntimeError(f"unexpected native action {output}")

    if arrival_event:
        arrival = Arrival(event="OAK authoring is requested for supplied source material.")
    elif legacy:
        arrival = Arrival(interface="interface.authoring-input", values={"SOURCE": work["request"]["text"], "VALIDATE": requested})
    else:
        arrival = Arrival(interface="interface.conversation-input", values={"REQUEST": work["request"]["text"],
            "PRIOR": prior, "CONTEXT": "{}", "VALIDATE": requested})
    result = execute(node, arrival, {}, act=native, source=source, load=load)
    require(result.state == {} and len(result.emissions) == 1, "authoring must emit once without state")
    validation_reached = any(output == ("RENDERED", "ARTIFACTS", "VALIDATION", "DELIVERABLE") for output, _ in trace)
    require(bool(observed_calls) == (requested and validation_reached and validation != "missing-execution"),
            "unrequested, unavailable or blocked helper simulation")
    return result.emissions, trace, observed_calls


def exercise_authoring_fixtures(documents: dict[str, str], fused: Node) -> None:
    """Compare actual modular/fused/native executions using the same offline decisions."""
    first, second = _fact_draft(), _fact_draft(complete=True)
    check_intent_specimens(first, second, _FACT_VIEWS)
    rejects(lambda: Node.model_validate(first["documents"][0]["node"]), "value")
    require("value" not in first["documents"][0]["node"]["constants"][1], "missing meaning was fabricated")
    expected = '<instructions>\nConstants hold values that do not change while the knowledge runs.\n</instructions>\n\n<constants>\nservice-name: "Cedar"\n\nsupport-hours: "09:00-17:00"\n\ntimezone: "Australia/Brisbane"\n</constants>\n'
    require(render(Node.model_validate(second["documents"][0]["node"])) + "\n" == expected, "E02 exact values changed")
    forms = [(parse(documents[ENTRY]), ENTRY, documents.get), (fused, None, None)]
    forms.extend((parse(body), None, None) for body in native_bodies(artifacts()))
    first_results = [_simulate(node, first, source=source, load=load) for node, source, load in forms]
    require(all(result == first_results[0] for result in first_results), "first-turn form parity failed")
    first_values = dict(first_results[0][0][0].values)
    require({key: first_values[key] for key in VIEW_FIELDS} == _FACT_VIEWS, "E02 first views changed")
    require(first_values["ARTIFACTS"] == EMPTY_MANIFEST and first_values["EFFECTS"] == NO_EFFECTS,
            "E02 unresolved work produced effects or artifacts")
    require(first_values["VALIDATION"] == "Programmatic validation was not performed (not requested).", "E02 false validation claim")
    next_results = [_simulate(node, second, source=source, load=load, prior=first_values["DRAFT"])
                    for node, source, load in forms]
    require(all(result == next_results[0] for result in next_results), "second-turn form parity failed")
    result = dict(next_results[0][0][0].values)
    require(json.loads(result["DRAFT"])["id"] == "fact-card-1" and LEGEND in result["INTENT_AST"], "continuity/legend lost")
    require(result["NEXT_DECISION"] == "" and json.loads(result["ARTIFACTS"])["documents"][0]["content"] == expected,
            "guided release did not deliver the exact agreed facts")
    direct = deepcopy(second)
    direct["request"]["mode"] = "direct"
    _check_validation_turns(forms, documents, direct)
    _check_crud_turns(forms, direct)
    _check_kind_turns(forms, direct)
    _check_blocked_turns(forms, documents, first, direct)


def _check_validation_turns(forms, documents: dict[str, str], direct: dict) -> None:
    for requested, status, consent, deliverable in (
        (False, "not-requested", False, True), (True, "passed", False, True),
        (True, "installation-declined", False, True), (True, "permission-required", True, True),
        (True, "unavailable", False, True), (True, "failed", False, False),
        (True, "identity-mismatch", False, False),
        (True, "missing-execution", False, True), (True, "permission-required", False, True),
        (True, "required-not-performed", False, False), (True, "stale-subject", False, False),
        (True, "repaired-and-passed", False, True),
    ):
        results = [_simulate(node, direct, source=source, load=load, legacy=True, requested=requested,
                            validation=status, consent=consent, deliverable=deliverable) for node, source, load in forms[:2]]
        require(results[0] == results[1], "legacy validation/consent parity changed")
        event = _simulate(forms[0][0], direct, source=ENTRY, load=documents.get, legacy=True, requested=requested,
                          validation=status, consent=consent, deliverable=deliverable, arrival_event=True)
        require(event[0] == results[0][0], "legacy natural and typed arrivals differ")
        require(not any(output == ("EFFECTS",) for output, _ in results[0][1]) or deliverable,
                "failed validation reached effects")
        require(any("--allow-install" in call for call in results[0][2]) == consent,
                "installation consent simulation changed")


def _check_crud_turns(forms, direct: dict) -> None:
    for operation in ("create", "read", "update", "delete"):
        fixture = deepcopy(direct)
        fixture["request"]["operation"] = operation
        results = [_simulate(node, fixture, source=source, load=load) for node, source, load in forms[:2]]
        require(results[0] == results[1], f"{operation} form parity changed")
        require(not any("guided satisfaction" in str(values) for _, values in results[0][1]), "direct operation interviewed")
        if operation == "read":
            require(not any(output == ("EFFECTS",) for output, _ in results[0][1]), "read acquired effects")
            require(json.loads(results[0][0][0].values["ARTIFACTS"]) == {"documents": [], "deletions": []}, "read rewrote input")


def _check_kind_turns(forms, direct: dict) -> None:
    for request_text, kind in CATALOGUE_CASES:
        fixture = deepcopy(direct)
        fixture["kind"] = kind
        fixture["request"]["text"] = request_text
        expected_node = _kind_node(kind)
        fixture["documents"] = [{"path": "example.oak.md", "node": expected_node.model_dump(mode="json", by_alias=True)}]
        fixture["outputs"] = [{"path": "example.oak.md", "format": "oak", "document": "example.oak.md", "source": None}]
        fixture["scope"].update(documents=["example.oak.md"], selectors=[], destination="response", effects=[], reference_boundary=[])
        fixture["sources"] = [{"id": "user-3", "identity": None, "locator": "user:3", "text": request_text, "read": "complete"}]
        fixture["annotations"] = [{"id": "K1", "document": "", "pointer": "/kind", "status": "confirmed",
                                    "meaning": kind, "question": "", "evidence": ["user:3"]}]
        fixture["changes"] = []
        fixture["source_map"] = [{"source": "user-3", "clause": request_text, "document": "example.oak.md",
                                    "annotations": ["K1"], "disposition": "preserved", "reason": "Independent kind specimen."}]
        fixture["authority"] = {"requests": [{"reference": "user:3", "purpose": request_text, "documents": ["example.oak.md"],
                                                "selectors": [], "effects": []}], "guided_release": False, "release_reference": ""}
        part_lines = [f"└─ {part}: {', '.join(entry.id for entry in getattr(expected_node, part))}"
                      for part in ("constants", "state", "processes") if getattr(expected_node, part)]
        views = {"UNDERSTANDING": f"Prepare {request_text} as {kind}.",
                 "INTENT_AST": "\n".join([f"example.oak.md [{kind}] ✓ [K1]", *part_lines, "", LEGEND]),
                 "CHANGES": "Prepared the requested kind.", "NEXT_DECISION": "", "READINESS": "Reviewed specimen."}
        check_draft(json.dumps(fixture), messages=frozenset({"user:3"}))
        check_view(fixture, views["INTENT_AST"])
        results = [_simulate(node, fixture, source=source, load=load, response_views=views) for node, source, load in forms]
        require(all(result == results[0] for result in results), f"{kind} delivery parity changed")
        delivered = json.loads(results[0][0][0].values["ARTIFACTS"])["documents"][0]["content"]
        require(parse(delivered) == expected_node, f"{kind} specimen meaning changed")
        require(bool(expected_node.state) == (kind == "stateful-skill"), "kind invented or lost state")
        if kind in ("compact-knowledge", "agents-md"):
            require(not any((expected_node.processes, expected_node.triggers, expected_node.interfaces)), "fixed knowledge acquired a workflow")


def _check_blocked_turns(forms, documents: dict[str, str], first: dict, direct: dict) -> None:
    multiple = deepcopy(direct)
    multiple["outputs"].append({**multiple["outputs"][0], "path": "second.oak.md"})
    result, trace, _ = _simulate(forms[0][0], multiple, source=ENTRY, load=documents.get, legacy=True)
    require(result[0].interface == "interface.conversation-output" and result[0].values["ARTIFACTS"] == EMPTY_MANIFEST,
            "multi-file legacy request fabricated a successful OAK result")
    require(not any(output == ("EFFECTS",) for output, _ in trace), "unsupported legacy request acquired effects")

    unreadable = deepcopy(first)
    unreadable["request"].update(mode="direct", operation="read")
    for node, source, load in forms:
        result, trace, calls = _simulate(node, unreadable, source=source, load=load, requested=True, validation="failed", deliverable=False)
        require(bool(calls) and result[0].values["ARTIFACTS"] == EMPTY_MANIFEST, "partial read could not report requested validation")
        require(not any(output == ("EFFECTS",) for output, _ in trace), "invalid read repaired files")
        _, trace, calls = _simulate(node, direct, source=source, load=load, authorised=False)
        require(not calls and not any(output == ("EFFECTS",) for output, _ in trace), "unauthorised request crossed a gate")


def _kind_node(kind: str) -> Node:
    """Return independent minimal outcomes for the twelve supplied intent cases."""
    if kind == "compact-knowledge":
        return Node(constants=[Constant(id="service", value="Cedar")])
    if kind == "agents-md":
        return Node(constants=[Constant(id="owned-concern", value="Repository test conventions.")])
    if kind == "stateful-skill":
        return Node(constants=[Constant(id="persistence", value="The host restores pending before each arrival and stores only successful state.")],
                    state=[State(id="pending", value=[])])
    instruction = {
        "agent": "Review supplied changes without editing files; return findings to the parent.",
        "single-shot-prompt": "Classify the supplied text once as positive, neutral or negative.",
        "skill": "Apply the supplied reusable procedure to the requested input and return its result.",
    }[kind]
    return Node(processes=[Process(id="perform-task", name="Perform task", body=[ACT(instruction)])])
