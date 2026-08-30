# Pydantic v2 JSON Schema & JSON -- Pitfalls

## 1. model_json_schema() returns a dict, not a JSON string

`model_json_schema()` and `TypeAdapter.json_schema()` return a jsonable dict, not a string. Call `json.dumps()` on the result if you need a JSON string. Do not confuse with `model_dump_json()` which serializes a model _instance_ to a JSON string.

## 2. GenerateJsonSchema is single-use

A `GenerateJsonSchema` instance can only be used once. After calling `generate()` or `generate_definitions()`, the instance is marked as used and will raise `PydanticUserError` on a second call. Always create a new instance for each schema generation.

## 3. Validation vs serialization mode differences

The default mode is `'validation'`. If your schema is consumed by something that reads serialized output (e.g., documenting API responses), you need `mode='serialization'`. Key differences:
- `Decimal`: validation accepts `number | string`, serialization is `string` only.
- Computed fields: only appear in serialization mode.
- Custom serializers (e.g., `PlainSerializer(str)` on an `int`): the serialization schema reflects the serializer output type, not the input type.

## 4. WithJsonSchema replaces the entire base schema

When using `WithJsonSchema({'examples': [1, 2]})`, you must also include `'type': 'integer'` (or whatever the base type is). It overrides the _entire_ generated base schema, not just appends to it. Normal modifications like auto-generated `title` are still applied on top.

## 5. json_schema_extra dict vs callable -- no mixing

You cannot compose a dict-type and a callable-type `json_schema_extra` in the same annotation stack. Use all dicts (which merge) or all callables. If you need both behaviors, use a callable that performs the dict update internally.

## 6. $ref inlining for modified sub-models

Sub-models with Field-level customizations (custom `title`, `description`, or `default`) are recursively inlined in the parent schema instead of being stored in `$defs` and referenced via `$ref`. This can bloat the schema if the same model is used in many places with different Field overrides.

## 7. by_alias=True is the default

JSON schema generation uses aliases as property keys by default. If your model has `Field(alias='...')`, the schema will use those aliases. Pass `by_alias=False` to use Python attribute names instead. This catches people who set aliases for serialization but expect attribute names in the schema.

## 8. Strict mode behaves differently for JSON vs dict input

`model_validate_json()` with `strict=True` is more lenient than `model_validate()` with `strict=True`:
- JSON parsing: `"1987-01-28"` string is accepted for `date`, `[1, 2]` array is accepted for `tuple`.
- Dict validation: `'1987-01-28'` string is rejected for `date`, `[1, 2]` list is rejected for `tuple`.

This is by design -- JSON has fewer native types, so coercion from JSON-native representations is allowed even in strict mode.

## 9. Partial JSON parsing requires default values

When using `from_json(data, allow_partial=True)`, incomplete fields are simply dropped from the parsed dict. If your model fields lack defaults, validation will fail with `missing` errors. Give all fields defaults (or use `Optional` with `None` default) for reliable partial parsing.

## 10. Callable and isinstance types have no JSON schema

Types validated via `isinstance` checks or `Callable` have no JSON schema representation. By default, they raise `PydanticInvalidForJsonSchema`. Options:
- Use `WithJsonSchema` annotation to provide a schema.
- Subclass `GenerateJsonSchema` and override `handle_invalid_for_json_schema` to raise `PydanticOmit` (silently drops the field).
- Use `SkipJsonSchema` to exclude the field.

## 11. ref_template changes $ref values but not $defs location

Setting `ref_template='#/components/schemas/{model}'` changes the `$ref` values in the schema, but definitions are still stored under the `$defs` key. You may need to post-process the schema dict to move definitions under `components/schemas` for OpenAPI compliance.

## 12. __get_pydantic_json_schema__ must call resolve_ref_schema

When implementing `__get_pydantic_json_schema__`, call `handler.resolve_ref_schema(json_schema)` before mutating the schema. If the schema is a `$ref`, modifying it directly will not work -- you need the resolved schema dict.

## 13. __get_pydantic_core_schema__ for custom types vs Annotated metadata

- Custom types (used as `field: MyType`): do NOT call `handler(source)` -- it will raise `PydanticSchemaGenerationError` because Pydantic cannot introspect your custom type. Build the core schema from scratch.
- Annotated metadata (used as `field: Annotated[str, MyMeta()]`): DO call `handler(source)` to get the inner type's schema, then wrap or modify it.

## 14. namedtuple and Decimal schema surprises

- `namedtuple` has no JSON equivalent; it is represented as an array in JSON schema.
- `Decimal` is exposed as a string (with a regex pattern), not a number. In validation mode, it accepts both number and string via `anyOf`.

## 15. Optional fields include null in schema

`Optional[X]` (or `X | None`) always generates `anyOf: [{...X schema...}, {type: null}]` in the JSON schema. There is no way to suppress the null branch without using `SkipJsonSchema[None]` in the union.

## 16. model_json_schema on BaseModel itself raises

Calling `BaseModel.model_json_schema()` directly (not on a subclass) raises `AttributeError`. Always call it on a concrete model subclass.

## 17. String caching can mask memory issues

The default `cache_strings=True` caches all parsed strings shorter than 64 characters in a 16K-entry cache. For workloads with highly diverse string values and minimal repetition, this adds overhead with no benefit. Set `cache_strings=False` in those cases.
