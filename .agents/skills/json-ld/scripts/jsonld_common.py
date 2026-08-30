#!/usr/bin/env python3
"""Shared safe I/O, context loading, processor adapters, and CLI utilities.

PyLD is the default standards processor.  The bundled ``profile`` engine is a
bounded deterministic implementation for the included examples and smoke tests;
it is not a general JSON-LD conformance implementation.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Callable, Iterable, Mapping
from urllib.parse import urlparse

MAX_INPUT_BYTES = 5 * 1024 * 1024
MAX_OUTPUT_BYTES = 20 * 1024 * 1024
MAX_JSON_DEPTH = 128
MAX_CONTEXT_DEPTH = 16
MAX_CONTEXT_URLS = 32


class JsonLdSkillError(Exception):
    """Structured operational or processing failure."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        path: str | None = None,
        identifier: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.path = path
        self.identifier = identifier
        self.details = dict(details or {})

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.path is not None:
            result["path"] = self.path
        if self.identifier is not None:
            result["identifier"] = self.identifier
        if self.details:
            result["details"] = self.details
        return result


class DuplicateKeyError(JsonLdSkillError):
    pass


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(
                "duplicate_key",
                f"Duplicate JSON object member {key!r}",
                path=f"$.{key}",
            )
        result[key] = value
    return result


def _json_depth(value: Any) -> int:
    maximum = 0
    stack: list[tuple[Any, int]] = [(value, 1)]
    while stack:
        current, depth = stack.pop()
        maximum = max(maximum, depth)
        if isinstance(current, dict):
            stack.extend((item, depth + 1) for item in current.values())
        elif isinstance(current, list):
            stack.extend((item, depth + 1) for item in current)
    return maximum


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def load_json_path(
    path: str | Path,
    *,
    max_bytes: int = MAX_INPUT_BYTES,
    max_depth: int = MAX_JSON_DEPTH,
) -> tuple[Any, dict[str, Any]]:
    file_path = Path(path).expanduser().resolve()
    try:
        stat = file_path.stat()
    except OSError as exc:
        raise JsonLdSkillError(
            "input_unavailable", f"Cannot read {file_path}: {exc}", path=str(file_path)
        ) from exc
    if not file_path.is_file():
        raise JsonLdSkillError(
            "input_not_file", f"Input is not a file: {file_path}", path=str(file_path)
        )
    if stat.st_size > max_bytes:
        raise JsonLdSkillError(
            "input_too_large",
            f"Input exceeds {max_bytes} bytes",
            path=str(file_path),
            details={"actual_bytes": stat.st_size, "maximum_bytes": max_bytes},
        )
    try:
        raw = file_path.read_bytes()
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise JsonLdSkillError(
            "invalid_utf8", f"Input is not UTF-8: {exc}", path=str(file_path)
        ) from exc
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicate_pairs)
    except JsonLdSkillError:
        raise
    except json.JSONDecodeError as exc:
        raise JsonLdSkillError(
            "json_syntax_error",
            exc.msg,
            path=f"{file_path}:{exc.lineno}:{exc.colno}",
            details={"line": exc.lineno, "column": exc.colno, "offset": exc.pos},
        ) from exc
    depth = _json_depth(value)
    if depth > max_depth:
        raise JsonLdSkillError(
            "json_depth_exceeded",
            f"JSON nesting depth {depth} exceeds {max_depth}",
            path=str(file_path),
            details={"actual_depth": depth, "maximum_depth": max_depth},
        )
    provenance = {
        "source_path": str(file_path),
        "source_bytes": len(raw),
        "source_sha256": sha256_bytes(raw),
    }
    return value, provenance


@dataclass(frozen=True)
class RegistryEntry:
    iri: str
    path: Path
    sha256: str
    content_type: str


