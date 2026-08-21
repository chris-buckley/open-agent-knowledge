# Contexts

Authority: [S01], [S02]. Security controls: [S08] in this skill.

## Contract role

`@context` maps local JSON terms and values into JSON-LD keywords and IRIs. It can also select compact shapes through coercion and container mappings. The same compact property name can have different graph meaning under different contexts, so a context is part of the data contract and MUST be versioned, governed, tested, and resolved reproducibly.

A context is not a structural schema. It does not require fields, enforce application cardinality, or prove graph targets. A context establishes interpretation. A JSON Schema and Pydantic profile establish selected structural and application rules.

## Context forms

A local context is the value of `@context` inside a JSON-LD document. It can be:

- An object containing context definitions.
- A string identifying a remote context document.
- An array containing objects, strings, or null, processed in order.
- Null, which requests context nullification subject to protected-term rules.

A remote context document MUST be a JSON object whose top-level object contains `@context`. The processor dereferences the remote IRI, takes that value, and recursively processes it. The loader and context processor MUST detect cycles. [S02]

Local object:

```json
{
  "@context": {
    "label": "https://example.org/term/label"
  }
}
```

Remote context:

```json
{
  "@context": "https://example.org/context/system-v1.jsonld"
}
```

Context array:

```json
{
  "@context": [
    "https://example.org/context/base-v1.jsonld",
    {
      "local_term": "https://example.org/term/local"
    }
  ]
}
```

Entries in a context array are processed from first to last. Later definitions can replace earlier definitions unless protection rules prohibit the replacement. An agent MUST review the whole active context, not only the nearest object literal.

## Simple and expanded term definitions

A simple term definition maps a term directly to an IRI or keyword.

```json
{
  "@context": {
    "label": "https://example.org/term/label",
    "id": "@id"
  }
}
```

An expanded term definition is an object that can declare the IRI mapping, reverse mapping, coercion, container, prefix behavior, scoped context, protection, language, or direction.

```json
{
  "@context": {
    "links_to": {
      "@id": "https://example.org/term/links_to",
      "@type": "@id",
      "@protected": true
    }
  }
}
```

Use an expanded definition when compact values need a declared interpretation or shape. Do not rely on a consumer guessing whether a string is a literal or node identifier.

## Absolute IRIs, compact IRIs, and terms

An absolute IRI carries its complete identity:

```text
https://example.org/system/orders
```

A compact IRI combines a prefix term and suffix:

```text
sys:orders
```

A term is a context-defined short name such as `label` or `Service`.

```json
{
  "@context": {
    "sys": {
      "@id": "https://example.org/system/",
      "@prefix": true
    },
    "schema": {
      "@id": "https://example.org/schema/",
      "@prefix": true
    },
    "Service": "schema:Service"
  }
}
```

The expanded identity of `sys:orders` is `https://example.org/system/orders`. The expanded identity of type `Service` is `https://example.org/schema/Service`.

A project SHOULD set `@prefix: true` explicitly on terms intended as prefixes. It MUST NOT assume that a visually similar prefix has the same expansion in another context.

## `@vocab`

`@vocab` sets the vocabulary mapping used for property names and type-like vocabulary values that are not otherwise terms, compact IRIs, or keywords.

```json
{
  "@context": {
    "@vocab": "https://example.org/term/"
  },
  "label": "Example",
  "@type": "System"
}
```

This can expand to the property `https://example.org/term/label` and type `https://example.org/term/System`.

`@vocab` does not make an ordinary `@id` value vocabulary-relative. Use an explicit compact IRI, absolute IRI, or an `@id` coercion with a governed base.

A broad `@vocab` makes compact authoring easy but can turn misspelled properties into unintended IRIs rather than obvious unknown terms. Profiles that require strict term sets SHOULD combine context processing with schema or application checks.

Set `@vocab` to null to remove a prior vocabulary mapping in the active context.

## `@base`

`@base` controls how document-relative IRI references are resolved, including relative `@id` values and values coerced to `@id`. It does not define the vocabulary used for property names.

```json
{
  "@context": {
    "@base": "https://example.org/system/",
    "related": {
      "@id": "https://example.org/term/related",
      "@type": "@id"
    }
  },
  "@id": "orders",
  "related": "orders/database"
}
```

A processor can resolve both relative values against the base. For durable cross-document application identities, authors SHOULD still prefer explicit absolute or compact IRIs so that identity does not depend on retrieval location.

