# Pydantic v2 -- Errors

## ValidationError

Raised automatically when data fails validation. Never raise it yourself from validators -- raise `ValueError` or `AssertionError` instead, and Pydantic wraps them.

```python
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    name: str
    age: int

try:
    User(name='Alice', age='not-a-number')
except ValidationError as e:
    print(e.error_count())   # 1
    print(e.errors())        # list[ErrorDetails]
    print(e.json())          # JSON string of errors list
    print(str(e))            # human-readable multi-line summary
```

### ErrorDetails dict

Each item from `.errors()` is a `TypedDict` with these keys:

```csv
Key,Type,Description
type,str,Machine-readable error code (e.g. 'missing')
loc,"tuple[str | int, ...]",Path to the error (field names and list indices)
msg,str,Human-readable message
input,Any,The value that failed validation
ctx,"dict[str, Any] | None",Context values used in the message template
url,str,Link to error docs at errors.pydantic.dev
```

### Location (loc) field

The `loc` tuple describes the path to the error through nested models and containers:

```python
# Top-level field:        ('field_name',)
# Nested model field:     ('parent_field', 'child_field')
# List element:           ('list_field', 2)
# Nested list in model:   ('items', 1, 'value')
```

Example output: `('recursive_model', 'lng')` means field `lng` inside nested model `recursive_model`.

## Common Validation Error Types

### Field presence and extras

```csv
Type,Trigger
missing,Required field not provided
extra_forbidden,Extra field when model_config = ConfigDict(extra='forbid')
frozen_field,Assigning to a field with frozen=True
frozen_instance,Assigning to any field when model has frozen=True config
```

### Type errors (wrong Python type)

```csv
Type,Expected type
string_type,str
int_type,int
float_type,float
bool_type,bool
bytes_type,bytes
list_type,list
dict_type,dict
set_type,set
tuple_type,tuple
model_type,BaseModel or dict
date_type,date
datetime_type,datetime
```

These are raised when the value cannot be coerced to the target type. In strict mode, no coercion is attempted at all.

### Parsing errors (string cannot be converted)

```csv
Type,Input string cannot be parsed as
int_parsing,int
float_parsing,float
bool_parsing,bool
date_parsing,date
datetime_parsing,datetime
uuid_parsing,UUID
url_parsing,URL
json_invalid,JSON
decimal_parsing,Decimal
```

### Numeric constraints

```csv
Type,Constraint,Field param
greater_than,value > X,gt=X
greater_than_equal,value >= X,ge=X
less_than,value < X,lt=X
less_than_equal,value <= X,le=X
multiple_of,value % X == 0,multiple_of=X
finite_number,"not inf, not too large",(automatic)
```

### String constraints

```csv
Type,Constraint,Field param
string_too_short,len < min,min_length=N
string_too_long,len > max,max_length=N
string_pattern_mismatch,does not match regex,pattern='...'
```

### Collection constraints

```csv
Type,Constraint,Field param
too_short,len < min,min_length=N
too_long,len > max,max_length=N
```

### Value and assertion errors (from validators)

```csv
Type,Source
value_error,raise ValueError(...) in a validator
assertion_error,assert statement fails in a validator
```

### Discriminated union errors

```csv
Type,Cause
union_tag_not_found,Discriminator field missing from input
union_tag_invalid,Discriminator value doesn't match any variant
literal_error,Value not in Literal[...] options
```

### Other notable errors

```csv
Type,Cause
enum,Value not a valid enum member
is_instance_of,Value not an instance of expected type (arbitrary types)
recursion_loop,Cyclic reference detected during validation
none_required,Expected None but got something else
no_such_attribute,Assigning undefined field with validate_assignment
get_attribute_error,Error reading attribute with from_attributes=True
callable_type,Value is not callable
url_scheme,URL scheme doesn't match (e.g. ftp:// for HttpUrl)
```

## Custom Error Messages

### Post-processing approach

Build a mapping from error `type` to custom message, then rewrite after catching:

```python
from pydantic_core import ErrorDetails
from pydantic import BaseModel, HttpUrl, ValidationError

CUSTOM_MESSAGES = {
    'int_parsing': 'Please provide a valid integer.',
    'url_scheme': 'URL must use {expected_schemes}.',
}

def convert_errors(e: ValidationError, custom_messages: dict[str, str]) -> list[ErrorDetails]:
    new_errors: list[ErrorDetails] = []
    for error in e.errors():
        custom_message = custom_messages.get(error['type'])
        if custom_message:
            ctx = error.get('ctx')
            error['msg'] = custom_message.format(**ctx) if ctx else custom_message
        new_errors.append(error)
    return new_errors

class Config(BaseModel):
    port: int
    url: HttpUrl

try:
    Config(port='abc', url='ftp://x.com')
except ValidationError as e:
    errors = convert_errors(e, CUSTOM_MESSAGES)
```

The `ctx` dict contains template variables from the original error (e.g. `{'gt': 42}` for `greater_than`, `{'expected_schemes': "'http' or 'https'"}` for `url_scheme`).

