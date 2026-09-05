"""Validate and lower one closed OAK profile; reject all other authored behaviour."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np
from oak import parse, render, resolve, execute, Arrival, ToolContract
from nodes.author import documents, SPEC, target
from runtime.numeric import parameters, inputs, sigmoid, PROFILE, OPERATIONS


def source_revision(directory: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(directory.iterdir()):
        if not p.is_file() or p.is_symlink() or p.suffix != ".md":
            raise ValueError("snapshot contains a non-document or symlink")
        h.update(p.name.encode()+b"\0"+p.read_bytes()+b"\0")
    return h.hexdigest()


def load(directory: Path):
    directory = directory.resolve()
    paths = list(directory.iterdir())
    if any(p.is_symlink() or not p.is_file() for p in paths):
        raise ValueError("snapshot must contain only regular OAK files")
    parsed = {p.name: parse(p.read_text()) for p in paths}
    values = {}
    for owner in SPEC:
        node = parsed[owner+".oak.md"]
        values[owner] = next(c.value for c in node.constants if c.id == "weights")
    w = parameters(values)
    expected = documents(w)
    if set(parsed) != set(expected):
        raise ValueError("missing or extra OAK document")
    for name in parsed:
        # Full structural equality covers schemas, instructions, actions, routing,
        # constant ownership, and wiring. No policy is silently erased at export.
        if parsed[name] != expected[name] or render(parsed[name]) != (directory/name).read_text():
            raise ValueError(f"unsupported or non-canonical profile document: {name}")
    graph = resolve(parsed["network.oak.md"], source="network.oak.md", load=lambda p: parsed[p])
    return w, graph


def oak_forward(directory: Path, data: object) -> np.ndarray:
    w, graph = load(directory)
    x = inputs(data)
    def handler(owner):
        def run(_step, values):
            a = np.array(values["W"], dtype=np.float64)
            if owner in ("left", "right"):
                b = inputs(values["X"])
                out = sigmoid(b @ a[0, :3] + a[0, 3])
            elif owner == "compose":
                out = a[0, 0]*(np.array(values["LEFT"]) @ np.array(values["RIGHT"]))
            else:
                out = sigmoid(a[0, 0]*np.array(values["COUNT"])+a[0, 1]*np.array(values["X"])[..., 2]+a[0, 2])
            return {SPEC[owner][3]: out.tolist()}
        return run
    tools = {"tensor."+k+".v1": ToolContract(handler(k), frozenset(v[1]+["W"]), frozenset([v[3]]),
             input=target(k+"-action"), output=target(v[2])) for k, v in SPEC.items()}
    result = execute(graph.documents[graph.root], Arrival(interface="interface.input", values={"X": x.tolist()}), {}, tools=tools, source=graph.root, load=lambda p: graph.documents[p])
    return np.array(result.emissions[0].values["PROB"])


def export(directory: Path, destination: Path):
    w, _ = load(directory)
    revision = source_revision(directory)
    destination.mkdir(parents=True, exist_ok=False)
    model = {"profile": PROFILE, "operations": list(OPERATIONS), "source_revision": revision,
             "dtype": "float64", "weights": {k: v.tolist() for k,v in w.items()}, "threshold": .5}
    (destination/"model.json").write_text(json.dumps(model, sort_keys=True, indent=2)+"\n")
    shutil.copyfile(Path(__file__).with_name("numeric.py"), destination/"inference.py")
    manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(destination.iterdir())}
    (destination/"SHA256SUMS.json").write_text(json.dumps(manifest, indent=2)+"\n")
    return model
