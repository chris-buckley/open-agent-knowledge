"""Reproduce numerical choices, never manufacture a new assistant trial."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from compression import session
from compression.numeric import read_kernels
from compression.task import SEEDS


def replay(destination: Path, recorded: Path) -> dict[str, object]:
    expected = json.loads((recorded / "final.json").read_bytes())
    frozen = json.loads((recorded / "freeze.json").read_bytes())
    if frozen["source-hashes"] != session.source_hashes():
        raise ValueError("replay source differs from the recorded study")
    session.start(destination)
    decisions = 0
    for seed in SEEDS:
        session.prepare(destination, seed)
        for index, path in enumerate(sorted((recorded / str(seed) / "proposals").glob("*.oak.md"))):
            if index:
                session.observe(destination, seed)
            proposal = session.read_record(path)
            session.propose(destination, seed, proposal["kind"], tuple(proposal["gains"]), proposal["rationale"], replay=True)
            actual = session.apply(destination, seed, proposal["number"])
            original = session.read_record(recorded / str(seed) / "decisions" / path.name)
            if actual["accepted"] != original["accepted"]:
                raise ValueError("replay acceptance differs")
            decisions += 1
    session.close(destination)
    actual = session.finish(destination)
    for seed, record in expected["results"].items():
        for regime, outcome in record["regimes"].items():
            for name, metrics in outcome["metrics"].items():
                observed = actual["results"][seed]["regimes"][regime]["metrics"][name]
                for field in ("accuracy", "cross-entropy", "teacher-decision-agreement"):
                    np.testing.assert_allclose(observed[field], metrics[field], rtol=1e-9, atol=1e-9)
    original_selected = json.loads((recorded / "selected.json").read_bytes())
    replay_selected = json.loads((destination / "selected.json").read_bytes())
    for seed, variants in original_selected.items():
        for name, model in variants.items():
            before = read_kernels(model["kernels"])
            after = read_kernels(replay_selected[seed][name]["kernels"])
            for old, new in zip(before, after, strict=True):
                if old.encoding != new.encoding or old.indices != new.indices:
                    raise ValueError("replay kernel structure differs")
                np.testing.assert_allclose(old.coefficients, new.coefficients, rtol=1e-9, atol=1e-9)
    report = {"new-assistant-decisions": actual["fresh-agent-decisions"], "replayed-decisions": decisions,
              "all-treatment-metrics-match": True, "all-selected-parameters-match-within-tolerance": True,
              "interpretation": "A numerical reproduction, not new agent reasoning."}
    if report["new-assistant-decisions"] != 0:
        raise ValueError("replay was mislabelled as live reasoning")
    session.write_json(destination / "replay.json", report)
    return report
