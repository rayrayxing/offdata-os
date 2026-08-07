<!-- Current operational Issue #1 body introduced by PCFA-02 and extended through PCFA-06. Synchronize only after integration. -->
# Codex Phase 0 — Validate and build the controlled local foundation

> [!CAUTION]
> **NOT AUTHORISED TO START.** A completed chat-first repository, green workflows, the permanent WS6.16 release, an issue assignment or a branch name does not authorize Codex. A valid local single-use permit is mandatory.

## Current authority

For current launch decisions, use:

- `AGENTS.md` — controlling instruction;
- `repository/current-operational-state.json` — sole live machine readiness and authority projection;
- `repository/repository-visibility-and-licence-posture.json` — current repository visibility and licence posture;
- `repository/pcfa04-product-scope-implementation-addendum.json` — current product-scope implementation obligations, all `planned_not_implemented`;
- `repository/pcfa05-minimum-valuable-consulting-loop.json` — current Minimum Valuable Consulting Loop contract, all stages `planned_not_implemented`;
- `repository/pcfa06-hermes-bounded-adoption-refresh.json` — current Hermes bounded-adoption refresh, all capability assessments `planned_not_implemented`;
- `handoff/codex-phase0-current-handoff.json` — current machine execution handoff;
- `contracts/pcfa01-launch-control-repair.json` — corrected release/launch SHA semantics;
- `handoff/codex-phase0-current-issue.md` — current Issue #1 body;
- `handoff/codex-phase0-current-hosted-controls-issue.md` — current Issue #19 body;
- `releases/pre-codex-final-reconciliation-2026-08-06.json` — immutable WS6.16 release evidence;
- `schemas/codex-phase0-launch-permit.schema.json` — current permit schema;
- `scripts/prepare_codex_phase0_launch.py` — fail-closed permit entrypoint;
- `scripts/require_workstream6_final_reconciliation.py` — permanent release gate.

The WS6.2 launch-control contract, WS6.2/WS6.3 status records, WS6.4 authority registry, WS6.13 licence placeholder, PCR-06 Hermes compatibility pack, pre-PCFA machine handoff and earlier issue bodies remain retained package-time evidence. Their embedded readiness, next-package, blocker and licence-decision fields are not current operational state.

## Current repository state

- [x] CF-P1–7 and PCR-01–10 are integrated.
- [x] WS-4 and WS-5 repository packages are integrated.
- [x] WS6.0–WS6.16 are integrated and the permanent release record is valid.
- [x] PCFA-01 defines corrected executable launch semantics.
- [x] PCFA-02 defines the successor current operational-state projection and current authority surfaces.
- [x] PCFA-03 resolves the repository posture to private/internal development with no public licence grant and no public distribution authorization.
- [x] PCFA-04 defines the missing product-scope implementation obligations and assigns them to existing IMP phases without widening IMP-P0.
- [x] PCFA-05 defines the Minimum Valuable Consulting Loop, Founder interrupts, restart/recycle/idempotency invariants and negative-path programme without implementing runtime.
- [x] PCFA-06 refreshes Hermes bounded-adoption policy against the current public documentation without changing the v0.18.2 stable pin or activating Hermes.
- [ ] Live GitHub repository visibility must be `private` and independently verified; a public repository is a launch blocker.
- [ ] GitHub hosted controls are verified in Issue #19.
- [ ] Historical branch cleanup is complete with final inventory containing only `main` before launch.
- [ ] A clean supported macOS report and Founder environment attestation are complete.
- [ ] The Founder explicitly approves IMP-P0 tasks P0.1–P0.4 against the exact then-current `main` SHA.
- [ ] Live Issue #1 and Issue #19 bodies match their current repository files.
- [ ] A valid local single-use launch permit has been issued.

`codex_start_authorized=false` until every unchecked gate is independently satisfied.

## Repository visibility and licence posture

PCFA-03 establishes the current posture:

1. repository visibility must be `private` before Codex Phase 0 launch or implementation;
2. the live verifier independently queries GitHub repository metadata and rejects public visibility;
3. there is no public licence grant and no selected open-source licence;
4. public distribution, open-source distribution, external contributions and client distribution remain unauthorized;
5. third-party dependencies retain their own licences;
6. any future public/open-source posture requires explicit Founder approval, a licence ADR, dependency-licence compatibility review and legal review if material.

The absence of a repository `LICENSE` file is intentional for the current private/internal posture and does not grant reuse rights.

## PCFA-04 product-scope implementation addendum

PCFA-04 is a specification overlay, not implementation. Its canonical record contains 14 product areas and 29 requirements, including the 15-requirement Consulting Craft `CQ-*` family. Every requirement is `planned_not_implemented`.

