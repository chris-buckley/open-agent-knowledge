<instructions>
This document owns the generated-only status and regeneration rules for repository outputs.
Treat every file in this directory as generated reference rather than source authority.
Do not edit a generated output by hand.
Use `authoring.md` as the generated single-shot OAK authoring prompt.
Use `oak.ebnf` as the generated grammar reference.
Use `docs` as the generated model and surface reference.
Regenerate each output through its owning script in `build`.
Change the owning package or build source instead of patching its output.
</instructions>