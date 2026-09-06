"""Procedurally separated task data; test labels never drive candidate selection."""
from __future__ import annotations

import hashlib
import numpy as np
from attention.numeric import SHAPES, forward, parameters

SEEDS = (7, 19, 31)
SPLITS = {"train": (512, 6, 1000), "dev": (256, 6, 2000),
          "test": (512, 6, 3000), "long": (512, 16, 4000),
          "crowded": (512, 16, 5000)}


def unit(rng: np.random.Generator, shape: tuple) -> np.ndarray:
    v = rng.normal(size=shape)
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def dataset(seed: int, split: str) -> tuple[dict, np.ndarray, tuple]:
    n, length, offset = SPLITS[split]
    rng = np.random.default_rng(seed + offset)
    k1, v1, k2 = (unit(rng, (n, length, 8)) for _ in range(3))
    labels = rng.integers(4, size=(n, length))
    v2 = np.eye(4)[labels]
    count = rng.integers(3, length+1, size=(2, n))
    if split in ("long", "crowded"):
        count[:] = length
    m1, m2 = (np.arange(length)[None, :] < c[:, None] for c in count)
    i, j = (np.array([rng.integers(c) for c in row]) for row in count)
    rows = np.arange(n)
    k2[rows, j] = v1[rows, i]
    if split == "crowded":
        # Nearly identical but distinct keys, paired with different values.
        for keys, indices in ((k1, i), (k2, j)):
            tangent = unit(rng, (n, 8))
            target = keys[rows, indices]
            tangent -= (tangent*target).sum(axis=-1, keepdims=True)*target
            tangent /= np.linalg.norm(tangent, axis=-1, keepdims=True)
            keys[rows, (indices+1) % length] = np.cos(.12)*target + np.sin(.12)*tangent
        v2[rows, (j+1) % length] = np.eye(4)[(labels[rows, j]+1) % 4]
    q = k1[rows, i].copy()
    x = dict(zip(("QUERY", "KEY1", "VALUE1", "MASK1", "KEY2", "VALUE2", "MASK2"),
                 (q, k1, v1, m1.astype(float), k2, v2, m2.astype(float)), strict=True))
    return x, labels[rows, j], (i, j)


def initial(seed: int) -> dict:
    rng = np.random.default_rng(seed)
    # No identity metric is handed to Q/K. V/O start near identity for both methods.
    return parameters({name: (rng.normal(0, .2, shape) if name.endswith(("query", "key"))
                        else np.eye(shape[0])+rng.normal(0, .05, shape)) for name, shape in SHAPES.items()})


def metrics(w: dict, data: tuple, *, ablate: str = "none") -> dict:
    x, y, indices = data
    p, logits, caches = forward(w, x, trace=True, ablate=ablate)
    maximum = logits.max(axis=1)
    logsum = maximum + np.log(np.exp(logits-maximum[:, None]).sum(axis=1))
    result = {"accuracy": float(np.mean(p.argmax(axis=1) == y)),
              "cross-entropy": float(np.mean(logsum-logits[np.arange(len(y)), y])),
              "examples": len(y)}
    for stage, cache, target in zip(("first", "second"), caches, indices, strict=True):
        a = cache[6]
        result[stage] = {"target-top1": float(np.mean(a.argmax(axis=1) == target)),
                         "target-mass": float(a[np.arange(len(y)), target].mean()),
                         "entropy": float(-(a*np.log(np.maximum(a, 1e-300))).sum(axis=1).mean())}
    return result


def identity(data: tuple) -> str:
    x, y, indices = data
    h = hashlib.sha256()
    for name, value in [*sorted(x.items()), ("labels", y), ("first-index", indices[0]), ("second-index", indices[1])]:
        h.update(name.encode()+str(value.shape).encode()+value.astype("<f8").tobytes())
    return h.hexdigest()


def accept(before: dict, after: dict) -> bool:
    return after["cross-entropy"] < before["cross-entropy"]-1e-6 and after["accuracy"] >= before["accuracy"]-.01
