<instructions>
You MUST pin the Pydantic version before generation.
You MUST choose validation or serialization mode explicitly.
You MUST choose alias behavior explicitly.
You MUST add a project-owned absolute `$id` and the Draft 2020-12 `$schema` URI to every standalone output.
You MUST validate the generated schema before comparing or publishing it.
You MUST resolve every generated reference without network access.
You MUST compare the generated document with the committed artifact.
You MUST test representative valid and invalid instances in both Pydantic and JSON Schema.
You MUST record every intentional runtime and portable-schema difference.
</instructions>

<constants>
PYDANTIC_EXAMPLE: "examples/pydantic/model.py"
PYDANTIC_SCHEMA: "examples/pydantic/generated.schema.json"
REGISTRY: "examples/registry.json"
</constants>

<processes>
<process id="generate-schema" name="Generate schema from Pydantic">
USE `shell` where: command="python examples/pydantic/model.py generate examples/pydantic/generated.schema.json --mode validation"
CAPTURE GENERATION_RESULT from `shell`
USE `shell` where: command="python scripts/validate_schema.py examples/pydantic/generated.schema.json"
CAPTURE SCHEMA_RESULT from `shell`
USE `shell` where: command="python scripts/check_references.py examples/pydantic/generated.schema.json"
CAPTURE REFERENCE_RESULT from `shell`
USE `shell` where: command="python scripts/validate_instance.py examples/pydantic/generated.schema.json examples/extension/retail-lending.valid.json"
CAPTURE PORTABLE_RESULT from `shell`
USE `shell` where: command="python examples/pydantic/model.py validate examples/extension/retail-lending.valid.json"
CAPTURE PYDANTIC_RESULT from `shell`
RETURN: GENERATION_RESULT, SCHEMA_RESULT, REFERENCE_RESULT, PORTABLE_RESULT, PYDANTIC_RESULT
</process>
</processes>

<input>
MODEL_PATH is the Pydantic model source to inspect.
OUTPUT_PATH is the standalone JSON Schema output path.
SCHEMA_MODE is validation or serialization.
BY_ALIAS states whether external aliases appear in the schema.
PYDANTIC_VERSION is the pinned Pydantic v2 version.
</input>
