# 76 — Methodology Library Preimplementation Readiness

## Status

**Chat-first methodology-library design readiness: complete.**

This package defines what must be fixed before IMP-P1 implementation starts. It does not import original source bytes, create a searchable runtime, promote source-local headings into canonical methods, approve the current source corpus on the Founder’s behalf, authorize IMP-P1, or authorize Codex launch.

The governing machine specification is `configs/methodology-library-preimplementation-readiness.yaml` and the fail-closed validator is `scripts/validate_methodology_library_preimplementation_readiness.py`.

## 1. Why this package exists

Phase 6 already completed the knowledge-ingestion intelligence that can be prepared without operating the future library runtime. It profiles 23 Founder-supplied sources, 154 source-local method headings, 99 aliases, 21 dependency-resolution cases, 12 collision families, 12 original method-record examples, 46 retrieval gold cases and 10 Methodology Radar categories.

It also explicitly leaves physical source import, passage persistence, searchable retrieval, deterministic re-ingestion against stored originals and canonical method promotion for implementation. This package closes the remaining **design ambiguity** around those deferred activities so Codex should not have to invent policy while implementing P1.1–P1.5.

## 2. Existing contracts retained rather than redesigned

The existing typed knowledge contracts remain authoritative for their record shapes:

- `SourceDocument`;
- `SourcePassage`;
- `MethodRecord`;
- `ProblemArchetype`;
- `MethodSelection`;
- `MethodologyCandidate`.

The existing knowledge-ingestion configuration remains authoritative for source preservation, stable chunking inputs, canonical identity precedence, quarantine triggers, method admission, rights defaults, volatility and retrieval expectations.

The existing Methodology Radar remains the discovery and candidate-governance specification. Discovery creates candidates only; it does not silently widen the canonical source corpus and cannot automatically promote a method.

## 3. Canonical source corpus and approval denominator

Before physical import begins, implementation must consume an **explicit current Founder-approved canonical source manifest**.

The existing 23-source profile is the prepared candidate inventory. It is not silently converted into approval evidence merely because the files were Founder supplied or previously profiled.

An exact approval record must:

1. bind the exact SHA-256 of `knowledge/source-manifest.yaml`;
2. list every approved source ID;
3. list any excluded source IDs and record a reason for each exclusion;
4. define the current approved-source accounting denominator;
5. reject unlisted discoveries as automatic additions to that denominator;
6. become stale if the bound source manifest or approved source bytes change.

`knowledge/canonical-source-approval.template.yaml` provides the required shape but deliberately records no approval.

Approval of the source denominator is not, by itself, authorization to start IMP-P1.

## 4. Source accounting and dispositions

Every Founder-approved source must have exactly one current governed disposition:

- `ingested_structured`;
- `duplicate`;
- `superseded`;
- `quarantined`;
- `excluded_with_reason`.

The implementation must preserve disposition history and must never silently omit an approved source.

A duplicate or superseded disposition does not erase provenance. An exclusion is invalid without a recorded reason. Quarantine is an explicit visible state rather than an implementation failure that can be silently bypassed.

The IMP-P1 completeness denominator is therefore approved source identities, **not** discovered files, extracted chunks, indexed headings or method-record counts.

## 5. Identity, provenance and versioning

Implementation must preserve the identity chain:

`approved source → immutable original/checksum → source passage/native locator → structured record → method version/release`

Required semantics:

- a stable source identity exists before extraction;
- original source bytes are preserved unchanged;
- SHA-256 is reverified when original bytes are physically imported;
- aliases resolve to canonical source identities rather than replacing them;
- source passages retain a page, section, paragraph, line or equivalent native locator where available;
- every generated structured record retains source identity and transformation provenance;
- a source change creates review work and a new governed version rather than silently replacing evidence;
- superseded source and method versions remain available for audit and rollback;
- aliases, labels and display names cannot change canonical identity.

## 6. Extraction and quarantine contract

P1.2 must implement the existing Markdown and DOCX extraction boundary without treating document content as executable authority.

Before implementation is accepted:

- identical source bytes and extraction configuration must produce deterministic identities and locations;
- instruction-like document content is untrusted data and never system instruction;
- malformed packages quarantine;
- checksum mismatches quarantine;
- ambiguous aliases quarantine;
- duplicate identities quarantine until explicitly resolved;
- unresolved dependencies remain visible controlled gaps;
- incomplete method records quarantine rather than being promoted or silently repaired by inference.

## 7. Method admission, collision and promotion

The 154 profiled domain headings are source-local retrieval and reconstruction signals. They are **not** 154 canonical methods.

A method may enter a canonical release only after:

