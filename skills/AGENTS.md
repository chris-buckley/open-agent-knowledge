<instructions>
$ reads a value; local targets start with their part; relative targets start with a document path; a bare $NAME is local to the running process; SET, CALL, EMIT, and trigger facts omit $.
Constants hold values that do not change while the knowledge runs.
Each process is the exact ordered way to do one task; follow its typed steps from top to bottom.
</instructions>

<constants>
owned-concern: "Portable skill products, authoring capability identity, declarative guide fusion, and consent-gated validator reuse."

capability-sources: CSV<<
source,owns
build/authoring_guides.py,guide composition and the authoring workflow
oak/rules/guidance.py,shared package authoring rules
examples/schemas/shape_gallery.py and examples/agents/shape_writer.py,"shape definitions, populated instances, and the working teaching pipeline"
skills/oak-authoring/scripts/validate.py,"optional runtime helper, skill version, immutable validator revision, and fingerprints"
build/authoring.py and build/fusion.py,"standard skill metadata, generated knowledge files, and agent assembly"
>>

delivery-contract: YAML<<
- Distribute skills/oak-authoring as a normal Git-versioned product directory with
  SKILL.md, numbered OAK references, teaching examples, and the optional script. Do
  not add provider-specific metadata or unused assets.
- Treat generated knowledge guides as the identical input documents for the skill
  and agent, not independently maintained prompts. Keep grammar material in EBNF.
- Keep the skill entry as the only operational scope. Supporting fusion documents
  may define constants and schemas only. Refuse authored policy, state, arrivals,
  processes, or interfaces in supporting documents instead of widening their scope.
- Namespace supporting definitions and rewrite typed targets after explicit resolution.
  Never rewrite literal payloads, templates, scripts, tool names, or embedded teaching
  documents.
- Check source and dependency fingerprints against the immutable validator revision
  before accepting a new version. A package version string alone is not proof of a
  matching validator.
- Leave runtime validation inactive unless requested, and require separate explicit
  approval before downloads or dependency installation. Preserve no-install authoring
  and honest not-performed results.
>>
</constants>

<processes>
<process id="change-capability" name="Change capability">
ACT Use <SOURCES> to change the owning source rather than editing generated skill documents. (SOURCES=$constant.capability-sources)
ACT Apply <CONTRACT> and the checks owned by build/AGENTS.md to both delivered forms and every validator outcome. (CONTRACT=$constant.delivery-contract)
</process>
</processes>