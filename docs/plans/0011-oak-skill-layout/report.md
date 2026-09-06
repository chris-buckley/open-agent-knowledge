# OAK authoring skill layout completion report

Completed: 2026-09-06
Classification: INTERNAL
Verdict: Approved against the accepted plan
Plan: [0011 OAK skill layout](plan.md)
Implementation commit: `13e134d1290a6c14d320d1d576de2f5602b87f75`
Verified implementation tree: `713ba2ecdaf2a567ffcc380844bdc52e81f3544e`

## Outcome

All ten execution tasks are complete. The generated skill now separates language references, practical guides, teaching assets, and a generic template. The skill and standalone agent share the same knowledge and retain one authoring operational scope. No OAK language or runtime change was needed.

Skill version is `2.3.0`. The validator remains pinned to revision `2b542c613c5d1a7e64b597884fae4f444ac34916`, source fingerprint `e9c301a254ec8897698816091bac99cc117d8e0fa052192e728d356d19c27bd1`, and dependency fingerprint `2412c436c0ffaa05c604da2d58be4b72c443b37efcaa094380845fd0fe3a3702`. Only the helper's skill-version constant changed; its runtime implementation did not.

## Observed state comparisons

| Comparison | Observed result | Evidence |
| --- | --- | --- |
| E01: Complete directory layout | Passed. The delivered package contains exactly 29 files, including six empty `.gitkeep` files. Directory relationships match the accepted specimen. The old review, validation, grammar, and teaching delivery paths are absent. | `_layout_inventory` uses an independent exact file and directory set. Negative cases reject missing files, extra files, and unexpected empty directories. All eight teaching documents match their owners; each scenario closes within its copied bundle. |
| E02: Generic OAK skill skeleton | Passed. `_template/SKILL.md` contains only generic metadata markers, a purpose marker, a literal layout constant, and optional OAK-part markers. Its support folders contain only empty `.gitkeep` files. | `_template_delivery` populates the actual scaffold into a temporary `SKILL.md`, strips metadata, parses and resolves one document, and runs the optional validator with successful parse/resolve results. XML and Markdown round trips preserve the node. The fixture is not shipped. |
| E03: Compact layout notation | Passed. The populated `layout` TEXT constant exactly matches the accepted `SKILL_TREE:` block, including U+2192 arrows, supplied descriptions, and two-space indentation. Displayed paths do not become imports. | The independent `EXPECTED_SKILL_TREE` specimen is compared with the actual template and parsed constant. Mutated arrows, indentation, labels, metadata, and markers are rejected. Resolution remains a single document. |

The unfilled template is rejected as active fusion input. The exact 516-byte template text is preserved as inert JSON knowledge in `guides/authoring.oak.md` and the standalone agent. The twelve-document authoring graph contains only the entry and its eleven support documents, not the template or teaching scenarios. The assembled node retains four processes, two outside triggers, two interfaces, no state, and no authored instruction policy.

## Task evidence

| Task | Completion evidence |
| --- | --- |
| P01.01 | `skills/AGENTS.md` records the new directory responsibilities, intentional empty template folders, and inert-template boundary. Canonical AGENTS checks pass. |
| P01.02 | `build/authoring_guides.py` assigns every package authoring rule to exactly one support document. Language knowledge and grammar live under references; authoring, review, and validation practice live under guides. |
| P01.03 | `examples/catalog.py` exports the complete core to `assets/examples`. Guide bindings, bounded-copy checks, and execution fixtures use the new locations. Scenario document contents are unchanged. |
| P02.01 | Existing build owners generate `_template/SKILL.md` and the six empty `.gitkeep` files. No separate authoring system, README index, or completed domain skill was introduced. |
| P02.02 | Repeated explanatory wording and duplicate state/instruction guidance were removed or shortened. Every shared package rule, complete teaching document, grammar, validator policy, and validator script remains available. The template stays literal during fusion. |
| P02.03 | The entry supplies the template and its use guidance while establishing scope, only calling for scaffolding when a new skill is requested. Version metadata agrees across the skill, guide identity, and embedded helper. Consent behavior and runtime fingerprints remain unchanged. |
| P03.01 | Authoring checks now cover exact inventory, generic markers, populated-template parsing, literal notation, rejected mutations, and template values in skill-agent execution traces. |
| P03.02 | Cleanup handles references, guides, assets, and template paths. Tests remove stale files in every owned root and preserve the helper and runtime cache. A current-source search found no replaced delivery references; historical plan specimens remain intact. |
| P03.03 | All generators ran; Python compiled; both complete verification entry points passed locally on Python 3.13.5 and in GitHub on Python 3.11. |
| P03.04 | All four generators were repeated without byte changes. The final source and product diff was inspected, exact tree identity was verified, and this report records the observed outcome. |

