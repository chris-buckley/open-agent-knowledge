"""Run every OAK example, freshness gate, and product-path check."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ROOT_TEXT = str(ROOT)

if ROOT_TEXT in sys.path:
    sys.path.remove(ROOT_TEXT)
sys.path.insert(0, ROOT_TEXT)

from build.checks import CHECKS


def validate_examples() -> None:
    """Raise when any example, gate, or working product path is invalid."""
    for check in CHECKS:
        check()


if __name__ == "__main__":
    validate_examples()
