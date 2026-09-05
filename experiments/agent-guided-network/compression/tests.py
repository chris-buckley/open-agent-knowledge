"""Observed contract checks; all numerical test cases use the separate pilot seed."""
from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from oak import parse, render

from attention.author import load as load_teacher
from attention.numeric import forward as teacher_forward
from compression import session
from compression.export import export_snapshot, storage, verify_export
from compression.fit import fold_weights, gradients, loss, project_kernels
from compression.numeric import (Encoding, Kernel, expand_kernel, forward, kernel_record, make_kernel, place_gains,
                                 read_kernel, read_kernels, validate_inputs)
from compression.oak_io import documents, load_snapshot, oak_forward, snapshot_hash, write_snapshot
from compression.task import REGIMES, case_hash, nearest_key, sample_cases


class CompressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.weights, _ = load_teacher(session.TEACHER)
        cls.folded = fold_weights(cls.weights)
        cls.cases = sample_cases(0, "train", "crowded")
        cls.inputs = {name: tensor[:3] for name, tensor in cls.cases.inputs.items()}

    def test_exact_folding(self) -> None:
        for regime in REGIMES:
            inputs = sample_cases(0, "dev", regime).inputs
            expected = teacher_forward(self.weights, inputs)
            actual = forward(self.folded, inputs)
            np.testing.assert_allclose(actual, expected, atol=1e-10, rtol=1e-10)
            np.testing.assert_array_equal(actual.argmax(axis=1), expected.argmax(axis=1))

    def test_general_input_folding(self) -> None:
        inputs = {name: tensor.copy() for name, tensor in self.inputs.items()}
        inputs["QUERY"] *= 0.7
        inputs["VALUE1"] *= -0.3
        inputs["VALUE2"] *= 1.7
        np.testing.assert_allclose(forward(self.folded, inputs), teacher_forward(self.weights, inputs), atol=1e-10)

    def test_parameter_counts(self) -> None:
        self.assertEqual(storage(self.folded)["stored-coefficients"], 144)
        self.assertEqual(storage(project_kernels(self.folded, Encoding.DIAGONAL))["stored-coefficients"], 20)
        tied = storage(place_gains((1.0, 1.0, 1.0)))
        self.assertEqual((tied["stored-coefficients"], tied["expanded-nonzeros"]), (3, 20))
        sparse = storage(project_kernels(self.folded, Encoding.SPARSE, fraction=0.25))
        self.assertEqual((sparse["stored-coefficients"], sparse["sparse-indices"]), (36, 36))

    def test_encodings_roundtrip(self) -> None:
        matrix = np.arange(64, dtype=float).reshape(8, 8)
        for encoding in Encoding:
            kernel = make_kernel(matrix, encoding, fraction=0.25)
            self.assertEqual(read_kernel(kernel_record(kernel)), kernel)
            self.assertEqual(expand_kernel(kernel).shape, (8, 8))

    def test_invalid_encodings(self) -> None:
        valid = kernel_record(place_gains((1.0, 1.0, 1.0))[0])
        for patch_values in ({"encoding": "eval"}, {"dimension": True}, {"dimension": 7},
                             {"coefficients": [float("nan")]}, {"coefficients": [True]},
                             {"coefficients": [1]}, {"coefficients": [9000.0]},
                             {"indices": [0]}, {"coefficients": []}):
            with self.subTest(patch=patch_values), self.assertRaises((ValueError, TypeError)):
                read_kernel(valid | patch_values)
        with self.assertRaises(ValueError):
            Kernel(Encoding.SPARSE, 4, (1.0, 2.0), (1, 1))
        with self.assertRaises(ValueError):
            read_kernels([valid])

    def test_inputs_reject_boolean(self) -> None:
        inputs = {name: tensor.tolist() for name, tensor in self.inputs.items()}
        inputs["QUERY"][0][0] = True
        with self.assertRaises(ValueError):
            validate_inputs(inputs)

    def test_inputs_reject_mask_or_shape(self) -> None:
        for name, tensor in (("MASK1", np.zeros_like(self.inputs["MASK1"])), ("KEY1", np.ones((3, 2, 7))),
                             ("QUERY", np.full((3, 8), np.nan)), ("MASK2", np.full_like(self.inputs["MASK2"], 0.5))):
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_inputs(self.inputs | {name: tensor})

    def test_no_hidden_labels(self) -> None:
        with self.assertRaises(ValueError):
            forward(self.folded, self.inputs | {"labels": self.cases.labels[:3]})

    def test_masked_entries_have_no_effect(self) -> None:
        inputs = {name: tensor.copy() for name, tensor in self.inputs.items()}
        inputs["MASK1"][:, -1] = 0
        expected = forward(self.folded, inputs)
        inputs["KEY1"][:, -1] = 3.5
        inputs["VALUE1"][:, -1] = -3.5
        np.testing.assert_array_equal(forward(self.folded, inputs), expected)

    def test_permutation_invariance(self) -> None:
        inputs = {name: tensor.copy() for name, tensor in self.inputs.items()}
        for name in ("KEY1", "VALUE1", "MASK1", "KEY2", "VALUE2", "MASK2"):
            inputs[name] = inputs[name][:, ::-1]
        np.testing.assert_allclose(forward(self.folded, inputs), forward(self.folded, self.inputs), atol=1e-12)

    def test_inference_does_not_mutate(self) -> None:
        snapshot = {name: tensor.copy() for name, tensor in self.inputs.items()}
        forward(self.folded, self.inputs)
        for name, tensor in snapshot.items():
            np.testing.assert_array_equal(tensor, self.inputs[name])

    def test_all_167_gradient_entries(self) -> None:
        rng = np.random.default_rng(0)
        dense = tuple(make_kernel(rng.normal(0, 0.3, (dimension, dimension)), Encoding.DENSE) for dimension in (8, 8, 4))
        families = (dense, project_kernels(dense, Encoding.DIAGONAL), place_gains((2.0, 3.0, 4.0)))
        for kernels in families:
            actual = gradients(kernels, self.inputs, self.cases.labels[:3])
            for block, kernel in enumerate(kernels):
                for index, expected in enumerate(actual[block]):
                    values = np.array(kernel.coefficients)
                    values[index] += 1e-5
                    plus = list(kernels)
                    plus[block] = replace(kernel, coefficients=tuple(float(v) for v in values))
                    values[index] -= 2e-5
                    minus = list(kernels)
                    minus[block] = replace(kernel, coefficients=tuple(float(v) for v in values))
                    estimate = (loss(tuple(plus), self.inputs, self.cases.labels[:3]) - loss(tuple(minus), self.inputs, self.cases.labels[:3])) / 2e-5
                    self.assertAlmostEqual(float(expected), estimate, places=6)

    def test_oak_roundtrip(self) -> None:
        for encoding in Encoding:
            kernels = project_kernels(self.folded, encoding, fraction=0.25)
            for node in documents(kernels).values():
                for grouping in ("xml", "markdown"):
                    text = render(node, grouping=grouping)
                    self.assertEqual(render(parse(text, grouping=grouping), grouping=grouping), text)

    def test_oak_executor_parity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "snapshot"
            kernels = place_gains((32.0, 32.0, 8.0))
            write_snapshot(kernels, directory)
            self.assertEqual(load_snapshot(directory), kernels)
            np.testing.assert_allclose(oak_forward(directory, self.inputs), forward(kernels, self.inputs), atol=1e-12)

    def test_unsupported_oak_tool(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "snapshot"
            write_snapshot(self.folded, directory)
            path = directory / "attention.oak.md"
            path.write_text(path.read_text().replace("tensor.compact.first.v1", "agent.hidden.v1"))
            with self.assertRaises(ValueError):
                load_snapshot(directory)

    def test_symlink_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "snapshot"
            write_snapshot(self.folded, directory)
            alias = Path(temporary) / "alias"
            alias.symlink_to(directory, target_is_directory=True)
            with self.assertRaises(ValueError):
                snapshot_hash(alias)

    def test_export_integrity_and_isolation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source, artifact = Path(temporary) / "source", Path(temporary) / "export"
            kernels = place_gains((32.0, 128.0, 8.0))
            write_snapshot(kernels, source)
            sizes = export_snapshot(source, artifact)
            report = verify_export(artifact, kernels, self.inputs)
            self.assertEqual(report["max-absolute-error"], 0)
            self.assertEqual(sizes["export-bytes"], sum(path.stat().st_size for path in artifact.iterdir()))
            (artifact / "model.json").write_text("{}")
            with self.assertRaises(ValueError):
                verify_export(artifact, kernels, self.inputs)

    def test_capability_floor(self) -> None:
        teacher = {"short": {"accuracy": 0.9, "cross-entropy": 0.2}}
        self.assertTrue(session.capability_floor(teacher, teacher))
        self.assertFalse(session.capability_floor({"short": {"accuracy": 0.85, "cross-entropy": 0.1}}, teacher))

    def test_task_control_and_disjoint_hashes(self) -> None:
        hashes = []
        for split in ("train", "dev"):
            for regime in REGIMES:
                cases = sample_cases(0, split, regime)
                np.testing.assert_array_equal(nearest_key(cases), cases.labels)
                hashes.append(case_hash(cases))
        self.assertEqual(len(hashes), len(set(hashes)))

    def test_stale_proposal_and_closed_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "run"
            session.start(directory)
            root = directory / "0"
            write_snapshot(self.folded, root / "snapshots" / "folded-144")
            (root / "CURRENT").write_text("folded-144")
            session.observe(directory, 0)
            session.propose(directory, 0, "identity", (32.0, 32.0, 8.0), "Unit test, not a live study decision.")
            write_snapshot(place_gains((1.0, 1.0, 1.0)), root / "snapshots" / "changed")
            (root / "CURRENT").write_text("changed")
            with self.assertRaisesRegex(ValueError, "stale proposal"):
                session.apply(directory, 0, 1)
            self.assertEqual((root / "CURRENT").read_text(), "changed")
            (directory / "SELECTION_CLOSED").write_text("closed")
            with self.assertRaisesRegex(ValueError, "selection is closed"):
                session.observe(directory, 0)

    def test_frozen_source_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "run"
            session.start(directory)
            with patch("compression.session.source_hashes", return_value={}):
                with self.assertRaisesRegex(ValueError, "frozen source changed"):
                    session.require_frozen(directory)

    def test_complete_pilot_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, patch.object(session, "SEEDS", (0,)):
            directory = Path(temporary) / "pilot"
            session.start(directory)
            session.prepare(directory, 0)
            session.propose(directory, 0, "identity", (32.0, 32.0, 8.0), "Implementation-only pilot, not a scored agent trial.", replay=True)
            session.apply(directory, 0, 1)
            session.close(directory)
            report = session.finish(directory)
            self.assertEqual(report["fresh-agent-decisions"], 0)
            self.assertEqual(set(report["results"]["0"]["regimes"]), set(REGIMES))
            with self.assertRaisesRegex(ValueError, "selection is closed"):
                session.propose(directory, 0, "identity", (64.0, 64.0, 8.0), "Must fail.")
