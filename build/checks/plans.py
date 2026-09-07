"""Persistent plan storage and SMEAC structure verification."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit

from build.checks.fixtures import ROOT
from examples.schemas.smeac_plan import ComparisonAuthority, NO_DIRECTORY_CHANGES
from oak import Node, Schema, SchemaBindingError, parse, render

_DIRECTORY = re.compile(r"([0-9]{4})-[a-z][a-z0-9]*(?:-[a-z0-9]+)*")
_PHASE = re.compile(r"### Phase ([1-9][0-9]*): \S.*")
_TASK = re.compile(r"- \[[ xX]\] Key task: ([A-Z][A-Z0-9._-]*[0-9]) \S.*")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_LINK = re.compile(r"\[[^\]\n]*\]\(([^\s)]+)\)")
_COMPARISON = re.compile(r"#### (E[0-9]{2,}): \S.*")
_COMPARISON_ID = re.compile(r"\bE[0-9]{2,}\b")


def _closes_fence(fence: str, marker: re.Match[str] | None) -> bool:
    return bool(marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip())


def _prose_lines(text: str) -> list[str]:
    """Mask fenced examples while preserving their original line positions."""
    lines = []
    fence: str | None = None
    for line in text.splitlines():
        lines.append("")
        marker = _FENCE.fullmatch(line)
        if fence is not None:
            if _closes_fence(fence, marker):
                fence = None
        elif marker:
            fence = marker[1]
        else:
            lines[-1] = line
    if fence is not None:
        raise ValueError("unclosed code fence")
    return lines


def _format_parts(template: str) -> tuple[list[str], list[str]]:
    sections = [line for line in template.splitlines() if line.startswith("## ")]
    phase = template.split("### Phase ", 1)[1].split("\n...\n", 1)[0]
    labels = [line.split(":", 1)[0] + ":" for line in phase.splitlines()[1:]
              if line and not line.startswith(("-", " ", "."))]
    if len(sections) != 5 or len(labels) != 3:
        raise ValueError("SMEAC schema must define five sections and three phase labels")
    return sections, labels


def _comparison_format(template: str) -> tuple[str, tuple[str, ...]]:
    prefix, pattern = template.split("#### <COMPARISON_ID>:", 1)
    heading = next(line for line in reversed(prefix.splitlines()) if line.startswith("### "))
    fields = tuple(line.split(":", 1)[0] + ":" for line in pattern.split("\n...\n", 1)[0].splitlines()
                   if ":" in line)
    if len(fields) != 4:
        raise ValueError("SMEAC comparisons must define authority, current state, desired state, and acceptance")
    return heading, fields


def _field_content(raw: list[str], field: str, concern: str) -> str:
    content = [raw[0][len(field):], *raw[1:]]
    if not any(line.strip() and not _FENCE.fullmatch(line) for line in content):
        raise ValueError(f"{concern} needs populated {field}")
    return "\n".join(content).strip()


def _field_contents(
    prose: list[str], raw: list[str], fields: tuple[str, ...], *, concern: str,
) -> list[str]:
    positions = [(index, field) for index, line in enumerate(prose) for field in fields
                 if line == field or line.startswith(field + " ")]
    if tuple(field for _, field in positions) != fields:
        raise ValueError(f"{concern} needs each schema field once, in order")
    contents: list[str] = []
    for position, (start, field) in enumerate(positions):
        end = positions[position + 1][0] if position + 1 < len(positions) else len(raw)
        contents.append(_field_content(raw[start:end], field, concern))
    return contents


def _comparison_authority(prose: list[str], raw: list[str], fields: tuple[str, ...]) -> ComparisonAuthority:
    contents = _field_contents(prose, raw, fields, concern="comparison")
    try:
        return ComparisonAuthority(contents[0])
    except ValueError as error:
        raise ValueError("comparison authority must be required or illustrative") from error


def _mission_bounds(prose: list[str], sections: list[str]) -> tuple[int, int]:
    if sections[1] not in prose or sections[2] not in prose:
        raise ValueError("plan needs Mission and Execution boundaries")
    return prose.index(sections[1]), prose.index(sections[2])


def _comparison_bounds(prose: list[str], heading: str, sections: list[str]) -> tuple[int, int] | None:
    starts = [index for index, line in enumerate(prose) if line == heading]
    if not starts:
        return None
    mission_start, mission_end = _mission_bounds(prose, sections)
    if len(starts) != 1 or not mission_start < starts[0] < mission_end:
        raise ValueError("state comparisons must occur once within Mission")
    start = starts[0]
    end = next((index for index in range(start + 1, mission_end)
                if prose[index].startswith("### ")), mission_end)
    return start, end


def _comparison_authorities(prose: list[str], raw: list[str], template: str) -> dict[str, ComparisonAuthority]:
    heading, fields = _comparison_format(template)
    sections, _ = _format_parts(template)
    bounds = _comparison_bounds(prose, heading, sections)
    if bounds is None:
        return {}
    start, end = bounds
    entries = [index for index in range(start + 1, end) if prose[index].startswith("#### ")]
    if not entries:
        raise ValueError("state comparisons need at least one named example")
    authorities: dict[str, ComparisonAuthority] = {}
    for position, index in enumerate(entries):
        match = _COMPARISON.fullmatch(prose[index])
        if match is None:
            raise ValueError("comparison needs an E01-style identifier and a populated name")
        identifier = match[1]
        if identifier in authorities:
            raise ValueError(f"duplicate comparison identifier {identifier}")
        stop = entries[position + 1] if position + 1 < len(entries) else end
        authorities[identifier] = _comparison_authority(prose[index + 1:stop], raw[index + 1:stop], fields)
    return authorities


def _validate_comparisons(text: str, prose: list[str], template: str) -> None:
    authorities = _comparison_authorities(prose, text.splitlines(), template)
    if not authorities:
        return  # Older plans use E-prefixed task identifiers.
    sections, labels = _format_parts(template)
    execution = prose[prose.index(sections[2]) + 1:prose.index(sections[3])]
    referenced = set(_COMPARISON_ID.findall("\n".join(execution)))
    if unknown := referenced - authorities.keys():
        raise ValueError(f"execution refers to unknown comparisons: {sorted(unknown)}")
    criteria = "\n".join(line for line in execution if line.startswith(labels[1] + " "))
    covered = set(_COMPARISON_ID.findall(criteria))
    required = {identifier for identifier, authority in authorities.items() if authority == ComparisonAuthority.REQUIRED}
    if missing := required - covered:
        raise ValueError(f"success criteria omit required comparisons: {sorted(missing)}")


def _directory_format(template: str) -> tuple[str, tuple[str, ...], str]:
    """Read field order and the fixed legend from the actual SMEAC template."""
    prefix, _ = template.split("<DIRECTORY_BASELINE>", 1)
    heading = next(line for line in reversed(prefix.splitlines()) if line.startswith("### "))
    body = template.split(heading + "\n", 1)[1].split("\n### ", 1)[0]
    prose = _prose_lines(body)
    fields = tuple(line.split(":", 1)[0] + ":" for line in prose if ":" in line)
    if len(fields) != 6 or len(set(fields)) != 6:
        raise ValueError("SMEAC directory view needs five fields and one fixed legend")
    legend = next(line for line in prose if line.startswith(fields[1] + " "))
    return heading, fields, legend


def _directory_bounds(prose: list[str], template: str, *, required: bool) -> tuple[int, int] | None:
    heading, _, _ = _directory_format(template)
    starts = [index for index, line in enumerate(prose) if line == heading]
    if not starts:
        if required:
            raise ValueError("plan requires Directory Changes")
        return None
    sections, _ = _format_parts(template)
    mission_start, mission_end = _mission_bounds(prose, sections)
    if len(starts) != 1 or not mission_start < starts[0] < mission_end:
        raise ValueError("Directory Changes must occur once within Mission")
    start = starts[0]
    _require_directory_position(prose[mission_start:start], template)
    end = next((i for i in range(start + 1, mission_end) if prose[i].startswith("### ")), mission_end)
    return start, end


def _require_directory_position(before: list[str], template: str) -> None:
    comparison, _ = _comparison_format(template)
    if not any(line.startswith("End state: ") for line in before) or comparison in before:
        raise ValueError("Directory Changes belongs after End state and before State Comparisons")


def _directory_view(content: str, label: str) -> str:
    """Check one text fence, not the directory tree's syntax or truth."""
    lines = content.splitlines()
    if len(lines) < 3:
        raise ValueError(f"directory {label} needs one populated text fence")
    opening, closing = _FENCE.fullmatch(lines[0]), _FENCE.fullmatch(lines[-1])
    if opening is None or opening[2].strip() != "text":
        raise ValueError(f"directory {label} needs one populated text fence")
    if not _closes_fence(opening[1], closing):
        raise ValueError(f"directory {label} needs one closed text fence")
    if any(_FENCE.fullmatch(line) for line in lines[1:-1]):
        raise ValueError(f"directory {label} needs exactly one text fence")
    view = "\n".join(lines[1:-1]).strip()
    if not view:
        raise ValueError(f"directory {label} is empty")
    return view


