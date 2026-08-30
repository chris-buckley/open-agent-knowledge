#!/usr/bin/env python3
"""Bounded JSON-LD 1.1 profile engine for included examples.

This module intentionally implements a declared subset.  It exists so the
skill's safe-loading, modelling, graph checks, and golden examples remain
executable in an offline environment where PyLD is unavailable.  Use PyLD for
standards-conforming general JSON-LD processing.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import json
from typing import Any, Iterable, Mapping
from urllib.parse import urljoin, urlparse

try:
    from jsonld_common import JsonLdSkillError, LocalDocumentRegistry
except ImportError:  # package execution
    from .jsonld_common import JsonLdSkillError, LocalDocumentRegistry

JSONLD_KEYWORDS = {
    "@base",
    "@container",
    "@context",
    "@direction",
    "@graph",
    "@id",
    "@import",
    "@included",
    "@index",
    "@json",
    "@language",
    "@list",
    "@nest",
    "@none",
    "@prefix",
    "@propagate",
    "@protected",
    "@reverse",
    "@set",
    "@type",
    "@value",
    "@version",
    "@vocab",
}


@dataclass
class TermDefinition:
    id: str | None = None
    reverse: str | None = None
    type: str | None = None
    container: tuple[str, ...] = ()
    language: str | None = None
    direction: str | None = None
    prefix: bool = False
    protected: bool = False
    scoped_context: Any = None

    def semantic_tuple(self) -> tuple[Any, ...]:
        return (
            self.id,
            self.reverse,
            self.type,
            self.container,
            self.language,
            self.direction,
            self.prefix,
            self.scoped_context,
        )


@dataclass
class ActiveContext:
    base: str | None = None
    vocab: str | None = None
    default_language: str | None = None
    default_direction: str | None = None
    terms: dict[str, TermDefinition] = field(default_factory=dict)

    def clone(self) -> "ActiveContext":
        return deepcopy(self)


class ProfileJsonLdProcessor:
    """Deterministic subset processor; not an official conformance engine."""

    name = "profile"

    def __init__(self, registry: LocalDocumentRegistry) -> None:
        self.registry = registry
        self._blank_counter = 0

    def expand(self, document: Any, *, base: str | None = None) -> list[Any]:
        active = ActiveContext(base=base)
        result = self._expand_element(document, active, active_property=None)
        if result is None:
            return []
        if not isinstance(result, list):
            result = [result]
        return result

    def compact(self, document: Any, context: Any, *, base: str | None = None) -> Any:
        expanded = document if self._looks_expanded(document) else self.expand(document, base=base)
        active = self._process_context(ActiveContext(base=base), context, remote_stack=[])
        compacted = self._compact_element(expanded, active, active_property=None)
        if isinstance(compacted, list):
            if len(compacted) == 1:
                compacted = compacted[0]
            else:
                compacted = {self._compact_iri("@graph", active): compacted}
        if not isinstance(compacted, dict):
            compacted = {self._compact_iri("@graph", active): compacted}
        context_key = self._compact_iri("@context", active)
        return {context_key: deepcopy(context), **compacted}

    def flatten(
        self, document: Any, context: Any | None = None, *, base: str | None = None
    ) -> Any:
        expanded = document if self._looks_expanded(document) else self.expand(document, base=base)
        nodes = self._flatten_expanded(expanded)
        if context is None:
            return nodes
        active = self._process_context(ActiveContext(base=base), context, remote_stack=[])
        compacted_nodes = [self._compact_element(node, active, None) for node in nodes]
        return {
            self._compact_iri("@context", active): deepcopy(context),
            self._compact_iri("@graph", active): compacted_nodes,
        }

    def frame(self, document: Any, frame: Any, *, base: str | None = None) -> Any:
        expanded = document if self._looks_expanded(document) else self.expand(document, base=base)
        nodes = self._flatten_expanded(expanded)
        node_map = {node["@id"]: node for node in nodes if "@id" in node}
        context = frame.get("@context") if isinstance(frame, dict) else None
        active = self._process_context(ActiveContext(base=base), context, remote_stack=[])
        frame_spec = self._expand_frame(frame, active)
        matches = [node for node in nodes if self._frame_matches(node, frame_spec)]
        embedded_once: set[str] = set()
        framed = [
            self._apply_frame(
                node,
                frame_spec,
                node_map,
                path=(),
                embedded_once=embedded_once,
            )
            for node in matches
        ]
        compacted = [self._compact_element(item, active, None) for item in framed]
        if len(compacted) == 1:
            body: dict[str, Any] = compacted[0]
        else:
            body = {self._compact_iri("@graph", active): compacted}
        if context is not None:
            return {self._compact_iri("@context", active): deepcopy(context), **body}
        return body

    def normalize(self, document: Any, *, base: str | None = None) -> str:
        expanded = document if self._looks_expanded(document) else self.expand(document, base=base)
        nodes = self._flatten_expanded(expanded)
        if any(str(node.get("@id", "")).startswith("_:") for node in nodes):
            raise JsonLdSkillError(
                "profile_blank_node_normalization_unsupported",
                "The profile engine does not claim canonical equivalence for blank-node graphs",
            )
        normalized = self._semantic_normal_form(nodes)
        return json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _looks_expanded(value: Any) -> bool:
        if isinstance(value, list):
            return not value or all(isinstance(item, dict) for item in value)
        return isinstance(value, dict) and "@context" not in value and any(
            key.startswith("http://") or key.startswith("https://") or key.startswith("@")
            for key in value
        )

    def _process_context(
        self,
        active: ActiveContext,
        local: Any,
        *,
        remote_stack: list[str],
    ) -> ActiveContext:
        if local is None:
            if any(definition.protected for definition in active.terms.values()):
                raise JsonLdSkillError(
                    "invalid_context_nullification",
                    "A null context cannot remove protected term definitions",
                )
            return ActiveContext(base=active.base)
        if isinstance(local, list):
            result = active
            for item in local:
                result = self._process_context(result, item, remote_stack=remote_stack)
            return result
        if isinstance(local, str):
            if local in remote_stack:
                raise JsonLdSkillError(
                    "cyclic_context", "Cyclic context reference", identifier=local
                )
            loaded = self.registry.load(local)
            if not isinstance(loaded, dict) or "@context" not in loaded:
                raise JsonLdSkillError(
                    "invalid_remote_context",
                    "Remote context document must contain @context",
                    identifier=local,
                )
            return self._process_context(
                active, loaded["@context"], remote_stack=remote_stack + [local]
            )
        if not isinstance(local, dict):
            raise JsonLdSkillError(
                "invalid_context_definition", "@context must be null, string, object, or array"
            )
        result = active.clone()
        imported = local.get("@import")
        if imported is not None:
            if not isinstance(imported, str):
                raise JsonLdSkillError("invalid_context_definition", "@import must be a string")
            loaded = self.registry.load(imported)
            imported_context = loaded.get("@context") if isinstance(loaded, dict) else None
            if not isinstance(imported_context, dict):
                raise JsonLdSkillError(
                    "invalid_remote_context", "Imported context must be an object", identifier=imported
                )
            if "@import" in imported_context:
                raise JsonLdSkillError(
                    "invalid_context_import",
                    "An imported context cannot contain another @import entry",
                    identifier=imported,
                )
            result = self._process_context(
                result, imported_context, remote_stack=remote_stack + [imported]
            )
        if "@base" in local:
            base = local["@base"]
            if base is not None and not isinstance(base, str):
                raise JsonLdSkillError("invalid_context_definition", "@base must be string or null")
            result.base = urljoin(result.base or "", base) if base is not None else None
        if "@vocab" in local:
            vocab = local["@vocab"]
            if vocab is not None and not isinstance(vocab, str):
                raise JsonLdSkillError("invalid_context_definition", "@vocab must be string or null")
            result.vocab = self._expand_iri(vocab, result, vocab=False, document_relative=True) if vocab else None
        if "@language" in local:
            language = local["@language"]
            if language is not None and not isinstance(language, str):
                raise JsonLdSkillError("invalid_context_definition", "@language must be string or null")
            result.default_language = language.lower() if isinstance(language, str) else None
        if "@direction" in local:
            direction = local["@direction"]
            if direction not in (None, "ltr", "rtl"):
                raise JsonLdSkillError("invalid_context_definition", "@direction must be ltr, rtl, or null")
            result.default_direction = direction
        default_protected = bool(local.get("@protected", False))
        for term, raw in local.items():
            if term.startswith("@"):
                continue
            if ":" in term and term.split(":", 1)[0] == "_":
                raise JsonLdSkillError("invalid_term_definition", f"Blank-node term is invalid: {term}")
            definition = self._create_term_definition(term, raw, result, default_protected)
            existing = result.terms.get(term)
            if existing and existing.protected and existing.semantic_tuple() != definition.semantic_tuple():
                raise JsonLdSkillError(
                    "protected_term_redefinition",
                    f"Protected term {term!r} cannot be redefined",
                    path=f"@context.{term}",
                )
            if definition.id is None and definition.reverse is None and raw is None:
                result.terms.pop(term, None)
            else:
                result.terms[term] = definition
        return result

    def _create_term_definition(
        self, term: str, raw: Any, active: ActiveContext, default_protected: bool
    ) -> TermDefinition:
        if raw is None:
            return TermDefinition(protected=default_protected)
        if isinstance(raw, str):
            if raw == "@context":
                raise JsonLdSkillError(
                    "invalid_keyword_alias", "@context cannot be aliased by a term definition"
                )
            identifier = raw if raw in JSONLD_KEYWORDS else self._expand_iri(raw, active, vocab=True)
            return TermDefinition(id=identifier, protected=default_protected)
        if not isinstance(raw, dict):
            raise JsonLdSkillError(
                "invalid_term_definition", f"Term {term!r} must map to string, object, or null"
            )
        reverse = raw.get("@reverse")
        identifier = raw.get("@id")
        if reverse is not None and identifier is not None:
            raise JsonLdSkillError(
                "invalid_reverse_property", f"Term {term!r} cannot define both @id and @reverse"
            )
        if reverse is not None:
            if not isinstance(reverse, str):
                raise JsonLdSkillError("invalid_reverse_property", "@reverse must be a string")
            reverse = self._expand_iri(reverse, active, vocab=True)
        elif identifier == "@context":
            raise JsonLdSkillError(
                "invalid_keyword_alias", "@context cannot be aliased by a term definition"
            )
        elif identifier is None:
            identifier = self._expand_iri(term, active, vocab=True)
        elif identifier in JSONLD_KEYWORDS:
            pass
        elif isinstance(identifier, str):
            identifier = self._expand_iri(identifier, active, vocab=True)
        else:
            raise JsonLdSkillError("invalid_iri_mapping", "@id in a term definition must be a string")
        type_mapping = raw.get("@type")
        if type_mapping is not None:
            if type_mapping not in {"@id", "@vocab", "@json", "@none"}:
                if not isinstance(type_mapping, str):
                    raise JsonLdSkillError("invalid_type_mapping", "@type mapping must be a string")
                type_mapping = self._expand_iri(type_mapping, active, vocab=True)
        container_raw = raw.get("@container", [])
        if isinstance(container_raw, str):
            container = (container_raw,)
        elif isinstance(container_raw, list) and all(isinstance(x, str) for x in container_raw):
            container = tuple(sorted(set(container_raw)))
        else:
            raise JsonLdSkillError("invalid_container_mapping", "@container must be a string or string array")
        allowed = {"@set", "@list", "@language", "@index", "@id", "@type", "@graph"}
        if any(item not in allowed for item in container):
            raise JsonLdSkillError("invalid_container_mapping", f"Unsupported container: {container}")
        container_set = set(container)
        permitted = [
            set(),
            {"@set"},
            {"@list"},
            {"@language"},
            {"@index"},
            {"@id"},
            {"@type"},
            {"@graph"},
            {"@set", "@language"},
            {"@set", "@index"},
            {"@set", "@id"},
            {"@set", "@type"},
            {"@set", "@graph"},
            {"@graph", "@id"},
            {"@graph", "@index"},
            {"@graph", "@id", "@set"},
            {"@graph", "@index", "@set"},
        ]
        if container_set not in permitted:
            raise JsonLdSkillError(
                "invalid_container_mapping", f"Invalid @container combination: {container}"
            )
        language = raw.get("@language")
        if language is not None and not isinstance(language, str):
            raise JsonLdSkillError("invalid_language_mapping", "@language mapping must be string or null")
        direction = raw.get("@direction")
        if direction not in (None, "ltr", "rtl"):
            raise JsonLdSkillError("invalid_direction_mapping", "@direction mapping must be ltr, rtl, or null")
        prefix = bool(raw.get("@prefix", False))
        protected = bool(raw.get("@protected", default_protected))
        return TermDefinition(
            id=identifier,
            reverse=reverse,
            type=type_mapping,
            container=container,
            language=language.lower() if isinstance(language, str) else None,
            direction=direction,
            prefix=prefix,
            protected=protected,
            scoped_context=deepcopy(raw.get("@context")),
        )

    def _expand_iri(
        self,
        value: str | None,
        active: ActiveContext,
        *,
        vocab: bool = False,
        document_relative: bool = False,
    ) -> str | None:
        if value is None or value in JSONLD_KEYWORDS:
            return value
        definition = active.terms.get(value)
        if definition and definition.id:
            return definition.id
        if ":" in value:
            prefix, suffix = value.split(":", 1)
            if prefix == "_" or suffix.startswith("//"):
                return value
            prefix_def = active.terms.get(prefix)
            if prefix_def and prefix_def.id and (prefix_def.prefix or prefix_def.id.endswith(("/", "#", ":"))):
                return prefix_def.id + suffix
            if urlparse(value).scheme:
                return value
        if vocab and active.vocab is not None:
            return active.vocab + value
        if document_relative and active.base is not None:
            return urljoin(active.base, value)
        return value

    def _expand_element(
        self, element: Any, active: ActiveContext, active_property: str | None
    ) -> Any:
        if element is None:
            return None
        if isinstance(element, list):
            result: list[Any] = []
            for item in element:
                expanded = self._expand_element(item, active, active_property)
                if expanded is None:
                    continue
                if isinstance(expanded, list):
                    result.extend(expanded)
                else:
                    result.append(expanded)
            return result
        if not isinstance(element, dict):
            if active_property is None:
                return None
            definition = active.terms.get(active_property)
            return self._expand_scalar(element, definition, active)
        local_active = active
        if "@context" in element:
            local_active = self._process_context(active, element["@context"], remote_stack=[])
        # Apply type-scoped contexts in lexical order for deterministic smoke behaviour.
        type_values = element.get("@type")
        if type_values is None:
            for alias, definition in local_active.terms.items():
                if definition.id == "@type" and alias in element:
                    type_values = element[alias]
                    break
        for raw_type in sorted(self._as_list(type_values)):
            if isinstance(raw_type, str):
                type_term = local_active.terms.get(raw_type)
                if type_term and type_term.scoped_context is not None:
                    local_active = self._process_context(
                        local_active, type_term.scoped_context, remote_stack=[]
                    )
        result: dict[str, Any] = {}
        nested_items: list[tuple[str, Any]] = []
        for key, value in element.items():
            if key == "@context":
                continue
            expanded_property = self._expand_iri(key, local_active, vocab=True)
            if expanded_property is None:
                continue
            if expanded_property == "@nest":
                if not isinstance(value, dict):
                    raise JsonLdSkillError("invalid_nest_value", "@nest value must be an object")
                nested_items.extend(value.items())
                continue
            self._expand_member(result, key, expanded_property, value, local_active)
        for key, value in nested_items:
            expanded_property = self._expand_iri(key, local_active, vocab=True)
            if expanded_property is not None:
                self._expand_member(result, key, expanded_property, value, local_active)
        self._validate_expanded_object(result)
        if "@set" in result and len(result) == 1:
            return result["@set"]
        return result

    def _expand_member(
        self,
        result: dict[str, Any],
        compact_property: str,
        expanded_property: str,
        value: Any,
        active: ActiveContext,
    ) -> None:
        if expanded_property in JSONLD_KEYWORDS:
            self._expand_keyword(result, expanded_property, value, active)
            return
        if not (expanded_property.startswith("http://") or expanded_property.startswith("https://") or expanded_property.startswith("_:")):
            raise JsonLdSkillError(
                "property_dropped",
                f"Property {compact_property!r} does not expand to an absolute IRI",
                path=f"$.{compact_property}",
            )
        definition = active.terms.get(compact_property)
        scoped_active = active
        if definition and definition.scoped_context is not None:
            scoped_active = self._process_context(active, definition.scoped_context, remote_stack=[])
        expanded_values = self._expand_container_value(value, compact_property, definition, scoped_active)
        if definition and definition.reverse:
            reverse_map = result.setdefault("@reverse", {})
            self._append_values(reverse_map, definition.reverse, expanded_values)
        else:
            self._append_values(result, expanded_property, expanded_values)

    def _expand_keyword(
        self, result: dict[str, Any], keyword: str, value: Any, active: ActiveContext
    ) -> None:
        if keyword == "@id":
            if not isinstance(value, str):
                raise JsonLdSkillError("invalid_id_value", "@id must be a string")
            result["@id"] = self._expand_iri(value, active, document_relative=True)
        elif keyword == "@type":
            values = self._as_list(value)
            if not all(isinstance(x, str) for x in values):
                raise JsonLdSkillError("invalid_type_value", "@type must contain strings")
            result["@type"] = [self._expand_iri(x, active, vocab=True) for x in values]
        elif keyword == "@value":
            result["@value"] = deepcopy(value)
        elif keyword == "@language":
            if not isinstance(value, str):
                raise JsonLdSkillError("invalid_language_tag", "@language must be a string")
            result["@language"] = value.lower()
        elif keyword == "@direction":
            if value not in {"ltr", "rtl"}:
                raise JsonLdSkillError("invalid_base_direction", "@direction must be ltr or rtl")
            result["@direction"] = value
        elif keyword == "@index":
            if not isinstance(value, str):
                raise JsonLdSkillError("invalid_index_value", "@index must be a string")
            result["@index"] = value
        elif keyword in {"@graph", "@included", "@set"}:
            expanded = self._expand_element(value, active, None)
            result[keyword] = expanded if isinstance(expanded, list) else [expanded]
        elif keyword == "@list":
            expanded = self._expand_element(value, active, None)
            values = expanded if isinstance(expanded, list) else [expanded]
            if any(isinstance(item, dict) and "@list" in item for item in values):
                raise JsonLdSkillError("list_of_lists", "JSON-LD lists cannot directly contain lists")
            result["@list"] = values
        elif keyword == "@reverse":
            expanded = self._expand_element(value, active, None)
            items = expanded if isinstance(expanded, list) else [expanded]
            reverse_map = result.setdefault("@reverse", {})
            for item in items:
                if not isinstance(item, dict):
                    raise JsonLdSkillError("invalid_reverse_value", "@reverse must expand to objects")
                nested = item.pop("@reverse", None)
                if isinstance(nested, dict):
                    for prop, vals in nested.items():
                        self._append_values(result, prop, vals)
                for prop, vals in item.items():
                    if prop.startswith("@"):
                        continue
                    self._append_values(reverse_map, prop, vals)
        elif keyword in {"@base", "@container", "@import", "@json", "@none", "@prefix", "@propagate", "@protected", "@version", "@vocab"}:
            return
        else:
            raise JsonLdSkillError("unsupported_keyword", f"Profile engine does not process {keyword}")

    def _expand_container_value(
        self,
        value: Any,
        property_term: str,
        definition: TermDefinition | None,
        active: ActiveContext,
    ) -> list[Any]:
        container = set(definition.container if definition else ())
        if "@language" in container and isinstance(value, dict):
            result: list[Any] = []
            for language, entries in value.items():
                for entry in self._as_list(entries):
                    if not isinstance(entry, str):
                        raise JsonLdSkillError("invalid_language_map_value", "Language-map values must be strings")
                    item: dict[str, Any] = {"@value": entry}
                    if language != "@none":
                        item["@language"] = language.lower()
                    if definition and definition.direction:
                        item["@direction"] = definition.direction
                    result.append(item)
            return result
        if "@index" in container and isinstance(value, dict):
            result = []
            for index, entries in value.items():
                expanded = self._expand_element(entries, active, property_term)
                for item in self._as_list(expanded):
                    if isinstance(item, dict) and index != "@none":
                        item = deepcopy(item)
                        item.setdefault("@index", index)
                    result.append(item)
            return result
        if "@id" in container and isinstance(value, dict):
            result = []
            for identifier, entries in value.items():
                expanded = self._expand_element(entries, active, property_term)
                for item in self._as_list(expanded):
                    if not isinstance(item, dict):
                        item = {"@value": item}
                    item = deepcopy(item)
                    if identifier != "@none":
                        item.setdefault("@id", self._expand_iri(identifier, active, document_relative=True))
                    result.append(item)
            return result
        if "@type" in container and isinstance(value, dict):
            result = []
            for type_name, entries in value.items():
                expanded = self._expand_element(entries, active, property_term)
                for item in self._as_list(expanded):
                    if not isinstance(item, dict):
                        item = {"@value": item}
                    item = deepcopy(item)
                    if type_name != "@none":
                        item.setdefault("@type", []).append(self._expand_iri(type_name, active, vocab=True))
                    result.append(item)
            return result
        expanded = self._expand_element(value, active, property_term)
        values = self._as_list(expanded)
        if "@list" in container:
            if any(isinstance(item, dict) and "@list" in item for item in values):
                raise JsonLdSkillError("list_of_lists", "JSON-LD lists cannot directly contain lists")
            return [{"@list": values}]
        return values

    def _expand_scalar(
        self, value: Any, definition: TermDefinition | None, active: ActiveContext
    ) -> dict[str, Any]:
        if definition and definition.type == "@id":
            if not isinstance(value, str):
                raise JsonLdSkillError("invalid_typed_value", "@id-coerced value must be a string")
            return {"@id": self._expand_iri(value, active, document_relative=True)}
        if definition and definition.type == "@vocab":
            if not isinstance(value, str):
                raise JsonLdSkillError("invalid_typed_value", "@vocab-coerced value must be a string")
            return {"@id": self._expand_iri(value, active, vocab=True)}
        item: dict[str, Any] = {"@value": deepcopy(value)}
        if definition and definition.type == "@json":
            item["@type"] = "@json"
        elif definition and definition.type and definition.type != "@none":
            item["@type"] = definition.type
        elif isinstance(value, str):
            language = definition.language if definition else active.default_language
            direction = definition.direction if definition else active.default_direction
            if language is not None:
                item["@language"] = language
            if direction is not None:
                item["@direction"] = direction
        return item

    @staticmethod
    def _append_values(target: dict[str, Any], key: str, values: Any) -> None:
        bucket = target.setdefault(key, [])
        if not isinstance(bucket, list):
            bucket = [bucket]
            target[key] = bucket
        if isinstance(values, list):
            bucket.extend(values)
        else:
            bucket.append(values)

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        if value is None:
            return []
        return value if isinstance(value, list) else [value]

    @staticmethod
    def _validate_expanded_object(value: dict[str, Any]) -> None:
        if "@value" in value:
            allowed = {"@value", "@type", "@language", "@direction", "@index"}
            invalid = set(value) - allowed
            if invalid:
                raise JsonLdSkillError(
                    "invalid_value_object",
                    f"Value object contains illegal members: {sorted(invalid)}",
                )
            if "@type" in value and ("@language" in value or "@direction" in value):
                raise JsonLdSkillError(
                    "invalid_value_object", "@type cannot be combined with @language or @direction"
                )
        if "@list" in value and set(value) - {"@list", "@index"}:
            raise JsonLdSkillError("invalid_list_object", "List object may only add @index")
        if "@set" in value and set(value) - {"@set", "@index"}:
            raise JsonLdSkillError("invalid_set_object", "Set object may only add @index")

    def _compact_iri(self, iri: str, active: ActiveContext, *, vocab: bool = True) -> str:
        candidates = [
            term
            for term, definition in active.terms.items()
            if definition.id == iri or definition.reverse == iri
        ]
        if candidates:
            return sorted(candidates, key=lambda x: (len(x), x))[0]
        if iri in JSONLD_KEYWORDS:
            return iri
        prefix_candidates: list[str] = []
        for term, definition in active.terms.items():
            if definition.id and (definition.prefix or definition.id.endswith(("/", "#", ":"))) and iri.startswith(definition.id):
                suffix = iri[len(definition.id) :]
                if suffix and ":" not in suffix and not suffix.startswith("//"):
                    prefix_candidates.append(f"{term}:{suffix}")
        if prefix_candidates:
            return sorted(prefix_candidates, key=lambda x: (len(x), x))[0]
        if vocab and active.vocab and iri.startswith(active.vocab):
            suffix = iri[len(active.vocab) :]
            if suffix:
                return suffix
        return iri

    def _compact_element(
        self, element: Any, active: ActiveContext, active_property: str | None
    ) -> Any:
        if isinstance(element, list):
            values = [self._compact_element(item, active, active_property) for item in element]
            definition = active.terms.get(active_property or "")
            force_array = bool(definition and "@set" in definition.container)
            if len(values) == 1 and not force_array:
                return values[0]
            return values
        if not isinstance(element, dict):
            return deepcopy(element)
        if "@value" in element:
            definition = active.terms.get(active_property or "")
            extras = set(element) - {"@value"}
            if not extras:
                return deepcopy(element["@value"])
            if definition:
                if element.get("@type") == definition.type:
                    return deepcopy(element["@value"])
                if element.get("@language") == definition.language and element.get("@direction") == definition.direction:
                    return deepcopy(element["@value"])
            result = {self._compact_iri(key, active): deepcopy(value) for key, value in element.items()}
            return result
        if "@id" in element and set(element) == {"@id"}:
            identifier = self._compact_iri(str(element["@id"]), active, vocab=False)
            definition = active.terms.get(active_property or "")
            if definition and definition.type in {"@id", "@vocab"}:
                return identifier
            return {self._compact_iri("@id", active): identifier}
        if "@list" in element:
            definition = active.terms.get(active_property or "")
            compacted = self._compact_element(element["@list"], active, active_property)
            if definition and "@list" in definition.container:
                return compacted if isinstance(compacted, list) else [compacted]
            result = {self._compact_iri("@list", active): compacted}
            if "@index" in element:
                result[self._compact_iri("@index", active)] = element["@index"]
            return result
        result: dict[str, Any] = {}
        for expanded_property, raw in sorted(element.items()):
            compact_property = self._compact_iri(expanded_property, active)
            if expanded_property == "@id":
                result[compact_property] = self._compact_iri(str(raw), active, vocab=False)
                continue
            if expanded_property == "@type":
                compacted_types = [self._compact_iri(str(item), active) for item in self._as_list(raw)]
                result[compact_property] = compacted_types[0] if len(compacted_types) == 1 else compacted_types
                continue
            if expanded_property == "@reverse":
                result[compact_property] = self._compact_element(raw, active, None)
                continue
            if expanded_property in {"@graph", "@included", "@set"}:
                result[compact_property] = self._compact_element(raw, active, None)
                continue
            definition = active.terms.get(compact_property)
            values = self._as_list(raw)
            if definition and "@language" in definition.container:
                language_map: dict[str, Any] = {}
                for item in values:
                    if not isinstance(item, dict) or "@value" not in item:
                        continue
                    language = item.get("@language", "@none")
                    language_map.setdefault(language, []).append(item["@value"])
                result[compact_property] = {
                    key: vals[0] if len(vals) == 1 and "@set" not in definition.container else vals
                    for key, vals in sorted(language_map.items())
                }
                continue
            if definition and "@index" in definition.container:
                index_map: dict[str, Any] = {}
                for item in values:
                    copied = deepcopy(item)
                    index = copied.pop("@index", "@none") if isinstance(copied, dict) else "@none"
                    index_map[index] = self._compact_element(copied, active, compact_property)
                result[compact_property] = index_map
                continue
            if definition and "@id" in definition.container:
                id_map: dict[str, Any] = {}
                for item in values:
                    copied = deepcopy(item)
                    identifier = copied.pop("@id", "@none") if isinstance(copied, dict) else "@none"
                    key = self._compact_iri(identifier, active, vocab=False) if identifier != "@none" else "@none"
                    id_map[key] = self._compact_element(copied, active, compact_property)
                result[compact_property] = id_map
                continue
            if definition and "@type" in definition.container:
                type_map: dict[str, Any] = {}
                for item in values:
                    copied = deepcopy(item)
                    types = self._as_list(copied.pop("@type", [])) if isinstance(copied, dict) else []
                    key = self._compact_iri(types[0], active) if types else "@none"
                    type_map[key] = self._compact_element(copied, active, compact_property)
                result[compact_property] = type_map
                continue
            compacted_values = [
                self._compact_element(item, active, compact_property) for item in values
            ]
            if len(compacted_values) == 1 and not (definition and "@set" in definition.container):
                result[compact_property] = compacted_values[0]
            else:
                result[compact_property] = compacted_values
        return result

    def _flatten_expanded(self, expanded: Any) -> list[dict[str, Any]]:
        self._blank_counter = 0
        node_map: dict[str, dict[str, Any]] = {}

        def blank_id() -> str:
            value = f"_:b{self._blank_counter}"
            self._blank_counter += 1
            return value

        def collect(node: Any, graph: str | None = None) -> Any:
            if isinstance(node, list):
                return [collect(item, graph) for item in node]
            if not isinstance(node, dict):
                return deepcopy(node)
            if "@value" in node:
                return deepcopy(node)
            if "@list" in node:
                return {"@list": [collect(item, graph) for item in node["@list"]], **({"@index": node["@index"]} if "@index" in node else {})}
            if set(node) <= {"@id", "@index"} and "@id" in node:
                return {"@id": node["@id"], **({"@index": node["@index"]} if "@index" in node else {})}
            if "@graph" in node and set(node) <= {"@graph", "@context", "@included"}:
                for item in self._as_list(node.get("@graph")):
                    collect(item, graph)
                for item in self._as_list(node.get("@included")):
                    collect(item, graph)
                return None
            identifier = node.get("@id") or blank_id()
            target = node_map.setdefault(identifier, {"@id": identifier})
            if graph is not None:
                target.setdefault("@graphName", graph)
            for prop, raw in node.items():
                if prop == "@id":
                    continue
                if prop == "@graph":
                    graph_nodes = []
                    for item in self._as_list(raw):
                        ref = collect(item, identifier)
                        if ref is not None:
                            graph_nodes.append(ref)
                    if graph_nodes:
                        target.setdefault("@graph", []).extend(graph_nodes)
                    continue
                if prop == "@included":
                    for item in self._as_list(raw):
                        collect(item, graph)
                    continue
                if prop == "@reverse":
                    reverse_map = target.setdefault("@reverse", {})
                    for rprop, rvalues in raw.items():
                        for item in self._as_list(rvalues):
                            ref = collect(item, graph)
                            if ref is not None:
                                reverse_map.setdefault(rprop, []).append(ref)
                    continue
                values = self._as_list(raw)
                bucket = target.setdefault(prop, [])
                for item in values:
                    if isinstance(item, dict) and "@value" not in item and "@list" not in item:
                        ref = collect(item, graph)
                        if ref is not None:
                            if isinstance(ref, dict) and "@id" in ref:
                                bucket.append({"@id": ref["@id"]})
                            else:
                                bucket.append(ref)
                    else:
                        bucket.append(collect(item, graph))
            return {"@id": identifier}

        for item in self._as_list(expanded):
            collect(item)
        for node in node_map.values():
            node.pop("@graphName", None)
            for key, value in list(node.items()):
                if isinstance(value, list):
                    node[key] = self._dedupe_sort_values(value)
        return [node_map[key] for key in sorted(node_map)]

    @staticmethod
    def _dedupe_sort_values(values: list[Any]) -> list[Any]:
        seen: set[str] = set()
        result: list[Any] = []
        for value in values:
            marker = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            if marker not in seen:
                seen.add(marker)
                result.append(value)
        return sorted(result, key=lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":")))

    def _expand_frame(self, frame: Any, active: ActiveContext) -> dict[str, Any]:
        if not isinstance(frame, dict):
            raise JsonLdSkillError("invalid_frame", "Frame must be an object")
        result: dict[str, Any] = {}
        for key, value in frame.items():
            if key == "@context":
                continue
            if key in {"@embed", "@explicit", "@requireAll", "@omitDefault", "@default"}:
                result[key] = deepcopy(value)
                continue
            expanded_key = self._expand_iri(key, active, vocab=True)
            if expanded_key in {"@id", "@type"}:
                values = self._as_list(value)
                result[expanded_key] = [
                    self._expand_iri(item, active, vocab=(expanded_key == "@type"), document_relative=(expanded_key == "@id"))
                    for item in values
                    if isinstance(item, str)
                ]
            elif expanded_key in {"@embed", "@explicit", "@requireAll", "@omitDefault"}:
                result[expanded_key] = value
            elif expanded_key == "@reverse":
                result[expanded_key] = self._expand_frame(value, active)
            elif expanded_key and not expanded_key.startswith("@"):
                if isinstance(value, list):
                    raw_subframe = value[0] if value else {}
                else:
                    raw_subframe = value
                if not isinstance(raw_subframe, dict):
                    raw_subframe = {}
                subframe = self._expand_frame(raw_subframe, active)
                if "@default" in raw_subframe:
                    subframe["@default"] = deepcopy(raw_subframe["@default"])
                result[expanded_key] = subframe
        return result

    @staticmethod
    def _frame_matches(node: Mapping[str, Any], frame: Mapping[str, Any]) -> bool:
        ids = frame.get("@id")
        if ids and node.get("@id") not in ids:
            return False
        types = set(frame.get("@type", []))
        if types and not types.intersection(node.get("@type", [])):
            return False
        if frame.get("@requireAll"):
            requested = [key for key in frame if not key.startswith("@")]
            if any(key not in node for key in requested):
                return False
        return True

    def _apply_frame(
        self,
        node: Mapping[str, Any],
        frame: Mapping[str, Any],
        node_map: Mapping[str, Mapping[str, Any]],
        *,
        path: tuple[str, ...],
        embedded_once: set[str],
    ) -> dict[str, Any]:
        identifier = str(node.get("@id", ""))
        embed = frame.get("@embed", "@once")
        if identifier in path or embed == "@never" or (embed == "@once" and identifier in embedded_once):
            return {"@id": identifier}
        if embed == "@once":
            embedded_once.add(identifier)
        explicit = bool(frame.get("@explicit", False))
        omit_default = bool(frame.get("@omitDefault", False))
        result: dict[str, Any] = {"@id": identifier}
        if "@type" in node:
            result["@type"] = deepcopy(node["@type"])
        properties: Iterable[str]
        if explicit:
            properties = sorted(key for key in frame if not key.startswith("@"))
        else:
            properties = sorted(key for key in node if not key.startswith("@"))
        for prop in properties:
            subframe = frame.get(prop, {})
            if prop not in node:
                if isinstance(subframe, dict) and "@default" in subframe and not omit_default:
                    result[prop] = [{"@value": deepcopy(subframe["@default"])}]
                continue
            framed_values: list[Any] = []
            for value in self._as_list(node[prop]):
                if isinstance(value, dict) and set(value) == {"@id"}:
                    target = node_map.get(str(value["@id"]))
                    if target is not None:
                        framed_values.append(
                            self._apply_frame(
                                target,
                                subframe if isinstance(subframe, dict) else {},
                                node_map,
                                path=path + (identifier,),
                                embedded_once=embedded_once,
                            )
                        )
                    else:
                        framed_values.append(deepcopy(value))
                elif isinstance(value, dict) and "@list" in value:
                    framed_values.append(
                        {
                            "@list": [
                                self._apply_frame(
                                    node_map[item["@id"]],
                                    subframe if isinstance(subframe, dict) else {},
                                    node_map,
                                    path=path + (identifier,),
                                    embedded_once=embedded_once,
                                )
                                if isinstance(item, dict) and set(item) == {"@id"} and item["@id"] in node_map
                                else deepcopy(item)
                                for item in value["@list"]
                            ]
                        }
                    )
                else:
                    framed_values.append(deepcopy(value))
            result[prop] = framed_values
        if "@reverse" in frame and "@reverse" in node:
            result["@reverse"] = deepcopy(node["@reverse"])
        return result

    def _semantic_normal_form(self, nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        def normalize_value(value: Any) -> Any:
            if isinstance(value, dict):
                return {key: normalize_value(value[key]) for key in sorted(value)}
            if isinstance(value, list):
                normalized = [normalize_value(item) for item in value]
                return sorted(normalized, key=lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
            return value

        return [normalize_value(node) for node in sorted(nodes, key=lambda x: x.get("@id", ""))]
