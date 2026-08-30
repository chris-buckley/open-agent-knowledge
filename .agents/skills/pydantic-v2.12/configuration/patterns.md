# Configuration — Recurring Patterns

## Shared Base Model Config

Define a project-wide base class to set defaults for all models.

```python
from pydantic import BaseModel, ConfigDict

class AppBaseModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        ser_json_inf_nan="constants",
    )

class User(AppBaseModel):
    name: str
    age: int
```

## Config Inheritance Override

Child models merge config with parent. Override specific keys per subclass.

```python
class Parent(BaseModel):
    model_config = ConfigDict(extra="allow", strict=False)

class Child(Parent):
    model_config = ConfigDict(strict=True)  # extra="allow" inherited, strict overridden
```

## Camel-Case API Contract

Use `alias_generator` for automatic snake_case ↔ camelCase conversion.

```python
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class ApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        serialize_by_alias=True,
    )
    user_name: str
    created_at: str
```

## Environment-Based Settings

Multi-source configuration with priority ordering: CLI > env vars > .env > secrets > defaults.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
    )
    db_host: str = "localhost"
    db_port: int = 5432
    debug: bool = False
```

## Nested Settings with Delimiter

Populate nested models from flat environment variables using a delimiter.

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class Database(BaseModel):
    host: str = "localhost"
    port: int = 5432

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")
    db: Database = Database()

# APP_DB__HOST=prod-db APP_DB__PORT=5433 -> Settings().db.host == "prod-db"
```

## Custom Source Priority

Override `settings_customise_sources` to reorder or add custom configuration sources.

```python
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

class Settings(BaseSettings):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return env_settings, init_settings, dotenv_settings, file_secret_settings
```

## Frozen + Hashable Config

Immutable models usable as dict keys or set members.

```python
from pydantic import BaseModel, ConfigDict

class CacheKey(BaseModel):
    model_config = ConfigDict(frozen=True)
    endpoint: str
    params: tuple[tuple[str, str], ...] = ()

cache: dict[CacheKey, str] = {}
```

## Settings Reload

Re-read all sources at runtime without recreating the instance.

```python
settings = Settings()
# ... environment changes ...
settings.__init__()  # re-reads env vars, .env, secrets
```
