# WS6.16 — Permanent release record

> [!CAUTION]
> **THE PERMANENT RELEASE DOES NOT EXIST YET.** This package prepares the only allowed post-merge finalization path. It must not fabricate an exact-main or hosted-evidence binding while WS6.8–WS6.15 remain unintegrated.

- Exact WS6.15 predecessor: `1361fff88bd08ae16218673337621571a7d315c6` (PR #56).
- Observed integrated `main`: `8ad0ea95b8d01c83347161e4ccf893f1844a219d`, through `WS6.15`.
- The permanent release path must remain absent in this preparation pull request.
- The future release record binds the exact integrated parent-main SHA, the exact successful WS6.16 preparation merge reference, final-check run/job/artifact IDs, and the independently verified artifact digest.
- Predecessor evidence is historical only and cannot substitute for current final evidence.
- The release record closes `WS6-BLOCK-006` and `WS6-CONSIST-010` only after those bindings are real and validated.
- `WS6-CONSIST-006` remains a separate post-merge manual branch-cleanup gate.
- Issue #19, clean macOS, Founder approval and a valid local single-use permit remain separate gates.
- `codex_start_authorized=false`.

## Required finalization sequence

1. Integrate the predecessor stack through the WS6.16 preparation package with explicit Founder merge approval.
2. Obtain a successful exact WS6.16 preparation merge-reference run and independently verify its retained artifact digest.
3. Observe the exact integrated `main` SHA after the preparation package lands.
4. Create `release/ws616-permanent-release-record` from that exact SHA.
5. Run `scripts/finalize_workstream6_permanent_release.py` with the exact run/job/artifact/digest evidence.
6. Review the generated permanent release, final evidence report and final defect ledger.
7. Merge that small release-record change only with explicit Founder approval.

## Current state

- Release machinery prepared: `true`.
- Permanent release record complete: `false`.
- Final reconciliation complete: `false`.
- All blocking defects closed: `false`.
- WS6.16 complete: `false`.
