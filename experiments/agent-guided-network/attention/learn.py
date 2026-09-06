"""Analytic differentiation and bounded optimiser tools, not artificial agents."""
from __future__ import annotations

import numpy as np
from attention.numeric import DIMENSION, compute, inputs, parameters, softmax

METHODS = ("joint", "first", "second", "sharpen-first", "sharpen-second", "sharpen-both", "soften-both", "cool-output", "sharpen-both-direct")
STEPS = 150
RATE = .025


def backward(dout: np.ndarray, cache: tuple, w: dict, stage: str) -> tuple[dict, np.ndarray]:
    q, k, v, qp, kp, vp, a, mixed = cache
    g = {stage+"-output": mixed.T @ dout}
    dm = dout @ w[stage+"-output"].T
    da = np.einsum("bd,bld->bl", dm, vp)
    ds = a*(da-(a*da).sum(axis=1, keepdims=True)) / np.sqrt(DIMENSION)
    dqp = np.einsum("bl,bld->bd", ds, kp)
    dkp = ds[:, :, None]*qp[:, None, :]
    dvp = a[:, :, None]*dm[:, None, :]
    g[stage+"-query"] = q.T @ dqp
    g[stage+"-key"] = np.einsum("bli,blj->ij", k, dkp)
    g[stage+"-value"] = np.einsum("bli,blj->ij", v, dvp)
    return g, dqp @ w[stage+"-query"].T


def gradients(w: dict, x: dict, y: np.ndarray) -> dict:
    logits, (first, second) = compute(w, x)
    dl = softmax(logits)
    dl[np.arange(len(y)), y] -= 1
    dl /= len(y)
    g2, dbridge = backward(dl, second, w, "second")
    g1, _ = backward(dbridge, first, w, "first")
    return g1 | g2


def adam(values: dict, data: tuple, *, steps: int, rate: float = RATE, owner: str = "both", dev: tuple | None = None) -> dict:
    if owner not in ("first", "second", "both") or not 0 <= steps <= 1200 or not 0 < rate <= .1:
        raise ValueError("invalid fitting budget or owner")
    w, x = parameters(values), inputs(data[0])
    y = np.asarray(data[1])
    if y.shape != (len(x["QUERY"]),) or y.dtype.kind not in "iu" or not np.isin(y, range(4)).all():
        raise ValueError("invalid labels")
    names = [name for name in w if owner == "both" or name.startswith(owner+"-")]
    m, v = ({name: np.zeros_like(w[name]) for name in names} for _ in range(2))
    from attention.task import metrics
    best = parameters(w)
    best_loss = metrics(w, dev)["cross-entropy"] if dev is not None else float("inf")
    for step in range(1, steps+1):
        g = gradients(w, x, y)
        for name in names:
            m[name] = .9*m[name]+.1*g[name]
            v[name] = .999*v[name]+.001*g[name]**2
            w[name] -= rate*(m[name]/(1-.9**step))/(np.sqrt(v[name]/(1-.999**step))+1e-8)
            np.clip(w[name], -64., 64., out=w[name])
        if dev is not None and (step % 25 == 0 or step == steps):
            loss = metrics(w, dev)["cross-entropy"]
            if loss < best_loss:
                best_loss, best = loss, parameters(w)
    return best if dev is not None else parameters(w)


def candidate(w: dict, data: tuple, method: str) -> dict:
    if method not in METHODS:
        raise ValueError("unsupported proposal method")
    c = parameters(w)
    if method == "cool-output":
        c["second-output"] *= .5
        return parameters(c)
    if method == "sharpen-both-direct":
        for stage in ("first", "second"):
            for name in ("query", "key"):
                c[stage+"-"+name] *= np.sqrt(2.)
        return parameters(c)
    if method.startswith(("sharpen-", "soften-")):
        scale = np.sqrt(2.) if method.startswith("sharpen-") else np.sqrt(.5)
        owner = method.split("-", 1)[1]
        for stage in ("first", "second"):
            if owner in (stage, "both"):
                for name in ("query", "key"):
                    c[stage+"-"+name] *= scale
        owner = "both"
    else:
        owner = method if method != "joint" else "both"
    return adam(c, data, steps=STEPS, owner=owner)
