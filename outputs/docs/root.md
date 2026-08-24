# Root

The one root node whose validator checks the complete tree graph.

## Examples

```json
[
  {
    "id": "root",
    "schemas": [
      {
        "id": "knowledge",
        "part": "schemas",
        "template": "<KNOWLEDGE>",
        "where": [
          {
            "placeholder": "KNOWLEDGE",
            "constraints": [
              {
                "kind": "type",
                "of": "string"
              }
            ]
          }
        ]
      },
      {
        "id": "result",
        "part": "schemas",
        "template": "<RESULT>",
        "where": [
          {
            "placeholder": "RESULT",
            "constraints": [
              {
                "kind": "type",
                "of": "string"
              }
            ]
          }
        ]
      }
    ],
    "triggers": [
      {
        "id": "run-trigger",
        "part": "triggers",
        "when": "The interpreter arrives to transform knowledge.",
        "process": "run"
      }
    ],
    "processes": [
      {
        "id": "run",
        "part": "processes",
        "name": "Transform knowledge",
        "steps": [
          {
            "kind": "act",
            "instruction": "Transform <KNOWLEDGE> into <RESULT>.",
            "inputs": [
              {
                "placeholder": "KNOWLEDGE",
                "value": {
                  "source": "interface",
                  "interface": "knowledge-interface",
                  "placeholder": "KNOWLEDGE"
                }
              }
            ],
            "outputs": [
              "RESULT"
            ]
          },
          {
            "kind": "emit",
            "interface": "result-interface",
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
      }
    ],
    "interfaces": [
      {
        "id": "knowledge-interface",
        "part": "interfaces",
        "direction": "in",
        "schema": "knowledge"
      },
      {
        "id": "result-interface",
        "part": "interfaces",
        "direction": "out",
        "schema": "result"
      }
    ]
  }
]
```

## Fields

### Id

`id`

The node id, unique across the tree.

```json
[
  "root"
]
```

### Instructions

`instructions`

The node instructions in authored order.

```json
[
  []
]
```

### Constants

`constants`

The node constants in authored order.

```json
[
  []
]
```

### Schemas

`schemas`

The node schemas in authored order.

```json
[
  [
    {
      "id": "knowledge",
      "part": "schemas",
      "name": null,
      "purpose": null,
      "template": "<KNOWLEDGE>",
      "where": [
        {
          "placeholder": "KNOWLEDGE",
          "constraints": [
            {
              "kind": "type",
              "of": "string"
            }
          ],
          "examples": [],
          "description": null
        }
      ]
    },
    {
      "id": "result",
      "part": "schemas",
      "name": null,
      "purpose": null,
      "template": "<RESULT>",
      "where": [
        {
          "placeholder": "RESULT",
          "constraints": [
            {
              "kind": "type",
              "of": "string"
            }
          ],
          "examples": [],
          "description": null
        }
      ]
    }
  ]
]
```

### State

`state`

The node state values in authored order.

```json
[
  []
]
```

### Triggers

`triggers`

The node triggers in authored order.

```json
[
  [
    {
      "id": "run-trigger",
      "part": "triggers",
      "given": null,
      "when": "The interpreter arrives to transform knowledge.",
      "process": "run"
    }
  ]
]
```

### Processes

`processes`

The node processes in authored order.

```json
[
  [
    {
      "id": "run",
      "part": "processes",
      "name": "Transform knowledge",
      "steps": [
        {
          "kind": "act",
          "instruction": "Transform <KNOWLEDGE> into <RESULT>.",
          "inputs": [
            {
              "placeholder": "KNOWLEDGE",
              "value": {
                "source": "interface",
                "interface": "knowledge-interface",
                "placeholder": "KNOWLEDGE"
              }
            }
          ],
          "outputs": [
            "RESULT"
          ]
        },
        {
          "kind": "emit",
          "interface": "result-interface",
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
    }
  ]
]
```

### Interfaces

`interfaces`

The node interfaces in authored order.

```json
[
  [
    {
      "id": "knowledge-interface",
      "part": "interfaces",
      "direction": "in",
      "schema": "knowledge",
      "description": null
    },
    {
      "id": "result-interface",
      "part": "interfaces",
      "direction": "out",
      "schema": "result",
      "description": null
    }
  ]
]
```

### Children

`children`

The child nodes in authored order.

```json
[
  []
]
```
