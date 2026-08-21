# Pydantic v2 Serialization -- Pitfalls

## 1. Subclass fields silently dropped

By default, if a field is annotated as `User` but you pass a `UserLogin(User)` instance, `model_dump()` only includes `User`'s fields. The `password` field on `UserLogin` is silently dropped. This is intentional (security by design) but surprising if you expect V1 behavior.

Fix: Use `SerializeAsAny[User]` on the field annotation, or pass `serialize_as_any=True` at call time.

## 2. serialize_as_any=True is global

The `serialize_as_any=True` runtime flag applies to all fields in the dump, not just the ones where duck typing matters. This can expose unintended subclass fields across the entire model tree.

Fix: Prefer `SerializeAsAny[T]` on specific fields instead of the global runtime flag.

## 3. Only one serializer per field

You cannot stack multiple `PlainSerializer`, `WrapSerializer`, or `@field_serializer` decorators on the same field. The last one wins or an error is raised. This includes mixing annotated-pattern and decorator-pattern serializers.

## 4. Plain serializer bypasses type validation on output

A `PlainSerializer` (or `@field_serializer` with `mode='plain'`) completely replaces the default serialization. If you return a value that does not match the field's type, Pydantic will not validate the output against the field type unless you explicitly set `return_type`.

```python
# This returns a string even though the field is `int` -- no error raised
DoubleInt = Annotated[int, PlainSerializer(lambda v: str(v))]
```

Fix: Set `return_type` explicitly on serializers when the output type differs from the input, or rely on the function's return type annotation.

## 5. mode='json' on model_dump() vs model_dump_json()

`model_dump(mode='json')` returns a Python dict with JSON-compatible values (lists instead of tuples, ISO strings instead of datetimes). It does not return a JSON string. `model_dump_json()` returns an actual JSON string. Confusing the two leads to type errors downstream.

## 6. exclude_unset tracks instantiation, not current state

`exclude_unset=True` omits fields not in `model_fields_set`. But if you mutate a field after construction (`m.age = 21`), that field is added to `model_fields_set`. It will then appear in the output even though it was not provided during instantiation.

## 7. Field-level exclude=True overrides include

If a field has `Field(exclude=True)`, passing `include={'that_field'}` in `model_dump()` will not bring it back. Field-level exclusion always wins.

## 8. dict(model) does not recursively convert sub-models

Calling `dict(model)` (or iterating) yields field values as-is. Sub-models remain as model instances, not dicts. Use `model_dump()` for recursive conversion.

## 9. model_validate_json strict mode accepts more than model_validate

In `strict=True` mode, `model_validate_json('{"when": "1987-01-28"}')` succeeds for a `date` field (JSON string to date coercion is allowed), but `model_validate({'when': '1987-01-28'})` raises a validation error (Python string to date is not allowed in strict mode). This asymmetry is by design but can cause confusion in tests.

## 10. Partial JSON parsing requires default values

`pydantic_core.from_json(data, allow_partial=True)` silently drops incomplete fields. If model fields lack defaults, validation will fail with `missing` errors on the dropped fields.

Fix: Give all fields defaults (or use a `WrapValidator` that catches `missing` errors and raises `PydanticUseDefault`).

## 11. @field_serializer('*') applies to subclass fields too

Passing `'*'` as the field name to `@field_serializer` matches all fields, including those defined on subclasses. This can cause unexpected serialization behavior when models are extended.

## 12. check_fields=False needed for base class serializers

If you define `@field_serializer('some_field')` on a base class where `some_field` does not exist (it exists only on subclasses), model creation raises an error by default.

Fix: Pass `check_fields=False` to the decorator.

## 13. Wrap serializer handler output type depends on mode

In a `WrapSerializer`, the `handler(value)` return type differs between Python and JSON modes. In Python mode, it returns the Python-native type. In JSON mode, it returns the JSON-compatible equivalent. Check `info.mode` if your wrap logic depends on the output type.

## 14. model_serializer plain mode must return the full structure

With `@model_serializer(mode='plain')`, you are responsible for returning the complete serialized output. Pydantic does not merge your return value with default serialization. Forgetting a field means it is gone.

## 15. when_used='json' serializers are invisible in Python mode

If you set `when_used='json'` on a serializer, calling `model_dump()` (Python mode) will not trigger it. Only `model_dump_json()` or `model_dump(mode='json')` will. This can make debugging confusing when testing with `model_dump()` alone.

## 16. RootModel iteration yields {'root': value}

Iterating over a `RootModel` or calling `dict()` on it produces `{'root': <value>}`, not the unwrapped value. Use `model.root` to access the inner value directly.

## 17. context is not propagated automatically

The `context` dict passed to `model_dump(context=...)` is available in serializer functions via `info.context`, but you must explicitly check for it. It defaults to `None`, not `{}`, so always guard with `isinstance(info.context, dict)` or a None check.
