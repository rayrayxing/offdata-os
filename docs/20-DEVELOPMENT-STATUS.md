# 20 — Development Status

## Snapshot

Date: 2026-08-07

**Chat-first development is integrated through CF-P1–7, PCR-01–10, WS-4, WS-5 and WS6.7; later WS6 work remains unintegrated, final Workstream 6 reconciliation and all manual launch gates remain pending; `codex_start_authorized=false`.**

This is the current human-readable status document. Historical phase-completion documents, PR descriptions, issue comments and reports remain evidence for their own packages but do not supersede this snapshot. `repository/canonical-authority-registry.json` makes those current, retained and superseded classifications machine-readable.

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

### WS6 integrated packages

- WS6.0 — baseline lock and final defect register;
- WS6.1 — controlling machine handoff reconciliation;
- WS6.2 — final launch-control reconciliation and final issue-body rebinding;
- WS6.3 — current human status and authority document repair;
- WS6.4 — canonical authority, supersession and evidence registry;
- WS6.5 — phase namespace normalization across current authority and issue surfaces;
- WS6.6 — required final workflow and status-check identity reservation;
- WS6.7 — configuration contradictions and zero-spend committed defaults.

WS6.7 closes `WS6-CONSIST-004`. Committed model-provider spend defaults remain zero and no paid provider use is authorized without a separate Founder gate.

WS6.6 closes `WS6-CONSIST-003`. The only current future branch-protection identity is `Validate final pre-Codex canonical handoff and complete release`, reserved in `.github/workflows/workstream6-final-pre-codex.yml` and governed by `contracts/workstream6-required-workflow-identity.json`. The reserved workflow is manual-only and deliberately fails closed; WS6.15 must activate its final implementation, WS6.16 must bind the permanent release, and issue #19 must still evidence hosted enforcement.

WS6.5 closes `WS6-CONSIST-002`. The canonical phase families are now `CF-P1–7`, `PCR-01–10`, `WS-4`, `WS-5`, `WS6.x` and `IMP-P0–12`. Legacy phase wording survives only as an explicitly mapped display alias or stable compatibility identifier. No `IMP-*` phase has started.

WS6.4 closes `WS6-CONSIST-001` and `WS6-CONSIST-007`. The registry classifies every current read-order item, every configured authority/evidence root, all current external issue roles, and exactly one current machine handoff and generated issue body. `WS6-BLOCK-006` remains open until the permanent post-merge final release is produced in WS6.16.

Retained WS6.3 package evidence continues to state: WS6.3 closes `WS6-BLOCK-003` and `WS6-CONSIST-008`; at that package boundary, `WS6.4` is the next permitted chat-first work package. That historical statement does not override the current integration state.

## Current controlling authority

- `AGENTS.md` — controlling instruction;
- `repository/canonical-authority-registry.json` — current/superseded authority and evidence classification;
- `contracts/workstream6-phase-namespace.json` — canonical phase-family and compatibility mapping;
- `contracts/workstream6-required-workflow-identity.json` — unique required check identity and predecessor supersession map;
- `.github/workflows/workstream6-final-pre-codex.yml` — reserved manual-only, fail-closed final workflow identity;
- `handoff/codex-phase0-handoff.json` — sole current machine execution contract;
- `contracts/codex-phase0-launch-control.json` — final launch control;
- `handoff/codex-phase0-issue-final.md` — sole current generated issue #1 body;
- `contracts/workstream6-current-status.json` — current-status document reconciliation;
- `releases/pre-codex-final-reconciliation-2026-08-06.json` — required future permanent final release.

The exact required future branch-protection check, reserved but not yet activated or enforced, is:

```text
Validate final pre-Codex canonical handoff and complete release
```

## Authority and evidence registry

The governed source is `configs/workstream6-canonical-authority.yaml`; the registry is `repository/canonical-authority-registry.json`; and the semantic gate is `scripts/validate_workstream6_canonical_authority.py`.

The registry’s exact records and ordered rules classify current authority, retained evidence, superseded issue bodies and future evidence templates. Reports, releases and attachments are evidence, not execution authority unless a current exact record or gate names them.

## Retained runtime boundary

The completed PCR-05 contract remains `contracts/runtime-adapter-contracts.json`. Every complete gate must run `scripts/validate_pcr05_runtime_adapters.py`; current and future repository status remains `runtime_activation_authorized=false` until a separately governed activation package exists.

## Canonical CF-P1–7 release evidence

The permanent canonical chat-first release remains `releases/canonical-chat-first-phase1-7-release.json`. Its controlling integrated commit is `7dc5531e641158e5a84fbbb9fdf07cefefd4782b`, with authoritative validation run `30976222896` and retained artifact `8918355687`. These values are historical release identity, not current launch authorization.

## Verified predecessor baseline

The latest successful complete hosted evidence remains predecessor evidence and does not substitute for exact acceptance on later draft packages. Every successor gate must preserve the 90 percent runtime coverage floor, deterministic generation, compilation, Ruff, strict MyPy, referential integrity and all fail-closed launch boundaries.

## Work remaining before Codex

WS6.8 through WS6.16 are not integrated to `main`. Draft stacked packages may be prepared sequentially, but they do not change integration authority or permit later packages to merge ahead of predecessors. The remaining work includes issue/backlog normalization, implementation obligations, developer and Founder experience specifications, deliverable and operational quality preparation, cross-authority consistency, final workflow activation, permanent evidence reconciliation and the post-merge release.

Codex remains blocked until all repository-side packages are complete and integrated and the following manual gates are independently evidenced:

1. issue #19 hosted controls are verified;
2. exact-allowlist historical branch cleanup is complete;
3. WS6.15 activates the canonical final workflow and branch protection requires `Validate final pre-Codex canonical handoff and complete release`;
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

## Earliest unintegrated package

`WS6.8` is the earliest WS6 package not integrated to `main`. Any later draft package remains dependent on ordered integration and exact predecessor revalidation.
