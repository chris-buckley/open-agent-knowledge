# Pydantic v2 API Quick Reference

Source: docs.pydantic.dev v2.12

## BaseModel

`from pydantic import BaseModel`

### Key Methods

```csv
Method,Signature,Description
__init__,(**data: Any) -> None,Create model by parsing and validating keyword arguments; raises ValidationError on failure
model_fields,"classmethod () -> dict[str, FieldInfo]",Mapping of field names to their FieldInfo objects
model_computed_fields,"classmethod () -> dict[str, ComputedFieldInfo]",Mapping of computed field names to their ComputedFieldInfo objects
model_extra,"property -> dict[str, Any] | None","Extra fields dict if extra='allow', else None"
model_fields_set,property -> set[str],Set of field names explicitly set during instantiation
model_construct,"classmethod (_fields_set=None, **values) -> Self",Create instance from trusted data without validation
model_copy,"(*, update=None, deep=False) -> Self",Shallow/deep copy with optional field updates (unvalidated)
model_dump,"(*, mode='python', include=None, exclude=None, context=None, by_alias=None, exclude_unset=False, exclude_defaults=False, exclude_none=False, exclude_computed_fields=False, round_trip=False, warnings=True, fallback=None, serialize_as_any=False) -> dict[str, Any]",Serialize model to dict
model_dump_json,"(*, indent=None, ensure_ascii=False, include=None, exclude=None, context=None, by_alias=None, exclude_unset=False, exclude_defaults=False, exclude_none=False, exclude_computed_fields=False, round_trip=False, warnings=True, fallback=None, serialize_as_any=False) -> str",Serialize model to JSON string
model_json_schema,"classmethod (by_alias=True, ref_template=DEFAULT_REF_TEMPLATE, schema_generator=GenerateJsonSchema, mode='validation', *, union_format='any_of') -> dict[str, Any]",Generate JSON Schema for the model class
model_parametrized_name,"classmethod (params: tuple[type[Any], ...]) -> str",Compute class name for generic parametrizations
model_post_init,(context: Any) -> None,Override for additional init logic after __init__ and model_construct
model_rebuild,"classmethod (*, force=False, raise_errors=True, _parent_namespace_depth=2, _types_namespace=None) -> bool | None",Rebuild pydantic-core schema; needed for forward references
model_validate,"classmethod (obj, *, strict=None, extra=None, from_attributes=None, context=None, by_alias=None, by_name=None) -> Self",Validate a Python object into a model instance
model_validate_json,"classmethod (json_data: str|bytes|bytearray, *, strict=None, extra=None, context=None, by_alias=None, by_name=None) -> Self",Validate JSON data into a model instance
model_validate_strings,"classmethod (obj, *, strict=None, extra=None, context=None, by_alias=None, by_name=None) -> Self",Validate string data into a model instance
```

### Key Class Attributes

```csv
Attribute,Type,Description
model_config,ClassVar[ConfigDict],Model configuration dictionary
__pydantic_fields__,"ClassVar[dict[str, FieldInfo]]",Field name to FieldInfo mapping
__pydantic_computed_fields__,"ClassVar[dict[str, ComputedFieldInfo]]",Computed field name to ComputedFieldInfo mapping
__pydantic_core_schema__,ClassVar[CoreSchema],The pydantic-core schema
__pydantic_complete__,ClassVar[bool],Whether model building is completed
__pydantic_validator__,ClassVar[SchemaValidator],The pydantic-core validator
__pydantic_serializer__,ClassVar[SchemaSerializer],The pydantic-core serializer
__pydantic_extra__,"dict[str, Any] | None",Extra field values (when extra='allow')
__pydantic_fields_set__,set[str],Names of explicitly set fields
__pydantic_private__,"dict[str, Any] | None",Private attribute values
```

## RootModel

`from pydantic import RootModel`

Bases: `BaseModel`, `Generic[RootModelRootType]`

A `BaseModel` for the root object of the model. Used for models wrapping a single value.

```python
RootModel(root: RootModelRootType = PydanticUndefined, **data)
```

