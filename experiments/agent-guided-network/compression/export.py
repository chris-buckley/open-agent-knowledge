"""Measure actual export sizes and verify a clean agent-free process."""
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

from compression.numeric import Inputs, Kernels, expand_kernel, forward, load_model, model_record
from compression.oak_io import documents, load_snapshot, snapshot_hash
from oak import render


def json_bytes(record: object) -> bytes:
    return (json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def storage(kernels: Kernels) -> dict[str, int]:
    coefficients = sum(len(kernel.coefficients) for kernel in kernels)
    indices = sum(len(kernel.indices) for kernel in kernels)
    return {"stored-coefficients": coefficients, "float64-coefficient-bytes": coefficients * 8,
        "expanded-matrix-positions": 144, "expanded-nonzeros": sum(int(np.count_nonzero(expand_kernel(kernel))) for kernel in kernels),
        "sparse-indices": indices, "uint16-equivalent-index-bytes": indices * 2,
        "model-bytes": len(json_bytes(model_record(kernels, "0" * 64))),
        "canonical-oak-bytes": sum(len(render(node).encode()) for node in documents(kernels).values())}


def export_snapshot(source: Path, destination: Path) -> dict[str, int]:
    kernels = load_snapshot(source)
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "model.json").write_bytes(json_bytes(model_record(kernels, snapshot_hash(source))))
    shutil.copyfile(Path(__file__).with_name("numeric.py"), destination / "inference.py")
    (destination / "requirements.txt").write_text("numpy>=2.3,<3\n", encoding="utf-8")
    manifest = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(destination.iterdir())}
    (destination / "SHA256SUMS.json").write_bytes(json_bytes(manifest))
    return storage(kernels) | {"runtime-bytes": (destination / "inference.py").stat().st_size,
        "export-bytes": sum(path.stat().st_size for path in destination.iterdir()),
        "manifest-bytes": (destination / "SHA256SUMS.json").stat().st_size}


def verify_export(directory: Path, kernels: Kernels, inputs: Inputs) -> dict[str, object]:
    manifest = json.loads((directory / "SHA256SUMS.json").read_bytes())
    if set(manifest) != {"model.json", "inference.py", "requirements.txt"}:
        raise ValueError("unexpected export manifest")
    if set(path.name for path in directory.iterdir()) != set(manifest) | {"SHA256SUMS.json"}:
        raise ValueError("unexpected export files")
    for filename, expected in manifest.items():
        path = directory / filename
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("export integrity failure")
    if load_model(directory / "model.json") != kernels:
        raise ValueError("export parameters differ from OAK source")
    expected_output = forward(kernels, inputs)
    with tempfile.TemporaryDirectory(prefix="oak-compact-offline-") as temporary:
        isolated = Path(temporary)
        for filename in manifest:
            shutil.copyfile(directory / filename, isolated / filename)
        np.savez(isolated / "input.npz", **inputs)
        script = '''import os, runpy, sys
repository = os.path.realpath(sys.argv[1])
def audit(event, args):
    if event.startswith("socket."):
        raise RuntimeError("network access forbidden")
    if event == "open" and isinstance(args[0], (str, bytes)):
        path = os.path.realpath(os.fsdecode(args[0]))
        if path.startswith(repository + os.sep) or path.endswith(".oak.md"):
            raise RuntimeError("repository or OAK access forbidden")
sys.addaudithook(audit)
sys.argv = ["inference.py", "model.json", "input.npz", "output.npy"]
runpy.run_path("inference.py", run_name="__main__")
assert not any(name == "oak" or name.startswith(("oak.", "compression.", "attention.")) for name in sys.modules)
'''
        completed = subprocess.run([sys.executable, "-I", "-c", script, str(Path(__file__).resolve().parents[3])],
            cwd=isolated, env={"PATH": os.environ.get("PATH", ""), "HOME": str(isolated), "OPENBLAS_NUM_THREADS": "1"},
            capture_output=True, text=True, timeout=30, check=False)
        if completed.returncode:
            raise RuntimeError(completed.stderr)
        actual_output = np.load(isolated / "output.npy", allow_pickle=False)
    np.testing.assert_allclose(actual_output, expected_output, rtol=1e-10, atol=1e-10)
    np.testing.assert_array_equal(actual_output.argmax(axis=1), expected_output.argmax(axis=1))
    return {"examples": len(actual_output), "max-absolute-error": float(np.abs(actual_output - expected_output).max()),
            "exact-decisions": True, "parameter-identity": True, "isolated-agent-free-process": True,
            "network-and-repository-blocked": True}
