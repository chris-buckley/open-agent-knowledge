# State

One JSON value that can change while the interpreter runs.

## Examples

```json
[
  {
    "id": "status",
    "part": "state",
    "value": "ready"
  }
]
```

## Fields

### Id

`id`

The entry id, unique across the tree.

```json
[
  "example"
]
```

### Part

`part`

The entry part discriminator.

```json
[
  "state"
]
```

### Value

`value`

The JSON value that can change.

```json
[
  "ready",
  0,
  {
    "complete": false
  }
]
```
