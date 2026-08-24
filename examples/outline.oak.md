<instructions>
Use the outline schema for every outline.
</instructions>

<constants>
DEFAULT_TZ: "Z"
</constants>

<schemas>
<schema id="oak:schema/outline-request" name="Outline Request" purpose="Describe the topic to outline.">
<TOPIC>

WHERE:
- <TOPIC> is string; is non-empty; topic to outline.
</schema>
<schema id="oak:schema/outline" name="Hierarchical Outline" purpose="Generate a semantic multilevel numbered outline, one space of indentation per level.">
## <OUTLINE_TITLE>

<LEVEL_1_NUMBER> <STATEMENT>
 <LEVEL_2_NUMBER> <STATEMENT>
  <LEVEL_3_NUMBER> <STATEMENT>
…

WHERE:
- <OUTLINE_TITLE> is string; is at most 80 characters; title for the outline.
- <LEVEL_1_NUMBER> matches `^[0-9]+$` (e.g. `1`, `2`).
- <LEVEL_2_NUMBER> matches `^[0-9]+[.][0-9]+$` (e.g. `1.1`, `1.2`).
- <LEVEL_3_NUMBER> matches `^[0-9]+[.][0-9]+[.][0-9]+$` (e.g. `1.1.1`); maximum depth.
- <STATEMENT> is one line; one atomic topic, instruction, or information, no obvious statements.
</schema>
</schemas>

<state>
STATUS: "ready"
</state>

<triggers>
- The interpreter arrives to write an outline. -> oak:process/write
</triggers>

<processes>
<process id="oak:process/write" name="Write an outline">
consumes: oak:interface/request
emits: oak:interface/outline
1. Collect the topic.
2. Emit the outline schema.
</process>
</processes>

<interfaces>
<interface id="oak:interface/request" direction="in" schema="oak:schema/outline-request">
The topic supplied to the outline process.
</interface>
<interface id="oak:interface/outline" direction="out" schema="oak:schema/outline">
The outline returned by the outline process.
</interface>
</interfaces>
