<instructions>
You MUST parse every input as JSON before schema evaluation.
You MUST reject a missing or non-Draft-2020-12 `$schema` declaration.
You MUST validate the schema against its meta-schema before validating the instance.
You MUST resolve references only from the explicit local registry.
You MUST state whether format is annotation-only or asserted.
You MUST report instance paths and schema paths for every validation failure.
You MUST run graph or business validation as a separate named gate.
You MUST return non-zero status for every failed gate.
</instructions>

<constants>
DEFAULT_FORMAT_POLICY: "annotation"
DIALECT: "https://json-schema.org/draft/2020-12/schema"
</constants>

<processes>
<process id="validate-contract" name="Validate schema and instance">
USE `shell` where: command="python scripts/validate_schema.py SCHEMA_PATH"
CAPTURE SCHEMA_RESULT from `shell`
USE `shell` where: command="python scripts/check_references.py SCHEMA_PATH --registry REGISTRY_PATH"
CAPTURE REFERENCE_RESULT from `shell`
USE `shell` where: command="python scripts/validate_instance.py SCHEMA_PATH INSTANCE_PATH --registry REGISTRY_PATH --format-policy FORMAT_POLICY"
CAPTURE INSTANCE_RESULT from `shell`
RETURN: SCHEMA_RESULT, REFERENCE_RESULT, INSTANCE_RESULT
</process>
</processes>

<input>
SCHEMA_PATH is the root Draft 2020-12 schema path.
INSTANCE_PATH is the JSON instance path.
REGISTRY_PATH is the explicit URI-to-local-path registry manifest.
FORMAT_POLICY is annotation or assert-known.
SEMANTIC_CHECKS names any separate graph or business validation commands.
</input>
