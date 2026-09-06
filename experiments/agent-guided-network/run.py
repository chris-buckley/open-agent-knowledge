"""Run from the repository root; proposal creation and evaluation are separate commands."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from training.session import prepare,observe,propose,apply,finish,replay


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("action",choices=["prepare","observe","propose","apply","finish","test","replay"])
    p.add_argument("work",type=Path,nargs="?",default=Path("/mnt/data/oak-numerical-run"))
    p.add_argument("--seed",type=int,choices=[7],default=7)
    p.add_argument("--owner",choices=["left","right","readout"])
    p.add_argument("--method",choices=["concept","head","concept-head"])
    p.add_argument("--rationale")
    p.add_argument("--proposal",type=Path)
    p.add_argument("--recorded",type=Path)
    a=p.parse_args()
    if a.action=="test":
        import unittest
        suite=unittest.defaultTestLoader.discover(str(Path(__file__).parent/"evaluation"),pattern="test_*.py")
        if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():raise SystemExit(1)
    elif a.action=="prepare":
        prepare(a.work);print("Prepared immutable source/data identities, baselines, and warm snapshots. No test metrics opened.")
    elif a.action=="observe":
        path,value=observe(a.work,a.seed);print(path);print(json.dumps(value,indent=2))
    elif a.action=="propose":
        if not all([a.owner,a.method,a.rationale]):p.error("propose requires owner, method, and rationale")
        print(propose(a.work,a.seed,a.owner,a.method,a.rationale))
    elif a.action=="apply":
        if not a.proposal:p.error("apply requires --proposal")
        print(json.dumps(apply(a.work,a.seed,a.proposal),indent=2))
    elif a.action=="replay":
        if not a.recorded:p.error("replay requires --recorded")
        print(json.dumps(replay(a.work,a.recorded)["summary"],indent=2))
    else:
        print(json.dumps(finish(a.work),indent=2))


if __name__=="__main__":main()
