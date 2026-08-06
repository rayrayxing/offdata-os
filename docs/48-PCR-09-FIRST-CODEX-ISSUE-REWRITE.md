# PCR-09 — First Codex issue rewrite

## Purpose

PCR-09 replaces the two overlapping, prompt-era Phase 0 issues with one deterministic, machine-reconciled Codex work issue. The canonical target is GitHub issue #1. Issue #2 is retained as history but is superseded as a duplicate after the rewrite is applied.

This phase prepares and validates the issue contract. It does not start Codex, approve Phase 0, activate a runtime, install Hermes, implement the Northstar blueprint, enable real client data, authorise external actions, permit paid services, deploy production infrastructure or authorise merge.

## Why the rewrite is required

The original issue #1 predates PCR-04 through PCR-09 and relies on a historical comment containing obsolete repository paths and test counts. Issue #2 partially updates the objective but creates a second overlapping workstream and still does not encode the current activation sequence, exact machine prerequisites, deny-by-default operating controls, stop conditions or completion-report contract.

A single canonical issue is required so Codex receives one bounded execution summary that is generated from the same source as the machine-readable Phase 0 handoff.

## Governed assets

PCR-09 adds:

- `configs/codex-phase0-issue.yaml` — human-reviewable rewrite policy and issue identity;
- `contracts/codex-phase0-issue.json` — deterministic machine contract;
- `handoff/codex-phase0-issue.md` — exact generated GitHub issue body;
- `schemas/codex-phase0-issue.schema.json` — Draft 2020-12 schema;
- `scripts/build_pcr09_codex_issue.py` — deterministic builder and Markdown renderer;
- `scripts/validate_pcr09_codex_issue.py` — schema, semantic, stale-generation and mutation validator;
- `.github/workflows/first-codex-issue.yml` — dedicated PCR-09 and retained-boundary CI gate;
- `reports/pcr09-validation-evidence.md` — retained implementation evidence.

PCR-09 also reconciles PCR-04 and PCR-08 so `pcr09_merged_to_main` becomes a mandatory activation condition before Codex Phase 0 may start.

## Canonical issue design

The generated issue body:

1. begins with **NOT AUTHORISED TO START**;
2. states that `AGENTS.md` and `handoff/codex-phase0-handoff.json` remain authoritative;
3. lists every activation condition as an unchecked item;
4. includes the complete required read order and exact required command set;
5. preserves the P0.1–P0.4 task graph and dependency order;
6. requires a draft pull request and Founder approval before merge;
7. prohibits Phase 1, real client data, paid services, external communications, OAuth, DNS and production deployment;
8. reproduces all stop conditions and completion-report fields;
9. records issue #2 as superseded, not as an additional workstream;
10. avoids dynamic test counts and historical chat snapshots.

The issue is an execution summary, not an authority source. Any conflict is resolved in favour of `AGENTS.md` and the generated machine handoff.

## Deterministic reconciliation

The PCR-09 builder reads:

- `configs/codex-phase0-issue.yaml`;
- `configs/codex-handoff.yaml`;
- `contracts/initial-operating-controls.json`.

It requires:

- exactly four Phase 0 tasks, `P0.1` through `P0.4`;
- twenty-six read-order files;
- nine prerequisite records;
- thirty-six required commands;
- eleven prohibited actions;
- eight stop conditions;
- ten activation conditions;
- eleven completion-report fields;
- exactly one canonical issue and one superseded duplicate;
- all execution and operating boundaries to remain inactive.

The generated Markdown body is hashed and size-checked against GitHub's issue-body limit. Remote GitHub synchronisation remains separate evidence and is never inferred from repository-local validation.

## Negative validation

The validator rejects thirty-one mutation cases, including:

- changing the phase or target issue;
- removing issue #2 supersession;
- weakening Founder approval or authority precedence;
- enabling Codex, Phase 1, runtime, real-client-data, external-action, paid-service, production or merge boundaries;
- deleting a Phase 0 task or breaking dependencies;
- removing the PCR-09 activation blocker;
- removing PCR-09 build or validation commands;
- changing the draft pull-request requirement;
- removing the Phase 0 prohibition or stop condition;
- claiming remote issue synchronisation from repository evidence;
- changing the generated issue-body digest.

## Activation and evidence boundary

A valid PCR-09 contract means the issue rewrite is internally coherent and ready to synchronise. It does not prove the remote GitHub issue matches the generated body and it does not authorise implementation.

The following remain mandatory before Codex starts:

1. PCR-03 through PCR-09 are merged to `main` in governed order;
2. issue #19 hosted controls are verified;
3. a clean macOS environment is available;
4. the Founder explicitly approves Phase 0.

`codex_start_authorized=false`, `phase1_authorized=false`, `runtime_activation_authorized=false`, `hermes_activation_authorized=false`, `northstar_implementation_authorized=false` and `initial_operating_controls_activation_authorized=false` remain binding.

## Cost, data and rollback

PCR-09 requires no paid service. It uses no real client data, secrets, OAuth, provider gateway, production deployment or external communication beyond the explicitly requested GitHub issue rewrite.

Before the remote rewrite, rollback is deletion of the PCR-09 branch or closing its pull request. After the rewrite, rollback is restoring the recorded original issue #1 title/body and reopening issue #2 if the Founder determines the rewrite should be reversed. No rollback may weaken prior governance or activate Codex.