```csv
Attribute/Method,Description
root,The root object of the model
"model_construct(root, _fields_set=None) -> Self",Create instance without validation
model_dump(...),Same params as BaseModel; return type is typically RootModelRootType
__pydantic_root_model__,Always True
```

## TypeAdapter

`from pydantic import TypeAdapter`

```python
TypeAdapter(type: Any, *, config: ConfigDict | None = None, _parent_depth: int = 2, module: str | None = None)
```

Validation and serialization for arbitrary types (not just BaseModel subclasses).

```csv
Method,Signature,Description
rebuild,"(*, force=False, raise_errors=True, _parent_namespace_depth=2, _types_namespace=None) -> bool | None",Rebuild schema for forward references
validate_python,"(object, /, *, strict=None, extra=None, from_attributes=None, context=None, experimental_allow_partial=False, by_alias=None, by_name=None) -> T",Validate a Python object
validate_json,"(data: str|bytes|bytearray, /, *, strict=None, extra=None, context=None, experimental_allow_partial=False, by_alias=None, by_name=None) -> T",Validate JSON data
validate_strings,"(obj, /, *, strict=None, extra=None, context=None, experimental_allow_partial=False, by_alias=None, by_name=None) -> T",Validate string data
get_default_value,"(*, strict=None, context=None) -> Some[T] | None","Get default value wrapped in Some, or None"
dump_python,"(instance, /, *, mode='python', include=None, exclude=None, by_alias=None, exclude_unset=False, exclude_defaults=False, exclude_none=False, round_trip=False, warnings=True, serialize_as_any=False) -> Any",Serialize to Python object
dump_json,"(instance, /, *, indent=None, include=None, exclude=None, by_alias=None, exclude_unset=False, exclude_defaults=False, exclude_none=False, round_trip=False, warnings=True, serialize_as_any=False) -> bytes",Serialize to JSON bytes
json_schema,"(*, by_alias=True, ref_template=DEFAULT_REF_TEMPLATE, schema_generator=GenerateJsonSchema, mode='validation') -> dict[str, Any]",Generate JSON Schema
json_schemas,"(inputs, /, *, by_alias=True, title=None, description=None, ref_template=DEFAULT_REF_TEMPLATE, schema_generator=GenerateJsonSchema) -> tuple[dict, dict]",Generate JSON Schema for multiple types
```

### Attributes

```csv
Attribute,Type,Description
core_schema,CoreSchema,The core schema for the type
validator,SchemaValidator,The schema validator
serializer,SchemaSerializer,The schema serializer
pydantic_complete,bool,Whether schema build succeeded
```

## Field()

`from pydantic import Field`

Returns `FieldInfo`. All parameters:

```csv
Parameter,Type,Default,Description
default,Any,(required or use default_factory),Default value for the field
default_factory,Callable,_Unset,Factory function for default value
alias,str | None,_Unset,Alternative name for field during validation and serialization
alias_priority,int | None,_Unset,Priority of alias vs field name
validation_alias,str | AliasPath | AliasChoices | None,_Unset,Alias used only during validation
serialization_alias,str | None,_Unset,Alias used only during serialization
title,str | None,_Unset,Title for JSON Schema
field_title_generator,"Callable[[str, FieldInfo], str] | None",_Unset,Callable to generate title from field name and info
description,str | None,_Unset,Description for JSON Schema
examples,list[Any] | None,_Unset,Example values for JSON Schema
exclude,bool | None,_Unset,Exclude field from serialization
exclude_if,"Callable[[Any], bool] | None",_Unset,Conditionally exclude based on value
discriminator,str | Discriminator | None,_Unset,Discriminator field for tagged unions
deprecated,Deprecated | str | bool | None,_Unset,Mark field as deprecated
json_schema_extra,"JsonDict | Callable[[JsonDict], None] | None",_Unset,Extra JSON Schema properties
frozen,bool | None,_Unset,Whether field is immutable
validate_default,bool | None,_Unset,Whether to validate default values
repr,bool,_Unset,Include in model repr
init,bool | None,_Unset,Include in __init__ (dataclasses)
init_var,bool | None,_Unset,Mark as init-only variable (dataclasses)
kw_only,bool | None,_Unset,Keyword-only in __init__ (dataclasses)
pattern,str | Pattern[str] | None,_Unset,Regex pattern constraint for strings
strict,bool | None,_Unset,Enable strict type checking
coerce_numbers_to_str,bool | None,_Unset,Coerce numeric types to string
gt,SupportsGt | None,_Unset,Greater-than constraint
ge,SupportsGe | None,_Unset,Greater-than-or-equal constraint
lt,SupportsLt | None,_Unset,Less-than constraint
le,SupportsLe | None,_Unset,Less-than-or-equal constraint
multiple_of,float | None,_Unset,Multiple-of constraint
allow_inf_nan,bool | None,_Unset,Allow infinity and NaN
max_digits,int | None,_Unset,Max digits for Decimal
decimal_places,int | None,_Unset,Max decimal places for Decimal
min_length,int | None,_Unset,Minimum length for strings/sequences
max_length,int | None,_Unset,Maximum length for strings/sequences
union_mode,"Literal['smart', 'left_to_right']",_Unset,Union validation strategy
fail_fast,bool | None,_Unset,Stop validation on first error in sequences
```

