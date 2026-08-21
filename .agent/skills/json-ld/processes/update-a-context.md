<instructions>
You MUST treat a context as a versioned data contract.
You MUST compare every term definition before approving a change.
You MUST publish a new context identifier for breaking changes.
You MUST update registry integrity data deliberately.
You MUST rerun expansion, framing, model, and semantic tests.
You MUST preserve the previous context for historical documents.
</instructions>

<constants>
PROCESS_VERSION: "1.0.0"
BREAKING_CHANGES: TEXT<<
Changing an expanded IRI mapping.
Changing literal versus identifier coercion.
Changing a datatype, language, or direction coercion.
Changing a container in a way that alters the profile shape.
Removing or unprotecting a contract-critical term.
Changing scoped context propagation.
>>
</constants>

<formats>
<format id="JSONLD_CONTEXT_CHANGE_V1" name="JSON-LD context change result" purpose="Report review and verification of one context change.">
## JSON-LD context change

Status: <STATUS>
Previous context: <OLD_CONTEXT>
Candidate context: <NEW_CONTEXT>
Classification: <CLASSIFICATION>
Changed terms: <CHANGED_TERMS>
Registry digest: <REGISTRY_SHA256>
Tests: <TEST_RESULTS>
Diagnostics: <DIAGNOSTICS>

WHERE:
- <CHANGED_TERMS> is Markdown; added, removed, and changed term definitions.
- <CLASSIFICATION> is String; one of compatible, breaking, rejected.
- <DIAGNOSTICS> is Markdown; unresolved issues or none.
- <NEW_CONTEXT> is Path; candidate context path.
- <OLD_CONTEXT> is Path; previous context path.
- <REGISTRY_SHA256> is String; lowercase SHA-256 of the updated registry.
- <STATUS> is String; one of pass, fail.
- <TEST_RESULTS> is Markdown; executed checks and results.
</format>
</formats>

<processes>
<process id="update-a-context" name="Update a context">
USE `Read` where: path=OLD_CONTEXT
CAPTURE OLD_DOCUMENT from `Read`
USE `Read` where: path=NEW_CONTEXT
CAPTURE NEW_DOCUMENT from `Read`
USE `ContextDiff` where: new_context=NEW_DOCUMENT, old_context=OLD_DOCUMENT
CAPTURE DIFF from `ContextDiff`
SET CLASSIFICATION := <CHANGE_CLASS> (from "Agent Inference" using BREAKING_CHANGES, DIFF)
IF CLASSIFICATION = "breaking" AND NEW_CONTEXT_IRI = OLD_CONTEXT_IRI:
  RETURN: format="JSONLD_CONTEXT_CHANGE_V1", changed_terms=DIFF, classification="rejected", diagnostics="Breaking mappings require a new immutable context IRI.", new_context=NEW_CONTEXT, old_context=OLD_CONTEXT, registry_sha256="", status="fail", test_results="not run"
USE `ValidateJsonLdContext` where: context=NEW_DOCUMENT, registry_path=REGISTRY_PATH
CAPTURE CONTEXT_REPORT from `ValidateJsonLdContext`
USE `UpdateRegistry` where: context_iri=NEW_CONTEXT_IRI, context_path=NEW_CONTEXT, registry_path=REGISTRY_PATH
CAPTURE REGISTRY from `UpdateRegistry`
USE `RunTests` where: command=TEST_COMMAND, working_directory=SKILL_ROOT
CAPTURE TEST_RESULTS from `RunTests`
IF TEST_RESULTS.status != "pass":
  RETURN: format="JSONLD_CONTEXT_CHANGE_V1", changed_terms=DIFF, classification=CLASSIFICATION, diagnostics=CONTEXT_REPORT, new_context=NEW_CONTEXT, old_context=OLD_CONTEXT, registry_sha256=REGISTRY.sha256, status="fail", test_results=TEST_RESULTS
RETURN: format="JSONLD_CONTEXT_CHANGE_V1", changed_terms=DIFF, classification=CLASSIFICATION, diagnostics="none", new_context=NEW_CONTEXT, old_context=OLD_CONTEXT, registry_sha256=REGISTRY.sha256, status="pass", test_results=TEST_RESULTS
</process>
</processes>

<input>
SKILL_ROOT is the json-ld skill root.
OLD_CONTEXT is the previous context path.
NEW_CONTEXT is the candidate context path.
OLD_CONTEXT_IRI is the previous immutable context identifier.
NEW_CONTEXT_IRI is the candidate immutable context identifier.
REGISTRY_PATH is the local registry path.
TEST_COMMAND is the complete regression command.
</input>
