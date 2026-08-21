<instructions>
You MUST classify the change as compatible, conditionally compatible, or breaking under the project's declared policy.
You MUST compare schema resources by canonical identity as well as file path.
You MUST review assertions, applicators, annotations, references, and vocabulary declarations separately.
You MUST test all existing valid and invalid fixtures.
You MUST test every domain adaptor against its parent contract.
You MUST inspect generated Pydantic schema differences separately from hand-authored differences.
You MUST reject hidden network retrieval and hidden draft fallback.
You MUST record semantic rules that remain outside JSON Schema.
</instructions>

<processes>
<process id="review-change" name="Review schema change">
USE `shell` where: command="python -m unittest discover -s tests -v"
CAPTURE TEST_RESULT from `shell`
USE `shell` where: command="python scripts/check_references.py CHANGED_SCHEMA --registry REGISTRY_PATH --json"
CAPTURE REFERENCE_RESULT from `shell`
SET COMPATIBILITY := "conditionally-compatible" (from "Agent Inference" using OLD_SCHEMA, NEW_SCHEMA, PROJECT_POLICY, TEST_RESULT, REFERENCE_RESULT)
SET BREAKING_REASONS := "" (from "Agent Inference" using OLD_SCHEMA, NEW_SCHEMA, PROJECT_POLICY)
SET SEMANTIC_LIMITS := "" (from "Agent Inference" using NEW_SCHEMA, APPLICATION_RULES)
RETURN: COMPATIBILITY, BREAKING_REASONS, SEMANTIC_LIMITS, TEST_RESULT, REFERENCE_RESULT
</process>
</processes>

<input>
OLD_SCHEMA is the prior released schema document or resource set.
NEW_SCHEMA is the proposed schema document or resource set.
CHANGED_SCHEMA is the root schema path for executable checks.
REGISTRY_PATH is the local schema registry manifest.
PROJECT_POLICY defines compatibility and versioning rules.
APPLICATION_RULES lists graph-wide and business constraints outside JSON Schema.
</input>
