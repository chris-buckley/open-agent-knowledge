# 02 Identifiers and references

Authority: JSON Schema Draft 2020-12 Core, RFC 3986, and the official `referencing` documentation listed in [00 Source manifest](00-source-manifest.md).

## Schema identity is a URI

Use `$id` to establish the identifier and base URI of a schema resource.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/schema/system"
}
```

A canonical `$id` SHOULD be an absolute URI without a non-empty fragment. Treat it as an identifier, not a promise that network retrieval will succeed. A URI can identify a locally registered resource.

The root resource also has an initial base URI supplied by the retrieval or embedding context. A relative `$id` resolves against the current base and establishes a new base for its resource. Relative root identifiers make a schema's identity depend on how it was loaded, so published modules SHOULD use stable absolute identifiers.

Do not confuse these identities:

- `$id` identifies a schema resource.
- an instance field such as `"id": "node:orders"` identifies an application object by project convention.
- `$anchor` identifies a location inside a schema resource.
- a file path identifies one local copy of a document.

They MAY be related by application policy, but JSON Schema does not equate them.

## URI-reference resolution

Resolve `$ref` and `$dynamicRef` as RFC 3986 URI references against the current base URI. Do not concatenate strings or assume paths are relative to the referencing file after `$id` changes the base.

The same relative reference resolves differently under different bases:

```text
current base: https://example.org/schema/team-a/root
reference:    common.json
result:       https://example.org/schema/team-a/common.json

current base: https://example.org/schema/team-b/root
reference:    common.json
result:       https://example.org/schema/team-b/common.json
```

A nested relative `$id` changes the base again:

```json
{
  "$id": "https://example.org/schema/root",
  "$defs": {
    "part": {
      "$id": "parts/part",
      "properties": {
        "value": {"$ref": "value.json"}
      }
    }
  }
}
```

Inside `part`, `value.json` resolves to `https://example.org/schema/parts/value.json`, not to a filesystem sibling chosen by the loader.

## `$ref`

`$ref` is an applicator. Its value is a URI reference. The resolved target MUST identify a schema.

```json
{"$ref": "https://example.org/schema/system#/$defs/Identifier"}
```

In Draft 2020-12, sibling keywords next to `$ref` also apply:

```json
{
  "$ref": "#/$defs/Identifier",
  "description": "The source node identifier"
}
```

Do not use a `$ref` object as if it copied or merged JSON text. Evaluation follows the target schema while preserving resource identity and dynamic scope.

`$ref` does not represent a relationship between two system instances. A relationship object needs ordinary instance properties such as `kind`, `from`, and `to`; JSON Schema then validates their shape.

## JSON Pointer fragments

A fragment beginning with `/` is a JSON Pointer into the target schema resource:

```json
{"$ref": "#/$defs/Node"}
```

Escape `~` as `~0` and `/` as `~1` inside pointer tokens. Pointer fragments are tied to document structure and can break when definitions move. Prefer a named anchor for stable public entry points.

## `$anchor`

`$anchor` gives a subschema a plain-name fragment within its resource:

```json
{
  "$id": "https://example.org/schema/system",
  "$defs": {
    "identifier": {
      "$anchor": "identifier",
      "type": "string"
    }
  }
}
```

Reference it as:

```json
{"$ref": "https://example.org/schema/system#identifier"}
```

Use a normal `$anchor` unless recursive extension requires dynamic rebinding.

## `$dynamicAnchor` and `$dynamicRef`

`$dynamicAnchor` creates an anchor that can participate in dynamic scope. `$dynamicRef` first resolves like a normal URI reference. When its fragment names a dynamic anchor, evaluation can use the nearest matching dynamic anchor in the active dynamic scope.

Use this pair for recursive schemas designed to be extended at every recursive depth. Do not use it merely because a schema is recursive; an ordinary `$ref` is sufficient for fixed recursion.

The included tree schemas demonstrate the pattern:

```json
{
  "$id": "https://example.org/schema/tree",
  "$dynamicAnchor": "node",
  "properties": {
    "children": {
      "items": {"$dynamicRef": "#node"}
    }
  }
}
```

The strict extension repeats `"$dynamicAnchor": "node"`, adds `tag`, and references the base. The dynamic reference then applies the strict extension to descendants, not only to the root.

A static reference checker can prove that the initial target exists. Only actual evaluation can demonstrate the final dynamic-scope behavior. The included `check_references.py` reports this distinction.

## `$defs`

`$defs` is a container for reusable subschemas. Its members do not become active unless another keyword applies them. A key under `$defs` is not, by itself, a public identity.

Use local references for private definitions:

```json
{
  "$defs": {
    "Identifier": {"type": "string", "minLength": 1}
  },
  "$ref": "#/$defs/Identifier"
}
```

Give a nested definition its own `$id` or `$anchor` only when it needs an addressable resource or stable entry point.

## Embedded resources and compound documents

A nested `$id` creates an embedded schema resource. A compound schema document bundles several resources in one JSON document.

A bundle MUST preserve each resource's original `$id`. References inside the bundle SHOULD continue to use the same URIs they used before bundling. Bundling changes delivery, not identity.

An offline registry SHOULD register the canonical URI of every independent resource and then crawl embedded resources and anchors. It MUST detect two different contents registered under the same URI.

Do not rewrite canonical `$id` values to `file:` URIs when copying schemas into a repository. Map the canonical IDs to local files in a registry such as [`examples/registry.json`](../examples/registry.json).

## Cross-file modules

Use this safe pattern:

```text
canonical schema URI -> explicit local registry entry -> local JSON file
```

The file does not need a network-retrievable URL. The local registry is the resolution authority for a build.

A root schema MAY use an absolute cross-file reference:

```json
{
  "$ref": "https://example.org/schema/system#/$defs/NodeCore"
}
```

The validator MUST fail when the registry lacks that resource. It MUST NOT search the working directory, guess a filename, or fetch the network unless a separate loader policy explicitly permits it.

## Cycles and recursion

Reference cycles are legal. A cycle is not automatically an error. Evaluation terminates according to the instance structure and the applicable schema semantics.

Use ordinary recursive `$ref` for a fixed recursive contract. Use `$dynamicRef` only when an extension must replace the recursive target through dynamic scope.

Guard application code against hostile depth and size even when the schema is valid. JSON Schema does not prescribe parser, call-stack, memory, or time limits.

## Deterministic resolution checklist

An agent MUST:

1. Require an explicit `$schema` at each standalone document root.
2. Record each canonical `$id` exactly once.
3. Resolve relative IDs and references with RFC 3986 rules.
4. Preserve IDs when moving or bundling files.
5. preload every allowed resource into an immutable registry.
6. disable network retrieval by default.
7. fail on missing resources, duplicate URI mappings, invalid fragments, and unsupported dialects.
8. report both the authored reference and the absolute resolved URI.
