"""Closed compact attention inference; this file is also the standalone export."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
import json
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

PROFILE = "oak-compact-attention-v1"
DIMENSIONS = (8, 8, 4)
COEFFICIENT_LIMIT = 8192.0
FIELDS = ("QUERY", "KEY1", "VALUE1", "MASK1", "KEY2", "VALUE2", "MASK2")
Array = NDArray[np.float64]
Inputs = dict[str, Array]


class Encoding(StrEnum):
    DENSE = "dense"
    DIAGONAL = "diagonal"
    IDENTITY = "scaled-identity"
    SPARSE = "sparse"


@dataclass(frozen=True, slots=True)
class Kernel:
    encoding: Encoding
    dimension: int
    coefficients: tuple[float, ...]
    indices: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if type(self.dimension) is not int or self.dimension not in (4, 8):
            raise ValueError("kernel dimension must be 4 or 8")
        if not isinstance(self.encoding, Encoding):
            raise ValueError("unknown kernel encoding")
        if not isinstance(self.coefficients, tuple) or not isinstance(self.indices, tuple):
            raise ValueError("kernel values must be immutable tuples")
        if any(type(c) is not float or not np.isfinite(c) or abs(c) > COEFFICIENT_LIMIT for c in self.coefficients):
            raise ValueError("expected finite bounded float coefficients")
        counts = {Encoding.DENSE: self.dimension**2, Encoding.DIAGONAL: self.dimension,
                  Encoding.IDENTITY: 1, Encoding.SPARSE: len(self.indices)}
        if len(self.coefficients) != counts[self.encoding]:
            raise ValueError("coefficient count differs from encoding")
        if self.encoding != Encoding.SPARSE and self.indices:
            raise ValueError("only sparse kernels carry indices")
        if any(type(i) is not int or not 0 <= i < self.dimension**2 for i in self.indices):
            raise ValueError("invalid sparse index")
        if self.indices != tuple(sorted(set(self.indices))):
            raise ValueError("sparse indices must be sorted and unique")


Kernels = tuple[Kernel, Kernel, Kernel]


def kernel_record(kernel: Kernel) -> dict[str, object]:
    return {"encoding": kernel.encoding.value, "dimension": kernel.dimension,
            "coefficients": list(kernel.coefficients), "indices": list(kernel.indices)}


def read_kernel(record: object) -> Kernel:
    if not isinstance(record, dict) or set(record) != {"encoding", "dimension", "coefficients", "indices"}:
        raise ValueError("invalid kernel fields")
    if not isinstance(record["coefficients"], list) or not isinstance(record["indices"], list):
        raise ValueError("kernel arrays must be lists")
    return Kernel(Encoding(record["encoding"]), record["dimension"],
                  tuple(record["coefficients"]), tuple(record["indices"]))


def read_kernels(records: object) -> Kernels:
    if not isinstance(records, list) or len(records) != 3:
        raise ValueError("three kernels are required")
    kernels = tuple(read_kernel(record) for record in records)
    if tuple(kernel.dimension for kernel in kernels) != DIMENSIONS:
        raise ValueError("kernel dimensions do not match the numerical profile")
    return kernels  # type: ignore[return-value]


def expand_kernel(kernel: Kernel) -> Array:
    coefficients = np.array(kernel.coefficients, dtype=np.float64)
    match kernel.encoding:
        case Encoding.DENSE:
            return coefficients.reshape(kernel.dimension, kernel.dimension)
        case Encoding.DIAGONAL:
            return np.diag(coefficients)
        case Encoding.IDENTITY:
            return np.eye(kernel.dimension) * coefficients[0]
        case Encoding.SPARSE:
            matrix = np.zeros((kernel.dimension, kernel.dimension))
            matrix.flat[list(kernel.indices)] = coefficients
            return matrix
    raise ValueError("unknown kernel encoding")


def make_kernel(matrix: Array, encoding: Encoding, *, fraction: float = 1.0) -> Kernel:
    dimension = len(matrix)
    if matrix.shape != (dimension, dimension):
        raise ValueError("kernel must be square")
    indices: tuple[int, ...] = ()
    match encoding:
        case Encoding.DENSE:
            coefficients = matrix.ravel()
        case Encoding.DIAGONAL:
            coefficients = matrix.diagonal()
        case Encoding.IDENTITY:
            coefficients = np.array([np.trace(matrix) / dimension])
        case Encoding.SPARSE:
            if not 0 < fraction <= 1:
                raise ValueError("sparse fraction must be in (0,1]")
            count = max(1, int(np.ceil(matrix.size * fraction)))
            selected = np.argsort(-np.abs(matrix.ravel()), kind="stable")[:count]
            indices = tuple(int(i) for i in sorted(selected))
            coefficients = matrix.ravel()[list(indices)]
    return Kernel(encoding, dimension, tuple(float(c) for c in coefficients), indices)


def place_gains(gains: tuple[float, float, float]) -> Kernels:
    if len(gains) != 3 or any(g <= 0 for g in gains):
        raise ValueError("three positive gains are required")
    return tuple(Kernel(Encoding.IDENTITY, dimension, (gain,))
                 for dimension, gain in zip(DIMENSIONS, gains, strict=True))  # type: ignore[return-value]


def _reject_boolean_entries(record: object) -> None:
    if isinstance(record, (bool, np.bool_)):
        raise ValueError("boolean tensor entries are forbidden")
    if isinstance(record, (list, tuple)):
        for element in record:
            _reject_boolean_entries(element)


def validate_inputs(records: Mapping[str, object]) -> Inputs:
    if set(records) != set(FIELDS):
        raise ValueError("unexpected input fields")
    for record in records.values():
        _reject_boolean_entries(record)
    arrays = {name: np.asarray(records[name]) for name in FIELDS}
    if any(a.dtype.kind not in "ifu" or not a.size or not np.isfinite(a).all() for a in arrays.values()):
        raise ValueError("expected nonempty finite numerical arrays")
    arrays = {name: a.astype(np.float64, copy=True) for name, a in arrays.items()}
    query = arrays["QUERY"]
    if query.ndim != 2 or query.shape[1] != 8 or not 1 <= len(query) <= 4096:
        raise ValueError("query shape must be [batch,8], batch in 1..4096")
    for hop, width in ((1, 8), (2, 4)):
        keys, values, mask = (arrays[f"{field}{hop}"] for field in ("KEY", "VALUE", "MASK"))
        if keys.ndim != 3 or keys.shape[0] != len(query) or keys.shape[2] != 8 or not 1 <= keys.shape[1] <= 64:
            raise ValueError("invalid key dimensions")
        if values.shape != (*keys.shape[:2], width) or mask.shape != keys.shape[:2]:
            raise ValueError("invalid value or mask dimensions")
        if not np.isin(mask, (0.0, 1.0)).all() or np.any(mask.sum(axis=1) == 0):
            raise ValueError("invalid or all-masked input")
    if any(np.abs(a).max() > 4 for a in arrays.values()):
        raise ValueError("input magnitude exceeds four")
    return arrays


def softmax(logits: Array) -> Array:
    exponentials = np.exp(logits - logits.max(axis=-1, keepdims=True))
    return exponentials / exponentials.sum(axis=-1, keepdims=True)


def attend(query: Array, keys: Array, values: Array, mask: Array, kernel: Array) -> tuple[Array, Array]:
    scores = np.einsum("bd,bld->bl", query @ kernel, keys)
    alignment = softmax(np.where(mask == 1, scores, -np.inf))
    return np.einsum("bl,bld->bd", alignment, values), alignment


def compute(matrices: tuple[Array, Array, Array], inputs: Inputs) -> tuple[Array, tuple]:
    first, second, output = matrices
    bridge, alignment1 = attend(inputs["QUERY"], inputs["KEY1"], inputs["VALUE1"], inputs["MASK1"], first)
    mixed, alignment2 = attend(bridge, inputs["KEY2"], inputs["VALUE2"], inputs["MASK2"], second)
    return mixed @ output, (bridge, alignment1, mixed, alignment2)


def forward(kernels: Kernels, inputs: Mapping[str, object]) -> Array:
    if tuple(kernel.dimension for kernel in kernels) != DIMENSIONS:
        raise ValueError("invalid network dimensions")
    matrices = tuple(expand_kernel(kernel) for kernel in kernels)
    logits, _ = compute(matrices, validate_inputs(inputs))
    probabilities = softmax(logits)
    if not np.isfinite(probabilities).all():
        raise ValueError("non-finite output")
    return probabilities


def model_record(kernels: Kernels, revision: str) -> dict[str, object]:
    return {"profile": PROFILE, "dtype": "float64", "decoder": "argmax-first", "source-revision": revision,
            "kernels": [kernel_record(kernel) for kernel in kernels]}


def load_model(model_file: Path) -> Kernels:
    record = json.loads(model_file.read_text(encoding="utf-8"))
    if set(record) != {"profile", "dtype", "decoder", "source-revision", "kernels"}:
        raise ValueError("invalid model fields")
    if record["profile"] != PROFILE or record["dtype"] != "float64" or record["decoder"] != "argmax-first":
        raise ValueError("unsupported model profile")
    return read_kernels(record["kernels"])


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        raise SystemExit("usage: inference.py MODEL.json INPUT.npz OUTPUT.npy")
    with np.load(sys.argv[2], allow_pickle=False) as batch:
        predictions = forward(load_model(Path(sys.argv[1])), dict(batch))
    np.save(sys.argv[3], predictions)
