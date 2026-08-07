# 19 — IMP-P0 Validation Addendum

## Current state and boundary

**Chat-first development is integrated through CF-P1–7, PCR-01–10, WS-4, WS-5 and WS6.13; WS6.14–WS6.16 final reconciliation and all manual launch gates remain pending; `codex_start_authorized=false`.**

The repository remains pre-Codex. This addendum defines validation expectations for a future permitted IMP-P0 session. It does not authorise implementation, branch creation, merge or IMP-P1.

## Controlling contracts

The authoritative classification, input inventory, task graph, command set, boundaries, stop conditions and activation conditions are in:

- `repository/canonical-authority-registry.json`;
- `contracts/workstream6-phase-namespace.json`;
- `contracts/workstream6-required-workflow-identity.json`;
- `handoff/codex-phase0-handoff.json`;
- `contracts/codex-phase0-launch-control.json`;
- `handoff/codex-phase0-issue-final.md`;
- the future permanent release `releases/pre-codex-final-reconciliation-2026-08-06.json`;
- the valid local single-use permit produced by `scripts/prepare_codex_phase0_launch.py`.

The canonical implementation identifier is `IMP-P0`; stable `phase0` filenames and machine keys are compatibility identifiers only.

The required hosted status check is exactly `Validate final pre-Codex canonical handoff and complete release`. WS6.6 reserves that identity in `.github/workflows/workstream6-final-pre-codex.yml`; the workflow remains manual-only and deliberately fail-closed until WS6.15 activates the final implementation.

## Mandatory pre-launch validation

Before a permit may be issued:

1. validate `repository/canonical-authority-registry.json`, `contracts/workstream6-required-workflow-identity.json`, and run the complete command set in `handoff/codex-phase0-handoff.json`;
2. require `python scripts/require_workstream6_final_reconciliation.py` to pass against the exact current `main` SHA;
3. confirm issue #1 matches `handoff/codex-phase0-issue-final.md` and remains open;
4. confirm issue #2 remains closed as duplicate;
5. complete issue #19 with hosted-control and exact-allowlist branch-cleanup evidence;
6. complete the clean macOS doctor report and Founder environment attestation;
7. record exact-SHA Founder approval for IMP-P0 tasks P0.1–P0.4 only;
8. run `scripts/prepare_codex_phase0_launch.py` with all evidence files;
9. confirm no Codex branch or IMP-P0 pull request exists before permit issuance.

A passing repository-local validation does not satisfy the final release, hosted-control, environment, Founder-approval or permit gates.

## Retained runtime validation

The pre-existing provider-independent runtime boundary remains governed by `contracts/runtime-adapter-contracts.json`. Every complete validation must run `scripts/validate_pcr05_runtime_adapters.py`, and the resulting state must remain `runtime_activation_authorized=false`.

## Permit-gated branch rule

Create `codex/phase-0-foundation` only after a valid permit exists. The branch must start from the permit’s approved `main` SHA. The first commit must add `governance/codex-phase0-launch-ack.json`. Any SHA, release, issue-body, required-check, evidence, approval or scope drift invalidates the permit and requires a stop.

The IMP-P0 pull request must remain draft. Merge and IMP-P1 are not authorised by the permit.

## Pre-existing governed inputs

Codex must integrate rather than duplicate the committed deterministic package, including:

- `packages/offdata-core/`;
- `configs/`, `contracts/`, `schemas/`, `requirements/`, `fixtures/`, `knowledge/`, `security/` and `repository/` governed records;
- `repository/canonical-authority-registry.json` and its exact current/superseded classifications;
- `api/openapi.json`;
- the canonical CF-P1–7 release and PCR-01–10 records;
- Workstream 4 readiness evidence;
- Workstream 5 historical launch-control evidence;
- all current WS6 contracts and reports.

Founder-supplied methodology binaries remain outside the repository. Their governed profiles and checksums are in `knowledge/source-manifest.yaml`; IMP-P0 must not import, expose or redistribute the originals.

## Required implementation validation

After a valid permit and before opening the draft pull request, Codex must:

1. execute every builder and validator in the machine handoff and leave no generated diff;
2. install `packages/offdata-core` in an isolated supported environment;
3. run the complete test suite with the 90 percent coverage floor;
4. run Python compilation, Ruff and strict MyPy;
5. validate JSON, JSON Schema and YAML records;
6. confirm generated records remain byte-reproducible;
7. confirm no duplicate lifecycle, policy, contract, test-identity or authority implementation was introduced;
8. preserve default-deny real-client-data, paid-service, OAuth and external-action boundaries;
9. retain all CF-P1–7, PCR-01–10, WS-4, WS-5 and WS6 gates;
10. document corrections, costs, risks, evidence and rollback;
11. perform a separate review pass and repair all blocking defects without weakening controls.

## Current verified repository baseline

The latest complete WS6.3 exact merge-reference gate recorded:

- 123 mapped requirements;
- 99 semantic tests;
- 245 executable test nodes;
- 604 typed reference edges;
- zero unresolved references;
- 247 runtime tests passed;
- 93.14 percent coverage against a 90 percent floor;
- successful Python compilation, Ruff and strict MyPy across 32 source files;
- 38 WS6.3 status mutations rejected;
- 41 invalid launch bundles rejected;
- no permit emitted;
- no repository or GitHub mutation by launch self-tests;
- real client data disabled and external actions not authorised.

This baseline is predecessor evidence. The authoritative current result is the latest successful complete gate for the exact pull-request merge reference being reviewed.

## Phase boundary

A valid IMP-P0 permit may authorise only P0.1–P0.4: repository baseline, local development environment, engineering quality baseline and security/operating documentation. It does not authorise product workflows, production infrastructure, real-client processing, external integrations, merge or IMP-P1.