The addendum covers mandate intake; the explicit Engagement Workspace; Quality and Assurance Console; Implementation and Benefits Workspace; broader ingestion formats and native provenance locators; 100% canonical-library source accounting; Consulting Craft quality; broader golden outputs; Office round-trip reconciliation; Founder/house style; asset-rights provenance; Founder attention burden metrics; explicit deliverable variants; and review/change-request workflow.

PCFA-04 does not create new IMP phases or new product-runtime scope in IMP-P0. It binds the additions to existing IMP-P1–P12 integration points. PCFA-05 now fulfills the MVCL dependency, while PCFA-07 must still reconcile these requirements into exact implementation-task, planned-test, evidence, dependency and phase-gate registrations.

## PCFA-05 Minimum Valuable Consulting Loop

PCFA-05 is a specification contract, not runtime implementation. It defines the 19-stage consulting loop from opportunity through closeout, 15 cross-loop invariants, six Founder interrupt classes and 13 mandatory negative-path cases. Every stage remains `planned_not_implemented`.

The governing sequence is `opportunity → mandate → engagement → decision framing → hypothesis tree → research plan → evidence → claim ledger → method → analysis and value → options → recommendation → Founder decision → storyline → deliverables → independent QA → implementation initiatives → benefits → closeout`.

The contract requires one engagement ID and canonical state, material claim traceability, reproducible numbers, retained contrary evidence, method justification, idempotency, exact-version Founder approval, restart-safe checkpoints, independent QA, cross-format reconciliation, recommendation-to-benefit traceability, audit history, Founder recycle/pause/cancel/stop control and no sole self-approval. PCFA-07 must register exact task/test/evidence/dependency/phase-gate bindings; PCFA-08 final cross-authority acceptance remains required.

## PCFA-06 Hermes bounded-adoption refresh

PCFA-06 is a specification and policy refresh, not Hermes installation or activation. The stable upstream pin remains `v0.18.2` / `v2026.7.7.2` / `9de9c25`; current public documentation is treated as a capability-policy snapshot and is **not** asserted to be identical to the pinned release. Every Hermes capability assessment remains `planned_not_implemented`.

The refresh explicitly keeps raw `/goal` from becoming workflow authority: any future use must map its completion contract into a governed `WorkerPackage`, with `WorkerPackage.acceptance` and offdata test evidence as completion authority, bounded turn budgets, offdata-owned durable checkpoints and Founder interrupts. Raw top-level background delegation, nested delegation and parallel fan-out remain denied; initial adapter concurrency remains one.

Hermes bundled, hub and learned skills remain candidate-only. `/learn` is suggestion-only, `/journey` is read-only observability, curator is disabled, and no automatic skill or methodology promotion is allowed. Mixture-of-Agents is candidate-only behind the offdata model router, requires explicit cost/provider/evaluation controls, and cannot by itself satisfy independent QA. Hermes memory remains noncanonical; MCP, tool gateway, messaging, cron/background sessions and optional Codex app-server runtime remain deferred or denied pending later controls.

PCFA-07 must map every PCFA-06 capability to exact requirement IDs, IMP tasks, planned tests, evidence, dependencies and phase gates. PCFA-08 final cross-authority acceptance remains required.

## Release and launch SHA semantics

The permanent WS6.16 record does **not** define the future launch SHA.

`release_parent_main_sha` is the historical exact integrated `main` immediately before the permanent release-record commit. At permit time:

1. the release parent must be an ancestor of the approved launch `main`;
2. the permanent release-record commit must be an ancestor of the approved launch `main`;
3. neither historical release SHA participates in current-launch SHA equality;
4. Founder approval, hosted-controls evidence, clean-macOS evidence, macOS doctor `HEAD`, local `HEAD` and remote `main` must all equal one exact approved current `main` SHA;
5. hosted-controls, clean-macOS and Founder evidence must bind the exact permanent-release SHA-256 and `repository/current-operational-state.json` SHA-256 through the `current_operational_state_sha256` field;
6. the current operational-state digest transitively binds the exact PCFA-03 repository-posture SHA-256;
7. the current operational-state authority directly binds the exact PCFA-04 product-scope addendum SHA-256;
8. the current operational-state authority directly binds the exact PCFA-05 MVCL SHA-256, and the launch entrypoint rejects missing, reordered, falsely implemented or permissive MVCL state;
9. the current operational-state authority directly binds the exact PCFA-06 Hermes bounded-adoption refresh SHA-256, and the launch entrypoint rejects activation, raw `/goal` authority, background delegation, automatic learning/promotion or MoA-router drift.

Any drift fails closed.

## Required read order

