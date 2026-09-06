<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; Targets of SET, CALL, EMIT, and trigger source or process fields omit $.
Process input schemas seed local bindings, process output schemas validate successful outputs, and CALL binds inputs and promotes declared outputs.
ACT input and output schemas validate resolved inputs before invocation and produced outputs before promotion.
RECEIVES accepts one complete instance of its schema.
A source-backed trigger supplies the received instance as the selected process input.
EMITS publishes one complete instance of its schema.
EMIT without bindings fills the target schema from same-named visible process bindings.
Constants hold values that do not change while the knowledge runs.
Each trigger is one named declaration: event carries the meaning, an optional source names the exact receive interface, an optional guard checks state after the match, and process selects the work.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
profile: "oak-generated-dialogue-v1"

vocabulary: ["<pad>", "<bos>", "<eos>", "<user>", "<assistant>", "<sep>", "<unk>", "the", "a", "is", "in", "was", "it", "now", "before", "where", "moved", "from", "to", "went", "travelled", "did", "come", "can", "you", "tell", "me", "please", "and", "i", "do", "not", "know", "then", "actually", "hello", "hi", ".", "?", "ball", "cup", "key", "book", "kitchen", "garden", "office", "hall"]
</constants>

<triggers>
chat-arrival(event="A dialogue chat arrives.", source=interface.chat, process=process.answer-chat)
batch-arrival(
  event="A dialogue batch arrives.",
  source=interface.batch,
  process=process.answer-batch,
)
</triggers>

<processes>
<process id="predict" name="Predict dialogue" input="contracts.oak.md#schema.histories-texts" output="contracts.oak.md#schema.replies">
ACT TOOL "dialogue.prepare" input="contracts.oak.md#schema.histories-texts" output="contracts.oak.md#schema.tokens-mask": Apply the registered numerical operation to <HISTORIES>, <TEXTS>, <TOKENS>, <MASK>. (
  HISTORIES=$HISTORIES,
  TEXTS=$TEXTS,
) -> TOKENS, MASK
CALL encoder.oak.md#process.encode (TOKENS=$TOKENS) -> MEMORY, STATE, PREVIOUS, TAPE, EMBEDDING
CALL generation.oak.md#process.start (STATE=$STATE, PREVIOUS=$PREVIOUS, TAPE=$TAPE)
CALL generation.oak.md#process.next-word (MEMORY=$MEMORY, MASK=$MASK, EMBEDDING=$EMBEDDING)
CALL generation.oak.md#process.next-word (MEMORY=$MEMORY, MASK=$MASK, EMBEDDING=$EMBEDDING)
CALL generation.oak.md#process.next-word (MEMORY=$MEMORY, MASK=$MASK, EMBEDDING=$EMBEDDING)
CALL generation.oak.md#process.next-word (MEMORY=$MEMORY, MASK=$MASK, EMBEDDING=$EMBEDDING)
CALL generation.oak.md#process.next-word (MEMORY=$MEMORY, MASK=$MASK, EMBEDDING=$EMBEDDING)
CALL generation.oak.md#process.next-word (MEMORY=$MEMORY, MASK=$MASK, EMBEDDING=$EMBEDDING)
CALL generation.oak.md#process.next-word (MEMORY=$MEMORY, MASK=$MASK, EMBEDDING=$EMBEDDING)
CALL generation.oak.md#process.next-word (MEMORY=$MEMORY, MASK=$MASK, EMBEDDING=$EMBEDDING)
CALL generation.oak.md#process.next-word (MEMORY=$MEMORY, MASK=$MASK, EMBEDDING=$EMBEDDING)
CALL generation.oak.md#process.next-word (MEMORY=$MEMORY, MASK=$MASK, EMBEDDING=$EMBEDDING)
CALL generation.oak.md#process.next-word (MEMORY=$MEMORY, MASK=$MASK, EMBEDDING=$EMBEDDING)
CALL generation.oak.md#process.next-word (MEMORY=$MEMORY, MASK=$MASK, EMBEDDING=$EMBEDDING)
CALL generation.oak.md#process.next-word (MEMORY=$MEMORY, MASK=$MASK, EMBEDDING=$EMBEDDING)
CALL generation.oak.md#process.next-word (MEMORY=$MEMORY, MASK=$MASK, EMBEDDING=$EMBEDDING)
CALL generation.oak.md#process.finish () -> REPLIES
</process>

<process id="answer-chat" name="Answer chat" input="contracts.oak.md#schema.texts" output="contracts.oak.md#schema.replies">
CALL memory.oak.md#process.recall () -> HISTORIES
CALL process.predict (HISTORIES=$HISTORIES, TEXTS=$TEXTS) -> REPLIES
CALL memory.oak.md#process.commit (HISTORIES=$HISTORIES, TEXTS=$TEXTS, REPLIES=$REPLIES)
EMIT interface.reply
</process>

<process id="answer-batch" name="Answer batch" input="contracts.oak.md#schema.histories-texts" output="contracts.oak.md#schema.replies">
CALL process.predict (HISTORIES=$HISTORIES, TEXTS=$TEXTS) -> REPLIES
EMIT interface.reply
</process>
</processes>

<interfaces>
chat RECEIVES contracts.oak.md#schema.texts
batch RECEIVES contracts.oak.md#schema.histories-texts
reply EMITS contracts.oak.md#schema.replies
</interfaces>