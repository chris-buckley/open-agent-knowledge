"""Observable profile tests, including evidence rejection and state equivalence."""
from __future__ import annotations

from collections import Counter
from dataclasses import replace
import copy
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
from oak import parse, render
from runtime import MAX_EVENTS, Session, encode_inputs, encode_words, load_record, model_record, forward
from task import Case, generate_cases, direction_pairs, order_pairs, render_case
from train import Network, configure, record_network
from oak_io import document, read_node, write_node
from verify import verify_model


class ProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        configure()
        cls.record = record_network(Network(0))

    def test_raw_case_direction(self) -> None:
        for a, b in direction_pairs(0, 64):
            self.assertNotEqual(a.answer, b.answer)
            ha, qa = render_case(a, 0)
            hb, qb = render_case(b, 0)
            self.assertEqual(Counter(' '.join(ha + [qa]).split()), Counter(' '.join(hb + [qb]).split()))

    def test_event_order_changes_answer(self) -> None:
        for a, b in order_pairs(0, 64):
            self.assertNotEqual(a.answer, b.answer)
            self.assertEqual(sorted(a.events), sorted(b.events))

    def test_same_history_paraphrases(self) -> None:
        for case in generate_cases(0, 32):
            self.assertNotEqual(render_case(case, 0)[0], render_case(case, 3)[0])
            self.assertEqual(case.answer, replace(case).answer)

    def test_disjoint_history_splits(self) -> None:
        training = generate_cases(0, 128)
        seen = {c.history_identity for c in training}
        development = generate_cases(1, 128, excluded=seen)
        self.assertFalse(seen & {c.history_identity for c in development})
        for pair in direction_pairs(2, 64, excluded=seen):
            self.assertFalse(seen & {c.history_identity for c in pair})

    def test_held_combinations_absent_from_training(self) -> None:
        for case in generate_cases(0, 256):
            self.assertTrue(all(obj != source and obj != dest for obj, source, dest in case.events))
        for case in generate_cases(1, 64, regime='combination'):
            latest = next(e for e in reversed(case.events) if e[0] == case.subject)
            self.assertEqual(latest[2], case.subject)

    def test_roundtrip_weights(self) -> None:
        weights = load_record(self.record)
        self.assertEqual(set(weights), set(load_record(json.loads(json.dumps(self.record)))))
        self.assertTrue(all(not matrix.flags.writeable for matrix in weights.values()))

    def test_bad_parameters(self) -> None:
        for change in ('nan', 'shape', 'boolean', 'extra'):
            record = copy.deepcopy(self.record)
            if change == 'nan': record['weights']['age']['scale'] = float('nan')
            if change == 'shape': record['weights']['age']['values'] = [0, 1]
            if change == 'boolean': record['weights']['age']['values'] = [True]
            if change == 'extra': record['weights']['unknown'] = record['weights']['age']
            with self.subTest(change=change), self.assertRaises(ValueError): load_record(record)

    def test_unknown_tokens(self) -> None:
        with self.assertRaises(ValueError): encode_words('a previously unseen word')
        with self.assertRaises(ValueError): encode_words('')

    def test_state_restore_and_reset(self) -> None:
        history, question = render_case(generate_cases(0, 1)[0], 0)
        first, second = Session(self.record), Session(self.record)
        for text in history:
            first.observe(text)
            second.observe(text)
            fresh = Session(self.record)
            fresh.restore(json.loads(json.dumps(second.snapshot())))
            second = fresh
        self.assertEqual(first.answer(question), second.answer(question))
        snapshot = first.snapshot()
        first.answer(question)
        self.assertEqual(first.snapshot(), snapshot)
        first.reset()
        self.assertEqual(first.snapshot()['events'], [])

    def test_changed_state_rejected_atomically(self) -> None:
        session = Session(self.record)
        session.observe('the ball moved from the hall to the garden')
        old = session.snapshot()
        bad = copy.deepcopy(old)
        bad['events'].append('unknownword')
        with self.assertRaises(ValueError): session.restore(bad)
        self.assertEqual(session.snapshot(), old)
        bad = copy.deepcopy(old); bad['revision'] = 'different'
        with self.assertRaises(ValueError): session.restore(bad)

    def test_capacity(self) -> None:
        session = Session(self.record)
        for _ in range(MAX_EVENTS): session.observe('the ball moved from the hall to the garden')
        old = session.snapshot()
        with self.assertRaises(ValueError): session.observe('the cup moved to the hall')
        self.assertEqual(session.snapshot(), old)
        with self.assertRaises(ValueError): session.answer('where is the cat now')

    def test_empty_history(self) -> None:
        with self.assertRaises(ValueError): Session(self.record).answer('where is the ball now')

    def test_canonical_oak(self) -> None:
        node = document(self.record)
        for grouping in ('xml', 'markdown'):
            text = render(node, grouping=grouping)
            self.assertEqual(parse(text), node)
            self.assertEqual(render(parse(text), grouping=grouping), text)

    def test_forbidden_profile_and_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'network.oak.md'; write_node(self.record, path)
            path.write_text(path.read_text().replace('meaning.answer.v1', 'external.agent.v1'))
            with self.assertRaises(ValueError): read_node(path)
            link = path.with_name('link.oak.md'); link.symlink_to(path)
            with self.assertRaises(ValueError): read_node(link)

    def test_padding_and_batch_invariance(self) -> None:
        cases = generate_cases(0, 2)
        histories, questions = zip(*(render_case(case, 0) for case in cases))
        x, q = encode_inputs(list(histories), list(questions))
        weights = load_record(self.record)
        batched = forward(weights, x, q)
        for i in range(2):
            a, b = encode_inputs([histories[i]], [questions[i]])
            np.testing.assert_allclose(batched[i], forward(weights, a, b)[0], atol=1e-12)

    def test_isolated_export_and_oak_parity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = verify_model(self.record, generate_cases(0, 8), Path(temporary) / 'verification')
            self.assertEqual(result['cases'], 8)
            self.assertTrue(result['same_decisions'])

    def test_freeze_rejection(self) -> None:
        from run import initialise, verify_freeze, write, propose
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / 'run'; initialise(directory)
            freeze = verify_freeze(directory)
            freeze['settings']['steps'] += 1
            (directory / 'freeze.json').write_text(json.dumps(freeze))
            with self.assertRaises(ValueError): verify_freeze(directory)

    def test_closed_selection_rejection(self) -> None:
        from run import initialise, propose, write
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / 'run'; initialise(directory)
            write(directory / 'SELECTION_CLOSED.json', {})
            with self.assertRaises(ValueError): propose(directory, 401, 'longer', 'test')
