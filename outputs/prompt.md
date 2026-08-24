<instructions>
$ reads a value; a dotted path starts with its part; a bare $NAME is local to the running process; SET, CALL, and EMIT omit $.
Each schema is one information shape: a template with <PLACEHOLDER> slots, and WHERE lines that constrain each slot.
Each trigger names one arrival reason, an optional state guard, and the process that runs when both match.
Each process is the exact way to do one task; follow its steps in order, top to bottom.
Reject an empty (SlugId|text) field.
Reject a process with no steps.
Reject unknown fields.
Reject an entry outside the seven parts (instructions|constants|schemas|state|triggers|processes|interfaces).
Require one root node.
Require each child of a node to be a node.
Reject a duplicate SlugId across nodes and entries.
Reject a (missing|wrong-type) reference target.
Omit unset optional fields from the Pydantic dump.
Reject a process value or emit step that conflicts with the interface direction.
Reject an act whose instruction placeholders differ from its inputs and outputs.
Reject a process that reads an unbound local binding.
Reject a process that redefines a visible local binding.
Reject an interface value whose placeholder is absent from the interface schema.
Reject an emit step whose bindings differ from the interface schema placeholders.
Reject a process call cycle.
Reject a statically dead process branch.
Fail one execution when multiple triggers match one cycle.
Reject a process name outside `ProcessName`.
Reject a trigger guard that reads no state value.
Reject a trigger guard that reads an (interface|local binding).
Reject equal trigger `when` values unless every guard pair is provably disjoint.
</instructions>

<constants>
</constants>

<schemas>
<schema id="type" name="Type" purpose="The bound value has one datatype from the vocabulary catalog.">
Type
The bound value has one datatype from the vocabulary catalog.
Fields:
- Kind: The constraint discriminator.
- Of: The datatype name.
Examples:
[
  {
    "kind": "type",
    "of": "string"
  }
]

WHERE:
</schema>

<schema id="one-of" name="OneOf" purpose="The bound value is one of the listed values.">
OneOf
The bound value is one of the listed values.
Fields:
- Kind: The constraint discriminator.
- Values: The allowed values.
Examples:
[
  {
    "kind": "one_of",
    "values": [
      "draft",
      "final"
    ]
  }
]

WHERE:
</schema>

<schema id="regex" name="Regex" purpose="The bound value matches one anchored portable rust-regex pattern.">
Regex
The bound value matches one anchored portable rust-regex pattern.
Fields:
- Kind: The constraint discriminator.
- Pattern: The whole-value portable pattern.
Examples:
[
  {
    "kind": "regex",
    "pattern": "^[0-9]+$"
  }
]

WHERE:
</schema>

<schema id="non-empty" name="NonEmpty" purpose="The bound value has at least one character or item.">
NonEmpty
The bound value has at least one character or item.
Fields:
- Kind: The constraint discriminator.
Examples:
[
  {
    "kind": "non_empty"
  }
]

WHERE:
</schema>

<schema id="max-chars" name="MaxChars" purpose="The bound value has at most n characters.">
MaxChars
The bound value has at most n characters.
Fields:
- Kind: The constraint discriminator.
- N: The character limit.
Examples:
[
  {
    "kind": "max_chars",
    "n": 160
  }
]

WHERE:
</schema>

<schema id="lines" name="Lines" purpose="The bound value has a positive line-count bound.">
Lines
The bound value has a positive line-count bound.
Fields:
- Kind: The constraint discriminator.
- Min: The fewest lines.
- Max: The most lines.
Examples:
[
  {
    "kind": "lines",
    "max": 1
  }
]

WHERE:
</schema>

<schema id="list-of" name="ListOf" purpose="The bound value is items of one datatype joined by one separator.">
ListOf
The bound value is items of one datatype joined by one separator.
Fields:
- Kind: The constraint discriminator.
- Item: The datatype of every item.
- Separator: The text between items.
Examples:
[
  {
    "kind": "list_of",
    "item": "integer",
    "separator": ", "
  }
]

WHERE:
</schema>

<schema id="at-least" name="AtLeast" purpose="The bound value is at least a number or another placeholder value.">
AtLeast
The bound value is at least a number or another placeholder value.
Fields:
- Kind: The constraint discriminator.
- Value: A number or a placeholder of the same schema.
Examples:
[
  {
    "kind": "at_least",
    "value": 1
  }
]

WHERE:
</schema>

