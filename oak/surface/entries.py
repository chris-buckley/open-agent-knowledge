"""Instruction, data, schema, trigger, interface, and node surfaces."""

from __future__ import annotations

from oak.node.model import Node
from oak.node.parts.constants import Constant
from oak.node.parts.instructions import Instruction
from oak.node.parts.interfaces import Interface
from oak.node.parts.schemas.model import Schema
from oak.node.parts.state import State
from oak.node.parts.triggers import Trigger
from oak.surface.model import _surface

ENTRY_SURFACES_BEFORE_PROCESSES = (
    _surface(
        "instruction",
        Instruction,
        "<BODY>",
        rendered=("body",),
        fixed=("part",),
        generated=("id",),
        part="instructions",
    ),
    _surface(
        "constant-inline",
        Constant,
        "<ID> AS <SCHEMA_ID>.<PLACEHOLDER>: <VALUE>",
        rendered=(
            "id",
            "schema_id",
            "placeholder",
            "value",
        ),
        fixed=(
            "part",
            "form",
        ),
        part="constants",
        when=(("form", "inline"),),
    ),
    _surface(
        "constant-text",
        Constant,
        "<ID> AS <SCHEMA_ID>.<PLACEHOLDER>: TEXT<<\n<VALUE>\n>>",
        rendered=(
            "id",
            "schema_id",
            "placeholder",
            "value",
        ),
        fixed=(
            "part",
            "form",
        ),
        part="constants",
        when=(("form", "text"),),
    ),
    _surface(
        "constant-json",
        Constant,
        "<ID> AS <SCHEMA_ID>.<PLACEHOLDER>: JSON<<\n<VALUE>\n>>",
        rendered=(
            "id",
            "schema_id",
            "placeholder",
            "value",
        ),
        fixed=(
            "part",
            "form",
        ),
        part="constants",
        when=(("form", "json"),),
    ),
    _surface(
        "constant-csv",
        Constant,
        "<ID> AS <SCHEMA_ID>.<PLACEHOLDER>: CSV<<\n<VALUE>\n>>",
        rendered=(
            "id",
            "schema_id",
            "placeholder",
            "value",
        ),
        fixed=(
            "part",
            "form",
        ),
        part="constants",
        when=(("form", "csv"),),
    ),
    _surface(
        "constant-yaml",
        Constant,
        "<ID> AS <SCHEMA_ID>.<PLACEHOLDER>: YAML<<\n<VALUE>\n>>",
        rendered=(
            "id",
            "schema_id",
            "placeholder",
            "value",
        ),
        fixed=(
            "part",
            "form",
        ),
        part="constants",
        when=(("form", "yaml"),),
    ),
    _surface(
        "schema",
        Schema,
        '<schema id="<ID>" name="<NAME>" purpose="<PURPOSE>">\n<TEMPLATE>\n\nWHERE:\n<WHERE>\n</schema>',
        rendered=(
            "id",
            "name",
            "purpose",
            "template",
            "where",
        ),
        fixed=("part",),
        part="schemas",
        tag="schema",
    ),
    _surface(
        "state",
        State,
        "<ID> AS <SCHEMA_ID>.<PLACEHOLDER>: <VALUE>",
        rendered=(
            "id",
            "schema_id",
            "placeholder",
            "value",
        ),
        fixed=("part",),
        part="state",
    ),
)

ENTRY_SURFACES_AFTER_PROCESSES = (
    _surface(
        "trigger",
        Trigger,
        (
            "trigger.<ID>.event := <EVENT>\n"
            "trigger.<ID>.source := <SOURCE>\n"
            "trigger.<ID>.guard := <GUARD>\n"
            "trigger.<ID>.process := <PROCESS>\n"
            "trigger.<ID>.seed.<SEED>"
        ),
        rendered=(
            "id",
            "event",
            "source",
            "guard",
            "process",
            "seed",
        ),
        fixed=("part",),
        part="triggers",
    ),
    _surface(
        "interface",
        Interface,
        '<interface id="<ID>" direction="<DIRECTION>" schema="<SCHEMA_ID>">\n<DESCRIPTION>\n</interface>',
        rendered=(
            "id",
            "direction",
            "schema_id",
            "description",
        ),
        fixed=("part",),
        part="interfaces",
        tag="interface",
    ),
    _surface(
        "node",
        Node,
        (
            "<instructions>\n<INSTRUCTIONS>\n</instructions>\n\n"
            "<constants>\n<CONSTANTS>\n</constants>\n\n"
            "<schemas>\n<SCHEMAS>\n</schemas>\n\n"
            "<state>\n<STATE>\n</state>\n\n"
            "<triggers>\n<TRIGGERS>\n</triggers>\n\n"
            "<processes>\n<PROCESSES>\n</processes>\n\n"
            "<interfaces>\n<INTERFACES>\n</interfaces>"
        ),
        rendered=(
            "instructions",
            "constants",
            "schemas",
            "state",
            "triggers",
            "processes",
            "interfaces",
        ),
    ),
)

__all__ = [
    "ENTRY_SURFACES_AFTER_PROCESSES",
    "ENTRY_SURFACES_BEFORE_PROCESSES",
]
