# Current operational state

This document is the human-readable companion to `repository/current-operational-state.json`.

## Current status

The chat-first specification and reconciliation programme is complete through WS6.16, the permanent Workstream 6 release is valid, and PCFA-01 repairs the real Codex Phase 0 launch semantics. PCFA-02 separates retained package-time snapshots from the live operational projection.

`codex_start_authorized=false`.

No Codex branch, IMP-P0 implementation, merge, IMP-P1, runtime/Hermes activation, real client data, paid service, OAuth, DNS change, production deployment or external action is authorized by this state.

## Current machine authority

For current operational decisions, use this order after `AGENTS.md`:

1. `repository/current-operational-state.json` — sole live machine readiness and authority projection;
2. `handoff/codex-phase0-current-handoff.json` — current machine execution handoff;
3. `contracts/pcfa01-launch-control-repair.json` — corrected release/launch SHA semantics;
4. `handoff/codex-phase0-current-issue.md` — current Issue #1 body to synchronize after integration;
5. `handoff/codex-phase0-current-hosted-controls-issue.md` — current Issue #19 body to synchronize after integration;
6. `releases/pre-codex-final-reconciliation-2026-08-06.json` — immutable WS6.16 release evidence;
7. `scripts/prepare_codex_phase0_launch.py` — fail-closed launch-permit entrypoint.

The current evidence templates use the neutral `handoff/codex-phase0-current-*` names.

## Historical package snapshots

The following remain valid evidence of their own package boundaries, but their embedded readiness, next-phase, blocker or authority labels must not be interpreted as current operational state:

- `contracts/codex-phase0-launch-control.json` — WS6.2;
- `contracts/workstream6-final-launch-control.json` — WS6.2;
- `contracts/workstream6-current-status.json` — WS6.3;
- `repository/canonical-authority-registry.json` — WS6.4;
- `handoff/codex-phase0-handoff.json` — PCR-04/WS6.1 successor snapshot;
- `handoff/codex-phase0-issue-final.md` — WS6.2 generated Issue #1 body;
- `handoff/codex-phase0-hosted-controls-issue-final.md` — pre-PCFA Issue #19 body;
- WS6.2 and PCFA-01 evidence-template snapshots named in the current operational-state contract.

They are preserved rather than rewritten so deterministic package reconstruction and audit history remain intact.

## Release versus launch SHA

The permanent WS6.16 record stores `release_parent_main_sha`, meaning the exact integrated `main` immediately before the permanent release-record commit. That historical SHA is not the future launch SHA.

At permit time:

- the release parent must be an ancestor of the approved launch `main`;
- the permanent release-record commit must be an ancestor of the approved launch `main`;
- both historical release SHAs are excluded from current-launch SHA equality;
- Founder approval, hosted-controls evidence, clean-macOS evidence, doctor `HEAD`, local `HEAD` and remote `main` must all bind one exact current `main` SHA;
- all launch evidence must bind the immutable release digest and the digest of `repository/current-operational-state.json`.

## Remaining gates

Before a permit can exist, all of the following must be independently evidenced against the then-current exact `main` SHA:

1. GitHub hosted controls in Issue #19;
2. exact-allowlist historical branch cleanup, ending with only `main` before launch;
3. clean supported macOS doctor evidence and Founder environment attestation;
4. explicit Founder authorization for IMP-P0 tasks P0.1–P0.4 only;
5. live Issue #1 and Issue #19 bodies synchronized to the current files;
6. a successful real run of `scripts/prepare_codex_phase0_launch.py` producing the local single-use permit.

The permit becomes stale after any approved-main, permanent-release, current-operational-state, current issue-body, evidence, required-check or scope change.

## Integration boundary

PCFA-02 is stacked on PCFA-01 while PCFA-01 remains unmerged. Current Issue #1 and Issue #19 files must not be synchronized to GitHub until the repository changes that introduce them are integrated. Until then, the live issue-body mismatch is an intentional fail-closed condition.
