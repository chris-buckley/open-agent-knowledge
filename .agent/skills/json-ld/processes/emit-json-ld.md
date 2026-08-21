<instructions>
You MUST validate the application model before emitting JSON-LD.
You MUST assign stable node and relationship identifiers before compaction.
You MUST use the governed context and local registry.
You MUST verify emitted graph meaning by re-expansion.
You MUST preserve output provenance and processor version.
</instructions>

<constants>
PROCESS_VERSION: "1.0.0"
DEFAULT_ENGINE: "pyld"
</constants>

<formats>
<format id="JSONLD_EMIT_V1" name="JSON-LD emit result" purpose="Report a governed JSON-LD emission result.">
## JSON-LD emission

Status: <STATUS>
Application source: <APPLICATION_PATH>
Output: <OUTPUT_PATH>
Output SHA-256: <OUTPUT_SHA256>
Processor: <PROCESSOR>
Semantic check: <SEMANTIC_STATUS>
Diagnostics: <DIAGNOSTICS>

WHERE:
- <APPLICATION_PATH> is Path; canonical application input path.
- <DIAGNOSTICS> is Markdown; ordered diagnostics or none.
- <OUTPUT_PATH> is Path; compact JSON-LD output path.
- <OUTPUT_SHA256> is String; lowercase SHA-256 of exact output bytes.
- <PROCESSOR> is String; processor name and exact version.
- <SEMANTIC_STATUS> is String; one of equivalent, different, not-run.
- <STATUS> is String; one of pass, fail.
</format>
</formats>

<processes>
<process id="emit-json-ld" name="Emit JSON-LD">
USE `Read` where: path=APPLICATION_PATH
CAPTURE APPLICATION_BYTES from `Read`
USE `ValidatePydantic` where: instance=APPLICATION_BYTES, model_path=MODEL_PATH
CAPTURE APPLICATION from `ValidatePydantic`
USE `ApplicationToJsonLd` where: application=APPLICATION, context_iri=CONTEXT_IRI
CAPTURE SOURCE_PROFILE from `ApplicationToJsonLd`
USE `LoadRegistry` where: path=REGISTRY_PATH
CAPTURE REGISTRY from `LoadRegistry`
USE `JsonLdExpand` where: document=SOURCE_PROFILE, engine=DEFAULT_ENGINE, registry=REGISTRY
CAPTURE EXPANDED from `JsonLdExpand`
USE `JsonLdCompact` where: context_path=CONTEXT_PATH, document=EXPANDED, engine=DEFAULT_ENGINE, registry=REGISTRY
CAPTURE COMPACT from `JsonLdCompact`
USE `Write` where: content=COMPACT, path=OUTPUT_PATH
USE `SemanticRoundtrip` where: context_path=CONTEXT_PATH, document=COMPACT, engine=DEFAULT_ENGINE, registry=REGISTRY
CAPTURE ROUNDTRIP from `SemanticRoundtrip`
SET OUTPUT_SHA256 := <SHA256> (from "Agent Inference" using COMPACT)
IF ROUNDTRIP.status != "equivalent":
  RETURN: format="JSONLD_EMIT_V1", application_path=APPLICATION_PATH, diagnostics=ROUNDTRIP, output_path=OUTPUT_PATH, output_sha256=OUTPUT_SHA256, processor=DEFAULT_ENGINE, semantic_status="different", status="fail"
RETURN: format="JSONLD_EMIT_V1", application_path=APPLICATION_PATH, diagnostics="none", output_path=OUTPUT_PATH, output_sha256=OUTPUT_SHA256, processor=DEFAULT_ENGINE, semantic_status="equivalent", status="pass"
</process>
</processes>

<input>
APPLICATION_PATH is the validated canonical application file.
MODEL_PATH is the Pydantic application model module.
CONTEXT_IRI is the immutable governed context identifier.
CONTEXT_PATH is the local reviewed context file.
REGISTRY_PATH is the exact local context registry.
OUTPUT_PATH is the compact JSON-LD output path.
</input>