1. a complete `MethodRecord` exists;
2. source provenance is reviewable;
3. copyright, licence and trademark concerns are reviewed where applicable;
4. the procedure is independently reconstructed without protected expression;
5. relevant evaluation/regression tests exist and pass;
6. collision, redundancy and compatibility analysis is complete;
7. an independent reviewer accepts the record;
8. the Founder approves promotion.

Automatic merge, automatic promotion and source self-authorization remain prohibited.

Collision handling must compare decision supported, problem type, preconditions, evidence burden, procedure, outputs, limitations and failure modes before any merge or supersession decision.

## 8. Retrieval acceptance before P1 completion

The existing 46 source-grounded retrieval cases are the minimum governed gold set for implementation.

Retrieval acceptance must establish, at minimum:

- exact expected source identity where a case specifies one;
- exact expected heading/native anchor where a case specifies one;
- prohibited source substitutions fail the case;
- ambiguous identity is surfaced rather than automatically guessed;
- source/access/rights filters cannot be bypassed by semantic similarity;
- full provenance accompanies evidence-bearing retrieval;
- a search snippet is never treated as evidence by itself.

The implementation may add broader retrieval metrics and cases, but it may not weaken these exact-case semantics.

## 9. Rights, confidentiality and protected expression

The current conservative rights posture remains controlling:

- Founder-supplied methodology may be profiled and used for governed internal derivation under the existing policy;
- external redistribution remains denied by default;
- client-confidential content is prohibited from the global methodology library;
- distinctive third-party templates, diagrams and protected expression are not copied into canonical methods;
- generated methods must be original offdata reconstructions with retained provenance;
- changed rights status produces review work rather than silent expansion of permitted use.

Rights confirmation remains required wherever the intended use exceeds the currently governed internal-use boundary.

## 10. Release, supersession and rollback

A canonical methodology release must be versioned and auditable.

Before a release is accepted:

- promoted method versions are immutable;
- the release has an exact manifest of included method versions and source provenance;
- regression failure blocks release;
- supersession links preserve the prior version rather than deleting it;
- promotion, merge and supersession decisions retain reviewer and Founder decision history;
- rollback restores the prior canonical release without reconstructing it from mutable current state.

Methodology Radar changes create candidates/review tasks and cannot silently mutate a released canonical library.

## 11. IMP-P1 implementation handoff

### P1.1 — Source import

Implementation evidence must show approved-corpus import, unchanged originals, checksum re-verification, source metadata/version capture and rights/confidentiality fields.

### P1.2 — Extraction pipeline

Implementation evidence must show deterministic Markdown/DOCX extraction, stable native source locations, malformed/duplicate handling and untrusted-instruction isolation.

### P1.3 — Canonical manifest and alias resolver

Implementation evidence must show 100% approved-source disposition accounting, exactly one current disposition per approved source, deterministic aliases, visible dependency gaps and zero silent omissions.

### P1.4 — Method and problem schemas

Implementation evidence must show valid and invalid fixtures for the typed contracts, quarantine of incomplete records, collision decisions and enforcement of the no-automatic-promotion boundary.

### P1.5 — Search and retrieval

Implementation evidence must show lexical/semantic/filtered retrieval, the complete governed gold set, provenance, ambiguity handling, access controls and prohibited-substitution failures.

## 12. What is complete now

The following preimplementation decisions are complete and governed:

- record-shape contracts;
- profiled candidate-source inventory;
- source identity and checksum metadata;
- alias and dependency-resolution behavior;
- collision-review dimensions;
- representative original method-record reconstructions;
- retrieval gold cases;
- Methodology Radar candidate/promotion boundaries;
- conservative rights and confidentiality policy;
- approved-source accounting semantics;
- P1.1–P1.5 implementation-evidence expectations;
- release, supersession and rollback semantics;
- an exact Founder source-approval template;
- fail-closed CI validation of this preimplementation package.

## 13. What remains intentionally uncompleted

This chat-first package does **not** claim completion of:

- explicit Founder approval of the current 23-source candidate corpus;
- physical storage/import of original methodology files;
- production passage extraction or persistence;
- searchable lexical/semantic retrieval runtime;
- final access-control enforcement in a live retrieval service;
- deterministic re-ingestion against stored originals;
- canonical promotion of the 154 indexed headings;
- external redistribution rights;
- IMP-P1 implementation evidence.

Those are future manual or implementation gates and must remain visible rather than being inferred from this document.

## 14. No-widening and authorization boundary

This readiness package adds no IMP phase, no backlog task, no PCFA-07 obligation and no Phase-0 obligation.

It does not modify Codex launch scope, which remains exactly P0.1–P0.4 under the current launch authority.

`imp_p1_authorized=false`.

`codex_start_authorized=false`.

No source bytes are ingested by this package, no method is promoted, no runtime is activated and no merge approval is inferred.
