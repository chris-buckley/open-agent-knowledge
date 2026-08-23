<schema id="oak:schema/outline" name="Hierarchical Outline" purpose="Generate a semantic multilevel numbered outline, one space of indentation per level.">
## <OUTLINE_TITLE>

<LEVEL_1_NUMBER> <STATEMENT>
 <LEVEL_2_NUMBER> <STATEMENT>
  <LEVEL_3_NUMBER> <STATEMENT>
...

WHERE:
- <OUTLINE_TITLE> is string; is at most 80 characters; title for the outline.
- <LEVEL_1_NUMBER> matches `^[0-9]+$` (e.g. `1`, `2`).
- <LEVEL_2_NUMBER> matches `^[0-9]+[.][0-9]+$` (e.g. `1.1`, `1.2`).
- <LEVEL_3_NUMBER> matches `^[0-9]+[.][0-9]+[.][0-9]+$` (e.g. `1.1.1`); maximum depth.
- <STATEMENT> is one line; one atomic topic, instruction, or information, no obvious statements.
</schema>
