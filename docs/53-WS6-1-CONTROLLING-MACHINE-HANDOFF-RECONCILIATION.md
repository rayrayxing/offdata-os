# WS6.1 — Controlling machine handoff reconciliation

## Purpose

WS6.1 repairs the controlling Codex Phase 0 machine handoff after the WS6.0
baseline proved that the PCR-04 source and validator stopped at the PCR-09-era
state.

The exact base is the merged WS6.0 `main` commit
`5c80cea82aa663cbe0a690e3f8f02504d121bea1`.

`AGENTS.md` remains controlling. This package authorizes no Codex work.

## Closed defects

WS6.1 closes exactly:

- `WS6-BLOCK-001` — stale handoff source and generated machine contract;
- `WS6-BLOCK-002` — validator that positively enforced the stale boundary.

The remaining blocking defects are `WS6-BLOCK-003` through
`WS6-BLOCK-006` and remain assigned to later Workstream 6 packages.

## Reconciled authority

The canonical source remains `configs/codex-handoff.yaml`. It deterministically
generates `handoff/codex-phase0-handoff.json` through
`scripts/build_pcr04_codex_handoff.py`.

The PCR-04 entrypoints now delegate to the WS6.1 reconciled builder and
validator while preserving their historical command names:

- `scripts/build_ws61_codex_handoff.py`;
- `scripts/validate_ws61_codex_handoff.py`.

The governed WS6.1 package is recorded in:

- `configs/workstream6-handoff-reconciliation.yaml`;
- `contracts/workstream6-handoff-reconciliation.json`;
- `schemas/workstream6-handoff-reconciliation.schema.json`;
- `reports/workstream6-handoff-reconciliation-evidence.md`.

## Required predecessor coverage

The handoff now includes all repository-side records through:

- CF-P1 through CF-P7;
- PCR-01 through PCR-10;
- Workstream 4 hosted-control preparation;
- Workstream 5 launch control;
- Workstream 6 baseline lock and WS6.1 handoff reconciliation.

It contains 14 ordered prerequisite records, 45 read-order paths, 49 required
launch commands and 15 ordered activation conditions.

## Final Workstream 6 gate

Repository-side completion of WS6.1 is not final Workstream 6 completion.
The activation sequence now requires:

`workstream6_final_reconciliation_merged_to_main`

The handoff also requires:

```text
python scripts/require_workstream6_final_reconciliation.py
```

The command fails closed until the final Workstream 6 release record exists and
proves exact-main binding, tested-merge-reference binding and closure of all
blocking defects. Its `--self-test` mode proves incomplete evidence is rejected
without claiming the live gate is complete.

## Permit and activation boundary

A valid Codex Phase 0 launch permit is now an explicit activation condition:

`valid_codex_phase0_launch_permit_issued`

The permit does not replace any other requirement. Codex may start only after
all of the following are independently true:

1. final Workstream 6 reconciliation is merged and evidenced;
2. issue #19 hosted controls and exact branch cleanup are verified;
3. the clean macOS environment is verified;
4. explicit Founder approval is bound to the exact current `main` SHA;
5. the Workstream 5 launch verifier issues a valid single-use permit.

Until then:

- `final_workstream6_gate_complete=false`;
- `launch_permit_issued=false`;
- `codex_start_authorized=false`.

## P0.3 regression scope

P0.3 acceptance now requires every CF-P1–7, PCR-01–10, Workstream 4,
Workstream 5 and final Workstream 6 gate to remain green. It also requires the
valid permit and exact approved `main` SHA to be verified before creation of
`codex/phase-0-foundation`.

## Validation

The WS6.1 workflow must:

- rebuild all governed records without diff;
- validate every prior component and both WS6.0 and WS6.1;
- reject stale activation, prerequisite, read-order, command and P0.3 mutations;
- prove the final Workstream 6 gate fails closed in self-test;
- run the complete 247-test runtime suite with at least 90 percent coverage;
- pass compilation, Ruff and strict MyPy;
- verify issues #1, #2 and #19 and confirm the Codex branch remains absent.

The dedicated check is:

`Validate WS6.1 controlling machine handoff and complete prior components`

## Scope boundary

WS6.1 does not:

- rewrite the final canonical issue body;
- rebind the Workstream 5 launch verifier;
- close issue #19;
- delete historical branches;
- issue a launch permit;
- create `codex/phase-0-foundation`;
- implement Next.js, FastAPI, PostgreSQL, object storage or deliverable renderers;
- use paid services or real client data;
- authorize Phase 0 implementation, Phase 0 merge or Phase 1.

## Completion and next action

WS6.1 is complete only when the exact PR merge reference passes every required
check and the reconciled tree is merged to `main`.

The next permitted work package is `WS6.2` — reconcile final launch control and
the canonical issue/permit binding.

## Rollback

Before merge, close the WS6.1 pull request and delete only
`governance/workstream6-handoff-reconciliation`.

After merge, revert the WS6.1 merge as one unit. Restore the WS6.0 handoff
baseline, preserve all retained evidence and keep Codex unauthorized.
