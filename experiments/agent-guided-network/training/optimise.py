"""Numerical tools only. Calling these functions is not an autonomous agent."""
from __future__ import annotations
import numpy as np
from runtime.numeric import forward, parameters
from evaluation.task import metrics


def gradients(w: dict, x: np.ndarray, y: np.ndarray) -> dict:
    p, t = forward(w, x, trace=True)
    q = (p - y) / y.size
    dc = q * w["readout"][0, 0]
    dl = (dc @ t["right"].swapaxes(-1, -2)) * t["left"] * (1 - t["left"])
    dr = (t["left"].swapaxes(-1, -2) @ dc) * t["right"] * (1 - t["right"])
    def selector(d):
        return np.array([[*(d[..., None] * x).sum(axis=(0, 1, 2)), d.sum()]])
    return {"left": selector(dl), "right": selector(dr),
            "readout": np.array([[(q*t["count"]).sum(), (q*x[..., 2]).sum(), q.sum()]])}


def adam(w: dict, x: np.ndarray, y: np.ndarray, *, steps: int, rate: float,
         owners: tuple[str, ...] = ("left", "right", "readout"), dev=None):
    w = parameters(w)
    m = {k: np.zeros_like(w[k]) for k in owners}
    v = {k: np.zeros_like(w[k]) for k in owners}
    best = parameters(w)
    best_loss = metrics(w, *dev)["bce"] if dev else float("inf")
    for step in range(1, steps + 1):
        g = gradients(w, x, y)
        for k in owners:
            m[k] = .9*m[k] + .1*g[k]
            v[k] = .999*v[k] + .001*g[k]**2
            w[k] -= rate*(m[k]/(1-.9**step))/(np.sqrt(v[k]/(1-.999**step))+1e-8)
            np.clip(w[k], -64, 64, out=w[k])
        if dev and step % 25 == 0:
            loss = metrics(w, *dev)["bce"]
            if loss < best_loss:
                best_loss, best = loss, parameters(w)
    return best if dev else parameters(w)


def fit_concept(w: dict, x: np.ndarray, owner: str, *, ridge: float = .001):
    if owner not in ("left", "right"):
        raise ValueError("concept fitting only supports relation selectors")
    # Task rule and these intermediate targets are disclosed to every treatment.
    channel = 0 if owner == "left" else 1
    a = np.column_stack([x.reshape(-1, 3), np.ones(x[..., 0].size)])
    target = np.log(99.0)*(2*x[..., channel].reshape(-1)-1)
    old = w[owner][0]
    output = forward(w, x, trace=True)[1][owner].reshape(-1)
    protected = np.abs(output - x[..., channel].reshape(-1)) < .05
    preserve = a[protected]
    design = np.concatenate([a, preserve, np.sqrt(ridge)*np.eye(4)])
    residual = np.concatenate([target-a@old, np.zeros(len(preserve)+4)])
    delta = np.linalg.lstsq(design, residual, rcond=None)[0]
    candidate = parameters(w)
    candidate[owner] = (old+delta).reshape(1, 4)
    parameters(candidate)
    return candidate, {"fit_rows": len(a), "preservation_rows": len(preserve),
                       "delta_norm": float(np.linalg.norm(delta)), "ridge": ridge}
