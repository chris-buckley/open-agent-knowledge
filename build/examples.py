"""Validate examples and every working product path."""

from datetime import datetime
from decimal import Decimal
from pathlib import Path
import sys
from typing import Annotated

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pydantic import ConfigDict, TypeAdapter, create_model

from oak.base import OakModel
from oak.execute import Arrival, Emission, ExecutionResult, execute
from oak.node import Node, Root
from oak.node.parts import (
    Act,
    AtLeast,
    AtMost,
    BindingValue,
    Call,
    Condition,
    Constant,
    ConstantValue,
    Emit,
    Fail,
    If,
    Instruction,
    Interface,
    InterfaceValue,
    Lines,
    ListOf,
    LiteralValue,
    MaxChars,
    NonEmpty,
    OneOf,
    Process,
    Regex,
    Schema,
    Set,
    State,
    StateValue,
    Trigger,
    Type,
    ValueBinding,
    Where,
    where,
)
from oak.parse import parse
from oak.render import node_xml, render
from oak.vocabulary import (
    DateTime,
    DottedPath,
    NonBlankLine,
    Placeholder,
    ProcessName,
    Quantity,
    RegexPattern,
    SlugId,
    Unit,
    ValueReference,
    datetime_text,
    number_text,
    quantity_text,
)

MODELS = (
    Type,
    OneOf,
    Regex,
    NonEmpty,
    MaxChars,
    Lines,
    ListOf,
    AtLeast,
    AtMost,
    Where,
    Schema,
    Instruction,
    Constant,
    State,
    LiteralValue,
    ConstantValue,
    StateValue,
    InterfaceValue,
    BindingValue,
    ValueBinding,
    Condition,
    Act,
    Set,
    Emit,
    If,
    Call,
    Fail,
    Process,
    Trigger,
    Interface,
    Node,
    Root,
    Quantity,
    DateTime,
    Arrival,
    Emission,
    ExecutionResult,
)

TEXT_EXAMPLES = (
    (
        "SlugId",
        SlugId,
        ("triage-decision", "stdin", "pwd", "mode"),
    ),
    (
        "Placeholder",
        Placeholder,
        ("COMMAND", "NEXT_ACTION"),
    ),
    (
        "DottedPath",
        DottedPath,
        (
            "constant.escalation-policy",
            "state.mode",
            "process.pwd",
            "interface.stdout",
            "interface.stdin.COMMAND",
        ),
    ),
    (
        "ValueReference",
        ValueReference,
        (
            "$constant.escalation-policy",
            "$state.mode",
            "$interface.stdin.COMMAND",
            "$SEVERITY",
        ),
    ),
    (
        "ProcessName",
        ProcessName,
        ("Route command", "Run pwd", "Write OAK"),
    ),
    (
        "NonBlankLine",
        NonBlankLine,
        ("Use the supplied schema.",),
    ),
    (
        "RegexPattern",
        RegexPattern,
        ("^[0-9]+$",),
    ),
)

_STRICT = ConfigDict(
    strict=True,
    regex_engine="rust-regex",
)


def _extra_examples(model: type[OakModel]) -> list[object]:
    extra = model.model_config.get("json_schema_extra")
    examples = extra.get("examples") if isinstance(extra, dict) else None
    if not examples:
        raise RuntimeError(f"{model.__name__} has no model examples")
    return list(examples)


def _instances(model: type[OakModel]) -> list[OakModel]:
    result = []
    for index, example in enumerate(_extra_examples(model)):
        try:
            result.append(model.model_validate(example))
        except Exception as error:
            raise RuntimeError(
                f"{model.__name__} model example {index} is invalid: {error}"
            ) from error
    return result


def model_schema(model: type[OakModel]) -> dict[str, object]:
    """Return the model definition from generated JSON Schema."""
    schema = model.model_json_schema()
    reference = schema.get("$ref")
    definitions = schema.get("$defs")

    if isinstance(reference, str) and isinstance(definitions, dict):
        prefix = "#/$defs/"
        if reference.startswith(prefix):
            resolved = definitions.get(reference[len(prefix) :])
            if isinstance(resolved, dict):
                return resolved

    return schema


