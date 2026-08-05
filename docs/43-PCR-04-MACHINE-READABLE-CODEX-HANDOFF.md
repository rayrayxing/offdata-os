# 43 — PCR-04 Machine-Readable Codex Handoff

## Purpose

PCR-04 replaces a prompt-only engineering transfer with a deterministic, schema-validated and semantically checked Codex Phase 0 handoff.

The handoff makes the first Codex assignment unambiguous without granting autonomous authority to begin, merge, purchase, deploy, connect external systems or use real client data.

## Governed artefacts

- `configs/codex-handoff.yaml` — human-reviewable source contract.
- `handoff/codex-phase0-handoff.json` — generated machine-readable handoff.
- `schemas/codex-handoff.schema.json` — structural contract.
- `scripts/build_pcr04_codex_handoff.py` — deterministic builder.
- `scripts/validate_pcr04_codex_handoff.py` — schema, semantic, path, dependency, prerequisite and mutation validation.
- `docs/14-CODEX-KICKOFF.md` — minimal invocation prompt that delegates details to the machine contract.
- `docs/19-PHASE-0-VALIDATION-ADDENDUM.md` — corrected pre-existing asset inventory and validation boundary.
- `reports/pcr04-validation-evidence.md` — exact run and review evidence.

## Contract contents

The generated handoff records:

- instruction precedence and non-controlling historical repositories;
- the required read order;
- the canonical Phase 0 target and maximum authorised phase;
- prerequisite release, test-identity, referential-integrity and repository-governance records;
- existing deterministic assets that must be integrated rather than duplicated;
- a dependency-checked P0.1–P0.4 task graph;
- required root-executable build, validation, test, compilation, lint and type-check commands;
- the canonical branch and draft-pull-request workflow;
- prohibited actions and stop conditions;
- Founder report fields;
- activation conditions;
- immutable data, external-action, cost, deployment, merge and accountability boundaries;
- a generated readiness snapshot from PCR-01, PCR-02 and PCR-03 records.

## Validation behaviour

PCR-04 fails when:

- the generated file is stale;
- the JSON does not satisfy its schema;
- a referenced repository path is missing;
- a prerequisite record is not healthy;
- the Phase 0 task graph is incomplete, duplicated, cyclic or contains unknown dependencies;
- Phase 1 or later becomes authorised;
- explicit Founder approval is removed;
- prohibited data, deployment, payment, external-action or merge boundaries are weakened;
- the canonical Phase 0 branch or draft-PR rule changes;
- the PCR-04 command is removed from the handoff;
- a package command omits its required working directory;
- transient stacked-pull-request metadata enters the canonical handoff;
- kickoff documentation drifts away from the machine contract.

The validator applies eight controlled mutations and proves that phase escalation, autonomous activation, external-action enablement, duplicate task identity, dependency cycles, removal of the PCR-04 command, missing package working directories and transient stacked-branch metadata are rejected.

## Activation boundary

A green PCR-04 gate means the repository is internally prepared for a Codex handoff. It does not mean Codex may start automatically.

All activation conditions in the handoff remain required:

1. PCR-03 merged to `main`;
2. PCR-04 merged to `main`;
3. issue #19 hosted controls verified;
4. explicit Founder Phase 0 approval;
5. a clean macOS environment.

## Cost, data and authority

PCR-04 requires no new paid service. It does not enable real client data, approve processors, import methodology binaries, expose restricted evaluation material, authorise external actions, deploy infrastructure or permit autonomous merge.

## Rollback

Before merge, close the PCR-04 pull request and delete its branch. After merge, use a reviewed revert of the PCR-04 merge commit. Do not weaken PCR-03 hosted protections or prior phase gates during rollback.
