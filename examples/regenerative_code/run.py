"""Check the saved regenerative-code example without calling a model."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
import json
import os
import random
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import ModuleType
from typing import Any

_REPOSITORY = Path(__file__).resolve().parents[2]
if (_REPOSITORY / "oak").is_dir() and str(_REPOSITORY) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY))

from lark import Lark, UnexpectedInput
from oak import Act, ActHandler, Arrival, ExecutionError, ExecutionResult, Node, execute, parse, render, resolve


ROOT = Path(__file__).resolve().parent
_ARTIFACT_IDS = (
    "original-source",
    "encoded-recipe",
    "decoded-a",
    "decoded-b",
    "failed-decoded-a",
    "failed-decoded-b",
    "invalid-recipe",
    "encoder-refusal",
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _constant(node: Node, identifier: str) -> Any:
    for item in node.constants:
        if item.id == identifier:
            return item.value
    raise RuntimeError(f"missing OAK constant {identifier!r}")


def _load_fixtures() -> tuple[Node, Node, dict[str, Any]]:
    example_text = (ROOT / "example.oak.md").read_text(encoding="utf-8")
    specimens_text = (ROOT / "specimens.oak.md").read_text(encoding="utf-8")
    example = parse(example_text)
    specimens = parse(specimens_text)
    return example, specimens, {item.id: item.value for item in specimens.constants}


def _check_hashes(example_text: str, values: dict[str, Any]) -> None:
    hashes = values["artifact-sha256"]
    _require(isinstance(hashes, dict), "artifact-sha256 must be a mapping")
    _require(set(_ARTIFACT_IDS).issubset(hashes), "artifact hashes omit a saved fixture")
    _require("system-prompt" in hashes, "artifact hashes omit the system prompt")
    for identifier, expected in hashes.items():
        if identifier == "system-prompt":
            actual = hashlib.sha256(example_text.encode("utf-8")).hexdigest()
        else:
            _require(identifier in values, f"hash names missing artifact {identifier!r}")
            artifact = values[identifier]
            _require(isinstance(artifact, str), f"artifact {identifier!r} must be text")
            actual = hashlib.sha256(artifact.encode("utf-8")).hexdigest()
        _require(actual == expected, f"SHA-256 mismatch for {identifier}")

    earlier_prompt = example_text
    for change in reversed(values["prompt-clarifications"]):
        before, after = change["before"], change["after"]
        _require(earlier_prompt.count(after) == 1, "prompt clarification cannot be reversed exactly")
        earlier_prompt = earlier_prompt.replace(after, before, 1)
    _require(
        hashlib.sha256(earlier_prompt.encode("utf-8")).hexdigest() == values["initial-system-sha256"],
        "reconstructed initial system prompt hash differs",
    )


def _check_oak(example_text: str, example: Node, values: dict[str, Any]) -> None:
    for grouping in ("xml", "markdown"):
        text = render(example, grouping=grouping)
        parsed = parse(text, grouping=grouping)
        resolve(parsed)
        _require(render(parsed, grouping=grouping) == text, f"OAK {grouping} round-trip changed")
    _require(render(parse(example_text)) == example_text, "saved example is not canonical OAK")
    _require(
        [item.id for item in example.processes] == ["encode", "decode"],
        "scenario must contain exactly encode then decode processes",
    )
    _require(not example.state, "encoding and decoding must remain stateless")

    grammar = _constant(example, "grammar")
    parser = Lark(grammar, parser="lalr")
    recipe = values["encoded-recipe"]
    parser.parse(recipe)
    bad_keyword_rejected = False
    try:
        parser.parse(recipe.replace("keep first", "keep random", 1))
    except UnexpectedInput:
        bad_keyword_rejected = True
    _require(bad_keyword_rejected, "grammar accepted an unknown deduplication keyword")

    invalid_recipe = values["invalid-recipe"]
    parser.parse(invalid_recipe)
    _require(
        "Keep account at least minimum." in invalid_recipe,
        "invalid-recipe no longer demonstrates a syntactically valid semantic mismatch",
    )


def _run_oak(node: Node, interface: str, payload: dict[str, Any], callback: ActHandler) -> ExecutionResult:
    return execute(node, Arrival(interface=interface, values=payload), {}, act=callback)


def _check_execution(example: Node, values: dict[str, Any]) -> None:
    success = {"READY": True, "ARTIFACT": "complete artifact", "REASON": ""}
    refusal = {"READY": False, "ARTIFACT": "", "REASON": "unsupported behavior"}

    for interface, payload, output_interface, artifact_key in (
        ("interface.encode-request", {"SOURCE": values["original-source"]}, "interface.encoded", "RECIPE"),
        ("interface.decode-request", {"RECIPE": values["encoded-recipe"]}, "interface.decoded", "SOURCE"),
    ):
        expected_bindings = dict(
            payload,
            GRAMMAR=_constant(example, "grammar"),
            SEMANTICS=_constant(example, "semantics"),
            TARGET=_constant(example, "target"),
            SCOPE=_constant(example, "scope"),
        )
        for candidate, expected_interface in ((success, output_interface), (refusal, "interface.failure")):
            observed: list[dict[str, Any]] = []

            def fixed_act(_action: Act, bindings: Any) -> dict[str, Any]:
                observed.append(dict(bindings))
                _require(dict(bindings) == expected_bindings,
                         "ACT inputs must contain exactly the request and shared prompt constants")
                return candidate

            result = _run_oak(example, interface, payload, fixed_act)
            _require(len(observed) == 1, "expected one deterministic simulated ACT")
            _require(len(result.emissions) == 1, "expected one output emission")
            emission = result.emissions[0]
            _require(emission.interface == expected_interface, "unexpected process output interface")
            if expected_interface != "interface.failure":
                _require(emission.values == {artifact_key: "complete artifact"}, "successful artifact changed")
            else:
                status = "UNSUPPORTED" if artifact_key == "RECIPE" else "INVALID"
                _require(emission.values == {"STATUS": status, "REASON": "unsupported behavior"},
                         "failure status or reason changed")

    invalid_outputs = (
        {"READY": True, "ARTIFACT": "", "REASON": ""},
        {"READY": True, "ARTIFACT": "complete", "REASON": "unresolved issue"},
        {"READY": False, "ARTIFACT": "partial", "REASON": "unsupported behavior"},
        {"READY": False, "ARTIFACT": "", "REASON": ""},
    )
    for output in invalid_outputs:
        for interface, payload in (
            ("interface.encode-request", {"SOURCE": values["original-source"]}),
            ("interface.decode-request", {"RECIPE": values["encoded-recipe"]}),
        ):
            rejected = False
            try:
                _run_oak(example, interface, payload, lambda _action, _bindings: output)
            except (ExecutionError, ValueError):
                rejected = True
            _require(rejected, f"OAK accepted invalid ACT decision: {output}")

    for interface, key in (("interface.encode-request", "SOURCE"), ("interface.decode-request", "RECIPE")):
        for payload in ({}, {key: ""}):
            rejected = False
            try:
                _run_oak(example, interface, payload, lambda _action, _bindings: success)
            except (ExecutionError, ValueError):
                rejected = True
            _require(rejected, f"OAK accepted empty or missing {key}")


def _tag(value: Any) -> Any:
    if isinstance(value, dict):
        return ("dict", sorted((key, _tag(item)) for key, item in value.items()))
    if isinstance(value, list):
        return ("list", [_tag(item) for item in value])
    if isinstance(value, tuple):
        return ("tuple", [_tag(item) for item in value])
    return (type(value).__name__, value)


def _invoke(function: Any, args: list[Any], kwargs: dict[str, Any]) -> dict[str, Any]:
    copied_args, copied_kwargs = copy.deepcopy(args), copy.deepcopy(kwargs)
    before = copy.deepcopy((copied_args, copied_kwargs))
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            result = {"return": function(*copied_args, **copied_kwargs)}
        except Exception as error:  # Exact type and message are part of this fixture's contract.
            result = {"exception": type(error).__name__, "message": str(error)}
    return {
        "result": result,
        "mutated": _tag((copied_args, copied_kwargs)) != _tag(before),
        "stdout": stdout.getvalue(),
        "stderr": stderr.getvalue(),
    }


def _row(event_id: Any = "x", account: Any = "alice", points: Any = 1) -> dict[str, Any]:
    return {"id": event_id, "account": account, "points": points}


def _edge_cases() -> list[tuple[str, list[Any], dict[str, Any]]]:
    cases: list[tuple[str, list[Any], dict[str, Any]]] = []

    def add(name: str, *args: Any, **kwargs: Any) -> None:
        cases.append((name, list(args), kwargs))

    add("required_events_argument")
    add("required_events_argument_with_keywords", minimum=1, limit=2)
    add("empty", [])
    add("explicit_null_events", None)
    add("basic", [_row()])
    add("keyword_call", events=[_row()], minimum=0, limit=5)
    add("dedup_before_filter", [_row(points=1), _row(points=99)], 10)
    add("first_valid_not_first_seen", [_row(points=True), _row(points=9)])
    add("global_dedup_cross_accounts", [_row(account="alice"), _row(account="bob", points=99)])
    add("trimmed_id", [_row(" x ", points=4), _row("x", points=99)])
    add("id_case_sensitive", [_row("X", points=4), _row("x", points=9)])
    add("unicode_casefold", [_row("1", "Straße", 4), _row("2", "STRASSE", 6)])
    add("unicode_trim", [_row("\u2003x\u00a0", "\u2003A\u00a0", 4)])
    add("unicode_dotted_i", [_row("1", "İ", 2), _row("2", "i", 3)])
    add("negative_points", [_row(points=-4)])
    add("zero_points", [_row(points=0)])
    add("boundary_minimum", [_row("1", points=4), _row("2", points=5)], 5)
    add("zero_limit_keeps_totals", [_row(points=7)], 0, 0)
    add("tie_break_and_full_totals", [_row("1", "z", 10), _row("2", "a", 10), _row("3", "b", 9)], 0, 1)
    add("big_integers", [_row("1", points=2**100), _row("2", points=2**100)])
    add("all_bad_rows", [None, True, 1, "x", [], {}, _row(points=False), _row(""), _row(account=" ")])
    add("ignored_extra_fields", [dict(_row(), extra={"a": [1, 2]})])
    add("validation_order_all_invalid", None, True, True)
    add("validation_order_minimum_first", [], True, True)
    add("too_many_args", [], 0, 5, 10)
    add("unknown_keyword", [], unknown=1)
    add("duplicate_keyword", [], events=[])
    for value in [None, True, False, -1, 0.0, "0", [], {}]:
        add("bad_minimum_" + repr(value), [], value)
        add("bad_limit_" + repr(value), [], 0, value)
    for value in [True, 0, "", {}, 1.2]:
        add("bad_events_" + repr(value), value)
    for field in ["id", "account", "points"]:
        missing = _row()
        del missing[field]
        add("missing_" + field, [missing, _row(points=3)])
        for value in [None, True, False, [], {}, 0, 0.0, "", " ", "1"]:
            record = _row()
            record[field] = value
            add("field_" + field + "_" + repr(value), [record, _row(points=3)])
    _require(len(cases) == 81, f"expected 81 frozen edge cases, got {len(cases)}")
    return cases


def _fuzz_cases(count: int = 2000):
    rng = random.Random(872341)
    ids = ["x", " x ", "X", "y", "", " ", "ß", "ss", "\u2003x"]
    names = ["Alice", "alice", " BOB ", "Straße", "STRASSE", "İ", "i", "", "\t"]
    invalid = [None, True, False, {}, [], 0.0, "1"]
    valid_params = [0, 0, 0, 1, 2, 5, 10, 20]
    for index in range(count):
        events = []
        for _ in range(rng.randrange(36)):
            if rng.random() < 0.13:
                events.append(copy.deepcopy(rng.choice(invalid)))
                continue
            record = _row(
                rng.choice(ids + invalid if rng.random() < 0.15 else ids),
                rng.choice(names + invalid if rng.random() < 0.15 else names),
                rng.choice(invalid) if rng.random() < 0.15 else rng.randint(-20, 100),
            )
            if rng.random() < 0.06:
                del record[rng.choice(["id", "account", "points"])]
            events.append(record)
        minimum = rng.choice(valid_params if rng.random() < 0.85 else invalid + [-1])
        limit = rng.choice(valid_params if rng.random() < 0.85 else invalid + [-1])
        if rng.random() < 0.03:
            events = rng.choice(invalid)
        yield "fuzz_" + str(index), [events, minimum, limit], {}


def _cli_cases(cases: list[tuple[str, list[Any], dict[str, Any]]]) -> list[str]:
    values: list[Any] = [{}, {"events": []}, {"events": None}, [], None, True, 2, "x"]
    for _, args, kwargs in cases:
        if args and len(args) <= 3 and not kwargs:
            values.append(dict(zip(["events", "minimum", "limit"], args)))
        if len(values) >= 38:
            break
    values.extend([
        {"events": [_row("1", "Straße", 4), _row("2", "STRASSE", 6)]},
        {"events": [_row(points=4)], "limit": 0},
        {"events": [_row(points=4)], "minimum": None},
        {"minimum": 1},
    ])
    inputs = [json.dumps(value, ensure_ascii=False) for value in values] + ["", "{", "null trailing", "{}\n{}"]
    _require(len(inputs) == 46, f"expected 46 CLI inputs, got {len(inputs)}")
    return inputs


def _load_program(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("saved_regenerative_fixture", path)
    _require(spec is not None and spec.loader is not None, f"cannot load saved program {path.name}")
    module = importlib.util.module_from_spec(spec)
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        spec.loader.exec_module(module)
    _require(not stdout.getvalue() and not stderr.getvalue(), f"{path.name} printed during import")
    _require(callable(getattr(module, "summarize", None)), f"{path.name} lacks summarize")
    return module


def _run_cli(path: Path, text: str, cwd: Path) -> dict[str, Any]:
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    try:
        process = subprocess.run(
            [sys.executable, str(path)],
            input=text.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=4,
            env=env,
            cwd=cwd,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(f"saved fixture {path.name} timed out") from error
    return {
        "status": process.returncode,
        "stdout": process.stdout.decode("utf-8"),
        "stderr": process.stderr.decode("utf-8"),
    }


def _differential(values: dict[str, Any]) -> tuple[int, int, int]:
    edges = _edge_cases()
    cases = edges + list(_fuzz_cases())
    _require(len(cases) == 2081, f"expected 2081 total function cases, got {len(cases)}")
    cli_inputs = _cli_cases(edges)
    with tempfile.TemporaryDirectory(prefix="oak-regenerative-") as temporary:
        temp = Path(temporary)
        fixture_ids = ("original-source", "decoded-a", "decoded-b")
        paths: dict[str, Path] = {}
        for identifier in fixture_ids:
            path = temp / f"{identifier}.py"
            path.write_text(values[identifier], encoding="utf-8", newline="\n")
            paths[identifier] = path

        original = _load_program(paths["original-source"])
        _require(original.summarize([]) == {"accounts": [], "accepted": 0, "points": 0},
                 "reference empty report differs from the independent expectation")
        _require(original.summarize([_row(points=1), _row(points=99)], 10)
                 == {"accounts": [], "accepted": 0, "points": 0}, "reference changed deduplication order")
        _require(original.summarize([_row("1", "Straße", 4), _row("2", "STRASSE", 6)]) == {
            "accounts": [{"account": "strasse", "events": 2, "points": 10}], "accepted": 2, "points": 10},
            "reference changed Unicode normalization")
        _require(original.summarize([_row(points=7)], limit=0)
                 == {"accounts": [], "accepted": 1, "points": 7}, "reference changed pre-limit totals")
        _require(original.summarize([_row(points=True), _row(points=9)])["points"] == 9,
                 "reference allowed a boolean point value to own an ID")
        expected = [_invoke(original.summarize, args, kwargs) for _, args, kwargs in cases]
        expected_cli = [_run_cli(paths["original-source"], value, temp) for value in cli_inputs]
        for identifier in ("decoded-a", "decoded-b"):
            candidate = _load_program(paths[identifier])
            for (label, args, kwargs), want in zip(cases, expected):
                got = _invoke(candidate.summarize, args, kwargs)
                _require(_tag(got) == _tag(want), f"{identifier} differs from original on {label}")
            for text, want in zip(cli_inputs, expected_cli):
                got = _run_cli(paths[identifier], text, temp)
                _require(got == want, f"{identifier} CLI differs from original on {text!r}")

        bug_input = "{}"
        for identifier in ("failed-decoded-a", "failed-decoded-b"):
            path = temp / f"{identifier}.py"
            path.write_text(values[identifier], encoding="utf-8", newline="\n")
            result = _run_cli(path, bug_input, temp)
            _require(result["status"] == 1 and "missing 1 required positional argument: 'events'" in result["stderr"],
                     f"{identifier} no longer exposes the recorded missing-default bug")
        return len(edges), len(cases) - len(edges), len(cli_inputs)


def validate_example() -> None:
    """Validate saved OAK and code artifacts deterministically, offline."""
    example_text = (ROOT / "example.oak.md").read_text(encoding="utf-8")
    example, _specimens, values = _load_fixtures()
    _check_oak(example_text, example, values)
    _check_hashes(example_text, values)
    _check_execution(example, values)
    edge_count, fuzz_count, cli_count = _differential(values)
    print(
        "Verified regenerative code example: "
        f"{edge_count} edge, {fuzz_count} seeded randomized, {cli_count} CLI inputs; "
        "all OAK actions were deterministic simulations."
    )


if __name__ == "__main__":
    validate_example()
