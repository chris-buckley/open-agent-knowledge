"""Validate examples, freshness gates, and every working product path."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
import json
from pathlib import Path
import runpy
import sys
from typing import Annotated

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pydantic import ConfigDict, TypeAdapter, ValidationError, create_model

from build.surfaces import (
    AUTHORABLE_MODELS,
    model_examples,
    model_schema,
    model_surfaces,
    slug,
    surface_example,
    surface_instance,
)
from oak import (
    Act,
    All,
    Any,
    Arrival,
    Assert,
    AtLeast,
    AtMost,
    BindingValue,
    Call,
    Compare,
    Constant,
    ConstantValue,
    DateTime,
    DottedPath,
    Emit,
    Emission,
    ExecutionError,
    ExecutionResult,
    Fail,
    Foreach,
    If,
    Instruction,
    Interface,
    InterfaceValue,
    Join,
    Lines,
    ListOf,
    LiteralValue,
    MaxChars,
    Node,
    NonBlankLine,
    NonEmpty,
    Not,
    OneOf,
    Par,
    Placeholder,
    Process,
    ProcessName,
    Quantity,
    Regex,
    RegexPattern,
    ResolutionError,
    Schema,
    Set,
    SlugId,
    State,
    StateValue,
    TargetPath,
    ToolContract,
    Trigger,
    Type,
    Unit,
    ValueBinding,
    ValueReference,
    Where,
    datetime_text,
    execute,
    number_text,
    parse,
    quantity_text,
    render,
    resolve,
    where,
)
from oak.base import OakModel
from oak.parse import _binding, _condition, _constraint, _interfaces, _named_values, _processes, _schemas, _steps, _triggers, _value, _where
from oak.rules import RULES
from oak.surface import SURFACES, surface_for

METADATA_MODELS = (
    *AUTHORABLE_MODELS,
    Quantity,
    DateTime,
    Arrival,
    Emission,
    ExecutionResult,
)

TEXT_EXAMPLES = (
    (SlugId, ("triage-decision", "stdin", "mode")),
    (Placeholder, ("COMMAND", "NEXT_ACTION")),
    (TargetPath, ("process.route", "../shared/processes.oak.md#process.route")),
    (DottedPath, ("constant.policy", "state.mode", "interface.stdin.COMMAND")),
    (ValueReference, ("$constant.policy", "$state.mode", "$interface.stdin.COMMAND", "$RESULT")),
    (ProcessName, ("Route command", "Write OAK")),
    (NonBlankLine, ("Use the supplied schema.",)),
    (RegexPattern, ("^[0-9]+$",)),
)

_STRICT = ConfigDict(strict=True, regex_engine="rust-regex")


def _field_model(model: type[OakModel], name: str) -> type[OakModel]:
    field = model.model_fields[name]
    annotation = Annotated[field.annotation, *field.metadata] if field.metadata else field.annotation
    return create_model(f"{model.__name__}{name.title()}Example", __base__=OakModel, value=(annotation, ...))


def _validate_text_examples() -> None:
    for annotation, examples in TEXT_EXAMPLES:
        adapter = TypeAdapter(annotation, config=_STRICT)
        for example in examples:
            adapter.validate_python(example)


def _validate_metadata() -> None:
    for model in METADATA_MODELS:
        schema = model_schema(model)
        if not schema.get("title") or not schema.get("description"):
            raise RuntimeError(f"{model.__name__} lacks title or description")
        model_examples(model)
        for name, field in model.model_fields.items():
            if not field.description:
                raise RuntimeError(f"{model.__name__}.{name} has no description")
            if not field.examples:
                raise RuntimeError(f"{model.__name__}.{name} has no examples")
            example_model = _field_model(model, name)
            for example in field.examples:
                example_model.model_validate({"value": example})


def _parse_surface(surface, text: str):
    model = surface.model
    lines = text.splitlines()
    if model is Node:
        return parse(text)
    if model is Instruction:
        return Instruction(id="generated", body=text)
    if model is Constant:
        return _named_values(lines, 1, constants=True)[0]
    if model is Schema:
        return _schemas(lines, 1, "xml")[0]
    if model is State:
        return _named_values(lines, 1, constants=False)[0]
    if model is Trigger:
        return _triggers(lines, 1, "xml")[0]
    if model is Process:
        return _processes(lines, 1, "xml")[0]
    if model is Interface:
        return _interfaces(lines, 1, "xml")[0]
    if model in (Type, OneOf, Regex, NonEmpty, MaxChars, Lines, ListOf, AtLeast, AtMost):
        return _constraint(text, surface.id, 1)
    if model is Where:
        return _where(text, surface.id, 1)
    if model in (LiteralValue, ConstantValue, StateValue, InterfaceValue, BindingValue):
        return _value(text, surface.id, 1)
    if model is ValueBinding:
        return _binding(text, surface.id, 1)
    if model in (Compare, All, Any, Not):
        return _condition(lines, 0, 0, surface.id, 1)[0]
    if model in (Act, Set, Emit, If, Call, Fail, Assert, Foreach, Par, Join):
        return _steps(lines, 0, 0, surface.id, 1)[0][0]
    raise TypeError(model.__name__)


def _normalized(value: OakModel) -> object:
    data = value.model_dump(mode="json", by_alias=True)
    if isinstance(value, Instruction):
        data.pop("id", None)
    if isinstance(value, Node):
        for instruction in data.get("instructions", []):
            instruction.pop("id", None)
    return data


def _freshness_gates() -> None:
    from build import docs as docs_build
    from build import prompt as prompt_build
    from build.docs import documents

    expected_names = {slug(model.__name__) + ".md" for model in AUTHORABLE_MODELS}
    if set(documents()) != expected_names:
        raise RuntimeError("freshness gate 1 failed")

    for model in AUTHORABLE_MODELS:
        for instance in model_examples(model):
            surface_for(instance)

    for surface in SURFACES:
        rendered = [field.name for field in surface.fields if field.role == "rendered"]
        if len(rendered) != len(set(rendered)):
            raise RuntimeError(f"freshness gate 3 failed for {surface.id}")

    for surface in SURFACES:
        if {field.name for field in surface.fields} != set(surface.model.model_fields):
            raise RuntimeError(f"freshness gate 4 failed for {surface.id}")

    for surface in SURFACES:
        surface_example(surface)

    for surface in SURFACES:
        original = surface_instance(surface)
        rebuilt = _parse_surface(surface, surface_example(surface))
        if _normalized(original) != _normalized(rebuilt):
            raise RuntimeError(f"freshness gate 6 failed for {surface.id}")

    parsed_docs = {name: parse(text) for name, text in documents().items()}

    for name, node in parsed_docs.items():
        if render(node, grouping="markdown") + "\n" != documents()[name]:
            raise RuntimeError(f"freshness gate 8 failed for {name}")

    if not (
        docs_build.SURFACE_SOURCE is prompt_build.SURFACE_SOURCE is SURFACES
        and docs_build.RULE_SOURCE is prompt_build.RULE_SOURCE is RULES
    ):
        raise RuntimeError("freshness gate 9 failed")

    _validate_outputs()


def _validate_examples_and_render() -> None:
    for stem in ("shell", "incident_triage"):
        path = ROOT / "examples" / f"{stem}.oak.md"
        text = path.read_text(encoding="utf-8")
        node = parse(text)
        if render(node) + "\n" != text:
            raise RuntimeError(f"{stem} canonical render is stale")
        for grouping in ("xml", "markdown"):
            rendered = render(node, grouping=grouping)
            if render(parse(rendered), grouping=grouping) != rendered:
                raise RuntimeError(f"{stem} {grouping} round trip changed text")


def _contract_schemas() -> tuple[Schema, Schema]:
    return (
        Schema(
            id="raw-name",
            template="<RAW_NAME>",
            where=[where("RAW_NAME", Type(of="string"), NonEmpty())],
        ),
        Schema(
            id="normal-name",
            template="<NORMAL_NAME>",
            where=[where("NORMAL_NAME", Type(of="string"), NonEmpty())],
        ),
    )


def _normalise_process() -> Process:
    return Process(
        id="normalise",
        name="Normalise name",
        input="schema.raw-name",
        output="schema.normal-name",
        steps=[
            Act(
                instruction="Normalise <RAW_NAME> into <NORMAL_NAME>.",
                inputs=[
                    ValueBinding(
                        placeholder="RAW_NAME",
                        value=BindingValue(binding="RAW_NAME"),
                    )
                ],
                outputs=["NORMAL_NAME"],
            )
        ],
    )


def _validate_resolution() -> None:
    shared = Node(schemas=[Schema(id="shared", template="<VALUE>", where=[where("VALUE", Type(of="string"))])])
    root = Node(interfaces=[Interface(id="shared", direction="in", schema="shared.oak.md#schema.shared")])
    graph = resolve(root, source="root.oak.md", load=lambda path: shared if path == "shared.oak.md" else None)
    _document, schema = graph.entry("root.oak.md", "shared.oak.md#schema.shared", Schema)
    if schema.id != "shared":
        raise RuntimeError("resolution selected the wrong schema")

    raw, normal = _contract_schemas()
    target = Node(schemas=[raw, normal], processes=[_normalise_process()])
    caller = Node(
        processes=[
            Process(
                id="handle",
                name="Handle request",
                steps=[
                    Call(
                        process="target.oak.md#process.normalise",
                        inputs=[ValueBinding(placeholder="RAW_NAME", value=LiteralValue(value="Ada"))],
                        outputs=["NORMAL_NAME"],
                    )
                ],
            )
        ]
    )
    def loader(path: str) -> Node | None:
        return target if path == "target.oak.md" else None

    resolve(caller, source="root.oak.md", load=loader)

    failures = (
        (
            "call_contract_mismatch",
            Node(
                processes=[
                    Process(
                        id="handle",
                        name="Handle request",
                        steps=[Call(process="target.oak.md#process.normalise")],
                    )
                ]
            ),
        ),
        (
            "trigger_process_input",
            Node(
                triggers=[
                    Trigger(
                        id="invalid",
                        when="A name arrives.",
                        then="target.oak.md#process.normalise",
                    )
                ]
            ),
        ),
    )
    for code, invalid in failures:
        try:
            resolve(invalid, source="root.oak.md", load=loader)
        except ResolutionError as error:
            if error.code != code:
                raise RuntimeError(f"expected {code}, got {error.code}") from None
        else:
            raise RuntimeError(f"expected {code}")

    relative_contract = Node(
        processes=[
            Process(
                id="invalid",
                name="Build result",
                input="target.oak.md#schema.raw-name",
                output="target.oak.md#schema.normal-name",
                steps=[
                    Act(
                        instruction="Read <RAW_NAME>.",
                        inputs=[
                            ValueBinding(
                                placeholder="RAW_NAME",
                                value=BindingValue(binding="RAW_NAME"),
                            )
                        ],
                    )
                ],
            )
        ]
    )
    try:
        resolve(relative_contract, source="root.oak.md", load=loader)
    except ResolutionError as error:
        if error.code != "process_output_binding_mismatch":
            raise RuntimeError(
                "expected process_output_binding_mismatch, "
                f"got {error.code}"
            ) from None
    else:
        raise RuntimeError("expected process_output_binding_mismatch")


def _validate_execution() -> None:
    shell = parse((ROOT / "examples" / "shell.oak.md").read_text(encoding="utf-8"))
    result = execute(
        shell,
        Arrival(when="A command line arrives.", interfaces={"interface.stdin": {"COMMAND": "pwd"}}),
        {"state.mode": "open"},
    )
    if result.process != "process.route" or result.emissions != [Emission(interface="interface.stdout", values={"OUTPUT": "/oak"})]:
        raise RuntimeError("shell execution failed")

    parallel = Node(
        state=[State(id="done", value=False)],
        triggers=[Trigger(id="run-trigger", when="Run parallel work.", then="process.run")],
        processes=[
            Process(
                id="run",
                name="Run tools",
                steps=[
                    Par(
                        steps=[
                            Act(tool="tool-a", instruction="Produce <A>.", outputs=["A"]),
                            Act(tool="tool-b", instruction="Produce <B>.", outputs=["B"]),
                        ]
                    ),
                    Join(),
                    Assert(
                        condition=All(
                            conditions=[
                                Compare(left=BindingValue(binding="A"), operator="not_equals", right=LiteralValue(value="")),
                                Compare(left=BindingValue(binding="B"), operator="not_equals", right=LiteralValue(value="")),
                            ]
                        )
                    ),
                    Foreach(
                        binding="ITEM",
                        value=LiteralValue(value=[1, 2]),
                        steps=[
                            Act(
                                instruction="Record <ITEM>.",
                                inputs=[ValueBinding(placeholder="ITEM", value=BindingValue(binding="ITEM"))],
                            )
                        ],
                    ),
                    Set(state="state.done", value=LiteralValue(value=True)),
                ],
            )
        ],
    )
    tools = {
        "tool-a": ToolContract(lambda _step, _values: {"A": "a"}, frozenset(), frozenset({"A"}), True),
        "tool-b": ToolContract(lambda _step, _values: {"B": "b"}, frozenset(), frozenset({"B"}), True),
    }
    result = execute(
        parallel,
        Arrival(when="Run parallel work."),
        {"state.done": False},
        act=lambda _step, _values: {},
        tools=tools,
    )
    if result.state != {"state.done": True}:
        raise RuntimeError("parallel or foreach execution failed")

    raw, normal = _contract_schemas()
    contract = Node(
        schemas=[raw, normal],
        triggers=[Trigger(id="name", when="A name arrives.", then="process.handle")],
        processes=[
            _normalise_process(),
            Process(
                id="handle",
                name="Handle request",
                steps=[
                    Call(
                        process="process.normalise",
                        inputs=[
                            ValueBinding(
                                placeholder="RAW_NAME",
                                value=InterfaceValue(interface="interface.request", placeholder="RAW_NAME"),
                            )
                        ],
                        outputs=["NORMAL_NAME"],
                    ),
                    Emit(
                        interface="interface.result",
                        bindings=[
                            ValueBinding(
                                placeholder="NORMAL_NAME",
                                value=BindingValue(binding="NORMAL_NAME"),
                            )
                        ],
                    ),
                ],
            ),
        ],
        interfaces=[
            Interface(id="request", direction="in", schema="schema.raw-name"),
            Interface(id="result", direction="out", schema="schema.normal-name"),
        ],
    )
    for grouping in ("xml", "markdown"):
        rendered = render(contract, grouping=grouping)
        if render(parse(rendered), grouping=grouping) != rendered:
            raise RuntimeError(f"process contract {grouping} round trip changed text")

    result = execute(
        contract,
        Arrival(when="A name arrives.", interfaces={"interface.request": {"RAW_NAME": " ada "}}),
        {},
        act=lambda _step, values: {"NORMAL_NAME": values["RAW_NAME"].strip().title()},
    )
    if result.emissions != [Emission(interface="interface.result", values={"NORMAL_NAME": "Ada"})]:
        raise RuntimeError("process contract execution failed")

    try:
        execute(
            contract,
            Arrival(
                when="A name arrives.",
                interfaces={"interface.request": {"RAW_NAME": "Ada"}},
            ),
            {},
            act=lambda _step, _values: {"NORMAL_NAME": ""},
        )
    except ExecutionError as error:
        if error.code != "invalid_process_output":
            raise RuntimeError(
                f"expected invalid_process_output, got {error.code}"
            ) from None
    else:
        raise RuntimeError("expected invalid_process_output")


def _expect_rule(code: str, author) -> None:
    try:
        author()
    except ValidationError as error:
        if code not in {str(item["type"]) for item in error.errors()}:
            raise RuntimeError(f"expected {code}, got {error}") from None
        return
    raise RuntimeError(f"expected {code}")


def _validate_contract_rules() -> None:
    raw, normal = _contract_schemas()

    def trigger_input() -> None:
        Node(
            schemas=[raw, normal],
            triggers=[Trigger(id="invalid", when="A name arrives.", then="process.normalise")],
            processes=[_normalise_process()],
        )

    def output_missing() -> None:
        Node(
            schemas=[raw, normal],
            processes=[
                Process(
                    id="normalise",
                    name="Normalise name",
                    input="schema.raw-name",
                    output="schema.normal-name",
                    steps=[
                        Act(
                            instruction="Read <RAW_NAME>.",
                            inputs=[ValueBinding(placeholder="RAW_NAME", value=BindingValue(binding="RAW_NAME"))],
                        )
                    ],
                )
            ],
        )

    def call_mismatch() -> None:
        Node(
            schemas=[raw, normal],
            processes=[
                _normalise_process(),
                Process(
                    id="handle",
                    name="Handle request",
                    steps=[Call(process="process.normalise")],
                ),
            ],
        )

    _expect_rule("trigger_process_input", trigger_input)
    _expect_rule("process_output_binding_mismatch", output_missing)
    _expect_rule("call_contract_mismatch", call_mismatch)


def _validate_json_ld_style_display() -> None:
    node = parse((ROOT / "examples" / "shell.oak.md").read_text(encoding="utf-8"))
    data = json.loads(
        render(
            node,
            render="json-ld",
            document="https://example.org/oak/shell.oak.md",
            vocabulary="https://example.org/oak#",
        )
    )
    if data.get("@id") != "https://example.org/oak/shell.oak.md":
        raise RuntimeError("JSON-LD document id is wrong")

    raw, normal = _contract_schemas()
    contract = Node(
        schemas=[raw, normal],
        processes=[
            _normalise_process(),
            Process(
                id="handle",
                name="Handle request",
                steps=[
                    Call(
                        process="process.normalise",
                        inputs=[ValueBinding(placeholder="RAW_NAME", value=LiteralValue(value="Ada"))],
                        outputs=["NORMAL_NAME"],
                    )
                ],
            ),
        ],
    )
    linked = json.loads(
        render(
            contract,
            render="json-ld",
            document="https://example.org/oak/contract.oak.md",
            vocabulary="https://example.org/oak#",
        )
    )
    normalise, handle = linked["processes"]
    call = handle["steps"][0]
    if not (
        normalise["input"]["@id"].endswith("#schema.raw-name")
        and normalise["output"]["@id"].endswith("#schema.normal-name")
        and call["process"]["@id"].endswith("#process.normalise")
        and call["outputs"] == ["NORMAL_NAME"]
    ):
        raise RuntimeError("JSON-LD process contract is wrong")

    styled = render(
        Node(instructions=[Instruction(id="wording", body="Utilize the exact command.")]),
        style="asd-ste100-9",
    )
    if "Use the exact command." not in styled:
        raise RuntimeError("controlled style failed")
    if number_text(12345.5) != "12\u2009345.5":
        raise RuntimeError("number display failed")
    if quantity_text(Quantity(value=Decimal("10"), unit=Unit.KILOGRAM)) != "10 kg":
        raise RuntimeError("quantity display failed")
    value = DateTime(value=datetime.fromisoformat("2026-08-24T17:35:38+10:00"), zone="Australia/Brisbane")
    if datetime_text(value) != "2026-08-24T17:35:38+10:00 [Australia/Brisbane]":
        raise RuntimeError("datetime display failed")


def _validate_outputs() -> None:
    from build.docs import documents
    from build.ebnf import grammar
    from build.prompt import prompt

    prompt_text = prompt()
    if render(parse(prompt_text), grouping="xml") + "\n" != prompt_text:
        raise RuntimeError("prompt output is not canonical XML OAK")

    expected = {
        ROOT / "outputs" / "oak.ebnf": grammar(),
        ROOT / "outputs" / "prompt.md": prompt_text,
        **{
            ROOT / "outputs" / "docs" / name: text
            for name, text in documents().items()
        },
    }
    for path, text in expected.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            raise RuntimeError(f"generated output is missing or stale: {path}")
    actual = set((ROOT / "outputs" / "docs").glob("*.md"))
    documented = {path for path in expected if path.parent == ROOT / "outputs" / "docs"}
    if actual != documented:
        raise RuntimeError("documentation output path set is stale")


def _run_example_wrappers() -> None:
    for stem in ("shell", "incident_triage"):
        runpy.run_path(str(ROOT / "examples" / f"{stem}.py"), run_name="__main__")


def validate_examples() -> None:
    """Raise when any example, gate, or working product path is invalid."""
    _validate_text_examples()
    _validate_metadata()
    _validate_examples_and_render()
    _validate_resolution()
    _validate_execution()
    _validate_contract_rules()
    _validate_json_ld_style_display()
    _run_example_wrappers()
    _freshness_gates()


if __name__ == "__main__":
    validate_examples()