When processing a remote context, the remote context's `@base` entry is ignored by the context-processing algorithm. The base URL used to resolve relative remote context references still comes from the retrieved context document location. [S02]

Set `@base` to null to remove an inherited base mapping.

## Default language and direction

A context can assign a default language to otherwise untagged strings:

```json
{
  "@context": {
    "@language": "en",
    "label": "https://example.org/term/label"
  },
  "label": "Service"
}
```

Expansion can produce:

```json
{
  "@value": "Service",
  "@language": "en"
}
```

A context can assign default text direction with `@direction` set to `ltr`, `rtl`, or null.

```json
{
  "@context": {
    "@language": "ar",
    "@direction": "rtl"
  }
}
```

Language tags and direction are semantic data. They are not display-only formatting. Applications MUST preserve them when they matter and MUST NOT collapse distinct language-tagged values into one untyped string without an explicit profile decision.

## Type coercion

A term definition can declare how compact scalar values expand.

### Node identifier coercion

```json
{
  "@context": {
    "links_to": {
      "@id": "https://example.org/term/links_to",
      "@type": "@id"
    },
    "sys": {
      "@id": "https://example.org/system/",
      "@prefix": true
    }
  },
  "links_to": "sys:base/service"
}
```

The string expands as a node reference, not a literal:

```json
{
  "https://example.org/term/links_to": [
    {
      "@id": "https://example.org/system/base/service"
    }
  ]
}
```

### Vocabulary coercion

`"@type": "@vocab"` interprets string values as vocabulary terms. Use it for values that name classes, predicates, or controlled vocabulary concepts, not ordinary entity identifiers.

### Datatype coercion

```json
{
  "@context": {
    "xsd": {
      "@id": "http://www.w3.org/2001/XMLSchema#",
      "@prefix": true
    },
    "confidence": {
      "@id": "https://example.org/term/confidence",
      "@type": "xsd:decimal"
    }
  },
  "confidence": 0.98
}
```

Expansion adds the datatype IRI to the value object. The application MUST still validate range rules such as `0 <= confidence <= 1`.

### JSON literal coercion

`"@type": "@json"` preserves a JSON value as an RDF JSON literal when converting to RDF. Use it only when the property intentionally carries an opaque JSON value. Do not use it to avoid modelling known structure.

## Language coercion

A term definition can apply a language and direction to that property's string values, overriding context defaults.

```json
{
  "@context": {
    "label_fr": {
      "@id": "https://example.org/term/label",
      "@language": "fr",
      "@direction": "ltr"
    }
  }
}
```

A term definition cannot combine language coercion with an ordinary datatype coercion. A value object cannot simultaneously carry both `@type` and `@language` or `@direction`. [S01]

## Scoped contexts

An expanded term definition can contain `@context`. The scope depends on how the term is used. [S01] [S02]

### Property-scoped context

When the term is used as a property, its scoped context applies while processing that property's value.

```json
{
  "@context": {
    "details": {
      "@id": "https://example.org/term/details",
      "@context": {
        "status": "https://example.org/term/detailStatus"
      }
    }
  },
  "details": {
    "status": "approved"
  }
}
```

Use property-scoped contexts when a nested authored shape needs local terms without changing the meaning of the same names elsewhere.

### Type-scoped context

When a term with a scoped context is used as a type, the context applies to nodes of that type.

```json
{
  "@context": {
    "Adaptor": {
      "@id": "https://example.org/schema/Adaptor",
      "@context": {
        "connects": {
          "@id": "https://example.org/term/links_to",
          "@type": "@id"
        }
      }
    }
  },
  "@type": "Adaptor",
  "connects": "https://example.org/system/base/service"
}
```

Scoped contexts are powerful and can make the same compact term mean different things in different scopes. A project SHOULD use them only when the authored-profile benefit outweighs debugging cost. An application profile SHOULD expand or frame before validation so Pydantic does not need to reproduce scope resolution.

## Context propagation

By default, a local context propagates to descendant node objects. A context can set `@propagate` to false so that the context applies to the current node but does not automatically propagate into nested node objects, subject to the detailed algorithm and previous-context rules. [S01] [S02]

Use non-propagating contexts when an outer object needs a local interpretation but embedded nodes must retain their own contexts. Test the exact expanded result. Do not infer propagation from JSON nesting alone.

## Protected terms

