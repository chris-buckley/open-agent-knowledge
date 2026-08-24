# Process

One named ordered way to do a task.

## Examples

```json
[
  {
    "id": "write-oak",
    "part": "processes",
    "name": "Write OAK",
    "steps": [
      {
        "kind": "act",
        "instruction": "Write the knowledge."
      }
    ]
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
  "processes"
]
```

### Name

`name`

The two-word process display name.

```json
[
  "Write OAK",
  "Route command"
]
```

### Steps

`steps`

The typed process steps in authored order.

```json
[
  [
    {
      "kind": "act",
      "instruction": "Write the knowledge.",
      "inputs": [],
      "outputs": []
    }
  ]
]
```
