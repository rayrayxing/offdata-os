# 20 — Development Status

## Snapshot

Date: 2026-08-06

**Chat-first development is complete through CF-P1–7, PCR-01–10, WS-4, WS-5 and WS6.3; final Workstream 6 reconciliation and all manual launch gates remain pending; `codex_start_authorized=false`.**

This is the current human-readable status document. Historical phase-completion documents, PR descriptions, issue comments and reports remain evidence for their own packages but do not supersede this snapshot.

## Completed chat-first packages

### CF-P1–7

The chat-first package contains the governed machine contracts, bounded agent system, restricted AI-audit oracle, deliverable semantic model, primary engagement fixtures, knowledge-ingestion intelligence and security/regionalisation controls. These are design and deterministic implementation inputs, not completed product implementation phases.

### PCR-01–10

The full reconciliation sequence is integrated:

- canonical release reconciliation;
- test identity and referential-integrity repair;
- repository and governance hygiene;
- machine-readable Codex handoff;
- runtime adapter contracts;
- Hermes compatibility;
- Northstar integration blueprint;
- initial operating controls;
- canonical Codex issue preparation;
- pre-Codex release and quality acceptance.

### WS-4 and WS-5

Repository-readiness, hosted-control evidence structures, clean-macOS doctor tooling and the predecessor launch-control package are integrated. Workstream 5 records remain historical predecessor evidence after WS6.2.

### WS6 completed packages

- WS6.0 — baseline lock and final defect register;
- WS6.1 — controlling machine handoff reconciliation;
- WS6.2 — final launch-control reconciliation and final issue-body rebinding;
- WS6.3 — current human status and authority document repair.

WS6.3 closes `WS6-BLOCK-003` and `WS6-CONSIST-008`. `WS6-BLOCK-006` remains open until the permanent post-merge final release is produced in the final reconciliation package.

## Current controlling authority

- `AGENTS.md` — controlling instruction;
- `handoff/codex-phase0-handoff.json` — machine execution contract;
- `contracts/codex-phase0-launch-control.json` — final launch control;
- `handoff/codex-phase0-issue-final.md` — only current generated issue #1 body;
- `contracts/workstream6-current-status.json` — current-status document reconciliation;
- `releases/pre-codex-final-reconciliation-2026-08-06.json` — required future permanent final release.

The exact required future branch-protection check is:

```text
Validate final pre-Codex canonical handoff and complete release
```

## Retained runtime boundary

The completed PCR-05 contract remains `contracts/runtime-adapter-contracts.json`. Every complete gate must run `scripts/validate_pcr05_runtime_adapters.py`; current and future repository status remains `runtime_activation_authorized=false` until a separately governed activation package exists.

## Verified predecessor baseline

The complete WS6.2 exact merge-reference gate recorded:

- 247 runtime tests passed in 27.05 seconds;
- 93.14 percent coverage across 4,604 statements;
- 245 executable test nodes;
- 99 semantic tests;
- 604 typed reference edges;
- zero unresolved references;
- Python compilation passed;
- Ruff passed;
- strict MyPy passed across 32 source files;
- 41 invalid launch bundles rejected;
- no permit emitted and no GitHub mutation performed by launch self-tests.

WS6.3 must retain or improve this baseline and add deterministic stale-state scanning for the current human authority documents.

## Work remaining before Codex

The remaining chat-first WS6 packages continue in sequence beginning with WS6.4. They include authority classification, terminology normalization, final workflow/check consolidation, remaining consistency and quality repairs, final evidence reconciliation and the permanent post-merge release.

Codex remains blocked until all repository-side packages are complete and the following manual gates are independently evidenced:

1. issue #19 hosted controls are verified;
2. exact-allowlist historical branch cleanup is complete;
3. branch protection requires `Validate final pre-Codex canonical handoff and complete release`;
4. a clean supported macOS report and Founder environment attestation are complete;
5. the Founder explicitly approves Codex Phase 0 tasks P0.1–P0.4 against the exact current `main` SHA;
6. `scripts/prepare_codex_phase0_launch.py` emits a valid local single-use permit.

## Current Founder actions

No Codex implementation action is required now. The useful Founder-controlled actions remain:

- preserve issue #19 as the manual hosted-control and environment evidence record;
- prepare evidence for MFA, `main` protection, stale-review dismissal, resolved conversations, force-push/deletion blocking and automatic merged-branch deletion;
- complete only exact-allowlist branch cleanup while retaining branch SHAs as evidence;
- prepare a clean macOS environment and run the redacted doctor after the final repository SHA is known;
- withhold Phase 0 approval until the permanent final release and all evidence are complete;
- do not purchase services, approve OAuth, enter credentials, enable real client data or permit external actions.

## Codex launch rule

Create `codex/phase-0-foundation` only after a valid permit exists and only from the permit’s approved SHA. The first commit must contain `governance/codex-phase0-launch-ack.json`. The pull request must remain draft. Merge, production deployment, real client data, runtime activation and Phase 1 remain unauthorised.

## Next permitted package

`WS6.4` is the next permitted chat-first work package after WS6.3 integration.
