# 03 Validation keywords

Authority: JSON Schema Draft 2020-12 Core and Validation specifications listed in [00 Source manifest](00-source-manifest.md).

## Type-sensitive evaluation

Most validation keywords apply only to compatible instance types. A string keyword does not reject a number merely because the number is not a string. Add `type` when the type is part of the contract.

```json
{"type": "string", "minLength": 1}
```

Use `type` with a string or a unique array of names from `null`, `boolean`, `object`, `array`, `number`, `string`, and `integer`.

`integer` accepts any JSON number with a zero fractional part. A parser may represent `1` and `1.0` differently, but both are mathematically integral for JSON Schema.

## Any-instance assertions

- `const` accepts only a value equal to its keyword value.
- `enum` accepts a value equal to one of the array members.

Both MAY contain any JSON types, including null, arrays, and objects. Prefer `const` for one tag value and `enum` for a finite choice.

```json
{"const": "retail-lending"}
```

## Null and boolean

Use explicit types:

```json
{"type": "null"}
```

```json
{"type": "boolean"}
```

For nullable values, use a JSON Schema union:

```json
{"type": ["string", "null"]}
```

Do not use the older OpenAPI-only `nullable` keyword in Draft 2020-12 schemas.

## Numbers and integers

- `minimum` and `maximum` are inclusive numeric bounds.
- `exclusiveMinimum` and `exclusiveMaximum` are numeric exclusive bounds in Draft 2020-12.
- `multipleOf` MUST be a number greater than zero; division of the instance by it must produce an integer.

```json
{
  "type": "number",
  "minimum": 0,
  "exclusiveMaximum": 100,
  "multipleOf": 0.01
}
```

Do not use the obsolete boolean form of exclusive bounds from old drafts.

JSON permits arbitrary-precision numbers conceptually. Implementations can lose precision through native floating-point representations. For money and exact decimal multiples, define a project representation policy, test boundary values, and consider scaled integers or strings when implementation precision cannot be controlled.

## Strings

- `minLength` and `maxLength` count JSON string characters, not encoded bytes or displayed grapheme clusters.
- `pattern` uses an ECMA-262 compatible regular-expression dialect and succeeds when any substring matches.
- `format` supplies semantic format information and is an annotation in the general Draft 2020-12 dialect.

Anchor a whole-string pattern explicitly:

```json
{
  "type": "string",
  "pattern": "^[A-Z]{3}$"
}
```

A bare pattern such as `p` matches any string containing `p`. Use portable ECMA-262 constructs, test with non-ASCII data, and avoid implementation-specific flags or lookarounds unless every target supports them.

Regular expressions can cause excessive CPU use. A validator or gateway SHOULD bound input size and evaluation time for untrusted schemas or instances.

The included schema checker relies on meta-schema type checks for `pattern` and `patternProperties`; it does not claim that Python's regular-expression parser proves ECMA-262 portability. The selected validator evaluates patterns with its implementation engine, so a project MUST test every portability-sensitive expression on each target runtime.

## `format` annotation and assertion

The general Draft 2020-12 meta-schema requires support for the Format Annotation vocabulary and marks the Format Assertion vocabulary optional. Therefore `"format": "uri"` does not, by itself, guarantee validation failure for a malformed URI.

A toolchain MUST choose and disclose one policy:

- annotation policy: collect or expose format names without asserting them;
- assertion policy: enable a checker for every used format and fail when a checker is unavailable;
- custom dialect policy: declare the Format Assertion vocabulary as required in a meta-schema and use an implementation that supports it.

The included validator defaults to `annotation` and offers `--format-policy assert-known`. It refuses assertion mode when any used format has no registered checker.

Do not assume every implementation checks the same optional formats or edge cases. Add ordinary assertions, such as `pattern`, when a portable structural subset matters independently of format support.

## Content annotations

`contentEncoding`, `contentMediaType`, and `contentSchema` describe string-encoded content. They are annotations in Draft 2020-12.

```json
{
  "type": "string",
  "contentEncoding": "base64",
  "contentMediaType": "image/png"
}
```

A validator MUST NOT automatically decode, parse, or validate embedded content by default. An application MAY add a separate bounded content-processing step. It MUST report that result separately from validation of the enclosing JSON instance.

Do not use content keywords as a security boundary. Limit decoded size, allowed media types, parser features, and recursion in the content processor.

## Object validation

Use these keywords for object shape:

