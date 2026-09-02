"""Surface selection, classification, fragment, and document freshness checks."""

from __future__ import annotations

from build import authoring as authoring_build
from build import docs as docs_build
from build.checks.fixtures import normalized
from build.docs import documents
from build.surfaces import (
    AUTHORABLE_MODELS,
    model_examples,
    slug,
    surface_example,
    surface_instance,
)
from oak.base import OakModel
from oak.base import OakModel
from oak.base import OakModel
from oak.base import OakModel
from oak.base import OakModel
from oak.parse.document import parse
from oak.parse.fragments import parse_fragment
from oak.parse.fragments import parse_fragment
from oak.parse.fragments import parse_fragment
from oak.parse.fragments import parse_fragment
from oak.parse.fragments import parse_fragment
from oak.render import render
from oak.rules.validation import RULES
from oak.surface.model import Surface
from oak.surface.model import Surface
from oak.surface.model import Surface
from oak.surface.model import Surface
from oak.surface.model import Surface
from oak.surface.registry import SURFACES, surface_for


def parse_surface(surface: Surface, text: str, *, grouping: str = "xml") -> OakModel:
    """Parse one rendered surface through the intentional fragment API."""
    return parse_fragment(surface.model, text, grouping=grouping, path=surface.id)


def parse_surface(surface: Surface, text: str, *, grouping: str = "xml") -> OakModel:
    """Parse one rendered surface through the intentional fragment API."""
    return parse_fragment(surface.model, text, grouping=grouping, path=surface.id)


def parse_surface(surface: Surface, text: str, *, grouping: str = "xml") -> OakModel:
    """Parse one rendered surface through the intentional fragment API."""
    return parse_fragment(surface.model, text, grouping=grouping, path=surface.id)


def parse_surface(surface: Surface, text: str, *, grouping: str = "xml") -> OakModel:
    """Parse one rendered surface through the intentional fragment API."""
    return parse_fragment(surface.model, text, grouping=grouping, path=surface.id)


def parse_surface(surface: Surface, text: str, *, grouping: str = "xml") -> OakModel:
    """Parse one rendered surface through the intentional fragment API."""
    return parse_fragment(surface.model, text, grouping=grouping, path=surface.id)


def validate_surfaces() -> None:
    """Validate every generated surface and its downstream document path."""
    expected_names = {
        slug(model.__name__) + ".md"
        for model in AUTHORABLE_MODELS
    }
    if set(documents()) != expected_names:
        raise RuntimeError("freshness gate 1 failed")

    for model in AUTHORABLE_MODELS:
        for instance in model_examples(model):
            surface_for(instance)

    for surface in SURFACES:
        rendered = [
            field.name
            for field in surface.fields
            if field.role == "rendered"
        ]
        if len(rendered) != len(set(rendered)):
            raise RuntimeError(
                f"freshness gate 3 failed for {surface.id}"
            )

    for surface in SURFACES:
        if {
            field.name
            for field in surface.fields
        } != set(surface.model.model_fields):
            raise RuntimeError(
                f"freshness gate 4 failed for {surface.id}"
            )

    for surface in SURFACES:
        surface_example(surface)

    for surface in SURFACES:
        original = surface_instance(surface)
        rebuilt = parse_surface(
            surface,
            surface_example(surface),
        )
        if normalized(original) != normalized(rebuilt):
            raise RuntimeError(
                f"freshness gate 6 failed for {surface.id}"
            )

    parsed_docs = {
        name: parse(text)
        for name, text in documents().items()
    }
    for name, node in parsed_docs.items():
        if render(node, grouping="xml") + "\n" != documents()[name]:
            raise RuntimeError(
                f"freshness gate 8 failed for {name}"
            )

    if not (
        docs_build.SURFACE_SOURCE
        is authoring_build.SURFACE_SOURCE
        is SURFACES
        and docs_build.RULE_SOURCE
        is authoring_build.RULE_SOURCE
        is RULES
    ):
        raise RuntimeError("freshness gate 9 failed")


__all__ = [
    "validate_surfaces",
]
