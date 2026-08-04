# 38 — Phase 6 Knowledge-Ingestion Intelligence Completion

## Status

**Chat-first Phase 6: complete and independently CI-validated.**

Date: 2026-08-05

This release completes the knowledge-ingestion intelligence that can be defined, inspected and tested without operating a production document pipeline. It profiles the Founder-supplied source library, governs identifiers and aliases, indexes source-derived method headings, defines rights and quarantine decisions, supplies retrieval gold cases and creates original offdata method-record examples without committing or redistributing the original source files.

Phase 6 does **not** claim that the source files have been physically imported, stored, parsed into passages or made searchable in a production retrieval service.

## 1. Governed source scope

The release profiles exactly 23 Founder-supplied sources:

- eleven core Markdown consulting standards;
- twelve domain DOCX methodology packs.

Every source profile records:

- stable repository source ID;
- original and preferred repository filename;
- declared title, file identifier, version and status where present;
- source format and role or domain;
- actual SHA-256 checksum calculated from the supplied file;
- byte size and structural counts;
- provenance classification;
- conservative rights status;
- external-redistribution prohibition;
- review cadence;
- explicit import state `profiled_original_not_committed`.

The original files remain unchanged and uncommitted. The profiles are metadata and intelligence records, not substitutes for the source documents.

## 2. Canonical manifest and alias resolution

`knowledge/source-manifest.yaml` is the canonical profiled source register. `knowledge/alias-map.yaml` contains 99 deterministic alias rules covering original names, preferred names, declared identifiers, historical names and controlled shorthand.

The resolver returns one of four governed states:

- `resolved` — exactly one authorised source target;
- `ambiguous` — multiple plausible targets and mandatory quarantine;
- `unresolved` — no authorised target and a controlled dependency gap;
- `invalid` — malformed or prohibited reference.

Ambiguous references are never resolved by model preference. In particular, generic references to “Implementation and Change” can refer to the core implementation standard or the domain methodology pack and therefore quarantine unless the reference supplies sufficient context.

Twenty-one dependency-resolution cases verify exact matches, aliases, declared IDs, ambiguity, missing dependencies and invalid references.

## 3. Domain method-heading index

The twelve DOCX packs contain 154 profiled method headings:

| Domain | Method headings |
|---|---:|
| Benefits realisation and performance improvement | 14 |
| Corporate and business-unit strategy | 14 |
| Cost and productivity | 16 |
| Customer experience | 14 |
| Digital and AI transformation | 13 |
| Growth and commercial strategy | 14 |
| IPO, valuation and capital strategy | 11 |
| Implementation and change | 12 |
| M&A, carve-out and integration | 13 |
| Operating-model transformation | 9 |
| Organisation and workforce | 12 |
| Risk and controls | 12 |
| **Total** | **154** |

The headings are classified as `indexed_not_promoted`. They may support source inspection, retrieval testing and candidate reconstruction, but they are not automatically canonical methods.

## 4. Original method-record reconstructions

The release provides twelve source-grounded, independently written method-record examples—one per domain. Each example uses the canonical `MethodRecord` contract and includes:

- purpose and decision use;
- applicability and prerequisites;
- required inputs;
- deterministic or governed procedure;
- outputs;
- limitations and failure modes;
- adjacent-method links;
- evidence and review expectations;
- source-local method reference;
- explicit reconstruction note.

The examples do not copy protected diagrams, templates or extended source wording. They demonstrate the transformation standard that the later ingestion workflow must follow.

## 5. Collision and dependency intelligence

Twelve method-collision families identify similar labels or overlapping concepts across the source library. A collision does not authorise merging. Resolution requires comparison of purpose, decision use, prerequisites, procedure, outputs, limitations and provenance.

The release also preserves controlled unresolved dependencies. Missing or ambiguous cross-references remain visible and quarantined rather than being invented or silently redirected.

## 6. Domain overlays

Twelve answer-neutral domain overlays define the minimum context needed to adapt the shared consulting kernel. Overlays can specify:

- domain vocabulary;
- typical decisions and stakeholders;
- evidence patterns;
- regulatory or specialist-review considerations;
- method families and dependencies;
- common traps.

They cannot prescribe the answer, suppress contrary evidence, weaken Founder authority or bypass method-selection requirements.

## 7. Retrieval evaluation

The release contains 46 source-grounded retrieval gold cases—two for each profiled source. Cases define:

- query intent;
- expected source ID;
- expected topic or heading signal;
- prohibited source substitutions;
- required ambiguity behaviour;
- rights and confidentiality constraints.

These cases are ready for later lexical, semantic and hybrid retrieval evaluation. They do not claim that a retrieval engine currently exists.