def _directory_annotations(current: str, planned: str) -> None:
    """Reject incomplete annotations; never reconstruct paths or compare a diff."""
    no_change = (current == NO_DIRECTORY_CHANGES, planned == NO_DIRECTORY_CHANGES)
    if no_change[0] != no_change[1]:
        raise ValueError("no-change wording must occupy both directory views")
    for view in (current, planned):
        if NO_DIRECTORY_CHANGES in view and view != NO_DIRECTORY_CHANGES:
            raise ValueError("no-change wording cannot be mixed with changed paths")
        if re.search(r"(?m)^[\s│├└─]*(?:\.\.\.|…)(?:\s*#.*)?$", view):
            raise ValueError("directory views must not hide affected leaves with ellipses")
        for marker in re.findall(r"\[move(?:\s+[^\]]*)?\]", view):
            source = marker.removeprefix("[move from ").removesuffix("]").strip()
            if not marker.startswith("[move from ") or not source or source == "PATH":
                raise ValueError("move annotation needs its original source path")


def _validate_directory_changes(text: str, prose: list[str], template: str, *, required: bool) -> None:
    bounds = _directory_bounds(prose, template, required=required)
    if bounds is None:
        return
    _, fields, legend = _directory_format(template)
    start, end = bounds
    contents = _field_contents(prose[start + 1:end], text.splitlines()[start + 1:end], fields, concern="directory view")
    slots = set(re.findall(r"<([A-Z][A-Z0-9_]*)>", template))
    markers = re.findall(r"<([A-Z][A-Z0-9_]*)>", "\n".join(contents))
    if slots.intersection(markers) or any(marker.startswith("DIRECTORY_") for marker in markers):
        raise ValueError("directory view retains an unfilled placeholder")
    if fields[1] + " " + contents[1] != legend:
        raise ValueError("directory legend differs from the schema")
    current, planned = (_directory_view(contents[i], fields[i]) for i in (2, 3))
    _directory_annotations(current, planned)


