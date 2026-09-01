<instructions>
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

A ... line in a template marks repetition of the pattern above it.
</instructions>

<schemas>
<schema id="code-changes" name="Code Changes" purpose="Display updated and new files with complete code, one block per file separated by a rule.">
## <CHANGE_TITLE>

<CHANGE_DESCRIPTION>
File: <FILE_PATH>
```<LANG>
<COMPLETE_CODE>
```

---

...

WHERE:
- <CHANGE_TITLE> is string; is non-empty; the title for the set of changes.
- <CHANGE_DESCRIPTION> is string; is non-empty; one terse present-voice description of the change, never changelog style.
- <FILE_PATH> is path; matches `^[A-Za-z0-9._\-][A-Za-z0-9._/\-]*$`; the repository-relative file path without parent traversal.
- <LANG> is string; is non-empty; one code language name for GitHub-flavored Markdown.
- <COMPLETE_CODE> is string; is non-empty; the complete file contents with terse present-voice comments.
</schema>
</schemas>