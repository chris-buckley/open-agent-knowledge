<instructions>
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

A ... line in a template marks repetition of the pattern above it.
</instructions>

<schemas>
<schema id="ideation-list" name="Ideation List" purpose="Generate structured brainstorming ideas for a given task, one block per idea separated by a rule.">
## <TASK_TITLE>

Ideas: <IDEA_COUNT>

[<IDEA_NUMBER>] <IDEA_TITLE>
Summary: <IDEA_SUMMARY>
Details: <IDEA_DETAILS>

---

...

WHERE:
- <TASK_TITLE> is string; is non-empty; the task or topic for ideation.
- <IDEA_COUNT> is integer; is at least 1; the total number of ideas, the list holds exactly this many.
- <IDEA_NUMBER> is integer; is at least 1; is at most <IDEA_COUNT>; the sequential idea number.
- <IDEA_TITLE> is string; is non-empty; one short present-tense active-voice title.
- <IDEA_SUMMARY> is string; is one line; one present-tense active-voice sentence.
- <IDEA_DETAILS> is string; is non-empty; two to four conceptual sentences without implementation, code, or pseudo-code.
</schema>
</schemas>