def validate_plan_text(text: str, template: str, *, require_directories: bool = False) -> None:
    """Check a populated plan's structure, execution phases, and paired examples."""
    lines = _prose_lines(text)
    sections, labels = _format_parts(template)
    headings = [(index, line) for index, line in enumerate(lines) if line.startswith("## ")]
    if [line for _, line in headings] != sections:
        raise ValueError("plan must contain the five SMEAC sections once, in schema order")
    if not any(re.fullmatch(r"# \S.*", line) for line in lines):
        raise ValueError("plan needs a populated title")
    slots = set(re.findall(r"<([A-Z][A-Z0-9_]*)>", template))
    if slots.intersection(re.findall(r"<([A-Z][A-Z0-9_]*)>", "\n".join(lines))):
        raise ValueError("plan retains an unfilled SMEAC placeholder")
    for position, (start, _) in enumerate(headings):
        end = headings[position + 1][0] if position + 1 < len(headings) else len(lines)
        if not any(line.strip() and not line.startswith("#") for line in lines[start + 1:end]):
            raise ValueError("SMEAC sections must contain populated content")

    execution = lines[headings[2][0] + 1:headings[3][0]]
    phase_count = 0
    identifiers: set[str] = set()
    for start, line in enumerate(execution):
        if not line.startswith("### Phase "):
            continue
        phase = _PHASE.fullmatch(line)
        phase_count += 1
        if phase is None or int(phase[1]) != phase_count:
            raise ValueError("phase headings need consecutive numbers starting at one")
        end = next((index for index in range(start + 1, len(execution))
                    if execution[index].startswith("### ")), len(execution))
        body = execution[start + 1:end]
        while body and not body[-1].strip():
            body.pop()
        if len(body) < 4 or any(not item.strip() for item in body):
            raise ValueError("phase needs compact adjacent fields and at least one checkbox task")
        for item, label in zip((body[0], body[-2], body[-1]), labels, strict=True):
            if not item.startswith(label + " ") or not item[len(label):].strip():
                raise ValueError(f"phase needs a populated plain {label} line")
        for item in body[1:-2]:
            task = _TASK.fullmatch(item)
            if task is None:
                raise ValueError("key tasks need a checkbox, a stable identifier such as P01.01, and text")
            if task[1] in identifiers:
                raise ValueError(f"duplicate task identifier {task[1]}")
            identifiers.add(task[1])
    if not phase_count:
        raise ValueError("execution needs at least one phase")
    _validate_directory_changes(text, lines, template, required=require_directories)
    _validate_comparisons(text, lines, template)


