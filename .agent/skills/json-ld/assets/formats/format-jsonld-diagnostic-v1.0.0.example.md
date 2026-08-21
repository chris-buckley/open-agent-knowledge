<formats>
<format id="JSONLD_DIAGNOSTIC_V1" name="JSON-LD diagnostic" purpose="Report one JSON-LD processing or graph validation failure.">
## JSON-LD diagnostic

Code: <CODE>
Stage: <STAGE>
Message: <MESSAGE>
File: <FILE_PATH>
JSON path: <JSON_PATH>
Identifier: <IDENTIFIER>
Cause: <CAUSE>
Correction: <CORRECTION>

WHERE:
- <CAUSE> is String; original processor or validator cause.
- <CODE> is String; stable machine-readable diagnostic code.
- <CORRECTION> is String; one practical correction.
- <FILE_PATH> is Path; source file path or empty when unavailable.
- <IDENTIFIER> is String; affected JSON-LD IRI or empty when unavailable.
- <JSON_PATH> is String; JSON path or empty when unavailable.
- <MESSAGE> is String; concise failure description.
- <STAGE> is String; one of json, loading, context, expansion, compaction, flattening, framing, schema, pydantic, graph, rdf, security.
</format>
</formats>
