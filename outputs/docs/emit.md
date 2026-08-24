# Emit

One schema instance emitted through one output interface.

## Examples

```json
[
  {
    "kind": "emit",
    "interface": "result",
    "bindings": [
      {
        "placeholder": "RESULT",
        "value": {
          "source": "binding",
          "binding": "RESULT"
        }
      }
    ]
  }
]
```

## Fields

### Kind

`kind`

The process step discriminator.

```json
[
  "emit"
]
```

### Interface

`interface`

The output interface that carries the schema instance.

```json
[
  "result"
]
```

### Bindings

`bindings`

One value binding for each interface schema placeholder.

```json
[
  [
    {
      "placeholder": "RESULT",
      "value": {
        "source": "binding",
        "binding": "RESULT"
      }
    }
  ]
]
```
