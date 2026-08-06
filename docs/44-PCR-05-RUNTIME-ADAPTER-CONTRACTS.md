# 44 — PCR-05 Runtime Adapter Contracts

## Purpose

PCR-05 turns the architecture principle of replaceable runtimes into deterministic, machine-readable contracts before Codex implements any runtime integration.

The contract keeps offdata’s control plane and canonical state independent from Pydantic AI, Restate, Codex, Hermes Agent, Claude Code, Pi, model providers and tool implementations. It defines interfaces and conformance requirements; it does not activate any runtime, provider, credential, processor, paid service or external action.

## Governed artefacts

- `configs/runtime-adapters.yaml` — human-reviewable source contract.
- `contracts/runtime-adapter-contracts.json` — deterministic machine-readable contract.
- `schemas/runtime-adapter-contracts.schema.json` — top-level and message schema.
- `scripts/build_pcr05_runtime_adapters.py` — deterministic builder and prerequisite snapshot.
- `scripts/validate_pcr05_runtime_adapters.py` — schema, semantic, cross-contract, sample and mutation validation.
- `reports/pcr05-validation-evidence.md` — exact implementation and review evidence.

## Adapter boundaries

PCR-05 defines four replaceable adapter kinds:

1. **Agent runtime** — typed `ContextPackage` input and `AgentEnvelope` output, tool allowlists, governed budgets, cancellation and audit events.
2. **Workflow runtime** — durable identity, checkpoints, idempotent replay, approval waits, cancellation and recovery without direct domain mutation.
3. **Worker harness** — isolated work packages for Codex or later harnesses, with explicit tools, write scope, acceptance tests, artefacts and logs.
4. **Tool runtime** — validated deterministic or approved-read invocations, with explicit side-effect, approval, idempotency and audit rules.

Every adapter returns references, proposed commands and audit evidence. Canonical engagement state may change only through validated offdata command APIs.

## Profiles and deferred integrations

The registry records contract-test, planned and deferred profiles. Pydantic AI, Restate, Codex and local deterministic tools are planned implementation families. Hermes Agent, Claude Code and Pi remain deferred bounded-worker candidates. No profile is activated by PCR-05.

Hermes skills or memory may later improve a Founder-facing worker, but they may not become canonical engagement truth, bypass tool or data controls, write canonical state directly or expand beyond a reviewed work package.

## Security and authority

Before Codex, only `public` and `internal` synthetic data are permitted. Real client data, unregistered processors, credential values, provider training, cross-tenant execution, cross-region transfer, paid services, production deployment, external side effects and autonomous merge remain denied.

All external-side-effect tool classes are registered as unavailable and require both scoped Founder approval and idempotency before any future activation.

## Validation behaviour

PCR-05 validates:

- exactly four governed adapter kinds;
- unique adapter, tool and conformance identities;
- all existing agent tool classes are declared;
- command-only canonical writes and deny-by-default external actions;
- typed request and response samples for every adapter kind;
- budget ceilings, usage reporting, classifications, processors and audit events;
- the command catalogue exposes the exact seven commands requiring idempotency;
- Codex and runtime activation remain false;
- fourteen conformance cases and eighteen controlled mutation cases.

The mutation suite proves rejection of direct writes, runtime memory as truth, deferred-profile activation, credential leakage, missing adapter kinds, enabled side effects, missing approval, undeclared agent tools, runtime activation, real client data, raised budgets, disabled idempotency, incomplete audit events, incomplete activation conditions, transient PR metadata, inconsistent readiness checks, false command-idempotency counts and side-effect requests without approval or idempotency.

## Activation boundary

A green PCR-05 gate means the runtime boundaries are internally specified. It does not authorise implementation execution or runtime activation.

All conditions remain mandatory: PCR-03, PCR-04 and PCR-05 merged to `main`; issue #19 hosted controls verified; explicit Founder Phase 0 approval; and a clean macOS environment.

`runtime_activation_authorized=false`

## Cost and rollback

PCR-05 requires no new paid service or subscription. Before merge, rollback is closing the pull request and deleting its branch. After merge, rollback is a reviewed revert of the PCR-05 merge commit without weakening prior gates.
