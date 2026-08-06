# WS6.5 — Phase namespace normalization

## Purpose

WS6.5 removes the ambiguity between completed chat-first design packages and future product implementation phases.

The canonical namespace is:

- `CF-P1–7` — completed chat-first foundation packages;
- `PCR-01–10` — completed pre-Codex reconciliation packages;
- `WS-4`, `WS-5` and `WS6.x` — governance, readiness and launch-control work packages;
- `IMP-P0–12` — future product implementation phases.

A completed `CF-*`, `PCR-*` or `WS-*` package never implies that an `IMP-*` phase has started or is authorized.

## Canonical contract

The governed source is:

`configs/workstream6-phase-namespace.yaml`

The generated contract and schema are:

- `contracts/workstream6-phase-namespace.json`
- `schemas/workstream6-phase-namespace.schema.json`

The executable gate is:

`scripts/validate_workstream6_phase_namespace.py`

## Compatibility boundary

Stable filenames, task IDs, branch names, schema keys and verifier keys retain their existing spelling so predecessor builders and launch controls remain compatible.

Examples include:

- `handoff/codex-phase0-handoff.json`;
- `scripts/prepare_codex_phase0_launch.py`;
- `codex/phase-0-foundation`;
- `P0.1` through `P0.4`;
- `explicit_founder_phase_0_approval_received`.

These are compatibility identifiers, not canonical phase labels and not authorization.

Legacy numeric phase wording and the former Codex display name are classified only as display aliases mapped to `IMP-PN`. The digest-bound issue #1 body retains those aliases for compatibility; all other current launch-facing prose uses the `IMP-*` namespace.

## Founder instruction received

At 2026-08-06T19:56:00+08:00, the Founder instructed the repository work to proceed with WS6.5 and communicated approval intent for issue #1.

That instruction authorizes this chat-first WS6.5 package only. It cannot yet satisfy the exact-SHA IMP-P0 approval gate because the final post-merge main SHA, permanent Workstream 6 release, hosted controls, clean-macOS evidence and local single-use permit do not yet exist.

Therefore:

- `founder_approval_intent_received=true`;
- `exact_final_main_sha_bound=false`;
- `launch_permit_issued=false`;
- `codex_start_authorized=false`;
- `phase0_implementation_authorized=false`.

## Validation

The WS6.5 gate proves:

- all four namespaces are disjoint;
- 49 canonical IDs exist;
- all 14 legacy aliases map to exactly one `IMP-*` ID;
- all 13 implementation phases `IMP-P0–12` appear in the backlog;
- eight current launch-facing surfaces use canonical `IMP-*` labels, while the digest-bound issue #1 body is an explicit compatibility-alias surface;
- compatibility identifiers remain stable;
- Founder approval intent is recorded without inferring implementation authorization;
- all prior builders, validators, runtime tests, compilation, Ruff, strict MyPy and launch self-tests continue to pass.

## Defect state

WS6.5 closes exactly:

`WS6-CONSIST-002`

The remaining blocking defect is:

`WS6-BLOCK-006`

The next permitted chat-first package is `WS6.6`.

## Rollback

Before merge, close the pull request and delete only `governance/workstream6-phase-namespace-normalization`.

After merge, revert WS6.5 as one unit, restore issue #1 and issue #19 from the synchronized generated bodies, and keep every launch and implementation boundary false.
