#!/usr/bin/env python3
"""Verify pinned official suite checkouts and invoke the PyLD 3.1.0 test harness.

The script never downloads code.  Supply a complete PyLD v3.1.0 checkout whose
official JSON-LD test-suite submodules are initialized at the pinned commits.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

EXPECTED = {
    "pyld": "104b85d",
    "json-ld-api": "289ebf3",
    "json-ld-framing": "fa22874",
    "rdf-dataset-canonicalization": "fbcfce5",
}


def git_head(path: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pyld-source", required=True, help="PyLD v3.1.0 source checkout")
    parser.add_argument("--check-only", action="store_true", help="Verify commits without running tests")
    parser.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--json", action="store_true", help="Emit a JSON readiness report")
    args = parser.parse_args()

    root = Path(args.pyld_source).expanduser().resolve()
    paths = {
        "pyld": root,
        "json-ld-api": root / "tests" / "json-ld-api",
        "json-ld-framing": root / "tests" / "json-ld-framing",
        "rdf-dataset-canonicalization": root / "tests" / "rdf-dataset-canonicalization",
    }
    checks: dict[str, Any] = {}
    ready = True
    for name, path in paths.items():
        head = git_head(path)
        expected = EXPECTED[name]
        ok = bool(head and head.startswith(expected))
        checks[name] = {
            "path": str(path),
            "expected_commit_prefix": expected,
            "actual_commit": head,
            "ok": ok,
        }
        ready = ready and ok
    report = {
        "ready": ready,
        "mode": args.mode,
        "check_only": args.check_only,
        "checks": checks,
        "network_used": False,
    }
    if args.json or args.check_only or not ready:
        print(json.dumps(report, indent=2, sort_keys=True))
    if not ready:
        raise SystemExit(2)
    if args.check_only:
        return

    runner = root / "tests" / "runtests.py"
    if runner.is_file():
        command = [sys.executable, str(runner)]
    else:
        command = [sys.executable, "-m", "pytest", "-q", "tests"]
    if args.mode == "smoke":
        # PyLD's own harness controls official manifest selection.  The smoke
        # route keeps pytest output concise and fails fast; full removes it.
        command.extend(["-x"] if "pytest" in command else [])
    completed = subprocess.run(command, cwd=root, check=False)
    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
