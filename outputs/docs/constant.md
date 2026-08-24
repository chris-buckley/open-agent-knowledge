# Constant

One value that stays the same during use.

## Examples

```json
[
  {
    "id": "default-time-zone",
    "part": "constants",
    "value": "Z"
  },
  {
    "id": "repository-tree",
    "part": "constants",
    "form": "text",
    "value": "oak\n└── SKILL.md"
  },
  {
    "id": "api-config",
    "part": "constants",
    "form": "json",
    "value": {
      "retries": 3,
      "timeout_ms": 2000
    }
  },
  {
    "id": "service-table",
    "part": "constants",
    "form": "csv",
    "value": [
      {
        "service": "billing",
        "enabled": true
      }
    ]
  },
  {
    "id": "deployment-config",
    "part": "constants",
    "form": "yaml",
    "value": {
      "region": "ap-southeast-2",
      "replicas": 2
    }
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
  "constants"
]
```

### Form

`form`

The OAK constant form.

```json
[
  "inline",
  "text",
  "json",
  "csv",
  "yaml"
]
```

### Value

`value`

The value that stays the same.

```json
[
  "Z",
  "oak\n└── SKILL.md",
  {
    "enabled": true
  },
  [
    {
      "service": "billing",
      "enabled": true
    }
  ]
]
```
