# PCR-04 Validation Evidence

Date: 2026-08-05

## Scope

PCR-04 machine-readable Codex handoff, prerequisite reconciliation, stale kickoff repair, deterministic generation, schema validation, semantic validation, mutation rejection and complete Phase 1–7 plus PCR-01–04 regression validation.

## Controlling implementation evidence

- Branch: `governance/pcr04-codex-handoff`
- Stacked pull request: `#20 — Complete PCR-04 machine-readable Codex handoff`
- Tested branch head: `f10f4ab8bd78029ebd30f0fa3b1222f8988c9770`
- Tested pull-request merge reference: `ff5ebc954ac6f12a17adb40ba7b080cb8cf493ec`
- Stacked base: PCR-03 head `0533af187c9c4a4cee666cbfa6ff647a6847bc97`
- GitHub Actions run: `30994678287`
- GitHub Actions job: `92268792367`
- Result: success; all 33 substantive workflow steps passed.

The pull request is stacked because PCR-03 remains subject to Founder merge approval. After PCR-03 merges, PR #20 must be retargeted to `main` and the complete exact merge-reference gate must pass again before PCR-04 merge.

## PCR-04 handoff evidence

The deterministic PCR-04 gate reported:

- Phase 0 tasks: 4;
- read-order files: 15;
- activation conditions: 5;
- controlled mutation cases rejected: 8;
- local prerequisite records passed: true;
- Codex start authorised: false.

The machine contract contains the instruction precedence, prerequisite records, existing governed assets, P0.1–P0.4 dependency graph, root-executable command set, canonical Phase 0 branch, draft-pull-request rule, prohibited actions, stop conditions, completion-report fields and immutable authority boundaries.

The eight rejected mutations cover:

1. Phase 1 escalation;
2. autonomous Codex activation;
3. external-action enablement;
4. duplicate Phase 0 task identity;
5. a task dependency cycle;
6. removal of the PCR-04 validation command;
7. removal of the package working directory from the test command;
8. insertion of transient stacked-pull-request metadata into the canonical handoff.

## Prior-phase regression evidence

The same exact merge reference passed:

- Phase 1 contract validation;
- Phase 2 agent-system validation;
- Phase 3 AI-audit analytical-oracle validation;
- Phase 4 deliverable-semantic-model validation;
- Phase 5 twelve-fixture programme validation;
- Phase 6 knowledge-ingestion intelligence validation;
- Phase 7 security and regionalisation validation;
- PCR-01 canonical release reconciliation;
- PCR-02 test identity and referential integrity;
- PCR-03 repository and governance hygiene;
- clean deterministic regeneration across all governed Phase 1–7 and PCR-01–04 records.

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
- repository workflow invariants: 17.

## Runtime and static-analysis evidence

- Pytest: 247 passed in 19.64 seconds.
- Coverage: 93.14 percent across 4,604 statements; required floor 90 percent.
- Python compilation: passed.
- Ruff: all checks passed.
- Strict MyPy: no issues in 32 source files.

## Release artifact

- Artifact ID: `8925636004`
- Artifact name: `offdata-chat-first-release-ff5ebc954ac6f12a17adb40ba7b080cb8cf493ec`
- Files: 101
- Size: 238,764 bytes
- ZIP SHA-256: `4acd32ebaa6d7a22e2d01fbef34f38eba58d07ba71132155717a66fd843e7694`
- Retention: 30 days
- Hidden governance files: explicitly included.
- PCR-04 source, schema, generated handoff, validator, kickoff documentation and evidence register: retained.

## Independent review and repairs

The first complete stacked implementation run, `30993955051`, passed the initial 33-step gate. A subsequent independent consumer-oriented review found three handoff-quality defects:

1. the package test and MyPy commands relied on an unstated working directory and would not be reliably executable from repository root;
2. the generated canonical handoff retained the temporary PCR-03 stacked branch name, which could become stale after merge and branch deletion;
3. the mandatory development-status document omitted PCR-03 and PCR-04 and did not describe the required merge and activation sequence.

The repairs made package commands root-executable, prohibited transient pull-request metadata, added two negative mutation cases and reconciled the development-status ledger. Run `30994678287` validated the repaired state without weakening any prior control.

The runner emitted a non-blocking platform warning that the pinned action versions target Node.js 20 and were forced by GitHub to run on Node.js 24. All actions completed successfully. Dependabot remains configured to surface supported updates.

## Activation boundary

A passing repository gate does not authorise Codex to start. Every governed activation condition remains required:

1. PCR-03 merged to `main`;
2. PCR-04 retargeted, revalidated and merged to `main`;
3. GitHub-hosted controls in issue #19 verified;
4. explicit Founder Phase 0 approval;
5. a clean macOS development environment.

The first Codex assignment remains Phase 0 only on `codex/phase-0-foundation`, using synthetic data and a draft pull request. Phase 1 progression is prohibited.

## Cost, data, authority and rollback

PCR-04 adds no required paid service or subscription.

Real client data, paid services, production deployment, processors, OAuth, DNS changes, external communications, restricted-oracle exposure and autonomous merge remain prohibited. Founder accountability is preserved.

Before merge, rollback is closing PR #20 and deleting its branch. After merge, rollback is a reviewed revert of the PCR-04 merge commit. PCR-03 governance controls and prior release gates must not be weakened during rollback.
