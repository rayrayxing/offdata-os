# PCR-05 Validation Evidence

Date: 2026-08-05

## Scope

PCR-05 runtime adapter source, generated machine contract, JSON Schema, typed examples, cross-contract reconciliation, conformance cases, mutation rejection, Codex handoff integration and complete Phase 1–7 plus PCR-01–05 regression validation.

## Controlling implementation evidence

- Branch: `governance/pcr05-runtime-adapters`
- Stacked pull request: `#21 — Complete PCR-05 runtime adapter contracts`
- Tested branch head: `2148dce33c9f2106b44bcb5a37f44640955149ac`
- Tested pull-request merge reference: `379c75d283a36f2a63ce2855b917e2b7674d68bb`
- Stacked base: PCR-04 head `bb8ca42877244d84481fa7246e9ba8784a6f0414`
- GitHub Actions run: `30999593507`
- GitHub Actions job: `92284960728`
- Result: success; all 35 substantive workflow steps passed.

The pull request is stacked because PCR-03 and PCR-04 remain subject to their governed Founder review and merge sequence. After the prerequisite pull requests merge, PR #21 must be retargeted to the merged PCR-04 base and the complete exact merge-reference gate must pass again before PCR-05 merge.

## PCR-05 contract evidence

The deterministic PCR-05 gate reported:

- adapter kinds: 4;
- adapter profiles: 8;
- governed tool classes: 20;
- typed request and response samples: 8;
- conformance cases: 14;
- controlled mutation cases rejected: 18;
- command catalogue entries: 10;
- commands requiring idempotency: 7;
- local prerequisite records passed: true;
- runtime activation authorised: false.

The four replaceable boundaries are agent runtime, durable workflow runtime, bounded worker harness and tool runtime. Every boundary preserves command-only canonical writes, non-canonical runtime memory, correlation identity, budgets, audit events, health checks, cancellation and kill switches.

The eight profiles cover a local agent contract stub, planned Pydantic AI, planned Restate, planned Codex worker harness, planned local tool runtime and deferred Hermes, Claude Code and Pi worker harnesses. No profile is activated.

All twenty current agent tool classes are reconciled. The five external-side-effect classes — `external_send`, `crm_write`, `calendar_write`, `file_publish` and `deployment` — remain unavailable and require scoped Founder approval plus idempotency before any future activation.

The exact idempotency-required command set is:

- `cancel_engagement`;
- `execute_external_action`;
- `propose_external_action`;
- `record_agent_output`;
- `record_approval`;
- `release_artefact`;
- `request_approval`.

## Prior-phase regression evidence

The same exact merge reference passed:

- Phase 1 machine-contract validation;
- Phase 2 agent-system validation;
- Phase 3 AI-audit analytical-oracle validation;
- Phase 4 deliverable-semantic-model validation;
- Phase 5 twelve-fixture programme validation;
- Phase 6 knowledge-ingestion intelligence validation;
- Phase 7 security and regionalisation validation;
- PCR-01 canonical release reconciliation;
- PCR-02 test identity and referential integrity;
- PCR-03 repository and governance hygiene;
- PCR-04 machine-readable Codex handoff;
- clean deterministic regeneration across all governed Phase 1–7 and PCR-01–05 records.

Key retained counts:

- registered models: 58;
- requirements: 123;
- executable test nodes: 245;
- planned tests: 54;
- semantic tests: 99;
- reference edges: 604;
- unresolved references: 0;
- controls: 48;
- threats: 20;
- incident playbooks: 12;
- fixtures: 17;
- source profiles: 23;
- repository required files: 18;
- repository workflow invariants: 20;
- PCR-04 read-order files: 17;
- PCR-04 activation conditions: 6;
- PCR-04 mutation cases rejected: 10.

## Runtime and static-analysis evidence

- Pytest: 247 passed in 34.71 seconds.
- Coverage: 93.14 percent across 4,604 statements; required floor 90 percent.
- Python compilation: passed.
- Ruff: all checks passed.
- Strict MyPy: no issues in 32 source files.

## Release artifact

- Artifact ID: `8927677696`
- Artifact name: `offdata-chat-first-release-379c75d283a36f2a63ce2855b917e2b7674d68bb`
- Files: 109
- Size: 263,492 bytes
- ZIP SHA-256: `b6c9209772b856b5932232eb41fd6448f8bac55e6ebed08bc2220cf9f9c8ffff`
- Retention: 30 days
- Hidden governance files: explicitly included.
- PCR-05 source, schema, generated contract, builder, validator, documentation and evidence register: retained.

## Independent review and repairs

The first complete PCR-05 run, `30998606856`, passed all generated-record, phase, runtime and type-check gates but failed Ruff because the new mutation suite used two assigned lambdas. The implementation was repaired without weakening a contract, test or mutation. Run `30998849839` then passed all 35 substantive steps.

A subsequent independent consumer and security review found four material quality defects:

1. external-side-effect approval and idempotency were described semantically but were not conditionally enforced by JSON Schema;
2. the validator did not initially reject transient stacked-pull-request metadata or inconsistent prerequisite readiness checks;
3. the command catalogue is a mapping, but the builder iterated it as a list and falsely reported zero idempotency-required commands instead of seven;
4. the mandatory development-status document stopped at PCR-04 and contradicted the PCR-05 validation and activation sequence.

The repairs added conditional schema enforcement, transient-metadata and readiness mutations, exact cross-contract command-idempotency reconciliation, an eighteenth mutation case, and development-status drift validation. Run `30999593507` validated the repaired state without weakening any prior control.

No unresolved review threads were present at the time of this evidence update.

The runner emitted a non-blocking platform warning that the pinned action versions target Node.js 20 and were forced by GitHub to run on Node.js 24. All actions completed successfully. Dependabot remains configured to surface supported updates.

## Activation boundary

A passing repository gate does not activate a runtime or authorise Codex to start. Every governed activation condition remains required:

1. PCR-03 merged to `main`;
2. PCR-04 retargeted, revalidated and merged to `main`;
3. PCR-05 retargeted, revalidated and merged to the merged PCR-04 base;
4. GitHub-hosted controls in issue #19 verified;
5. explicit Founder Phase 0 approval;
6. a clean macOS development environment.

The first Codex assignment remains Phase 0 only on `codex/phase-0-foundation`, using synthetic data and a draft pull request. `runtime_activation_authorized=false`, `codex_start_authorized=false` and the Phase 1 prohibition remain binding.

## Cost, data, authority and rollback

PCR-05 adds no required paid service or subscription.

Real client data, paid services, production deployment, credential collection, unregistered processors, provider training, cross-tenant execution, external actions and autonomous merge remain prohibited. Founder accountability is preserved.

Before merge, rollback is closing PR #21 and deleting its branch. After merge, rollback is a reviewed revert of the PCR-05 merge commit. PCR-03 governance controls, the PCR-04 handoff and all prior release gates must not be weakened during rollback.
