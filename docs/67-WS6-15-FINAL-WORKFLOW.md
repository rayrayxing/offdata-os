# WS6.15 — Final workflow

> [!CAUTION]
> **WORKFLOW ACTIVATION IS NOT CODEX AUTHORIZATION.** WS6.15 activates the exact final check while keeping the permanent release, manual gates, permit, IMP-P0 implementation and merge authority false.

- Exact predecessor: `272450f7aa4ac1c5c94c644bd9e1bbaa015685d1` (WS6.14 / PR #55).
- Current integrated main remains `cb2bffe74e62804250ac36168c4206cb8b9d021a` through `WS6.7`.
- Final check: `Validate final pre-Codex canonical handoff and complete release`.
- Automatic triggers: pull requests, pushes to `main`, and manual dispatch.
- Exact WS6.15 activation PR may pass without a permanent release only when its branch, base branch and base SHA all match the governed exception and the permanent release is absent.
- Every other run requires `scripts/require_workstream6_final_reconciliation.py` to pass.
- After WS6.15 integration, `main` therefore fails closed until WS6.16 creates and validates the permanent release.
- Hosted branch protection remains a separate issue #19 manual gate.
- `codex_start_authorized=false`.

## Remaining defects

- `WS6-BLOCK-006`
- `WS6-CONSIST-006`
- `WS6-CONSIST-010`

## Next package

`WS6.16` — permanent post-merge release and final evidence reconciliation.
