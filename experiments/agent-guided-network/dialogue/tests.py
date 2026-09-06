"""Preflight checks for generation, OAK/Python parity, data, state and edit permissions."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
import numpy as np
import torch
from graph import (Revision, compile_graph, join_parameters, oak_run, validate_oak_revision,
                   validate_python_revision, write_graph, read_graph)
from runtime import (EOS, MAX_INPUT, MAX_REPLY, Program, Session, encode_inputs, identity,
                     load_model, predict, reply_text, token_ids)
from task import generate
from train import Network, configure, model_record


class DialogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        configure()
        cls.model = model_record(Network(0))
        cls.temp = tempfile.TemporaryDirectory()
        cls.directory = Path(cls.temp.name) / 'baseline'
        write_graph(cls.model, cls.directory)
        cls.program = compile_graph(cls.directory)
        cls.text = 'The ball moved from the hall to the garden. Where is the ball now?'

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_01_eos_truncates_not_template(self) -> None:
        self.assertEqual(reply_text([token_ids('hello')[0], EOS, token_ids('garden')[0]]), 'Hello')

    def test_02_torch_numpy_probabilities(self) -> None:
        with torch.no_grad():
            actual = Network(0)(torch.tensor(encode_inputs([[]], [self.text]))).softmax(-1).numpy()
        expected = predict(self.model, [[]], [self.text])[1]
        np.testing.assert_allclose(actual, expected, atol=2e-6, rtol=2e-5)

    def test_03_parameter_roundtrip(self) -> None:
        self.assertEqual(self.model, join_parameters(self.directory))

    def test_04_native_oak_parity(self) -> None:
        replies, state = oak_run(self.directory, [('interface.chat', {'TEXTS': [self.text]})])
        direct = Session(self.model)
        self.assertEqual(replies[0]['REPLIES'], [direct.answer(self.text)])
        self.assertTrue(state)

    def test_05_lowered_parity(self) -> None:
        actual = Program(self.program).run('interface.chat', {'TEXTS': [self.text]})['REPLIES']
        self.assertEqual(actual, predict(self.model, [[]], [self.text])[0])

    def test_06_session_restore(self) -> None:
        original, restored = Session(self.model), Session(self.model)
        original.answer(self.text)
        restored.restore(json.loads(json.dumps(original.snapshot())))
        self.assertEqual(original.answer('Where was it before?'), restored.answer('Where was it before?'))

    def test_07_lowered_restore(self) -> None:
        original, restored = Program(self.program), Program(self.program)
        original.run('interface.chat', {'TEXTS': [self.text]})
        restored.restore(json.loads(json.dumps(original.snapshot())))
        self.assertEqual(original.run('interface.chat', {'TEXTS': ['Where was it before?']}),
                         restored.run('interface.chat', {'TEXTS': ['Where was it before?']}))

    def test_08_model_bound_restore(self) -> None:
        snapshot = Session(self.model).snapshot()
        snapshot['model'] = 'invalid'
        with self.assertRaises(ValueError):
            Session(self.model).restore(snapshot)

    def test_09_context_overflow(self) -> None:
        with self.assertRaises(ValueError):
            Session(self.model).answer('ball ' * (MAX_INPUT + 1))

    def test_10_failure_preserves_state(self) -> None:
        session = Session(self.model)
        before = session.snapshot()
        with self.assertRaises(ValueError):
            session.answer('')
        self.assertEqual(before, session.snapshot())

    def test_11_unknown_token_explicit(self) -> None:
        self.assertEqual(token_ids('unfamiliar'), [6])

    def test_12_dataset_determinism_disjoint(self) -> None:
        first = generate(3, 64)
        second = generate(3, 64, excluded={row.key for row in first})
        self.assertEqual(first, generate(3, 64))
        self.assertFalse({row.key for row in first} & {row.key for row in second})

    def test_13_scoped_edit_both(self) -> None:
        candidate = copy.deepcopy(self.model)
        candidate['weights']['output_bias'][0] += 0.01
        revision = Revision(identity(self.model), ('readout',))
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / 'candidate'
            write_graph(candidate, directory)
            self.assertEqual(validate_python_revision(self.model, candidate, revision), ['readout'])
            self.assertEqual(validate_oak_revision(self.directory, directory, revision), ['readout'])

    def test_14_forbidden_owner(self) -> None:
        candidate = copy.deepcopy(self.model)
        candidate['weights']['output_bias'][0] += 0.01
        with self.assertRaises(ValueError):
            validate_python_revision(self.model, candidate, Revision(identity(self.model), ('encoder',)))

    def test_15_stale_edit(self) -> None:
        with self.assertRaises(ValueError):
            validate_python_revision(self.model, self.model, Revision('stale', ('encoder',)))

    def test_16_invalid_weights(self) -> None:
        for mutation in ('shape', 'nonfinite', 'vocabulary'):
            candidate = copy.deepcopy(self.model)
            if mutation == 'shape':
                candidate['weights']['key'] = [1]
            elif mutation == 'nonfinite':
                candidate['weights']['key'][0][0] = float('nan')
            else:
                candidate['vocabulary'] = list(reversed(candidate['vocabulary']))
            with self.assertRaises(ValueError):
                load_model(candidate)

    def test_17_shared_generation_calls(self) -> None:
        calls = self.program['source']['call_sites']
        self.assertEqual(sum(call['target'] == 'attention.oak.md#process.attend' for call in calls), 2 * MAX_REPLY)

    def test_18_missing_dependency(self) -> None:
        import shutil
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / 'broken'
            shutil.copytree(self.directory, directory)
            (directory / 'attention.oak.md').unlink()
            with self.assertRaises(ValueError):
                read_graph(directory)

    def test_19_all_four_turns_exist(self) -> None:
        for row in generate(15, 32):
            self.assertEqual(len(row.users), 4)
            self.assertEqual(len(row.answers), 4)
            self.assertIn('it', row.users[1].lower())
            self.assertGreater(len(token_ids(row.answers[0])), 1)

    def test_20_lowered_transaction(self) -> None:
        program = Program(self.program)
        before = program.snapshot()
        with self.assertRaises(ValueError):
            program.run('interface.chat', {'TEXTS': ['']})
        self.assertEqual(before, program.snapshot())


if __name__ == '__main__':
    unittest.main(verbosity=2)
