# Pydantic v2 Configuration

## Setting Config on Models

Use the `model_config` class attribute with `ConfigDict`:

```python
from pydantic import BaseModel, ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(str_max_length=100, extra='forbid')
    name: str
```

Or pass config options as class keyword arguments (recognized by type checkers):

```python
class MyModel(BaseModel, frozen=True):
    name: str
```

## Setting Config on Other Types

Pydantic dataclasses -- pass `config` to the decorator:

```python
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

@dataclass(config=ConfigDict(str_max_length=10, validate_assignment=True))
class User:
    name: str
```

TypedDict / stdlib dataclasses -- use `__pydantic_config__` or the `@with_config` decorator:

```python
from typing_extensions import TypedDict
from pydantic import ConfigDict, with_config

@with_config(ConfigDict(str_to_lower=True))
class Model(TypedDict):
    x: str
```

TypeAdapter -- pass `config` argument:

```python
from pydantic import ConfigDict, TypeAdapter

ta = TypeAdapter(list[str], config=ConfigDict(coerce_numbers_to_str=True))
```

@validate_call -- pass `config` argument to the decorator.

## Config Inheritance

Child models merge config with their parent. The child's settings override the parent's on a per-key basis:

```python
from pydantic import BaseModel, ConfigDict

class Parent(BaseModel):
    model_config = ConfigDict(extra='allow', str_to_lower=False)

class Child(Parent):
    model_config = ConfigDict(str_to_lower=True)
    x: str

m = Child(x='FOO', y='bar')
print(Child.model_config)
#> {'extra': 'allow', 'str_to_lower': True}
```

Create a custom base class to change behavior globally across all your models.

## Config Propagation

- Pydantic models/dataclasses nested as fields: config does NOT propagate across model boundaries. Each model keeps its own config.
- stdlib dataclasses/TypedDicts nested as fields: config DOES propagate from the parent, unless the nested type has its own config set.

## ConfigDict Options Quick Reference

### String Handling

```csv
Option,Type,Default,Description
str_strip_whitespace,bool,False,Strip leading/trailing whitespace from strings
str_to_lower,bool,False,Lowercase all string values
str_to_upper,bool,False,Uppercase all string values
str_min_length,int,0,Minimum length for string fields
str_max_length,int | None,None,Maximum length for string fields
```

### Validation Behavior

```csv
Option,Type,Default,Description
strict,bool,False,Disable type coercion; require exact types
extra,'allow' | 'forbid' | 'ignore','ignore',How to handle extra fields during init
frozen,bool,False,Make instances immutable and hashable
validate_assignment,bool,False,Re-validate when attributes are set after init
validate_default,bool,False,Validate default values during validation
validate_return,bool,False,Validate return values from @validate_call
revalidate_instances,'never' | 'always' | 'subclass-instances','never',When to revalidate model instances passed as field values
arbitrary_types_allowed,bool,False,Allow non-pydantic types as field types (validated via isinstance)
from_attributes,bool,False,Build models from object attributes (ORM mode)
coerce_numbers_to_str,bool,False,Auto-coerce int/float/Decimal to str in lax mode
use_enum_values,bool,False,Store .value of enums instead of the enum member
cache_strings,bool | 'all' | 'keys' | 'none',True,Cache strings to improve validation performance
```

### Alias and Naming

```csv
Option,Type,Default,Description
populate_by_name,bool,False,Allow populating aliased fields by field name. Deprecated in v2.11+; use validate_by_name + validate_by_alias instead
validate_by_alias,bool,True,Allow populating fields by alias *(v2.11+)*
validate_by_name,bool,False,Allow populating aliased fields by name *(v2.11+)*
serialize_by_alias,bool,False,"Serialize using alias by default *(v2.11+, will change to True in v3)*"
alias_generator,Callable | AliasGenerator | None,None,Auto-generate aliases from field names
loc_by_alias,bool,True,Use alias in validation error loc paths
```

### JSON Serialization

```csv
Option,Type,Default,Description
ser_json_timedelta,'iso8601' | 'float','iso8601',Timedelta serialization format. Use ser_json_temporal instead (v2.12+)
ser_json_temporal,'iso8601' | 'seconds' | 'milliseconds','iso8601',Temporal type serialization format *(v2.12+)*
val_temporal_unit,'seconds' | 'milliseconds' | 'infer','infer',Unit for validating numeric datetime input *(v2.12+)*
ser_json_bytes,'utf8' | 'base64' | 'hex','utf8',Bytes serialization format
val_json_bytes,'utf8' | 'base64' | 'hex','utf8',Bytes deserialization format
ser_json_inf_nan,'null' | 'constants' | 'strings','null',How to serialize inf and NaN float values
```

