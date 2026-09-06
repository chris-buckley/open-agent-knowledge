"""Recheck the recorded pre-migration example fingerprints against a checkout.

Run with the OAK dependencies installed:
    python docs/plans/0012-flat-python-authoring/evidence/compare.py

This is historical migration evidence, not a new current-source authority.
Only typed structural fields are translated back for comparison. Literal data,
schemas, state values, instruction text, and all other properties are untouched.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from oak import node_json_ld, parse, render


def digest(value: object) -> str:
    encoded = value if isinstance(value, str) else json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def old_model(value: dict) -> dict:
    result = deepcopy(value)

    def body(statements: list[dict]) -> None:
        for statement in statements:
            if statement["kind"] in {"foreach", "while", "par"}:
                statement["steps"] = statement.pop("body")
                body(statement["steps"])
            elif statement["kind"] == "if":
                body(statement["then"])
                if statement["otherwise"] is not None:
                    body(statement["otherwise"])

    for process in result["processes"]:
        process["steps"] = process.pop("body")
        body(process["steps"])
    return result


def old_json_ld(value: dict) -> dict:
    result = deepcopy(value)
    context = result["@context"]
    context["steps"] = {"@id": "oak:steps", "@container": "@list"}
    del context["then"]
    context["thenSteps"] = {"@id": "oak:thenSteps", "@container": "@list"}

    def body(statements: list[dict]) -> None:
        for statement in statements:
            if statement["@type"] in {"oak:Foreach", "oak:While", "oak:Par"}:
                statement["steps"] = statement.pop("body")["@list"]
                body(statement["steps"])
            elif statement["@type"] == "oak:If":
                statement["thenSteps"] = statement.pop("then")
                body(statement["thenSteps"])
                if "otherwise" in statement:
                    body(statement["otherwise"])

    for process in result.get("processes", []):
        process["steps"] = process.pop("body")["@list"]
        body(process["steps"])
    return result


def run() -> None:
    evidence = Path(__file__).with_name("preservation.json")
    expected = json.loads(evidence.read_text(encoding="utf-8"))
    for path, record in expected["documents"].items():
        node = parse((ROOT / path).read_text(encoding="utf-8"))
        observed = {
            "xml": digest(render(node)),
            "markdown": digest(render(node, grouping="markdown")),
            "model": digest(old_model(node.model_dump(mode="json", by_alias=True))),
            "json_ld": digest(old_json_ld(node_json_ld(
                node, document="https://example.org/" + path, vocabulary="https://example.org/oak#",
            ))),
        }
        if observed != record:
            raise RuntimeError(f"migration changed {path}: {observed}")
    print(f"PASS: {len(expected['documents'])} documents, two exact text groupings and two structural comparisons.")


if __name__ == "__main__":
    run()
