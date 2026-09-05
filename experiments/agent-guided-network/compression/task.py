"""Fresh two-hop tasks; development diversity is not recycled test evidence."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib

import numpy as np
from numpy.typing import NDArray

from compression.numeric import Array, Inputs, Kernels, compute, expand_kernel, softmax

SEEDS = (107, 223, 331)
REGIMES = {"short": (6, None), "long": (16, None), "crowded": (16, 0.12), "extreme": (32, 0.04)}
DEVELOPMENT_REGIMES = ("short", "long", "crowded")
SAMPLE_COUNTS = {"train": 192, "dev": 192, "test": 1024}
Labels = NDArray[np.int64]


@dataclass(frozen=True, slots=True)
class Cases:
    inputs: Inputs
    labels: Labels
    first_target: Labels
    second_target: Labels


def _unit(rng: np.random.Generator, shape: tuple[int, ...]) -> Array:
    vectors = rng.normal(size=shape)
    return vectors / np.linalg.norm(vectors, axis=-1, keepdims=True)


def sample_cases(seed: int, split: str, regime: str) -> Cases:
    if split not in SAMPLE_COUNTS or regime not in REGIMES or seed < 0:
        raise ValueError("invalid sampling recipe")
    count = SAMPLE_COUNTS[split]
    length, angle = REGIMES[regime]
    rng = np.random.default_rng(np.random.SeedSequence([20260906, seed, tuple(SAMPLE_COUNTS).index(split),
                                                      tuple(REGIMES).index(regime)]))
    keys1, values1, keys2 = (_unit(rng, (count, length, 8)) for _ in range(3))
    classes = rng.integers(4, size=(count, length))
    values2 = np.eye(4)[classes]
    lengths = rng.integers(3, length + 1, size=(2, count)) if regime == "short" else np.full((2, count), length)
    mask1, mask2 = (np.arange(length)[None, :] < row[:, None] for row in lengths)
    first, second = (np.array([rng.integers(size) for size in row]) for row in lengths)
    rows = np.arange(count)
    keys2[rows, second] = values1[rows, first]
    if angle is not None:
        for keys, target in ((keys1, first), (keys2, second)):
            tangent = _unit(rng, (count, 8))
            direction = keys[rows, target]
            tangent -= (tangent * direction).sum(axis=-1, keepdims=True) * direction
            tangent /= np.linalg.norm(tangent, axis=-1, keepdims=True)
            keys[rows, (target + 1) % length] = np.cos(angle) * direction + np.sin(angle) * tangent
        values2[rows, (second + 1) % length] = np.eye(4)[(classes[rows, second] + 1) % 4]
    return Cases({"QUERY": keys1[rows, first].copy(), "KEY1": keys1, "VALUE1": values1,
                  "MASK1": mask1.astype(float), "KEY2": keys2, "VALUE2": values2, "MASK2": mask2.astype(float)},
                 classes[rows, second], first, second)


def combine_cases(groups: tuple[Cases, ...]) -> Cases:
    maximum = max(group.inputs["KEY1"].shape[1] for group in groups)
    batches: dict[str, list[Array]] = {name: [] for name in groups[0].inputs}
    for group in groups:
        for name, tensor in group.inputs.items():
            if name != "QUERY":
                padding = [(0, 0), (0, maximum - tensor.shape[1])] + ([(0, 0)] if tensor.ndim == 3 else [])
                tensor = np.pad(tensor, padding)
            batches[name].append(tensor)
    return Cases({name: np.concatenate(parts) for name, parts in batches.items()},
                 np.concatenate([group.labels for group in groups]),
                 np.concatenate([group.first_target for group in groups]),
                 np.concatenate([group.second_target for group in groups]))


def numerical_tuple(cases: Cases) -> tuple[Inputs, Labels]:
    return cases.inputs, cases.labels


def case_hash(cases: Cases) -> str:
    digest = hashlib.sha256()
    for name, tensor in [*sorted(cases.inputs.items()), ("labels", cases.labels),
                         ("first-target", cases.first_target), ("second-target", cases.second_target)]:
        digest.update(name.encode() + str(tensor.shape).encode() + tensor.astype("<f8").tobytes())
    return digest.hexdigest()


def measure(kernels: Kernels, cases: Cases) -> dict[str, object]:
    matrices = tuple(expand_kernel(kernel) for kernel in kernels)
    logits, (_, first, _, second) = compute(matrices, cases.inputs)
    return measure_logits(logits, cases.labels) | {
        "first-target-top1": float(np.mean(first.argmax(axis=1) == cases.first_target)),
        "second-target-top1": float(np.mean(second.argmax(axis=1) == cases.second_target)),
        "first-target-mass": float(first[np.arange(len(first)), cases.first_target].mean()),
        "second-target-mass": float(second[np.arange(len(second)), cases.second_target].mean()),
    }


def measure_logits(logits: Array, labels: Labels) -> dict[str, object]:
    maximum = logits.max(axis=1)
    cross_entropy = maximum + np.log(np.exp(logits - maximum[:, None]).sum(axis=1)) - logits[np.arange(len(labels)), labels]
    return {"accuracy": float(np.mean(logits.argmax(axis=1) == labels)), "cross-entropy": float(cross_entropy.mean()),
            "examples": len(labels)}


def nearest_key(cases: Cases) -> Labels:
    """Task-structure control, not neural inference or access to hidden targets."""
    inputs = cases.inputs
    first_scores = np.einsum("bd,bld->bl", inputs["QUERY"], inputs["KEY1"])
    first = np.where(inputs["MASK1"] == 1, first_scores, -np.inf).argmax(axis=1)
    bridge = inputs["VALUE1"][np.arange(len(first)), first]
    second_scores = np.einsum("bd,bld->bl", bridge, inputs["KEY2"])
    second = np.where(inputs["MASK2"] == 1, second_scores, -np.inf).argmax(axis=1)
    return inputs["VALUE2"][np.arange(len(second)), second].argmax(axis=1)
