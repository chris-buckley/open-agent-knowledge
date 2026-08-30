# 01 Core and vocabularies

Authority: JSON Schema Draft 2020-12 Core and Validation specifications listed in [00 Source manifest](00-source-manifest.md).

## Instance and schema

A JSON instance is the JSON value being described or checked. It MAY be any JSON value: null, boolean, string, number, array, or object.

A JSON Schema is a JSON value interpreted as a schema under a dialect. A schema is either an object or a boolean. `true` accepts every instance. `false` accepts no instance.

An agent MUST keep these levels separate:

```text
schema document -> interpreted under a dialect -> evaluates an instance
```

A validator normally evaluates and reports. It does not normally edit, coerce, fill, sort, dereference, or normalize the instance. An application MAY perform those actions in a separate step, but it MUST NOT describe them as JSON Schema validation.

## Documents, subschemas, and resources

A schema document is one JSON document that contains a root schema. Nested schema-valued keywords contain subschemas.

A schema resource is a schema with its own identity and resource root. The document root is always a resource. A nested schema becomes another resource when a nested `$id` establishes its identity. One document can therefore contain several resources.

Use these terms precisely:

- `document` concerns physical JSON packaging.
- `resource` concerns schema identity and reference scope.
- `subschema` concerns a schema nested under a schema-valued keyword.
- `root schema` concerns the schema at a document or resource boundary.

A document boundary does not always equal a resource boundary. Reference resolution follows resource identity and base URIs, not directory intuition.

## Dialects, meta-schemas, and vocabularies

A dialect is the complete language used to interpret a schema. A dialect combines vocabularies and is identified by the URI in `$schema`.

A meta-schema is a JSON Schema that describes valid schemas for a dialect or vocabulary. Meta-schema validation checks schema syntax and keyword value shapes. It does not prove that every implementation supports every declared vocabulary correctly.

A vocabulary is a named set of keywords with defined syntax and semantics. Draft 2020-12 separates, among others, the Core, Applicator, Validation, Unevaluated, Format Annotation, Format Assertion, Content, and Metadata vocabularies.

`$vocabulary` belongs in a meta-schema resource. It declares vocabulary URIs and boolean support requirements:

- `true` means an implementation MUST understand that vocabulary to process schemas using the meta-schema.
- `false` means an implementation that does not understand it SHOULD continue, normally treating unknown keywords as annotations.

An ordinary application schema MUST NOT use `$vocabulary` as a feature flag. The keyword is ignored when the document is not being processed as a meta-schema.

## Keyword roles

JSON Schema keywords have three main evaluation roles:

- An applicator applies one or more subschemas to instance locations. Examples include `properties`, `items`, `allOf`, and `$ref`.
- An assertion can cause validation failure. Examples include `type`, `required`, `minimum`, and `maxItems`.
- An annotation records information from successful evaluation. Examples include `title`, `description`, and the default Draft 2020-12 behavior of `format`.

A keyword can have more than one defined behavior in a vocabulary. Annotation collection also drives `unevaluatedProperties` and `unevaluatedItems`, so implementations must track which locations were successfully evaluated.

Unknown keywords are normally treated as annotations. This extensibility rule does not prove that an implementation supports the vocabulary that defined them. A production toolchain SHOULD reject a required unknown vocabulary before instance validation.

## Validation does not insert defaults

`default` is a metadata annotation. It associates a JSON value with a schema location. It does not instruct a validator to create a missing property or replace a value.

An application MAY use `default` during form generation or instance construction. That application MUST define when defaults apply, how competing annotations are resolved, and whether the resulting instance is validated again.

The examples deliberately include a `default: []` annotation on `children`, but every container still requires `children`. The validator will not insert the array.

## Schema validity and instance validity

Schema validity asks whether a schema conforms to its declared meta-schema. Instance validity asks whether an instance successfully evaluates against a valid schema.

Run these as separate gates:

```text
1. Parse JSON.
2. Select and support the declared dialect.
3. Validate the schema against its meta-schema.
4. Resolve every required schema resource.
5. Evaluate the instance.
6. Run application-level semantic checks.
```

A malformed schema can make an instance result meaningless. A valid schema can still reject an instance. A structurally valid instance can still violate graph-wide or business rules.

## Structural and graph-wide validation

JSON Schema evaluates the JSON representation and the locations reached by schema applicators. It can require a `from` property to be a non-empty string. It does not, in the general case, prove that the string names another object elsewhere in a graph.

Use a separate graph validation layer for rules such as:

- every relationship target exists;
- identifiers are unique across recursive containment;
- a relationship kind permits particular endpoint kinds;
- no containment cycle exists;
- a decision is authorized by an owner;
- values in separate documents agree;
- a JSON-LD term expands to the intended IRI.

The included [`check_graph_targets.py`](../scripts/check_graph_targets.py) demonstrates one bounded post-schema rule. It is explicitly a project checker, not a JSON Schema feature.

## Dialect declaration

A standalone schema in this skill MUST begin with:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema"
}
```

`$schema` MUST be an absolute normalized URI. In Draft 2020-12 it identifies both the dialect and its meta-schema. The specification recommends placing it in the document root and permits it at embedded resource roots.

When `$schema` is absent, behavior is implementation-defined. Some libraries choose a default or latest draft. This skill treats omission as an error because a hidden draft choice makes results non-portable.

The scripts also reject a different dialect rather than silently falling back to Draft 7, 2019-09, or a library default.

## Unsupported dialects and vocabularies

A tool MUST report an unsupported `$schema` URI before instance validation. It MUST NOT reinterpret the schema as a familiar draft.

For a custom dialect, a tool MUST inspect its meta-schema and `$vocabulary` declaration. It MUST refuse a vocabulary marked `true` when it lacks the required implementation. It SHOULD report unsupported optional vocabularies marked `false` and continue only under an explicit policy.

The included scripts intentionally support only the general Draft 2020-12 dialect. They do not claim to discover and execute arbitrary custom vocabularies.