### Related Classes

```csv
Class,Description
FieldInfo,"Metadata container for field definitions; has get_default(), is_required(), asdict()"
"PrivateAttr(default, default_factory)","Define private attributes (not validated, not serialized)"
ModelPrivateAttr,Container for private attribute metadata
computed_field,Decorator to define computed (read-only) properties included in serialization
ComputedFieldInfo,Metadata container for computed fields
```

## ConfigDict

`from pydantic import ConfigDict`

Bases: `TypedDict`. All options:

```csv
Option,Type,Default,Description
title,str | None,None,Title for generated JSON Schema
model_title_generator,"Callable[[type], str] | None",None,Callable to generate model title
field_title_generator,"Callable[[str, FieldInfo | ComputedFieldInfo], str] | None",None,Callable to generate field title
str_to_lower,bool,False,Lowercase all str fields
str_to_upper,bool,False,Uppercase all str fields
str_strip_whitespace,bool,False,Strip whitespace from str fields
str_min_length,int,None,Minimum length for str fields
str_max_length,int | None,None,Maximum length for str fields
extra,'allow' | 'forbid' | 'ignore' | None,'ignore',How to handle extra fields
frozen,bool,False,Make model instances immutable and hashable
populate_by_name,bool,False,"Allow populating by field name when alias set (deprecated, use validate_by_name)"
use_enum_values,bool,False,Store enum .value instead of enum instance
validate_assignment,bool,False,Revalidate on attribute assignment
arbitrary_types_allowed,bool,False,Allow non-pydantic types in fields
from_attributes,bool,False,Build models from object attributes (ORM mode)
loc_by_alias,bool,True,Use alias in error locations
alias_generator,"Callable[[str], str] | AliasGenerator | None",None,Auto-generate aliases from field names
ignored_types,"tuple[type, ...]",(),Types to ignore during schema building
allow_inf_nan,bool,True,Allow infinity/NaN for float fields
json_schema_extra,JsonDict | Callable | None,None,Extra JSON Schema properties
json_encoders,dict | None,None,Custom JSON encoders (deprecated)
strict,bool,False,Enable strict mode globally
revalidate_instances,'always' | 'never' | 'subclass-instances','never',When to revalidate model instances
ser_json_timedelta,'iso8601' | 'float','iso8601',Timedelta serialization format
ser_json_temporal,'iso8601' | 'seconds_float' | 'milliseconds_float','iso8601',Temporal type serialization format
val_temporal_unit,'s' | 'ms' | 'us' | 'ns','s',Temporal unit for validation from numbers
ser_json_bytes,'utf8' | 'base64' | 'hex','utf8',Bytes serialization encoding
val_json_bytes,'utf8' | 'base64' | 'hex','utf8',Bytes validation encoding
ser_json_inf_nan,'null' | 'constants' | 'strings','null',How to serialize inf/nan in JSON
validate_default,bool,False,Validate default values
validate_return,bool,False,Validate return values (validate_call)
protected_namespaces,"tuple[str, ...]","('model_',)",Namespace prefixes that warn on field names
hide_input_in_errors,bool,False,Hide input data in validation errors
defer_build,bool,False,Defer schema build until first use
plugin_settings,"dict[str, object] | None",None,Settings passed to plugins
schema_generator,type[GenerateJsonSchema] | None,None,Custom JSON Schema generator
json_schema_serialization_defaults_required,bool,False,Mark fields with defaults as required in serialization schema
json_schema_mode_override,'validation' | 'serialization' | None,None,Force JSON Schema mode
coerce_numbers_to_str,bool,False,Coerce numeric types to string globally
regex_engine,'rust-regex' | 'python-re','rust-regex',Regex engine for pattern validation
validation_error_cause,bool,False,Include original exception as __cause__
use_attribute_docstrings,bool,False,Use attribute docstrings as field descriptions
cache_strings,bool | 'all' | 'keys' | 'none',True,String caching strategy
validate_by_alias,bool | None,None,Whether to accept alias during validation
validate_by_name,bool | None,None,Whether to accept field name during validation
serialize_by_alias,bool | None,None,Whether to use alias during serialization
url_preserve_empty_path,bool,False,Preserve empty path segment in URLs
```

