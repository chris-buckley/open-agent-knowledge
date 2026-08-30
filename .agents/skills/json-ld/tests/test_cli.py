from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PYTHON, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_every_required_cli_has_help() -> None:
    for name in (
        "expand.py",
        "compact.py",
        "flatten.py",
        "frame.py",
        "inspect_graph.py",
        "semantic_roundtrip.py",
    ):
        result = run(f"scripts/{name}", "--help")
        assert result.returncode == 0, (name, result.stderr)
        assert "usage:" in result.stdout.lower()


def test_expand_cli_emits_machine_envelope() -> None:
    result = run(
        "scripts/expand.py",
        "examples/compact/base-system.jsonld",
        "--engine",
        "profile",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["operation"] == "expand"
    assert payload["engine"] == "profile"
    assert payload["source"]["source_sha256"]


def test_graph_inspector_finds_missing_target() -> None:
    result = run(
        "scripts/inspect_graph.py",
        "examples/invalid/missing-target.jsonld",
        "--engine",
        "profile",
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert {issue["code"] for issue in payload["issues"]} == {"missing_reference_target"}


def test_graph_inspector_accepts_complete_bundle() -> None:
    result = run(
        "scripts/inspect_graph.py",
        "examples/compact/system-bundle.jsonld",
        "--engine",
        "profile",
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["ok"] is True


def test_semantic_roundtrip_reports_graph_not_text_equivalence() -> None:
    result = run(
        "scripts/semantic_roundtrip.py",
        "examples/compact/system-bundle.jsonld",
        "--context",
        "examples/contexts/system-context.jsonld",
        "--engine",
        "profile",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)["result"]
    assert payload["equivalent"] is True
    assert payload["textually_equal"] is False


def test_default_engine_does_not_silently_fall_back() -> None:
    result = run("scripts/expand.py", "examples/compact/base-system.jsonld")
    if result.returncode == 0:
        assert json.loads(result.stdout)["engine"] == "pyld"
    else:
        payload = json.loads(result.stderr)
        assert payload["error"]["code"] == "processor_unavailable"


def test_pydantic_conversion_clis() -> None:
    to_model = run(
        "examples/pydantic/jsonld_to_pydantic.py",
        "examples/compact/system-bundle.jsonld",
        "--engine",
        "profile",
        "--external-id",
        "sys:base",
    )
    assert to_model.returncode == 0, to_model.stderr
    assert json.loads(to_model.stdout)["application"]["id"] == "sys:domain"
    to_jsonld = run(
        "examples/pydantic/pydantic_to_jsonld.py",
        "examples/pydantic/application-system.json",
        "--engine",
        "profile",
    )
    assert to_jsonld.returncode == 0, to_jsonld.stderr
    assert json.loads(to_jsonld.stdout)["jsonld"]["@id"] == "sys:domain"


def test_official_suite_runner_has_help() -> None:
    result = run("scripts/run_official_subset.py", "--help")
    assert result.returncode == 0
    assert "check-only" in result.stdout


def test_cross_document_graph_resolution() -> None:
    result = run(
        "scripts/inspect_graph.py",
        "examples/compact/base-system.jsonld",
        "examples/compact/cross-document-reference.jsonld",
        "--engine",
        "profile",
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["ok"] is True
