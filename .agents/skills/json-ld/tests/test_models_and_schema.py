from __future__ import annotations
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError

from models import (
    ApplicationSystem,
    SystemProfileSource,
    application_to_source,
    source_to_application,
)

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_framed_profile_validates_with_pydantic() -> None:
    profile = load("examples/framed/domain-extension.framed.jsonld")
    typed = SystemProfileSource.model_validate(profile, context={"external_ids": {"sys:base"}})
    assert typed.id == "sys:domain"
    assert typed.nodes[1].type == "Adaptor"


def test_source_and_application_models_convert_both_directions() -> None:
    profile = load("examples/framed/domain-extension.framed.jsonld")
    typed = SystemProfileSource.model_validate(profile, context={"external_ids": {"sys:base"}})
    application = source_to_application(typed)
    rebuilt = application_to_source(application)
    assert rebuilt.model_dump(mode="json", by_alias=True, exclude_none=True) == typed.model_dump(
        mode="json", by_alias=True, exclude_none=True
    )


def test_application_model_is_clean_of_jsonld_keywords() -> None:
    application = ApplicationSystem.model_validate(load("examples/pydantic/application-system.json"))
    dumped = application.model_dump(mode="json")
    assert "@context" not in dumped
    assert "@id" not in dumped


def test_json_schema_is_valid_draft_2020_12() -> None:
    schema = load("examples/pydantic/application-profile.schema.json")
    Draft202012Validator.check_schema(schema)


def test_json_schema_accepts_valid_profile() -> None:
    schema = load("examples/pydantic/application-profile.schema.json")
    profile = load("examples/framed/domain-extension.framed.jsonld")
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(profile)


def test_json_schema_accepts_structural_missing_target() -> None:
    schema = load("examples/pydantic/application-profile.schema.json")
    profile = load("examples/invalid/missing-target.framed.jsonld")
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(profile)


def test_pydantic_graph_check_rejects_missing_target() -> None:
    profile = load("examples/invalid/missing-target.framed.jsonld")
    with pytest.raises(ValidationError, match="graph reference targets are absent"):
        SystemProfileSource.model_validate(profile)