- `properties` applies named subschemas when those properties exist.
- `required` requires property names independently of `properties`.
- `patternProperties` applies subschemas to names matching regular expressions.
- `additionalProperties` applies to names not matched by `properties` or `patternProperties` in the same schema object.
- `propertyNames` validates each property name as a string instance.
- `minProperties` and `maxProperties` bound property count.
- `dependentRequired` requires peer properties when a trigger property exists.
- `dependentSchemas` applies a whole subschema when a trigger property exists.
- `unevaluatedProperties` applies to properties not successfully evaluated by other applicable keywords.

`properties` does not make properties required:

```json
{
  "type": "object",
  "properties": {"owner": {"type": "string"}},
  "required": ["owner"]
}
```

`patternProperties` patterns are not implicitly anchored. Use `^x-` to match a prefix rather than any name containing `x-`.

### Why `additionalProperties: false` surprises under composition

`additionalProperties` sees only sibling `properties` and `patternProperties` in the same schema object. It does not treat properties declared in another `allOf` branch as known.

This fails to extend a closed base:

```json
{
  "allOf": [
    {
      "type": "object",
      "properties": {"id": {"type": "string"}},
      "additionalProperties": false
    },
    {
      "type": "object",
      "properties": {"domain": {"type": "string"}}
    }
  ]
}
```

The base branch sees `domain` as additional and rejects it.

Close the final composed record with `unevaluatedProperties: false` instead:

```json
{
  "allOf": [
    {"$ref": "https://example.org/schema/system"},
    {
      "type": "object",
      "properties": {"domain": {"const": "retail-lending"}},
      "required": ["domain"]
    }
  ],
  "unevaluatedProperties": false
}
```

Successful evaluation through `$ref`, `allOf`, and selected conditional branches can mark properties as evaluated before the final closure runs. Put the closure at the leaf contract that knows the complete property set.

## Conditional object extension

Annotations from a successful `then` or `else` branch also participate in unevaluated tracking:

```json
{
  "type": "object",
  "properties": {
    "kind": {"enum": ["service", "store"]}
  },
  "required": ["kind"],
  "if": {"properties": {"kind": {"const": "service"}}},
  "then": {
    "properties": {"endpoint": {"type": "string"}},
    "required": ["endpoint"]
  },
  "else": {
    "properties": {"engine": {"type": "string"}},
    "required": ["engine"]
  },
  "unevaluatedProperties": false
}
```

## Array validation

- `prefixItems` applies positional schemas to the matching leading indices.
- `items` applies one schema to indices after `prefixItems`, or to every item when `prefixItems` is absent.
- `contains` requires at least one matching item unless adjacent `minContains` changes the lower bound.
- `minContains` and `maxContains` bound the number of `contains` matches.
- `minItems` and `maxItems` bound array length.
- `uniqueItems: true` requires pairwise unique JSON values.
- `unevaluatedItems` applies to indices not successfully evaluated by other applicable array keywords.

Draft 2020-12 tuple form:

```json
{
  "type": "array",
  "prefixItems": [
    {"type": "string"},
    {"type": "integer"}
  ],
  "items": false
}
```

This accepts exactly a string followed by an integer. In older drafts, an array-valued `items` plus `additionalItems` expressed tuple validation. Treat that form only as a migration note; do not author it in this skill.

A homogeneous array uses one `items` schema:

```json
{"type": "array", "items": {"$ref": "#/$defs/Node"}}
```

`contains` evaluates matches rather than positions selected by `prefixItems` or `items`:

```json
{
  "type": "array",
  "contains": {"type": "string", "const": "primary"},
  "minContains": 1,
  "maxContains": 1
}
```

When `contains` is absent, `minContains` and `maxContains` have no effect. The default lower bound with `contains` is one. `minContains: 0` is useful only with a meaningful upper bound or annotation purpose.

`uniqueItems` compares complete JSON values, not only an `id` field. It cannot generally enforce unique object identifiers. Use a graph or application-level uniqueness check.

## Annotations and documentation

The Metadata vocabulary defines:

- `title` - a short human-readable name;
- `description` - explanatory text;
- `default` - an associated default value, not insertion behavior;
- `examples` - sample values;
- `deprecated` - advice to avoid a location;
- `readOnly` - advice that the owning authority manages the value;
- `writeOnly` - advice that retrieved representations omit the value.

Editors, documentation generators, form builders, and language servers MAY use these annotations for labels, hover text, completion, examples, warnings, or input controls. Validators are not required to enforce application behavior from them.

An agent SHOULD ensure defaults and examples validate against the adjacent schema even though the specification only recommends it. An agent MUST define API behavior separately for `readOnly` and `writeOnly` when those flags affect requests or responses.