def _validate_navigation(path: Path, root: Path) -> None:
    lines = _prose_lines(path.read_text(encoding="utf-8"))
    targets = [match[1] for match in _LINK.finditer("\n".join(lines))]
    targets.extend(line.split(": ", 1)[1] for line in lines
                   if line.startswith(("plan: ", "target_path: ")))
    for target in targets:
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        relative = unquote(parsed.path)
        destination = (root if relative.startswith("docs/") else path.parent) / relative
        if not destination.is_file():
            raise ValueError(f"broken navigational reference in {path.name}: {target}")


def _validate_record_files(directory: Path, repository: Path) -> None:
    entries = {path.name for path in directory.iterdir()}
    if "plan.md" not in entries:
        raise ValueError(f"{directory.name} needs plan.md")
    if entries - {"plan.md", "report.md", "evidence"}:
        raise ValueError(f"unexpected plan files in {directory.name}")
    for filename in entries & {"plan.md", "report.md"}:
        path = directory / filename
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            raise ValueError(f"{directory.name}/{filename} must be a non-empty file")
        _validate_navigation(path, repository)
    if "evidence" in entries:
        _require_evidence_files(directory / "evidence")


def _require_evidence_files(evidence: Path) -> None:
    if not evidence.is_dir() or not any(path.is_file() for path in evidence.rglob("*")):
        raise ValueError(f"{evidence.parent.name}/evidence must contain supporting files")


def _validate_record_plan(directory: Path, template: str, *, historical: bool, required: bool) -> None:
    text = (directory / "plan.md").read_text(encoding="utf-8")
    try:
        if not historical:
            validate_plan_text(text, template, require_directories=required)
        elif required:
            _validate_directory_changes(text, _prose_lines(text), template, required=True)
    except ValueError as error:
        raise ValueError(f"{directory.name}/plan.md: {error}") from None


def validate_plan_directory(
    root: Path, template: str, historical: set[str], *,
    directory_first: int | None = None, reopened: frozenset[str] = frozenset(),
) -> None:
    """Require one stable named directory for each plan and its optional evidence."""
    identifiers: set[str] = set()
    discovered: set[str] = set()
    for directory in sorted(root.iterdir()):
        name = _DIRECTORY.fullmatch(directory.name)
        if not directory.is_dir() or name is None:
            raise ValueError(f"plan entry must be a numbered topic directory: {directory.name}")
        if name[1] in identifiers:
            raise ValueError(f"duplicate plan number {name[1]}")
        identifiers.add(name[1])
        discovered.add(directory.name)
        _validate_record_files(directory, root.parent.parent)
        required = directory.name in reopened or directory_first is not None and int(name[1]) >= directory_first
        _validate_record_plan(directory, template, historical=directory.name in historical, required=required)
    if historical - discovered:
        raise ValueError("historical format exceptions refer to missing plan directories")
    if reopened - discovered:
        raise ValueError("reopened directory policy refers to missing plan directories")


