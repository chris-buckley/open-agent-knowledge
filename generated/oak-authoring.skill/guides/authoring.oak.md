<instructions>
Constants hold values that do not change while the knowledge runs.
</instructions>

<constants>
guidance: YAML<<
- Treat the complete supplied host context as the source, regardless of modality.
- Omit every part and entry that the source does not justify.
- Do not invent state, triggers, processes, interfaces, tools, or relative paths.
- Use the shortest unambiguous names and reuse one exact domain noun across parts.
>>

part-authoring-priority: ["schemas", "constants", "state", "interfaces", "triggers", "processes", "instructions"]

skill-template: JSON<<
"---\nname: \"<SKILL_NAME>\"\ndescription: \"<SKILL_DESCRIPTION>\"\n---\n\n<INSTRUCTIONS_PART>\n<constants>\npurpose: <PURPOSE_JSON>\n\nlayout: TEXT<<\nSKILL_TREE:\n  SKILL.md→Skill entry point\n  references/→Supporting knowledge\n  assets/\n    constants/→Reusable fixed values\n    schemas/→Reusable information shapes\n  processes/→OAK workflows\n  guides/→Practical guidance\n  scripts/→Executable helpers\n>>\n\n<CONSTANT_ENTRIES>\n</constants>\n<SCHEMAS_PART>\n<STATE_PART>\n<TRIGGERS_PART>\n<PROCESSES_PART>\n<INTERFACES_PART>\n"
>>

template-use: "For new skills use _template/SKILL.md or verbatim skill-template. Quote metadata as YAML strings, PURPOSE_JSON as a JSON string. Replace PART lines with justified OAK sections plus a blank line, or delete them. Fill CONSTANT_ENTRIES or leave empty. Remove markers, unused parts/resources, and .gitkeep when adding content. Unfilled scaffolding is inert."
</constants>
