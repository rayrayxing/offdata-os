# offdata OS

**offdata** is a Founder-governed, AI-native consulting operating system designed to execute most analyst, consultant and engagement-management work while preserving human accountability for material decisions, external commitments, commercial choices and client relationships.

This repository is the **canonical build repository** for the new offdata consulting platform. The older `rayrayxing/offdata` and `rayrayxing/offdata-clean` repositories are historical references only.

## Current canonical status

**Chat-first development is complete through CF-P1–7, PCR-01–10, WS-4, WS-5 and WS6.4; final Workstream 6 reconciliation and all manual launch gates remain pending; `codex_start_authorized=false`.**

- Initial operator: Founder only.
- Initial hosting and data region: Singapore.
- Data: synthetic only; real client data remains prohibited.
- Codex implementation phase: not started and not authorised.
- Current authority registry: `repository/canonical-authority-registry.json`.
- Current canonical issue: `handoff/codex-phase0-issue-final.md`, synchronized to issue #1.
- Current launch control: `contracts/codex-phase0-launch-control.json`.
- Current machine handoff: `handoff/codex-phase0-handoff.json`.
- Required future branch-protection check: `Validate final pre-Codex canonical handoff and complete release`.
- Required permanent final release: `releases/pre-codex-final-reconciliation-2026-08-06.json`.

Historical PCR and Workstream completion documents remain evidence of their own completed packages. They do not supersede the current status above or authorise Codex.

## Authority and read order

1. `AGENTS.md`
2. `GOVERNANCE.md`
3. `SECURITY.md`
4. `CONTRIBUTING.md`
5. `docs/00-START-HERE.md`
6. `docs/20-DEVELOPMENT-STATUS.md`
7. `repository/canonical-authority-registry.json`
8. `handoff/codex-phase0-handoff.json`
9. `contracts/codex-phase0-launch-control.json`
10. `handoff/codex-phase0-issue-final.md`

The authority registry classifies every current read-order item and retained evidence surface. The complete implementation read order and command set remain machine-governed in `handoff/codex-phase0-handoff.json`. Chat history, old pull-request descriptions, superseded issue bodies and historical reports are not current execution authority.

## Codex entry gate

Codex may not begin merely because repository validation passes. Every one of the following must first be independently satisfied:

1. the permanent final Workstream 6 release exists and passes `scripts/require_workstream6_final_reconciliation.py`;
2. issue #19 is completed with evidence for hosted controls and exact-allowlist historical branch cleanup;
3. a clean macOS doctor report and Founder environment attestation are complete;
4. the Founder gives explicit approval for Codex Phase 0 only against the exact current `main` SHA; and
5. `scripts/prepare_codex_phase0_launch.py` emits a valid local single-use permit.

Create `codex/phase-0-foundation` only after that permit exists and only from its approved SHA. The first commit must contain the governed launch acknowledgement. The pull request must remain draft; merge and Phase 1 remain unauthorised.

## Retained runtime boundary

The provider-independent runtime contract remains `contracts/runtime-adapter-contracts.json` and must pass `scripts/validate_pcr05_runtime_adapters.py` in every complete gate. Contract existence never activates a runtime: `runtime_activation_authorized=false`.

## Product objective

offdata should support the full consulting lifecycle from qualified opportunity and mandate intake through framing, research, analysis, recommendation, deliverable production, implementation and benefits verification. It should also support controlled origination, CRM continuity, methodology scouting and continuous quality improvement.

## Non-negotiable principles

1. **Operational autonomy, not accountability autonomy.** Material, external, commercial, legal, irreversible or high-risk actions require Founder approval.
2. **The database is the system of record.** Chat history, model memory and agent sessions are not authoritative engagement truth.
3. **Evidence before assertion.** Material claims must be traceable to evidence, analysis, assumptions and review state.
4. **One story, many surfaces.** PPTX, DOCX, XLSX, PDF, SVG and HTML outputs must be rendered from a shared semantic engagement model.
5. **Deterministic calculations.** Models calculate; language models interpret and communicate.
6. **Independent quality review.** The creator of material work cannot be its sole approver.
7. **Client separation.** Cross-engagement retrieval or reuse of confidential client material requires explicit authority.
8. **Specification-first, test-first, phase-gated.** Implementation must not build ahead of the approved phase.
9. **No secrets in source control or chat.** Credentials belong only in approved secret-management or OAuth interfaces.
10. **Copyright-safe methodology development.** External ideas may inform independently reconstructed methods; protected or confidential material must not be copied.

## Initial implementation target

After a valid permit is issued, Codex Phase 0 may establish only the controlled local project foundation defined by tasks P0.1–P0.4. Application and operating-infrastructure directories are populated only through separately approved implementation phases.
