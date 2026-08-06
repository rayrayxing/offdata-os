# 58 — WS6.6 Required Workflow Identity

## Purpose

WS6.6 closes `WS6-CONSIST-003` by assigning one exact future branch-protection identity and proving that every predecessor check is historical or package-scoped rather than current launch authority.

## Canonical identity

- Workflow file: `.github/workflows/workstream6-final-pre-codex.yml`
- Workflow name: `Final pre-Codex canonical handoff and release`
- Job key: `validate-final-pre-codex`
- Required check: `Validate final pre-Codex canonical handoff and complete release`
- Contract: `contracts/workstream6-required-workflow-identity.json`

The check identity is case-sensitive and whitespace-sensitive. No alias, workflow display name, package validation check or predecessor check may substitute for it.

## Fail-closed reservation

WS6.6 reserves the identity but does not activate the final workflow. The canonical workflow:

- has `workflow_dispatch` only;
- has no `push`, `pull_request` or `workflow_call` trigger;
- exits non-zero with an explicit WS6.15 activation message;
- cannot be treated as proof of the permanent release;
- is not yet configured as a hosted required check.

WS6.15 must replace the reservation with the final implementation. WS6.16 must produce the permanent release record. Issue #19 must separately evidence branch-protection enforcement against the exact final `main` SHA.

## Supersession

The Workstream 4 check `Validate complete chat-first Phase 1–7 and PCR-01–10 release` and the Workstream 5 check `Validate Codex Phase 0 launch control and complete prior release` remain retained predecessor evidence only. WS6 package checks such as `Validate WS6.6 required workflow identity and complete prior components` validate chat-first packages and are not branch-protection substitutes.

## Validation

`scripts/validate_workstream6_required_workflow_identity.py`:

1. validates the JSON Schema and deterministic build;
2. scans every `.github/workflows/*.yml` and `.yaml` file;
3. proves the canonical job name occurs exactly once and only in the canonical workflow;
4. proves the canonical workflow is manual-only and explicitly fails closed;
5. verifies current authority surfaces use the exact identity;
6. rejects predecessor aliases, duplicate identities, early automatic activation, early hosted enforcement, and authorization drift;
7. runs after every required prior builder and validator in the complete gate.

PR #43 is the clean automatic-CI retry for the same WS6.6 package after GitHub Actions infrastructure failures prevented the original matrix from reaching complete terminal results.

## Completion boundary

WS6.6 closes only `WS6-CONSIST-003`. `WS6-BLOCK-006` remains open. Final reconciliation, hosted controls, branch cleanup, clean macOS, exact-SHA Founder approval, permit issuance, IMP-P0 implementation, merge and IMP-P1 remain unauthorized.

Next permitted work package: `WS6.7`.
