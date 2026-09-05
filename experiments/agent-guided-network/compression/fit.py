"""Exact algebraic folding and non-agent numerical compression controls."""
from __future__ import annotations

from collections.abc import Mapping

import numpy as np

from compression.numeric import (Array, Encoding, Inputs, Kernel, Kernels, compute, expand_kernel,
                                 make_kernel, softmax)


def fold_weights(weights: Mapping[str, Array]) -> Kernels:
    first = weights["first-query"] @ weights["first-key"].T / np.sqrt(8)
    second = weights["first-value"] @ weights["first-output"] @ weights["second-query"] @ weights["second-key"].T / np.sqrt(8)
    output = weights["second-value"] @ weights["second-output"]
    return tuple(make_kernel(matrix, Encoding.DENSE) for matrix in (first, second, output))  # type: ignore[return-value]


def project_kernels(kernels: Kernels, encoding: Encoding, *, fraction: float = 1.0) -> Kernels:
    return tuple(make_kernel(expand_kernel(kernel), encoding, fraction=fraction) for kernel in kernels)  # type: ignore[return-value]


def loss(kernels: Kernels, inputs: Inputs, labels: Array) -> float:
    logits, _ = compute(tuple(expand_kernel(kernel) for kernel in kernels), inputs)
    maximum = logits.max(axis=1)
    return float(np.mean(maximum + np.log(np.exp(logits - maximum[:, None]).sum(axis=1))
                         - logits[np.arange(len(labels)), labels]))


def gradients(kernels: Kernels, inputs: Inputs, labels: Array) -> tuple[Array, ...]:
    matrices = tuple(expand_kernel(kernel) for kernel in kernels)
    logits, (bridge, alignment1, mixed, alignment2) = compute(matrices, inputs)
    dlogits = softmax(logits)
    dlogits[np.arange(len(labels)), labels] -= 1
    dlogits /= len(labels)
    output_gradient = mixed.T @ dlogits
    dmixed = dlogits @ matrices[2].T
    dalignment2 = np.einsum("bd,bld->bl", dmixed, inputs["VALUE2"])
    dscores2 = alignment2 * (dalignment2 - (alignment2 * dalignment2).sum(axis=1, keepdims=True))
    dprojected2 = np.einsum("bl,bld->bd", dscores2, inputs["KEY2"])
    second_gradient = bridge.T @ dprojected2
    dbridge = dprojected2 @ matrices[1].T
    dalignment1 = np.einsum("bd,bld->bl", dbridge, inputs["VALUE1"])
    dscores1 = alignment1 * (dalignment1 - (alignment1 * dalignment1).sum(axis=1, keepdims=True))
    first_gradient = inputs["QUERY"].T @ np.einsum("bl,bld->bd", dscores1, inputs["KEY1"])
    return tuple(_parameter_gradient(kernel, gradient) for kernel, gradient in
                 zip(kernels, (first_gradient, second_gradient, output_gradient), strict=True))


def _parameter_gradient(kernel: Kernel, gradient: Array) -> Array:
    match kernel.encoding:
        case Encoding.DENSE:
            return gradient.ravel()
        case Encoding.DIAGONAL:
            return gradient.diagonal().copy()
        case Encoding.IDENTITY:
            return np.array([np.trace(gradient)])
        case Encoding.SPARSE:
            return gradient.ravel()[list(kernel.indices)]
    raise ValueError("unknown encoding")


def fit_kernels(kernels: Kernels, training: tuple, development: tuple, *, steps: int = 200,
                rate: float = 0.05) -> tuple[Kernels, dict[str, object]]:
    """Fit final labels only; select checkpoints on independent development loss."""
    if not 0 < steps <= 1000 or not 0 < rate <= 1:
        raise ValueError("invalid fitting budget")
    parameters = [np.array(kernel.coefficients) for kernel in kernels]
    moments, variances = ([np.zeros_like(parameter) for parameter in parameters] for _ in range(2))
    best, current = kernels, kernels
    best_loss = loss(kernels, development[0], development[1])
    selected_step = 0
    for step in range(1, steps + 1):
        gradient_values = gradients(current, training[0], training[1])
        for index, gradient in enumerate(gradient_values):
            moments[index] = 0.9 * moments[index] + 0.1 * gradient
            variances[index] = 0.999 * variances[index] + 0.001 * gradient**2
            parameters[index] -= rate * (moments[index] / (1 - 0.9**step)) / (
                np.sqrt(variances[index] / (1 - 0.999**step)) + 1e-8)
            np.clip(parameters[index], -8192.0, 8192.0, out=parameters[index])
        current = tuple(Kernel(kernel.encoding, kernel.dimension, tuple(float(c) for c in parameter), kernel.indices)
                        for kernel, parameter in zip(kernels, parameters, strict=True))
        if step % 20 == 0 or step == steps:
            current_loss = loss(current, development[0], development[1])
            if current_loss < best_loss:
                best, best_loss, selected_step = current, current_loss, step
    return best, {"gradient-steps": steps, "checkpoint-evaluations": 1 + steps // 20,
                  "selected-step": selected_step, "rate": rate, "selected-development-loss": best_loss}
