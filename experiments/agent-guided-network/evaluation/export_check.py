"""Check a generated artifact in a fresh process, without OAK or training access."""
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
from runtime.numeric import forward, load_model


def check_artifact(artifact: Path, w: dict, x: np.ndarray):
    manifest=json.loads((artifact/"SHA256SUMS.json").read_text())
    if set(manifest)!={"model.json","inference.py"}:
        raise ValueError("incomplete export manifest")
    for name,digest in manifest.items():
        if hashlib.sha256((artifact/name).read_bytes()).hexdigest()!=digest:
            raise ValueError("export hash mismatch")
    model=load_model(artifact/"model.json")
    for key in w:
        if not np.array_equal(w[key],model["weights"][key]):
            raise ValueError("exported parameters differ from source")
    boundary=np.stack([np.zeros((4,4,3)),np.ones((4,4,3)),np.full((4,4,3),.5)])
    cases=np.concatenate([x,boundary])
    reference=forward(w,cases)
    with tempfile.TemporaryDirectory(prefix="oak-agent-free-") as temporary:
        dest=Path(temporary)
        for name in manifest:
            shutil.copyfile(artifact/name,dest/name)
        np.save(dest/"input.npy",cases)
        # A clean cwd, isolated Python, stripped environment, and an audit hook
        # prevent use of OAK documents, repository code, and network connections.
        harness='''import sys, runpy, os
repo = sys.argv[1]
def audit(event, args):
    if event.startswith("socket."):
        raise RuntimeError("network forbidden")
    if event == "open" and isinstance(args[0], (str, bytes)):
        p = os.path.realpath(os.fsdecode(args[0]))
        if p.startswith(repo + os.sep) or p.endswith(".oak.md"):
            raise RuntimeError("repository and OAK access forbidden")
sys.addaudithook(audit)
sys.argv = ["inference.py", "model.json", "input.npy", "output.npy"]
runpy.run_path("inference.py", run_name="__main__")
assert not any(k == "oak" or k.startswith("oak.") or k.startswith("training") for k in sys.modules)
'''
        repo=Path(__file__).resolve().parents[3]
        p=subprocess.run([sys.executable,"-I","-c",harness,str(repo)],cwd=dest,
                         env={"PATH":os.environ.get("PATH",""),"HOME":str(dest),"OPENBLAS_NUM_THREADS":"1"},
                         capture_output=True,text=True,timeout=30)
        if p.returncode:
            raise RuntimeError(p.stderr)
        actual=np.load(dest/"output.npy",allow_pickle=False)
    if not np.allclose(reference,actual,rtol=1e-12,atol=1e-12):
        raise ValueError("export numerical mismatch")
    if not np.array_equal(reference>=.5,actual>=.5):
        raise ValueError("export decision mismatch")
    return {"max_absolute_error":float(np.max(np.abs(reference-actual))),"decision_equivalence":True,
            "worlds":len(cases),"clean_process_exit":p.returncode,"network_and_repository_access_blocked":True,
            "parameter_identity":True}
