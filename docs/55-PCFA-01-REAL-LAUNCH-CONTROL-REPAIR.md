# 55 — PCFA-01 Real Launch-Control Repair

## Status

PCFA-01 is a post-WS6 corrective package. It does not reopen, rewrite or renumber WS6.16. The permanent WS6.16 release remains immutable evidence. `codex_start_authorized=false` throughout this package.

## Defect repaired

The pre-PCFA launch verifier treated the final Workstream 6 release SHA as if it were the exact current launch `main` SHA. That is incompatible with the permanent WS6.16 schema-v2 release, whose field `release_parent_main_sha` intentionally records the exact integrated `main` **before** the permanent release-record commit.

The prior real permit path therefore required a legacy `integrated_main_sha` or `main_sha` field that the valid WS6.16 record does not contain, then attempted to include that value in the equality set for current launch evidence.

## Correct semantics

PCFA-01 separates four identities:

1. `release_parent_main_sha` — historical exact integrated main before the permanent release-record commit;
2. permanent release-record commit — the commit that introduced the immutable WS6.16 record;
3. permanent release SHA-256 — immutable release content identity;
4. `approved_main_sha` — exact current `main` from which Codex Phase 0 may later be launched.

The permit verifier now requires:

- the actual WS6.16 schema-v2 record to validate without any legacy launch-main field;
- the release parent to be an ancestor of the approved launch main;
- the permanent release-record commit to be an ancestor of the approved launch main;
- the historical release parent and release-record commit to be excluded from current-launch SHA equality;
- Founder approval, hosted controls, clean-macOS attestation, macOS doctor git head, local HEAD and remote `main` to bind one exact current launch SHA;
- hosted controls, clean-macOS attestation and Founder authorization to bind the same permanent release digest;
- hosted controls and Founder authorization to bind the canonical Issue #1 body digest;
- hosted controls to bind the live Issue #19 body digest;
- Codex branch and open Codex PR to remain absent before permit issuance.

## Corrective assets

PCFA-01 adds:

- `contracts/pcfa01-launch-control-repair.json`;
- corrected 2.1 evidence templates under `handoff/pcfa01-*`;
- a 2.1 launch-permit schema carrying both historical release identities and the corrective-contract digest;
- `scripts/validate_pcfa01_launch_control.py`;
- expanded launch self-tests using the actual permanent WS6.16 record plus synthetic descendant/pre-release cases.

The WS6.2 launch-control contract and generated WS6.2 templates remain retained package snapshots. PCFA-02 is responsible for current-authority projection cleanup and canonical handoff/Issue wording reconciliation; PCFA-01 repairs the executable permit path without rewriting historical WS6 evidence.

## Required regression coverage

The launch self-test must accept one valid synthetic descendant bundle and reject mutations covering at least:

- all hosted-control attestations;
- incomplete or non-exclusive branch cleanup;
- stale status-check identity;
- doctor failure, dirty state or wrong branch;
- missing Founder authorization, scope drift, merge or Phase 1 authority;
- current launch SHA drift in every evidence source, local HEAD or remote main;
- permanent release digest drift in every launch evidence source;
- canonical Issue #1 digest drift;
- live Issue #19 body drift after attestation;
- missing release-parent ancestry;
- missing permanent release-record ancestry;
- use of the pre-release parent as the launch main;
- release-parent/release-record identity collapse;
- missing or invalid permanent release state;
- existing Codex branch or open Codex PR;
- corrective-contract mutations that re-enable the original bug or authorize implementation.

The actual repository WS6.16 record must be exercised directly and must pass despite containing neither `integrated_main_sha` nor `main_sha`.

## Phase boundary

PCFA-01 does not authorize:

- Codex Phase 0 implementation;
- creation of `codex/phase-0-foundation`;
- merge of an IMP-P0 pull request;
- IMP-P1;
- runtime or Hermes activation;
- real client data;
- paid services, OAuth, DNS or external actions.

Completion means the corrective branch passes the inherited full repository validation, the permanent release gate, PCFA-01 validation, expanded launch self-test, compilation, Ruff, strict MyPy and the existing runtime coverage floor, then is presented as a draft pull request for Founder review. Merge remains a separate Founder-controlled action.
