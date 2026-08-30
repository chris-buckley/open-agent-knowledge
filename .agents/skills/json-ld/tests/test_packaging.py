from __future__ import annotations
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", ".pytest_cache", "__pycache__"} for part in path.parts):
            continue
        try:
            yield path, path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue


def test_skill_entrypoint_and_numbered_references_exist() -> None:
    assert (ROOT / "SKILL.md").is_file()
    references = sorted((ROOT / "references").glob("*.md"))
    assert references
    assert all(re.match(r"\d\d-[a-z0-9-]+\.md$", path.name) for path in references)


def test_no_tabs_or_smart_quotes() -> None:
    forbidden = {"\t", "\u2018", "\u2019", "\u201c", "\u201d"}
    for path, text in text_files():
        found = forbidden.intersection(text)
        assert not found, (path, found)


def test_no_virtual_environments_or_dependency_trees() -> None:
    forbidden_parts = {".venv", "venv", "node_modules"}
    offenders = [path for path in ROOT.rglob("*") if forbidden_parts.intersection(path.parts)]
    assert not offenders


def test_required_delivery_artifacts_exist() -> None:
    required = [
        "SKILL.md",
        "README.md",
        "LICENSE",
        "requirements.txt",
        "build-report.md",
        "scripts/expand.py",
        "scripts/compact.py",
        "scripts/flatten.py",
        "scripts/frame.py",
        "scripts/inspect_graph.py",
        "scripts/semantic_roundtrip.py",
        "guides/design-a-context-v1.0.0.guide.md",
        "guides/design-identifiers-v1.0.0.guide.md",
        "guides/model-relationships-v1.0.0.guide.md",
        "guides/create-an-application-profile-v1.0.0.guide.md",
        "guides/debug-json-ld-v1.0.0.guide.md",
        "processes/ingest-json-ld.md",
        "processes/emit-json-ld.md",
        "processes/update-a-context.md",
        "processes/run-conformance-tests.md",
    ]
    missing = [item for item in required if not (ROOT / item).is_file()]
    assert not missing


def test_skill_reference_links_resolve() -> None:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    links = re.findall(r"\[[^]]+\]\(([^)]+)\)", skill)
    assert links
    missing = [link for link in links if not (ROOT / link).resolve().is_file()]
    assert not missing


def test_process_documents_have_required_aps_sections() -> None:
    for path in sorted((ROOT / "processes").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for tag in ("instructions", "formats", "processes", "input"):
            assert f"<{tag}>" in text and f"</{tag}>" in text, (path, tag)
        assert "//" not in text
