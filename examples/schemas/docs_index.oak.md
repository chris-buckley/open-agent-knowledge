<instructions>
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

A ... line in a template marks repetition of the pattern above it.
</instructions>

<schemas>
<schema id="docs-index" name="Documentation Index" purpose="Map documentation hierarchically for navigation: groups contain pages, pages contain headings.">
# <PROJECT_TITLE> Documentation Map

> Fetch the complete documentation index at: <INDEX_URL>
> Last updated: <TIMESTAMP>

## <GROUP_NAME>

### [<PAGE_TITLE>](<PAGE_URL>)
* <HEADING_TEXT>
  * <SUBHEADING_TEXT>

...

WHERE:
- <PROJECT_TITLE> is string; is non-empty; the name of the project or documentation set.
- <INDEX_URL> is uri; the URL where this index can be fetched.
- <TIMESTAMP> is datetime; when the index was generated.
- <GROUP_NAME> is string; is non-empty; the documentation section name.
- <PAGE_TITLE> is string; is non-empty; the title of the documentation page.
- <PAGE_URL> is uri; the link to the documentation page.
- <HEADING_TEXT> is string; is non-empty; one heading from the page.
- <SUBHEADING_TEXT> is string; is non-empty; one nested heading under its parent.
</schema>
</schemas>