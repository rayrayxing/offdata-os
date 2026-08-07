<!-- Current operational Issue #1 body introduced by PCFA-02. Synchronize only after integration. -->
# Codex Phase 0 — Validate and build the controlled local foundation

> [!CAUTION]
> **NOT AUTHORISED TO START.** A completed chat-first repository, green workflows, the permanent WS6.16 release, an issue assignment or a branch name does not authorize Codex. A valid local single-use permit is mandatory.

## Current authority

For current launch decisions, use:

- `AGENTS.md` — controlling instruction;
- `repository/current-operational-state.json` — sole live machine readiness and authority projection;
- `handoff/codex-phase0-current-handoff.json` — current machine execution handoff;
- `contracts/pcfa01-launch-control-repair.json` — corrected release/launch SHA semantics;
- `handoff/codex-phase0-current-issue.md` — current Issue #1 body;
- `handoff/codex-phase0-current-hosted-controls-issue.md` — current Issue #19 body;
- `releases/pre-codex-final-reconciliation-2026-08-06.json` — immutable WS6.16 release evidence;
- `schemas/codex-phase0-launch-permit.schema.json` — current permit schema;
- `scripts/prepare_codex_phase0_launch.py` — fail-closed permit entrypoint;
- `scripts/require_workstream6_final_reconciliation.py` — permanent release gate.

The WS6.2 launch-control contract, WS6.2/WS6.3 status records, WS6.4 authority registry, pre-PCFA machine handoff and earlier issue bodies remain retained package-time evidence. Their embedded readiness, next-package and blocker fields are not current operational state.

## Current repository state

- [x] CF-P1–7 and PCR-01–10 are integrated.
- [x] WS-4 and WS-5 repository packages are integrated.
- [x] WS6.0–WS6.16 are integrated and the permanent release record is valid.
- [x] PCFA-01 defines corrected executable launch semantics.
- [x] PCFA-02 defines the successor current operational-state projection and current authority surfaces.
- [ ] GitHub hosted controls are verified in Issue #19.
- [ ] Historical branch cleanup is complete with final inventory containing only `main` before launch.
- [ ] A clean supported macOS report and Founder environment attestation are complete.
- [ ] The Founder explicitly approves IMP-P0 tasks P0.1–P0.4 against the exact then-current `main` SHA.
- [ ] Live Issue #1 and Issue #19 bodies match their current repository files.
- [ ] A valid local single-use launch permit has been issued.

`codex_start_authorized=false` until every unchecked gate is independently satisfied.

## Release and launch SHA semantics

The permanent WS6.16 record does **not** define the future launch SHA.

`release_parent_main_sha` is the historical exact integrated `main` immediately before the permanent release-record commit. At permit time:

1. the release parent must be an ancestor of the approved launch `main`;
2. the permanent release-record commit must be an ancestor of the approved launch `main`;
3. neither historical release SHA participates in current-launch SHA equality;
4. Founder approval, hosted-controls evidence, clean-macOS evidence, macOS doctor `HEAD`, local `HEAD` and remote `main` must all equal one exact approved current `main` SHA;
5. hosted-controls, clean-macOS and Founder evidence must bind the exact permanent-release SHA-256 and `repository/current-operational-state.json` SHA-256.

Any drift fails closed.

## Required read order

1. `AGENTS.md`
2. `repository/current-operational-state.json`
3. `docs/CURRENT-OPERATIONAL-STATE.md`
4. `handoff/codex-phase0-current-handoff.json`
5. `contracts/pcfa01-launch-control-repair.json`
6. `handoff/codex-phase0-current-issue.md`
7. `handoff/codex-phase0-current-hosted-controls-issue.md`
8. `releases/pre-codex-final-reconciliation-2026-08-06.json`
9. `docs/01-PRODUCT-VISION.md`
10. `docs/02-FUNCTIONAL-REQUIREMENTS.md`
11. `docs/03-ARCHITECTURE.md`
12. `docs/10-TESTING-STRATEGY.md`
13. `docs/11-BUILD-BACKLOG.md`
14. `docs/14-CODEX-KICKOFF.md`
15. `docs/19-PHASE-0-VALIDATION-ADDENDUM.md`
16. `handoff/codex-phase0-current-hosted-controls-attestation.template.json`
17. `handoff/codex-phase0-current-clean-macos-attestation.template.json`
18. `handoff/codex-phase0-current-founder-authorization.template.json`
19. `handoff/codex-phase0-current-launch-ack.template.json`
20. `schemas/codex-phase0-launch-permit.schema.json`
21. `scripts/prepare_codex_phase0_launch.py`
22. `scripts/require_workstream6_final_reconciliation.py`

Historical PCR/WS package records remain available for audit and deterministic regression but do not override the current projection above.

## Preflight

From a clean supported macOS clone at the exact intended `main` SHA, run:

```bash
bash scripts/run_ws62_ci.sh
python scripts/validate_pcfa01_launch_control.py
python scripts/validate_pcfa02_current_operational_state.py
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
- the SHA-256 of `repository/current-operational-state.json`;
- current Issue #1 and/or Issue #19 body digests where required.

Then run:

```bash
python scripts/prepare_codex_phase0_launch.py \
  --hosted-controls .local/codex-phase0-launch/hosted-controls.json \
  --macos-report .local/codex-phase0-launch/macos-doctor.json \
  --macos-attestation .local/codex-phase0-launch/macos-attestation.json \
  --founder-approval .local/codex-phase0-launch/founder-approval.json
```

The output permit is local, ignored, mode `0600`, single-use and stale on any approved-main, release, current-state, issue-body, evidence, required-check or scope change.

## Authorized scope after a valid permit exists

Only:

- `P0.1` — repository baseline;
- `P0.2` — local development environment;
- `P0.3` — engineering quality baseline;
- `P0.4` — security and operating documentation.

Create `codex/phase-0-foundation` only from the permit's approved SHA. The first commit must contain `governance/codex-phase0-launch-ack.json` populated from the current acknowledgement template. Open a draft pull request and stop at the Founder gate.

## Still prohibited

- IMP-P1 or later implementation;
- merging the IMP-P0 pull request without separate Founder approval;
- runtime or Hermes activation;
- Northstar product-runtime activation;
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
