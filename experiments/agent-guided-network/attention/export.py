"""Export and independently load a closed attention model without OAK or agents."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import numpy as np
from attention.author import load, revision
from attention.numeric import PROFILE, forward, load_model


def export(source: Path, destination: Path) -> dict:
    w, _ = load(source)
    model = {"profile": PROFILE, "dtype": "float64", "decoder": "argmax-first",
             "source-revision": revision(source), "weights": {k: v.tolist() for k, v in w.items()}}
    destination.mkdir(parents=True, exist_ok=False)
    (destination/"model.json").write_text(json.dumps(model, indent=2, sort_keys=True, allow_nan=False)+"\n")
    shutil.copyfile(Path(__file__).with_name("numeric.py"), destination/"inference.py")
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in destination.iterdir()}
    (destination/"SHA256SUMS.json").write_text(json.dumps(hashes, indent=2)+"\n")
    return model


def check(artifact: Path, w: dict, x: dict) -> dict:
    hashes = json.loads((artifact/"SHA256SUMS.json").read_text())
    if set(hashes) != {"inference.py", "model.json"}:
        raise ValueError("invalid artifact manifest")
    for name, expected in hashes.items():
        if hashlib.sha256((artifact/name).read_bytes()).hexdigest() != expected:
            raise ValueError("artifact hash mismatch")
    model = load_model(artifact/"model.json")
    for name in w:
        np.testing.assert_array_equal(w[name], model["weights"][name])
    expected = forward(w, x)
    with tempfile.TemporaryDirectory(prefix="oak-attention-offline-") as temporary:
        directory = Path(temporary)
        for name in hashes:
            shutil.copyfile(artifact/name, directory/name)
        np.savez(directory/"input.npz", **x)
        script = '''import sys, os, runpy
repo = os.path.realpath(sys.argv[1])
def audit(event, args):
    if event.startswith("socket."):
        raise RuntimeError("network forbidden")
    if event == "open" and isinstance(args[0], (str, bytes)):
        p = os.path.realpath(os.fsdecode(args[0]))
        if p.startswith(repo + os.sep) or p.endswith(".oak.md"):
            raise RuntimeError("repository/OAK access forbidden")
sys.addaudithook(audit)
sys.argv = ["inference.py", "model.json", "input.npz", "output.npy"]
runpy.run_path("inference.py", run_name="__main__")
assert not any(n == "oak" or n.startswith(("oak.", "training.", "attention.")) for n in sys.modules)
'''
        process = subprocess.run([sys.executable, "-I", "-c", script, str(Path(__file__).resolve().parents[3])],
                                 cwd=directory, env={"PATH": os.environ.get("PATH", ""), "HOME": str(directory),
                                                     "OPENBLAS_NUM_THREADS": "1"}, capture_output=True, text=True, timeout=30)
        if process.returncode:
            raise RuntimeError(process.stderr)
        actual = np.load(directory/"output.npy", allow_pickle=False)
    np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-12)
    np.testing.assert_array_equal(actual.argmax(axis=1), expected.argmax(axis=1))
    return {"max-absolute-error": float(np.max(np.abs(actual-expected))), "examples": len(expected),
            "decisions-identical": True, "parameters-identical": True, "isolated-process": True,
            "network-and-repository-blocked": True}
