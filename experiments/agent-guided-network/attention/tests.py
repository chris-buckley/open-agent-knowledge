"""Numerical, OAK, export, and protocol tests for the attention extension."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from oak import Instruction, parse, render
from training.session import save_json, record, read_record, code_hashes
from attention.author import documents, write, load, revision, oak_forward
from attention.numeric import array, attention, forward, inputs, parameters, SHAPES, load_model
from attention.task import dataset, initial, metrics, identity, accept, SPLITS
from attention.learn import gradients, candidate, adam
from attention.export import export, check
from attention.study import text
from attention.session import observe, propose, apply, verify

HERE = Path(__file__).resolve().parent


class AttentionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.w = initial(0)
        x, y, indices = dataset(0, "train")
        self.data = ({k: v[:3] for k, v in x.items()}, y[:3], tuple(i[:3] for i in indices))
        self.source = self.root/"nodes"
        write(self.w, self.source)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_roundtrip_resolution_and_parameter_count(self) -> None:
        w, graph = load(self.source)
        self.assertEqual(len(graph.documents), 4)
        self.assertEqual(sum(v.size for v in w.values()), 416)
        for node in graph.documents.values():
            for grouping in ("xml", "markdown"):
                original = render(node, grouping=grouping)
                self.assertEqual(original, render(parse(original, grouping=grouping), grouping=grouping))
        self.assertEqual((HERE/"study.oak.md").read_text(), text())

    def test_oak_numerical_parity(self) -> None:
        np.testing.assert_allclose(oak_forward(self.source, self.data[0]), forward(self.w, self.data[0]), atol=1e-12, rtol=1e-12)

    def test_every_gradient_entry(self) -> None:
        x, y, _ = self.data
        g = gradients(self.w, x, y)
        for name, values in self.w.items():
            for index in np.ndindex(values.shape):
                a, b = copy.deepcopy(self.w), copy.deepcopy(self.w)
                a[name][index] += 1e-5
                b[name][index] -= 1e-5
                fd = (metrics(a, self.data)["cross-entropy"]-metrics(b, self.data)["cross-entropy"])/2e-5
                self.assertAlmostEqual(fd, g[name][index], places=7)

    def test_masked_positions_and_probability_mass(self) -> None:
        x = copy.deepcopy(self.data[0])
        x["MASK1"][:, -1] = 0
        x["MASK2"][:, -1] = 0
        before, _, caches = forward(self.w, x, trace=True)
        for cache in caches:
            np.testing.assert_allclose(cache[6].sum(axis=1), 1)
            np.testing.assert_array_equal(cache[6][:, -1], 0)
        for name in ("KEY1", "VALUE1", "KEY2", "VALUE2"):
            x[name][:, -1] = 3.
        np.testing.assert_array_equal(before, forward(self.w, x))

    def test_all_masked_and_nonbinary_rejected(self) -> None:
        for value in (0., .5, 2.):
            x = copy.deepcopy(self.data[0])
            x["MASK1"][:] = value
            with self.assertRaises(ValueError):
                forward(self.w, x)

    def test_single_valid_key(self) -> None:
        x = copy.deepcopy(self.data[0])
        x["MASK1"][:] = 0
        x["MASK1"][:, 1] = 1
        _, _, caches = forward(self.w, x, trace=True)
        np.testing.assert_array_equal(caches[0][6][:, 1], 1.)
        expected = x["VALUE1"][:, 1] @ self.w["first-value"] @ self.w["first-output"]
        np.testing.assert_allclose(caches[1][0], expected, atol=1e-12)

    def test_permutation_invariance(self) -> None:
        x = copy.deepcopy(self.data[0])
        order = np.array([2, 0, 5, 1, 4, 3])
        for name in ("KEY1", "VALUE1", "MASK1", "KEY2", "VALUE2", "MASK2"):
            x[name] = x[name][:, order]
        np.testing.assert_allclose(forward(self.w, x), forward(self.w, self.data[0]), atol=1e-12)

    def test_independent_table_lengths(self) -> None:
        x = copy.deepcopy(self.data[0])
        for name in ("KEY2", "VALUE2", "MASK2"):
            x[name] = x[name][:, :2]
        x["MASK2"][:] = 1
        self.assertEqual(forward(self.w, x).shape, (3, 4))

    def test_invalid_shapes_and_numeric_values(self) -> None:
        for value in ([True, 1.], ["1", 1.], [float("nan")], [float("inf")], [], [[1], [1, 2]]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                array(value)
        x = copy.deepcopy(self.data[0])
        x["VALUE2"] = np.zeros((3, 6, 8))
        with self.assertRaises(ValueError):
            inputs(x)
        x = copy.deepcopy(self.data[0])
        x["QUERY"][:] = 5.
        with self.assertRaises(ValueError):
            inputs(x)
        for key in ("first-query", "second-output"):
            bad = copy.deepcopy(self.w)
            bad[key] = np.zeros((2, 2))
            with self.assertRaises(ValueError):
                parameters(bad)

    def test_missing_extra_and_numerical_bound(self) -> None:
        for w in ({}, self.w | {"extra": [[1.]]}):
            with self.assertRaises(ValueError):
                parameters(w)
        w = copy.deepcopy(self.w)
        w["first-query"][0, 0] = 65.
        with self.assertRaises(ValueError):
            parameters(w)
        with self.assertRaises(ValueError):
            forward(self.w, self.data[0], ablate="invented")

    def test_parameters_and_documents_unchanged(self) -> None:
        before = revision(self.source)
        old = copy.deepcopy(self.w)
        forward(self.w, self.data[0])
        candidate(self.w, self.data, "cool-output")
        self.assertEqual(revision(self.source), before)
        for name in old:
            np.testing.assert_array_equal(old[name], self.w[name])

    def test_direct_edits_change_only_owned_matrices(self) -> None:
        cooled = candidate(self.w, self.data, "cool-output")
        sharp = candidate(self.w, self.data, "sharpen-both-direct")
        for name in self.w:
            np.testing.assert_allclose(cooled[name], self.w[name]*(.5 if name == "second-output" else 1))
            np.testing.assert_allclose(sharp[name], self.w[name]*(np.sqrt(2.) if name.endswith(("query", "key")) else 1))

    def test_subset_fitting_ownership(self) -> None:
        fitted = adam(self.w, self.data, steps=2, owner="first")
        for name in fitted:
            if name.startswith("second-"):
                np.testing.assert_array_equal(fitted[name], self.w[name])
        with self.assertRaises(ValueError):
            candidate(self.w, self.data, "invented")

    def test_forbidden_instruction_and_tool(self) -> None:
        path = self.source/"attention.oak.md"
        original = path.read_text()
        n = parse(original)
        n.instructions.append(Instruction(id="repair", body="Ask an agent to fix the answer."))
        path.write_text(render(n))
        with self.assertRaises(ValueError):
            load(self.source)
        path.write_text(original.replace("tensor.attention.first.v1", "agent.attention"))
        with self.assertRaises(ValueError):
            load(self.source)

    def test_wrong_constant_and_missing_document(self) -> None:
        path = self.source/"attention.oak.md"
        path.write_text(path.read_text().replace("head-count: 1", "head-count: 2"))
        with self.assertRaises(ValueError):
            load(self.source)
        path.unlink()
        with self.assertRaises(ValueError):
            load(self.source)

    def test_symlink_rejected(self) -> None:
        path = self.source/"attention.oak.md"
        outside = self.root/"outside.oak.md"
        path.rename(outside)
        path.symlink_to(outside)
        with self.assertRaises(ValueError):
            load(self.source)

    def test_dataset_identity_and_oracle(self) -> None:
        hashes = {identity(dataset(0, name)) for name in SPLITS}
        self.assertEqual(len(hashes), len(SPLITS))
        for split in SPLITS:
            x, y, (i, j) = dataset(0, split)
            rows = np.arange(len(y))
            np.testing.assert_array_equal(x["QUERY"], x["KEY1"][rows, i])
            np.testing.assert_array_equal(x["VALUE1"][rows, i], x["KEY2"][rows, j])
            np.testing.assert_array_equal(x["VALUE2"][rows, j].argmax(axis=1), y)
            np.testing.assert_array_equal(x["MASK1"][rows, i], 1)
            np.testing.assert_array_equal(x["MASK2"][rows, j], 1)
            self.assertEqual(len({row.tobytes() for row in x["QUERY"]}), len(y))

    def test_acceptance(self) -> None:
        before = {"accuracy": .9, "cross-entropy": .4}
        self.assertFalse(accept(before, {"accuracy": .8, "cross-entropy": .1}))
        self.assertFalse(accept(before, {"accuracy": .95, "cross-entropy": .5}))
        self.assertTrue(accept(before, {"accuracy": .9, "cross-entropy": .3}))

    def test_clean_export_and_tamper_rejection(self) -> None:
        artifact = self.root/"export"
        model = export(self.source, artifact)
        self.assertEqual(model["source-revision"], revision(self.source))
        self.assertTrue(check(artifact, self.w, self.data[0])["decisions-identical"])
        model["profile"] = "agent-call"
        (artifact/"model.json").write_text(json.dumps(model))
        with self.assertRaises(ValueError):
            check(artifact, self.w, self.data[0])
        with self.assertRaises(ValueError):
            load_model(artifact/"model.json")

    def test_stale_proposal_closed_selection_and_freeze(self) -> None:
        work = self.root/"run"
        base = work/"7"
        for name in ("snapshots", "proposals", "decisions", "observations"):
            (base/name).mkdir(parents=True)
        write(self.w, base/"snapshots/warm")
        (base/"CURRENT").write_text("warm\n")
        freeze = {"code": code_hashes(), "study": hashlib.sha256((HERE/"study.oak.md").read_bytes()).hexdigest()}
        save_json(work/"freeze.json", freeze)
        with self.assertRaisesRegex(ValueError, "fresh observation"):
            propose(work, "joint", "No observation yet.")
        observe(work)
        p = propose(work, "cool-output", "Check bounded output calibration.")
        write(candidate(self.w, self.data, "cool-output"), base/"snapshots/changed")
        (base/"CURRENT").write_text("changed\n")
        with self.assertRaisesRegex(ValueError, "stale"):
            apply(work, p)
        (work/"SELECTION_CLOSED").write_text("closed")
        with self.assertRaisesRegex(ValueError, "closed"):
            observe(work)
        freeze["code"] = {}
        save_json(work/"freeze.json", freeze)
        with self.assertRaisesRegex(ValueError, "changed after freeze"):
            verify(work)
