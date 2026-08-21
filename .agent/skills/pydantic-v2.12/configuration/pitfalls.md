# Configuration Pitfalls

## ConfigDict Pitfalls

### Config does not propagate across Pydantic model boundaries

Each Pydantic model (and Pydantic dataclass) is its own "configuration boundary." A parent model's `str_to_lower=True` will NOT apply to a nested Pydantic model's fields:

```python
class User(BaseModel):
    name: str  # NOT affected by Parent's str_to_lower

class Parent(BaseModel):
    model_config = ConfigDict(str_to_lower=True)
    user: User

print(Parent(user={'name': 'JOHN'}))
#> user=User(name='JOHN')   <-- NOT lowered
```

Config DOES propagate into stdlib dataclasses and TypedDicts that lack their own config.

### Multiple inheritance does not follow MRO for config

When a model inherits from multiple base classes, Pydantic does NOT follow the standard Python Method Resolution Order (MRO) for merging `model_config`. Results may be unpredictable. Prefer single-inheritance chains for config.

### `populate_by_name` is deprecated in v2.11+

Replace `populate_by_name=True` with the more explicit combination:

```python
model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
```

### Cannot set both `validate_by_alias=False` and `validate_by_name=False`

This would make it impossible to populate any aliased field. Pydantic raises a usage error. If you set `validate_by_alias=False`, Pydantic auto-sets `validate_by_name=True`.

### `use_enum_values` does not apply to defaults without `validate_default=True`

If a field has `Optional[SomeEnum]` with a default enum member, the default stays as the enum object unless you also enable `validate_default=True` (because extraction of `.value` happens during validation, not at definition time):

```python
class SomeModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    some_field: Optional[SomeEnum] = Field(
        default=SomeEnum.FOO, validate_default=True  # required!
    )
```

### `json_encoders` is deprecated

This v1 carryover still works but is deprecated and will be removed. Use custom serializers (`@field_serializer`, `PlainSerializer`, `WrapSerializer`) instead.

### `schema_generator` is deprecated (v2.10+)

The `GenerateSchema` class is private and subject to change. Avoid relying on it.

### `ser_json_timedelta` replaced by `ser_json_temporal` (v2.12+)

`ser_json_timedelta` will be deprecated in v3. Use `ser_json_temporal` which covers `datetime`, `date`, `time`, and `timedelta`.

### `frozen=True` makes instances hashable only if ALL attributes are hashable

Setting `frozen=True` generates `__hash__()`, but the hash will fail at runtime if any field value is unhashable (e.g., a `list` or `dict`).

### `arbitrary_types_allowed` does NOT validate internals of arbitrary types

Pydantic only checks `isinstance`. It does not inspect or validate attributes within arbitrary type instances:

```python
class Pet:
    def __init__(self, name: str):
        self.name = name

class Model(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    pet: Pet

Model(pet=Pet(name=42))  # passes -- name=42 is NOT validated
```

### `revalidate_instances` only affects the model it is set on

Setting `revalidate_instances='always'` on `User` does NOT cause `Transaction` to revalidate `User` instances. You must set it on the model that OWNS the field (i.e., `Transaction`), or on the field type itself.

### `extra='forbid'` with TypeAdapter raises an error if config is on the wrapped type

You cannot pass `config` to `TypeAdapter` if the wrapped type already supports its own config (e.g., a `BaseModel`). A usage error is raised.

### `protected_namespaces` changed default in v2.10

Default changed from `('model_',)` to `('model_validate', 'model_dump')`. Fields like `model_id` are now allowed. If upgrading from earlier v2, you may need to adjust.

### `serialize_by_alias` default will change to `True` in v3

Currently defaults to `False`. Plan ahead for the v3 change if you rely on serialization not using aliases.

## Pydantic Settings Pitfalls

### `BaseSettings` validates defaults by default (unlike `BaseModel`)

`BaseSettings` has `validate_default=True` by default. If a default value does not pass validation, it will raise immediately. This differs from `BaseModel` where defaults are NOT validated by default.

### `case_sensitive` has no effect on Windows

Python's `os.environ` on Windows is always case-insensitive. The `case_sensitive=True` setting will not change this behavior.

### `env_prefix` does NOT apply to aliased fields

If a field has an alias, the environment variable name matches the alias, not `env_prefix + field_name`:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='MY_')
    foo: str = Field(alias='FooAlias')
    # env var name is 'FooAlias', NOT 'MY_FooAlias'
```

### Dotenv files load ALL entries regardless of `env_prefix`

All values from a `.env` file are passed to the model, whether they start with `env_prefix` or not. Extra entries trigger `ValidationError` if `extra='forbid'` (the default for `BaseSettings`).

### `extra='forbid'` is NOT the default for `BaseSettings`

The default `extra` for `BaseSettings` is still `'ignore'` (same as `BaseModel`). However, dotenv files pass all entries to the model, which can cause unexpected validation errors if you switch to `extra='forbid'`.

### Environment variables always override `.env` file values

This is by design but can be surprising. Even a stale env var will shadow a carefully maintained `.env` value.

### `.env` file lookup is CWD only -- no parent directory search

If you specify `env_file='.env'`, Pydantic only checks the current working directory. It does NOT walk up the directory tree.

### `env_nested_delimiter` can over-split field names

With `env_nested_delimiter='_'` and a field named `api_key` inside a nested model `llm`, the env var `LLM_API_KEY` would be parsed as `llm.api.key` (three levels deep). Use `env_nested_max_split=1` to limit splitting depth:

```python
model_config = SettingsConfigDict(
    env_nested_delimiter='_',
    env_nested_max_split=1,  # only split once: llm + api_key
)
```

### Nested sub-models must inherit from `pydantic.BaseModel`

If nested types do not inherit from `BaseModel`, pydantic-settings will initialize them separately and collect field values individually, which can produce unexpected results.

### Secrets directory missing only generates a warning (by default)

A non-existent `secrets_dir` will not raise an error -- just a warning. Use `NestedSecretsSettingsSource` with `secrets_dir_missing='error'` if you need strict behavior.

### `_env_file` override on instantiation completely replaces config

Passing `_env_file='prod.env'` at instantiation ignores whatever was set in `model_config`. To skip all `.env` loading, pass `_env_file=None`.

### CLI source is highest priority by default

When `cli_parse_args` is enabled, CLI arguments take precedence over ALL other sources (including init kwargs and env vars) unless you customize source ordering.