### Helpers

```csv
Name,Description
with_config(config: ConfigDict),Decorator to apply config to TypedDicts and dataclasses
ExtraValues,"Type alias: Literal['allow', 'forbid', 'ignore']"
```

### Alias Generators

`from pydantic.alias_generators import to_pascal, to_camel, to_snake`

```csv
Function,Description
to_pascal(s: str) -> str,Convert snake_case to PascalCase
to_camel(s: str) -> str,Convert snake_case to camelCase
to_snake(s: str) -> str,Convert PascalCase/camelCase to snake_case
```

## Functional Validators

`from pydantic import AfterValidator, BeforeValidator, PlainValidator, WrapValidator, field_validator, model_validator`

### Annotated Validators (used with `Annotated[T, ...]`)

```csv
Class,Signature,Description
AfterValidator,(func: NoInfoValidatorFunction | WithInfoValidatorFunction),Runs after inner validation
BeforeValidator,"(func, json_schema_input_type=PydanticUndefined)",Runs before inner validation
PlainValidator,"(func, json_schema_input_type=Any)",Replaces inner validation entirely
WrapValidator,"(func, json_schema_input_type=PydanticUndefined)",Wraps inner validation; receives handler
```

### Decorator Validators

```csv
Decorator,Signature,Description
field_validator,"(field, /, *fields, mode='after', check_fields=None, json_schema_input_type=PydanticUndefined)","Validate specific fields; modes: 'before', 'after', 'wrap', 'plain'"
model_validator,"(*, mode: Literal['wrap', 'before', 'after'])","Validate entire model; 'before' receives raw input, 'after' receives model instance"
```

### Utility Types

```csv
Type,Description
InstanceOf[T],"Annotated type that validates value isinstance(v, T)"
SkipValidation,Skip all validation for the annotated type
"ValidateAs(from_type, instantiation_hook)","Validate as one type, then transform to another"
```

## Functional Serializers

`from pydantic import PlainSerializer, WrapSerializer, field_serializer, model_serializer`

### Annotated Serializers (used with `Annotated[T, ...]`)

```csv
Class,Signature,Description
PlainSerializer,"(func: SerializerFunction, return_type=PydanticUndefined, when_used='always')",Replace default serialization with custom function
WrapSerializer,"(func: WrapSerializerFunction, return_type=PydanticUndefined, when_used='always')",Wrap default serialization; handler calls inner logic
SerializeAsAny,(),Enable duck-typing serialization behavior
```

`when_used` values: `'always'`, `'unless-none'`, `'json'`, `'json-unless-none'`

### Decorator Serializers

```csv
Decorator,Signature,Description
field_serializer,"(field, /, *fields, mode='plain', return_type=..., when_used='always', check_fields=None)","Serialize specific fields; modes: 'plain', 'wrap'"
model_serializer,"(*, mode='plain', when_used='always')","Serialize entire model; modes: 'plain', 'wrap'"
```

