# Workstream 5 launch-control evidence

## Repository package

- Source: `configs/codex-phase0-launch-control.yaml`
- Contract: `contracts/codex-phase0-launch-control.json`
- Control schema: `schemas/codex-phase0-launch-control.schema.json`
- Evidence schema: `schemas/codex-phase0-launch-evidence.schema.json`
- Permit schema: `schemas/codex-phase0-launch-permit.schema.json`
- Builder: `scripts/build_workstream5_launch_control.py`
- Validator: `scripts/validate_workstream5_launch_control.py`
- Launch verifier: `scripts/prepare_codex_phase0_launch.py`
- Generated canonical issue body: `handoff/codex-phase0-issue-workstream5.md`
- Permanent release record: `releases/codex-phase0-launch-control-2026-08-06.json`
- Workflow: `.github/workflows/workstream5-launch-control.yml`

## Baseline

- Repository: `rayrayxing/offdata-os`
- Pre-Workstream 5 `main`: `94fe29e60449a384c1c5fad1f3bb6289d4ac1c29`
- Canonical issue: #1
- Hosted-controls issue: #19
- Duplicate issue: #2
- Required Codex branch: `codex/phase-0-foundation`
- Authorized task boundary after all gates: P0.1–P0.4 only

## Expected validation

The exact pull-request merge reference must:

- rebuild every Phase 1–7, PCR-01–10, Workstream 4 and Workstream 5 record without a diff;
- pass every retained semantic and mutation validator;
- pass the launch verifier self-test without writing a permit;
- pass the deterministic runtime suite at or above 90 percent coverage;
- pass compilation, Ruff and strict MyPy;
- verify issue #1 is open, issue #2 is closed as duplicate and issue #19 remains open before manual completion;
- verify no Codex Phase 0 branch or pull request exists; and
- retain an exact artifact with run, job, SHA and digest evidence.

## Manual gates intentionally pending

The committed contract must retain:

- `hosted_controls_verified=false`;
- `clean_macos_environment_verified=false`;
- `explicit_founder_phase0_approval_received=false`;
- `approved_main_sha_bound=false`;
- `launch_permit_issued=false`; and
- `codex_start_authorized=false`.

No successful repository check may flip these values.

## Costs and credentials

- Paid cost incurred by this workstream: zero.
- Paid service required for launch control: none.
- New credential required: none.
- Actual permit preparation requires the Founder's already-authenticated local Git and GitHub CLI session; credentials are never captured in evidence.

## Rollback

Before launch, revert the Workstream 5 merge and restore the PCR-10 issue body if the control package must be withdrawn. Delete only `.local/codex-phase0-launch/` to remove local evidence and permits. Keep `codex/phase-0-foundation` absent.

After launch, follow the draft Phase 0 pull request's rollback instructions and stop at the Founder gate.
