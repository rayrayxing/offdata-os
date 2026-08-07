# Current operational state

This document is the human-readable companion to `repository/current-operational-state.json`.

## Current status

The chat-first specification and reconciliation programme is complete through WS6.16, the permanent Workstream 6 release is valid, PCFA-01 repairs the real Codex Phase 0 launch semantics, PCFA-02 separates retained package-time snapshots from the live operational projection, PCFA-03 resolves repository visibility/licence posture, and PCFA-04 defines the missing product-scope implementation addendum.

All PCFA-04 product requirements remain `planned_not_implemented`. PCFA-04 does not widen IMP-P0 or claim product/runtime implementation.

`codex_start_authorized=false`.

No Codex branch, IMP-P0 implementation, merge, IMP-P1, runtime/Hermes activation, public distribution, open-source distribution, external contribution, real client data, paid service, OAuth, DNS change, production deployment or external action is authorized by this state.

## Current machine authority

For current operational decisions, use this order after `AGENTS.md`:

1. `repository/current-operational-state.json` — sole live machine readiness and authority projection;
2. `repository/repository-visibility-and-licence-posture.json` — current PCFA-03 private/internal repository and licence posture;
3. `repository/pcfa04-product-scope-implementation-addendum.json` — current PCFA-04 product-scope implementation obligations;
4. `docs/71-PCFA-04-PRODUCT-SCOPE-IMPLEMENTATION-ADDENDUM.md` — human-readable product-scope addendum;
5. `handoff/codex-phase0-current-handoff.json` — current machine execution handoff;
6. `contracts/pcfa01-launch-control-repair.json` — corrected release/launch SHA semantics;
7. `handoff/codex-phase0-current-issue.md` — current Issue #1 body to synchronize after integration;
8. `handoff/codex-phase0-current-hosted-controls-issue.md` — current Issue #19 body to synchronize after integration;
9. `releases/pre-codex-final-reconciliation-2026-08-06.json` — immutable WS6.16 release evidence;
10. `scripts/prepare_codex_phase0_launch.py` — fail-closed launch-permit entrypoint.

The current evidence templates use the neutral `handoff/codex-phase0-current-*` names.

## Repository visibility and licence posture

PCFA-03 resolves the current policy posture as follows:

- required GitHub repository visibility before Codex launch and IMP-P0 implementation: `private`;
- a live public repository is a launch blocker;
- the launch verifier independently queries GitHub repository metadata and cannot be overridden by an attestation;
- licence mode: `no_public_licence_grant_proprietary_internal`;
- selected open-source licence: none;
- implicit licence grant: false;
- public/open-source distribution: unauthorized;
- external contributions and client distribution: unauthorized;
- third-party dependencies retain their own licences.

The repository was observed as public when PCFA-03 was prepared on 2026-08-07. That observation is historical evidence only; it does not satisfy the private-visibility gate. The actual hosted setting must be changed to private and independently verified before a launch permit can exist.

The current private/internal posture intentionally does not require a repository `LICENSE` file. Any future public or open-source posture requires explicit Founder approval, a licence ADR, dependency-licence compatibility review, and legal review if material.

## PCFA-04 product-scope implementation addendum

PCFA-04 defines 14 product areas and 29 explicit requirements, all `planned_not_implemented`. The package covers:

- Mandate Intake Workbench;
- explicit Engagement Workspace;
- Quality and Assurance Console;
- Implementation and Benefits Workspace;
- broader ingestion formats and native provenance locators;
- 100% approved canonical-library source accounting;
- 15 Consulting Craft `CQ-*` requirements;
- broader golden-output coverage;
- Office round-trip reconciliation;
- Founder/house-style profile;
- deliverable asset-rights provenance;
- Founder attention burden metrics;
- explicit deliverable variants;
- review/change-request workflow.

The requirements are assigned to existing IMP-P1–P12 integration points. No new product-runtime work is added to IMP-P0. CRM, origination and Methodology Radar remain required to feed the same canonical mandate/engagement/method state rather than introducing new stores.

PCFA-05 still must define the Minimum Valuable Consulting Loop machine contract. PCFA-07 still must reconcile every PCFA-04 requirement into exact implementation-task, planned-test, evidence, dependency and blocking-phase-gate registrations.

The current operational state directly binds the SHA-256 of `repository/pcfa04-product-scope-implementation-addendum.json`, and the launch entrypoint rejects a missing, permissive or drifted PCFA-04 record.

## Historical package snapshots

The following remain valid evidence of their own package boundaries, but their embedded readiness, next-phase, blocker, authority or licence-decision labels must not be interpreted as current operational state:

- `contracts/codex-phase0-launch-control.json` — WS6.2;
- `contracts/workstream6-final-launch-control.json` — WS6.2;
- `contracts/workstream6-current-status.json` — WS6.3;
- `repository/canonical-authority-registry.json` — WS6.4;
- `configs/workstream6-phase0-licence-decision-placeholder.yaml` — WS6.13 licence placeholder;
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
- all launch evidence must bind the immutable release digest and the digest of `repository/current-operational-state.json`;
- the current operational-state digest transitively binds the exact PCFA-03 repository-posture digest;
- current authority directly binds the exact PCFA-04 product-scope addendum digest.

## Remaining gates

Before a permit can exist, all of the following must be independently evidenced against the then-current exact `main` SHA:

1. remaining chat-first PCFA packages are integrated and current authority regenerated;
2. live GitHub repository visibility is `private`;
3. GitHub hosted controls in Issue #19;
4. exact-allowlist historical branch cleanup, ending with only `main` before launch;
5. clean supported macOS doctor evidence and Founder environment attestation;
6. explicit Founder authorization for IMP-P0 tasks P0.1–P0.4 only;
7. live Issue #1 and Issue #19 bodies synchronized to the current files;
8. a successful real run of `scripts/prepare_codex_phase0_launch.py` producing the local single-use permit.

The permit becomes stale after any approved-main, permanent-release, current-operational-state, repository-posture, product-scope, current issue-body, evidence, required-check or scope change.

## Integration boundary

PCFA-04 is stacked on PCFA-03, which is stacked on PCFA-02 and PCFA-01. The current Issue #1 and Issue #19 files must not be synchronized to GitHub until the repository changes that introduce them are integrated. Until then, live issue-body mismatch and public repository visibility are intentional fail-closed conditions.
