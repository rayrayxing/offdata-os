# 69 — PCFA-02 Separate Historical Package State from Current Operational State

## Status

PCFA-02 is a post-release corrective package stacked on PCFA-01. It does not reopen or rewrite WS6.0–WS6.16 and it does not authorize Codex. `codex_start_authorized=false` throughout this package.

## Problem

Completed PCR/WS packages intentionally contain package-time facts: readiness snapshots, then-open defects, then-next work packages and authority labels. After later packages completed, several of those immutable records still looked like live operational state when read in isolation.

Examples include the WS6.2 launch contract, WS6.3 current-status reconciliation, WS6.4 authority registry and the PCR-04/WS6.1 machine handoff. Rewriting those records would destroy deterministic package reconstruction and audit history; treating them as live would give future automation stale authority.

## Resolution

PCFA-02 introduces exactly one successor live machine readiness projection:

`repository/current-operational-state.json`

Its governed source is `configs/current-operational-state.yaml`, its schema is `schemas/current-operational-state.schema.json`, its deterministic builder is `scripts/build_pcfa02_current_operational_state.py`, and its semantic validator is `scripts/validate_pcfa02_current_operational_state.py`.

The projection explicitly classifies predecessor state records and PCFA-01 evidence templates as retained package snapshots. Their embedded status fields remain true for their own package boundaries but cannot drive current launch decisions.

## Current authority surfaces

PCFA-02 adds neutral successor surfaces that are not named after a completed package:

- `docs/CURRENT-OPERATIONAL-STATE.md`;
- `handoff/codex-phase0-current-handoff.json`;
- `handoff/codex-phase0-current-issue.md`;
- `handoff/codex-phase0-current-hosted-controls-issue.md`;
- `handoff/codex-phase0-current-hosted-controls-attestation.template.json`;
- `handoff/codex-phase0-current-clean-macos-attestation.template.json`;
- `handoff/codex-phase0-current-founder-authorization.template.json`;
- `handoff/codex-phase0-current-launch-ack.template.json`.

Live Issue #1 and Issue #19 must only be synchronized to the new bodies after the repository change introducing them is integrated. Until then, the real permit verifier fails closed on the body-digest mismatch.

## Launch-control cutover

`scripts/prepare_codex_phase0_launch.py` now loads the current operational-state projection for live authority and uses the WS6.2 launch-control contract only as retained predecessor evidence.

The permit verifier requires current evidence to bind:

1. one exact then-current approved `main` SHA across Founder approval, hosted-controls evidence, clean-macOS evidence, macOS doctor `HEAD`, local `HEAD` and remote `main`;
2. the immutable WS6.16 release SHA-256;
3. the SHA-256 of `repository/current-operational-state.json`;
4. current Issue #1 and Issue #19 body SHA-256 values where applicable;
5. release-parent and permanent release-record ancestry to the approved current `main` SHA.

The permanent release parent and permanent release-record commit are historical identities and remain excluded from current-launch SHA equality.

## Permit and evidence version

Current evidence templates and the launch permit advance to schema version `2.2.0`. The permit now includes the current-operational-state digest in its deterministic identity and declares `stale_on_current_operational_state_change=true`.

PCFA-01's v2.1 templates remain unchanged as retained corrective-package evidence. Its validator is successor-aware: it continues to prove the PCFA-01 repair while accepting a stricter successor permit schema that still binds the PCFA-01 corrective contract.

## Required acceptance

PCFA-02 is complete only when:

- deterministic regeneration produces no diff;
- the current-state schema validates;
- historical WS6.2/WS6.3/WS6.4/PCR-04 state is proven retained rather than rewritten;
- the current handoff and current issue bodies point only to successor operational authority;
- current evidence templates bind current-state and release digests;
- the expanded launch self-test rejects stale package authority, state-digest drift, release drift, issue drift, SHA drift and authorization widening;
- the permanent WS6.16 gate passes;
- PCFA-01 successor validation passes;
- all inherited CF/PCR/WS validations pass;
- runtime tests meet the existing 90 percent coverage floor;
- compilation, Ruff and strict MyPy pass;
- the complete pull-request workflow matrix is green.

## Boundaries

PCFA-02 does not authorize:

- creation of `codex/phase-0-foundation`;
- IMP-P0 implementation;
- merge of PCFA-01, PCFA-02 or any IMP pull request;
- IMP-P1;
- runtime, Hermes or Northstar product activation;
- real client data;
- paid services, OAuth, DNS changes, production deployment or external actions.

PCFA-02 is stacked on PCFA-01 until the Founder separately approves and integrates the dependency chain. Material merges remain Founder-controlled.
