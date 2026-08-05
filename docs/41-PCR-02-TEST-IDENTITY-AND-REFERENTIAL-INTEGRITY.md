# 41 — PCR-02 Test Identity and Referential-Integrity Repair

## Status

**PCR-02 complete and independently CI-validated.**

Date: 2026-08-05

PCR-02 separates stable semantic test identities from executable pytest node paths and validates the governed identifier graph before Codex integration. It repairs the dangling and wrong-kind references identified during the pre-Codex review without changing any lifecycle, authority, source-rights, analytical-oracle, deliverable or security conclusion.

## 1. Stable semantic test layer

`requirements/test-definitions.yaml` is the governed source for implementation evidence. `requirements/test-definitions.json` is its deterministic generated registry.

The registry preserves a semantic test ID when its status changes from planned to implemented. It records:

- stable test ID;
- purpose or title;
- test kind and execution stage;
- requirement, control and threat relationships;
- planned or implemented status;
- one or more executable evidence nodes;
- evidence environment;
- expected result and real-client-data significance where applicable;
- exact source records from which the definition was assembled.

The legacy `requirements/test-registry.json` remains the executable-node and remaining-planned view required by Phase 1. It now points to the canonical semantic registry and removes completed IDs only from the planned view, not from canonical identity history.

## 2. Threat-model repairs

PCR-02 replaces six invalid references:

| Threat | Invalid reference | Governed replacement |
|---|---|---|
| THR-002 | `SEC-P7-CONTEXT-001` | `SEC-P7-TENANT-001` alongside `SEC-P7-ENGAGEMENT-001` |
| THR-011 | `SEC-P7-BACKUP-001` | `SEC-P7-CONTROL-001` alongside `IT-BACKUP-RESTORE-001` |
| THR-013 | `SEC-P7-AUDIT-001` | `SEC-P7-BASELINE-001` alongside `IT-BASELINE-IMMUTABLE-001` |
| THR-014 | `SEC-P7-SUPPLY-001` | `SEC-P7-UNTRUSTED-001` alongside `SEC-SUPPLY-CHAIN-001` |
| THR-017 | requirement ID `QA-008` used as a test | semantic test `UT-QA-INDEP-001` |
| THR-018 | `SEC-P7-ENV-001` | `SEC-P7-DEV-DATA-001` alongside `IT-ENV-SEPARATION-001` |

These replacements use existing governed semantic tests. PCR-02 does not invent operating evidence or mark deferred production tests complete.

The new gate also detected that mandatory control `CTRL-KILL-SWITCH-TEST` had no governed semantic-test binding. It is now linked to planned operating test `IT-ROLLBACK-001`. The binding closes the governance gap while retaining the test's planned status until Codex can execute operating rollback and kill-switch evidence.

## 3. Governed identifier graph

`requirements/referential-integrity-baseline.json` records a deterministic pass report and typed edges across:

- 123 catalogue requirements;
- semantic test definitions and executable evidence;
- security controls, threats and incident playbooks;
- agents and their skill packages;
- commands, events and requirement mappings;
- primary and compound fixtures and their engagement types;
- source profiles and alias-resolution targets.

The validator rejects:

- dangling references;
- wrong-kind references;
- duplicate identifiers or duplicate alias rules;
- evidence nodes that do not exist;
- evidence nodes without requirement mappings;
- semantic tests and evidence nodes with no shared requirement;
- planned tests that claim execution evidence;
- retired tests referenced by threats;
- threats with missing controls, playbooks or tests;
- mandatory controls without governed test coverage;
- commands pointing to unknown requirements or events;
- compound fixtures using unknown engagement types;
- aliases pointing to unknown sources;
- agents pointing to missing skill packages.

## 4. Ambiguous aliases

The Phase 6 alias design intentionally permits the same alias text to resolve to different source IDs when ambiguity must be quarantined. PCR-02 therefore validates unique alias-to-source rules rather than incorrectly requiring every alias string to be globally unique. Exact duplicate rules remain prohibited.

## 5. Test hierarchy completion

`META-TEST-HIERARCHY-001` is converted from planned to executable evidence. The generated semantic registry contains all historical planned identities plus the Phase 7 security catalogue, with completed identities retained rather than deleted.

The validated release contains:

- 99 stable semantic test identities;
- 45 implemented semantic tests;
- 54 remaining planned semantic tests;
- 245 executable pytest evidence nodes;
- 20 completed planned-test identities retained in canonical history.

No operating integration, artefact-rendering, production-security or Founder-acceptance test is upgraded merely because its specification is now referentially sound.

## 6. Validation result

Permanent read-only GitHub Actions run `30988776497`, job `92249669835`, validated branch head `3064996e92d96f96abb225c22a403d8c7de1483e` through pull-request merge reference `bc5ed646de65ccfa10e4159f7f9000f99bf78295`.

The gate confirmed:

- all Phase 1–7 validators passed;
- PCR-01 passed;
- PCR-02 passed;
- clean deterministic generation passed;
- 604 typed reference edges and zero unresolved references;
- 247 runtime tests passed;
- 93.14 percent coverage against a 90 percent floor;
- Python compilation passed;
- Ruff passed;
- strict MyPy passed across 32 source files.

The retained 73-file artefact is `8923215176`, with compressed size 181,769 bytes and SHA-256 `6729db7667238391097428ed04e386d3729a4d8b6cb1ba6000342c85d95c2024`.

See `reports/pcr02-validation-evidence.md` for the full evidence record.

## 7. Security and authority boundary

PCR-02 does not:

- enable real client data;
- approve a processor;
- create production-security evidence;
- import original methodology binaries;
- expose restricted answer keys to agents;
- authorise an external action;
- allow an agent to approve its own work;
- replace the Founder as accountable decision-maker.

Real client data remains prohibited.
