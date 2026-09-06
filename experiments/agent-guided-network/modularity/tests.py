"""Observable equivalence, graph semantics and module-update boundaries."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.append(str(Path(__file__).resolve().parents[1] / 'meaning'))

import numpy as np
from oak import parse, render
from graph import (Proposal, compile_graph, export_graph, graph_hashes, join_parameters,
                   oak_run, read_graph, validate_revision, write_graph)
from operations import GROUPS, Program, canonical_bytes, decode_parameters, identity, invoke
from runtime import encode_inputs, forward, load_record
from task import generate_cases, render_case

ARCHIVE = ROOT / 'experiments/agent-guided-network/results/meaning-run/reproduced/records.tar.xz'


def baseline() -> dict:
    with tarfile.open(ARCHIVE) as archive:
        return json.load(archive.extractfile('401/agent.json'))


class ModularTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / 'source'
        self.record = baseline()
        write_graph(self.record, self.source)
        self.compiled = compile_graph(self.source)
        self.payload = {'HISTORIES': [['the ball moved from the hall to the garden']],
                        'QUESTIONS': ['where is the ball now']}

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _candidate(self, groups: tuple[str, ...] = ('encoder',)) -> Path:
        record = copy.deepcopy(self.record)
        for group in groups:
            key = GROUPS[group][0]
            record['weights'][key]['scale'] *= .99
        candidate = self.root / 'candidate'
        write_graph(record, candidate)
        return candidate

    def _proposal(self, groups: tuple[str, ...] = ('encoder',)) -> Proposal:
        return Proposal(identity(graph_hashes(self.source)), groups, 'Test one owned update.')

    def test_six_canonical_documents(self) -> None:
        self.assertEqual(len(read_graph(self.source).documents), 6)
        for path in self.source.glob('*.oak.md'):
            node = parse(path.read_text())
            self.assertEqual(render(node), path.read_text())
            markdown = render(node, grouping='markdown')
            self.assertEqual(parse(markdown), node)

    def test_parameters_preserved(self) -> None:
        self.assertEqual(join_parameters(self.source), self.record)

    def test_numerical_equivalence(self) -> None:
        for form in range(4):
            cases = generate_cases(17, 24, regime='medium')
            rendered = [render_case(case, form) for case in cases]
            histories, questions = [x[0] for x in rendered], [x[1] for x in rendered]
            events, query = encode_inputs(histories, questions)
            reference = forward(load_record(self.record), events, query)
            got = Program(self.compiled).run('interface.batch', {'HISTORIES': histories, 'QUESTIONS': questions})
            np.testing.assert_allclose(got['PROBABILITIES'], reference, atol=1e-12, rtol=0)
            np.testing.assert_array_equal(np.argmax(got['PROBABILITIES'], axis=1), reference.argmax(1))

    def test_actual_oak_matches_lowering(self) -> None:
        actual, _ = oak_run(self.source, [('interface.batch', self.payload)])
        compiled = Program(self.compiled).run('interface.batch', self.payload)
        np.testing.assert_allclose(actual[0]['PROBABILITIES'], compiled['PROBABILITIES'], atol=1e-12, rtol=0)

    def test_observation_state_round_trip(self) -> None:
        program = Program(self.compiled)
        for text in self.payload['HISTORIES'][0]:
            program.run('interface.observe', {'TEXT': text})
            saved = json.loads(canonical_bytes(program.snapshot()))
            program = Program(self.compiled)
            program.restore(saved)
        answer = program.run('interface.answer', {'QUESTIONS': self.payload['QUESTIONS']})
        self.assertEqual(answer['REPLIES'], ['garden'])
        emissions, state = oak_run(self.source, [('interface.observe', {'TEXT': self.payload['HISTORIES'][0][0]}),
                                                  ('interface.answer', {'QUESTIONS': self.payload['QUESTIONS']})])
        self.assertEqual(emissions[0]['REPLIES'], answer['REPLIES'])
        self.assertEqual(state, program.snapshot()['state'])
        program.reset()
        self.assertEqual(program.snapshot()['state'], self.compiled['initial_state'])

    def test_failed_update_is_transactional(self) -> None:
        program = Program(self.compiled)
        old = program.snapshot()
        with self.assertRaises(ValueError):
            program.run('interface.observe', {'TEXT': 'unsupported vocabulary'})
        self.assertEqual(program.snapshot(), old)

    def test_model_bound_restore(self) -> None:
        candidate = self._candidate()
        with self.assertRaises(ValueError):
            Program(compile_graph(candidate)).restore(Program(self.compiled).snapshot())

    def test_bad_restore(self) -> None:
        program = Program(self.compiled)
        saved = program.snapshot()
        saved['state']['memory.oak.md#state.history'] = [['unrecognised']]
        with self.assertRaises(ValueError):
            program.restore(saved)

    def test_encoder_reused_by_both_consumers(self) -> None:
        sites = self.compiled['source']['call_sites']
        callers = {site['caller'] for site in sites if site['target'] == 'encoder.oak.md#process.encode'}
        self.assertEqual(callers, {'network.oak.md#process.encode-events', 'network.oak.md#process.encode-question'})
        self.assertEqual(sum('constant.parameters' in name for name in self.compiled['constants']), 3)

    def test_lowering_obeys_changed_wiring(self) -> None:
        path = self.source / 'network.oak.md'
        node = parse(path.read_text())
        predict = next(p for p in node.processes if p.id == 'predict')
        readout = predict.steps[-1]
        readout.inputs[0].value.binding = 'QUERY'
        path.write_text(render(node))
        changed = compile_graph(self.source)
        old = Program(self.compiled).run('interface.batch', self.payload)
        new = Program(changed).run('interface.batch', self.payload)
        self.assertGreater(np.max(np.abs(old['PROBABILITIES'] - new['PROBABILITIES'])), 1e-4)
        actual, _ = oak_run(self.source, [('interface.batch', self.payload)])
        np.testing.assert_allclose(actual[0]['PROBABILITIES'], new['PROBABILITIES'], atol=1e-12, rtol=0)

    def test_missing_dependency(self) -> None:
        (self.source / 'encoder.oak.md').unlink()
        with self.assertRaises(Exception):
            compile_graph(self.source)

    def test_symlink_dependency(self) -> None:
        path = self.source / 'encoder.oak.md'
        moved = self.root / 'external.oak.md'
        path.rename(moved)
        path.symlink_to(moved)
        with self.assertRaises(ValueError):
            compile_graph(self.source)

    def test_unknown_operation(self) -> None:
        path = self.source / 'encoder.oak.md'
        path.write_text(path.read_text().replace('modular.encode.v1', 'unregistered.encode.v1'))
        with self.assertRaises(ValueError):
            compile_graph(self.source)

    def test_changed_action_instruction(self) -> None:
        path = self.source / 'encoder.oak.md'
        path.write_text(path.read_text().replace('registered numerical contract', 'different numerical contract'))
        with self.assertRaises(ValueError):
            compile_graph(self.source)

    def test_extra_schema_semantics(self) -> None:
        path = self.source / 'contracts.oak.md'
        node = parse(path.read_text())
        node.schemas[0].purpose = 'Changed contract meaning.'
        path.write_text(render(node))
        with self.assertRaises(ValueError):
            compile_graph(self.source)

    def test_bad_tensor(self) -> None:
        record = copy.deepcopy(self.record['weights'])
        params = {name: record[name] for name in GROUPS['encoder']}
        params['embedding']['values'] = [[1]]
        with self.assertRaises(ValueError):
            decode_parameters([params], 'encoder')

    def test_empty_mask(self) -> None:
        params = [{name: self.record['weights'][name] for name in GROUPS['attention']}]
        with self.assertRaises(ValueError):
            invoke('modular.attend.v1', {'MEMORY': np.zeros((1, 1, 24)), 'QUERY': np.zeros((1, 24)),
                                        'MASK': [[0]], 'PARAMETERS': params})

    def test_scoped_revision(self) -> None:
        audit = validate_revision(self.source, self._candidate(), self._proposal())
        self.assertEqual(audit['changed'], ['encoder.oak.md'])
        self.assertEqual(len(audit['unchanged']), 5)

    def test_cross_module_write(self) -> None:
        with self.assertRaises(ValueError):
            validate_revision(self.source, self._candidate(('encoder', 'readout')), self._proposal())

    def test_nonparameter_write(self) -> None:
        candidate = self._candidate()
        path = candidate / 'encoder.oak.md'
        node = parse(path.read_text())
        node.constants[1].value = 'An altered responsibility.'
        path.write_text(render(node))
        with self.assertRaises(ValueError):
            validate_revision(self.source, candidate, self._proposal())

    def test_stale_revision(self) -> None:
        with self.assertRaises(ValueError):
            validate_revision(self.source, self._candidate(), Proposal('stale', ('encoder',), 'Test.'))

    def test_export_is_graph_derived(self) -> None:
        destination = self.root / 'export'
        export_graph(self.source, destination)
        record = json.loads((destination / 'program.json').read_text())
        self.assertEqual(record['digest'], self.compiled['digest'])
        self.assertEqual(Program(record).run('interface.batch', self.payload)['REPLIES'], ['garden'])
        self.assertEqual((destination / 'inference.py').read_bytes(), Path(__file__).with_name('operations.py').read_bytes())


if __name__ == '__main__':
    unittest.main()
