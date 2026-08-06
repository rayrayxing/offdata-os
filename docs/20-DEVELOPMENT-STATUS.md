# 20 — Development Status

## Snapshot

Date: 2026-08-06

**Chat-first development is complete through CF-P1–7, PCR-01–10, WS-4, WS-5 and WS6.5; final Workstream 6 reconciliation and all manual launch gates remain pending; `codex_start_authorized=false`.**

This is the current human-readable status document. Historical phase-completion documents, PR descriptions, issue comments and reports remain evidence for their own packages but do not supersede this snapshot. `repository/canonical-authority-registry.json` now makes those current, retained and superseded classifications machine-readable.

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
- WS6.3 — current human status and authority document repair;
- WS6.4 — canonical authority, supersession and evidence registry;
- WS6.5 — phase namespace normalization across current authority and issue surfaces.

WS6.5 closes `WS6-CONSIST-002`. The canonical phase families are now `CF-P1–7`, `PCR-01–10`, `WS-4`, `WS-5`, `WS6.x` and `IMP-P0–12`. Legacy phase wording survives only as an explicitly mapped display alias or stable compatibility identifier. No `IMP-*` phase has started.

WS6.4 closes `WS6-CONSIST-001` and `WS6-CONSIST-007`. The registry classifies every current read-order item, every configured authority/evidence root, all current external issue roles, and exactly one current machine handoff and generated issue body. `WS6-BLOCK-006` remains open until the permanent post-merge final release is produced in WS6.16.

Retained WS6.3 package evidence continues to state: WS6.3 closes `WS6-BLOCK-003` and `WS6-CONSIST-008`; at that package boundary, `WS6.4` is the next permitted chat-first work package. That historical statement does not override the current next package below.

## Current controlling authority

- `AGENTS.md` — controlling instruction;
- `repository/canonical-authority-registry.json` — current/superseded authority and evidence classification;
- `contracts/workstream6-phase-namespace.json` — canonical phase-family and compatibility mapping;
- `handoff/codex-phase0-handoff.json` — sole current machine execution contract;
- `contracts/codex-phase0-launch-control.json` — final launch control;
- `handoff/codex-phase0-issue-final.md` — sole current generated issue #1 body;
- `contracts/workstream6-current-status.json` — current-status document reconciliation;
- `releases/pre-codex-final-reconciliation-2026-08-06.json` — required future permanent final release.

The exact required future branch-protection check is:

```text
Validate final pre-Codex canonical handoff and complete release
```

## Authority and evidence registry

The governed source is `configs/workstream6-canonical-authority.yaml`; the registry is `repository/canonical-authority-registry.json`; and the semantic gate is `scripts/validate_workstream6_canonical_authority.py`.

The registry contains 39 exact records, 11 ordered rules and three external issue records. Exact records take precedence over rules. Earlier IMP-P0 issue bodies and the PCR-09 machine snapshot remain retained evidence but are explicitly superseded. Reports, releases and attachments are evidence, not execution authority unless a current exact record or gate names them.

## Retained runtime boundary

The completed PCR-05 contract remains `contracts/runtime-adapter-contracts.json`. Every complete gate must run `scripts/validate_pcr05_runtime_adapters.py`; current and future repository status remains `runtime_activation_authorized=false` until a separately governed activation package exists.

## Canonical CF-P1–7 release evidence

The permanent canonical chat-first release remains `releases/canonical-chat-first-phase1-7-release.json`. Its controlling integrated commit is `7dc5531e641158e5a84fbbb9fdf07cefefd4782b`, with authoritative validation run `30976222896` and retained artifact `8918355687`. These values are historical release identity, not current launch authorization.

## Verified predecessor baseline

The complete WS6.3 exact merge-reference gate recorded:

- 247 runtime tests passed in 29.62 seconds in the dedicated gate;
- 93.14 percent coverage across 4,604 statements;
- 245 executable test nodes;
- 99 semantic tests;
- 604 typed reference edges;
- zero unresolved references;
- Python compilation passed;
- Ruff passed;
- strict MyPy passed across 32 source files;
- 38 WS6.3 mutations rejected;
- 41 invalid launch bundles rejected;
- no permit emitted and no GitHub mutation performed by launch self-tests.

WS6.5 retains this baseline and adds deterministic phase-family separation without changing launch authority.

## Work remaining before Codex

The remaining chat-first WS6 packages continue in sequence beginning with WS6.6. They include required workflow/check consolidation, remaining configuration and issue consistency repairs, implementation-obligation maps, developer and Founder experience specifications, quality preparation, cross-authority consistency, final evidence reconciliation and the permanent post-merge release.

Codex remains blocked until all repository-side packages are complete and the following manual gates are independently evidenced:

1. issue #19 hosted controls are verified;
2. exact-allowlist historical branch cleanup is complete;
3. branch protection requires `Validate final pre-Codex canonical handoff and complete release`;
4. a clean supported macOS report and Founder environment attestation are complete;
5. the Founder explicitly approves IMP-P0 tasks P0.1–P0.4 against the exact current `main` SHA;
6. `scripts/prepare_codex_phase0_launch.py` emits a valid local single-use permit.

## Current Founder actions

No Codex implementation action is required now. The useful Founder-controlled actions remain:

- preserve issue #19 as the manual hosted-control and environment evidence record;
- prepare evidence for MFA, `main` protection, stale-review dismissal, resolved conversations, force-push/deletion blocking and automatic merged-branch deletion;
- complete only exact-allowlist branch cleanup while retaining branch SHAs as evidence;
- prepare a clean macOS environment and run the redacted doctor after the final repository SHA is known;
- treat the recorded approval intent as non-executable until exact-SHA approval, the permanent final release and all evidence are complete;
- do not purchase services, approve OAuth, enter credentials, enable real client data or permit external actions.

## Codex launch rule

Create `codex/phase-0-foundation` only after a valid permit exists and only from the permit’s approved SHA. The first commit must contain `governance/codex-phase0-launch-ack.json`. The pull request must remain draft. Merge, production deployment, real client data, runtime activation and IMP-P1 remain unauthorised.

## Next permitted package

`WS6.6` is the next permitted chat-first work package after WS6.5 integration.
