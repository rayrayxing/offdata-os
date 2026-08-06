# WS6.2 — Final launch-control reconciliation

## Purpose

WS6.2 replaces the Workstream 5-era launch authority with a final Workstream 6-aware contract without authorizing Codex.

The package begins from exact merged `main` `a3fb3ea21029f01c52bc8e871dd7bcb284a31f7c` and closes only:

- `WS6-BLOCK-004` — the launch verifier could not prove final Workstream 6 inclusion;
- `WS6-BLOCK-005` — issue #1 and permit digests were still bound to the Workstream 5 body.

## Controlling authority after WS6.2

- `AGENTS.md` remains controlling.
- `handoff/codex-phase0-handoff.json` remains the machine execution contract.
- `contracts/codex-phase0-launch-control.json` is the controlling final launch-control contract.
- `contracts/workstream6-final-launch-control.json` records this work package.
- `handoff/codex-phase0-issue-final.md` is the only generated issue body accepted by the launch verifier.
- `scripts/prepare_codex_phase0_launch.py` is the local, fail-closed permit verifier.
- `scripts/require_workstream6_final_reconciliation.py` is an independent prerequisite.

The PCR-09, PCR-10 and Workstream 5 issue bodies and the Workstream 5 durable release remain historical, non-controlling evidence.

## Final release gate

A permit cannot be produced unless:

1. `releases/pre-codex-final-reconciliation-2026-08-06.json` exists;
2. its release ID is `PRE-CODEX-FINAL-RECONCILIATION-2026-08-06`;
3. every blocking Workstream 6 defect is closed;
4. final reconciliation is complete;
5. exact `main` and tested merge reference are bound;
6. the release itself keeps `codex_start_authorized=false`;
7. its integrated `main` SHA equals every evidence bundle, local HEAD and remote `main`.

Until WS6.16 creates that permanent post-merge record, real launch preparation must fail.

## Final issue and status-check binding

Issue #1 must remain open and match `handoff/codex-phase0-issue-final.md` exactly.

The following Workstream 5-era digest is explicitly rejected:

```text
9f5bff38d973405be03d5b78e4ceb29280e77e1fd89a972c9d3fbb9e43df2791
```

The hosted-controls attestation must name the future final required check exactly:

```text
Validate final pre-Codex canonical handoff and complete release
```

The Workstream 5 and WS6.1 job names are historical and cannot satisfy the final launch verifier.

## Permit binding

The single-use local permit now binds digests for:

- the final launch-control contract;
- the final canonical issue body;
- the permanent final Workstream 6 release;
- hosted controls;
- macOS doctor report;
- macOS attestation;
- Founder authorization.

The permit is invalid after any `main`, final release, issue-body, required-check, evidence or scope change.

## Reconciled templates

All launch templates use schema version `2.0.0`.

The hosted-controls template contains `required_status_check_name`. The launch acknowledgement contains `final_workstream6_release_sha256`.

## Scope and boundaries

Only P0.1–P0.4 may eventually be authorized. The required branch remains `codex/phase-0-foundation`; the pull request must remain draft.

WS6.2 does not:

- create a permit;
- create the Codex branch;
- authorize implementation or merge;
- authorize Phase 1;
- activate a runtime or Hermes;
- enable real client data, paid services, OAuth, DNS, production or external communication.

## Validation

The WS6.2 gate must:

- regenerate the final contract, issue body, templates and package record without diff;
- validate JSON Schema and semantic invariants;
- reject stale Workstream 5 issue and status-check identities;
- reject missing or stale final Workstream 6 evidence;
- reject widened scope or authorization;
- run the launch-verifier self-test;
- run every prior CF, PCR and Workstream builder and validator;
- run all runtime tests with at least 90 percent coverage;
- compile Python and pass Ruff and strict MyPy;
- verify issue #1 final-body sync, issue #2 duplicate closure, issue #19 fail-closed state and Codex-branch absence.

## Completion and next work

WS6.2 closes exactly blockers 004 and 005. Blockers 003 and 006 remain open.

The next permitted chat-first work package is **WS6.3 — reconcile current human authority and status documentation**.

## Rollback

Before merge, close the WS6.2 pull request, restore issue #1 from the Workstream 5 body and delete only `governance/workstream6-final-launch-control`.

After merge, revert WS6.2 as one unit and restore the Workstream 5 contract, verifier, templates and issue body together. Every authorization flag must remain false.
