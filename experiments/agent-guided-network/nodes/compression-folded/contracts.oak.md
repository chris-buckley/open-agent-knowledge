<instructions>
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
</instructions>

<schemas>
<schema id="input" name="Compact Attention Payload" purpose="Carry a complete compact-host payload.">
QUERY: <QUERY>
KEY1: <KEY1>
VALUE1: <VALUE1>
MASK1: <MASK1>
KEY2: <KEY2>
VALUE2: <VALUE2>
MASK2: <MASK2>

WHERE:
- <QUERY> is non-empty; the host checks exact numerical shape and encoding.
- <KEY1> is non-empty; the host checks exact numerical shape and encoding.
- <VALUE1> is non-empty; the host checks exact numerical shape and encoding.
- <MASK1> is non-empty; the host checks exact numerical shape and encoding.
- <KEY2> is non-empty; the host checks exact numerical shape and encoding.
- <VALUE2> is non-empty; the host checks exact numerical shape and encoding.
- <MASK2> is non-empty; the host checks exact numerical shape and encoding.
</schema>

<schema id="prediction" name="Compact Attention Payload" purpose="Carry a complete compact-host payload.">
PROB: <PROB>

WHERE:
- <PROB> is non-empty; the host checks exact numerical shape and encoding.
</schema>

<schema id="decode" name="Compact Attention Payload" purpose="Carry a complete compact-host payload.">
LOGITS: <LOGITS>

WHERE:
- <LOGITS> is non-empty; the host checks exact numerical shape and encoding.
</schema>

<schema id="kernel" name="Compact Attention Payload" purpose="Carry a complete compact-host payload.">
KERNEL: <KERNEL>

WHERE:
- <KERNEL> is non-empty; the host checks exact numerical shape and encoding.
</schema>

<schema id="first-input" name="Compact Attention Payload" purpose="Carry a complete compact-host payload.">
QUERY: <QUERY>
KEY1: <KEY1>
VALUE1: <VALUE1>
MASK1: <MASK1>

WHERE:
- <QUERY> is non-empty; the host checks exact numerical shape and encoding.
- <KEY1> is non-empty; the host checks exact numerical shape and encoding.
- <VALUE1> is non-empty; the host checks exact numerical shape and encoding.
- <MASK1> is non-empty; the host checks exact numerical shape and encoding.
</schema>

<schema id="first-output" name="Compact Attention Payload" purpose="Carry a complete compact-host payload.">
BRIDGE: <BRIDGE>
ALIGN1: <ALIGN1>

WHERE:
- <BRIDGE> is non-empty; the host checks exact numerical shape and encoding.
- <ALIGN1> is non-empty; the host checks exact numerical shape and encoding.
</schema>

<schema id="first-action" name="Compact Attention Payload" purpose="Carry a complete compact-host payload.">
QUERY: <QUERY>
KEY1: <KEY1>
VALUE1: <VALUE1>
MASK1: <MASK1>
SCORE: <SCORE>

WHERE:
- <QUERY> is non-empty; the host checks exact numerical shape and encoding.
- <KEY1> is non-empty; the host checks exact numerical shape and encoding.
- <VALUE1> is non-empty; the host checks exact numerical shape and encoding.
- <MASK1> is non-empty; the host checks exact numerical shape and encoding.
- <SCORE> is non-empty; the host checks exact numerical shape and encoding.
</schema>

<schema id="second-input" name="Compact Attention Payload" purpose="Carry a complete compact-host payload.">
BRIDGE: <BRIDGE>
KEY2: <KEY2>
VALUE2: <VALUE2>
MASK2: <MASK2>

WHERE:
- <BRIDGE> is non-empty; the host checks exact numerical shape and encoding.
- <KEY2> is non-empty; the host checks exact numerical shape and encoding.
- <VALUE2> is non-empty; the host checks exact numerical shape and encoding.
- <MASK2> is non-empty; the host checks exact numerical shape and encoding.
</schema>

<schema id="second-output" name="Compact Attention Payload" purpose="Carry a complete compact-host payload.">
LOGITS: <LOGITS>
ALIGN2: <ALIGN2>

WHERE:
- <LOGITS> is non-empty; the host checks exact numerical shape and encoding.
- <ALIGN2> is non-empty; the host checks exact numerical shape and encoding.
</schema>

<schema id="second-action" name="Compact Attention Payload" purpose="Carry a complete compact-host payload.">
BRIDGE: <BRIDGE>
KEY2: <KEY2>
VALUE2: <VALUE2>
MASK2: <MASK2>
SCORE: <SCORE>
OUTPUT: <OUTPUT>

WHERE:
- <BRIDGE> is non-empty; the host checks exact numerical shape and encoding.
- <KEY2> is non-empty; the host checks exact numerical shape and encoding.
- <VALUE2> is non-empty; the host checks exact numerical shape and encoding.
- <MASK2> is non-empty; the host checks exact numerical shape and encoding.
- <SCORE> is non-empty; the host checks exact numerical shape and encoding.
- <OUTPUT> is non-empty; the host checks exact numerical shape and encoding.
</schema>
</schemas>