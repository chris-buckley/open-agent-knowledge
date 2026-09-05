"""Frozen synthetic relation task and metrics. No agent code or candidate selection."""
from __future__ import annotations
import hashlib
import numpy as np
from runtime.numeric import forward, parameters

SEEDS = (7, 19, 31)
SIZES = {"train": 128, "dev": 64, "test": 256}
OFFSETS = {"train": 10000, "dev": 20000, "test": 30000, "pilot": 40000}


def dataset(seed: int, split: str) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed + OFFSETS[split])
    x = (rng.random((SIZES.get(split, 128), 4, 4, 3)) < np.array([.35, .35, .15])).astype(np.float64)
    y = ((x[..., 0] @ x[..., 1] > 0) & (x[..., 2] == 0)).astype(np.float64)
    return x, y


def initial(seed: int) -> dict:
    rng = np.random.default_rng(seed)
    return parameters({"left": rng.normal(0, .3, (1, 4)), "right": rng.normal(0, .3, (1, 4)),
                       "compose": [[1.0]], "readout": [[1.0, -1.0, -1.0]]})


def metrics(w: dict, x: np.ndarray, y: np.ndarray) -> dict:
    p, t = forward(w, x, trace=True)
    bce = np.mean(np.logaddexp(0, t["logits"]) - y * t["logits"])
    pred = p >= .5
    positive, negative = y == 1, y == 0
    tpr = float(pred[positive].mean()) if positive.any() else None
    tnr = float((~pred[negative]).mean()) if negative.any() else None
    return {"bce": float(bce), "accuracy": float(np.mean(pred == y)),
            "balanced_accuracy": (tpr + tnr) / 2 if tpr is not None and tnr is not None else None,
            "positive_fraction": float(y.mean()), "worlds": len(x), "decisions": y.size}


def accept(incumbent: dict, candidate: dict) -> bool:
    return candidate["bce"] < incumbent["bce"] - 1e-6 and candidate["accuracy"] >= incumbent["accuracy"] - .02


def digest_array(a: np.ndarray) -> str:
    return hashlib.sha256(a.astype("<f8").tobytes()).hexdigest()


def assert_split_separation(seed: int) -> dict:
    sets, ids = [], {}
    for split in SIZES:
        x, y = dataset(seed, split)
        hashes = {hashlib.sha256(world.tobytes()).hexdigest() for world in x}
        if len(hashes) != len(x) or any(hashes & s for s in sets):
            raise ValueError("duplicate relation world within or across splits")
        sets.append(hashes)
        ids[split] = {"inputs": digest_array(x), "labels": digest_array(y)}
    return ids
