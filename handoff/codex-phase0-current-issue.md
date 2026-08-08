<!-- Current operational Issue #1 body introduced by PCFA-02 and extended through PCFA-08. Synchronize only after integration. -->
# Codex Phase 0 — Validate and build the controlled local foundation

> [!CAUTION]
> **NOT AUTHORISED TO START.** A valid local single-use permit remains mandatory. `codex_start_authorized=false`.

## Current authority

Read `AGENTS.md`, then `repository/current-operational-state.json`. The current projection binds `repository/repository-visibility-and-licence-posture.json`, `repository/pcfa04-product-scope-implementation-addendum.json`, `repository/pcfa05-minimum-valuable-consulting-loop.json`, `repository/pcfa06-hermes-bounded-adoption-refresh.json`, `requirements/pcfa07-codex-implementation-backlog-reconciliation.json`, `repository/pcfa08-final-pre-codex-cross-authority-acceptance.json`, `handoff/codex-phase0-current-handoff.json`, `contracts/pcfa01-launch-control-repair.json`, and the immutable WS6.16 release.

Historical PCR/WS package records remain audit evidence only and do not override current readiness.

## Corrective packages

- **PCFA-03:** repository visibility must be `private` before launch. The current posture is proprietary/internal with **no public licence grant**. Live public visibility remains a launch blocker.
- **PCFA-04 product-scope:** 29 product and Consulting Craft requirements remain `planned_not_implemented`; no product-runtime scope is added to IMP-P0.
- **PCFA-05 Minimum Valuable Consulting Loop:** 19 stages, 15 invariants, 13 negative cases and six Founder interrupts remain `planned_not_implemented`; no workflow runtime is implemented.
- **PCFA-06 Hermes bounded-adoption refresh:** stable pin remains `v0.18.2`; all 11 Hermes capability assessments remain `planned_not_implemented`; Hermes is not activated.
- **PCFA-07 Codex implementation backlog reconciliation:** all **93** corrective obligations now map to existing IMP tasks with exact dependencies, components, blocking phase gates, evidence types and unique planned tests. Every PCFA-07 test remains `planned_not_executed`. PCFA-07 adds zero IMP phases, zero tasks and zero IMP-P0 obligations. Codex launch remains limited to **P0.1–P0.4**. PCFA-08 final repository-side cross-authority acceptance is complete on this candidate; manual launch gates remain pending.
- **PCFA-08 final cross-authority acceptance:** 18 cross-authority invariants pass; the exact cleanup plan contains 65 non-`main` refs and requires final-SHA evidence plus an independently verified live `main`-only branch inventory. This is repository-side acceptance only.

## Release and launch SHA semantics

The permanent WS6.16 `release_parent_main_sha` is historical evidence, not the future launch SHA. At permit time, the historical release parent and release-record commit must be ancestors of the exact Founder-approved current `main`; they are not required to equal that SHA. Launch evidence must bind the immutable release digest and `current_operational_state_sha256`. Any change to current authority, including PCFA-07 or PCFA-08, makes prior permit evidence stale.

## Remaining launch gates

PCFA-08 final cross-authority acceptance is complete on this repository candidate. The remaining launch gates are live private repository visibility, Issue #19 hosted controls, exact cleanup of the governed 65 non-main branches with final-SHA evidence, clean supported macOS evidence, synchronized live Issue #1/#19 bodies, exact-SHA Founder approval for P0.1–P0.4, and a valid single-use permit from `scripts/prepare_codex_phase0_launch.py`.

PCFA-08 does not authorize implementation. No IMP-P1+ implementation, runtime/Hermes activation, merge, real client data, paid services, external actions, production deployment or autonomous merge is authorized.

## Preflight

Run the current preflight commands from `handoff/codex-phase0-current-handoff.json`, including `python scripts/validate_pcfa07_backlog_reconciliation.py`, `python scripts/validate_pcfa08_final_acceptance.py`, `python scripts/prepare_codex_phase0_launch.py --self-test`, and `python scripts/require_workstream6_final_reconciliation.py`. Any failure or generated diff blocks launch.

## Live issue synchronization

Synchronize this file to live Issue #1 only after the repository changes that introduce it are integrated. Issue #2 remains closed as duplicate; Issue #19 must satisfy its current hosted-controls body and evidence rules.