def _rejection_examples(template: str) -> None:
    sections, labels = _format_parts(template)
    phase = "\n".join((
        "### Phase 1: Verify the change", labels[0] + " Establish the result.",
        "- [ ] Key task: P01.01 Verify the result.",
        labels[1] + " The check passes.", labels[2] + " Verification is complete.",
    ))
    valid = "# Example plan\n" + "\n".join(
        heading + "\n" + (phase if index == 2 else "Populated section.")
        for index, heading in enumerate(sections)
    )
    validate_plan_text(valid, template)
    _comparison_examples(template, valid)
    _directory_examples(template, valid)
    _directory_adoption_examples(template, valid)
    task = "- [ ] Key task: P01.01 Verify the result."
    invalid = (
        (valid.replace(sections[1], "## Missing mission"), "five SMEAC sections"),
        (valid.replace("# Example plan", "Example plan"), "populated title"),
        (valid.replace("Populated section.", "", 1), "populated content"),
        (valid.replace(task, "- Key task: P01.01 Verify the result."), "checkbox"),
        (valid.replace("P01.01 Verify", "Verify"), "stable identifier"),
        (valid.replace(task, task + "\n" + task), "duplicate task identifier"),
        (valid.replace(labels[0], "- " + labels[0]), "plain " + labels[0]),
        (valid.replace(labels[1], "\n" + labels[1]), "compact adjacent fields"),
        (valid.replace("Phase 1:", "Phase 2:"), "consecutive numbers"),
        (valid.replace("Example plan", "<PLAN_TITLE>"), "unfilled SMEAC placeholder"),
        (valid.replace(phase, "Execution overview.\n```markdown\n" + phase + "\n```"), "at least one phase"),
        ("```markdown\n" + valid + "\n```", "five SMEAC sections"),
        (valid + "\n```", "unclosed code fence"),
    )
    for source, reason in invalid:
        try:
            validate_plan_text(source, template)
        except ValueError as error:
            if reason not in str(error):
                raise RuntimeError(f"expected plan rejection {reason!r}, got {error}") from None
            continue
        raise RuntimeError("invalid SMEAC plan structure was accepted")

    with TemporaryDirectory(prefix="oak-plan-check-") as temporary:
        root = Path(temporary)
        current = root / "0001-example"
        current.mkdir()
        plan = current / "plan.md"
        plan.write_text(valid, encoding="utf-8")
        old = root / "0000-historical"
        old.mkdir()
        (old / "plan.md").write_text("# Preserved historical plan", encoding="utf-8")
        historical = {old.name}
        validate_plan_directory(root, template, historical)
        candidates = (
            (root / "0002-plan.md", None, "numbered topic directory"),
            (root / "unnumbered", {}, "numbered topic directory"),
            (root / "0001-duplicate", {"plan.md": valid}, "duplicate plan number"),
            (root / "0002-missing-plan", {"report.md": "Orphan report"}, "needs plan.md"),
            (current / "unexpected.md", None, "unexpected plan files"),
            (current / "evidence", {}, "must contain supporting files"),
        )
        for candidate, children, reason in candidates:
            if children is None:
                candidate.write_text("unexpected", encoding="utf-8")
            else:
                candidate.mkdir()
                for filename, content in children.items():
                    (candidate / filename).write_text(content, encoding="utf-8")
            try:
                try:
                    validate_plan_directory(root, template, historical)
                except ValueError as error:
                    if reason not in str(error):
                        raise RuntimeError(f"expected storage rejection {reason!r}, got {error}") from None
                    continue
                raise RuntimeError(f"invalid plan storage was accepted: {candidate.name}")
            finally:
                if children is None:
                    candidate.unlink()
                else:
                    for filename in children:
                        (candidate / filename).unlink()
                    candidate.rmdir()
        (current / "report.md").write_text("Plan: [plan](missing.md)", encoding="utf-8")
        try:
            validate_plan_directory(root, template, historical)
        except ValueError as error:
            if "broken navigational reference" not in str(error):
                raise RuntimeError(f"unexpected navigation rejection: {error}") from None
        else:
            raise RuntimeError("broken plan navigation was accepted")
        (current / "report.md").write_text("Plan: [plan](plan.md)", encoding="utf-8")
        (current / "evidence").mkdir()
        (current / "evidence" / "result.txt").write_text("Observed result", encoding="utf-8")
        validate_plan_directory(root, template, historical)


