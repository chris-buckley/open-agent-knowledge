<instructions>
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

A ... line in a template marks repetition of the pattern above it.
</instructions>

<schemas>
<schema id="code-map" name="Code Map" purpose="Display relevant code snippets with links to their source lines.">
<AREA_TITLE>
> [<SHORT_DESC>](<REPO_NAME>/<REL_PATH>#L<LINE_FROM>-L<LINE_TO>)
```<LANG>
<SNIPPET>
```

...

WHERE:
- <AREA_TITLE> is string; is non-empty; the title of the area being described.
- <SHORT_DESC> is string; is non-empty; one short description of the code snippet.
- <REPO_NAME> is string; matches `^[A-Za-z0-9._\-]+$`; one path segment naming the repository.
- <REL_PATH> is path; matches `^[A-Za-z0-9._\-][A-Za-z0-9._/\-]*$`; the repository-relative file path without parent traversal.
- <LINE_FROM> is integer; is at least 1; the first snippet line number.
- <LINE_TO> is integer; is at least <LINE_FROM>; the last snippet line number.
- <LANG> is string; is non-empty; one code language name for GitHub-flavored Markdown.
- <SNIPPET> is string; is non-empty; the code lines from LINE_FROM to LINE_TO, each prefixed with its source line number.
</schema>
</schemas>