1. `AGENTS.md`
2. `repository/current-operational-state.json`
3. `repository/repository-visibility-and-licence-posture.json`
4. `repository/pcfa04-product-scope-implementation-addendum.json`
5. `repository/pcfa05-minimum-valuable-consulting-loop.json`
6. `repository/pcfa06-hermes-bounded-adoption-refresh.json`
7. `docs/CURRENT-OPERATIONAL-STATE.md`
8. `docs/71-PCFA-04-PRODUCT-SCOPE-IMPLEMENTATION-ADDENDUM.md`
9. `docs/72-PCFA-05-MINIMUM-VALUABLE-CONSULTING-LOOP.md`
10. `docs/73-PCFA-06-HERMES-BOUNDED-ADOPTION-REFRESH.md`
11. `handoff/codex-phase0-current-handoff.json`
12. `contracts/pcfa01-launch-control-repair.json`
13. `handoff/codex-phase0-current-issue.md`
14. `handoff/codex-phase0-current-hosted-controls-issue.md`
15. `releases/pre-codex-final-reconciliation-2026-08-06.json`
16. `docs/01-PRODUCT-VISION.md`
17. `docs/02-FUNCTIONAL-REQUIREMENTS.md`
18. `docs/03-ARCHITECTURE.md`
19. `docs/10-TESTING-STRATEGY.md`
20. `docs/11-BUILD-BACKLOG.md`
21. `docs/14-CODEX-KICKOFF.md`
22. `docs/19-PHASE-0-VALIDATION-ADDENDUM.md`
23. `handoff/codex-phase0-current-hosted-controls-attestation.template.json`
24. `handoff/codex-phase0-current-clean-macos-attestation.template.json`
25. `handoff/codex-phase0-current-founder-authorization.template.json`
26. `handoff/codex-phase0-current-launch-ack.template.json`
27. `schemas/codex-phase0-launch-permit.schema.json`
28. `scripts/prepare_codex_phase0_launch.py`
29. `scripts/require_workstream6_final_reconciliation.py`

Historical PCR/WS package records remain available for audit and deterministic regression but do not override the current projection above.

## Preflight

From a clean supported macOS clone at the exact intended `main` SHA, run:

```bash
bash scripts/run_ws62_ci.sh
python scripts/validate_pcfa01_launch_control.py
python scripts/validate_pcfa02_current_operational_state.py
python scripts/validate_pcfa03_repository_posture.py
python scripts/validate_pcfa04_product_scope_addendum.py
python scripts/validate_pcfa05_mvcl.py
python scripts/prepare_codex_phase0_launch.py --self-test
python scripts/require_workstream6_final_reconciliation.py
```

Any failure or generated diff blocks launch.

## Launch evidence

Use filled copies of the current templates:

```text
handoff/codex-phase0-current-hosted-controls-attestation.template.json
handoff/codex-phase0-current-clean-macos-attestation.template.json
handoff/codex-phase0-current-founder-authorization.template.json
```

Each applicable evidence file must bind:

- the exact approved current `main` SHA;
- the permanent WS6.16 release SHA-256;
- the SHA-256 of `repository/current-operational-state.json` in `current_operational_state_sha256`;
- current Issue #1 and/or Issue #19 body digests where required.

The hosted-controls attestation must additionally contain `repository_visibility_private=true`, and the launch verifier independently confirms the same state from live GitHub repository metadata.

Then run:

```bash
python scripts/prepare_codex_phase0_launch.py \
  --hosted-controls .local/codex-phase0-launch/hosted-controls.json \
  --macos-report .local/codex-phase0-launch/macos-doctor.json \
  --macos-attestation .local/codex-phase0-launch/macos-attestation.json \
  --founder-approval .local/codex-phase0-launch/founder-approval.json
```

The output permit is local, ignored, mode `0600`, single-use and stale on any approved-main, release, current-state, repository-posture, product-scope, MVCL, issue-body, evidence, required-check or scope change.

## Authorized scope after a valid permit exists

Only:

- `P0.1` — repository baseline;
- `P0.2` — local development environment;
- `P0.3` — engineering quality baseline;
- `P0.4` — security and operating documentation.

Create `codex/phase-0-foundation` only from the permit's approved SHA. The first commit must contain `governance/codex-phase0-launch-ack.json` populated from the current acknowledgement template. Open a draft pull request and stop at the Founder gate.

## Still prohibited

- implementing PCFA-04 product features during IMP-P0 unless they are strictly foundation interfaces already within P0.1–P0.4;
- IMP-P1 or later implementation;
- merging the IMP-P0 pull request without separate Founder approval;
- runtime or Hermes activation;
- Northstar product-runtime activation;
- public or open-source distribution;
- external contributions under an inferred licence;
- real client data;
- paid services or trials;
- requesting or committing credentials;
- OAuth or third-party access approval;
- DNS changes;
- external communications;
- staging or production deployment;
- autonomous merge;
- weakening tests or golden expectations.

## Live issue synchronization

This file becomes the live canonical Issue #1 body only after the repository change introducing it is integrated. Before permit issuance, the verifier requires live Issue #1 to be open and its body SHA-256 to exactly match this file.

Issue #2 must remain closed as duplicate. Issue #19 must satisfy its own current body and evidence rules.