def _comparison_examples(template: str, plan: str) -> None:
    current = "```markdown\n## Skill layout\n- `SKILL.md`: entry point\n```"
    desired = "```text\nSKILL_TREE:\n  SKILL.md→Skill entry point\n```"
    comparison = (
        "### State Comparisons\n\n"
        "#### E01: Skill tree notation\n"
        "Authority: required\n"
        f"Current state:\n{current}\n"
        f"Desired state:\n{desired}\n"
        "Acceptance: Preserve the colon, indentation, and arrow without adjacent spaces.\n\n"
    )
    paired = plan.replace("## 3. Execution", comparison + "## 3. Execution").replace(
        "The check passes.", "The E01 comparison matches its acceptance criteria."
    )
    validate_plan_text(paired, template)
    validate_plan_text(paired.replace("Authority: required", "Authority: illustrative").replace(
        "The E01 comparison", "The example"
    ), template)
    second = comparison.split("#### ", 1)[1].replace("E01:", "E02:").replace("required", "illustrative")
    validate_plan_text(paired.replace("## 3. Execution", "#### " + second + "## 3. Execution"), template)
    validate_plan_text(paired.replace(desired, "[Desired specimen](evidence/desired.txt)"), template)
    validate_plan_text(paired.replace("Current state:", "Observed state:"),
                       template.replace("Current state:", "Observed state:"))

    invalid = (
        (paired.replace(current, "```text\n\n```"), "populated Current state:"),
        (paired.replace(desired, ""), "populated Desired state:"),
        (paired.replace("Authority: required", "Authority: approved"), "required or illustrative"),
        (paired.replace("E01: Skill", "Skill"), "E01-style identifier"),
        (paired.replace("Current state:", "Desired state:"), "each schema field once"),
        (paired.replace("Acceptance: Preserve the colon, indentation, and arrow without adjacent spaces.", ""),
         "each schema field once"),
        (paired.replace("## 3. Execution", "#### " + second.replace("E02:", "E01:") + "## 3. Execution"),
         "duplicate comparison identifier"),
        (paired.replace("The E01 comparison", "The result"), "omit required comparisons"),
        (paired.replace("The E01 comparison", "The E99 comparison"), "unknown comparisons"),
        (paired.replace(comparison, "").replace("## 2. Mission", comparison + "## 2. Mission"),
         "once within Mission"),
        (paired.replace(comparison, "### State Comparisons\n~~~~markdown\n" + comparison + "~~~~\n"),
         "at least one named example"),
        (paired.replace("#### E01: Skill tree notation", ""), "at least one named example"),
    )
    for source, reason in invalid:
        try:
            validate_plan_text(source, template)
        except ValueError as error:
            if reason not in str(error):
                raise RuntimeError(f"expected comparison rejection {reason!r}, got {error}") from None
            continue
        raise RuntimeError(f"invalid state comparison was accepted: {reason}")


def _require_plan_rejection(operation: Callable[[], object], reason: str) -> None:
    try:
        operation()
    except ValueError as error:
        if reason not in str(error):
            raise RuntimeError(f"expected plan rejection {reason!r}, got {error}") from error
    else:
        raise RuntimeError(f"invalid directory plan was accepted: {reason}")


