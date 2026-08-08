<!-- Current operational Issue #19 body introduced by PCFA-02 and extended through PCFA-08. Synchronize only after integration. -->
# Verify hosted controls, private repository visibility, branch cleanup and clean macOS before Codex

This issue is the current human evidence record for repository visibility, GitHub-hosted controls, exact-allowlist historical branch cleanup and the clean macOS environment.

> [!CAUTION]
> Completing this issue is necessary but not sufficient to authorize Codex. Exact-SHA Founder approval and a valid local single-use permit remain separate gates. `codex_start_authorized=false` until all gates pass.

## Current authority

Use `repository/current-operational-state.json` for live machine readiness, `repository/pcfa08-final-pre-codex-cross-authority-acceptance.json` for final repository-side cross-authority acceptance and the exact cleanup plan, and `repository/repository-visibility-and-licence-posture.json` for the current visibility/licence posture. The pre-PCFA Workstream 4/5/6 status contracts, the WS6.13 licence placeholder and earlier issue bodies remain package-time evidence only.

PCFA-03 requires private/internal development with no public licence grant. Public distribution, open-source distribution and external contributions remain unauthorized.

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

## Repository visibility and hosted GitHub controls

Attach screenshots or a concise settings audit for the then-current repository state.

- [ ] repository visibility is `private`;
- [ ] Founder-account MFA is enabled;
- [ ] `main` requires a pull request;
- [ ] `main` requires exactly `Validate final pre-Codex canonical handoff and complete release`;
- [ ] stale approvals are dismissed after new commits;
- [ ] review conversations must be resolved;
- [ ] force pushes to `main` are blocked;
- [ ] deletion of `main` is blocked;
- [ ] merged head branches are automatically deleted.

The hosted-controls attestation must bind:

- `repository_visibility_private=true`;
- the exact then-current approved `main` SHA;
- the exact permanent WS6.16 release SHA-256;
- the exact SHA-256 of `repository/current-operational-state.json` in `current_operational_state_sha256`;
- the exact current Issue #1 body SHA-256;
- the exact current Issue #19 body SHA-256;
- the required status-check name;
- the final branch inventory and its canonical SHA-256 digest.

The launch verifier independently queries live GitHub repository metadata. An attestation cannot override a live public repository state.

## Licence/distribution boundary

The current posture is private/internal development with no public licence grant and no selected open-source licence. The absence of a repository `LICENSE` file is intentional and does not grant reuse rights. Public/open-source distribution or external contributions require a future explicit Founder decision, licence ADR, dependency-licence compatibility review and legal review if material.

## Historical branch cleanup

PCFA-08 governs an exact allowlist of **65** non-`main` branches to remove only after dependency-order integration. Delete only exact branch names explicitly classified for cleanup. Preserve every deleted branch's final SHA as evidence. Never use wildcard or prefix deletion.

- [ ] review the governed exact allowlist and retained branch evidence;
- [ ] verify ancestry where required;
- [ ] preserve final SHAs before deletion and record all 65 entries under `branch_cleanup.deleted_branches`;
- [ ] delete only approved historical refs;
- [ ] confirm `codex/phase-0-foundation` is absent before permit issuance;
- [ ] confirm no IMP-P0 pull request is open;
- [ ] independently confirm the live GitHub branch inventory contains only `main`;
- [ ] capture the final branch inventory;
- [ ] record `branch_cleanup.complete=true` with `remaining_branches=["main"]` in the hosted-controls attestation.

Each `deleted_branches` item must record the exact branch name, its final 40-hex SHA and a governed disposition (`merged`, `obsolete` or `superseded`). `branch_cleanup.inventory_sha256` must equal the SHA-256 of the canonical sorted live branch-name JSON captured after cleanup. The launch verifier checks exact coverage of all 65 PCFA-08 cleanup refs and independently queries GitHub for the final live inventory. Branch deletion is irreversible at the ref level; retaining exact SHAs is the rollback evidence.

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

The clean-macOS evidence must bind the exact current approved `main` SHA, permanent-release digest and `current_operational_state_sha256`. The permanent release's historical parent SHA does **not** need to equal the approved current `main` SHA; its parent and record commit must instead be ancestors of that current SHA.

## Founder authorization and permit

After repository visibility, hosted-control, cleanup and clean-macOS evidence is complete:

1. synchronize live Issue #1 and Issue #19 to their current repository bodies;
2. complete `handoff/codex-phase0-current-founder-authorization.template.json`;
3. approve exactly IMP-P0 tasks P0.1–P0.4 against the exact then-current `main` SHA;
4. keep merge, IMP-P1 and public distribution unauthorized;
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

Close Issue #19 as completed only after all repository-visibility, hosted-control, cleanup and clean-environment evidence is complete and this live issue body matches `handoff/codex-phase0-current-hosted-controls-issue.md` exactly.

At permit time the verifier requires:

- live repository visibility is `private`;
- Issue #1 open with the current Issue #1 body;
- Issue #2 closed as duplicate;
- Issue #19 closed as completed with this current body;
- only `main` remaining before Codex branch creation;
- no Codex Phase 0 branch or open pull request;
- exact-SHA Founder IMP-P0-only approval;
- all evidence bound to the permanent-release digest and `current_operational_state_sha256`.

Until then, all implementation, distribution and activation boundaries remain false.
