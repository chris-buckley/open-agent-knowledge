# Security and deterministic processing

Treat every external JSON-LD document and context as untrusted input. Contexts can redefine the meaning and type coercion of ordinary keys, trigger additional resource loading, and cause large expanded outputs. The security boundary starts before JSON parsing and continues through graph validation.

## Threat model

An untrusted document can attempt to:

- load attacker-controlled remote contexts;
- follow redirects into unexpected hosts or private networks;
- use `file:`, `data:`, or another dangerous scheme;
- replace or nullify protected definitions;
- create cyclic context references or imports;
- exploit duplicate JSON keys and parser disagreement;
- consume memory through deep nesting, large documents, lists, or expansion growth;
- make a familiar term expand to an unexpected predicate;
- create many blank nodes or repeated embeddings;
- exploit output order to win a duplicate-identity conflict;
- inject an absent or unauthorized graph target that remains structurally valid.

## Default policy

The supplied scripts MUST NOT retrieve arbitrary remote contexts. They resolve an exact HTTPS IRI only when [`examples/contexts/registry.json`](../examples/contexts/registry.json), or another explicit registry, pins:

- the IRI;
- the local file path;
- the expected SHA-256 digest;
- the allowed JSON-LD media type.

A missing entry is a rejection. There is no network fallback.

## Context allowlist and pinning

Use an exact-match registry rather than a suffix or substring allowlist. Hostname allowlists alone do not pin bytes, paths, redirects, or versions.

A context contract SHOULD use an immutable versioned IRI such as:

```text
https://example.org/context/system-v1.jsonld
```

The registry MUST bind that IRI to reviewed bytes. Updating the bytes at the same IRI changes the data contract and MUST trigger an integrity failure until the registry is deliberately updated.

## Integrity verification

Compute SHA-256 over the exact UTF-8 document bytes before parsing. Verify it against the registry. Preserve the digest in provenance.

A content digest proves byte identity, not trustworthiness. Review the context, namespace authority, and change process before allowlisting it.

## Offline operation

Offline processing is the default for reproducible builds and tests. A production loader MAY retrieve remote contexts only through a separately reviewed adapter that enforces all controls in this reference.

Do not let a processor's built-in loader bypass the application loader. The PyLD adapter always supplies the local registry loader.

## Redirect handling

The bundled loader performs no redirects because it performs no network requests.

A network-enabled adapter MUST:

1. Set a small redirect limit.
2. Revalidate scheme, host, port, and path at every hop.
3. Reject redirects to loopback, link-local, private, metadata, and local network addresses.
4. Reject HTTPS-to-HTTP downgrade.
5. Pin or verify final bytes.
6. Record the requested and final URL.
7. Use the final document URL correctly as the base where the JSON-LD API requires it.

## Content types

Accept only reviewed JSON-LD-compatible media types. The local registry accepts `application/ld+json` and `application/json`.

A network loader MUST reject HTML, scripts, archives, and ambiguous binary content unless a separate feature deliberately supports HTML extraction under strict controls. Do not sniff arbitrary content into JSON-LD.

## Size, timeout, and depth limits

Apply limits before invoking the processor:

- maximum input bytes;
- maximum registered context bytes;
- maximum JSON nesting depth;
- maximum context-reference depth;
- maximum total loaded documents;
- maximum expansion output bytes or node count;
- maximum frame embedding depth;
- maximum wall-clock time for network and processing;
- maximum redirects.

The bundled defaults are defined in [`scripts/jsonld_common.py`](../scripts/jsonld_common.py). CLI flags can lower or deliberately raise bounded limits.

A network adapter MUST set connect, response-header, body, and total timeouts. It MUST stream with a hard response-size cap rather than read an unbounded body.

## Cyclic contexts and imports

Reject:

- a context URL that reaches itself through remote context processing;
- cyclic `@import` chains;
- an imported context that itself contains `@import`, which JSON-LD 1.1 forbids;
- context-reference depth beyond the configured limit.

Do not rely only on a processor recursion error. Preflight references so diagnostics name the cycle and pinned resource.

## Protected terms and null contexts

Use `@protected` for contract-critical terms. Reject conflicting redefinitions. A null context cannot remove protected term definitions.

Protection does not make a remote context safe. It prevents selected active definitions from being silently changed later in context processing.

## Scheme restrictions

Reject at least:

- `file:` to prevent local-file access;
- `data:` to prevent unreviewed embedded remote documents;
- `ftp:` and `gopher:` as unsupported retrieval paths;
- scheme-relative URLs;
- unknown schemes.

The local registry requires HTTPS identifiers even though the bytes remain local.

## Duplicate JSON keys

JSON permits processors to handle duplicate object names inconsistently. Security-sensitive parsing MUST reject duplicates before JSON-LD processing.

The fixture [`examples/invalid/duplicate-key.json`](../examples/invalid/duplicate-key.json) demonstrates this error. The bundled parser reports the duplicated JSON path.

## Expansion growth

A small compact document can expand into many arrays, value objects, and nodes. A hostile frame can also repeat embedded data.

Measure and limit:

- input bytes;
- expanded object count;
- value count;
- node count;
- output bytes;
- embedding depth.

Process in an isolated worker with memory and CPU limits for high-risk ingestion. Do not expose the processor directly as an unrestricted web endpoint.

## Cache policy

A context cache MUST key by the full IRI and validated content identity. It MUST preserve the final URL and content type where those affect processing.

Invalidate or reject when:

- the configured digest changes;
- the context version changes;
- trust policy changes;
- the loader implementation changes materially;
- the cached content lacks provenance.

Do not use an unbounded global cache shared across tenants with different allowlists.

## Reproducible builds

A reproducible processing record SHOULD include:

- source digest;
- registry digest;
- every loaded context digest;
- processor name and version;
- Python version;
- processing mode;
- base IRI;
- frame and frame digest;
- all material algorithm options;
- selected root identifier;
- output digest;
- profile version.

The same record enables audit, cache keys, and regression testing.

## Trust boundaries

Separate these trust decisions:

1. The JSON bytes are syntactically safe to parse.
2. Every context was allowed and integrity checked.
3. JSON-LD processing succeeded without dropped or relative terms.
4. The selected frame produced the expected profile.
5. Pydantic and JSON Schema accepted the structure.
6. Graph targets, uniqueness, ownership, and provenance checks passed.
7. The application actor is authorized to use or mutate the referenced entities.

A successful earlier layer does not imply a successful later layer.

## Malicious remote-context example

[`examples/invalid/untrusted-remote-context.jsonld`](../examples/invalid/untrusted-remote-context.jsonld) uses an unapproved context URL. The safe loader rejects it before expansion.

```bash
python scripts/expand.py \
  examples/invalid/untrusted-remote-context.jsonld \
  --registry examples/contexts/registry.json \
  --engine profile
```

The command returns a non-zero exit code and a machine-readable `remote_context_rejected` error.

## Output safety

JSON-LD strings are still untrusted strings. Escape them for HTML, logs, shells, SQL, and other sinks using the sink's rules. Pydantic validation does not prove sink safety.

Machine-readable stdout MUST contain only the declared JSON result. The scripts direct errors to a structured envelope and use non-zero exit codes. A caller SHOULD separate progress logs from machine output.