def _directory_examples(template: str, plan: str) -> None:
    from build.checks.plan_fixtures import (
        CURRENT_TREE, DIRECTORY_EXAMPLE, DIRECTORY_EXAMPLES, MOVE_EXAMPLE,
        NO_CHANGE_EXAMPLE, PLANNED_TREE,
    )

    entry = "End state: The approved fixture change is reviewed.\n\n" + DIRECTORY_EXAMPLE + "\n"
    paired = plan.replace("## 3. Execution", entry + "## 3. Execution")
    for example in DIRECTORY_EXAMPLES:
        validate_plan_text(paired.replace(DIRECTORY_EXAMPLE, example), template, require_directories=True)
    validate_plan_text(paired.replace("```text", "~~~~text").replace("```", "~~~~"), template,
                       require_directories=True)
    validate_plan_text(paired.replace("Current:", "Observed:"), template.replace("Current:", "Observed:"),
                       require_directories=True)
    validate_plan_text(paired.replace(CURRENT_TREE, CURRENT_TREE + "\nOwnership: inert tree text, not a field."),
                       template, require_directories=True)

    after_comparisons = paired.replace("### Directory Changes", "### State Comparisons\n### Directory Changes")
    invalid = (
        (paired.replace(DIRECTORY_EXAMPLE, ""), "requires Directory Changes"),
        (paired.replace(DIRECTORY_EXAMPLE, "~~~~markdown\n" + DIRECTORY_EXAMPLE + "~~~~\n"),
         "requires Directory Changes"),
        (paired.replace(DIRECTORY_EXAMPLE, DIRECTORY_EXAMPLE * 2), "once within Mission"),
        (paired.replace(entry, "").replace("## 2. Mission", entry + "## 2. Mission"), "once within Mission"),
        (paired.replace("End state: The approved fixture change is reviewed.\n", ""), "after End state"),
        (after_comparisons, "before State Comparisons"),
        (paired.replace("Ownership:", "Planned:"), "each schema field once"),
        (paired.replace("Current:", "Temporary:").replace("Planned:", "Current:").replace("Temporary:", "Planned:"),
         "each schema field once"),
        (paired.replace("Baseline: inspected fixture revision abc123.", "Baseline:"), "populated Baseline:"),
        (paired.replace("[keep] unchanged context; ", ""), "legend differs"),
        (paired.replace(CURRENT_TREE, ""), "populated Current:"),
        (paired.replace(PLANNED_TREE, "   \n   "), "populated Planned:"),
        (paired.replace("```text\n" + CURRENT_TREE + "\n```", CURRENT_TREE), "populated text fence"),
        (paired.replace("```text", "```python", 1), "populated text fence"),
        (paired.replace(CURRENT_TREE, CURRENT_TREE + "\n```\n```text\nsecond tree"), "exactly one text fence"),
        (paired.replace(PLANNED_TREE + "\n```", PLANNED_TREE), "unclosed code fence"),
        (paired.replace(PLANNED_TREE, "<DIRECTORY_PLANNED>"), "unfilled placeholder"),
        (paired.replace(CURRENT_TREE, "<PLAN_TITLE>"), "unfilled placeholder"),
        (paired.replace(PLANNED_TREE, "<TASK>"), "unfilled placeholder"),
        (paired.replace("fixture revision abc123.", "<DIRECTORY_BASELINE>"), "unfilled"),
        (paired.replace(PLANNED_TREE, "project/\n└── ... # hidden affected files"), "ellipses"),
        (paired.replace(DIRECTORY_EXAMPLE, MOVE_EXAMPLE.replace("[move from old.py]", "[move]")), "original source path"),
        (paired.replace(DIRECTORY_EXAMPLE, MOVE_EXAMPLE.replace("[move from old.py]", "[move from ]")), "original source path"),
        (paired.replace(DIRECTORY_EXAMPLE, MOVE_EXAMPLE.replace("[move from old.py]", "[move from PATH]")), "original source path"),
        (paired.replace(PLANNED_TREE, "No directory or file changes."), "both directory views"),
        (paired.replace(CURRENT_TREE, CURRENT_TREE + "\nNo directory or file changes."), "mixed with changed paths"),
        (paired.replace(DIRECTORY_EXAMPLE, NO_CHANGE_EXAMPLE.replace("Ownership: No changed source or output ownership.",
                                                                  "Ownership:")), "populated Ownership:"),
    )
    for source, reason in invalid:
        _require_plan_rejection(lambda: validate_plan_text(source, template, require_directories=True), reason)


def _directory_adoption_examples(template: str, plan: str) -> None:
    from build.checks.plan_fixtures import DIRECTORY_EXAMPLE

    paired = plan.replace("## 3. Execution", "End state: Reviewed fixture.\n" + DIRECTORY_EXAMPLE + "\n## 3. Execution")
    with TemporaryDirectory(prefix="oak-directory-adoption-") as temporary:
        root = Path(temporary)
        old, recent, current = (root / name for name in ("0000-old", "0015-recent", "0016-current"))
        for directory, text in ((old, "# Preserved old format"), (recent, plan), (current, paired)):
            directory.mkdir()
            (directory / "plan.md").write_text(text, encoding="utf-8")
        historical = {old.name}
        validate_plan_directory(root, template, historical, directory_first=16)
        if (old / "plan.md").read_text() != "# Preserved old format" or (recent / "plan.md").read_text() != plan:
            raise RuntimeError("prospective checking rewrote historical plans")
        (current / "plan.md").write_text(plan, encoding="utf-8")
        _require_plan_rejection(lambda: validate_plan_directory(root, template, historical, directory_first=16),
                                "requires Directory Changes")
        (current / "plan.md").write_text(paired, encoding="utf-8")
        _require_plan_rejection(
            lambda: validate_plan_directory(root, template, historical, directory_first=16, reopened=frozenset({recent.name})),
            "requires Directory Changes",
        )
        (recent / "plan.md").write_text(paired, encoding="utf-8")
        validate_plan_directory(root, template, historical, directory_first=16, reopened=frozenset({recent.name}))
        (recent / "plan.md").write_text(plan.replace("- [ ] Key task:", "- Key task:"), encoding="utf-8")
        _require_plan_rejection(lambda: validate_plan_directory(root, template, historical, directory_first=16), "checkbox")
        (recent / "plan.md").write_text(plan, encoding="utf-8")
        _require_plan_rejection(
            lambda: validate_plan_directory(root, template, historical, directory_first=16, reopened=frozenset({old.name})),
            "requires Directory Changes",
        )
        # Reopening adds the directory obligation, not unrelated historical format migration.
        (old / "plan.md").write_text(
            "# Old format\n## 2. Mission\nEnd state: Reviewed.\n" + DIRECTORY_EXAMPLE + "\n## 3. Execution\nOld record.",
            encoding="utf-8",
        )
        validate_plan_directory(root, template, historical, directory_first=16, reopened=frozenset({old.name}))
        _require_plan_rejection(
            lambda: validate_plan_directory(root, template, historical, directory_first=16, reopened=frozenset({"0014-missing"})),
            "missing plan directories",
        )