class LocalDocumentRegistry:
    """Exact-match, integrity-checked, offline document registry."""

    def __init__(
        self,
        registry_path: str | Path | None,
        *,
        max_document_bytes: int = MAX_INPUT_BYTES,
    ) -> None:
        self.registry_path = (
            Path(registry_path).expanduser().resolve() if registry_path else None
        )
        self.max_document_bytes = max_document_bytes
        self._entries: dict[str, RegistryEntry] = {}
        self._cache: dict[str, Any] = {}
        if self.registry_path is not None:
            self._load_registry()

    def _load_registry(self) -> None:
        assert self.registry_path is not None
        payload, _ = load_json_path(self.registry_path, max_bytes=self.max_document_bytes)
        if not isinstance(payload, dict) or payload.get("version") != 1:
            raise JsonLdSkillError(
                "invalid_registry",
                "Context registry must be an object with version 1",
                path=str(self.registry_path),
            )
        documents = payload.get("documents")
        if not isinstance(documents, dict):
            raise JsonLdSkillError(
                "invalid_registry",
                "Context registry documents must be an object",
                path=str(self.registry_path),
            )
        root = self.registry_path.parent
        for iri, spec in documents.items():
            if not isinstance(iri, str) or not isinstance(spec, dict):
                raise JsonLdSkillError(
                    "invalid_registry",
                    "Each registry entry must map an IRI to an object",
                    path=str(self.registry_path),
                )
            parsed = urlparse(iri)
            if parsed.scheme != "https":
                raise JsonLdSkillError(
                    "registry_scheme_rejected",
                    f"Registry IRI must use https: {iri}",
                    identifier=iri,
                )
            relative = spec.get("path")
            digest = spec.get("sha256")
            content_type = spec.get("content_type")
            if not all(isinstance(x, str) and x for x in (relative, digest, content_type)):
                raise JsonLdSkillError(
                    "invalid_registry_entry",
                    f"Registry entry is incomplete: {iri}",
                    identifier=iri,
                )
            candidate = (root / relative).resolve()
            try:
                candidate.relative_to(root.resolve())
            except ValueError as exc:
                raise JsonLdSkillError(
                    "registry_path_escape",
                    f"Registry path escapes its directory: {relative}",
                    identifier=iri,
                ) from exc
            self._entries[iri] = RegistryEntry(
                iri=iri,
                path=candidate,
                sha256=digest.lower(),
                content_type=content_type.lower(),
            )

    @property
    def iris(self) -> tuple[str, ...]:
        return tuple(sorted(self._entries))

    def load(self, iri: str) -> Any:
        parsed = urlparse(iri)
        if parsed.scheme in {"file", "data", "ftp", "gopher"}:
            raise JsonLdSkillError(
                "remote_scheme_rejected",
                f"Scheme {parsed.scheme!r} is not permitted",
                identifier=iri,
            )
        if iri not in self._entries:
            raise JsonLdSkillError(
                "remote_context_rejected",
                "Remote document is not pinned in the local registry",
                identifier=iri,
                details={"allowed": list(self.iris)},
            )
        if iri in self._cache:
            return self._cache[iri]
        entry = self._entries[iri]
        try:
            raw = entry.path.read_bytes()
        except OSError as exc:
            raise JsonLdSkillError(
                "registered_document_unavailable",
                f"Cannot read pinned document: {exc}",
                path=str(entry.path),
                identifier=iri,
            ) from exc
        if len(raw) > self.max_document_bytes:
            raise JsonLdSkillError(
                "registered_document_too_large",
                f"Pinned document exceeds {self.max_document_bytes} bytes",
                path=str(entry.path),
                identifier=iri,
            )
        actual = sha256_bytes(raw)
        if actual != entry.sha256:
            raise JsonLdSkillError(
                "integrity_mismatch",
                "Pinned document SHA-256 does not match the registry",
                path=str(entry.path),
                identifier=iri,
                details={"actual_sha256": actual, "expected_sha256": entry.sha256},
            )
        if entry.content_type not in {
            "application/ld+json",
            "application/json",
        }:
            raise JsonLdSkillError(
                "content_type_rejected",
                f"Pinned content type is not JSON-LD compatible: {entry.content_type}",
                path=str(entry.path),
                identifier=iri,
            )
        try:
            document = json.loads(
                raw.decode("utf-8"), object_pairs_hook=_reject_duplicate_pairs
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise JsonLdSkillError(
                "registered_document_invalid_json",
                f"Pinned document is not valid UTF-8 JSON: {exc}",
                path=str(entry.path),
                identifier=iri,
            ) from exc
        self._cache[iri] = document
        return document

    def pyld_loader(self) -> Callable[..., dict[str, Any]]:
        def loader(url: str, options: Any = None) -> dict[str, Any]:
            del options
            document = self.load(url)
            entry = self._entries[url]
            return {
                "contextUrl": None,
                "documentUrl": url,
                "document": document,
                "contentType": entry.content_type,
            }

        return loader


def _iter_context_references(value: Any) -> Iterable[str]:
    if value is None:
        return
    if isinstance(value, str):
        yield value
        return
    if isinstance(value, list):
        for item in value:
            yield from _iter_context_references(item)
        return
    if isinstance(value, dict):
        imported = value.get("@import")
        if isinstance(imported, str):
            yield imported
        for definition in value.values():
            if isinstance(definition, dict) and "@context" in definition:
                yield from _iter_context_references(definition["@context"])


def preflight_contexts(
    document: Any,
    registry: LocalDocumentRegistry,
    *,
    max_context_depth: int = MAX_CONTEXT_DEPTH,
    max_context_urls: int = MAX_CONTEXT_URLS,
) -> dict[str, Any]:
    """Resolve every remote context through the registry before processing."""

    seen: set[str] = set()
    stack: list[str] = []

    def visit_context(context: Any, depth: int, *, imported: bool = False) -> None:
        if depth > max_context_depth:
            raise JsonLdSkillError(
                "context_depth_exceeded",
                f"Context depth exceeds {max_context_depth}",
                details={"context_stack": list(stack)},
            )
        if imported and isinstance(context, dict) and "@import" in context:
            raise JsonLdSkillError(
                "invalid_context_import",
                "An imported context cannot contain another @import entry",
                details={"context_stack": list(stack)},
            )
        imported_iri = context.get("@import") if isinstance(context, dict) else None
        for iri in _iter_context_references(context):
            parsed = urlparse(iri)
            if not parsed.scheme:
                continue
            if iri in stack:
                raise JsonLdSkillError(
                    "cyclic_context",
                    "Cyclic remote context or @import detected",
                    identifier=iri,
                    details={"cycle": stack + [iri]},
                )
            if iri in seen:
                continue
            if len(seen) >= max_context_urls:
                raise JsonLdSkillError(
                    "context_url_limit_exceeded",
                    f"More than {max_context_urls} context URLs were encountered",
                    identifier=iri,
                )
            stack.append(iri)
            loaded = registry.load(iri)
            seen.add(iri)
            nested = loaded.get("@context") if isinstance(loaded, dict) else None
            visit_context(nested, depth + 1, imported=(iri == imported_iri))
            stack.pop()

    def walk(value: Any, depth: int = 0) -> None:
        if isinstance(value, dict):
            if "@context" in value:
                visit_context(value["@context"], depth + 1)
            for child in value.values():
                walk(child, depth)
        elif isinstance(value, list):
            for child in value:
                walk(child, depth)

    walk(document)
    return {"context_count": len(seen), "context_iris": sorted(seen)}


def load_processor(engine: str, registry: LocalDocumentRegistry):
    if engine == "profile":
        try:
            from profile_engine import ProfileJsonLdProcessor
        except ImportError:  # package execution
            from .profile_engine import ProfileJsonLdProcessor
        return ProfileJsonLdProcessor(registry)
    if engine != "pyld":
        raise JsonLdSkillError("unknown_engine", f"Unknown processor engine: {engine}")
    try:
        from pyld import jsonld  # type: ignore
    except ImportError as exc:
        raise JsonLdSkillError(
            "processor_unavailable",
            "PyLD is not installed. Install PyLD==3.1.0 or select --engine profile "
            "for the bounded included-example processor.",
            details={"required_distribution": "PyLD==3.1.0"},
        ) from exc

    class PyLdProcessor:
        name = "pyld"

        @staticmethod
        def _dropped(*args: Any, **kwargs: Any) -> None:
            raise JsonLdSkillError(
                "property_dropped",
                "Strict processing rejected a property that JSON-LD expansion would drop",
                details={"arguments": [repr(x) for x in args], "keywords": kwargs},
            )

        def _options(self, base: str | None = None) -> dict[str, Any]:
            result: dict[str, Any] = {
                "documentLoader": registry.pyld_loader(),
                "ordered": True,
                "processingMode": "json-ld-1.1",
                "on_property_dropped": self._dropped,
            }
            if base:
                result["base"] = base
            return result

        def expand(self, document: Any, *, base: str | None = None) -> Any:
            try:
                return jsonld.expand(document, options=self._options(base))
            except JsonLdSkillError:
                raise
            except Exception as exc:
                raise _map_pyld_error(exc) from exc

        def compact(self, document: Any, context: Any, *, base: str | None = None) -> Any:
            try:
                expanded = jsonld.expand(document, options=self._options(base))
                return jsonld.compact(expanded, context, options=self._options(base))
            except JsonLdSkillError:
                raise
            except Exception as exc:
                raise _map_pyld_error(exc) from exc

        def flatten(
            self, document: Any, context: Any | None = None, *, base: str | None = None
        ) -> Any:
            try:
                expanded = jsonld.expand(document, options=self._options(base))
                return jsonld.flatten(expanded, context, options=self._options(base))
            except JsonLdSkillError:
                raise
            except Exception as exc:
                raise _map_pyld_error(exc) from exc

        def frame(self, document: Any, frame: Any, *, base: str | None = None) -> Any:
            options = self._options(base)
            options.update(
                {
                    "embed": "@once",
                    "omitGraph": True,
                    "pruneBlankNodeIdentifiers": True,
                }
            )
            try:
                expanded = jsonld.expand(document, options=self._options(base))
                return jsonld.frame(expanded, frame, options=options)
            except JsonLdSkillError:
                raise
            except Exception as exc:
                raise _map_pyld_error(exc) from exc

        def normalize(self, document: Any, *, base: str | None = None) -> str:
            options = self._options(base)
            options.update(
                {
                    "algorithm": "URDNA2015",
                    "format": "application/n-quads",
                }
            )
            try:
                return str(jsonld.normalize(document, options=options))
            except JsonLdSkillError:
                raise
            except Exception as exc:
                raise _map_pyld_error(exc) from exc

    return PyLdProcessor()


def _map_pyld_error(exc: Exception) -> JsonLdSkillError:
    text = str(exc)
    lowered = text.lower()
    mappings = [
        ("protected term", "protected_term_redefinition"),
        ("recursive context inclusion", "cyclic_context"),
        ("invalid remote context", "invalid_remote_context"),
        ("invalid context entry", "invalid_context_definition"),
        ("invalid iri mapping", "invalid_iri_mapping"),
        ("loading remote context failed", "context_loading_failed"),
        ("list of lists", "list_of_lists"),
    ]
    code = "jsonld_processing_error"
    for needle, candidate in mappings:
        if needle in lowered:
            code = candidate
            break
    details: dict[str, Any] = {"processor": "PyLD", "exception_type": type(exc).__name__}
    cause = getattr(exc, "cause", None)
    if cause is not None:
        details["cause"] = str(cause)
    return JsonLdSkillError(code, text, details=details)


def default_registry_path() -> Path:
    return Path(__file__).resolve().parents[1] / "examples" / "contexts" / "registry.json"


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("input", help="UTF-8 JSON or JSON-LD input file")
    parser.add_argument(
        "--engine",
        choices=("pyld", "profile"),
        default="pyld",
        help="Processor engine; pyld is the standards default",
    )
    parser.add_argument(
        "--registry",
        default=str(default_registry_path()),
        help="Pinned local document registry (default: included example registry)",
    )
    parser.add_argument("--base", help="Explicit base IRI for relative identifiers")
    parser.add_argument("--output", help="Write result to this path instead of stdout")
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Emit only the operation result instead of the machine envelope",
    )
    parser.add_argument(
        "--max-input-bytes", type=int, default=MAX_INPUT_BYTES, help="Input byte limit"
    )
    parser.add_argument(
        "--max-output-bytes", type=int, default=MAX_OUTPUT_BYTES, help="Output byte limit"
    )
    parser.add_argument(
        "--max-json-depth", type=int, default=MAX_JSON_DEPTH, help="JSON nesting limit"
    )
    parser.add_argument(
        "--max-context-depth",
        type=int,
        default=MAX_CONTEXT_DEPTH,
        help="Remote context/import depth limit",
    )
    parser.add_argument(
        "--max-context-urls",
        type=int,
        default=MAX_CONTEXT_URLS,
        help="Distinct remote context URL limit",
    )


