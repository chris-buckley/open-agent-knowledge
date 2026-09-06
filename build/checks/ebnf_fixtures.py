"""Fixed expectations reviewed against the pre-layout grammar and accepted plan."""

# These fingerprints are observations from 7e002d5, not regenerated expectations.
SOURCE_FINGERPRINT = "1ee033c0dd4aa0785c3032b31139d24ea1e970133ac7248fe2ab95311adf97d0"
GROUPING_FINGERPRINTS = {
    ("xml", "markdown"): "95cd111380f3b76686d4e9737e318891e0c07f4cf86e05dabde285aa6e97680f",
    ("xml",): "b0839de6fbeed43c5ea4d7e017dd549b212367df9adc854795c865aea513ba69",
    ("markdown",): "ceb59ffc62ef5fc628e043f696a170ace84ec6f221863d56e72c99e61e718c99",
    ("markdown", "xml"): "7d32c9e3c3faecb803197f991fc4b1d7e88947d27856ee8d23a0dd3a388560e5",
}

HEADINGS = (
    "Scope and notation",
    "01. Lexical tokens and whitespace",
    "02. Values, targets and bindings",
    "03. Conditions",
    "04. Part contents",
    "Instructions", "Constants", "Schemas", "State", "Triggers", "Processes", "Interfaces",
    "05. XML and Markdown grouping",
    "06. Complete document",
)

# Literal and opaque productions alone may exceed the reference's soft width.
WIDTH_EXCEPTIONS = frozenset((
    "logical_nl", "process_name", "regex_pattern", "relative_document_path",
    "surface_act_native", "surface_act_tool",
))

VALUE_SPECIMEN = '''process_value   = json_value | "$", value_target ;
value_target    = constant_target | local_state_target | placeholder ;

value_binding   = placeholder, "=", process_value ;
binding_list    = "(", [ value_binding, { ",", value_binding }, [ "," ] ], ")" ;
output_bindings = "->", placeholder, { ",", placeholder } ;'''

TRIGGER_SPECIMEN = '''trigger_declaration =
    slug_id, "(",
    trigger_field, { ",", trigger_field }, [ "," ],
    ")", logical_nl ;

trigger_field =
      "event",   "=", json_string
    | "source",  "=", local_interface_target
    | "guard",   "=", condition
    | "process", "=", process_target
    | "seed",    "=", binding_list ;'''

STATEMENT_SPECIMEN = '''process_statement =
      if_statement
    | while_statement
    | assert_statement
    | call_statement
    | emit_statement
    | set_statement
    | fail_statement
    | surface_act_native
    | surface_act_tool
    | surface_statement_foreach
    | surface_statement_par
    | surface_statement_join ;'''

FOREACH_SPECIMEN = '''surface_statement_foreach = ? FOREACH <BINDING> IN <VALUE>:
  <BODY> ? ;'''

DUPLICATE_SPECIMENS = (
    'constant_target = [ relative_document_path, "#" ], "constant.", slug_id ;',
    'constant_target = [ relative_document_path, "#" ], "constant", ".", slug_id ;',
)
