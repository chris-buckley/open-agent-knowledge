"""Agent-free float64 inference for the fixed four-module pilot profile."""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np

PROFILE = "oak-two-hop-v1"
SHAPES = {"left": (1, 4), "right": (1, 4), "compose": (1, 1), "readout": (1, 3)}
OPERATIONS = ("tensor.left.v1", "tensor.right.v1", "tensor.compose.v1", "tensor.readout.v1")


def array(value: object, shape: tuple[int, ...] | None = None) -> np.ndarray:
    """Reject coercible strings, booleans, ragged, empty, and non-finite tensors."""
    def reject_bool(v):
        if isinstance(v, (bool, np.bool_)):
            raise ValueError("boolean tensor entries are forbidden")
        if isinstance(v, (list, tuple)):
            for item in v: reject_bool(item)
    reject_bool(value)
    a = np.asarray(value)
    if a.dtype.kind not in "ifu" or not a.size or not np.isfinite(a).all():
        raise ValueError("tensor must contain finite numeric values, not booleans or strings")
    if shape is not None and a.shape != shape:
        raise ValueError(f"expected tensor shape {shape}, got {a.shape}")
    return a.astype(np.float64, copy=True)


def parameters(values: dict) -> dict[str, np.ndarray]:
    if set(values) != set(SHAPES):
        raise ValueError("missing or extra parameter owner")
    result = {k: array(values[k], shape) for k, shape in SHAPES.items()}
    if any(np.max(np.abs(v)) > 64 for v in result.values()):
        raise ValueError("parameter magnitude exceeds 64")
    if result["compose"][0, 0] != 1.0:
        raise ValueError("composition gain is frozen at one")
    return result


def inputs(value: object) -> np.ndarray:
    x = array(value)
    if x.ndim != 4 or x.shape[1:] != (4, 4, 3) or not 1 <= len(x) <= 4096:
        raise ValueError("input must have shape [batch,4,4,3], batch in 1..4096")
    if np.any((x < 0) | (x > 1)):
        raise ValueError("relation inputs must lie in [0,1]")
    return x


def sigmoid(z: np.ndarray) -> np.ndarray:
    # Stable without clipping the logits or changing the mathematical function.
    return np.exp(-np.logaddexp(0.0, -z))


def forward(values: dict, data: object, *, trace: bool = False):
    w, x = parameters(values), inputs(data)
    left = sigmoid(x @ w["left"][0, :3] + w["left"][0, 3])
    right = sigmoid(x @ w["right"][0, :3] + w["right"][0, 3])
    count = w["compose"][0, 0] * (left @ right)
    logits = w["readout"][0, 0] * count + w["readout"][0, 1] * x[..., 2] + w["readout"][0, 2]
    probability = sigmoid(logits)
    if trace:
        return probability, {"left": left, "right": right, "count": count, "logits": logits}
    return probability


def load_model(path: Path) -> dict:
    model = json.loads(path.read_text())
    if set(model) != {"profile", "operations", "source_revision", "dtype", "weights", "threshold"}:
        raise ValueError("unknown model fields")
    if model["profile"] != PROFILE or model["operations"] != list(OPERATIONS):
        raise ValueError("unsupported inference graph")
    if model["dtype"] != "float64" or model["threshold"] != 0.5:
        raise ValueError("unsupported numerical policy")
    parameters(model["weights"])
    return model


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        raise SystemExit("usage: inference.py MODEL.json INPUT.npy OUTPUT.npy")
    model = load_model(Path(sys.argv[1]))
    np.save(sys.argv[3], forward(model["weights"], np.load(sys.argv[2], allow_pickle=False)))
