<instructions>
Each schema is one information shape: a template with <PLACEHOLDER> slots and WHERE lines that constrain each slot.
</instructions>

<schemas>
<schema id="verification" name="Verification" purpose="Identify the exact subject revision, performed check, observed result, and recorded evidence.">
Subject: <VERIFIED_SUBJECT>
Revision: <VERIFIED_REVISION>
Check: <CHECK>
Passed: <PASSED>
Evidence: <EVIDENCE>

WHERE:
- <VERIFIED_SUBJECT> is string; is non-empty; the subject actually inspected by the verifier.
- <VERIFIED_REVISION> is string; matches `^[0-9a-f]{64}$`; the SHA-256 digest of the immutable snapshot actually checked.
- <CHECK> is string; is non-empty; the versioned check definition actually performed.
- <PASSED> is boolean; the observed check result, not a confidence estimate.
- <EVIDENCE> is string; is non-empty; the host-recorded evidence location, whose existence the host must establish.
</schema>
</schemas>