### JSON Schema

```csv
Option,Type,Default,Description
title,str | None,None,JSON schema title (defaults to model name)
model_title_generator,"Callable[[type], str] | None",None,Custom model title generator
field_title_generator,"Callable[[str, FieldInfo], str] | None",None,Custom field title generator
json_schema_extra,dict | Callable | None,None,Extra properties for JSON schema
json_schema_serialization_defaults_required,bool,False,Mark defaulted fields as required in serialization schema
json_schema_mode_override,'validation' | 'serialization' | None,None,Force a specific schema mode
```

### Error Handling and Security

```csv
Option,Type,Default,Description
hide_input_in_errors,bool,False,Omit input values from ValidationError messages
validation_error_cause,bool,False,Show Python exceptions as cause in exception groups
protected_namespaces,"tuple[str | Pattern, ...]","('model_validate', 'model_dump')",Prefixes/patterns that prevent field name collisions
```

### Miscellaneous

```csv
Option,Type,Default,Description
regex_engine,'rust-regex' | 'python-re','rust-regex',Regex engine for pattern validation
allow_inf_nan,bool,True,Allow inf/NaN in float/decimal fields
ignored_types,"tuple[type, ...]",(),Types allowed as class attributes without annotations
use_attribute_docstrings,bool,False,Use bare string literals after fields as descriptions
defer_build,bool,False,Defer validator/serializer construction until first use
plugin_settings,"dict[str, object] | None",None,Settings passed to Pydantic plugins
json_encoders,dict | None,None,"Custom JSON encoders per type (deprecated, v1 carryover)"
schema_generator,type | None,None,Custom schema generator (deprecated in v2.10)
url_preserve_empty_path,bool,False,Preserve empty URL paths *(v2.12+)*
```

## ConfigDict Code Examples

### extra -- controlling extra fields

```python
from pydantic import BaseModel, ConfigDict, ValidationError

class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid')
    x: int

try:
    Strict(x=1, y='a')
except ValidationError as e:
    print(e)  # y: Extra inputs are not permitted

class Flexible(BaseModel):
    model_config = ConfigDict(extra='allow')
    x: int

m = Flexible(x=1, y='a')
assert m.__pydantic_extra__ == {'y': 'a'}
```

You can type extra values by annotating `__pydantic_extra__`:

```python
from pydantic import BaseModel, ConfigDict, Field

class Model(BaseModel):
    __pydantic_extra__: dict[str, int] = Field(init=False)
    x: int
    model_config = ConfigDict(extra='allow')

m = Model(x=1, y='2')  # y coerced to int
assert m.y == 2
```

You can override `extra` per-call via `model_validate(..., extra='forbid')`.

### frozen -- immutable models

```python
class Immutable(BaseModel, frozen=True):
    x: int

obj = Immutable(x=1)
obj.x = 2  # raises ValidationError; also caught by type checkers
```

### alias_generator -- automatic case conversion

```python
from pydantic import BaseModel, ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel, to_pascal

class Voice(BaseModel):
    model_config = ConfigDict(alias_generator=to_pascal)
    name: str
    language_code: str

voice = Voice(Name='Filiz', LanguageCode='tr-TR')
print(voice.model_dump(by_alias=True))
#> {'Name': 'Filiz', 'LanguageCode': 'tr-TR'}
```

Use `AliasGenerator` for different validation vs serialization aliases:

```python
class Athlete(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_pascal,
        )
    )
    first_name: str

athlete = Athlete(firstName='John')
print(athlete.model_dump(by_alias=True))  #> {'FirstName': 'John'}
```

Built-in generators: `to_pascal`, `to_camel`, `to_snake` (from `pydantic.alias_generators`).

### validate_by_name + validate_by_alias (v2.11+)

```python
from pydantic import BaseModel, ConfigDict, Field

class Model(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
    my_field: str = Field(alias='my_alias')

m = Model(my_alias='foo')   # works
m = Model(my_field='foo')   # also works
```

### strict -- disabling type coercion

```python
from pydantic import BaseModel, ConfigDict

class Model(BaseModel):
    model_config = ConfigDict(strict=True)
    name: str
    age: int

Model(name='Alice', age='30')  # raises ValidationError: age must be int
```

### revalidate_instances

```python
from pydantic import BaseModel

class User(BaseModel, revalidate_instances='always'):
    name: str

class Transaction(BaseModel):
    user: User

u = User(name='John')
u.name = 123          # bypass: no validate_assignment
t = Transaction(user=u)  # with 'always': re-validates, catches the int
```

## Pydantic Settings

Separate package: `pip install pydantic-settings`

### Basic Usage

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='MY_APP_')

    db_host: str = 'localhost'
    db_port: int = 5432
    debug: bool = False