def load_operation_context(args: argparse.Namespace) -> tuple[Any, dict[str, Any], LocalDocumentRegistry, Any]:
    document, provenance = load_json_path(
        args.input, max_bytes=args.max_input_bytes, max_depth=args.max_json_depth
    )
    registry = LocalDocumentRegistry(args.registry, max_document_bytes=args.max_input_bytes)
    context_report = preflight_contexts(
        document,
        registry,
        max_context_depth=args.max_context_depth,
        max_context_urls=args.max_context_urls,
    )
    provenance["context_preflight"] = context_report
    processor = load_processor(args.engine, registry)
    return document, provenance, registry, processor


def emit_result(
    *,
    operation: str,
    engine: str,
    result: Any,
    provenance: Mapping[str, Any],
    raw: bool,
    output: str | None,
    max_output_bytes: int,
    extra: Mapping[str, Any] | None = None,
) -> None:
    payload: Any
    if raw:
        payload = result
    else:
        payload = {
            "ok": True,
            "operation": operation,
            "engine": engine,
            "source": dict(provenance),
            "result": result,
        }
        if extra:
            payload.update(extra)
    encoded = canonical_json_bytes(payload)
    if len(encoded) > max_output_bytes:
        raise JsonLdSkillError(
            "output_too_large",
            f"Output exceeds {max_output_bytes} bytes",
            details={"actual_bytes": len(encoded), "maximum_bytes": max_output_bytes},
        )
    if output:
        target = Path(output).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(encoded)
    else:
        sys.stdout.buffer.write(encoded)