## 8. Rights and source-use controls

The default rights posture is conservative:

- internal profiling and controlled retrieval evaluation may proceed from Founder-supplied materials;
- external redistribution is denied by default;
- uncertain rights require Founder confirmation;
- original files and extracted passages must preserve provenance;
- protected wording, diagrams and templates cannot be copied into offdata canonical methods;
- client content is prohibited from the methodology library;
- a source cannot grant itself broader usage rights.

`UT-RIGHTS-001` now provides executable evidence for this policy.

## 9. Methodology Radar source taxonomy

Ten discovery categories define the initial Methodology Radar source taxonomy. Each category includes source type, authority expectations, novelty tests, provenance requirements, copyright and trademark cautions, review cadence and promotion controls.

Discovery creates candidates only. No candidate may automatically become canonical, supersede an existing method or grant itself source authority.

## 10. Reproducible baseline

`knowledge/knowledge-ingestion-baseline.json` is generated deterministically from the governed YAML sources. It contains stable counts, profiles, method headings, retrieval cases, configuration identity and a SHA-256 intelligence digest.

The permanent CI gate regenerates the baseline and fails on byte drift. Mutation tests cover:

- changed source checksums or structural metadata;
- duplicate source IDs;
- ambiguous aliases;
- missing dependencies;
- illegal automatic promotion;
- external redistribution;
- invalid method ranges and references;
- stale generated baselines;
- missing overlay, collision, retrieval or taxonomy coverage.

## 11. Requirement and test traceability

Phase 6 adds twenty mapped executable test nodes and converts three planned tests into executable evidence:

- `UT-ALIAS-001`;
- `UT-OVERLAY-001`;
- `UT-RIGHTS-001`.

The combined registry now records:

- 178 implemented test nodes;
- 54 remaining planned tests;
- 18 completed planned-test IDs;
- all 123 catalogue requirements mapped to implemented or planned evidence.

`IT-INGEST-001` remains planned because physical source import, persistence and production extraction have not yet been executed.

## 12. Independent validation evidence

GitHub Actions run `30959590530`, job `92160335027`, validated branch head `adbb1566b8b8074be6c429075c593f1376bae4db` and pull-request merge reference `2222d2138806fc7177830fed0f5894b7dbd0f548` on Ubuntu 24.04 and Python 3.11.15.

### Phase 6 validator

```text
PHASE 6 KNOWLEDGE-INGESTION INTELLIGENCE VALIDATION PASSED
- source_profiles=23
- core_markdown_sources=11
- domain_docx_sources=12
- method_headings=154
- aliases=99
- dependency_cases=21
- collision_families=12
- method_record_examples=12
- retrieval_cases=46
- radar_categories=10
- completed_planned_tests=3
- physical_import_boundary=preserved
- automatic_method_promotion=blocked
```

### Complete Phase 1–6 quality gate

- Phase 1 contract validator: passed;
- Phase 2 agent-system validator: passed;
- Phase 3 analytical-oracle validator: passed;
- Phase 4 deliverable-semantic validator: passed;
- Phase 5 additional-fixture validator: passed;
- Phase 6 knowledge-ingestion-intelligence validator: passed;
- read-only clean generation of all governed Phase 1–6 records: passed;
- runtime tests: 180 passed;
- total coverage: 93.40 percent;
- mandatory coverage floor: 90 percent;
- Python compilation: passed;
- Ruff: passed;
- strict MyPy: passed with no issues across 29 source files.

### Retained release artefact

- files: 51;
- artefact ID: `8912417530`;
- compressed size: 136,618 bytes;
- SHA-256: `9ee83d4015b1f96bf35925d3f509d80200167df24a6f277413edfd499ae36087`;
- retention: 30 days.

## 13. Explicitly deferred evidence

Phase 6 does not establish:

- committing or redistributing the original methodology files;
- object-storage persistence;
- production DOCX or Markdown extraction;
- stable passage creation and location tracking;
- malformed-file and duplicate-file handling against an operating ingestion service;
- lexical, semantic or hybrid indexing;
- searchable retrieval execution;
- access-control enforcement in a retrieval service;
- deterministic re-ingestion against stored originals;
- Founder confirmation of external usage rights;
- promotion of the 154 source-local headings into canonical methods.

These are integration or governance gates and must not be represented as complete.

## 14. Phase-gate conclusion

Phase 6 is complete as the governed chat-first knowledge-ingestion intelligence. Codex can later implement physical ingestion and retrieval against explicit source profiles, aliases, rights decisions, method transformations and gold cases rather than rediscovering those rules.