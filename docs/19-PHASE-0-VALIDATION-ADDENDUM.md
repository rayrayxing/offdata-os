# 19 — Phase 0 Validation Addendum

## Controlling machine contract

The authoritative Phase 0 input inventory, task graph, command set, boundaries, stop conditions and activation conditions are in `handoff/codex-phase0-handoff.json`.

Before application work, Codex must run:

```bash
python scripts/validate_pcr05_runtime_adapters.py
python scripts/validate_pcr06_hermes_compatibility.py
python scripts/validate_pcr07_northstar_blueprint.py
python scripts/validate_pcr08_initial_operating_controls.py
python scripts/validate_pcr04_codex_handoff.py
```

`initial_operating_controls_activation_authorized=false`, `runtime_activation_authorized=false`, `hermes_activation_authorized=false` and `northstar_implementation_authorized=false` remain binding. The intended working branch is `codex/phase-0-foundation`. A passing handoff confirms repository-local prerequisites; it does not replace explicit Founder approval or the hosted-control checks tracked in issue #19.

## Pre-existing implementation inputs

Codex must integrate, not duplicate, the following governed assets:

- `packages/offdata-core/pyproject.toml`
- `packages/offdata-core/src/offdata_core/`
- `packages/offdata-core/tests/`
- `configs/lifecycle.yaml`
- `configs/policy.yaml`
- `configs/agents.yaml`
- `configs/agent-evaluations.yaml`
- `configs/canonical-release.yaml`
- `configs/knowledge-ingestion.yaml`
- `configs/repository-governance.yaml`
- `configs/security-regionalisation.yaml`
- `configs/runtime-adapters.yaml`
- `contracts/runtime-adapter-contracts.json`
- `schemas/runtime-adapter-contracts.schema.json`
- `configs/hermes-compatibility.yaml`
- `contracts/hermes-compatibility-pack.json`
- `schemas/hermes-compatibility.schema.json`
- `configs/northstar-integration-blueprint.yaml`
- `contracts/northstar-integration-blueprint.json`
- `schemas/northstar-integration-blueprint.schema.json`
- `configs/initial-operating-controls.yaml`
- `contracts/initial-operating-controls.json`
- `schemas/initial-operating-controls.schema.json`
- `api/openapi.json`
- `contracts/model-registry.json`
- `contracts/command-event-catalogue.json`
- `schemas/*.json`
- `requirements/test-registry.json`
- `requirements/test-definitions.json`
- `requirements/referential-integrity-baseline.json`
- `fixtures/additional-primary-fixtures.json`
- `knowledge/knowledge-ingestion-baseline.json`
- `security/security-regionalisation-baseline.json`
- `releases/canonical-chat-first-phase1-7-release.json`
- `repository/repository-governance-baseline.json`

The original Founder-supplied methodology binaries remain outside the repository. Their governed profiles and checksums are in `knowledge/source-manifest.yaml`; Phase 0 must not import or expose those originals.

## Required validation

1. Validate the PCR-05 runtime contract, PCR-06 Hermes compatibility, PCR-07 Northstar blueprint, PCR-08 initial operating controls, PCR-04 handoff and every prerequisite validator.
2. Install `packages/offdata-core` in an isolated Python environment.
3. Run the complete test suite with the 90 percent coverage floor.
4. Run Python compilation, Ruff and strict MyPy.
5. Validate generated JSON, JSON Schema and YAML records.
6. Confirm generated records are clean and byte-reproducible.
7. Confirm no duplicate lifecycle, policy, contract or test-identity implementation is introduced.
8. Preserve the default-deny real-client-data and external-action boundaries.
9. Add Phase 0 application and infrastructure checks without removing any Phase 1–7 or PCR-01–08 gate.
10. Document corrections as reviewed changes rather than silently changing governing intent.

## Current verified baseline

The final PCR-03 exact-head run before PCR-04 recorded:

- 123 mapped requirements;
- 99 semantic tests;
- 245 executable test nodes;
- 604 typed reference edges;
- zero unresolved references;
- 247 runtime tests passed;
- 93.14 percent coverage against a 90 percent floor;
- successful compilation, Ruff and strict MyPy;
- real client data disabled;
- external actions not authorised.

PCR-04 adds a deterministic handoff validator and mutation checks. PCR-05 adds typed runtime boundaries without activating a runtime. PCR-06 preserves Hermes compatibility without activation. PCR-07 defines the synthetic Northstar end-to-end implementation blueprint without authorising implementation. PCR-08 configures the initial Founder-only, deny-by-default operating controls while explicitly leaving hosted, operating-environment and production evidence incomplete. The authoritative current result is always the latest successful complete GitHub Actions run for the exact pull-request merge reference.

## Phase boundary

Phase 0 creates the controlled project foundation only. It must not begin knowledge-ingestion implementation, product workflows, production infrastructure, real-client processing, external integrations or Phase 1 work.

## PCR-09 first Codex issue contract

Before Phase 0 can be authorised, the generated first-issue contract must remain current and pass its dedicated validator:

- `contracts/codex-phase0-issue.json`
- `scripts/validate_pcr09_codex_issue.py`

Preparing or validating this contract does not authorise Codex to start.
