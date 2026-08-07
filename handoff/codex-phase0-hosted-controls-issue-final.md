<!-- Current canonical issue #19 body after WS6.16 permanent release. -->
# Verify hosted controls and clean environment before Codex

The canonical implementation identifier is `IMP-P0`; stable `phase0` filenames and gate keys remain compatibility identifiers only.

This issue is the authoritative human evidence record for GitHub-hosted settings, exact-allowlist historical branch cleanup and the clean macOS environment. Repository files and successful workflows cannot prove these manual gates.

> [!CAUTION]
> **Codex is not authorised to start.** Completing or closing this issue is necessary but not sufficient. A permanent final Workstream 6 release, exact-SHA Founder approval and a valid local single-use permit are separately required.

## Current repository state

- [x] CF-P1–7 and PCR-01–10 are integrated.
- [x] WS-4 repository readiness is integrated.
- [x] WS-5 predecessor launch control is integrated and retained as historical evidence.
- [x] WS6.0 baseline lock is integrated.
- [x] WS6.1 machine handoff reconciliation is integrated.
- [x] WS6.2 final launch-control reconciliation is integrated.
- [x] WS6.3 current status repair is integrated.
- [x] WS6.4 canonical authority and evidence registry is integrated.
- [x] WS6.5 phase namespace normalization is integrated.
- [x] WS6.6 required workflow identity is included in this package and becomes integrated when this package merges.
- [x] All WS6.0–WS6.16 packages are integrated.
- [x] `releases/pre-codex-final-reconciliation-2026-08-06.json` exists and passes `scripts/require_workstream6_final_reconciliation.py`.
- [x] Issue #1 is open and synchronized to `handoff/codex-phase0-issue-final.md`.
- [x] Issue #2 remains closed as duplicate.
- [x] The final required status-check identity is uniquely reserved as `Validate final pre-Codex canonical handoff and complete release`.
- [x] WS6.15 activated `.github/workflows/workstream6-final-pre-codex.yml`; hosted enforcement of the exact check remains to be evidenced below.
- [ ] `codex/phase-0-foundation` and any IMP-P0 pull request remain absent at permit issuance.

The permanent WS6.16 release and exact preparation evidence are retained in `releases/pre-codex-final-reconciliation-2026-08-06.json` and `reports/workstream6-final-evidence.md`. Manual hosted controls, branch cleanup, clean macOS, exact-SHA Founder approval and the local permit remain pending.

## Founder-hosted GitHub attestations

Attach screenshots or a concise settings audit. Every item must be verified against the then-current final `main` SHA; do not infer settings from workflow files.

- [ ] Confirm MFA is enabled for the accountable Founder account.
- [ ] Require a pull request before changes reach `main`.
- [ ] After WS6.15 activation, require exactly `Validate final pre-Codex canonical handoff and complete release` before merge.
- [ ] Dismiss stale approvals when new commits are pushed.
- [ ] Require all review conversations to be resolved before merge.
- [ ] Block force pushes to `main`.
- [ ] Block deletion of `main`.
- [ ] Enable automatic deletion of merged head branches.

Record completed evidence in a filled copy of:

```text
handoff/codex-phase0-hosted-controls-attestation.template.json
```

The attestation must reference the exact final `main` SHA, required check name, issue state and final release digest.

## Historical branch cleanup

Delete only exact branch names classified by the governed cleanup contract. Never use wildcard or prefix deletion, never delete `main`, and retain each deleted branch’s final SHA in the evidence record.

- [ ] Review the exact allowlist in `contracts/workstream4-readiness.json` and later authority-classification records.
- [ ] Confirm merged ancestry where the contract requires it.
- [ ] Delete each approved historical branch manually.
- [ ] Confirm intentionally retained active branches are explicitly classified.
- [ ] Confirm `codex/phase-0-foundation` is absent before permit issuance.
- [ ] Attach the final branch inventory.
- [ ] Record `branch_cleanup.complete=true` and the final remaining branch list in the hosted-controls attestation.

Branch deletion has no automatic rollback. Preserve exact SHAs before deleting refs.

## Clean macOS environment

After the permanent final release identifies the exact final `main` SHA, use a fresh clone of that SHA and run:

```bash
mkdir -p .local/codex-phase0-launch
python scripts/doctor_pre_codex_macos.py \
  --output .local/codex-phase0-launch/macos-doctor.json
```

The doctor is non-destructive and redacted. It does not install software, display secrets, activate services or authorise Codex.

Complete a filled copy of:

```text
handoff/codex-phase0-clean-macos-attestation.template.json
```

Then verify:

- [ ] the report shows a supported clean macOS environment;
- [ ] the clone is clean and resettable at the exact final `main` SHA;
- [ ] a supported container runtime is available;
- [ ] at least 20 GiB free disk space is available;
- [ ] no real client files are present;
- [ ] no credential values are stored in the repository or evidence;
- [ ] no paid service or trial is required for IMP-P0;
- [ ] the Founder clean-environment attestation is complete;
- [ ] the doctor report, attestation and final release reference the same SHA.

## Founder authorization and local permit

Only after every repository, hosted-control, branch-cleanup and clean-macOS item is evidenced:

1. complete `handoff/codex-phase0-founder-authorization.template.json`;
2. approve exactly IMP-P0 tasks P0.1–P0.4, branch `codex/phase-0-foundation` and a draft pull request;
3. bind approval to the exact final `main` SHA and final release digest;
4. keep merge and IMP-P1 unauthorised;
5. run:

```bash
python scripts/prepare_codex_phase0_launch.py \
  --hosted-controls .local/codex-phase0-launch/hosted-controls.json \
  --macos-report .local/codex-phase0-launch/macos-doctor.json \
  --macos-attestation .local/codex-phase0-launch/macos-attestation.json \
  --founder-approval .local/codex-phase0-launch/founder-approval.json
```

A successful verifier run writes a local, ignored, mode-`0600`, single-use permit. It does not create a branch, open or merge a pull request, activate a runtime or change GitHub settings.

- [ ] explicit Founder IMP-P0-only approval is recorded against the exact final `main` SHA;
- [ ] all final-release and evidence digests validate;
- [ ] a local single-use permit is issued;
- [ ] the permit scope remains P0.1–P0.4 only;
- [ ] merge and IMP-P1 remain unauthorised.

Create `codex/phase-0-foundation` only after the valid permit exists and only from its approved SHA.

## Completion rule

Close this issue as completed only after every hosted-control, cleanup and clean-environment item is checked with attached evidence. Closing this issue does not itself authorise Codex.

Until completed issue evidence, exact-SHA approval and permit all exist:

- `github_hosted_controls_in_issue_19_verified=false`
- `clean_macos_environment_available=false`
- `explicit_founder_phase_0_approval_received=false`
- `approved_main_sha_bound=false`
- `launch_permit_issued=false`
- `codex_start_authorized=false`

Real client data, external actions, paid services, OAuth, DNS changes, production deployment, runtime activation, Hermes activation, Northstar product implementation, autonomous merge and IMP-P1 remain prohibited.
