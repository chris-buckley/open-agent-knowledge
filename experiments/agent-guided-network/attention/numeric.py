"""Agent-free two-hop, single-head scaled dot-product cross-attention."""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np

PROFILE = "oak-attention-two-hop-v1"
DIMENSION = 8
CLASSES = 4
SHAPES = {f"{stage}-{name}": (size, size)
          for stage in ("first", "second")
          for name, size in (("query", 8), ("key", 8), ("value", 8 if stage == "first" else 4),
                             ("output", 8 if stage == "first" else 4))}
FIELDS = ("QUERY", "KEY1", "VALUE1", "MASK1", "KEY2", "VALUE2", "MASK2")


def array(value: object) -> np.ndarray:
    """Validate before float conversion; booleans and strings are not numbers here."""
    def inspect(item: object) -> None:
        if isinstance(item, (bool, np.bool_)):
            raise ValueError("boolean tensor entries are forbidden")
        if isinstance(item, (list, tuple)):
            for child in item:
                inspect(child)
    inspect(value)
    a = np.asarray(value)
    if a.dtype.kind not in "ifu" or not a.size or not np.isfinite(a).all():
        raise ValueError("expected nonempty finite numerical tensor")
    return a.astype(np.float64, copy=True)


def parameters(values: dict) -> dict[str, np.ndarray]:
    if set(values) != set(SHAPES):
        raise ValueError("missing or extra parameter")
    result = {name: array(values[name]) for name in SHAPES}
    for name, shape in SHAPES.items():
        if result[name].shape != shape or np.max(np.abs(result[name])) > 64:
            raise ValueError(f"invalid parameter shape or magnitude: {name}")
    return result


def inputs(values: dict) -> dict[str, np.ndarray]:
    if set(values) != set(FIELDS):
        raise ValueError("missing or extra input")
    x = {name: array(values[name]) for name in FIELDS}
    q = x["QUERY"]
    if q.ndim != 2 or q.shape[1] != DIMENSION or not 1 <= len(q) <= 4096:
        raise ValueError("query must have shape [batch,8], batch in 1..4096")
    for stage, width in ((1, 8), (2, 4)):
        k, v, mask = (x[f"{kind}{stage}"] for kind in ("KEY", "VALUE", "MASK"))
        if k.ndim != 3 or k.shape[0] != len(q) or k.shape[2] != 8 or not 1 <= k.shape[1] <= 64:
            raise ValueError("keys must have shape [batch,length,8], length in 1..64")
        if v.shape != (*k.shape[:2], width) or mask.shape != k.shape[:2]:
            raise ValueError("value or mask shape mismatch")
        if not np.isin(mask, (0., 1.)).all() or np.any(mask.sum(axis=1) == 0):
            raise ValueError("mask must contain zero/one and retain at least one key per query")
    if any(np.max(np.abs(a)) > 4 for a in x.values()):
        raise ValueError("input magnitude exceeds four")
    return x


def softmax(logits: np.ndarray) -> np.ndarray:
    values = np.exp(logits - logits.max(axis=-1, keepdims=True))
    return values / values.sum(axis=-1, keepdims=True)


def attention(q: np.ndarray, k: np.ndarray, v: np.ndarray, mask: np.ndarray,
              w: dict, stage: str, *, uniform: bool = False) -> tuple[np.ndarray, tuple]:
    qp, kp, vp = q @ w[stage+"-query"], k @ w[stage+"-key"], v @ w[stage+"-value"]
    scores = np.einsum("bd,bld->bl", qp, kp) / np.sqrt(DIMENSION)
    if uniform:
        scores = np.zeros_like(scores)
    weights = softmax(np.where(mask == 1, scores, -np.inf))
    mixed = np.einsum("bl,bld->bd", weights, vp)
    out = mixed @ w[stage+"-output"]
    return out, (q, k, v, qp, kp, vp, weights, mixed)


def compute(w: dict, x: dict, *, ablate: str = "none") -> tuple[np.ndarray, tuple]:
    """Internal hot path. Public callers validate once with forward."""
    bridge, first = attention(x["QUERY"], x["KEY1"], x["VALUE1"], x["MASK1"], w, "first",
                              uniform=ablate in ("first", "both"))
    logits, second = attention(bridge, x["KEY2"], x["VALUE2"], x["MASK2"], w, "second",
                               uniform=ablate in ("second", "both"))
    return logits, (first, second)


def forward(values: dict, data: dict, *, trace: bool = False, ablate: str = "none"):
    if ablate not in ("none", "first", "second", "both"):
        raise ValueError("unknown attention intervention")
    logits, caches = compute(parameters(values), inputs(data), ablate=ablate)
    probability = softmax(logits)
    if not np.isfinite(probability).all():
        raise ValueError("non-finite inference output")
    return (probability, logits, caches) if trace else probability


def load_model(path: Path) -> dict:
    model = json.loads(path.read_text())
    if set(model) != {"profile", "dtype", "source-revision", "weights", "decoder"}:
        raise ValueError("unknown export fields")
    if model["profile"] != PROFILE or model["dtype"] != "float64" or model["decoder"] != "argmax-first":
        raise ValueError("unsupported numerical profile")
    parameters(model["weights"])
    return model


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        raise SystemExit("usage: inference.py MODEL.json INPUT.npz OUTPUT.npy")
    model = load_model(Path(sys.argv[1]))
    with np.load(sys.argv[2], allow_pickle=False) as source:
        data = dict(source)
    np.save(sys.argv[3], forward(model["weights"], data))
