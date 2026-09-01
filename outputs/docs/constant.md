<instructions>
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Constant: One value that stays the same during use.
Use the same columns in every CSV row.
Give a schema binding both a schema target and a placeholder.
Use only JSON scalar values in CSV cells.
Give each CSV constant one non-empty list of object rows.
Make every schema-bound value satisfy its placeholder constraints.
Give each TEXT constant one string value.
Bind a placeholder present in the selected schema.
Do not bind a placeholder that has a placeholder-valued bound.
</instructions>

<constants>
example-1: "default-time-zone: \"Z\""

example-2: "repository-tree: TEXT<<\noak\n└── SKILL.md\n>>"

example-3: "api-config: JSON<<\n{\n  \"retries\": 3,\n  \"timeout_ms\": 2000\n}\n>>"

example-4: "service-table: CSV<<\nservice,enabled\nbilling,true\n>>"

example-5: "deployment-config: YAML<<\nregion: ap-southeast-2\nreplicas: 2\n>>"

grammar: TEXT<<
surface_constant_inline = ? <ID> AS <SCHEMA_ID>.<PLACEHOLDER>: <VALUE> ? ;
surface_constant_text = ? <ID> AS <SCHEMA_ID>.<PLACEHOLDER>: TEXT<<
<VALUE>
>> ? ;
surface_constant_json = ? <ID> AS <SCHEMA_ID>.<PLACEHOLDER>: JSON<<
<VALUE>
>> ? ;
surface_constant_csv = ? <ID> AS <SCHEMA_ID>.<PLACEHOLDER>: CSV<<
<VALUE>
>> ? ;
surface_constant_yaml = ? <ID> AS <SCHEMA_ID>.<PLACEHOLDER>: YAML<<
<VALUE>
>> ? ;
>>
</constants>

<schemas>
<schema id="constant-inline" name="Constant constant-inline" purpose="One value that stays the same during use.">
<ID> AS <SCHEMA_ID>.<PLACEHOLDER>: <VALUE>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <SCHEMA_ID> is string; The optional local or relative schema target whose placeholder constrains the value..
- <PLACEHOLDER> is string; The schema placeholder the value must satisfy..
- <VALUE> is string; is non-empty; The value that stays the same..
</schema>

<schema id="constant-text" name="Constant constant-text" purpose="One value that stays the same during use.">
<ID> AS <SCHEMA_ID>.<PLACEHOLDER>: TEXT<<
<VALUE>
>>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <SCHEMA_ID> is string; The optional local or relative schema target whose placeholder constrains the value..
- <PLACEHOLDER> is string; The schema placeholder the value must satisfy..
- <VALUE> is string; is non-empty; The value that stays the same..
</schema>

<schema id="constant-json" name="Constant constant-json" purpose="One value that stays the same during use.">
<ID> AS <SCHEMA_ID>.<PLACEHOLDER>: JSON<<
<VALUE>
>>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <SCHEMA_ID> is string; The optional local or relative schema target whose placeholder constrains the value..
- <PLACEHOLDER> is string; The schema placeholder the value must satisfy..
- <VALUE> is string; is non-empty; The value that stays the same..
</schema>

<schema id="constant-csv" name="Constant constant-csv" purpose="One value that stays the same during use.">
<ID> AS <SCHEMA_ID>.<PLACEHOLDER>: CSV<<
<VALUE>
>>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <SCHEMA_ID> is string; The optional local or relative schema target whose placeholder constrains the value..
- <PLACEHOLDER> is string; The schema placeholder the value must satisfy..
- <VALUE> is string; is non-empty; The value that stays the same..
</schema>

<schema id="constant-yaml" name="Constant constant-yaml" purpose="One value that stays the same during use.">
<ID> AS <SCHEMA_ID>.<PLACEHOLDER>: YAML<<
<VALUE>
>>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <SCHEMA_ID> is string; The optional local or relative schema target whose placeholder constrains the value..
- <PLACEHOLDER> is string; The schema placeholder the value must satisfy..
- <VALUE> is string; is non-empty; The value that stays the same..
</schema>
</schemas>
