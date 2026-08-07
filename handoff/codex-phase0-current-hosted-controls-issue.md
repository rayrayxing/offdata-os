<!-- Current operational Issue #19 body introduced by PCFA-02. Synchronize only after integration. -->
# Verify hosted controls, branch cleanup and clean macOS before Codex

This issue is the current human evidence record for GitHub-hosted controls, exact-allowlist historical branch cleanup and the clean macOS environment.

> [!CAUTION]
> Completing this issue is necessary but not sufficient to authorize Codex. Exact-SHA Founder approval and a valid local single-use permit remain separate gates. `codex_start_authorized=false` until all gates pass.

## Current authority

Use `repository/current-operational-state.json` for live machine readiness and authority. The pre-PCFA Workstream 4/5/6 status contracts and issue bodies remain package-time evidence only.

Current evidence templates:

```text
handoff/codex-phase0-current-hosted-controls-attestation.template.json
handoff/codex-phase0-current-clean-macos-attestation.template.json
handoff/codex-phase0-current-founder-authorization.template.json
```

The immutable permanent release remains:

```text
releases/pre-codex-final-reconciliation-2026-08-06.json
```

Its `release_parent_main_sha` is historical. It is not required to equal the future approved launch SHA.

## Hosted GitHub controls

Attach screenshots or a concise settings audit for the then-current repository state.

- [ ] Founder-account MFA is enabled.
- [ ] `main` requires a pull request.
- [ ] `main` requires exactly `Validate final pre-Codex canonical handoff and complete release`.
- [ ] stale approvals are dismissed after new commits.
- [ ] review conversations must be resolved.
- [ ] force pushes to `main` are blocked.
- [ ] deletion of `main` is blocked.
- [ ] merged head branches are automatically deleted.

The hosted-controls attestation must bind:

- the exact then-current approved `main` SHA;
- the exact permanent WS6.16 release SHA-256;
- the exact SHA-256 of `repository/current-operational-state.json`;
- the exact current Issue #1 body SHA-256;
- the exact current Issue #19 body SHA-256;
- the required status-check name;
- the final branch inventory.

## Historical branch cleanup

Delete only exact branch names explicitly classified for cleanup. Preserve every deleted branch's final SHA as evidence. Never use wildcard or prefix deletion.

- [ ] review the governed exact allowlist and retained branch evidence;
- [ ] verify ancestry where required;
- [ ] preserve final SHAs before deletion;
- [ ] delete only approved historical refs;
- [ ] confirm `codex/phase-0-foundation` is absent before permit issuance;
- [ ] confirm no IMP-P0 pull request is open;
- [ ] capture the final branch inventory;
- [ ] record `branch_cleanup.complete=true` with `remaining_branches=["main"]` in the hosted-controls attestation.

Branch deletion is irreversible at the ref level; retaining exact SHAs is the rollback evidence.

## Clean macOS environment

Use a fresh clone of the exact intended current `main` SHA and run:

```bash
mkdir -p .local/codex-phase0-launch
python scripts/doctor_pre_codex_macos.py \
  --output .local/codex-phase0-launch/macos-doctor.json
```

Then complete `handoff/codex-phase0-current-clean-macos-attestation.template.json`.

Verify:

- [ ] supported macOS and architecture checks pass;
- [ ] the clone is clean and on `main` at the intended exact SHA;
- [ ] the container runtime and required local tooling are available;
- [ ] at least the required free disk threshold is available;
- [ ] no real client files are present;
- [ ] no repository credentials are present;
- [ ] no paid service or trial is required for IMP-P0;
- [ ] the Founder environment attestation is complete.

The clean-macOS evidence must bind the exact current approved `main` SHA, permanent-release digest and current-operational-state digest. The permanent release's historical parent SHA does **not** need to equal the approved current `main` SHA; its parent and record commit must instead be ancestors of that current SHA.

## Founder authorization and permit

After the hosted-control, cleanup and clean-macOS evidence is complete:

1. synchronize live Issue #1 and Issue #19 to their current repository bodies;
2. complete `handoff/codex-phase0-current-founder-authorization.template.json`;
3. approve exactly IMP-P0 tasks P0.1–P0.4 against the exact then-current `main` SHA;
4. keep merge and IMP-P1 unauthorized;
5. run the real permit verifier.

```bash
python scripts/prepare_codex_phase0_launch.py \
  --hosted-controls .local/codex-phase0-launch/hosted-controls.json \
  --macos-report .local/codex-phase0-launch/macos-doctor.json \
  --macos-attestation .local/codex-phase0-launch/macos-attestation.json \
  --founder-approval .local/codex-phase0-launch/founder-approval.json
```

A successful run writes a local, ignored, mode-`0600`, single-use permit. It does not create a branch or authorize merge.

## Completion rule

Close Issue #19 as completed only after all hosted-control, cleanup and clean-environment evidence is complete and this live issue body matches `handoff/codex-phase0-current-hosted-controls-issue.md` exactly.

At permit time the verifier requires:

- Issue #1 open with the current Issue #1 body;
- Issue #2 closed as duplicate;
- Issue #19 closed as completed with this current body;
- only `main` remaining before Codex branch creation;
- no Codex Phase 0 branch or open pull request;
- exact-SHA Founder IMP-P0-only approval;
- all evidence bound to the permanent-release digest and current-operational-state digest.

Until then, all implementation and activation boundaries remain false.
