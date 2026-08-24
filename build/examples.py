"""Validate every declared model, field, and named text example."""

from typing import Annotated

from pydantic import (
    ConfigDict,
    TypeAdapter,
    create_model,
)

from oak.base import OakModel
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
)
from oak.vocabulary import (
    DottedPath,
    NonBlankLine,
    Placeholder,
    ProcessName,
    RegexPattern,
    SlugId,
    ValueReference,
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
)

TEXT_EXAMPLES = (
    (
        "SlugId",
        SlugId,
        (
            "triage-decision",
            "stdin",
            "pwd",
            "mode",
        ),
    ),
    (
        "Placeholder",
        Placeholder,
        (
            "COMMAND",
            "NEXT_ACTION",
        ),
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
        (
            "Route command",
            "Run pwd",
            "Write OAK",
        ),
    ),
    (
        "NonBlankLine",
        NonBlankLine,
        (
            "Use the supplied schema.",
        ),
    ),
    (
        "RegexPattern",
        RegexPattern,
        (
            "^[0-9]+$",
        ),
    ),
)

_STRICT = ConfigDict(
    strict=True,
    regex_engine="rust-regex",
)


def _validate_text_examples() -> None:
    for name, annotation, examples in TEXT_EXAMPLES:
        adapter = TypeAdapter(
            annotation,
            config=_STRICT,
        )
        for index, example in enumerate(examples):
            try:
                adapter.validate_python(example)
            except Exception as error:
                raise RuntimeError(
                    f"{name} text example {index} is invalid: {error}"
                ) from error


def _validate_model_examples() -> None:
    for model in MODELS:
        extra = model.model_config.get("json_schema_extra")
        examples = (
            extra.get("examples")
            if isinstance(extra, dict)
            else None
        )
        if not examples:
            raise RuntimeError(
                f"{model.__name__} has no model examples"
            )

        for index, example in enumerate(examples):
            try:
                model.model_validate(example)
            except Exception as error:
                raise RuntimeError(
                    f"{model.__name__} model example "
                    f"{index} is invalid: {error}"
                ) from error

        for name, field in model.model_fields.items():
            if not field.description:
                raise RuntimeError(
                    f"{model.__name__}.{name} has no description"
                )
            if not field.examples:
                raise RuntimeError(
                    f"{model.__name__}.{name} has no examples"
                )

            annotation = (
                Annotated[
                    field.annotation,
                    *field.metadata,
                ]
                if field.metadata
                else field.annotation
            )
            example_model = create_model(
                f"{model.__name__}{name.title()}Example",
                __base__=OakModel,
                value=(annotation, ...),
            )

            for index, example in enumerate(field.examples):
                try:
                    example_model.model_validate(
                        {"value": example}
                    )
                except Exception as error:
                    raise RuntimeError(
                        f"{model.__name__}.{name} example "
                        f"{index} is invalid: {error}"
                    ) from error


def validate_examples() -> None:
    """Raise when any declared example is missing or invalid."""
    _validate_text_examples()
    _validate_model_examples()


if __name__ == "__main__":
    validate_examples()
