# PCR-01 canonical release reconciliation validation evidence

## Status

**PASS** — all Phase 1–7 regression gates and the PCR-01 canonical-release reconciliation gate completed successfully.

Date: 2026-08-05

## Canonical source release

PCR-01 reconciles the final completed Phase 1–7 source release:

- pull request: `#15`;
- pull-request head: `8da0f1167d9b6f4da792770b0d564379aa46c3fe`;
- pull-request merge reference: `264459045ce75d7d7c60cbc980a50193f08a6f16`;
- controlling `main` commit: `7dc5531e641158e5a84fbbb9fdf07cefefd4782b`;
- final Phase 1–7 run: `30976222896`;
- final Phase 1–7 job: `92210649514`;
- final Phase 1–7 artifact: `8918355687`;
- artifact SHA-256: `3b9f14c520d31ce5f73fbecc726b032a3134042769ee84176e85d642fe2ea852`.

Runs `30975868412` and `30976088173` are preserved as successful superseded snapshots. They are not the controlling release evidence.

## PCR-01 implementation gate

- workflow: `Machine contracts, agents, oracle, deliverables, fixtures, knowledge, security and release`;
- run ID: `30983105556`;
- job ID: `92231688824`;
- validated branch head: `6d770f2128785c4dbeaf646e3eaa839591c0f299`;
- validated pull-request merge reference: `cd4e72dac2cce80d238477c9e1b0288c616b2947`;
- runner: Ubuntu 24.04;
- Python: 3.11.15;
- conclusion: success.

## Release-reconciliation evidence

The validation confirms:

- one controlling release identity exists;
- the final Phase 7 run is distinct from both superseded snapshots;
- exact SHA-256 and byte size are recorded for seven governed records;
- all 23 Founder-supplied source profiles are represented;
- source-profile counts reconcile to 11 core Markdown and 12 domain DOCX sources;
- source-profile bytes reconcile to 2,294,919;
- aggregate source-profile digest is reproducible;
- original source binaries remain uncommitted;
- external redistribution remains denied by default;
- restricted analytical and deliverable answer keys remain agent-invisible;
- changed or missing governed files invalidate the canonical manifest;
- changed source-profile checksums invalidate governed expectations;
- the committed manifest is byte reproducible and self-verifying;
- real client data remains disabled;
- Founder accountability remains preserved.

## Prior-phase regression results

- Phase 1 contract validator: passed;
- Phase 2 agent-system validator: passed;
- Phase 3 analytical-oracle validator: passed;
- Phase 4 deliverable-semantic validator: passed;
- Phase 5 additional-fixture validator: passed;
- Phase 6 knowledge-ingestion validator: passed;
- Phase 7 security-and-regionalisation validator: passed;
- read-only clean generation of all Phase 1–7 and PCR-01 governed records: passed.

## Requirement traceability

- implemented test nodes: 226;
- remaining planned tests: 55;
- completed planned-test IDs: 19;
- catalogue requirements mapped: 123 of 123.

PCR-01 adds eleven mapped executable test nodes. It does not convert any operating-infrastructure or Founder-acceptance test into completed evidence.

## Complete deterministic quality gate

- runtime tests: 228 passed;
- total code coverage: 93.39 percent;
- enforced coverage minimum: 90 percent;
- Python compilation: passed;
- Ruff lint: passed;
- strict MyPy: passed across 31 source files.

## Retained implementation-gate artifact

- files: 68;
- artifact ID: `8920937473`;
- compressed size: 163,702 bytes;
- SHA-256: `6cc7168786e2484a99d558d57e261194cc124943f3c4e9ece4b6c2d8480784d6`;
- retention: 30 days.

## Documentation-inclusive boundary

This report records the successful implementation gate. The exact documentation-inclusive pull-request head must pass the same unchanged checks before review and merge. That final run will be the merge gate and will not silently replace the canonical Phase 1–7 source-release identity stored in the generated manifest.

## Operating boundary

PCR-01 does not validate an operating application or production environment. The following remain deferred:

- macOS execution;
- PostgreSQL and object-storage operation;
- physical methodology-file import;
- live retrieval and model providers;
- durable workflow execution;
- Office rendering;
- external integrations and actions;
- production security evidence;
- Founder acceptance of real-client production.

Real client data remains prohibited.
