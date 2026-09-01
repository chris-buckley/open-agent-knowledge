<instructions>
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

A ... line in a template marks repetition of the pattern above it.
</instructions>

<schemas>
<schema id="hierarchical-outline" name="Hierarchical Outline" purpose="Generate a semantic numbered outline of at most three levels, one space of indentation per level.">
## <OUTLINE_TITLE>

<LEVEL_1_NUMBER> <STATEMENT>
 <LEVEL_2_NUMBER> <STATEMENT>
  <LEVEL_3_NUMBER> <STATEMENT>

...

WHERE:
- <OUTLINE_TITLE> is string; is non-empty; the title for the outline.
- <LEVEL_1_NUMBER> is string; matches `^[0-9]+$`; the level one number.
- <LEVEL_2_NUMBER> is string; matches `^[0-9]+\.[0-9]+$`; the level two number.
- <LEVEL_3_NUMBER> is string; matches `^[0-9]+\.[0-9]+\.[0-9]+$` (e.g. `1.1.1`, `1.1.2`); the level three number at the maximum depth.
- <STATEMENT> is string; is non-empty; one atomic statement without obvious content.
</schema>
</schemas>