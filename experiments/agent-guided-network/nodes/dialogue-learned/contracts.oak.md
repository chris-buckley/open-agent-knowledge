<instructions>
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
</instructions>

<schemas>
<schema id="context" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
CONTEXT: <CONTEXT>

WHERE:
- <CONTEXT> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="hidden" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
HIDDEN: <HIDDEN>

WHERE:
- <HIDDEN> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="histories" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
HISTORIES: <HISTORIES>

WHERE:
- <HISTORIES> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="histories-texts" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
HISTORIES: <HISTORIES>
TEXTS: <TEXTS>

WHERE:
- <HISTORIES> is non-empty; the numerical host validates the exact tensor or message contract.
- <TEXTS> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="histories-texts-replies" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
HISTORIES: <HISTORIES>
TEXTS: <TEXTS>
REPLIES: <REPLIES>

WHERE:
- <HISTORIES> is non-empty; the numerical host validates the exact tensor or message contract.
- <TEXTS> is non-empty; the numerical host validates the exact tensor or message contract.
- <REPLIES> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="memory-mask-embedding" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
MEMORY: <MEMORY>
MASK: <MASK>
EMBEDDING: <EMBEDDING>

WHERE:
- <MEMORY> is non-empty; the numerical host validates the exact tensor or message contract.
- <MASK> is non-empty; the numerical host validates the exact tensor or message contract.
- <EMBEDDING> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="memory-state-mask" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
MEMORY: <MEMORY>
STATE: <STATE>
MASK: <MASK>

WHERE:
- <MEMORY> is non-empty; the numerical host validates the exact tensor or message contract.
- <STATE> is non-empty; the numerical host validates the exact tensor or message contract.
- <MASK> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="memory-state-mask-parameters" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
MEMORY: <MEMORY>
STATE: <STATE>
MASK: <MASK>
PARAMETERS: <PARAMETERS>

WHERE:
- <MEMORY> is non-empty; the numerical host validates the exact tensor or message contract.
- <STATE> is non-empty; the numerical host validates the exact tensor or message contract.
- <MASK> is non-empty; the numerical host validates the exact tensor or message contract.
- <PARAMETERS> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="memory-state-previous-tape-embedding" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
MEMORY: <MEMORY>
STATE: <STATE>
PREVIOUS: <PREVIOUS>
TAPE: <TAPE>
EMBEDDING: <EMBEDDING>

WHERE:
- <MEMORY> is non-empty; the numerical host validates the exact tensor or message contract.
- <STATE> is non-empty; the numerical host validates the exact tensor or message contract.
- <PREVIOUS> is non-empty; the numerical host validates the exact tensor or message contract.
- <TAPE> is non-empty; the numerical host validates the exact tensor or message contract.
- <EMBEDDING> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="newprevious-newtape" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
NEWPREVIOUS: <NEWPREVIOUS>
NEWTAPE: <NEWTAPE>

WHERE:
- <NEWPREVIOUS> is non-empty; the numerical host validates the exact tensor or message contract.
- <NEWTAPE> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="newstate" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
NEWSTATE: <NEWSTATE>

WHERE:
- <NEWSTATE> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="replies" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
REPLIES: <REPLIES>

WHERE:
- <REPLIES> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="state-context-previous-embedding" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
STATE: <STATE>
CONTEXT: <CONTEXT>
PREVIOUS: <PREVIOUS>
EMBEDDING: <EMBEDDING>

WHERE:
- <STATE> is non-empty; the numerical host validates the exact tensor or message contract.
- <CONTEXT> is non-empty; the numerical host validates the exact tensor or message contract.
- <PREVIOUS> is non-empty; the numerical host validates the exact tensor or message contract.
- <EMBEDDING> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="state-context-previous-embedding-parameters" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
STATE: <STATE>
CONTEXT: <CONTEXT>
PREVIOUS: <PREVIOUS>
EMBEDDING: <EMBEDDING>
PARAMETERS: <PARAMETERS>

WHERE:
- <STATE> is non-empty; the numerical host validates the exact tensor or message contract.
- <CONTEXT> is non-empty; the numerical host validates the exact tensor or message contract.
- <PREVIOUS> is non-empty; the numerical host validates the exact tensor or message contract.
- <EMBEDDING> is non-empty; the numerical host validates the exact tensor or message contract.
- <PARAMETERS> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="state-context-tape" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
STATE: <STATE>
CONTEXT: <CONTEXT>
TAPE: <TAPE>

WHERE:
- <STATE> is non-empty; the numerical host validates the exact tensor or message contract.
- <CONTEXT> is non-empty; the numerical host validates the exact tensor or message contract.
- <TAPE> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="state-context-tape-parameters" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
STATE: <STATE>
CONTEXT: <CONTEXT>
TAPE: <TAPE>
PARAMETERS: <PARAMETERS>

WHERE:
- <STATE> is non-empty; the numerical host validates the exact tensor or message contract.
- <CONTEXT> is non-empty; the numerical host validates the exact tensor or message contract.
- <TAPE> is non-empty; the numerical host validates the exact tensor or message contract.
- <PARAMETERS> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="state-previous-tape" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
STATE: <STATE>
PREVIOUS: <PREVIOUS>
TAPE: <TAPE>

WHERE:
- <STATE> is non-empty; the numerical host validates the exact tensor or message contract.
- <PREVIOUS> is non-empty; the numerical host validates the exact tensor or message contract.
- <TAPE> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="stored" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
STORED: <STORED>

WHERE:
- <STORED> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="tape" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
TAPE: <TAPE>

WHERE:
- <TAPE> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="texts" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
TEXTS: <TEXTS>

WHERE:
- <TEXTS> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="token" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
TOKEN: <TOKEN>

WHERE:
- <TOKEN> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="tokens" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
TOKENS: <TOKENS>

WHERE:
- <TOKENS> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="tokens-mask" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
TOKENS: <TOKENS>
MASK: <MASK>

WHERE:
- <TOKENS> is non-empty; the numerical host validates the exact tensor or message contract.
- <MASK> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>

<schema id="tokens-parameters" name="Dialogue Payload" purpose="Carry a complete bounded numerical payload.">
TOKENS: <TOKENS>
PARAMETERS: <PARAMETERS>

WHERE:
- <TOKENS> is non-empty; the numerical host validates the exact tensor or message contract.
- <PARAMETERS> is non-empty; the numerical host validates the exact tensor or message contract.
</schema>
</schemas>