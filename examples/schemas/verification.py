"""One reusable verification record tied to an immutable subject revision."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oak import Node, NonEmpty, Regex, Schema, Type, parse, render, resolve, where

VERIFICATION_FIELDS = (
    "VERIFIED_SUBJECT", "VERIFIED_REVISION", "CHECK", "PASSED", "EVIDENCE",
)

verification_schema = Schema(
    id="verification",
    name="Verification",
    purpose="Identify the exact subject revision, performed check, observed result, and recorded evidence.",
    template=(
        "Subject: <VERIFIED_SUBJECT>\nRevision: <VERIFIED_REVISION>\n"
        "Check: <CHECK>\nPassed: <PASSED>\nEvidence: <EVIDENCE>"
    ),
    where=[
        where("VERIFIED_SUBJECT", Type(of="string"), NonEmpty(),
              description="the subject actually inspected by the verifier"),
        where("VERIFIED_REVISION", Type(of="string"), Regex(pattern="^[0-9a-f]{64}$"),
              description="the SHA-256 digest of the immutable snapshot actually checked"),
        where("CHECK", Type(of="string"), NonEmpty(),
              description="the versioned check definition actually performed"),
        where("PASSED", Type(of="boolean"),
              description="the observed check result, not a confidence estimate"),
        where("EVIDENCE", Type(of="string"), NonEmpty(),
              description="the host-recorded evidence location, whose existence the host must establish"),
    ],
)

verification_node = Node(schemas=[verification_schema])
TARGET = Path(__file__).with_suffix(".oak.md")


def build() -> str:
    """Render and validate the shared verification shape without claiming truth."""
    text = render(verification_node)
    parsed = parse(text)
    resolve(parsed)
    if render(parsed) != text:
        raise RuntimeError("verification schema did not round-trip")
    verification_schema.bind({
        "VERIFIED_SUBJECT": "candidate-1",
        "VERIFIED_REVISION": "a" * 64,
        "CHECK": "implementation-checks-v1",
        "PASSED": True,
        "EVIDENCE": "evidence/candidate-1.json",
    })
    return text


def write() -> Path:
    """Write the canonical sibling snapshot."""
    TARGET.write_text(build(), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(f"wrote {write()}")
