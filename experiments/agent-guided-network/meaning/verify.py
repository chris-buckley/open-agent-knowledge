"""Independent batch, canonical OAK, restored-state and isolated-process checks."""
from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np
import torch

from runtime import ROOMS, Session, canonical_bytes, encode_inputs, forward, load_record
from task import Case, render_case
from train import encode_cases, restore_network
from oak_io import export_node, oak_dialogue, write_node

_DRIVER = '''import sys, json, builtins
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from inference import Session, encode_inputs, load_record, forward
root = sys.argv[1]
def audit(event, args):
    if event.startswith('socket.'):
        raise RuntimeError('network forbidden')
    if event == 'open' and isinstance(args[0], str) and args[0].startswith(root):
        raise RuntimeError('repository access forbidden')
sys.addaudithook(audit)
original_import = builtins.__import__
def guarded(name, *args, **kwargs):
    if name.split('.')[0] in ('oak', 'torch', 'task', 'train', 'transformers'):
        raise RuntimeError('non-deployment import forbidden')
    return original_import(name, *args, **kwargs)
builtins.__import__ = guarded
record = json.loads(Path('model.json').read_text())
requests = json.loads(Path('requests.json').read_text())
answers = []
for request in requests:
    session = Session(record)
    for text in request['events']:
        session.observe(text)
        saved = json.loads(json.dumps(session.snapshot()))
        session = Session(record)
        session.restore(saved)
    first = session.answer(request['question'])
    session.restore(json.loads(json.dumps(session.snapshot())))
    assert first == session.answer(request['question'])
    answers.append(first)
    session.reset()
    assert session.snapshot()['events'] == []
print(json.dumps(answers))
'''


def verify_model(record: dict, cases: list[Case], directory: Path, *, form: int = 0) -> dict:
    directory.mkdir(parents=True, exist_ok=False)
    node_file = directory / 'network.oak.md'
    write_node(record, node_file)
    export = export_node(node_file, directory / 'export')
    events, questions, _ = encode_cases(cases, form)
    with torch.no_grad():
        reference = torch.softmax(restore_network(record).eval()(events, questions)[0], dim=-1).numpy()
    deployed = forward(load_record(record), events.numpy(), questions.numpy())
    error = float(np.max(np.abs(reference - deployed)))
    if error > 1e-10 or not np.array_equal(reference.argmax(-1), deployed.argmax(-1)):
        raise AssertionError('training/deployment numerical mismatch')
    requests = []
    expected = []
    for case, probability in zip(cases, deployed, strict=True):
        history, question = render_case(case, form)
        requests.append({'events': history, 'question': question})
        expected.append(ROOMS[int(probability.argmax())])
    for request, answer in zip(requests[:8], expected[:8], strict=True):
        if oak_dialogue(node_file, request['events'], [request['question']])[0] != answer:
            raise AssertionError('OAK reply mismatch')
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        for name in ('inference.py', 'model.json'):
            (work / name).write_bytes((directory / 'export' / name).read_bytes())
        (work / 'driver.py').write_text(_DRIVER)
        (work / 'requests.json').write_bytes(canonical_bytes(requests))
        result = subprocess.run([sys.executable, '-I', str(work / 'driver.py'), str(Path(__file__).resolve().parents[3])],
            cwd=work, env={'PATH': os.environ.get('PATH', ''), 'OPENBLAS_NUM_THREADS': '1'},
            capture_output=True, text=True, check=True, timeout=40)
        if json.loads(result.stdout) != expected:
            raise AssertionError('isolated restored-state reply mismatch')
    return {'cases': len(cases), 'torch_numpy_max_error': error, 'same_decisions': True,
            'oak_serialised_state_cases': min(8, len(cases)), 'isolated_restored_state_cases': len(cases), 'export': export}