def _reject_directory_bindings(schema: Schema, slots: tuple[str, ...]) -> None:
    from build.checks.plan_fixtures import PLAN_VALUES

    for slot in slots:
        candidates = ({key: value for key, value in PLAN_VALUES.items() if key != slot},
                      {**PLAN_VALUES, slot: ""}, {**PLAN_VALUES, slot: 42})
        for values in candidates:
            try:
                schema.bind(values)
            except SchemaBindingError:
                continue
            raise RuntimeError(f"directory schema accepted a missing, empty or non-string {slot}")


def _directory_schema_examples(schema: Schema) -> None:
    from build.checks.plan_fixtures import PLAN_VALUES

    directory_slots = ("DIRECTORY_BASELINE", "DIRECTORY_CURRENT", "DIRECTORY_PLANNED",
                       "DIRECTORY_OWNERSHIP", "DIRECTORY_VERIFICATION")
    if {slot for slot in schema.placeholders if slot.startswith("DIRECTORY_")} != set(directory_slots):
        raise RuntimeError("SMEAC directory schema lost its five fields")
    if any(not field.description for field in schema.where if field.placeholder in directory_slots):
        raise RuntimeError("SMEAC directory fields need meaning beyond their string types")
    schema.bind(PLAN_VALUES)
    _reject_directory_bindings(schema, directory_slots)
    _directory_grouping_examples(schema)


def _directory_grouping_examples(schema: Schema) -> None:
    from build.checks.plan_fixtures import DIRECTORY_EXAMPLE, PLAN_VALUES

    for grouping in ("xml", "markdown"):
        text = render(Node(schemas=[schema]), grouping=grouping)
        recovered = parse(text)
        if recovered.schemas != [schema] or render(recovered, grouping=grouping) != text:
            raise RuntimeError(f"{grouping} changed the SMEAC schema")
        # Populate one inert specimen, not a new repetition or document-rendering API.
        populated = re.sub(r"<([A-Z][A-Z0-9_]*)>", lambda match: str(PLAN_VALUES[match[1]]), schema.template)
        populated = "\n".join(line for line in populated.splitlines() if line.strip() != "...")
        if DIRECTORY_EXAMPLE.strip() not in populated:
            raise RuntimeError("populated directory view differs from the independent specimen")
        validate_plan_text(populated, recovered.schemas[0].template, require_directories=True)


def _directory_policy(policy: dict[str, object]) -> tuple[int, frozenset[str]]:
    first = policy["directory-change-first-plan"]
    reopened = policy["directory-change-reopened-plans"]
    if type(first) is not int or not 0 <= first <= 9999:
        raise RuntimeError("directory-change-first-plan must be a four-digit plan number")
    if (not isinstance(reopened, list) or any(not isinstance(name, str) for name in reopened)
            or len(set(reopened)) != len(reopened)):
        raise RuntimeError("directory-change-reopened-plans must contain unique plan directory names")
    return first, frozenset(reopened)


def validate_plans() -> None:
    """Apply the docs owner and canonical SMEAC template to persistent plans."""
    policy = {entry.id: entry.value for entry in parse(
        (ROOT / "docs" / "AGENTS.md").read_text(encoding="utf-8")
    ).constants}
    schema = parse((ROOT / policy["plan-format"]).read_text(encoding="utf-8")).schemas
    if len(schema) != 1 or schema[0].id != "smeac-plan":
        raise RuntimeError("plan format must resolve to the canonical SMEAC schema")
    template = schema[0].template
    _rejection_examples(template)
    _directory_schema_examples(schema[0])
    first, reopened = _directory_policy(policy)
    try:
        validate_plan_directory(ROOT / policy["plan-root"], template,
                                set(policy["historical-plan-formats"]),
                                directory_first=first, reopened=reopened)
    except ValueError as error:
        raise RuntimeError(f"persistent plan check failed: {error}") from None


__all__ = ["validate_plan_directory", "validate_plan_text", "validate_plans"]
