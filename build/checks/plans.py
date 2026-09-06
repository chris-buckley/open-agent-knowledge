"""Persistent plan storage and SMEAC structure verification."""

from __future__ import annotations

from pathlib import Path
import re
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit

from build.checks.fixtures import ROOT
from examples.schemas.smeac_plan import ComparisonAuthority
from oak.parse import parse

_DIRECTORY = re.compile(r"([0-9]{4})-[a-z][a-z0-9]*(?:-[a-z0-9]+)*")
_PHASE = re.compile(r"### Phase ([1-9][0-9]*): \S.*")
_TASK = re.compile(r"- \[[ xX]\] Key task: ([A-Z][A-Z0-9._-]*[0-9]) \S.*")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_LINK = re.compile(r"\[[^\]\n]*\]\(([^\s)]+)\)")
_COMPARISON = re.compile(r"#### (E[0-9]{2,}): \S.*")
_COMPARISON_ID = re.compile(r"\bE[0-9]{2,}\b")


def _prose_lines(text: str) -> list[str]:
    """Mask fenced examples while preserving their original line positions."""
    lines = []
    fence: str | None = None
    for line in text.splitlines():
        lines.append("")
        marker = _FENCE.fullmatch(line)
        if fence is not None:
            if (marker and marker[1][0] == fence[0]
                    and len(marker[1]) >= len(fence) and not marker[2].strip()):
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


def _comparison_content(raw: list[str], field: str) -> str:
    content = [raw[0][len(field):], *raw[1:]]
    if not any(line.strip() and not _FENCE.fullmatch(line) for line in content):
        raise ValueError(f"comparison needs populated {field}")
    return "\n".join(content).strip()


def _comparison_authority(prose: list[str], raw: list[str], fields: tuple[str, ...]) -> ComparisonAuthority:
    positions = [(index, field) for index, line in enumerate(prose) for field in fields
                 if line == field or line.startswith(field + " ")]
    if tuple(field for _, field in positions) != fields:
        raise ValueError("comparison needs each schema field once, in order")
    contents: list[str] = []
    for position, (start, field) in enumerate(positions):
        end = positions[position + 1][0] if position + 1 < len(positions) else len(raw)
        contents.append(_comparison_content(raw[start:end], field))
    try:
        return ComparisonAuthority(contents[0])
    except ValueError as error:
        raise ValueError("comparison authority must be required or illustrative") from error


def _comparison_bounds(prose: list[str], heading: str, sections: list[str]) -> tuple[int, int] | None:
    starts = [index for index, line in enumerate(prose) if line == heading]
    if not starts:
        return None
    mission_start, mission_end = prose.index(sections[1]), prose.index(sections[2])
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


def validate_plan_text(text: str, template: str) -> None:
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


def validate_plan_directory(root: Path, template: str, historical: set[str]) -> None:
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
        entries = {path.name for path in directory.iterdir()}
        if "plan.md" not in entries:
            raise ValueError(f"{directory.name} needs plan.md")
        if entries - {"plan.md", "report.md", "evidence"}:
            raise ValueError(f"unexpected plan files in {directory.name}")
        for filename in entries & {"plan.md", "report.md"}:
            path = directory / filename
            if not path.is_file() or not path.read_text(encoding="utf-8").strip():
                raise ValueError(f"{directory.name}/{filename} must be a non-empty file")
            _validate_navigation(path, root.parent.parent)
        if "evidence" in entries:
            evidence = directory / "evidence"
            if not evidence.is_dir() or not any(path.is_file() for path in evidence.rglob("*")):
                raise ValueError(f"{directory.name}/evidence must contain supporting files")
        if directory.name not in historical:
            try:
                validate_plan_text((directory / "plan.md").read_text(encoding="utf-8"), template)
            except ValueError as error:
                raise ValueError(f"{directory.name}/plan.md: {error}") from None
    if historical - discovered:
        raise ValueError("historical format exceptions refer to missing plan directories")


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
    try:
        validate_plan_directory(ROOT / policy["plan-root"], template,
                                set(policy["historical-plan-formats"]))
    except ValueError as error:
        raise RuntimeError(f"persistent plan check failed: {error}") from None


__all__ = ["validate_plan_directory", "validate_plan_text", "validate_plans"]
