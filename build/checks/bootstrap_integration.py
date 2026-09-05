"""Explicit network integration check for a detached skill's optional validator.

Not part of ordinary repository checks. Run only with --allow-download to approve
fetching the pinned repository and installing its dependencies in a temporary,
isolated cache. The retained installation must work again without that flag.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from build.authoring import SCRIPT, TARGET


def run() -> None:
    with tempfile.TemporaryDirectory(prefix="oak-bootstrap-integration-") as directory:
        root = Path(directory)
        script = root / "validate.py"
        document = root / "agent.oak.md"
        shutil.copyfile(SCRIPT, script)
        shutil.copyfile(TARGET, document)
        cache = root / "cache"
        command = [sys.executable, str(script), str(document), "--source", str(root / "not-installed"), "--cache-dir", str(cache)]
        def check(arguments: list[str], expected: int) -> dict:
            result = subprocess.run(arguments, capture_output=True, text=True, check=False, timeout=900)
            if result.returncode != expected:
                raise RuntimeError(f"bootstrap returned {result.returncode}, expected {expected}:\n{result.stdout}\n{result.stderr}")
            return json.loads(result.stdout)
        refusal = check(command, 2)
        if refusal["reason"] != "permission-required" or cache.exists():
            raise RuntimeError("detached skill did work without installation permission")
        installed = check([*command, "--allow-install"], 0)
        markers = list(cache.glob("*/installation.json"))
        if len(markers) != 1 or installed["status"] != "valid":
            raise RuntimeError("approved installation did not retain a validated environment")
        timestamp = markers[0].stat().st_mtime_ns
        reused = check(command, 0)
        if reused != installed or markers[0].stat().st_mtime_ns != timestamp:
            raise RuntimeError("repeat validation did not reuse the matching installation")
        print(json.dumps({"bootstrap": "passed", "revision": installed["revision"], "checks": ["refusal without download", "approved pinned download", "isolated dependency install", "standalone parse and resolution", "retained cache reuse without permission flag"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-download", action="store_true", required=True)
    parser.parse_args()
    run()
