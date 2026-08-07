# 70 — PCFA-03 Repository visibility and licence posture

## Purpose

PCFA-03 resolves the contradiction between the repository's hosted public visibility and the absence of any public licence/distribution grant, without rewriting the historical WS6.13 licence placeholder.

## Decision

The current offdata development posture is:

- GitHub repository visibility required for Codex Phase 0 launch and IMP-P0 implementation: **private**;
- licence posture: **no public licence grant / proprietary internal development**;
- selected open-source licence: none;
- implicit licence grant: false;
- public/open-source distribution: unauthorized;
- external contributions: unauthorized;
- client distribution: unauthorized;
- third-party dependencies retain their own licences.

The repository was observed as public on 2026-08-07 while this package was prepared. That is a historical observation, not an approved operational posture. The hosted visibility setting must be changed to private and verified before Codex launch.

## Historical versus current authority

`configs/workstream6-phase0-licence-decision-placeholder.yaml` remains immutable WS6.13 package-time evidence showing that no licence had yet been selected. PCFA-03 does not rewrite that record.

The current successor authority is:

- `repository/repository-visibility-and-licence-posture.json` — current posture;
- `repository/current-operational-state.json` — current launch/readiness projection, including the exact posture SHA-256;
- `handoff/codex-phase0-current-handoff.json` — current execution handoff;
- `scripts/prepare_codex_phase0_launch.py` — real fail-closed launch entrypoint.

## Enforcement

A real Codex Phase 0 permit requires both:

1. hosted-controls evidence containing `repository_visibility_private=true`; and
2. a live GitHub repository metadata response with `visibility=private` and `private=true`.

The verifier rejects public visibility even if all other evidence is valid. The current operational-state digest binds the exact PCFA-03 posture digest, so any posture change invalidates current evidence through the existing current-state staleness rule.

## Future licence changes

Any future public/open-source distribution posture requires:

1. explicit Founder approval;
2. a licence ADR;
3. dependency-licence compatibility review; and
4. legal review if material.

No repository `LICENSE` file is added by PCFA-03 because the current posture does not grant public reuse rights.

## Repository-side completion versus hosted gate

PCFA-03 deliberately separates two facts:

- repository-side posture decision and launch enforcement: complete;
- live GitHub private visibility: pending manual hosted setting verification.

The latter remains a launch blocker and is recorded as `repository_visibility_private_verified=false` in current operational state.

## Acceptance

PCFA-03 is repository-side complete only when:

- posture YAML, generated JSON and schema reconcile deterministically;
- current operational state references and hashes the posture;
- WS6.13 remains historical and unchanged;
- current Issue #1, Issue #19, handoff and status surfaces expose the private/no-public-grant posture;
- hosted-controls template requires explicit private-visibility attestation;
- synthetic public-visibility and permissive-licence mutations fail;
- the full inherited CF/PCR/WS/PCFA validation path, runtime tests, coverage, Ruff, strict MyPy and compile checks pass;
- all authorization boundaries remain false.

## Boundaries

PCFA-03 does not itself change GitHub repository visibility, authorize Codex, create the Phase 0 branch, authorize merge, select an open-source licence, enable public distribution, activate runtime/Hermes, enable real client data, approve paid services/OAuth, or deploy anything.

`codex_start_authorized=false`.
