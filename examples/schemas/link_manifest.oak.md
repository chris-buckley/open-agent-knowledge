<instructions>
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

A ... line in a template marks repetition of the pattern above it.
</instructions>

<schemas>
<schema id="link-manifest" name="Link Manifest" purpose="List documentation links with descriptions for quick navigation, one entry per link.">
# <MANIFEST_TITLE>

- [<LINK_TITLE>](<LINK_URL>): <LINK_DESCRIPTION>
...

WHERE:
- <MANIFEST_TITLE> is string; is non-empty; the title of the manifest or documentation set.
- <LINK_TITLE> is string; is non-empty; the display title for the link.
- <LINK_URL> is uri; the URL to the resource.
- <LINK_DESCRIPTION> is string; is one line; one sentence describing the linked resource.
</schema>
</schemas>