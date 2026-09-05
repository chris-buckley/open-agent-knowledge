<instructions>
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
</instructions>

<schemas>
<schema id="input" name="Attention Payload" purpose="Carry complete tensor instances for the closed attention host.">
QUERY: <QUERY>
KEY1: <KEY1>
VALUE1: <VALUE1>
MASK1: <MASK1>
KEY2: <KEY2>
VALUE2: <VALUE2>
MASK2: <MASK2>

WHERE:
- <QUERY> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <KEY1> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <VALUE1> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <MASK1> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <KEY2> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <VALUE2> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <MASK2> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
</schema>

<schema id="prediction" name="Attention Payload" purpose="Carry complete tensor instances for the closed attention host.">
PROB: <PROB>

WHERE:
- <PROB> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
</schema>

<schema id="decode" name="Attention Payload" purpose="Carry complete tensor instances for the closed attention host.">
LOGITS: <LOGITS>

WHERE:
- <LOGITS> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
</schema>

<schema id="parameters" name="Attention Payload" purpose="Carry complete tensor instances for the closed attention host.">
WQ: <WQ>
WK: <WK>
WV: <WV>
WO: <WO>

WHERE:
- <WQ> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <WK> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <WV> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <WO> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
</schema>

<schema id="first-input" name="Attention Payload" purpose="Carry complete tensor instances for the closed attention host.">
QUERY: <QUERY>
KEY1: <KEY1>
VALUE1: <VALUE1>
MASK1: <MASK1>

WHERE:
- <QUERY> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <KEY1> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <VALUE1> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <MASK1> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
</schema>

<schema id="first-output" name="Attention Payload" purpose="Carry complete tensor instances for the closed attention host.">
BRIDGE: <BRIDGE>
ALIGN1: <ALIGN1>

WHERE:
- <BRIDGE> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <ALIGN1> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
</schema>

<schema id="first-action" name="Attention Payload" purpose="Carry complete tensor instances for the closed attention host.">
QUERY: <QUERY>
KEY1: <KEY1>
VALUE1: <VALUE1>
MASK1: <MASK1>
WQ: <WQ>
WK: <WK>
WV: <WV>
WO: <WO>

WHERE:
- <QUERY> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <KEY1> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <VALUE1> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <MASK1> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <WQ> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <WK> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <WV> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <WO> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
</schema>

<schema id="second-input" name="Attention Payload" purpose="Carry complete tensor instances for the closed attention host.">
BRIDGE: <BRIDGE>
KEY2: <KEY2>
VALUE2: <VALUE2>
MASK2: <MASK2>

WHERE:
- <BRIDGE> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <KEY2> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <VALUE2> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <MASK2> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
</schema>

<schema id="second-output" name="Attention Payload" purpose="Carry complete tensor instances for the closed attention host.">
LOGITS: <LOGITS>
ALIGN2: <ALIGN2>

WHERE:
- <LOGITS> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <ALIGN2> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
</schema>

<schema id="second-action" name="Attention Payload" purpose="Carry complete tensor instances for the closed attention host.">
BRIDGE: <BRIDGE>
KEY2: <KEY2>
VALUE2: <VALUE2>
MASK2: <MASK2>
WQ: <WQ>
WK: <WK>
WV: <WV>
WO: <WO>

WHERE:
- <BRIDGE> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <KEY2> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <VALUE2> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <MASK2> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <WQ> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <WK> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <WV> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
- <WO> is non-empty; exact rank, dimensions, finite values and masking are checked by the numerical host.
</schema>
</schemas>