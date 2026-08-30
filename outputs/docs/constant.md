~~~~instructions
Constants hold values that do not change while the knowledge runs.
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.

Constant: One value that stays the same during use.
Use the same columns in every CSV row.
Use only JSON scalar values in CSV cells.
Give each CSV constant one non-empty list of object rows.
Give each TEXT constant one string value.
~~~~

~~~~constants
example-1: "default-time-zone: \"Z\""

example-2: "repository-tree: TEXT<<\noak\n└── SKILL.md\n>>"

example-3: "api-config: JSON<<\n{\n  \"retries\": 3,\n  \"timeout_ms\": 2000\n}\n>>"

example-4: "service-table: CSV<<\nservice,enabled\nbilling,true\n>>"

example-5: "deployment-config: YAML<<\nregion: ap-southeast-2\nreplicas: 2\n>>"

grammar: TEXT<<
surface_constant_inline = ? <ID>: <VALUE> ? ;
surface_constant_text = ? <ID>: TEXT<<
<VALUE>
>> ? ;
surface_constant_json = ? <ID>: JSON<<
<VALUE>
>> ? ;
surface_constant_csv = ? <ID>: CSV<<
<VALUE>
>> ? ;
surface_constant_yaml = ? <ID>: YAML<<
<VALUE>
>> ? ;
>>
~~~~

~~~~schemas
~~~schema;id="constant-inline";name="Constant constant-inline";purpose="One value that stays the same during use."
<ID>: <VALUE>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The value that stays the same..
~~~

~~~schema;id="constant-text";name="Constant constant-text";purpose="One value that stays the same during use."
<ID>: TEXT<<
<VALUE>
>>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The value that stays the same..
~~~

~~~schema;id="constant-json";name="Constant constant-json";purpose="One value that stays the same during use."
<ID>: JSON<<
<VALUE>
>>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The value that stays the same..
~~~

~~~schema;id="constant-csv";name="Constant constant-csv";purpose="One value that stays the same during use."
<ID>: CSV<<
<VALUE>
>>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The value that stays the same..
~~~

~~~schema;id="constant-yaml";name="Constant constant-yaml";purpose="One value that stays the same during use."
<ID>: YAML<<
<VALUE>
>>

WHERE:
- <ID> is string; is non-empty; The entry id, unique in its OAK document..
- <VALUE> is string; is non-empty; The value that stays the same..
~~~
~~~~

~~~~state
~~~~

~~~~triggers
~~~~

~~~~processes
~~~~

~~~~interfaces
~~~~
