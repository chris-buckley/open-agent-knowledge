# Act

One open-ended action with declared inputs and outputs.

## Examples

```json
[
  {
    "kind": "act",
    "instruction": "Turn <REQUEST> into <RESULT>.",
    "inputs": [
      {
        "placeholder": "REQUEST",
        "value": {
          "source": "interface",
          "interface": "request",
          "placeholder": "REQUEST"
        }
      }
    ],
    "outputs": [
      "RESULT"
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
  "act"
]
```

### Instruction

`instruction`

The action the interpreter performs.

```json
[
  "Turn <REQUEST> into <RESULT>."
]
```

### Inputs

`inputs`

The action input bindings in authored order.

```json
[
  [
    {
      "placeholder": "REQUEST",
      "value": {
        "source": "interface",
        "interface": "request",
        "placeholder": "REQUEST"
      }
    }
  ]
]
```

### Outputs

`outputs`

The immutable local bindings the action must produce.

```json
[
  [
    "RESULT"
  ]
]
```