def cli_main(operation: Callable[[argparse.Namespace], None]) -> None:
    try:
        operation(parse_args_for(operation))
    except JsonLdSkillError as exc:
        error = {"ok": False, "error": exc.as_dict()}
        sys.stderr.buffer.write(canonical_json_bytes(error))
        raise SystemExit(2) from exc
    except BrokenPipeError:
        raise SystemExit(0)


def parse_args_for(operation: Callable[[argparse.Namespace], None]) -> argparse.Namespace:
    parser_factory = getattr(operation, "parser_factory", None)
    if parser_factory is None:
        raise RuntimeError("CLI operation has no parser_factory")
    return parser_factory().parse_args()


def attach_parser(operation: Callable[[argparse.Namespace], None], factory: Callable[[], argparse.ArgumentParser]) -> None:
    setattr(operation, "parser_factory", factory)


def load_auxiliary_json(
    path: str,
    args: argparse.Namespace,
    registry: LocalDocumentRegistry | None = None,
) -> tuple[Any, dict[str, Any]]:
    value, provenance = load_json_path(
        path, max_bytes=args.max_input_bytes, max_depth=args.max_json_depth
    )
    if registry is not None:
        provenance["context_preflight"] = preflight_contexts(
            value,
            registry,
            max_context_depth=args.max_context_depth,
            max_context_urls=args.max_context_urls,
        )
    return value, provenance


def environment_report() -> dict[str, Any]:
    try:
        from importlib.metadata import version
    except ImportError:  # pragma: no cover
        return {}
    names = ["PyLD", "pydantic", "jsonschema", "rdflib"]
    result: dict[str, Any] = {"python": sys.version.split()[0]}
    for name in names:
        try:
            result[name] = version(name)
        except Exception:
            result[name] = None
    return result
