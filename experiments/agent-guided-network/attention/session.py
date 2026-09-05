"""Real proposals and numerical replay are separate, revision-pinned activities."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import time
import numpy as np
from training.session import record, read_record, save_json, code_hashes
from attention.author import write, load, revision, oak_forward
from attention.numeric import parameters, forward
from attention.learn import adam, candidate, METHODS, STEPS
from attention.task import dataset, initial, metrics, identity, accept, SEEDS, SPLITS
from attention.export import export, check
from attention.study import text

HERE = Path(__file__).resolve().parent


def verify(work: Path) -> None:
    f = json.loads((work/"freeze.json").read_text())
    if f["code"] != code_hashes() or f["study"] != hashlib.sha256((HERE/"study.oak.md").read_bytes()).hexdigest():
        raise ValueError("source or study changed after freeze")


def current(work: Path, seed: int) -> tuple[Path, dict]:
    base = work/str(seed)
    path = base/"snapshots"/(base/"CURRENT").read_text().strip()
    return path, load(path)[0]


def open_selection(work: Path) -> None:
    verify(work)
    if (work/"SELECTION_CLOSED").exists():
        raise ValueError("selection is closed")


def scaled_control(w: dict, dev: tuple) -> tuple[dict, list]:
    """A fixed non-agent control, not a simulated reasoning session."""
    best = parameters(w)
    best_loss = metrics(w, dev)["cross-entropy"]
    trials = []
    for score in (.5, 1., 2.):
        for output in (.5, 1., 2.):
            c = parameters(w)
            for stage in ("first", "second"):
                for key in ("query", "key"):
                    c[stage+"-"+key] *= np.sqrt(score)
            c["second-output"] *= output
            result = metrics(c, dev)
            trials.append({"score-factor": score, "output-factor": output, "dev": result})
            if accept(metrics(w, dev), result) and result["cross-entropy"] < best_loss:
                best, best_loss = c, result["cross-entropy"]
    return best, trials


def prepare(work: Path) -> None:
    if (HERE/"study.oak.md").read_text() != text():
        raise ValueError("stale generated study")
    work.mkdir(parents=True, exist_ok=False)
    save_json(work/"freeze.json", {"code": code_hashes(), "study": hashlib.sha256((HERE/"study.oak.md").read_bytes()).hexdigest(),
                                  "baseline": "06eae1cd9aaf697b705a16f6d96baad01f8988fa", "python": sys.version, "numpy": np.__version__,
                                  "proposers": 1, "logical-attention-roles": 2, "trainable-scalars": 416,
                                  "model": "GPT-6 Pro, session-reported", "conversation-cost": None, "conversation-tokens": None})
    t = time.perf_counter()
    for seed in SEEDS:
        base = work/str(seed)
        for name in ("snapshots", "observations", "proposals", "decisions"):
            (base/name).mkdir(parents=True)
        train, dev = dataset(seed, "train"), dataset(seed, "dev")
        w = initial(seed)
        warm = adam(w, train, steps=80)
        numerical = adam(warm, train, steps=600, dev=dev)
        grid, trials = scaled_control(numerical, dev)
        networks = {"initial": w, "warm": warm, "numerical": numerical, "scale-control": grid}
        for name, network in networks.items():
            write(network, base/"snapshots"/name)
        (base/"CURRENT").write_text("warm\n")
        save_json(base/"baseline.json", {"dev": {k: metrics(v, dev) for k, v in networks.items()}, "scale-trials": trials,
                                       "warm-gradient-steps": 80, "numerical-gradient-steps": 600,
                                       "numerical-checkpoints": 25, "scale-candidates": 9})
        save_json(base/"split-identities.json", {name: identity(dataset(seed, name)) for name in SPLITS})
    save_json(work/"preparation.json", {"seconds": time.perf_counter()-t, "test-metrics-observed": False})


def observe(work: Path, seed: int = 7) -> tuple[Path, dict]:
    open_selection(work)
    directory, w = current(work, seed)
    base = work/str(seed)
    result = {"revision": revision(directory), "train": metrics(w, dataset(seed, "train")),
              "dev": metrics(w, dataset(seed, "dev")),
              "matrix-norms": {name: float(np.linalg.norm(value)) for name, value in w.items()}}
    path = base/"observations"/f"{len(list((base/'observations').glob('*.oak.md')))+1:03}.oak.md"
    record(path, result)
    return path, result


def propose(work: Path, method: str, rationale: str, *, actor: str = "assistant") -> Path:
    open_selection(work)
    base = work/"7"
    source, _ = current(work, 7)
    observations = sorted((base/"observations").glob("*.oak.md"))
    count = len(list((base/"proposals").glob("*.oak.md")))
    if method not in METHODS or not rationale.strip() or actor not in ("assistant", "replay"):
        raise ValueError("invalid proposal")
    if count >= 4:
        raise ValueError("four-proposal budget exhausted")
    if not observations or read_record(observations[-1])["revision"] != revision(source):
        raise ValueError("fresh observation required")
    path = base/"proposals"/f"{count+1:03}.oak.md"
    record(path, {"baseline": revision(source), "observation": hashlib.sha256(observations[-1].read_bytes()).hexdigest(),
                  "owner": "attention-network", "method": method, "rationale": rationale, "actor": actor}, proposal=True)
    return path


def apply(work: Path, proposal: Path) -> dict:
    open_selection(work)
    base = work/"7"
    directory, w = current(work, 7)
    r = read_record(proposal)
    if set(r) != {"baseline", "observation", "owner", "method", "rationale", "actor"}:
        raise ValueError("invalid proposal fields")
    if r["baseline"] != revision(directory):
        raise ValueError("stale proposal")
    if proposal.parent.resolve() != (base/"proposals").resolve() or (base/"decisions"/proposal.name).exists():
        raise ValueError("proposal unowned or already evaluated")
    if r["method"] not in METHODS or r["actor"] not in ("assistant", "replay") or r["owner"] != "attention-network":
        raise ValueError("invalid proposal values")
    evidence = {hashlib.sha256(p.read_bytes()).hexdigest(): read_record(p)["revision"] for p in (base/"observations").glob("*.oak.md")}
    if evidence.get(r["observation"]) != r["baseline"]:
        raise ValueError("observation does not match proposal")
    t = time.perf_counter()
    c = candidate(w, dataset(7, "train"), r["method"])
    destination = base/"snapshots"/("candidate-"+proposal.name.split(".")[0])
    write(c, destination)
    c, _ = load(destination)
    dev = dataset(7, "dev")
    before, after = metrics(w, dev), metrics(c, dev)
    ok = accept(before, after)
    if revision(current(work, 7)[0]) != r["baseline"]:
        raise ValueError("baseline drift before acceptance")
    if ok:
        temporary = base/"CURRENT.next"
        temporary.write_text(destination.name+"\n")
        os.replace(temporary, base/"CURRENT")
    result = {"proposal": hashlib.sha256(proposal.read_bytes()).hexdigest(), "baseline": r["baseline"],
              "candidate": revision(destination), "accepted": ok, "before": before, "after": after,
              "gradient-steps": 0 if r["method"] in ("cool-output", "sharpen-both-direct") else STEPS,
              "seconds": time.perf_counter()-t, "actor": r["actor"]}
    record(base/"decisions"/proposal.name, result)
    return result


def finish(work: Path) -> dict:
    open_selection(work)
    proposals = sorted((work/"7/proposals").glob("*.oak.md"))
    if not proposals or any(not (work/"7/decisions"/p.name).exists() for p in proposals):
        raise ValueError("all proposals must be evaluated")
    sequence = [read_record(p) for p in proposals]
    (work/"SELECTION_CLOSED").write_text("No new decisions; remaining seeds replay recorded methods.\n")
    selected = {}
    for seed in SEEDS:
        base = work/str(seed)
        path = current(work, seed)[0]
        if seed != 7:
            w = load(base/"snapshots/warm")[0]
            decisions = []
            for r in sequence:
                c = candidate(w, dataset(seed, "train"), r["method"])
                before, after = metrics(w, dataset(seed, "dev")), metrics(c, dataset(seed, "dev"))
                ok = accept(before, after)
                decisions.append({"method": r["method"], "accepted": ok, "before": before, "after": after, "actor": "replay"})
                if ok:
                    w = c
            path = base/"snapshots/agent-replay"
            write(w, path)
            save_json(base/"replay.json", decisions)
        selected[str(seed)] = {name: {"path": str((base/"snapshots"/name).relative_to(work)),
                                     "revision": revision(base/"snapshots"/name)}
                               for name in ("initial", "warm", "numerical", "scale-control")}
        selected[str(seed)]["agent"] = {"path": str(path.relative_to(work)), "revision": revision(path)}
    save_json(work/"selected.json", selected)
    results, exports, interventions = {}, {}, {}
    for seed in SEEDS:
        key = str(seed)
        results[key], exports[key], interventions[key] = {}, {}, {}
        source = work/selected[key]["agent"]["path"]
        w = load(source)[0]
        artifact = work/key/"export"
        export(source, artifact)
        for split in ("test", "long", "crowded"):
            data = dataset(seed, split)
            results[key][split] = {name: metrics(load(work/entry["path"])[0], data) for name, entry in selected[key].items()}
            interventions[key][split] = {name: metrics(w, data, ablate=name) for name in ("first", "second", "both")}
            exports[key][split] = check(artifact, w, data[0])
            small = {k: v[:2] for k, v in data[0].items()}
            error = float(np.max(np.abs(oak_forward(source, small)-forward(w, small))))
            if error > 1e-12:
                raise ValueError("OAK executor parity failure")
            exports[key][split]["oak-executor-error"] = error
    summary = {split: {name: {metric: {"mean": float(np.mean(a := [results[str(s)][split][name][metric] for s in SEEDS])),
                                      "min": float(min(a)), "max": float(max(a))}
                              for metric in ("accuracy", "cross-entropy")}
                       for name in selected["7"]} for split in ("test", "long", "crowded")}
    result = {"results": results, "summary": summary, "interventions": interventions, "exports": exports,
              "actual-assistant-proposals": sum(r["actor"] == "assistant" for r in sequence),
              "new-assistant-seeds": [7] if any(r["actor"] == "assistant" for r in sequence) else [],
              "replay-seeds": [19, 31], "independent-agents": False, "superiority-established": False}
    save_json(work/"final.json", result)
    return result


def replay(work: Path, recorded: Path) -> dict:
    prepare(work)
    for path in sorted((recorded/"7/proposals").glob("*.oak.md")):
        r = read_record(path)
        observe(work)
        proposal = propose(work, r["method"], r["rationale"], actor="replay")
        apply(work, proposal)
    result = finish(work)
    expected = json.loads((recorded/"final.json").read_text())
    for seed in result["results"]:
        for split in result["results"][seed]:
            for name in result["results"][seed][split]:
                for metric in ("accuracy", "cross-entropy"):
                    np.testing.assert_allclose(result["results"][seed][split][name][metric], expected["results"][seed][split][name][metric], rtol=1e-9, atol=1e-11)
    return result
