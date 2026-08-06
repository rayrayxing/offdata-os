# 50 — Workstream 4 Hosted Controls, Evidence and Environment Readiness

## Purpose

Workstream 4 converts the integrated PCR-03 through PCR-10 repository into an auditable pre-Codex release package without claiming settings or environment facts that cannot be proved from repository files.

The repository-side preparation is automated and deterministic. GitHub account settings, branch protection and the clean macOS machine remain explicit Founder attestations. A green repository gate never authorizes Codex by itself.

## Authoritative records

- `configs/workstream4-readiness.yaml` — human-reviewable readiness source.
- `contracts/workstream4-readiness.json` — deterministic machine contract.
- `releases/pre-codex-chat-first-2026-08-06.json` — permanent release evidence committed to the repository.
- `scripts/doctor_pre_codex_macos.py` — non-destructive, redacted clean-machine doctor.
- Issue #19 — hosted-control and environment attestation record.
- Issue #1 — canonical Codex Phase 0 assignment, still not authorized to start.

## Repository-side completion

The repository package must:

1. retain final integrated `main` SHA `617e4fe59a9f712d75da29f88508819c0296fc84`;
2. retain the exact PCR-10 and complete-release run, job, artifact and digest evidence;
3. use immutable Node 24-native pins for checkout, Python setup and artifact upload in every permanent workflow;
4. expose one final status-check name: `Validate complete chat-first Phase 1–7 and PCR-01–10 release`;
5. rebuild every Phase 1–7 and PCR-01–10 record without a diff;
6. pass all validators, the complete runtime suite, coverage, compilation, Ruff and strict MyPy;
7. verify issue #1 and issue #2 hosted state;
8. retain a precise branch-cleanup allowlist;
9. provide a non-destructive macOS readiness doctor that never prints secret values;
10. preserve every authorization boundary as denied.

## Manual hosted controls

The following may be marked complete only from the GitHub settings UI or equivalent authoritative evidence:

- MFA on the accountable Founder account;
- pull requests required before `main` changes;
- the final complete validation check required;
- stale approvals dismissed after new commits;
- review conversations resolved before merge;
- force pushes and deletion of `main` blocked;
- automatic deletion of merged head branches enabled.

Screenshots or a concise settings audit must be attached to issue #19. Repository files and successful past merges are not sufficient proof of current settings.

## Branch cleanup

Cleanup is restricted to exact branch names in the Workstream 4 contract.

Merged branches require an ancestry check against `main`. Explicitly superseded branches require a recorded reason. Wildcards, prefixes and deletion of `main` are prohibited. A failed or unauthorized deletion is recorded as a manual hosted-control blocker rather than ignored.

## Clean macOS environment

Run from a fresh clone:

```bash
python scripts/doctor_pre_codex_macos.py --output reports/pre-codex-macos-doctor.json
```

The doctor is non-destructive. It reports operating system, architecture, required commands, clean Git state, free disk capacity and container-runtime availability. It does not install software, reveal environment values, request credentials, activate paid services or authorize Codex.

After reviewing the redacted report, the Founder must attest that:

- the machine is a supported clean macOS environment;
- no real client files are present;
- no credentials are stored in the repository;
- no paid service or trial is required;
- the environment can be reset safely.

## Completion rule

Workstream 4 is complete only when all repository checks pass, branch cleanup is complete, issue #19 hosted controls are verified, a clean macOS report and Founder environment attestation are attached, and the Workstream 4 contract is reconciled.

Even then, Codex starts only after a separate explicit, SHA-bound Founder Phase 0 approval. Phase 1, runtime activation, Hermes activation, Northstar implementation, real client data, external actions, paid services, production deployment and autonomous merge remain prohibited.

## Rollback

Repository changes are rolled back through a reviewed revert. Hosted settings are restored through the GitHub settings UI with evidence recorded in issue #19. Environment rollback deletes only the clean synthetic clone and generated doctor report. No real client data is involved.
