# PCR-02 validation evidence

## Status

**PASS** — PCR-02 test identity and referential-integrity repair, together with the complete Phase 1–7 and PCR-01 regression suite, passed the permanent read-only release gate.

Date: 2026-08-05

## Exact GitHub Actions evidence

- workflow: `Machine contracts, agents, oracle, deliverables, fixtures, knowledge, security and release`;
- run ID: `30988776497`;
- job ID: `92249669835`;
- validated branch head: `3064996e92d96f96abb225c22a403d8c7de1483e`;
- validated pull-request merge reference: `bc5ed646de65ccfa10e4159f7f9000f99bf78295`;
- runner: Ubuntu 24.04;
- Python: 3.11.15;
- conclusion: success.

The permanent workflow used repository-level `contents: read` permission. Temporary source-retention and repair permissions were removed before this run.

## Stable semantic-test evidence

The generated semantic registry contains:

- semantic test identities: 99;
- implemented semantic test identities: 45;
- remaining planned semantic test identities: 54;
- executable pytest evidence nodes: 245;
- completed planned-test identities retained in history: 20.

A semantic test remains identifiable after moving from planned to implemented. Executable node paths are evidence implementations rather than the canonical identity.

`META-TEST-HIERARCHY-001` is now executable. No operating integration, production-security, artefact-rendering or Founder-acceptance test was upgraded merely because its references were repaired.

## Referential-integrity evidence

The deterministic graph validated:

- catalogue requirements: 123;
- security controls: 48;
- threats and abuse cases: 20;
- incident playbooks: 12;
- bounded agents: 11;
- commands: 10;
- events: 15;
- primary and compound fixture identities: 17;
- Founder-supplied source profiles: 23;
- alias rules: 99;
- typed reference edges: 604;
- unresolved references: **0**.

The validator rejects dangling references, wrong-kind references, duplicate identifiers, missing executable nodes, unmapped evidence, false execution claims, retired-test use, untested mandatory controls, missing skill packages, unknown command requirements or events, unknown fixture engagement types and invalid source aliases.

## Threat-model repairs

The gate verifies that the six invalid references identified during the pre-Codex review were replaced with existing governed semantic tests:

- `SEC-P7-CONTEXT-001` → `SEC-P7-TENANT-001`;
- `SEC-P7-BACKUP-001` → `SEC-P7-CONTROL-001`;
- `SEC-P7-AUDIT-001` → `SEC-P7-BASELINE-001`;
- `SEC-P7-SUPPLY-001` → `SEC-P7-UNTRUSTED-001`;
- wrong-kind requirement `QA-008` → semantic test `UT-QA-INDEP-001`;
- `SEC-P7-ENV-001` → `SEC-P7-DEV-DATA-001`.

The integrity gate also detected that mandatory control `CTRL-KILL-SWITCH-TEST` lacked governed semantic-test coverage. It is now linked to planned operating evidence `IT-ROLLBACK-001`; the control is covered without falsely claiming that an operating kill-switch test has executed.

## Mutation and reproducibility evidence

PCR-02 includes mutation tests for:

- dangling test, requirement, control, playbook, agent, event, fixture, source and alias references;
- requirement IDs used where test IDs are required;
- nonexistent executable test nodes;
- planned tests claiming execution evidence;
- evidence nodes without requirement mappings;
- semantic tests and executable nodes with no shared requirement;
- mandatory controls without governed test coverage;
- stale or byte-drifted generated registries;
- duplicate and invalid alias rules.

The semantic registry and referential-integrity baseline regenerate byte-for-byte from governed source records.

## Complete deterministic quality gate

- Phase 1 validator: passed;
- Phase 2 validator: passed;
- Phase 3 analytical-oracle validator: passed;
- Phase 4 deliverable-semantic validator: passed;
- Phase 5 fixture-programme validator: passed;
- Phase 6 knowledge-intelligence validator: passed;
- Phase 7 security-regionalisation validator: passed;
- PCR-01 canonical-release validator: passed;
- PCR-02 test-identity and referential-integrity validator: passed;
- clean deterministic generation: passed;
- runtime tests: **247 passed**;
- total code coverage: **93.14 percent**;
- required coverage floor: 90 percent;
- Python compilation: passed;
- Ruff: passed;
- strict MyPy: passed across **32 source files**.

## Retained release artefact

- artefact ID: `8923215176`;
- name: `offdata-chat-first-release-bc5ed646de65ccfa10e4159f7f9000f99bf78295`;
- files: 73;
- compressed size: 181,769 bytes;
- SHA-256: `6729db7667238391097428ed04e386d3729a4d8b6cb1ba6000342c85d95c2024`;
- created: 2026-08-05T08:23:47Z;
- expiry: 2026-09-04T08:23:46Z;
- retention: 30 days.

## Preserved boundary

PCR-02 does not install Codex or Hermes, import original methodology binaries, create an operating identity or storage system, execute deferred production tests, authorise external actions, expose restricted answer keys or enable real client data.

**Real client data remains prohibited.**
