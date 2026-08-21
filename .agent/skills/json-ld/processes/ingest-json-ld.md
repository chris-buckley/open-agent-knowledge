<instructions>
You MUST treat external JSON-LD as untrusted input.
You MUST resolve remote resources through an explicit local registry.
You MUST expand before interpreting compact terms.
You MUST frame into a governed application profile before Pydantic validation.
You MUST report graph-wide target failures separately from structural failures.
You MUST preserve source and processing provenance.
</instructions>

<constants>
PROCESS_VERSION: "1.0.0"
DEFAULT_ENGINE: "pyld"
</constants>

<formats>
<format id="JSONLD_INGEST_V1" name="JSON-LD ingest result" purpose="Report a governed JSON-LD ingestion result.">
## JSON-LD ingestion

Status: <STATUS>
Source: <SOURCE_PATH>
Source SHA-256: <SOURCE_SHA256>
Application artifact: <APPLICATION_PATH>
Root identifier: <ROOT_ID>
Processor: <PROCESSOR>
Diagnostics: <DIAGNOSTICS>

WHERE:
- <APPLICATION_PATH> is Path; path to the validated canonical application artifact or empty on failure.
- <DIAGNOSTICS> is Markdown; ordered diagnostics grouped by processing layer.
- <PROCESSOR> is String; processor name and exact version.
- <ROOT_ID> is String; selected root identifier or empty on failure.
- <SOURCE_PATH> is Path; original input path.
- <SOURCE_SHA256> is String; lowercase SHA-256 of exact source bytes.
- <STATUS> is String; one of pass, fail.
</format>
</formats>

<processes>
<process id="ingest-json-ld" name="Ingest JSON-LD">
USE `Read` where: path=SOURCE_PATH
CAPTURE SOURCE_BYTES from `Read`
SET SOURCE_SHA256 := <SHA256> (from "Agent Inference" using SOURCE_BYTES)
USE `ValidateJson` where: duplicate_keys="reject", max_bytes=MAX_BYTES, max_depth=MAX_DEPTH, source=SOURCE_BYTES
CAPTURE SOURCE_DOCUMENT from `ValidateJson`
USE `LoadRegistry` where: path=REGISTRY_PATH
CAPTURE REGISTRY from `LoadRegistry`
USE `JsonLdExpand` where: document=SOURCE_DOCUMENT, engine=DEFAULT_ENGINE, registry=REGISTRY
CAPTURE EXPANDED from `JsonLdExpand`
USE `JsonLdFlatten` where: document=EXPANDED, engine=DEFAULT_ENGINE, registry=REGISTRY
CAPTURE FLATTENED from `JsonLdFlatten`
USE `GraphInspect` where: document=FLATTENED, external_ids=EXTERNAL_IDS
CAPTURE GRAPH_REPORT from `GraphInspect`
IF GRAPH_REPORT.status = "fail":
  RETURN: format="JSONLD_INGEST_V1", application_path="", diagnostics=GRAPH_REPORT, processor=DEFAULT_ENGINE, root_id="", source_path=SOURCE_PATH, source_sha256=SOURCE_SHA256, status="fail"
USE `JsonLdFrame` where: document=EXPANDED, engine=DEFAULT_ENGINE, frame_path=FRAME_PATH, registry=REGISTRY
CAPTURE FRAMED from `JsonLdFrame`
USE `ValidateJsonSchema` where: instance=FRAMED, schema_path=SCHEMA_PATH
CAPTURE SCHEMA_REPORT from `ValidateJsonSchema`
USE `ValidatePydantic` where: external_ids=EXTERNAL_IDS, instance=FRAMED, model_path=MODEL_PATH
CAPTURE APPLICATION from `ValidatePydantic`
USE `Write` where: content=APPLICATION, path=APPLICATION_PATH
RETURN: format="JSONLD_INGEST_V1", application_path=APPLICATION_PATH, diagnostics=SCHEMA_REPORT, processor=DEFAULT_ENGINE, root_id=ROOT_ID, source_path=SOURCE_PATH, source_sha256=SOURCE_SHA256, status="pass"
</process>
</processes>

<input>
SOURCE_PATH is the untrusted JSON-LD file.
REGISTRY_PATH is the exact local context registry.
FRAME_PATH is the governed application frame.
SCHEMA_PATH is the Draft 2020-12 application-profile schema.
MODEL_PATH is the Pydantic source and canonical model module.
APPLICATION_PATH is the canonical output path.
ROOT_ID is the required application root identifier.
EXTERNAL_IDS is the approved external identifier set.
MAX_BYTES and MAX_DEPTH are governed resource limits.
</input>
