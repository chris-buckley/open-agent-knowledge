"""Audit this migration against frozen baseline hashes without importing generators."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent


def audit() -> dict[str, object]:
    baseline = json.loads((EVIDENCE / "baseline-products.json").read_text(encoding="utf-8"))
    counts: Counter[str] = Counter()
    generated = ROOT / "generated"
    expected: set[str] = set()
    for original, record in baseline["products"].items():
        change = record["change"]
        if change == "consolidated guidance":
            continue  # Guidance consolidation is reviewed separately, not hash-equivalent.
        destination = ROOT / record["destination"]
        content = destination.read_bytes()
        if change == "definition path constant":
            current = b'syntax-reference: "generated/oak.ebnf"'
            previous = b'syntax-reference: "outputs/oak.ebnf"'
            if content.count(current) != 1:
                raise RuntimeError(f"missing or repeated migrated grammar reference: {destination}")
            content = content.replace(current, previous)
        if len(content) != record["bytes"] or hashlib.sha256(content).hexdigest() != record["sha256"]:
            raise RuntimeError(f"unapproved product content change: {original}")
        counts[change] += 1
        if destination.is_relative_to(generated):
            expected.add(destination.relative_to(generated).as_posix())
        else:
            if record["destination"] != "build/authoring_validator.py":
                raise RuntimeError("unexpected maintained source destination")
            helper = generated / "oak-authoring.skill/scripts/validate.py"
            if helper.read_bytes() != content:
                raise RuntimeError("delivered validator differs from the frozen maintained source")
            expected.add(helper.relative_to(generated).as_posix())
    actual = {path.relative_to(generated).as_posix() for path in generated.rglob("*")
              if path.is_file() and "__pycache__" not in path.parts}
    if expected != actual:
        raise RuntimeError(f"product manifest differs: {sorted(expected ^ actual)}")
    if {path.name for path in generated.iterdir()} != {"definitions", "oak.ebnf", "oak-authoring.oak.md", "oak-authoring.skill"}:
        raise RuntimeError("incorrect generated root entries")
    if any((ROOT / name).exists() for name in ("outputs", "skills")):
        raise RuntimeError("obsolete product roots remain")
    if (ROOT / "build/docs.py").exists():
        raise RuntimeError("obsolete definition generator remains")
    if list(generated.rglob("AGENTS.md")) or any(path.is_symlink() for path in generated.rglob("*")):
        raise RuntimeError("generated products contain repository guidance or symlinks")
    sizes = {"agent": (generated / "oak-authoring.oak.md").stat().st_size,
             "skill_entry": (generated / "oak-authoring.skill/SKILL.md").stat().st_size}
    if sizes["agent"] > 64_000 or sizes["skill_entry"] > 10_000:
        raise RuntimeError("existing product byte limits exceeded")
    return {"verdict": "passed", "baseline": baseline["baseline"], "products": len(actual),
            "checked_changes": dict(sorted(counts.items())), "bytes": sizes,
            "guidance": "Consolidation requires scoped-rule and source review; not a byte-equivalence claim."}


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
