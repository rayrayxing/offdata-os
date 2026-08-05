# 40 — PCR-01 Canonical Release Reconciliation

## Status

**Implementation in progress; canonical Phase 1–7 evidence identified and governed.**

Date: 2026-08-05

PCR-01 reconciles the completed chat-first Phase 1–7 release into one immutable source of truth before Codex integration begins. It does not redesign any completed phase and does not claim operating infrastructure, live model execution or production readiness.

## 1. Canonical Phase 1–7 release

The controlling completed chat-first release is:

- repository: `rayrayxing/offdata-os`;
- merged pull request: `#15`;
- pull-request head: `8da0f1167d9b6f4da792770b0d564379aa46c3fe`;
- pull-request merge reference: `264459045ce75d7d7c60cbc980a50193f08a6f16`;
- controlling `main` merge commit: `7dc5531e641158e5a84fbbb9fdf07cefefd4782b`;
- final validation run: `30976222896`;
- final validation job: `92210649514`;
- retained release artifact: `8918355687`;
- artifact SHA-256: `3b9f14c520d31ce5f73fbecc726b032a3134042769ee84176e85d642fe2ea852`;
- artifact files: 65;
- artifact compressed size: 157,193 bytes;
- artifact retention: 30 days.

This final exact-head gate supersedes the earlier successful implementation and documentation snapshots. Those snapshots remain recorded for audit history but are not controlling release evidence.

## 2. Reconciliation source and generated manifest

`configs/canonical-release.yaml` records the governed evidence source. It distinguishes:

- the final authoritative release;
- two earlier successful but superseded validation snapshots;
- Phase 1–7 quality totals;
- the critical governed records whose exact bytes must be digested;
- the 23 Founder-supplied source profiles and their original-file checksums;
- the boundaries that remain false or prohibited.

`releases/canonical-chat-first-phase1-7-release.json` is generated deterministically from that source and the exact repository bytes. It contains:

- one release identity;
- exact PR, commit, workflow, job and artifact evidence;
- SHA-256 and byte size for seven governed records;
- all 23 source-profile checksum records;
- an aggregate source-profile digest;
- the historical Phase 1–7 quality summary;
- preserved authority and security boundaries;
- a self-verifying manifest digest.

## 3. Governed records

The release manifest digests:

1. `requirements/test-registry.json`;
2. `fixtures/additional-primary-fixtures.json`;
3. `fixtures/digital-ai/FIXTURE-DAI-001/oracle-baseline.json`;
4. `fixtures/digital-ai/FIXTURE-DAI-001/deliverable-semantic-baseline.json`;
5. `knowledge/knowledge-ingestion-baseline.json`;
6. `security/security-regionalisation-baseline.json`;
7. `knowledge/source-manifest.yaml`.

The analytical and deliverable answer keys remain restricted and explicitly agent-invisible.

## 4. Source-library integrity

PCR-01 preserves exactly:

- 11 core Markdown consulting standards;
- 12 domain DOCX methodology packs;
- 23 total source profiles;
- 2,294,919 profiled source bytes;
- status `profiled_original_not_committed`;
- external redistribution denied by default;
- original methodology binaries uncommitted.

The original local source files remain the import inputs for Codex. PCR-01 does not copy, transform or broaden rights to those files.

## 5. Superseded evidence snapshots

The following successful runs remain part of the audit history but are not the final controlling evidence:

| Run | Job | Artifact | Reason superseded |
|---:|---:|---:|---|
| `30975868412` | `92209612760` | `8918232404` | Successful implementation gate before later documentation and exact-head runs |
| `30976088173` | `92210248160` | `8918307764` | Successful documentation-inclusive gate before the final exact-head gate |

They are retained as historical evidence rather than silently deleted or presented as current.

## 6. Deterministic controls

`offdata_core.release_reconciliation` provides strict immutable contracts and deterministic functions for:

- release-evidence validation;
- exact repository-file SHA-256 calculation;
- source-profile checksum preservation;
- aggregate source-profile reconciliation;
- restricted-oracle isolation checks;
- byte-reproducible manifest generation;
- independent committed-manifest verification;
- rejection of missing, changed or contradictory evidence.

The PCR-01 validator also requires the Phase 7 completion record, Phase 7 validation report and development status to identify the same canonical release.

## 7. Validation scope

PCR-01 adds executable evidence for:

- exact release identity;
- final-versus-superseded evidence separation;
- governed-record digest integrity;
- source-profile checksum integrity;
- deterministic manifest reproducibility;
- stale-manifest detection;
- missing-record failure;
- restricted-oracle isolation;
- continued real-client-data prohibition;
- continued Founder accountability.

The complete Phase 1–7 test and quality gate must pass unchanged alongside PCR-01.

## 8. Explicit boundary

PCR-01 reconciles the completed chat-first release. It does not establish:

- an operating macOS development environment;
- PostgreSQL or object-storage execution;
- physical methodology-file import;
- live retrieval;
- model-provider integration;
- durable workflow execution;
- rendered Office deliverables;
- CRM, email, calendar or external actions;
- production identity, encryption, restoration, monitoring or deletion evidence;
- real-client production approval.

Real client data remains prohibited.

## 9. Final validation evidence

The exact PCR-01 branch-head validation run, retained artifact and merge evidence will be recorded after the documentation-inclusive gate passes. Until then, this document governs the reconciled Phase 1–7 source release but does not claim PCR-01 completion.
