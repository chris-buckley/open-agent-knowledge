# Pydantic v2 Types -- Pitfalls

## 1. Lax Mode Coercion Surprises

Problem: By default, Pydantic coerces compatible types. `'123'` becomes `123` for `int` fields. This is often undesired for API inputs where you want type safety.

```python
class Model(BaseModel):
    count: int

m = Model(count='42')  # succeeds, count=42 (not a string)
```

Fix: Use `StrictInt`, `Field(strict=True)`, or `ConfigDict(strict=True)`.

## 2. Union Order Matters in `left_to_right` Mode

Problem: With `union_mode='left_to_right'`, the string `'456'` matches `int` first because numeric strings are coercible to int in lax mode.

```python
class User(BaseModel):
    id: int | str = Field(union_mode='left_to_right')

print(User(id='456').id)  # 456 (int!), not '456' (str)
```

Fix: Use `smart` mode (default), put more specific types first, or use discriminated unions. Smart mode picks the "best" match -- `str` for a string input.

## 3. Smart Union Mode Is Not Guaranteed Stable

Problem: The internal `smart` union matching algorithm may change between Pydantic minor releases.

Fix: If you need deterministic matching behavior, use `union_mode='left_to_right'` or discriminated unions.

## 4. Discriminated Unions with Single Variant

Problem: `Union[Cat]` collapses to `Cat` at the Python level. Pydantic cannot distinguish `Union[T]` from `T`, so discriminated unions require at least two variants.

```python
# This will NOT work as expected:
class Model(BaseModel):
    pet: Union[Cat] = Field(discriminator='pet_type')  # Union[Cat] == Cat
```

Fix: Discriminated unions must have 2+ members.

## 5. Callable Discriminators Must Handle Both dict and Model

Problem: Callable discriminators receive `dict` during validation but model instances during serialization. Forgetting to handle both causes runtime errors.

```python
# WRONG -- only handles dict:
def discriminator(v):
    return v['type']  # fails on model instances

# CORRECT:
def discriminator(v):
    if isinstance(v, dict):
        return v.get('type')
    return getattr(v, 'type', None)
```

## 6. TypeAdapter Is Not a Type Annotation

Problem: `TypeAdapter` instances cannot be used as field types in models.

```python
ta = TypeAdapter(list[int])

# WRONG:
class Model(BaseModel):
    items: ta  # TypeError -- ta is an instance, not a type

# CORRECT -- use the type directly:
class Model(BaseModel):
    items: list[int]
```

## 7. TypeAdapter Creation Overhead

Problem: Each `TypeAdapter(SomeType)` call builds a full validation schema. Creating them in hot loops is expensive.

```python
# WRONG:
for item in data:
    TypeAdapter(int).validate_python(item)

# CORRECT:
ta = TypeAdapter(int)
for item in data:
    ta.validate_python(item)
```

## 8. TypeAdapter.dump_json Returns bytes, Not str

Problem: Unlike `BaseModel.model_dump_json()` which returns `str`, `TypeAdapter.dump_json()` returns `bytes`. This is a deliberate V2 design choice but catches people off guard.

```python
ta = TypeAdapter(list[int])
result = ta.dump_json([1, 2, 3])
print(type(result))  # <class 'bytes'>  -- not str!
print(result)        # b'[1,2,3]'
```

Fix: Call `.decode()` if you need a `str`.

## 9. Forward References Require model_rebuild()

Problem: If type `B` is defined after model `A` that references it, Pydantic cannot resolve the forward reference at class definition time.

```python
class A(BaseModel):
    b: 'B | None' = None

class B(BaseModel):
    value: int

# Without rebuild, A doesn't know about B:
A.model_rebuild()  # REQUIRED
```

For `TypeAdapter`, use `defer_build=True` and call `.rebuild()` after the type is defined.

## 10. TypeAdapter Forward Reference Namespace

Problem: `TypeAdapter` resolves forward references from the caller's frame globals, not the module where the type was defined. This can cause incorrect resolution if the type alias is imported from another module.

```python
# a.py
IntList = list[int]
OuterDict = dict[str, 'IntList']

# b.py
from a import OuterDict
IntList = int  # shadows the original IntList!
v = TypeAdapter(OuterDict)
v.validate_python({'x': 1})  # works but resolves IntList as int, not list[int]
```

Fix: Be careful with forward references in type aliases used across modules. `BaseModel` handles this better because it resolves in its own `__module__`.