<schema id="at-most" name="AtMost" purpose="The bound value is at most a number or another placeholder value.">
AtMost
The bound value is at most a number or another placeholder value.
Fields:
- Kind: The constraint discriminator.
- Value: A number or a placeholder of the same schema.
Examples:
[
  {
    "kind": "at_most",
    "value": 160
  }
]

WHERE:
</schema>

<schema id="where" name="Where" purpose="One placeholder, its constraints, examples, and description.">
Where
One placeholder, its constraints, examples, and description.
Fields:
- Placeholder: The bare placeholder name.
- Constraints: The constraints every bound value must satisfy.
- Examples: Values that satisfy every locally resolvable constraint.
- Description: What the placeholder holds, in one line.
Examples:
[
  {
    "placeholder": "OUTLINE_TITLE",
    "constraints": [
      {
        "kind": "type",
        "of": "string"
      }
    ],
    "description": "title for the outline"
  }
]

WHERE:
</schema>

<schema id="schema" name="Schema" purpose="One reusable information shape: a template and one Where per placeholder.">
Schema
One reusable information shape: a template and one Where per placeholder.
Fields:
- Id: The entry id, unique across the tree.
- Part: The entry part discriminator.
- Name: The display name.
- Purpose: What the information shape is for.
- Template: The literal shape with variable parts written as \u003CPLACEHOLDER\u003E.
- Where: One Where per distinct template placeholder, in authored order.
Examples:
[
  {
    "id": "outline",
    "part": "schemas",
    "name": "Hierarchical Outline",
    "purpose": "Generate a numbered outline.",
    "template": "## \u003COUTLINE_TITLE\u003E\n",
    "where": [
      {
        "placeholder": "OUTLINE_TITLE",
        "constraints": [
          {
            "kind": "type",
            "of": "string"
          }
        ]
      }
    ]
  }
]

WHERE:
</schema>

<schema id="instruction" name="Instruction" purpose="One rule the interpreter must follow.">
Instruction
One rule the interpreter must follow.
Fields:
- Id: The entry id, unique across the tree.
- Part: The entry part discriminator.
- Body: One directive or declarative rule.
Examples:
[
  {
    "id": "read-prd",
    "part": "instructions",
    "body": "Read the product requirements before work."
  }
]

WHERE:
</schema>

<schema id="constant" name="Constant" purpose="One value that stays the same during use.">
Constant
One value that stays the same during use.
Fields:
- Id: The entry id, unique across the tree.
- Part: The entry part discriminator.
- Form: The OAK constant form.
- Value: The value that stays the same.
Examples:
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

WHERE:
</schema>

<schema id="state" name="State" purpose="One JSON value that can change while the interpreter runs.">
State
One JSON value that can change while the interpreter runs.
Fields:
- Id: The entry id, unique across the tree.
- Part: The entry part discriminator.
- Value: The JSON value that can change.
Examples:
[
  {
    "id": "status",
    "part": "state",
    "value": "ready"
  }
]

WHERE:
</schema>

<schema id="literal-value" name="LiteralValue" purpose="One authored JSON value.">
LiteralValue
One authored JSON value.
Fields:
- Source: The process value source discriminator.
- Value: The authored JSON value.
Examples:
[
  {
    "source": "literal",
    "value": "critical"
  }
]

WHERE:
</schema>

<schema id="constant-value" name="ConstantValue" purpose="One value read from a constant entry.">
ConstantValue
One value read from a constant entry.
Fields:
- Source: The process value source discriminator.
- Constant: The constant entry to read.
Examples:
[
  {
    "source": "constant",
    "constant": "policy"
  }
]

WHERE:
</schema>

<schema id="state-value" name="StateValue" purpose="One value read from a state entry.">
StateValue
One value read from a state entry.
Fields:
- Source: The process value source discriminator.
- State: The state entry to read.
Examples:
[
  {
    "source": "state",
    "state": "status"
  }
]

WHERE:
</schema>

<schema id="interface-value" name="InterfaceValue" purpose="One placeholder value read from an active input interface.">
InterfaceValue
One placeholder value read from an active input interface.
Fields:
- Source: The process value source discriminator.
- Interface: The active input interface to read.
- Placeholder: The interface schema placeholder to read.
Examples:
[
  {
    "source": "interface",
    "interface": "request",
    "placeholder": "REQUEST"
  }
]

WHERE:
</schema>

<schema id="binding-value" name="BindingValue" purpose="One value read from a prior process-local binding.">
BindingValue
One value read from a prior process-local binding.
Fields:
- Source: The process value source discriminator.
- Binding: The visible process-local binding to read.
Examples:
[
  {
    "source": "binding",
    "binding": "RESULT"
  }
]

