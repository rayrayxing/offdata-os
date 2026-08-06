# 00 — Start Here

## Purpose

This document tells the Founder, reviewers and future Codex sessions how to interpret the offdata repository without confusing completed chat-first design with implementation authority.

## Current canonical status

**Chat-first development is complete through CF-P1–7, PCR-01–10, WS-4, WS-5 and WS6.5; final Workstream 6 reconciliation and all manual launch gates remain pending; `codex_start_authorized=false`.**

The repository is **pre-Codex**. It is not presently executing implementation IMP-P0. A deterministic consulting kernel and governed chat-first package exist in `packages/offdata-core/`, but they remain inputs to a future permitted implementation session.

No production infrastructure, real client data, external outreach, OAuth approval, paid service activation, runtime activation, Hermes activation, Northstar product implementation, autonomous merge or IMP-P1 work is authorised.

## Canonical repository and authority

`rayrayxing/offdata-os` is the only controlling build repository. `rayrayxing/offdata` and `rayrayxing/offdata-clean` are historical references only.

Current authority is interpreted in this order:

1. `AGENTS.md`;
2. `GOVERNANCE.md`, `SECURITY.md` and `CONTRIBUTING.md`;
3. this current-status document and `docs/20-DEVELOPMENT-STATUS.md`;
4. `repository/canonical-authority-registry.json`;
5. `contracts/workstream6-phase-namespace.json`;
6. `handoff/codex-phase0-handoff.json`;
7. `contracts/codex-phase0-launch-control.json`;
8. `handoff/codex-phase0-issue-final.md` and synchronized issue #1;
9. the future permanent release `releases/pre-codex-final-reconciliation-2026-08-06.json`.

The phase namespace contract defines `CF-P1–7`, `PCR-01–10`, `WS-*` and `IMP-P0–12`. The authority registry classifies current, supporting, retained and superseded repository records. Historical completion documents remain evidence for the package they describe. Old PR numbers, branch names, issue bodies, run summaries and chat messages do not override current authority.

## Build labels

- **CF-P1–7**: completed chat-first design, contracts, fixtures and deterministic logic.
- **PCR-01–10**: completed pre-Codex reconciliation packages.
- **WS-4 and WS-5**: completed repository-readiness and launch-control predecessors.
- **WS6.x**: final pre-Codex reconciliation packages.
- **IMP-P0–12**: future implementation phases. None has started.

A completed CF or PCR package is not an implemented product phase and is not permission to begin IMP-P0.

## Current read order

Before any launch preparation, read:

1. `AGENTS.md`;
2. `README.md`;
3. this file;
4. `docs/20-DEVELOPMENT-STATUS.md`;
5. `docs/14-CODEX-KICKOFF.md`;
6. `docs/19-PHASE-0-VALIDATION-ADDENDUM.md`;
7. `repository/canonical-authority-registry.json`;
8. `contracts/workstream6-phase-namespace.json`;
9. `handoff/codex-phase0-handoff.json`;
10. `contracts/codex-phase0-launch-control.json`;
11. `handoff/codex-phase0-issue-final.md`.

The registry classifies the full machine and issue read orders. The machine handoff contains the complete implementation read order and command set. Do not replace it with this abbreviated orientation list.

## Launch sequence

IMP-P0 remains blocked until all of the following are independently verified:

1. every required WS6 package is integrated and the permanent final release passes `scripts/require_workstream6_final_reconciliation.py`;
2. issue #19 records completed hosted controls, the exact required check `Validate final pre-Codex canonical handoff and complete release`, and exact-allowlist branch cleanup;
3. a clean macOS doctor report and Founder environment attestation reference the exact current `main` SHA;
4. the Founder explicitly approves only tasks P0.1–P0.4 against that same SHA; and
5. `scripts/prepare_codex_phase0_launch.py` writes a valid local single-use permit.

Create `codex/phase-0-foundation` only after the permit exists. The branch must start from the permit’s approved SHA, the first commit must contain the governed acknowledgement, and the pull request must remain draft. Merge and IMP-P1 remain prohibited.

## Founder operating model

The Founder provides product and business judgement, creates accounts, enters credentials through secure interfaces, completes any approved OAuth steps, reviews evidence and approves material changes. ChatGPT develops and reviews bounded chat-first artifacts. Codex performs computer-environment implementation only after the launch gate is satisfied.

## Definition of done

A governed package or implementation phase is complete only when its requirements, deterministic generation, tests, independent review, evidence, documentation, costs, risks and rollback are complete and the required Founder decision is explicit. Repository files and green CI never substitute for a manual approval or launch permit.