```

`BaseSettings` extends `BaseModel`. Field values are resolved from multiple sources by priority.

### Field Value Priority (highest to lowest)

1. CLI arguments (if `cli_parse_args` enabled)
2. `__init__` keyword arguments
3. Environment variables
4. Dotenv (`.env`) file values
5. Secrets directory files
6. Field default values

### Environment Variables

- Default env var name = field name (case-insensitive by default).
- Set `env_prefix` to add a prefix to all env var names.
- `env_prefix` does NOT apply to aliased fields.
- Set `case_sensitive=True` to require exact case match.
- Complex types (`list`, `dict`, sub-models) are parsed as JSON from env vars.
- Use `env_nested_delimiter='__'` to populate nested models: `MY_APP__DB__HOST=...`

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='MY_APP_',
        env_nested_delimiter='__',
    )
    db_host: str
```

### Dotenv (.env) Files

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )
```

- Environment variables always take priority over `.env` values.
- Override at instantiation: `Settings(_env_file='prod.env')` or `Settings(_env_file=None)` to skip.
- Multiple files: `env_file=('.env', '.env.prod')` -- later files override earlier ones.
- Extra fields in `.env` file will raise `ValidationError` if `extra='forbid'`.

### Secrets

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir='/run/secrets')
    database_password: str
```

- Each secret is a single file where filename = field name, contents = value.
- Env vars and `.env` always take priority over secrets.
- Override at init: `Settings(_secrets_dir='/other/path')`.
- Multiple dirs: `secrets_dir=('/var/run', '/run/secrets')` -- later dirs win.
- Use `NestedSecretsSettingsSource` for nested model secrets and subdirectory layouts.

### Other Config File Sources

```csv
Source Class,Config Key,File Type
JsonConfigSettingsSource,json_file,JSON
TomlConfigSettingsSource,toml_file,TOML
YamlConfigSettingsSource,yaml_file,YAML
PyprojectTomlConfigSettingsSource,pyproject_toml_table_header,pyproject.toml
```

### Customizing Source Priority

Override `settings_customise_sources` to reorder, add, or remove sources:

```python
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

class Settings(BaseSettings):
    database_dsn: str

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # env vars now have highest priority
        return env_settings, init_settings, file_secret_settings
```

### Custom Settings Source

Subclass `PydanticBaseSettingsSource` and implement `get_field_value` and `__call__`:

```python
from typing import Any
from pydantic.fields import FieldInfo
from pydantic_settings import PydanticBaseSettingsSource

class MySource(PydanticBaseSettingsSource):
    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        value = ...  # load from your source
        return value, field_name, False

    def __call__(self) -> dict[str, Any]:
        d = {}
        for field_name, field in self.settings_cls.model_fields.items():
            val, key, is_complex = self.get_field_value(field, field_name)
            val = self.prepare_field_value(field_name, field, val, is_complex)
            if val is not None:
                d[key] = val
        return d
```

Access previous sources' results via `self.current_state` or `self.settings_sources_data`.

### BaseSettings Validation Defaults

Unlike `BaseModel`, `BaseSettings` validates default values by default. Disable with `validate_default=False`.

### In-Place Reloading

```python
settings = Settings()
# after environment changes...
settings.__init__()  # re-reads from all sources
```

## Experimental Features (v2.8+)

### Pipeline API (v2.8.0, experimental)

Composable, type-safe validation/transformation chains:

```python
from typing import Annotated
from pydantic import BaseModel
from pydantic.experimental.pipeline import validate_as

class User(BaseModel):
    name: Annotated[str, validate_as(str).str_lower()]
    age: Annotated[int, validate_as(int).gt(0)]
    password: Annotated[
        str,
        validate_as(str).transform(str.lower).predicate(lambda x: x != 'password'),
    ]
```

Steps: `.validate_as(type)`, `.transform(fn)`, `.predicate(fn)`, `.gt()`, `.len()`, `.str_lower()`, `.str_strip()`, `.str_pattern()`. Supports union via `|` operator.

### Partial Validation (v2.10.0, experimental)

Validate incomplete JSON (useful for LLM streaming):

```python
from pydantic import TypeAdapter
from typing_extensions import TypedDict, NotRequired

class Item(TypedDict):
    a: int
    b: NotRequired[float]

ta = TypeAdapter(list[Item])
result = ta.validate_json(
    '[{"a": 1, "b"',
    experimental_allow_partial=True,
)
#> [{'a': 1}]
```

Modes: `False` (off), `True` (on), `'trailing-strings'` (include incomplete trailing strings).

Limitations: `TypeAdapter` only, supports `list`/`dict`/`TypedDict`/models, ignores errors in last element only.
