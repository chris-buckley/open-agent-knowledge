"""Command boundary for live compression decisions and numerical replay."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compression import session, study


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("test", "study", "start", "prepare", "observe", "propose", "apply", "close", "finish", "replay"))
    parser.add_argument("directory", nargs="?", type=Path)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--kind", choices=("diagonal", "identity"))
    parser.add_argument("--gains", type=float, nargs=3, default=())
    parser.add_argument("--rationale", default="")
    parser.add_argument("--number", type=int)
    parser.add_argument("--recorded", type=Path)
    arguments = parser.parse_args()
    if arguments.command == "test":
        from compression import tests
        outcome = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
        raise SystemExit(0 if outcome.wasSuccessful() else 1)
    if arguments.command == "study":
        Path(study.__file__).with_suffix(".oak.md").write_text(study.text(), encoding="utf-8")
        return
    if arguments.directory is None:
        parser.error("directory is required")
    if arguments.command in ("prepare", "observe", "propose", "apply") and arguments.seed is None:
        parser.error("seed is required")
    if arguments.command == "apply" and arguments.number is None:
        parser.error("proposal number is required")
    match arguments.command:
        case "start":
            outcome = session.start(arguments.directory)
        case "prepare":
            outcome = session.prepare(arguments.directory, arguments.seed)
        case "observe":
            outcome = session.observe(arguments.directory, arguments.seed)
        case "propose":
            outcome = session.propose(arguments.directory, arguments.seed, arguments.kind, tuple(arguments.gains), arguments.rationale)
        case "apply":
            outcome = session.apply(arguments.directory, arguments.seed, arguments.number)
        case "close":
            outcome = session.close(arguments.directory)
        case "finish":
            final = session.finish(arguments.directory)
            outcome = {seed: {regime: row["metrics"]["agent"] for regime, row in record["regimes"].items()}
                       for seed, record in final["results"].items()}
        case "replay":
            if arguments.recorded is None:
                parser.error("recorded directory is required")
            from compression.replay import replay
            outcome = replay(arguments.directory, arguments.recorded)
        case _:
            raise ValueError("unknown command")
    print(json.dumps(outcome, indent=2))


if __name__ == "__main__":
    main()
