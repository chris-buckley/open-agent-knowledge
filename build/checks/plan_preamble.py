"""Validate planning metadata without treating it as executable authority."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
import re
from types import MappingProxyType

import yaml
from yaml.nodes import MappingNode, ScalarNode

from examples.schemas.smeac_plan import INTENT_HEADING, PlanClassification


@dataclass(frozen=True, slots=True)
class PlanOpening:
    metadata: Mapping[str, str | datetime]
    body: str


def read_plan_opening(text: str) -> PlanOpening:
    """Read one leading YAML mapping, rejecting duplicate keys and compound values."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        raise ValueError("plan needs leading YAML frontmatter")
    end = next((i for i, line in enumerate(lines[1:], 1) if line.rstrip("\r\n") == "---"), None)
    if end is None:
        raise ValueError("plan frontmatter needs a closing delimiter")
    header = "".join(lines[1:end])
    try:
        node = yaml.compose(header, Loader=yaml.SafeLoader)
        _require_metadata_mapping(node)
        metadata = yaml.safe_load(header)
    except yaml.YAMLError as error:
        raise ValueError("plan frontmatter is malformed YAML") from error
    if any(not isinstance(value, (str, datetime)) for value in metadata.values()):
        raise ValueError("plan metadata needs string scalars, except a prepared datetime")
    if any(isinstance(value, datetime) and key != "prepared" for key, value in metadata.items()):
        raise ValueError("quote date-like metadata to preserve its string value")
    return PlanOpening(MappingProxyType(metadata), "".join(lines[end + 1:]))


def _require_metadata_mapping(node: object) -> None:
    if not isinstance(node, MappingNode) or not node.value:
        raise ValueError("plan frontmatter needs one nonempty mapping")
    names: set[str] = set()
    for key, value in node.value:
        if not isinstance(key, ScalarNode) or key.tag != "tag:yaml.org,2002:str" or not key.value.strip():
            raise ValueError("plan metadata keys must be nonempty strings without merges")
        if key.value in names:
            raise ValueError(f"duplicate plan metadata key: {key.value}")
        names.add(key.value)
        if not isinstance(value, ScalarNode):
            raise ValueError("plan metadata values must be scalars")


def validate_plan_opening(text: str, template: str) -> PlanOpening:
    """Check decoded metadata and the Intent-first body against its source template."""
    opening = read_plan_opening(text)
    expected = read_plan_opening(template).metadata
    missing = expected.keys() - opening.metadata.keys()
    if missing:
        raise ValueError(f"plan metadata is missing required fields: {sorted(missing)}")
    if any(not str(value).strip() for value in opening.metadata.values()):
        raise ValueError("plan metadata fields must be populated or omitted")
    slots = set(re.findall(r"<([A-Z][A-Z0-9_]*)>", template))
    if slots.intersection(re.findall(r"<([A-Z][A-Z0-9_]*)>", "\n".join(map(str, opening.metadata.values())))):
        raise ValueError("plan metadata retains an unfilled SMEAC placeholder")
    if not isinstance(opening.metadata["title"], str):
        raise ValueError("plan title must be a string")
    _require_prepared_datetime(opening.metadata["prepared"])
    try:
        PlanClassification(opening.metadata["classification"])
    except ValueError as error:
        raise ValueError("plan classification differs from the SMEAC choices") from error
    first = next((line for line in opening.body.splitlines() if line.strip()), "")
    if first != INTENT_HEADING:
        raise ValueError("plan body must start with Intent, without a title or metadata preface")
    return opening


def _require_prepared_datetime(prepared: str | datetime) -> None:
    try:
        instant = datetime.fromisoformat(prepared) if isinstance(prepared, str) else prepared
    except ValueError as error:
        raise ValueError("plan prepared field needs an ISO datetime") from error
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("plan prepared datetime needs an explicit timezone")