### Custom loc formatting

Convert the default tuple-based `loc` to dot notation:

```python
def loc_to_dot_sep(loc: tuple[str | int, ...]) -> str:
    path = ''
    for i, x in enumerate(loc):
        if isinstance(x, str):
            if i > 0:
                path += '.'
            path += x
        elif isinstance(x, int):
            path += f'[{x}]'
    return path

# ('items', 1, 'value') -> 'items[1].value'
```

### PydanticCustomError (from validators)

Raise in validators to produce custom error types and messages:

```python
from pydantic_core import PydanticCustomError
from pydantic import BaseModel, field_validator

class Order(BaseModel):
    quantity: int

    @field_validator('quantity')
    @classmethod
    def check_quantity(cls, v: int) -> int:
        if v <= 0:
            raise PydanticCustomError(
                'positive_required',           # custom type code
                'Value must be positive, got {value}',  # message template
                {'value': v},                  # context dict
            )
        return v
```

## PydanticUserError (Usage Errors)

Raised at class definition time (not during validation) when Pydantic is used incorrectly. These are `TypeError` subclasses. Each has a `.code` attribute.

### Most common usage errors

```csv
Code,Cause and fix
class-not-fully-defined,"Forward ref type not yet defined. Fix: define the type, then call Model.model_rebuild()."
model-field-missing-annotation,Field declared without type annotation. Fix: add annotation or use ClassVar.
decorator-missing-field,@field_validator('x') but field x doesn't exist. Fix: correct name or use check_fields=False.
validator-no-fields,@field_validator used without field names. Fix: @field_validator('field_name').
validator-invalid-fields,"Fields passed as list instead of separate args. Fix: @field_validator('a', 'b') not @field_validator(['a', 'b'])."
validator-instance-method,Validator is an instance method (has self). Fix: use @classmethod.
validator-signature,Wrong number of params on @field_validator. Needs cls and v minimum.
config-both,Both class Config and model_config defined. Pick one (use model_config).
removed-kwargs,V1 keyword (e.g. regex) used in Field(). Use V2 equivalent (pattern).
model-field-overridden,Base class field overridden without annotation in subclass.
undefined-annotation,Forward ref can't be resolved. Call model_rebuild() after defining the type.
schema-for-unknown-type,Type annotation Pydantic can't handle (e.g. a literal int value as a type).
base-model-instantiated,BaseModel() called directly. Always subclass it.
model-config-invalid-field-name,Field named model_config. Use a different name.
discriminator-no-field,Discriminated union member missing the discriminator field.
discriminator-needs-literal,Discriminator field is not Literal type.
discriminator-validator,Before/wrap/plain validator on discriminator field. Remove it or drop discriminator.
type-adapter-config-unused,Passing config to TypeAdapter for a type that has its own config. Set config on the type directly.
root-model-extra,extra config on RootModel. Not supported.
model-serializer-instance-method,@model_serializer not on instance method. Must have self.
with-config-on-model,@with_config on a BaseModel subclass. Use model_config instead.
dataclass-on-model,@dataclass decorator on a BaseModel subclass. Use one or the other.
validate-call-type,"@validate_call on unsupported callable (class, @classmethod in wrong order, callable instance)."
```

### Other Pydantic-specific errors

```csv
Class,Base,When
PydanticUserError,TypeError,Incorrect API usage (see table above)
PydanticUndefinedAnnotation,NameError,Forward ref can't be resolved
PydanticImportError,ImportError,V1 import path used in V2
PydanticSchemaGenerationError,--,Core schema generation failed
PydanticInvalidForJsonSchema,--,Type can't be represented in JSON Schema
```

## Error Handling Patterns

### Basic catch and report

```python
from pydantic import BaseModel, ValidationError

class Item(BaseModel):
    name: str
    price: float

def create_item(data: dict) -> Item | None:
    try:
        return Item(**data)
    except ValidationError as e:
        for err in e.errors():
            field = '.'.join(str(x) for x in err['loc'])
            print(f"  {field}: {err['msg']} (type={err['type']})")
        return None
```

### FastAPI integration

FastAPI catches `ValidationError` automatically for request body/params and returns 422 responses. For manual validation inside endpoints:

```python
from fastapi import HTTPException
from pydantic import BaseModel, ValidationError

class Settings(BaseModel):
    threshold: float

def apply_settings(raw: dict):
    try:
        s = Settings(**raw)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    return s
```

### Collecting errors from multiple sources

```python
all_errors = []
for i, record in enumerate(records):
    try:
        Model(**record)
    except ValidationError as e:
        for err in e.errors():
            all_errors.append({
                'record': i,
                'loc': err['loc'],
                'msg': err['msg'],
                'type': err['type'],
            })
```

### Filtering errors by type

```python
try:
    Model(**data)
except ValidationError as e:
    missing = [err for err in e.errors() if err['type'] == 'missing']
    type_errors = [err for err in e.errors() if err['type'].endswith('_type')]
```
