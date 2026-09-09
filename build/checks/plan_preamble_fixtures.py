"""Independent Intent-first examples and prospective adoption rejections."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from build.checks.plan_fixtures import DIRECTORY_EXAMPLE
from build.checks.plan_preamble import read_plan_opening
from build.checks.plans import validate_plan_directory, validate_plan_text

_HEADER = '''---
title: "Preserve one shared operation"
prepared: 2026-09-08T10:00:00Z
classification: PUBLIC
plan: 0018-example
readiness: Ready for implementation review, not approval
---
'''
_INTENT = "## Intent\n\nKeep one owner without changing the shared operation's behaviour.\n\n"
_BODY = (
    "## 1. Situation\n\nTwo callers duplicate one operation.\n\n"
    "## 2. Mission\n\nExtract the operation and preserve both callers.\n\n"
    "End state: Both callers use the reviewed helper.\n\n"
    + DIRECTORY_EXAMPLE + "\n"
    "## 3. Execution\n\nConcept of operations: Extract, verify, then review.\n\n"
    "### Phase 1: Verify the shared operation\n"
    "Objective: Establish unchanged results.\n"
    "- [ ] Key task: P01.01 Compare both callers with the fixed expected results.\n"
    "Success criteria: Both callers return the expected results.\n"
    "Transition trigger: The reviewed change is ready for its next decision.\n\n"
    "## 4. Admin and Logistics\n\nUse the supplied fixture and preserve its history.\n\n"
    "## 5. Command and Signal\n\nThe operator owns approval; this specimen grants none.\n"
)
_PLAN = _HEADER + "\n" + _INTENT + _BODY
_LEGACY = "# Preserved legacy plan\n\n" + _BODY


def _require_rejection(operation: Callable[[], object], reason: str) -> None:
    try:
        operation()
    except ValueError as error:
        if reason not in str(error):
            raise RuntimeError(f"expected preamble rejection {reason!r}, got {error}") from error
    else:
        raise RuntimeError(f"invalid planning preamble was accepted: {reason}")


def validate_preamble_examples(template: str) -> None:
    """Exercise valid metadata, rejected structures, and unchanged historical gates."""
    if not template.startswith("---\ntitle: <PLAN_TITLE>\nprepared: <TIMESTAMP>\nclassification: <CLASSIFICATION>\n---\n"):
        raise RuntimeError("SMEAC metadata differs from the independent frontmatter specimen")
    if template.count("## Intent\n") != 1 or template.count("<LEADERS_INTENT>") != 1:
        raise RuntimeError("SMEAC must own one Intent section and one intent binding")
    if not template.index("## Intent\n") < template.index("<LEADERS_INTENT>") < template.index("## 1. Situation"):
        raise RuntimeError("SMEAC intent must precede Situation")
    if "Intent: <LEADERS_INTENT>" in template:
        raise RuntimeError("SMEAC duplicated intent under Execution")
    validate = lambda text: validate_plan_text(text, template, require_directories=True, require_preamble=True)
    validate(_PLAN)
    validate(_PLAN.replace("\n", "\r\n"))
    validate(_PLAN.replace('"Preserve one shared operation"', '\'Title: "quoted" # literal\''))
    validate(_PLAN.replace('"Preserve one shared operation"', '"true"'))
    validate(_PLAN.replace('"Preserve one shared operation"', '"2026-09-08"'))
    validate(_PLAN.replace('"Preserve one shared operation"', '>\n  Preserve one\n  shared operation'))
    validate(_PLAN.replace("readiness: Ready for implementation review, not approval", "notes: |-\n  ## 1. Situation\n  # A literal metadata value"))
    validate(_PLAN.replace("Two callers duplicate one operation.", "Two callers duplicate one operation.\n```markdown\n## Intent\nIntent: inert specimen\n```"))
    opening = read_plan_opening(_PLAN)
    if opening.metadata["title"] != "Preserve one shared operation" or opening.metadata["plan"] != "0018-example":
        raise RuntimeError("frontmatter lost its decoded title or plan identity")
    if opening.metadata["prepared"] != datetime(2026, 9, 8, 10, tzinfo=timezone.utc):
        raise RuntimeError("frontmatter changed the prepared instant")
    if opening.body != "\n" + _INTENT + _BODY:
        raise RuntimeError("frontmatter reading changed the literal plan body")
    _invalid_preamble_examples(validate)
    _preamble_adoption_examples(template)


def _invalid_preamble_examples(validate: Callable[[str], None]) -> None:
    invalid = (
        (_PLAN.removeprefix("---\n"), "leading YAML"),
        (_PLAN.replace("\n---\n", "\n", 1), "closing delimiter"),
        (_PLAN.replace('title: "Preserve one shared operation"', "title: [unfinished"), "malformed YAML"),
        ("---\n- a sequence\n---\n" + _INTENT + _BODY, "nonempty mapping"),
        ("---\n---\n" + _INTENT + _BODY, "nonempty mapping"),
        (_PLAN.replace("classification: PUBLIC", "classification: PUBLIC\nclassification: INTERNAL"), "duplicate plan metadata"),
        (_PLAN.replace("classification: PUBLIC\n", ""), "missing required fields"),
        (_PLAN.replace('title: "Preserve one shared operation"', 'title: ""'), "populated or omitted"),
        (_PLAN.replace('title: "Preserve one shared operation"', "title: null"), "string scalars"),
        (_PLAN.replace('title: "Preserve one shared operation"', "title: true"), "string scalars"),
        (_PLAN.replace("plan: 0018-example", "plan: [0018-example]"), "values must be scalars"),
        (_PLAN.replace("plan: 0018-example", "true: invalid-key"), "keys must be nonempty strings"),
        (_PLAN.replace("plan: 0018-example", '"": invalid-key'), "keys must be nonempty strings"),
        (_PLAN.replace("plan: 0018-example", "<<: {plan: 0018-example}"), "without merges"),
        (_PLAN.replace("classification: PUBLIC", "classification: SECRET"), "classification"),
        (_PLAN.replace("prepared: 2026-09-08T10:00:00Z", "prepared: yesterday"), "ISO datetime"),
        (_PLAN.replace("prepared: 2026-09-08T10:00:00Z", "prepared: 2026-09-08T10:00:00"), "explicit timezone"),
        (_PLAN.replace("plan: 0018-example", "plan: 2026-09-08T10:00:00Z"), "quote date-like"),
        (_PLAN.replace('"Preserve one shared operation"', '"<PLAN_TITLE>"'), "unfilled SMEAC placeholder"),
        (_PLAN.replace(_INTENT, ""), "start with Intent"),
        (_PLAN.replace(_INTENT, "Prepared: 2026-09-08\n" + _INTENT), "start with Intent"),
        (_PLAN.replace(_INTENT, "# Extra body title\n" + _INTENT), "start with Intent"),
        (_PLAN.replace(_INTENT, "## Intent\n\n"), "populated content"),
        (_PLAN.replace(_INTENT, _INTENT * 2), "five SMEAC sections"),
        (_PLAN.replace(_INTENT, "").replace("## 2. Mission", _INTENT + "## 2. Mission"), "start with Intent"),
        (_PLAN.replace("Concept of operations:", "Intent: Duplicate intent.\nConcept of operations:"), "intent belongs only"),
        (_PLAN.replace("Concept of operations:", "# Extra title\nConcept of operations:"), "title belongs in metadata"),
        (_PLAN.replace("## 2. Mission", "## Missing mission"), "five SMEAC sections"),
        (_PLAN.replace("- [ ] Key task:", "- Key task:"), "checkbox"),
        (_PLAN.replace(DIRECTORY_EXAMPLE, ""), "requires Directory Changes"),
        (_PLAN + "\n```", "unclosed code fence"),
    )
    for text, reason in invalid:
        _require_rejection(lambda: validate(text), reason)


def _preamble_adoption_examples(template: str) -> None:
    with TemporaryDirectory(prefix="oak-preamble-adoption-") as temporary:
        repository = Path(temporary)
        root = repository / "docs" / "plans"
        historical, legacy, current = (root / name for name in ("0000-old", "0017-legacy", "0018-current"))
        for directory, text in ((historical, "# Preserved original format"), (legacy, _LEGACY), (current, _PLAN)):
            directory.mkdir(parents=True)
            (directory / "plan.md").write_text(text, encoding="utf-8")
        validate = lambda: validate_plan_directory(root, template, {historical.name}, directory_first=16, preamble_first=18)
        validate()
        if (legacy / "plan.md").read_text() != _LEGACY:
            raise RuntimeError("preamble adoption changed a historical plan")
        (current / "plan.md").write_text(_LEGACY, encoding="utf-8")
        _require_rejection(validate, "leading YAML")
        (current / "plan.md").write_text(_PLAN, encoding="utf-8")
        (legacy / "plan.md").write_text(_LEGACY.replace("- [ ] Key task:", "- Key task:"), encoding="utf-8")
        _require_rejection(validate, "checkbox")
        (legacy / "plan.md").write_text(_LEGACY, encoding="utf-8")
        (current / "plan.md").write_text(_PLAN + "\n[Missing source](absent.md)\n", encoding="utf-8")
        _require_rejection(validate, "broken navigational reference")
        (current / "plan.md").write_text(_PLAN, encoding="utf-8")
        report = current / "report.md"
        report.write_text("---\nplan: absent.md\n---\n# Report\nNo result is claimed.\n", encoding="utf-8")
        _require_rejection(validate, "broken navigational reference")
        report.write_text("# Report\n[Plan](plan.md)\n", encoding="utf-8")
        validate()
