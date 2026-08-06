# 55 — WS6.3 Current Status Document Repair

## Purpose

WS6.3 removes conflicting human-facing repository states after WS6.2 and establishes one fail-closed current status across README, Start Here, Codex Kickoff, the Phase 0 validation addendum, Development Status and live issue #19.

## Canonical status

> Chat-first development is complete through CF-P1–7, PCR-01–10, WS-4, WS-5 and WS6.3; final Workstream 6 reconciliation and all manual launch gates remain pending; `codex_start_authorized=false`.

This wording distinguishes completed chat-first packages from future implementation phases and prevents a green workflow, issue assignment or branch name from being read as launch authority.

## Repairs

WS6.3:

- removes the obsolete “through PCR-05” repository status;
- removes PCR-03–08 stacked-PR merge instructions;
- removes the retired Workstream 5 status-check identity from current authority;
- prohibits branch creation before a valid permit;
- makes the permanent final WS6 release an explicit prerequisite;
- makes exact-SHA hosted, macOS and Founder evidence mandatory;
- prepares one canonical issue #19 body for live synchronization;
- preserves historical completion documents as evidence rather than rewriting them.

## Deterministic records

- Source: `configs/workstream6-current-status.yaml`
- Contract: `contracts/workstream6-current-status.json`
- Schema: `schemas/workstream6-current-status.schema.json`
- Builder: `scripts/build_workstream6_current_status.py`
- Validator: `scripts/validate_workstream6_current_status.py`
- Evidence: `reports/workstream6-current-status-evidence.md`
- Canonical issue #19 body: `handoff/codex-phase0-hosted-controls-issue-final.md`

The contract binds the exact Git blob fingerprint of every current human-authority surface. The validator independently checks those fingerprints, the canonical status phrase, required current tokens, forbidden stale-state patterns, defect closure and all authorization boundaries.

## Defect closure

WS6.3 closes exactly:

- `WS6-BLOCK-003` — current human authority documents described conflicting repository states;
- `WS6-CONSIST-008` — repository status and phase-boundary phrases were inconsistent.

`WS6-BLOCK-006` remains open because no permanent post-merge final Workstream 6 release exists yet.

## Authorization boundary

WS6.3 does not authorize Codex Phase 0, branch creation, merge, Phase 1, runtime activation, Hermes activation, Northstar product implementation, real client data, external actions, paid services, OAuth or deployment.

The implementation branch may be created only after the permanent final release, completed issue #19 evidence, clean macOS evidence, exact-SHA Founder approval and a valid local single-use permit all exist.

## Validation

The WS6.3 gate must:

1. rebuild every governed record through WS6.3 and produce no diff;
2. run all CF-P1–7, PCR-01–10, WS-4, WS-5 and preceding WS6 validators;
3. validate all six current status surfaces and their fingerprints;
4. reject every obsolete PR, status-check and pre-permit branch phrase;
5. run the launch and final-release self-tests without emitting a permit;
6. run the complete runtime suite with the 90 percent coverage floor;
7. pass Python compilation, Ruff and strict MyPy;
8. verify live issues #1, #2 and #19 and confirm the Codex branch remains absent.

## Rollback

Before merge, close the WS6.3 pull request, restore the five previous documents and issue #19 body, and delete only the WS6.3 branch. After merge, revert the WS6.3 merge as one unit and restore issue #19 from the last synchronized body. Keep every authorization flag false during rollback.

## Next package

After WS6.3 integration, the next permitted chat-first package is `WS6.4`.
