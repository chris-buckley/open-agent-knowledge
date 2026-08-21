from __future__ import annotations
import json
from pathlib import Path

import pytest

from jsonld_common import JsonLdSkillError, LocalDocumentRegistry, load_json_path, preflight_contexts
from profile_engine import ProfileJsonLdProcessor

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "examples" / "contexts" / "registry.json"


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


@pytest.fixture()
def processor() -> ProfileJsonLdProcessor:
    return ProfileJsonLdProcessor(LocalDocumentRegistry(REGISTRY))


def test_expansion_matches_golden(processor: ProfileJsonLdProcessor) -> None:
    source = load("examples/compact/system-bundle.jsonld")
    expected = load("examples/expanded/system-bundle.expanded.json")
    assert processor.expand(source) == expected


def test_flattening_matches_golden(processor: ProfileJsonLdProcessor) -> None:
    source = load("examples/compact/system-bundle.jsonld")
    expected = load("examples/flattened/system-bundle.flattened.json")
    assert processor.flatten(source) == expected


def test_framing_matches_application_profile(processor: ProfileJsonLdProcessor) -> None:
    source = load("examples/compact/system-bundle.jsonld")
    frame = load("examples/framed/system.frame.jsonld")
    expected = load("examples/framed/domain-extension.framed.jsonld")
    assert processor.frame(source, frame) == expected


def test_container_maps_match_golden(processor: ProfileJsonLdProcessor) -> None:
    source = load("examples/containers/container-maps.jsonld")
    expected = load("examples/containers/container-maps.expanded.json")
    assert processor.expand(source) == expected


def test_compaction_roundtrip_preserves_named_node_graph(processor: ProfileJsonLdProcessor) -> None:
    source = load("examples/compact/system-bundle.jsonld")
    context = load("examples/contexts/system-context.jsonld")["@context"]
    before = processor.expand(source)
    compacted = processor.compact(before, context)
    after = processor.expand(compacted)
    assert processor.normalize(before) == processor.normalize(after)
    assert compacted != source


def test_direct_and_reverse_forms_expand_to_same_edge(processor: ProfileJsonLdProcessor) -> None:
    direct = processor.expand(load("examples/compact/direct-relationship.jsonld"))
    reverse = processor.expand(load("examples/compact/reverse-relationship.jsonld"))
    direct_node = direct[0]
    reverse_node = reverse[0]
    direct_target = direct_node["https://example.org/term/links_to"][0]["@id"]
    reverse_source = reverse_node["@reverse"]["https://example.org/term/links_to"][0]["@id"]
    assert direct_node["@id"] == reverse_source
    assert reverse_node["@id"] == direct_target


def test_preflight_accepts_pinned_context() -> None:
    registry = LocalDocumentRegistry(REGISTRY)
    source = load("examples/compact/system-bundle.jsonld")
    report = preflight_contexts(source, registry)
    assert report["context_iris"] == ["https://example.org/context/system-v1.jsonld"]


def test_preflight_rejects_unpinned_remote_context() -> None:
    registry = LocalDocumentRegistry(REGISTRY)
    source = load("examples/invalid/untrusted-remote-context.jsonld")
    with pytest.raises(JsonLdSkillError, match="not pinned") as caught:
        preflight_contexts(source, registry)
    assert caught.value.code == "remote_context_rejected"


def test_preflight_rejects_cyclic_contexts() -> None:
    registry = LocalDocumentRegistry(REGISTRY)
    source = load("examples/invalid/cyclic-context-document.jsonld")
    with pytest.raises(JsonLdSkillError) as caught:
        preflight_contexts(source, registry)
    assert caught.value.code == "cyclic_context"


def test_protected_term_redefinition_is_rejected(processor: ProfileJsonLdProcessor) -> None:
    source = load("examples/invalid/protected-term-redefinition.jsonld")
    with pytest.raises(JsonLdSkillError) as caught:
        processor.expand(source)
    assert caught.value.code == "protected_term_redefinition"


def test_null_context_cannot_remove_protected_terms(processor: ProfileJsonLdProcessor) -> None:
    source = {
        "@context": [
            {
                "label": {
                    "@id": "https://example.org/term/label",
                    "@protected": True,
                }
            },
            None,
        ],
        "label": "Example",
    }
    with pytest.raises(JsonLdSkillError) as caught:
        processor.expand(source)
    assert caught.value.code == "invalid_context_nullification"


def test_context_keyword_cannot_be_aliased(processor: ProfileJsonLdProcessor) -> None:
    source = {"@context": {"ctx": "@context"}, "@id": "https://example.org/system/a"}
    with pytest.raises(JsonLdSkillError) as caught:
        processor.expand(source)
    assert caught.value.code == "invalid_keyword_alias"


def test_illegal_container_combination_is_rejected(processor: ProfileJsonLdProcessor) -> None:
    source = {
        "@context": {
            "members": {
                "@id": "https://example.org/term/member",
                "@container": ["@id", "@type"],
            }
        },
        "members": {},
    }
    with pytest.raises(JsonLdSkillError) as caught:
        processor.expand(source)
    assert caught.value.code == "invalid_container_mapping"


def test_duplicate_json_keys_are_rejected() -> None:
    with pytest.raises(JsonLdSkillError) as caught:
        load_json_path(ROOT / "examples" / "invalid" / "duplicate-key.json")
    assert caught.value.code == "duplicate_key"


def test_rdf_example_is_valid_nquads() -> None:
    rdflib = pytest.importorskip("rdflib")
    dataset = rdflib.Dataset()
    dataset.parse(ROOT / "examples" / "rdf" / "system-bundle.nq", format="nquads")
    assert len(dataset) == 24


def test_registry_rejects_disallowed_scheme() -> None:
    registry = LocalDocumentRegistry(REGISTRY)
    with pytest.raises(JsonLdSkillError) as caught:
        registry.load("file:///etc/passwd")
    assert caught.value.code == "remote_scheme_rejected"