## 11. Named Type Aliases Cannot Contain Field-Specific Metadata

Problem: Named aliases (`TypeAliasType` or PEP 695 `type` statement) cannot contain `default`, `alias`, `deprecated`, or other field-specific metadata.

```python
from typing_extensions import TypeAliasType

# WRONG -- alias/default are field-specific, not type-specific:
MyAlias = TypeAliasType('MyAlias', Annotated[int, Field(default=1)])

class Model(BaseModel):
    x: MyAlias  # NOT allowed -- behavior is undefined
```

Fix: Only use validation constraints (e.g., `gt`, `min_length`, `Strict()`) in named aliases. Apply field metadata at the field definition site.

## 12. bool Is a Subclass of int

Problem: In Python, `bool` is a subclass of `int`. In strict mode, `True`/`False` are explicitly rejected for `int` and `float` fields, but in lax mode they are accepted.

```python
class Model(BaseModel):
    count: int

print(Model(count=True).count)  # 1 (lax mode accepts bool as int)
```

Fix: Use `StrictInt` to reject booleans, or add a validator.

## 13. EmailStr Requires email-validator Package

Problem: `EmailStr` and `NameEmail` from `pydantic.networks` require the `email-validator` package. Without it, you get an `ImportError` at runtime, not at import time of your module.

Fix: Install with `pip install pydantic[email]` or `pip install email-validator`.

## 14. Strict Mode Behaves Differently for JSON vs Python

Problem: In strict mode, date/time types accept ISO format strings when validating JSON (since JSON has no native date type), but reject strings when validating Python objects.

```python
ta = TypeAdapter(date)

ta.validate_json('"2000-01-01"', strict=True)      # OK (JSON has no date type)
ta.validate_python('2000-01-01', strict=True)       # RAISES (Python has date type)
```

This is by design but can be confusing.

## 15. Recursive Type Aliases Need Named Aliases

Problem: Implicit (unnamed) recursive type aliases fail because Python cannot resolve the self-reference.

```python
# WRONG -- NameError: Json is not defined
Json = Union[dict[str, Json], list[Json], str, int, float, bool, None]

# CORRECT -- use TypeAliasType:
from typing_extensions import TypeAliasType
Json = TypeAliasType('Json', 'Union[dict[str, Json], list[Json], str, int, float, bool, None]')
```

Named aliases are lazily evaluated, so forward self-references work.

## 16. Secret Types Serialize as Masked by Default

Problem: `SecretStr` and `SecretBytes` serialize to `'**********'` by default. If you need the actual value in serialization (e.g., writing to a config file), you must explicitly extract it.

```python
cfg.model_dump()  # {'password': SecretStr('**********')} -- masked!
```

Fix: Use a custom serializer, or call `.get_secret_value()` explicitly.

## 17. ImportString Default Values Need validate_default=True

Problem: When setting an `ImportString` field's default to a string value, the string is NOT automatically imported unless `validate_default=True` is set.

```python
class Config(BaseModel):
    handler: ImportString = 'math.cos'  # default stays as string 'math.cos'

c = Config()
print(c.handler)  # 'math.cos' (string, NOT the cos function!)
```

Fix: Use `Field(default='math.cos', validate_default=True)` or set the default to the actual Python object (`math.cos`).

## 18. conint/confloat/constr Are Legacy

Problem: The `conint()`, `confloat()`, `constr()` etc. functions work but are considered legacy. They are less composable than the `Annotated` pattern.

Fix: Prefer `Annotated[int, Field(gt=0)]` or `Annotated[str, StringConstraints(min_length=1)]` for new code.

## 19. __get_validators__ Is Deprecated

Problem: The V1-style `__get_validators__` method is deprecated in V2. Types that only implement this will show deprecation warnings.

Fix: Implement `__get_pydantic_core_schema__` instead. This gives you full control over validation, serialization, and JSON schema generation.

## 20. Annotated Metadata Must Be Hashable for Unions

Problem: If you use a custom annotation class in `Annotated` and that type appears in a `Union`, the annotation must be hashable. Without `frozen=True` on a dataclass annotation, you get a `TypeError`.

```python
@dataclass  # WRONG -- not hashable
class MyValidator:
    func: Callable
    def __get_pydantic_core_schema__(self, ...): ...

# Fails in: Annotated[str, MyValidator(str.lower)] | None

@dataclass(frozen=True)  # CORRECT -- hashable
class MyValidator:
    func: Callable
    def __get_pydantic_core_schema__(self, ...): ...
```
