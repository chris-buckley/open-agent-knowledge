<instructions>
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
</instructions>

<schemas>
<schema id="api-coverage-table" name="API Coverage Table" purpose="Report API operation coverage against a specification, one row per operation.">
## <TABLE_NAME>
| Operation | URI | SpecRef | Gap |
| --- | --- | --- | --- |
| <OPERATION> | <ENDPOINT_PATH> | <SPEC_REF> | <GAP> |

WHERE:
- <TABLE_NAME> is string; is non-empty; the title for the API coverage table.
- <OPERATION> is string; is one of `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`; the HTTP method.
- <ENDPOINT_PATH> is string; matches `^/.*$`; the absolute path of the API endpoint.
- <SPEC_REF> is string; is non-empty; the reference in the form OpenAPI: target or Swagger: target.
- <GAP> is string; is one of `OK`, `MISSING_PATH`, `MISSING_METHOD`, `REQ_SCHEMA_MISMATCH`, `RESP_SCHEMA_MISMATCH`, `STATUS_CODE_MISSING`; the coverage gap analysis code.
</schema>
</schemas>