A context or individual term definition can set `@protected: true`. A protected term cannot be redefined by an ordinary later context. [S01] [S02]

```json
{
  "@context": {
    "@protected": true,
    "label": "https://example.org/term/label"
  }
}
```

Protected terms reduce silent semantic remapping. A governed public context SHOULD protect stable application terms. Context updates that need a different meaning SHOULD introduce a new context version or new term IRI instead of overriding a protected definition.

Nullifying a context that contains protected terms is an `invalid context nullification` error unless the calling algorithm explicitly permits overriding protection. Ordinary authored documents MUST NOT rely on such an override.

## Context import

A JSON-LD 1.1 context object can use `@import` to load another context object and reverse-merge it before applying local entries. Local entries can then refine or replace imported entries, subject to protection. [S01] [S02]

```json
{
  "@context": {
    "@import": "https://example.org/context/base-v1.jsonld",
    "local_term": "https://example.org/term/local"
  }
}
```

The imported document MUST resolve to a valid context object. The imported context object MUST NOT contain another `@import` entry. Imports MUST be pinned, cycle-checked, and bounded like other remote contexts. A project SHOULD avoid import chains because the normative import target cannot recursively import another context.

## Null contexts

A null context resets the active context to an initial context when legal. It can deliberately stop inherited terms from applying to a nested portion of a document.

```json
{
  "@context": {
    "label": "https://example.org/term/label"
  },
  "outer": {
    "@context": null,
    "label": "This name no longer has the outer mapping"
  }
}
```

The unmapped property can then be dropped during expansion or resolved by another mapping. Strict ingress SHOULD surface such dropped properties. Null contexts MUST NOT be used to bypass protected-term governance.

## Keyword aliasing

A term can alias a JSON-LD keyword:

```json
{
  "@context": {
    "id": "@id",
    "type": "@type"
  },
  "id": "https://example.org/system/orders",
  "type": "https://example.org/schema/System"
}
```

Keyword aliases are processing aliases. They do not create new graph predicates. Agents MUST apply keyword rules to aliases exactly as they apply to the keyword. JSON-LD 1.1 forbids aliasing `@context`. [S01]

Canonical `@id` and `@type` are usually clearer at system boundaries. Use legal keyword aliases only when an existing JSON shape requires them or a governed authoring profile gains clear value. Pydantic source models can accept either canonical keywords or declared aliases, but the selected profile SHOULD serialize one canonical form.

## Precedence and overriding

The active context is produced by ordered processing. Relevant precedence rules include:

1. Process context array entries in order.
2. Resolve imports before applying the importing object's own entries.
3. Process `@base`, `@direction`, `@language`, `@propagate`, `@version`, and `@vocab` before ordinary term definitions because they affect definition creation. [S02]
4. Apply local contexts and scoped contexts according to the node and property being processed.
5. Permit later ordinary definitions to replace earlier unprotected definitions.
6. Reject incompatible redefinition of protected terms.

An agent MUST diagnose the complete active context and expansion result before blaming the compact input. A property can be structurally unchanged while a later context changes its IRI or value coercion.

## Invalid context conditions

A processor can reject a context for reasons including:

- A local context has an invalid JSON-LD type.
- A remote context document lacks a top-level `@context`.
- Remote contexts or imports form a cycle.
- A term definition recursively depends on itself through unresolved definitions.
- A term maps to an invalid keyword-like value or invalid IRI mapping.
- `@id` and `@reverse` are both used in one term definition.
- A reverse-property definition uses an illegal container.
- `@type`, `@language`, `@direction`, or `@container` has an invalid value or combination.
- A protected term is redefined.
- A protected active context is nullified.
- `@version` conflicts with the selected processing mode.
- An `@import` target is invalid or cyclic.

Map processor error names to the practical fixes in [09 Error catalog](09-error-catalog.md).

## Context governance checklist

A production context contract MUST record:

- Immutable context IRI and semantic version.
- Content hash and retrieval policy.
- Namespace owners.
- Term IRI, value kind, coercion, and container for every application term.
- Protected terms.
- Default base, language, and direction decisions.
- Imports and scoped contexts.
- Compatibility policy for adding, deprecating, or changing terms.
- Golden expansion and compaction examples.
- Processor and processing mode used for verification.
- Security limits and offline registry mapping.

Follow [Design a context](../guides/design-a-context-v1.0.0.guide.md) and [Update a context](../processes/update-a-context.md).