def model_examples(model: type[OakModel]) -> list[object]:
    """Return validated JSON-safe model examples."""
    return [
        instance.model_dump(mode="json", by_alias=True, exclude_unset=True)
        for instance in _instances(model)
    ]


def _example_model(
    model: type[OakModel],
    name: str,
) -> type[OakModel]:
    field = model.model_fields[name]
    annotation = (
        Annotated[field.annotation, *field.metadata]
        if field.metadata
        else field.annotation
    )
    return create_model(
        f"{model.__name__}{name.title()}Example",
        __base__=OakModel,
        value=(annotation, ...),
    )


def field_examples(
    model: type[OakModel],
    name: str,
) -> list[object]:
    """Return explicit examples or derive Node and Root examples."""
    field = model.model_fields[name]
    authored = list(field.examples or [])

    if not authored:
        if model not in (Node, Root):
            raise RuntimeError(f"{model.__name__}.{name} has no examples")

        authored = [
            instance.model_dump(mode="json", by_alias=True)[name]
            for instance in _instances(model)
        ]

    example_model = _example_model(model, name)
    result = []

    for index, example in enumerate(authored):
        try:
            checked = example_model.model_validate({"value": example})
        except Exception as error:
            raise RuntimeError(
                f"{model.__name__}.{name} example {index} is invalid: {error}"
            ) from error

        result.append(
            checked.model_dump(mode="json", by_alias=True)["value"]
        )

    return result


def _validate_text_examples() -> None:
    for name, annotation, examples in TEXT_EXAMPLES:
        adapter = TypeAdapter(annotation, config=_STRICT)
        for index, example in enumerate(examples):
            try:
                adapter.validate_python(example)
            except Exception as error:
                raise RuntimeError(
                    f"{name} text example {index} is invalid: {error}"
                ) from error


def _validate_model_examples() -> None:
    for model in MODELS:
        schema = model_schema(model)
        if not schema.get("title"):
            raise RuntimeError(f"{model.__name__} has no title")
        if not schema.get("description"):
            raise RuntimeError(f"{model.__name__} has no description")

        model_examples(model)

        for name, field in model.model_fields.items():
            if not field.description:
                raise RuntimeError(f"{model.__name__}.{name} has no description")
            field_examples(model, name)


def _product_root() -> Root:
    command = Schema(
        id="command-line",
        name="Command Line",
        purpose="Carry one command.",
        template="<COMMAND>",
        where=[
            where(
                "COMMAND",
                Type(of="string"),
                NonEmpty(),
                description="the exact command",
            )
        ],
    )
    output = Schema(
        id="terminal-output",
        name="Terminal Output",
        purpose="Carry one output line.",
        template="<OUTPUT>",
        where=[
            where(
                "OUTPUT",
                Type(of="string"),
                NonEmpty(),
                description="the output line",
            )
        ],
    )

    return Root(
        id="root",
        instructions=[
            Instruction(
                id="controlled-wording",
                body="Utilize the exact command.",
            )
        ],
        constants=[
            Constant(
                id="inline-value",
                value="Z",
            ),
            Constant(
                id="repository-tree",
                form="text",
                value="oak\n└── SKILL.md",
            ),
            Constant(
                id="api-config",
                form="json",
                value={"retries": 3, "timeout_ms": 2000},
            ),
            Constant(
                id="service-table",
                form="csv",
                value=[
                    {"service": "billing", "enabled": True},
                    {"service": "support", "enabled": False},
                ],
            ),
            Constant(
                id="deployment-config",
                form="yaml",
                value={"region": "ap-southeast-2", "replicas": 2},
            ),
        ],
        schemas=[command, output],
        state=[State(id="mode", value="open")],
        triggers=[
            Trigger(
                id="command-trigger",
                given=Condition(
                    left=StateValue(state="mode"),
                    operator="equals",
                    right=LiteralValue(value="open"),
                ),
                when="A command line arrives.",
                process="route",
            )
        ],
        processes=[
            Process(
                id="route",
                name="Route command",
                steps=[
                    If(
                        condition=Condition(
                            left=InterfaceValue(
                                interface="stdin",
                                placeholder="COMMAND",
                            ),
                            operator="equals",
                            right=LiteralValue(value="pwd"),
                        ),
                        then=[Call(process="pwd")],
                        otherwise=[Fail(message="Unknown command.")],
                    )
                ],
            ),
            Process(
                id="pwd",
                name="Run pwd",
                steps=[
                    Emit(
                        interface="stdout",
                        bindings=[
                            ValueBinding(
                                placeholder="OUTPUT",
                                value=LiteralValue(value="/oak"),
                            )
                        ],
                    )
                ],
            ),
        ],
        interfaces=[
            Interface(
                id="stdin",
                direction="in",
                schema="command-line",
                description="The command supplied to the tree.",
            ),
            Interface(
                id="stdout",
                direction="out",
                schema="terminal-output",
                description="The output returned by the tree.",
            ),
        ],
    )