## Verification

The repository's 33 registered verification checks passed through both `python -m build.examples` and `python build/examples.py`. This includes detached examples, document closure, canonical representations, fusion rejections, typed and natural arrivals, validator identity and consent, output freshness, and scoped repository rules.

The following commands completed successfully:

```text
python -m compileall -q oak build examples skills/oak-authoring/scripts
python -m examples.catalog
python -m build.ebnf
python -m build.docs
python -m build.authoring
python -m build.examples
python build/examples.py
```

Repeated generation covered all four generators, not just the authoring output. A whole-working-tree hash comparison was unchanged locally. In GitHub, regeneration left no working diff or untracked files and matched the expected complete Git tree before publication.

GitHub evidence: [Python 3.11 verification and exact-tree publication](https://github.com/chris-buckley/open-agent-knowledge/actions/runs/34009771664). Every job step completed successfully. The published commit's tree equals the locally tested tree shown above.

| Product | Before | After | Limit |
| --- | ---: | ---: | ---: |
| `skills/oak-authoring/SKILL.md` | 8,299 bytes | 8,022 bytes | 10,000 bytes |
| `outputs/oak-authoring.oak.md` | 63,943 bytes | 63,982 bytes | 64,000 bytes |

The agent has 18 bytes of remaining budget; the limit was not raised.

SHA-256 of the delivered products:

```text
82f3b3c6d8de6f254f7b468ad9862b51185be43bea521a7ffa950361c796da74  skills/oak-authoring/SKILL.md
6c5e706344aef4c649256cf57a6842761a7aa3491b4efe5a190fa2e681169c17  skills/oak-authoring/_template/SKILL.md
11f3a2a8a1edb70cf8bed6669c3a89a2556fbc3b02bf97305e4da89f186b3945  outputs/oak-authoring.oak.md
```

## Changed paths

Source owners and checks: `build/authoring.py`, `build/authoring_guides.py`, `build/checks/authoring.py`, `build/fusion.py` (ordering comment only), `examples/catalog.py`, `skills/AGENTS.md`, and `skills/oak-authoring/scripts/validate.py` (skill version only).

Generated products: the skill entry, reorganised references and guides, all teaching assets at their new locations, generic template and empty-folder markers, and `outputs/oak-authoring.oak.md`. The old delivery paths were removed rather than aliased.

Completion records: this report and the matching checked-off plan. The closing documentation commit changes no implementation or product bytes.

## Environment and scope notes

The supplied starting commit was `80f2712feff87d06f25ac7a170b647f5abafe7b2`. An archive produced from that exact commit was checksum-verified and its reconstructed Git tree matched `f7b963f7c0de1028c296de2abde998452eb6f684`. Earlier SMEAC and repository naming/history work on the requested branch was retained.

The plan's Windows `.venv` was not available in this execution environment. Local checks used Python 3.13.5, and GitHub supplied the required Python 3.11 verification against the identical candidate. Only the repository's declared dependencies were installed in the hosted runner; the optional user-facing validator's installation consent behavior was not changed.

A temporary branch-only workflow supplied the pinned archive and published the verified candidate. It was removed before the implementation commit and does not appear in the final product diff. Existing commits were preserved; there was no rebase, squash, force push, or merge into main.

These checks establish structure, resolution, deterministic generation, and parity under the repository's native-host fixtures. They do not claim arbitrary model-quality guarantees or that an authored host action has executed outside those fixtures.

## Final verdict

Approved against E01, E02, E03, all ten plan tasks, and the complete repository verification. No unresolved implementation findings remain. The implementation is ready for pull-request review.
