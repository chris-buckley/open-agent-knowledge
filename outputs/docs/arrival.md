# Arrival

One trigger arrival and its active input values.

## Examples

```json
[
  {
    "when": "A command line arrives.",
    "interfaces": {
      "stdin": {
        "COMMAND": "pwd"
      }
    }
  }
]
```

## Fields

### When

`when`

The arrival reason matched against trigger text.

```json
[
  "A command line arrives."
]
```

### Interfaces

`interfaces`

The active input bindings by interface id.

```json
[
  {
    "stdin": {
      "COMMAND": "pwd"
    }
  }
]
```