WHERE:
</schema>

<schema id="value-binding" name="ValueBinding" purpose="One placeholder bound to one process value.">
ValueBinding
One placeholder bound to one process value.
Fields:
- Placeholder: The placeholder receiving the process value.
- Value: The process value bound to the placeholder.
Examples:
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

WHERE:
</schema>

<schema id="condition" name="Condition" purpose="One structural JSON comparison.">
Condition
One structural JSON comparison.
Fields:
- Left: The value on the left of the comparison.
- Operator: The structural JSON comparison operator.
- Right: The value on the right of the comparison.
Examples:
[
  {
    "left": {
      "source": "state",
      "state": "status"
    },
    "operator": "equals",
    "right": {
      "source": "literal",
      "value": "ready"
    }
  }
]

WHERE:
</schema>

<schema id="act" name="Act" purpose="One open-ended action with declared inputs and outputs.">
Act
One open-ended action with declared inputs and outputs.
Fields:
- Kind: The process step discriminator.
- Instruction: The action the interpreter performs.
- Inputs: The action input bindings in authored order.
- Outputs: The immutable local bindings the action must produce.
Examples:
[
  {
    "kind": "act",
    "instruction": "Turn \u003CREQUEST\u003E into \u003CRESULT\u003E.",
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

WHERE:
</schema>

<schema id="set" name="Set" purpose="One state write.">
Set
One state write.
Fields:
- Kind: The process step discriminator.
- State: The state entry to write.
- Value: The process value written to the state entry.
Examples:
[
  {
    "kind": "set",
    "state": "status",
    "value": {
      "source": "literal",
      "value": "complete"
    }
  }
]

WHERE:
</schema>

<schema id="emit" name="Emit" purpose="One schema instance emitted through one output interface.">
Emit
One schema instance emitted through one output interface.
Fields:
- Kind: The process step discriminator.
- Interface: The output interface that carries the schema instance.
- Bindings: One value binding for each interface schema placeholder.
Examples:
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

WHERE:
</schema>

<schema id="if" name="If" purpose="One condition with a required then branch and an optional otherwise branch.">
If
One condition with a required then branch and an optional otherwise branch.
Fields:
- Kind: The process step discriminator.
- Condition: The comparison that selects the branch.
- Then: The steps run when the condition is true.
- Otherwise: The steps run when the condition is false.
Examples:
[
  {
    "kind": "if",
    "condition": {
      "left": {
        "source": "state",
        "state": "status"
      },
      "operator": "equals",
      "right": {
        "source": "literal",
        "value": "ready"
      }
    },
    "then": [
      {
        "kind": "set",
        "state": "status",
        "value": {
          "source": "literal",
          "value": "complete"
        }
      }
    ],
    "otherwise": [
      {
        "kind": "fail",
        "message": "The state is not ready."
      }
    ]
  }
]

WHERE:
</schema>

<schema id="call" name="Call" purpose="One synchronous process invocation.">
Call
One synchronous process invocation.
Fields:
- Kind: The process step discriminator.
- Process: The process entry to invoke synchronously.
Examples:
[
  {
    "kind": "call",
    "process": "finalize"
  }
]

WHERE:
</schema>

<schema id="fail" name="Fail" purpose="One explicit process failure.">
Fail
One explicit process failure.
Fields:
- Kind: The process step discriminator.
- Message: The failure message.
Examples:
[
  {
    "kind": "fail",
    "message": "The result is empty."
  }
]

WHERE:
</schema>

<schema id="process" name="Process" purpose="One named ordered way to do a task.">
Process
One named ordered way to do a task.
Fields:
- Id: The entry id, unique across the tree.
- Part: The entry part discriminator.
- Name: The two-word process display name.
- Steps: The typed process steps in authored order.
Examples:
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

WHERE:
</schema>

<schema id="trigger" name="Trigger" purpose="One arrival reason, optional state guard, and selected process.">
Trigger
One arrival reason, optional state guard, and selected process.
Fields:
- Id: The entry id, unique across the tree.
- Part: The entry part discriminator.
- Given: The optional state condition checked after when matches.
- When: Why the interpreter enters the knowledge.
- Process: The process entry selected by the trigger.
Examples:
[
  {
    "id": "write-oak-trigger",
    "part": "triggers",
    "given": {
      "left": {
        "source": "state",
        "state": "status"
      },
      "operator": "equals",
      "right": {
        "source": "literal",
        "value": "ready"
      }
    },
    "when": "The interpreter arrives to write OAK.",
    "process": "write-oak"
  }
]

WHERE:
</schema>

<schema id="interface" name="Interface" purpose="One crossing of information at the tree boundary.">
Interface
One crossing of information at the tree boundary.
Fields:
- Id: The entry id, unique across the tree.
- Part: The entry part discriminator.
- Direction: The direction across the tree boundary.
- Schema: The schema entry that defines the information shape.
- Description: What the tree boundary crossing means.
Examples:
[
  {
    "id": "request",
    "part": "interfaces",
    "direction": "in",
    "schema": "request-shape",
    "description": "The request supplied to the tree."
  }
]

WHERE:
</schema>

<schema id="node" name="Node" purpose="One complete set of the seven parts with nested child nodes.">
Node
One complete set of the seven parts with nested child nodes.
Fields:
- Id: The node id, unique across the tree.
- Instructions: The node instructions in authored order.
- Constants: The node constants in authored order.
- Schemas: The node schemas in authored order.
- State: The node state values in authored order.
- Triggers: The node triggers in authored order.
- Processes: The node processes in authored order.
- Interfaces: The node interfaces in authored order.
- Children: The child nodes in authored order.
Examples:
[
  {
    "id": "example-node",
    "instructions": [
      {
        "id": "use-schema",
        "part": "instructions",
        "body": "Use the supplied schema."
      }
    ]
  }
]

WHERE:
</schema>

<schema id="root" name="Root" purpose="The one root node whose validator checks the complete tree graph.">
Root
The one root node whose validator checks the complete tree graph.
Fields:
- Id: The node id, unique across the tree.
- Instructions: The node instructions in authored order.
- Constants: The node constants in authored order.
- Schemas: The node schemas in authored order.
- State: The node state values in authored order.
- Triggers: The node triggers in authored order.
- Processes: The node processes in authored order.
- Interfaces: The node interfaces in authored order.
- Children: The child nodes in authored order.
Examples:
[
  {
    "id": "root",
    "schemas": [
      {
        "id": "knowledge",
        "part": "schemas",
        "template": "\u003CKNOWLEDGE\u003E",
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
        "template": "\u003CRESULT\u003E",
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
            "instruction": "Transform \u003CKNOWLEDGE\u003E into \u003CRESULT\u003E.",
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

WHERE:
</schema>

<schema id="quantity" name="Quantity" purpose="One decimal value and one unit.">
Quantity
One decimal value and one unit.
Fields:
- Value: The decimal quantity value.
- Unit: The unit selected from the shared catalog.
Examples:
[
  {
    "value": "10",
    "unit": "kg"
  }
]

WHERE:
</schema>

<schema id="date-time" name="DateTime" purpose="One aware datetime and its optional IANA time zone name.">
DateTime
One aware datetime and its optional IANA time zone name.
Fields:
- Value: The datetime with a numeric UTC offset.
- Zone: The optional IANA time zone name.
Examples:
[
  {
    "value": "2026-08-24T17:35:38+10:00",
    "zone": "Australia/Brisbane"
  }
]

WHERE:
</schema>

<schema id="arrival" name="Arrival" purpose="One trigger arrival and its active input values.">
Arrival
One trigger arrival and its active input values.
Fields:
- When: The arrival reason matched against trigger text.
- Interfaces: The active input bindings by interface id.
Examples:
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

WHERE:
</schema>

<schema id="emission" name="Emission" purpose="One validated interface emission.">
Emission
One validated interface emission.
Fields:
- Interface: The output interface id.
- Values: The validated schema bindings.
Examples:
[
  {
    "interface": "stdout",
    "values": {
      "OUTPUT": "/oak"
    }
  }
]

WHERE:
</schema>

<schema id="execution-result" name="ExecutionResult" purpose="The committed result of one arrival cycle.">
ExecutionResult
The committed result of one arrival cycle.
Fields:
- Process: The selected process, or null when none matched.
- State: The state after successful completion.
- Emissions: The emissions in execution order.
Examples:
[
  {
    "process": "pwd",
    "state": {
      "mode": "open"
    },
    "emissions": [
      {
        "interface": "stdout",
        "values": {
          "OUTPUT": "/oak"
        }
      }
    ]
  }
]

WHERE:
</schema>
</schemas>

<state>
</state>

<triggers>
<trigger id="write-oak-trigger" when="A model arrives to write OAK." process="write-oak" />
</triggers>

<processes>
<process id="write-oak" name="Write OAK">
ACT Write OAK from the supplied models.
</process>
</processes>

<interfaces>
</interfaces>
