<instructions>
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
</instructions>

<schemas>
<schema id="relations" name="Tensor Payload" purpose="Carry complete float64 tensors checked by the numerical host.">
X: <X>

WHERE:
- <X> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
</schema>

<schema id="pair" name="Tensor Payload" purpose="Carry complete float64 tensors checked by the numerical host.">
LEFT: <LEFT>
RIGHT: <RIGHT>

WHERE:
- <LEFT> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
- <RIGHT> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
</schema>

<schema id="evidence" name="Tensor Payload" purpose="Carry complete float64 tensors checked by the numerical host.">
COUNT: <COUNT>
X: <X>

WHERE:
- <COUNT> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
- <X> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
</schema>

<schema id="left-values" name="Tensor Payload" purpose="Carry complete float64 tensors checked by the numerical host.">
LEFT: <LEFT>

WHERE:
- <LEFT> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
</schema>

<schema id="right-values" name="Tensor Payload" purpose="Carry complete float64 tensors checked by the numerical host.">
RIGHT: <RIGHT>

WHERE:
- <RIGHT> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
</schema>

<schema id="counts" name="Tensor Payload" purpose="Carry complete float64 tensors checked by the numerical host.">
COUNT: <COUNT>

WHERE:
- <COUNT> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
</schema>

<schema id="probabilities" name="Tensor Payload" purpose="Carry complete float64 tensors checked by the numerical host.">
PROB: <PROB>

WHERE:
- <PROB> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
</schema>

<schema id="parameters" name="Tensor Payload" purpose="Carry complete float64 tensors checked by the numerical host.">
W: <W>

WHERE:
- <W> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
</schema>

<schema id="left-action" name="Tensor Payload" purpose="Carry complete float64 tensors checked by the numerical host.">
X: <X>
W: <W>

WHERE:
- <X> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
- <W> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
</schema>

<schema id="right-action" name="Tensor Payload" purpose="Carry complete float64 tensors checked by the numerical host.">
X: <X>
W: <W>

WHERE:
- <X> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
- <W> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
</schema>

<schema id="compose-action" name="Tensor Payload" purpose="Carry complete float64 tensors checked by the numerical host.">
LEFT: <LEFT>
RIGHT: <RIGHT>
W: <W>

WHERE:
- <LEFT> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
- <RIGHT> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
- <W> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
</schema>

<schema id="readout-action" name="Tensor Payload" purpose="Carry complete float64 tensors checked by the numerical host.">
COUNT: <COUNT>
X: <X>
W: <W>

WHERE:
- <COUNT> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
- <X> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
- <W> is non-empty; a finite rectangular numerical tensor with exact dimensions are checked by the profile.
</schema>
</schemas>