## Annotated Handlers

`from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler`

Used when implementing `__get_pydantic_core_schema__` and `__get_pydantic_json_schema__`.

```csv
Class,Method/Property,Description
GetJsonSchemaHandler,mode: JsonSchemaMode,Current mode: 'validation' or 'serialization'
GetJsonSchemaHandler,resolve_ref_schema(maybe_ref_json_schema) -> JsonSchemaValue,Resolve $ref to concrete JSON schema
GetCoreSchemaHandler,field_name: str | None,Name of closest field to this validator
GetCoreSchemaHandler,generate_schema(source_type) -> CoreSchema,Generate schema for a different type
GetCoreSchemaHandler,resolve_ref_schema(maybe_ref_schema) -> CoreSchema,Resolve definition-ref to concrete CoreSchema
```

## Experimental

`from pydantic.experimental.pipeline import validate_as`

### Pipeline API (`_Pipeline`)

Chainable validation/transformation steps for use with `Annotated`.

```csv
Method,Description
transform(func),Transform output of previous step
"validate_as(tp, *, strict=False)",Validate/parse into a new type
validate_as_deferred(func),Deferred type resolution for self-referential models
constrain(constraint),"Apply Ge, Gt, Le, Lt, Len, MultipleOf, Timezone constraints"
predicate(func),Apply a predicate function as constraint
gt(v) / lt(v) / ge(v) / le(v),Numeric comparison constraints
"len(min, max)",Length constraint
multiple_of(v),Multiple-of constraint
eq(v) / not_eq(v),Equality constraints
in_(collection) / not_in(collection),Membership constraints
otherwise(pipeline),Alternative pipeline on failure
then(pipeline),Chain another pipeline
```

### Arguments Schema

```csv
Function,Description
generate_arguments_schema(func),Generate a core schema for function arguments
```

## pydantic_core Key Exports

`from pydantic_core import ...`

### Core Classes

```csv
Class,Description
"SchemaValidator(schema, config=None)",Rust-backed validator; owns the validation pipeline
SchemaSerializer,Rust-backed serializer for model output
ValidationError,"Raised on validation failure; has errors(), error_count(), json()"
SchemaError,Raised when schema definition is invalid
"PydanticCustomError(type, message_template, context)",Custom validation error with template message
"PydanticKnownError(type, context)",Known validation error type
```

### Signal Exceptions

```csv
Class,Description
PydanticOmit,Raise during serialization to omit a value
PydanticUseDefault,Raise during validation to use default value
PydanticSerializationError,Raised on serialization failure
PydanticSerializationUnexpectedValue,Raised for unexpected values during serialization
```

### Types

```csv
Type,Description
Url,Parsed URL type
MultiHostUrl,URL supporting multiple hosts
MultiHostHost,"Single host entry with username, password, host, port"
ArgsKwargs,Container for positional args and keyword kwargs
Some[T],Wrapper indicating a value is present (vs None for absent)
TzInfo,"Timezone info type with tzname(), utcoffset(), dst(), fromutc()"
```

### Utility Functions

```csv
Function,Description
"to_json(value, *, indent=None, include=None, exclude=None, by_alias=True, exclude_none=False) -> bytes",Serialize any Python object to JSON bytes
"from_json(data, *, allow_inf_nan=True, cache_strings=True, allow_partial=False) -> Any",Parse JSON bytes/str to Python objects
"to_jsonable_python(value, *, include=None, exclude=None, by_alias=True, exclude_none=False) -> Any",Convert to JSON-serializable Python objects
```

### ErrorDetails TypedDict

```csv
Key,Type,Description
type,str,Error type identifier
loc,"tuple[int | str, ...]",Location of the error
msg,str,Human-readable error message
input,Any,The input value that caused the error
ctx,"dict[str, Any]",(optional) Additional context
url,str,(optional) URL for error documentation
```

## Version Information

```python
from pydantic import __version__
from pydantic.version import version_info
```

```csv
Name,Description
__version__,Pydantic version string (e.g. '2.12.5')
version_info() -> str,"Full version info for Pydantic, pydantic-core, Python, platform, and related packages"
```
