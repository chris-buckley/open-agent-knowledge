"""Revision-pinned live proposals, independent scoring, and sealed final testing."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import time

import numpy as np
import pydantic
from oak import Constant, Node, parse, render

from attention.author import load as load_teacher
from attention.numeric import forward as teacher_forward
from compression import study
from compression.export import export_snapshot, json_bytes, storage, verify_export
from compression.fit import fit_kernels, fold_weights, project_kernels
from compression.numeric import Encoding, Kernels, expand_kernel, forward, kernel_record, place_gains, read_kernels
from compression.oak_io import load_snapshot, oak_forward, snapshot_hash, write_snapshot
from compression.task import (DEVELOPMENT_REGIMES, REGIMES, SEEDS, Cases, case_hash, combine_cases, measure,
                              nearest_key, numerical_tuple, sample_cases)

EXPERIMENT = Path(__file__).resolve().parents[1]
REPOSITORY = EXPERIMENT.parents[1]
TEACHER = EXPERIMENT / "nodes" / "attention-learned"


def write_json(path: Path, record: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json_bytes(record))


def write_record(path: Path, record: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError("immutable record already exists")
    path.write_text(render(Node(constants=[Constant(id="record", value=record)])), encoding="utf-8")


def read_record(path: Path) -> dict:
    node = parse(path.read_text(encoding="utf-8"))
    if len(node.constants) != 1 or node.constants[0].id != "record" or render(node) != path.read_text(encoding="utf-8"):
        raise ValueError("invalid evidence record")
    record = node.constants[0].value
    if not isinstance(record, dict):
        raise ValueError("evidence must contain a named record")
    return record


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes() -> dict[str, str]:
    sources = [*Path(__file__).parent.glob("*.py"), Path(__file__).with_name("study.oak.md"),
               *(EXPERIMENT / "attention").glob("*.py"), *TEACHER.glob("*.oak.md")]
    return {path.relative_to(REPOSITORY).as_posix(): file_hash(path) for path in sorted(sources)}


def require_frozen(directory: Path, *, selection_open: bool = True) -> None:
    record = json.loads((directory / "freeze.json").read_bytes())
    if record["source-hashes"] != source_hashes():
        raise ValueError("frozen source changed")
    if selection_open and (directory / "SELECTION_CLOSED").exists():
        raise ValueError("selection is closed")


def start(directory: Path) -> dict[str, object]:
    if Path(__file__).with_name("study.oak.md").read_text(encoding="utf-8") != study.text():
        raise ValueError("study snapshot is stale")
    directory.mkdir(parents=True, exist_ok=False)
    record = {"time-utc": datetime.now(timezone.utc).isoformat(), "baseline-commit": "01093746154ef972842df1c1c0f298101921b579",
              "protocol-commit": "35317423f42720bfdc50637b3109f80409e07882", "source-hashes": source_hashes(),
              "python": platform.python_version(), "numpy": np.__version__, "pydantic": pydantic.__version__,
              "physical-assistants": 1, "external-model-calls": 0, "conversation-cost": None,
              "seeds": list(SEEDS), "teacher-training-seeds": [7]}
    write_json(directory / "freeze.json", record)
    return record


def development_cases(seed: int) -> dict[str, Cases]:
    return {regime: sample_cases(seed, "dev", regime) for regime in DEVELOPMENT_REGIMES}


def measures(kernels: Kernels, cases: dict[str, Cases]) -> dict[str, dict]:
    return {regime: measure(kernels, group) for regime, group in cases.items()}


def mean_loss(metrics: dict[str, dict]) -> float:
    return float(np.mean([row["cross-entropy"] for row in metrics.values()]))


def capability_floor(candidate: dict[str, dict], teacher: dict[str, dict]) -> bool:
    accuracy_pass = all(candidate[regime]["accuracy"] >= row["accuracy"] - study.ACCURACY_MARGIN
                        for regime, row in teacher.items())
    return accuracy_pass and mean_loss(candidate) <= mean_loss(teacher) + study.LOSS_MARGIN


def select_grid(gains: tuple[float, ...], cases: dict[str, Cases], *, paired: bool) -> tuple[Kernels, dict[str, object]]:
    pairs = ((gain, gain) for gain in gains) if paired else itertools.product(gains, repeat=2)
    candidates = [(place_gains((first, second, 8.0)), first, second) for first, second in pairs]
    scored = [(mean_loss(measures(kernels, cases)), index, kernels) for index, (kernels, _, _) in enumerate(candidates)]
    score, index, selected = min(scored, key=lambda row: (row[0], row[1]))
    return selected, {"candidate-evaluations": len(candidates), "selected-gains": [c.coefficients[0] for c in selected],
                      "selected-development-loss": score, "gradient-steps": 0}


def prepare(directory: Path, seed: int) -> dict[str, object]:
    require_frozen(directory)
    if seed not in SEEDS or (directory / str(seed)).exists():
        raise ValueError("invalid or already prepared seed")
    begin = time.perf_counter()
    root = directory / str(seed)
    root.mkdir()
    weights, _ = load_teacher(TEACHER)
    folded = fold_weights(weights)
    cases = development_cases(seed)
    training_groups = tuple(sample_cases(seed, "train", regime) for regime in DEVELOPMENT_REGIMES)
    training = combine_cases(training_groups)
    development = combine_cases(tuple(cases.values()))
    candidates = {"folded-144": folded, "pruned-36": project_kernels(folded, Encoding.SPARSE, fraction=0.25),
                  "pruned-72": project_kernels(folded, Encoding.SPARSE, fraction=0.5),
                  "projected-20": project_kernels(folded, Encoding.DIAGONAL)}
    budgets: dict[str, dict] = {}
    for encoding, name in ((Encoding.DENSE, "fitted-144"), (Encoding.DIAGONAL, "fitted-20"), (Encoding.IDENTITY, "fitted-3")):
        candidates[name], budgets[name] = fit_kernels(project_kernels(folded, encoding), numerical_tuple(training),
            numerical_tuple(development), steps=study.FIT_STEPS, rate=study.FIT_RATE)
    candidates["grid-4"], budgets["grid-4"] = select_grid(study.MATCHED_GRID, cases, paired=True)
    candidates["grid-36"], budgets["grid-36"] = select_grid(study.GAIN_GRID, cases, paired=False)
    controls = {}
    for name, kernels in candidates.items():
        revision = write_snapshot(kernels, root / "snapshots" / name)
        controls[name] = {"snapshot": name, "revision": revision, "development": measures(kernels, cases),
                          "storage": storage(kernels), "budget": budgets.get(name, {"gradient-steps": 0, "candidate-evaluations": 1})}
    write_json(root / "controls.json", controls)
    write_json(root / "data-hashes.json", {"train": {r: case_hash(g) for r, g in zip(DEVELOPMENT_REGIMES, training_groups, strict=True)},
                                          "dev": {r: case_hash(g) for r, g in cases.items()}})
    (root / "CURRENT").write_text("folded-144", encoding="utf-8")
    write_json(root / "preparation.json", {"tool-seconds": time.perf_counter() - begin,
        "controls-hidden-from-live-observation": True, "teacher-parameters": 416, "teacher-f64-bytes": 3328})
    return observe(directory, seed)


def observe(directory: Path, seed: int) -> dict[str, object]:
    require_frozen(directory)
    root = directory / str(seed)
    current = (root / "CURRENT").read_text(encoding="utf-8")
    snapshot = root / "snapshots" / current
    kernels = load_snapshot(snapshot)
    cases = development_cases(seed)
    observations = root / "observations"
    observations.mkdir(exist_ok=True)
    number = len(list(observations.glob("*.oak.md"))) + 1
    record = {"kind": "observation", "seed": seed, "snapshot": current, "revision": snapshot_hash(snapshot),
              "development": measures(kernels, cases), "storage": storage(kernels),
              "diagonal-means": [float(np.trace(expand_kernel(k)) / k.dimension) for k in kernels],
              "coefficient-ranges": [[min(k.coefficients), max(k.coefficients)] for k in kernels]}
    filename = f"{number:03d}.oak.md"
    write_record(observations / filename, record)
    record["observation"] = filename
    return record


def propose(directory: Path, seed: int, kind: str, gains: tuple[float, ...], rationale: str,
            *, replay: bool = False) -> dict[str, object]:
    require_frozen(directory)
    root = directory / str(seed)
    if kind not in ("diagonal", "identity") or not rationale.strip():
        raise ValueError("invalid proposal kind or rationale")
    if kind == "identity":
        place_gains(gains)
    elif gains:
        raise ValueError("diagonal projection takes no supplied gains")
    proposals = root / "proposals"
    proposals.mkdir(exist_ok=True)
    number = len(list(proposals.glob("*.oak.md"))) + 1
    if number > study.PROPOSAL_CAP:
        raise ValueError("proposal budget exhausted")
    observation_path = sorted((root / "observations").glob("*.oak.md"))[-1]
    observation = read_record(observation_path)
    current = (root / "CURRENT").read_text(encoding="utf-8")
    if observation["revision"] != snapshot_hash(root / "snapshots" / current):
        raise ValueError("stale observation")
    record = {"kind": kind, "gains": list(gains), "seed": seed, "number": number, "rationale": rationale,
              "baseline": observation["revision"], "snapshot": current,
              "observation": observation_path.name, "observation-hash": file_hash(observation_path),
              "proposer": "numerical-replay" if replay else "live-assistant", "gradient-steps": 0}
    write_record(proposals / f"{number:03d}.oak.md", record)
    return record


def apply(directory: Path, seed: int, number: int) -> dict[str, object]:
    require_frozen(directory)
    begin = time.perf_counter()
    root = directory / str(seed)
    proposal_path = root / "proposals" / f"{number:03d}.oak.md"
    proposal = read_record(proposal_path)
    if proposal["seed"] != seed or proposal["number"] != number:
        raise ValueError("proposal identity mismatch")
    decision_path = root / "decisions" / f"{number:03d}.oak.md"
    if decision_path.exists():
        raise ValueError("proposal already evaluated")
    observation_path = root / "observations" / proposal["observation"]
    if file_hash(observation_path) != proposal["observation-hash"]:
        raise ValueError("observation changed")
    current = (root / "CURRENT").read_text(encoding="utf-8")
    before_path = root / "snapshots" / current
    if current != proposal["snapshot"] or snapshot_hash(before_path) != proposal["baseline"]:
        raise ValueError("stale proposal")
    before = load_snapshot(before_path)
    if proposal["kind"] == "identity":
        candidate = place_gains(tuple(proposal["gains"]))
    elif proposal["kind"] == "diagonal" and not proposal["gains"]:
        candidate = project_kernels(before, Encoding.DIAGONAL)
    else:
        raise ValueError("unsupported proposal")
    cases = development_cases(seed)
    teacher = load_snapshot(root / "snapshots" / "folded-144")
    teacher_metrics, previous, candidate_metrics = (measures(model, cases) for model in (teacher, before, candidate))
    size, previous_size, teacher_size = (storage(model) for model in (candidate, before, teacher))
    smaller = size["stored-coefficients"] < teacher_size["stored-coefficients"] and size["model-bytes"] < teacher_size["model-bytes"]
    fewer = size["stored-coefficients"] < previous_size["stored-coefficients"]
    same_better = size["stored-coefficients"] == previous_size["stored-coefficients"] and mean_loss(candidate_metrics) < mean_loss(previous) - 1e-6
    accepted = smaller and capability_floor(candidate_metrics, teacher_metrics) and (fewer or same_better)
    name = f"candidate-{number:03d}"
    revision = write_snapshot(candidate, root / "snapshots" / name)
    record = {"seed": seed, "number": number, "proposal-hash": file_hash(proposal_path), "baseline": proposal["baseline"],
        "candidate": name, "candidate-revision": revision, "accepted": accepted, "development": candidate_metrics,
        "storage": size, "capability-floor": capability_floor(candidate_metrics, teacher_metrics),
        "smaller-model": smaller, "tool-seconds": time.perf_counter() - begin, "gradient-steps": 0}
    require_frozen(directory)
    if (root / "CURRENT").read_text() != current or snapshot_hash(before_path) != proposal["baseline"]:
        raise ValueError("incumbent changed before acceptance")
    write_record(decision_path, record)
    if accepted:
        (root / "CURRENT").write_text(name, encoding="utf-8")
    return record


def close(directory: Path) -> dict[str, object]:
    require_frozen(directory)
    selected = {}
    for seed in SEEDS:
        root = directory / str(seed)
        controls = json.loads((root / "controls.json").read_bytes())
        current = (root / "CURRENT").read_text(encoding="utf-8")
        proposals = list((root / "proposals").glob("*.oak.md"))
        decisions = list((root / "decisions").glob("*.oak.md"))
        if not proposals or len(proposals) != len(decisions):
            raise ValueError("finish every proposal before closing selection")
        names = {name: row["snapshot"] for name, row in controls.items()} | {"agent": current}
        selected[str(seed)] = {name: {"snapshot": snapshot, "revision": snapshot_hash(root / "snapshots" / snapshot),
            "kernels": [kernel_record(k) for k in load_snapshot(root / "snapshots" / snapshot)]} for name, snapshot in names.items()}
    write_json(directory / "selected.json", selected)
    (directory / "SELECTION_CLOSED").write_text(file_hash(directory / "selected.json"), encoding="utf-8")
    return {"selected-hash": file_hash(directory / "selected.json"), "seeds": list(SEEDS)}


def paired_interval(difference: np.ndarray, seed: int) -> list[float]:
    if np.all(difference == difference[0]):
        return [float(difference[0]), float(difference[0])]
    rng = np.random.default_rng(seed)
    means = rng.choice(difference, size=(2000, len(difference))).mean(axis=1)
    return [float(value) for value in np.quantile(means, [0.025, 0.975])]


def finish(directory: Path) -> dict[str, object]:
    require_frozen(directory, selection_open=False)
    selected_file = directory / "selected.json"
    if (directory / "SELECTION_CLOSED").read_text() != file_hash(selected_file):
        raise ValueError("selected models changed after closure")
    if (directory / "final.json").exists():
        raise ValueError("final result already recorded")
    selected = json.loads(selected_file.read_bytes())
    weights, _ = load_teacher(TEACHER)
    results: dict[str, dict] = {}
    for seed in SEEDS:
        root = directory / str(seed)
        variants = {name: read_kernels(row["kernels"]) for name, row in selected[str(seed)].items()}
        agent_snapshot = root / "snapshots" / selected[str(seed)]["agent"]["snapshot"]
        export_sizes = {name: export_snapshot(root / "snapshots" / selected[str(seed)][name]["snapshot"],
            root / "export" if name == "agent" else root / "exports" / name) for name in variants}
        sizes = export_sizes["agent"]
        regimes = {}
        for regime_index, regime in enumerate(REGIMES):
            cases = sample_cases(seed, "test", regime)
            reference = teacher_forward(weights, cases.inputs)
            probabilities = {name: forward(model, cases.inputs) for name, model in variants.items()}
            metrics = {name: measure(model, cases) for name, model in variants.items()}
            for name, probability in probabilities.items():
                metrics[name]["teacher-decision-agreement"] = float(np.mean(probability.argmax(axis=1) == reference.argmax(axis=1)))
            folded = probabilities["folded-144"]
            np.testing.assert_allclose(folded, reference, atol=1e-10, rtol=1e-10)
            np.testing.assert_array_equal(folded.argmax(axis=1), reference.argmax(axis=1))
            agent_correct = probabilities["agent"].argmax(axis=1) == cases.labels
            grid_correct = probabilities["grid-36"].argmax(axis=1) == cases.labels
            teacher_correct = reference.argmax(axis=1) == cases.labels
            sample = {name: tensor[:2] for name, tensor in cases.inputs.items()}
            oak_output = oak_forward(agent_snapshot, sample)
            np.testing.assert_allclose(oak_output, probabilities["agent"][:2], atol=1e-10, rtol=1e-10)
            regimes[regime] = {"data-hash": case_hash(cases), "metrics": metrics,
                "teacher-416-accuracy": float(teacher_correct.mean()), "nearest-key-accuracy": float(np.mean(nearest_key(cases) == cases.labels)),
                "fold-max-error": float(np.abs(folded - reference).max()),
                "agent-minus-grid95": paired_interval(agent_correct.astype(float) - grid_correct, seed + 100 * regime_index),
                "agent-minus-teacher95": paired_interval(agent_correct.astype(float) - teacher_correct, seed + 200 * regime_index),
                "export": verify_export(root / "export", variants["agent"], cases.inputs),
                "oak-executor-max-error": float(np.abs(oak_output - probabilities["agent"][:2]).max())}
        results[str(seed)] = {"regimes": regimes, "agent-storage": sizes,
            "model-storage": export_sizes,
            "proposal-count": len(list((root / "proposals").glob("*.oak.md")))}
    write_json(directory / "final.json", {"results": results, "selection-hash": file_hash(selected_file),
        "fresh-agent-decisions": sum(read_record(p)["proposer"] == "live-assistant" for p in directory.glob("*/proposals/*.oak.md")),
        "interpretation": "Conditional fixed-model comparisons on three fresh data seeds; one teacher and one shared-context assistant."})
    return json.loads((directory / "final.json").read_bytes())
