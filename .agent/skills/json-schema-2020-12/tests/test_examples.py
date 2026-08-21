from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing.exceptions import Unresolvable

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
PYDANTIC_EXAMPLE = ROOT / "examples" / "pydantic" / "model.py"
sys.path.insert(0, str(SCRIPTS))

from _common import (  # noqa: E402
    ToolError,
    build_registry,
    check_schema,
    format_checker_for_policy,
    load_json,
    load_registry_manifest,
    require_draft_2020_12,
)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PYDANTIC_MODEL = load_module(PYDANTIC_EXAMPLE, "skill_pydantic_example")
REGISTRY_PATH = ROOT / "examples" / "registry.json"
PYTHON = sys.executable


def run_cli(*parts: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PYTHON, *(str(part) for part in parts)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )


class SkillExamplesTest(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.schemas = {
            path.relative_to(ROOT).as_posix(): require_draft_2020_12(load_json(path), path)
            for path in sorted((ROOT / "examples").rglob("*.schema.json"))
        }
        extension_path = ROOT / "examples/extension/schema/retail-lending.schema.json"
        cls.registry, _ = build_registry(
            root_schema=cls.schemas["examples/extension/schema/retail-lending.schema.json"],
            root_path=extension_path,
            registry_manifest=REGISTRY_PATH,
        )

    def assertExit(self, expected: int, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(
            expected,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )

    def errors_for(self, schema_name: str, instance_name: str):
        schema = self.schemas[schema_name]
        instance = load_json(ROOT / instance_name)
        validator = Draft202012Validator(
            schema,
            registry=self.registry,
            format_checker=FormatChecker(),
        )
        return list(validator.iter_errors(instance))

    def test_all_standalone_example_schemas_are_meta_valid(self) -> None:
        self.assertGreaterEqual(len(self.schemas), 7)
        for name, schema in self.schemas.items():
            with self.subTest(schema=name):
                check_schema(schema, ROOT / name)

    def test_reference_registry_resolves_without_network(self) -> None:
        result = run_cli(
            "scripts/check_references.py",
            "examples/extension/schema/retail-lending.schema.json",
            "--registry",
            REGISTRY_PATH,
        )
        self.assertExit(0, result)
        self.assertIn("0 unresolved", result.stdout)

    def test_missing_registry_resource_is_a_hard_failure(self) -> None:
        schema = self.schemas["examples/extension/schema/retail-lending.schema.json"]
        instance = load_json(ROOT / "examples/extension/retail-lending.valid.json")
        validator = Draft202012Validator(schema)
        with self.assertRaises(Exception) as caught:
            list(validator.iter_errors(instance))
        chain = []
        current: BaseException | None = caught.exception
        while current is not None:
            chain.append(current)
            current = current.__cause__ or current.__context__
        self.assertTrue(any(isinstance(item, Unresolvable) for item in chain))

    def test_base_and_domain_instances_validate(self) -> None:
        cases = [
            (
                "examples/system/schema/system.schema.json",
                "examples/system/base-system.valid.json",
            ),
            (
                "examples/extension/schema/retail-lending.schema.json",
                "examples/extension/retail-lending.valid.json",
            ),
            (
                "examples/pydantic/generated.schema.json",
                "examples/extension/retail-lending.valid.json",
            ),
        ]
        for schema, instance in cases:
            with self.subTest(schema=schema):
                self.assertEqual([], self.errors_for(schema, instance))

    def test_valid_base_instance_also_satisfies_closed_profile(self) -> None:
        self.assertEqual(
            [],
            self.errors_for(
                "examples/system/schema/system-closed.schema.json",
                "examples/system/base-system.valid.json",
            ),
        )

    def test_domain_instance_satisfies_the_parent_contract(self) -> None:
        self.assertEqual(
            [],
            self.errors_for(
                "examples/system/schema/system.schema.json",
                "examples/extension/retail-lending.valid.json",
            ),
        )

    def test_leaf_contract_rejects_unevaluated_property(self) -> None:
        errors = self.errors_for(
            "examples/extension/schema/retail-lending.schema.json",
            "examples/invalid/retail-lending.invalid.json",
        )
        self.assertEqual(1, len(errors))
        self.assertEqual("unevaluatedProperties", errors[0].validator)
        self.assertIn("'debug' was unexpected", errors[0].message)

    def test_closed_base_profile_rejects_extra_property(self) -> None:
        errors = self.errors_for(
            "examples/system/schema/system-closed.schema.json",
            "examples/system/base-system-closed.invalid.json",
        )
        self.assertEqual(1, len(errors))
        self.assertIn("'unexpected' was unexpected", errors[0].message)

    def test_recursive_dynamic_reference_tightens_descendants(self) -> None:
        self.assertEqual(
            [],
            self.errors_for(
                "examples/recursive/strict-tree.schema.json",
                "examples/recursive/strict-tree.valid.json",
            ),
        )
        errors = self.errors_for(
            "examples/recursive/strict-tree.schema.json",
            "examples/recursive/strict-tree.invalid.json",
        )
        messages = [error.message for error in errors]
        nested = [child.message for error in errors for child in error.context]
        self.assertTrue(
            any("'tag' is a required property" in value for value in messages + nested)
        )
        self.assertTrue(any(list(error.absolute_path) == ["children", 0] for error in errors))

    def test_structural_reference_can_name_a_missing_graph_target(self) -> None:
        self.assertEqual(
            [],
            self.errors_for(
                "examples/extension/schema/retail-lending.schema.json",
                "examples/extension/retail-lending.missing-target.json",
            ),
        )
        graph = run_cli(
            "scripts/check_graph_targets.py",
            "examples/extension/retail-lending.missing-target.json",
        )
        self.assertExit(1, graph)
        self.assertIn("target 'node:missing' does not exist", graph.stderr)

    def test_valid_graph_targets_pass_the_application_check(self) -> None:
        result = run_cli(
            "scripts/check_graph_targets.py",
            "examples/extension/retail-lending.valid.json",
        )
        self.assertExit(0, result)

    def test_pydantic_generation_is_deterministic(self) -> None:
        expected = json.loads(
            (ROOT / "examples/pydantic/generated.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(expected, PYDANTIC_MODEL.generated_schema())

    def test_pydantic_type_adapter_generation_is_deterministic(self) -> None:
        expected = json.loads(
            (ROOT / "examples/pydantic/node.generated.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(expected, PYDANTIC_MODEL.generated_node_schema())

    def test_pydantic_runtime_accepts_aliases_and_recursive_nodes(self) -> None:
        raw = load_json(ROOT / "examples/extension/retail-lending.valid.json")
        model = PYDANTIC_MODEL.RetailLendingSystem.model_validate(raw)
        dumped = model.model_dump(mode="json", by_alias=True)
        self.assertEqual("node:home-loan", dumped["nodes"][0]["children"][0]["id"])
        self.assertIn("from", dumped["relationships"][0])
        self.assertNotIn("from_", dumped["relationships"][0])

    def test_invalid_tagged_node_reports_missing_currency(self) -> None:
        result = run_cli(
            "scripts/validate_instance.py",
            "examples/extension/schema/retail-lending.schema.json",
            "examples/invalid/retail-lending-node.invalid.json",
            "--registry",
            REGISTRY_PATH,
            "--json",
        )
        self.assertExit(1, result)
        payload = json.loads(result.stdout)
        self.assertTrue(
            any(
                record["instancePath"] == "/nodes/0/children/0"
                and record["keyword"] == "required"
                and "'currency' is a required property" in record["message"]
                for record in payload["errors"]
            )
        )

    def test_missing_registry_resource_is_a_cli_tool_failure(self) -> None:
        result = run_cli(
            "scripts/validate_instance.py",
            "examples/extension/schema/retail-lending.schema.json",
            "examples/extension/retail-lending.valid.json",
        )
        self.assertExit(2, result)
        self.assertIn("unresolvable schema reference", result.stderr)

    def test_missing_dialect_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "schema.json"
            path.write_text('{"type": "string"}\n', encoding="utf-8")
            with self.assertRaises(ToolError) as caught:
                require_draft_2020_12(load_json(path), path)
        self.assertIn("expected $schema", str(caught.exception))

    def test_unsupported_dialect_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "schema.json"
            path.write_text(
                json.dumps(
                    {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "type": "string",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ToolError) as caught:
                require_draft_2020_12(load_json(path), path)
        self.assertIn("draft-07", str(caught.exception))

    def test_duplicate_json_object_keys_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "schema.json"
            path.write_text(
                '{"$schema":"https://json-schema.org/draft/2020-12/schema",'
                '"type":"string","type":"number"}\n',
                encoding="utf-8",
            )
            with self.assertRaises(ToolError) as caught:
                load_json(path)
        self.assertIn("duplicate JSON object key 'type'", str(caught.exception))

    def test_registry_manifest_cannot_escape_its_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            registry_dir = base / "registry"
            registry_dir.mkdir()
            schema_path = base / "schema.json"
            schema_path.write_text(
                json.dumps(
                    {
                        "$schema": "https://json-schema.org/draft/2020-12/schema",
                        "$id": "https://example.org/schema/escaped",
                        "type": "string",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            manifest = registry_dir / "registry.json"
            manifest.write_text(
                json.dumps(
                    {"https://example.org/schema/escaped": "../schema.json"}
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(ToolError) as caught:
                load_registry_manifest(manifest)
        self.assertIn("escapes the manifest directory", str(caught.exception))

    def test_invalid_anchor_is_rejected_as_core_syntax(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "schema.json"
            path.write_text(
                json.dumps(
                    {
                        "$schema": "https://json-schema.org/draft/2020-12/schema",
                        "$anchor": "bad/anchor",
                        "type": "string",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            schema = require_draft_2020_12(load_json(path), path)
            with self.assertRaises(ToolError) as caught:
                check_schema(schema, path)
        self.assertIn("bad/anchor", str(caught.exception))

    def test_local_fragment_reference_works_without_root_id(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "schema.json"
            path.write_text(
                json.dumps(
                    {
                        "$schema": "https://json-schema.org/draft/2020-12/schema",
                        "$ref": "#/$defs/value",
                        "$defs": {"value": {"type": "string"}},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            result = run_cli("scripts/check_references.py", path)
        self.assertExit(0, result)
        self.assertIn("0 unresolved", result.stdout)

    def test_reference_target_must_be_a_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "schema.json"
            path.write_text(
                json.dumps(
                    {
                        "$schema": "https://json-schema.org/draft/2020-12/schema",
                        "$id": "https://example.org/schema/non-schema-target",
                        "title": "annotation string",
                        "$ref": "#/title",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            result = run_cli("scripts/check_references.py", path)
        self.assertExit(1, result)
        self.assertIn("not a schema", result.stderr)

    def test_format_annotation_and_assertion_policies_differ(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            schema_path = base / "schema.json"
            instance_path = base / "instance.json"
            schema_path.write_text(
                json.dumps(
                    {
                        "$schema": "https://json-schema.org/draft/2020-12/schema",
                        "type": "string",
                        "format": "uri",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            instance_path.write_text(json.dumps("not a uri") + "\n", encoding="utf-8")
            annotation = run_cli(
                "scripts/validate_instance.py",
                schema_path,
                instance_path,
                "--format-policy",
                "annotation",
            )
            assertion = run_cli(
                "scripts/validate_instance.py",
                schema_path,
                instance_path,
                "--format-policy",
                "assert-known",
            )
        self.assertExit(0, annotation)
        self.assertExit(1, assertion)
        self.assertIn("keyword format", assertion.stderr)

    def test_unknown_format_is_reported_under_each_policy(self) -> None:
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://example.org/schema/custom-format-test",
            "type": "string",
            "format": "project-code",
        }
        checker, names = format_checker_for_policy("annotation", schemas=[schema])
        self.assertIsNone(checker)
        self.assertEqual(("project-code",), names)
        with self.assertRaises(ToolError) as caught:
            format_checker_for_policy("assert-known", schemas=[schema])
        self.assertIn("no checker is registered", str(caught.exception))

    def test_invalid_cli_reports_instance_and_schema_paths(self) -> None:
        result = run_cli(
            "scripts/validate_instance.py",
            "examples/extension/schema/retail-lending.schema.json",
            "examples/invalid/retail-lending.invalid.json",
            "--registry",
            REGISTRY_PATH,
        )
        self.assertExit(1, result)
        self.assertIn("instance <root>", result.stderr)
        self.assertIn("schema /unevaluatedProperties", result.stderr)


if __name__ == "__main__":
    unittest.main()
