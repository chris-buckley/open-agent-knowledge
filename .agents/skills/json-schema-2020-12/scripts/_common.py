#!/usr/bin/env python3
"""Shared, offline-safe helpers for the JSON Schema skill scripts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag, urljoin, urlsplit

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import FormatError, SchemaError, ValidationError
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable
from referencing.jsonschema import DRAFT202012

DRAFT_2020_12 = "https://json-schema.org/draft/2020-12/schema"
JsonValue = Any


class ToolError(RuntimeError):
    """A deterministic user-facing tool failure."""


class DuplicateKeyError(ValueError):
    """An object used the same JSON member name more than once."""

    def __init__(self, key: str) -> None:
        super().__init__(key)
        self.key = key


def reject_duplicate_keys(pairs: list[tuple[str, JsonValue]]) -> dict[str, JsonValue]:
    result: dict[str, JsonValue] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(key)
        result[key] = value
    return result


@dataclass(frozen=True)
class LoadedResource:
    uri: str
    path: Path
    contents: JsonValue


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def load_json(path: Path) -> JsonValue:
    """Load one UTF-8 JSON document and report its exact source location."""

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ToolError(f"cannot read {path}: {exc}") from exc
    try:
        return json.loads(text, object_pairs_hook=reject_duplicate_keys)
    except DuplicateKeyError as exc:
        raise ToolError(f"duplicate JSON object key {exc.key!r} in {path}") from exc
    except json.JSONDecodeError as exc:
        raise ToolError(
            f"invalid JSON in {path}:{exc.lineno}:{exc.colno}: {exc.msg}"
        ) from exc


def require_draft_2020_12(schema: JsonValue, path: Path) -> Mapping[str, JsonValue]:
    """Reject implicit, older, and unsupported top-level dialects."""

    if not isinstance(schema, dict):
        raise ToolError(
            f"{path}: a standalone schema must be an object with an explicit $schema; "
            "boolean schemas can be used as subschemas"
        )
    actual = schema.get("$schema")
    if actual != DRAFT_2020_12:
        shown = "missing" if actual is None else repr(actual)
        raise ToolError(
            f"{path}: expected $schema {DRAFT_2020_12!r}; found {shown}"
        )
    return schema


def schema_id(schema: JsonValue) -> str | None:
    if isinstance(schema, dict):
        value = schema.get("$id")
        if isinstance(value, str) and value:
            return value
    return None


def require_absolute_resource_uri(uri: str, *, source: Path | str) -> None:
    checker = FormatChecker()
    try:
        checker.check(uri, "uri")
    except FormatError as exc:
        raise ToolError(f"{source}: registry key {uri!r} is not a valid absolute URI") from exc
    parsed = urlsplit(uri)
    if not parsed.scheme:
        raise ToolError(f"{source}: registry key {uri!r} must be an absolute URI")
    if parsed.fragment:
        raise ToolError(f"{source}: registry key {uri!r} must not contain a fragment")


def parse_resource_argument(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("expected URI=PATH")
    uri, raw_path = value.split("=", 1)
    if not uri or not raw_path:
        raise argparse.ArgumentTypeError("expected non-empty URI=PATH")
    return uri, Path(raw_path)


def load_registry_manifest(path: Path) -> list[LoadedResource]:
    raw = load_json(path)
    if not isinstance(raw, dict):
        raise ToolError(f"{path}: registry manifest must be a JSON object of URI to path")
    base = path.resolve().parent
    resources: list[LoadedResource] = []
    for uri, relative in sorted(raw.items()):
        if not isinstance(uri, str) or not uri:
            raise ToolError(f"{path}: registry URI keys must be non-empty strings")
        require_absolute_resource_uri(uri, source=path)
        if not isinstance(relative, str) or not relative:
            raise ToolError(f"{path}: registry path for {uri!r} must be a non-empty string")
        relative_path = Path(relative)
        if relative_path.is_absolute():
            raise ToolError(
                f"{path}: registry path for {uri!r} must be relative; "
                "use --resource for an explicit external path"
            )
        resource_path = (base / relative_path).resolve()
        try:
            resource_path.relative_to(base)
        except ValueError as exc:
            raise ToolError(
                f"{path}: registry path for {uri!r} escapes the manifest directory; "
                "use --resource for an explicit external path"
            ) from exc
        contents = load_json(resource_path)
        schema = require_draft_2020_12(contents, resource_path)
        check_schema(schema, resource_path)
        declared = schema_id(schema)
        if declared is not None and declared != uri:
            raise ToolError(
                f"{path}: key {uri!r} does not match $id {declared!r} in {resource_path}"
            )
        resources.append(LoadedResource(uri=uri, path=resource_path, contents=contents))
    return resources


def load_explicit_resources(values: Sequence[tuple[str, Path]]) -> list[LoadedResource]:
    resources: list[LoadedResource] = []
    for uri, raw_path in values:
        require_absolute_resource_uri(uri, source="--resource")
        path = raw_path.resolve()
        contents = load_json(path)
        schema = require_draft_2020_12(contents, path)
        check_schema(schema, path)
        declared = schema_id(schema)
        if declared is not None and declared != uri:
            raise ToolError(
                f"resource key {uri!r} does not match $id {declared!r} in {path}"
            )
        resources.append(LoadedResource(uri=uri, path=path, contents=contents))
    return resources


def build_registry(
    *,
    root_schema: JsonValue | None = None,
    root_path: Path | None = None,
    registry_manifest: Path | None = None,
    explicit_resources: Sequence[tuple[str, Path]] = (),
) -> tuple[Registry[JsonValue], tuple[LoadedResource, ...]]:
    """Build an in-memory registry with no network or filesystem retriever."""

    loaded: list[LoadedResource] = []
    if registry_manifest is not None:
        loaded.extend(load_registry_manifest(registry_manifest.resolve()))
    loaded.extend(load_explicit_resources(explicit_resources))
    if root_schema is not None:
        root_uri = schema_id(root_schema)
        if root_uri is None and root_path is not None:
            root_uri = root_path.resolve().as_uri()
        if root_uri:
            loaded.append(
                LoadedResource(
                    uri=root_uri,
                    path=(root_path or Path("<memory>")),
                    contents=root_schema,
                )
            )

    by_uri: dict[str, LoadedResource] = {}
    for item in loaded:
        previous = by_uri.get(item.uri)
        if previous is not None and previous.contents != item.contents:
            raise ToolError(
                f"duplicate registry URI {item.uri!r} maps to both "
                f"{previous.path} and {item.path}"
            )
        by_uri[item.uri] = item

    registry: Registry[JsonValue] = Registry()
    for uri in sorted(by_uri):
        item = by_uri[uri]
        resource = Resource.from_contents(
            item.contents,
            default_specification=DRAFT202012,
        )
        registry = registry.with_resource(uri, resource)
    # Crawl embedded resources and anchors before validation. The registry remains
    # immutable and has no retrieve callback, so missing resources cannot trigger I/O.
    registry = registry.crawl()
    return registry, tuple(by_uri[uri] for uri in sorted(by_uri))


def escape_pointer_token(token: object) -> str:
    return str(token).replace("~", "~0").replace("/", "~1")


def json_pointer(parts: Iterable[object]) -> str:
    tokens = [escape_pointer_token(part) for part in parts]
    return "" if not tokens else "/" + "/".join(tokens)


def sorted_validation_errors(
    validator: Draft202012Validator,
    instance: JsonValue,
) -> list[ValidationError]:
    return sorted(
        validator.iter_errors(instance),
        key=lambda error: (
            json_pointer(error.absolute_path),
            json_pointer(error.absolute_schema_path),
            error.validator or "",
            error.message,
        ),
    )


def error_record(error: ValidationError, *, depth: int = 0) -> dict[str, JsonValue]:
    return {
        "depth": depth,
        "instancePath": json_pointer(error.absolute_path),
        "schemaPath": json_pointer(error.absolute_schema_path),
        "keyword": error.validator,
        "message": error.message,
    }


def iter_error_records(error: ValidationError, *, depth: int = 0) -> Iterator[dict[str, JsonValue]]:
    yield error_record(error, depth=depth)
    children = sorted(
        error.context,
        key=lambda child: (
            json_pointer(child.absolute_path),
            json_pointer(child.absolute_schema_path),
            child.validator or "",
            child.message,
        ),
    )
    for child in children:
        yield from iter_error_records(child, depth=depth + 1)


def render_error_text(error: ValidationError, *, document: Path) -> list[str]:
    lines: list[str] = []
    for record in iter_error_records(error):
        indent = "  " * int(record["depth"])
        instance_path = record["instancePath"] or "<root>"
        schema_path = record["schemaPath"] or "<root>"
        keyword = record["keyword"] or "<unknown>"
        lines.append(
            f"{indent}{document} instance {instance_path}; schema {schema_path}; "
            f"keyword {keyword}: {record['message']}"
        )
    return lines


_ANCHOR_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9._-]*$")


def _check_known_format(value: str, format_name: str, *, path: Path, pointer: tuple[object, ...]) -> None:
    checker = FormatChecker()
    try:
        checker.check(value, format_name)
    except FormatError as exc:
        location = json_pointer(pointer) or "<root>"
        raise ToolError(
            f"invalid Draft 2020-12 schema {path}; schema {location}: "
            f"{value!r} is not a valid {format_name}"
        ) from exc


def check_core_keyword_syntax(schema: Mapping[str, JsonValue], path: Path) -> None:
    """Assert Core URI and anchor requirements that meta-schema format annotations do not enforce."""

    anchors_by_resource: dict[str, dict[str, str]] = {}

    def walk(
        current: JsonValue,
        *,
        pointer: tuple[object, ...],
        base_uri: str,
        resource_uri: str,
    ) -> None:
        if not isinstance(current, dict):
            return

        next_base = base_uri
        next_resource = resource_uri
        identifier = current.get("$id")
        if isinstance(identifier, str):
            _check_known_format(
                identifier,
                "uri-reference",
                path=path,
                pointer=pointer + ("$id",),
            )
            resolved = urljoin(base_uri, identifier)
            if not urlsplit(resolved).scheme:
                location = json_pointer(pointer + ("$id",)) or "<root>"
                raise ToolError(
                    f"invalid Draft 2020-12 schema {path}; schema {location}: "
                    f"$id {identifier!r} does not resolve to an absolute URI"
                )
            if urlsplit(resolved).fragment:
                location = json_pointer(pointer + ("$id",)) or "<root>"
                raise ToolError(
                    f"invalid Draft 2020-12 schema {path}; schema {location}: "
                    "$id must not contain a non-empty fragment"
                )
            next_base = resolved
            next_resource = urldefrag(resolved)[0]

        dialect = current.get("$schema")
        if isinstance(dialect, str):
            _check_known_format(
                dialect,
                "uri",
                path=path,
                pointer=pointer + ("$schema",),
            )
            if dialect != DRAFT_2020_12:
                location = json_pointer(pointer + ("$schema",)) or "<root>"
                raise ToolError(
                    f"invalid Draft 2020-12 schema {path}; schema {location}: "
                    f"unsupported embedded dialect {dialect!r}"
                )

        for keyword in ("$ref", "$dynamicRef"):
            value = current.get(keyword)
            if isinstance(value, str):
                _check_known_format(
                    value,
                    "uri-reference",
                    path=path,
                    pointer=pointer + (keyword,),
                )

        resource_anchors = anchors_by_resource.setdefault(next_resource, {})
        for keyword in ("$anchor", "$dynamicAnchor"):
            value = current.get(keyword)
            if not isinstance(value, str):
                continue
            location = json_pointer(pointer + (keyword,)) or "<root>"
            if not _ANCHOR_PATTERN.fullmatch(value):
                raise ToolError(
                    f"invalid Draft 2020-12 schema {path}; schema {location}: "
                    f"{keyword} {value!r} is not a valid plain-name anchor"
                )
            previous = resource_anchors.get(value)
            if previous is not None and previous != location:
                raise ToolError(
                    f"invalid Draft 2020-12 schema {path}; schema {location}: "
                    f"anchor {value!r} duplicates {previous} in resource {next_resource}"
                )
            resource_anchors[value] = location

        for keyword in sorted(_SCHEMA_SINGLE):
            child = current.get(keyword)
            if isinstance(child, (dict, bool)):
                walk(
                    child,
                    pointer=pointer + (keyword,),
                    base_uri=next_base,
                    resource_uri=next_resource,
                )
        for keyword in sorted(_SCHEMA_ARRAY):
            children = current.get(keyword)
            if isinstance(children, list):
                for index, child in enumerate(children):
                    if isinstance(child, (dict, bool)):
                        walk(
                            child,
                            pointer=pointer + (keyword, index),
                            base_uri=next_base,
                            resource_uri=next_resource,
                        )
        for keyword in sorted(_SCHEMA_MAP):
            children = current.get(keyword)
            if isinstance(children, dict):
                for name in sorted(children):
                    child = children[name]
                    if isinstance(child, (dict, bool)):
                        walk(
                            child,
                            pointer=pointer + (keyword, name),
                            base_uri=next_base,
                            resource_uri=next_resource,
                        )

    initial = path.resolve().as_uri()
    walk(schema, pointer=(), base_uri=initial, resource_uri=urldefrag(initial)[0])


def check_schema(schema: Mapping[str, JsonValue], path: Path) -> None:
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        instance_path = json_pointer(exc.absolute_path) or "<root>"
        schema_path = json_pointer(exc.absolute_schema_path) or "<root>"
        raise ToolError(
            f"invalid Draft 2020-12 schema {path}; instance {instance_path}; "
            f"meta-schema {schema_path}: {exc.message}"
        ) from exc
    check_core_keyword_syntax(schema, path)


_SCHEMA_SINGLE = {
    "additionalProperties",
    "contains",
    "contentSchema",
    "else",
    "if",
    "items",
    "not",
    "propertyNames",
    "then",
    "unevaluatedItems",
    "unevaluatedProperties",
}
_SCHEMA_ARRAY = {"allOf", "anyOf", "oneOf", "prefixItems"}
_SCHEMA_MAP = {"$defs", "dependentSchemas", "patternProperties", "properties"}


def iter_subschemas(schema: JsonValue, pointer: tuple[object, ...] = ()) -> Iterator[tuple[tuple[object, ...], JsonValue]]:
    """Yield schema positions without treating examples or defaults as schemas."""

    if not isinstance(schema, dict):
        return
    yield pointer, schema
    for keyword in sorted(_SCHEMA_SINGLE):
        child = schema.get(keyword)
        if isinstance(child, (dict, bool)):
            yield from iter_subschemas(child, pointer + (keyword,))
    for keyword in sorted(_SCHEMA_ARRAY):
        children = schema.get(keyword)
        if isinstance(children, list):
            for index, child in enumerate(children):
                if isinstance(child, (dict, bool)):
                    yield from iter_subschemas(child, pointer + (keyword, index))
    for keyword in sorted(_SCHEMA_MAP):
        children = schema.get(keyword)
        if isinstance(children, dict):
            for name in sorted(children):
                child = children[name]
                if isinstance(child, (dict, bool)):
                    yield from iter_subschemas(child, pointer + (keyword, name))


def used_formats(schemas: Iterable[JsonValue]) -> tuple[str, ...]:
    names: set[str] = set()
    for schema in schemas:
        for _, subschema in iter_subschemas(schema):
            if isinstance(subschema, dict):
                value = subschema.get("format")
                if isinstance(value, str):
                    names.add(value)
    return tuple(sorted(names))


def known_format_names() -> frozenset[str]:
    checker = FormatChecker()
    return frozenset(checker.checkers)


def format_checker_for_policy(
    policy: str,
    *,
    schemas: Iterable[JsonValue],
) -> tuple[FormatChecker | None, tuple[str, ...]]:
    names = used_formats(schemas)
    if policy == "annotation":
        return None, names
    if policy != "assert-known":
        raise ToolError(f"unsupported format policy {policy!r}")
    unknown = sorted(set(names) - set(known_format_names()))
    if unknown:
        raise ToolError(
            "format assertion requested, but no checker is registered for: "
            + ", ".join(unknown)
        )
    return FormatChecker(), names


def add_registry_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--registry",
        type=Path,
        help="JSON object mapping canonical schema URIs to local paths; paths are relative to the manifest",
    )
    parser.add_argument(
        "--resource",
        action="append",
        default=[],
        type=parse_resource_argument,
        metavar="URI=PATH",
        help="add one local schema resource; may be repeated",
    )


def resolve_uri(base_uri: str, reference: str) -> str:
    """Resolve a URI reference using RFC 3986 semantics exposed by urljoin."""

    return urljoin(base_uri, reference)


def reference_document_uri(base_uri: str, reference: str) -> str:
    absolute = resolve_uri(base_uri, reference)
    document_uri, _ = urldefrag(absolute)
    return document_uri


def catch_reference_error(exc: BaseException) -> ToolError | None:
    """Turn referencing failures, including jsonschema wrappers, into stable text."""

    current: BaseException | None = exc
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, Unresolvable):
            return ToolError(f"unresolvable schema reference: {current}")
        current = current.__cause__ or current.__context__
    name = type(exc).__name__.lower()
    if "referenc" in name or "resolv" in name:
        return ToolError(f"schema reference failure: {exc}")
    return None


def emit_json(value: JsonValue) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))
