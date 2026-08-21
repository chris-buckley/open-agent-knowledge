<instructions>
You MUST verify processor and suite revisions before running official tests.
You MUST run local application tests separately from official processor tests.
You MUST not download test suites during this process.
You MUST preserve exact commands, versions, exit codes, and failing test identifiers.
You MUST not claim full conformance from a bounded subset.
</instructions>

<constants>
PROCESS_VERSION: "1.0.0"
PYLD_COMMIT_PREFIX: "104b85d"
API_SUITE_PREFIX: "289ebf3"
FRAMING_SUITE_PREFIX: "fa22874"
NORMALIZATION_SUITE_PREFIX: "fbcfce5"
</constants>

<formats>
<format id="JSONLD_CONFORMANCE_V1" name="JSON-LD conformance result" purpose="Report local and official JSON-LD verification.">
## JSON-LD conformance

Status: <STATUS>
Processor: <PROCESSOR>
Local tests: <LOCAL_RESULTS>
Official tests: <OFFICIAL_RESULTS>
Suite revisions: <SUITE_REVISIONS>
Unsupported coverage: <UNSUPPORTED>
Diagnostics: <DIAGNOSTICS>

WHERE:
- <DIAGNOSTICS> is Markdown; failures and exact commands or none.
- <LOCAL_RESULTS> is Markdown; local test count and result.
- <OFFICIAL_RESULTS> is Markdown; official suite result or not-run with reason.
- <PROCESSOR> is String; processor name and exact version.
- <STATUS> is String; one of pass, fail, partial.
- <SUITE_REVISIONS> is Markdown; verified repository commit identifiers.
- <UNSUPPORTED> is Markdown; coverage not established by this run.
</format>
</formats>

<processes>
<process id="run-conformance-tests" name="Run conformance tests">
USE `RunTests` where: command=LOCAL_TEST_COMMAND, working_directory=SKILL_ROOT
CAPTURE LOCAL_RESULTS from `RunTests`
IF LOCAL_RESULTS.status != "pass":
  RETURN: format="JSONLD_CONFORMANCE_V1", diagnostics=LOCAL_RESULTS, local_results=LOCAL_RESULTS, official_results="not run", processor=PROCESSOR, status="fail", suite_revisions="not checked", unsupported="official coverage"
IF PYLD_CHECKOUT = "":
  RETURN: format="JSONLD_CONFORMANCE_V1", diagnostics="Pinned PyLD checkout was not supplied.", local_results=LOCAL_RESULTS, official_results="not run", processor=PROCESSOR, status="partial", suite_revisions="declared only", unsupported="Official expansion, compaction, flattening, framing, RDF, and negative suite coverage was not established."
USE `VerifyRevision` where: expected=PYLD_COMMIT_PREFIX, path=PYLD_CHECKOUT
CAPTURE PYLD_REVISION from `VerifyRevision`
USE `VerifyRevision` where: expected=API_SUITE_PREFIX, path=API_SUITE_PATH
CAPTURE API_REVISION from `VerifyRevision`
USE `VerifyRevision` where: expected=FRAMING_SUITE_PREFIX, path=FRAMING_SUITE_PATH
CAPTURE FRAMING_REVISION from `VerifyRevision`
USE `VerifyRevision` where: expected=NORMALIZATION_SUITE_PREFIX, path=NORMALIZATION_SUITE_PATH
CAPTURE NORMALIZATION_REVISION from `VerifyRevision`
USE `RunTests` where: command=OFFICIAL_TEST_COMMAND, working_directory=PYLD_CHECKOUT
CAPTURE OFFICIAL_RESULTS from `RunTests`
IF OFFICIAL_RESULTS.status != "pass":
  RETURN: format="JSONLD_CONFORMANCE_V1", diagnostics=OFFICIAL_RESULTS, local_results=LOCAL_RESULTS, official_results=OFFICIAL_RESULTS, processor=PROCESSOR, status="fail", suite_revisions=[PYLD_REVISION, API_REVISION, FRAMING_REVISION, NORMALIZATION_REVISION], unsupported="none declared beyond processor documentation"
RETURN: format="JSONLD_CONFORMANCE_V1", diagnostics="none", local_results=LOCAL_RESULTS, official_results=OFFICIAL_RESULTS, processor=PROCESSOR, status="pass", suite_revisions=[PYLD_REVISION, API_REVISION, FRAMING_REVISION, NORMALIZATION_REVISION], unsupported="none declared beyond processor documentation"
</process>
</processes>

<input>
SKILL_ROOT is the json-ld skill root.
PROCESSOR is the processor name and exact version.
LOCAL_TEST_COMMAND is the local pytest command.
PYLD_CHECKOUT is the optional trusted PyLD v3.1.0 checkout.
API_SUITE_PATH is the API suite checkout path.
FRAMING_SUITE_PATH is the framing suite checkout path.
NORMALIZATION_SUITE_PATH is the normalization suite checkout path.
OFFICIAL_TEST_COMMAND is the upstream suite command.
</input>
