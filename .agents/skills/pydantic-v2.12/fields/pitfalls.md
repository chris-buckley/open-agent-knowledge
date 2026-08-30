# Pydantic v2 Fields -- Pitfalls

## 1. Field() Assignment Looks Like a Default but Is Not

```python
class Model(BaseModel):
    name: str = Field(frozen=True)  # still REQUIRED, no default value
```

`Field()` without `default` or `default_factory` does NOT make the field optional. The assignment syntax is misleading -- prefer the `Annotated` pattern for non-default metadata to avoid confusion.

## 2. Annotated Pattern and Type Checker Blindness

Type checkers (mypy, pyright) do NOT understand `Field()` inside `Annotated`. They will not synthesize the correct `__init__` for `alias`, `default`, or `default_factory` placed in `Annotated`:

```python
# Type checker does NOT see alias='username' here:
name: Annotated[str, Field(alias='username')]

# Type checker DOES see alias='username' here:
name: str = Field(alias='username')
```

Use assignment pattern for `alias`, `default`, `default_factory`. Use `Annotated` for constraints and metadata only.

## 3. Mixing Field and Type Metadata in Annotated

```python
# WRONG -- deprecated attaches to `Annotated[int, ...]`, not to the Optional union:
field_bad: Annotated[int, Field(deprecated=True)] | None = None

# CORRECT -- deprecated is part of the full union annotation:
field_ok: Annotated[int | None, Field(deprecated=True)] = None
```

When using `Annotated[X, ...] | None`, the metadata only applies to the `X` branch, not the full union. Place the complete type inside `Annotated`.

## 4. default and default_factory Are Mutually Exclusive

```python
class Model(BaseModel):
    x: int = Field(default=0, default_factory=lambda: 1)  # TypeError!
```

You cannot specify both. Pick one.

## 5. default_factory with Validated Data Depends on Field Order

```python
class User(BaseModel):
    username: str = Field(default_factory=lambda data: data['email'])  # KeyError!
    email: EmailStr
```

The `data` dict only contains fields defined BEFORE the current one. Reorder fields so dependencies come first.

## 6. Mutable Defaults Are Deep-Copied, Not Shared

Unlike plain Python or dataclasses, Pydantic deep-copies mutable defaults per instance. This is safe but can be surprising if you expect shared state. Also means you do NOT need `default_factory=list` for empty lists -- `Field(default=[])` works correctly.

## 7. Defaults Are NOT Validated by Default

```python
class Model(BaseModel):
    age: int = 'not a number'  # no error at class definition or instantiation!
```

Invalid defaults silently pass unless you enable `validate_default=True` per-field or `model_config = ConfigDict(validate_default=True)` model-wide.

## 8. V1 to V2 Removed/Renamed kwargs

These raise errors or warnings if used in `Field()`:

```csv
V1 kwarg,V2 replacement
const,Use Literal[value] type
min_items,min_length (deprecated warning)
max_items,max_length (deprecated warning)
unique_items,Use set type
allow_mutation,frozen (deprecated warning)
regex,pattern
**extra kwargs,json_schema_extra dict
```

## 9. Alias Precedence Surprises

- `validation_alias` overrides `alias` for validation.
- `serialization_alias` overrides `alias` for serialization.
- If an `alias_generator` is set AND you set `alias` on a field, the field alias wins by default (`alias_priority=2`).
- If you want the generator to override a field alias, set `alias_priority=1`.

## 10. Serialization Does NOT Use Aliases by Default

```python
class User(BaseModel):
    name: str = Field(alias='username')

user = User(username='john')
user.model_dump()               # {'name': 'john'}       -- field name, NOT alias
user.model_dump(by_alias=True)  # {'username': 'john'}   -- alias only when requested
```

This is inconsistent with validation (which uses aliases by default). Use `model_config = ConfigDict(serialize_by_alias=True)` to change the default.

## 11. validation_alias Not Understood by Type Checkers

Type checkers only understand the `alias` parameter for `__init__` synthesis. If you use `validation_alias`, the type checker will not know about it. Workaround: use `alias` + `serialization_alias` set to the field name:

```python
class Model(BaseModel):
    my_field: int = Field(
        alias='myValidationAlias',
        serialization_alias='my_field',
    )
```

## 12. Cannot Set validate_by_alias=False AND validate_by_name=False

This raises a `UserError`. At least one must be `True`.

## 13. computed_field Does Not Validate Return Values

Pydantic does not run validators on computed field outputs. If your `@property` returns the wrong type, no error is raised -- it will serialize as-is (or fail at serialization time).

## 14. computed_field Requires Return Type Annotation

```python
@computed_field
@property
def area(self):  # ERROR -- no return type annotation
    return self.w * self.h
```

Always annotate the return type.

## 15. computed_field and mypy Compatibility

mypy may emit `Decorated property not supported`. Add `# type: ignore[prop-decorator]` to the `@computed_field` line. pyright handles it correctly.

## 16. cached_property Under computed_field Has No Cache Invalidation

Pydantic does not manage cache invalidation for `@cached_property`. If the source fields change (e.g., via `model_copy`), the cached value may be stale.

## 17. Deprecated Fields Emit Warnings in Validators

Accessing a deprecated field inside a `@model_validator` or `@field_validator` triggers a `DeprecationWarning`. Suppress explicitly:

```python
with warnings.catch_warnings():
    warnings.simplefilter('ignore', DeprecationWarning)
    value = self.deprecated_field
```

## 18. exclude=True Removes from Serialization, Not Validation

A field with `exclude=True` is still validated and stored on the model instance. It is only removed from `model_dump()` / `model_dump_json()` output.

## 19. json_schema_extra Callable Must Mutate In-Place

When passing a callable to `json_schema_extra`, it must modify the dict in-place and return `None`. Returning a new dict is ignored:

```python
# CORRECT:
json_schema_extra=lambda schema: schema.update({'x-custom': True})

# WRONG (return value ignored):
json_schema_extra=lambda schema: {**schema, 'x-custom': True}
```

## 20. AliasPath and AliasChoices Only Work with validation_alias

`AliasPath` and `AliasChoices` are only valid for `validation_alias`, not for `alias` or `serialization_alias` (which must be plain strings).
