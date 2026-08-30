"""Declarative authored text variants shared by every OAK consumer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from oak.base import OakModel
from oak.node import Node
from oak.node.parts import (
    Act,
    All,
    Any,
    Assert,
    AtLeast,
    AtMost,
    BindingValue,
    Call,
    Compare,
    Constant,
    ConstantValue,
    Emit,
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
    NonEmpty,
    Not,
    OneOf,
    Par,
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
    While,
)

FieldRole = Literal["rendered", "fixed", "omitted", "generated"]
_PRESENT = object()


@dataclass(frozen=True, slots=True)
class SurfaceField:
    """One model field classification in one authored text variant."""

    name: str
    role: FieldRole
    placeholder: str | None = None


@dataclass(frozen=True, slots=True)
class Surface:
    """One concrete authored text variant."""

    id: str
    model: type[OakModel]
    shape: str
    fields: tuple[SurfaceField, ...]
    part: str | None = None
    tag: str | None = None
    when: tuple[tuple[str, object], ...] = ()

    def matches(self, value: OakModel) -> bool:
        """Return whether this descriptor selects one model value."""
        return type(value) is self.model and all(
            (getattr(value, name) is not None if expected is _PRESENT else getattr(value, name) == expected)
            for name, expected in self.when
        )


def _fields(
    model: type[OakModel],
    *,
    rendered: tuple[str, ...] = (),
    fixed: tuple[str, ...] = (),
    omitted: tuple[str, ...] = (),
    generated: tuple[str, ...] = (),
) -> tuple[SurfaceField, ...]:
    roles: dict[str, FieldRole] = {}
    for role, names in (
        ("rendered", rendered),
        ("fixed", fixed),
        ("omitted", omitted),
        ("generated", generated),
    ):
        for name in names:
            if name in roles:
                raise RuntimeError(f"{model.__name__}.{name} is classified twice")
            roles[name] = role
    missing = set(model.model_fields) - set(roles)
    unknown = set(roles) - set(model.model_fields)
    if missing or unknown:
        raise RuntimeError(
            f"{model.__name__} surface fields differ; "
            f"missing={sorted(missing)} unknown={sorted(unknown)}"
        )
    return tuple(
        SurfaceField(
            name=name,
            role=roles[name],
            placeholder=name.upper() if roles[name] == "rendered" else None,
        )
        for name in model.model_fields
    )


def _surface(
    identifier: str,
    model: type[OakModel],
    shape: str,
    *,
    rendered: tuple[str, ...] = (),
    fixed: tuple[str, ...] = (),
    omitted: tuple[str, ...] = (),
    generated: tuple[str, ...] = (),
    part: str | None = None,
    tag: str | None = None,
    when: tuple[tuple[str, object], ...] = (),
) -> Surface:
    return Surface(
        id=identifier,
        model=model,
        shape=shape,
        fields=_fields(
            model,
            rendered=rendered,
            fixed=fixed,
            omitted=omitted,
            generated=generated,
        ),
        part=part,
        tag=tag,
        when=when,
    )


SURFACES = (
    _surface("constraint-type", Type, "is <OF>", rendered=("of",), fixed=("kind",)),
    _surface("constraint-one-of", OneOf, "is one of <VALUES>", rendered=("values",), fixed=("kind",)),
    _surface("constraint-regex", Regex, "matches `<PATTERN>`", rendered=("pattern",), fixed=("kind",)),
    _surface("constraint-non-empty", NonEmpty, "is non-empty", fixed=("kind",)),
    _surface("constraint-max-chars", MaxChars, "is at most <N> characters", rendered=("n",), fixed=("kind",)),
    _surface("constraint-lines", Lines, "has <MIN> to <MAX> lines", rendered=("min", "max"), fixed=("kind",)),
    _surface("constraint-list-of", ListOf, "is a list of <ITEM> joined by `<SEPARATOR>`", rendered=("item", "separator"), fixed=("kind",)),
    _surface("constraint-at-least", AtLeast, "is at least <VALUE>", rendered=("value",), fixed=("kind",)),
    _surface("constraint-at-most", AtMost, "is at most <VALUE>", rendered=("value",), fixed=("kind",)),
    _surface("where", Where, "- <PLACEHOLDER> <CONSTRAINTS> <EXAMPLES> <DESCRIPTION>.", rendered=("placeholder", "constraints", "examples", "description")),
    _surface("instruction", Instruction, "<BODY>", rendered=("body",), fixed=("part",), generated=("id",), part="instructions"),
    _surface("constant-inline", Constant, "<ID>: <VALUE>", rendered=("id", "value"), fixed=("part", "form"), part="constants", when=(("form", "inline"),)),
    _surface("constant-text", Constant, "<ID>: TEXT<<\n<VALUE>\n>>", rendered=("id", "value"), fixed=("part", "form"), part="constants", when=(("form", "text"),)),
    _surface("constant-json", Constant, "<ID>: JSON<<\n<VALUE>\n>>", rendered=("id", "value"), fixed=("part", "form"), part="constants", when=(("form", "json"),)),
    _surface("constant-csv", Constant, "<ID>: CSV<<\n<VALUE>\n>>", rendered=("id", "value"), fixed=("part", "form"), part="constants", when=(("form", "csv"),)),
    _surface("constant-yaml", Constant, "<ID>: YAML<<\n<VALUE>\n>>", rendered=("id", "value"), fixed=("part", "form"), part="constants", when=(("form", "yaml"),)),
    _surface("schema", Schema, '<schema id="<ID>" name="<NAME>" purpose="<PURPOSE>">\n<TEMPLATE>\n\nWHERE:\n<WHERE>\n</schema>', rendered=("id", "name", "purpose", "template", "where"), fixed=("part",), part="schemas", tag="schema"),
    _surface("state", State, "<ID>: <VALUE>", rendered=("id", "value"), fixed=("part",), part="state"),
    _surface("value-literal", LiteralValue, "<VALUE>", rendered=("value",), fixed=("source",)),
    _surface("value-constant", ConstantValue, "$<CONSTANT>", rendered=("constant",), fixed=("source",)),
    _surface("value-state", StateValue, "$<STATE>", rendered=("state",), fixed=("source",)),
    _surface("value-interface", InterfaceValue, "$<INTERFACE>.<PLACEHOLDER>", rendered=("interface", "placeholder"), fixed=("source",)),
    _surface("value-binding", BindingValue, "$<BINDING>", rendered=("binding",), fixed=("source",)),
    _surface("value-binding-line", ValueBinding, "<PLACEHOLDER> = <VALUE>", rendered=("placeholder", "value")),
    _surface("condition-compare", Compare, "<LEFT> <OPERATOR> <RIGHT>", rendered=("left", "operator", "right"), fixed=("kind",)),
    _surface("condition-all", All, "ALL:\n  <CONDITIONS>", rendered=("conditions",), fixed=("kind",)),
    _surface("condition-any", Any, "ANY:\n  <CONDITIONS>", rendered=("conditions",), fixed=("kind",)),
    _surface("condition-not", Not, "NOT:\n  <CONDITION>", rendered=("condition",), fixed=("kind",)),
    _surface("act-native", Act, "ACT <INSTRUCTION>\n  INPUTS:\n    <INPUTS>\n  OUTPUTS: <OUTPUTS>", rendered=("instruction", "inputs", "outputs"), fixed=("kind",), omitted=("tool",), when=(("tool", None),)),
    _surface("act-tool", Act, 'ACT TOOL "<TOOL>": <INSTRUCTION>\n  INPUTS:\n    <INPUTS>\n  OUTPUTS: <OUTPUTS>', rendered=("tool", "instruction", "inputs", "outputs"), fixed=("kind",), when=(("tool", _PRESENT),)),
    _surface("step-set", Set, "SET <STATE> = <VALUE>", rendered=("state", "value"), fixed=("kind",)),
    _surface("step-emit", Emit, "EMIT <INTERFACE>:\n  <BINDINGS>", rendered=("interface", "bindings"), fixed=("kind",)),
    _surface("step-if", If, "IF <CONDITION>:\nTHEN:\n  <THEN>\nELSE:\n  <OTHERWISE>", rendered=("condition", "then", "otherwise"), fixed=("kind",)),
    _surface("step-call", Call, "CALL <PROCESS>:\n  INPUTS:\n    <INPUTS>\n  OUTPUTS: <OUTPUTS>", rendered=("process", "inputs", "outputs"), fixed=("kind",)),
    _surface("step-fail", Fail, "FAIL <MESSAGE>", rendered=("message",), fixed=("kind",)),
    _surface("step-assert", Assert, "ASSERT <CONDITION>\nMESSAGE <MESSAGE>", rendered=("condition", "message"), fixed=("kind",)),
    _surface("step-foreach", Foreach, "FOREACH <BINDING> IN <VALUE>:\n  <STEPS>", rendered=("binding", "value", "steps"), fixed=("kind",)),
    _surface("step-while", While, "WHILE <CONDITION> LIMIT <LIMIT>:\n  <STEPS>", rendered=("condition", "limit", "steps"), fixed=("kind",)),
    _surface("step-par", Par, "PAR:\n  <STEPS>", rendered=("steps",), fixed=("kind",)),
    _surface("step-join", Join, "JOIN", fixed=("kind",)),
    _surface("process", Process, '<process id="<ID>" name="<NAME>" input="<INPUT>" output="<OUTPUT>">\n<STEPS>\n</process>', rendered=("id", "name", "input", "output", "steps"), fixed=("part",), part="processes", tag="process"),
    _surface("trigger", Trigger, '<trigger id="<ID>">\nGIVEN: <GIVEN>\nWHEN: <WHEN>\nTHEN: <THEN>\n</trigger>', rendered=("id", "given", "when", "then"), fixed=("part",), part="triggers", tag="trigger"),
    _surface("interface", Interface, '<interface id="<ID>" direction="<DIRECTION>" schema="<SCHEMA_ID>">\n<DESCRIPTION>\n</interface>', rendered=("id", "direction", "schema_id", "description"), fixed=("part",), part="interfaces", tag="interface"),
    _surface("node", Node, "<instructions>\n<INSTRUCTIONS>\n</instructions>\n\n<constants>\n<CONSTANTS>\n</constants>\n\n<schemas>\n<SCHEMAS>\n</schemas>\n\n<state>\n<STATE>\n</state>\n\n<triggers>\n<TRIGGERS>\n</triggers>\n\n<processes>\n<PROCESSES>\n</processes>\n\n<interfaces>\n<INTERFACES>\n</interfaces>", rendered=("instructions", "constants", "schemas", "state", "triggers", "processes", "interfaces")),
)

SURFACES_BY_ID = {surface.id: surface for surface in SURFACES}
if len(SURFACES_BY_ID) != len(SURFACES):
    raise RuntimeError("surface ids are not unique")


def surfaces_for_model(model: type[OakModel]) -> tuple[Surface, ...]:
    """Return every concrete surface for one model."""
    return tuple(surface for surface in SURFACES if surface.model is model)


def surface_for(value: OakModel) -> Surface:
    """Return the one descriptor selected by a model value."""
    matches = [surface for surface in SURFACES if surface.matches(value)]
    if len(matches) != 1:
        raise RuntimeError(
            f"{type(value).__name__} selects {len(matches)} surfaces: "
            + ", ".join(surface.id for surface in matches)
        )
    return matches[0]


def entry_surface(tag: str) -> Surface:
    """Return the one body-entry descriptor for a tag."""
    matches = [surface for surface in SURFACES if surface.tag == tag]
    if len(matches) != 1:
        raise RuntimeError(f"entry tag {tag} selects {len(matches)} surfaces")
    return matches[0]