def _validate_render_and_parse() -> None:
    root = _product_root()
    if render(root) != node_xml(root):
        raise RuntimeError("the default render is not OAK xml authored")

    for grouping in ("xml", "markdown"):
        text = render(root, grouping=grouping)
        parsed = parse(text)
        rebuilt = render(parsed, grouping=grouping)
        if rebuilt != text:
            raise RuntimeError(f"the {grouping} OAK round trip changed text")

    styled = render(root, style="asd-ste100-9")
    if "Use the exact command." not in styled:
        raise RuntimeError("the controlled style did not rewrite wording")
    if root.instructions[0].body != "Utilize the exact command.":
        raise RuntimeError("the controlled style changed the authored tree")


def _validate_execution() -> None:
    root = Root.model_validate(_extra_examples(Root)[0])
    state: dict[str, object] = {}

    result = execute(
        root,
        Arrival(
            when="The interpreter arrives to transform knowledge.",
            interfaces={
                "knowledge-interface": {"KNOWLEDGE": "oak"}
            },
        ),
        state,
        act=lambda _step, values: {
            "RESULT": str(values["KNOWLEDGE"]).upper()
        },
    )

    if state:
        raise RuntimeError("execution mutated the caller state")
    if result.process != "run":
        raise RuntimeError("execution selected the wrong process")
    if result.state:
        raise RuntimeError("execution committed unexpected state")
    if result.emissions != [
        Emission(
            interface="result-interface",
            values={"RESULT": "OAK"},
        )
    ]:
        raise RuntimeError("execution emitted the wrong values")


def _validate_display() -> None:
    if number_text(12345.5) != "12\u2009345.5":
        raise RuntimeError("number display is invalid")

    if quantity_text(
        Quantity(value=Decimal("10"), unit=Unit.KILOGRAM)
    ) != "10 kg":
        raise RuntimeError("quantity display is invalid")

    value = DateTime(
        value=datetime.fromisoformat("2026-08-24T17:35:38+10:00"),
        zone="Australia/Brisbane",
    )
    if datetime_text(value) != (
        "2026-08-24T17:35:38+10:00 [Australia/Brisbane]"
    ):
        raise RuntimeError("datetime display is invalid")


def _validate_outputs() -> None:
    from build.docs import documents
    from build.ebnf import grammar
    from build.prompt import prompt

    expected = {
        ROOT / "outputs" / "oak.ebnf": grammar(),
        ROOT / "outputs" / "prompt.md": prompt(),
    }
    expected.update(
        {
            ROOT / "outputs" / "docs" / name: text
            for name, text in documents().items()
        }
    )

    for path, text in expected.items():
        if not path.is_file():
            raise RuntimeError(f"missing generated output {path}")
        if path.read_text(encoding="utf-8") != text:
            raise RuntimeError(f"generated output is stale: {path}")

    actual_docs = set((ROOT / "outputs" / "docs").glob("*.md"))
    expected_docs = {
        path for path in expected if path.parent == ROOT / "outputs" / "docs"
    }
    if actual_docs != expected_docs:
        raise RuntimeError("the documentation output set is stale")

    parse(expected[ROOT / "outputs" / "prompt.md"])


def validate_examples() -> None:
    """Raise when any example or working product path is invalid."""
    _validate_text_examples()
    _validate_model_examples()
    _validate_render_and_parse()
    _validate_execution()
    _validate_display()
    _validate_outputs()


if __name__ == "__main__":
    validate_examples()
