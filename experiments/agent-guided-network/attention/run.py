"""Run the attention extension without changing the first experiment's entry point."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from attention.session import prepare, observe, propose, apply, finish, replay
from attention.learn import METHODS


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "observe", "propose", "apply", "finish", "test", "replay"])
    parser.add_argument("work", type=Path, nargs="?", default=Path("/tmp/oak-attention-run"))
    parser.add_argument("--method", choices=METHODS)
    parser.add_argument("--rationale")
    parser.add_argument("--proposal", type=Path)
    parser.add_argument("--recorded", type=Path)
    args = parser.parse_args()
    if args.action == "test":
        import unittest
        from attention.tests import AttentionTests
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AttentionTests))
        if not result.wasSuccessful():
            raise SystemExit(1)
    elif args.action == "prepare":
        prepare(args.work)
        print("Source and study frozen. Baselines ready; test metrics unopened.")
    elif args.action == "observe":
        path, values = observe(args.work)
        print(path)
        print(json.dumps(values, indent=2))
    elif args.action == "propose":
        if not args.method or not args.rationale:
            parser.error("propose requires --method and --rationale")
        print(propose(args.work, args.method, args.rationale))
    elif args.action == "apply":
        if not args.proposal:
            parser.error("apply requires --proposal")
        print(json.dumps(apply(args.work, args.proposal), indent=2))
    elif args.action == "finish":
        print(json.dumps(finish(args.work)["summary"], indent=2))
    else:
        if not args.recorded:
            parser.error("replay requires --recorded")
        r = replay(args.work, args.recorded)
        print(json.dumps({"summary": r["summary"], "new-assistant-proposals": r["actual-assistant-proposals"]}, indent=2))


if __name__ == "__main__":
    main()
