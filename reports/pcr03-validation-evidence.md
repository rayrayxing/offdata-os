# PCR-03 Validation Evidence

Date: 2026-08-05

## Scope

PCR-03 repository and governance hygiene:

- repository policy files, ownership rules, templates, and dependency-governance configuration;
- removal of tracked editable-install build metadata;
- deterministic repository-governance source and baseline;
- prohibited-path, case-collision, required-file, and workflow-invariant enforcement;
- complete Phase 1–7 plus PCR-01–03 regression validation;
- independent review and repair before Founder merge approval.

## Controlling implementation evidence

- Branch: `governance/pcr03-repository-hygiene`
- Pull request: `#18 — Complete PCR-03 repository and governance hygiene`
- Tested branch head: `3c14f697c46b2136f3faac3e55da9b2f7b10a02f`
- Tested pull-request merge ref: `bd3fb962441e5d2a611a658b0146a7c4c9ca4c4b`
- Base `main` commit: `cdd3279fa9a57945194794e358eb6780c0f46178`
- GitHub Actions workflow run: `30991977008`
- GitHub Actions job: `92259983894`
- Result: success; all 31 substantive workflow steps passed.

## PCR-03 evidence

The deterministic PCR-03 gate reported:

- required governance files: 18;
- prohibited tracked paths: 0;
- case-colliding paths: 0;
- mandatory workflow invariants: 14;
- real-client-data boundary: false.

The workflow invariants include read-only repository permissions, non-persisted checkout credentials, superseded-run cancellation, exact action commit pins, explicit hidden-file evidence retention, PCR-03 build and validation, and inclusion of the governance baseline in the clean-generation gate.

## Prior-phase regression evidence

The same exact merge ref passed:

- Phase 1 contract validation;
- Phase 2 agent-system validation;
- Phase 3 AI-audit analytical-oracle validation;
- Phase 4 deliverable-semantic-model validation;
- Phase 5 twelve-fixture programme validation;
- Phase 6 knowledge-ingestion intelligence validation;
- Phase 7 security and regionalisation validation;
- PCR-01 canonical release reconciliation;
- PCR-02 semantic test identity and referential integrity.

Key retained counts:

- registered models: 58;
- requirements: 123;
- implemented executable test nodes: 245;
- planned tests: 54;
- semantic tests: 99;
- reference edges: 604;
- unresolved references: 0;
- controls: 48;
- threats: 20;
- incident playbooks: 12;
- fixtures: 17;
- source profiles: 23.

## Runtime and static-analysis evidence

- Pytest: 247 passed in 34.85 seconds.
- Coverage: 93.14% across 4,604 statements; required floor 90%.
- Python compilation: passed.
- Ruff: all checks passed.
- Strict MyPy: no issues in 32 source files.

## Release artifact

- Artifact ID: `8924523892`
- Artifact name: `offdata-chat-first-release-bd3fb962441e5d2a611a658b0146a7c4c9ca4c4b`
- Files: 86
- Size: 198,383 bytes
- ZIP SHA-256: `b1fab90f7f04d98d08594822d27a1752a3f4fb686f574d76d42dfa580bde3a54`
- Retention: 30 days
- Hidden governance files: explicitly included.

## Independent review and repairs

The first PCR-03 workflow run, `30991399805`, correctly failed at the deterministic clean-generation step because the committed governance baseline contained a stale build-script digest. The digest was repaired without weakening the gate.

A later independent review identified that hidden `.github` governance files could be omitted from the release artifact under the upload action's default behaviour. PCR-03 was strengthened to retain hidden files explicitly and to pin all three third-party workflow actions to exact commits. Run `30991977008` validated the repaired state.

The runner emitted a non-blocking platform warning that the pinned action versions target Node.js 20 and were forced by GitHub to run on Node.js 24. The actions completed successfully. Dependabot is configured to surface future supported action updates.

## Pull-request reconciliation

Obsolete Phase 5 pull requests `#11` and `#12` were closed with explicit references to merged PR `#13`, the controlling twelve-fixture implementation. They remain available only as historical development evidence.

## Hosted-setting boundary

Repository files and the available GitHub connector cannot prove or mutate account MFA, branch protection, required-check settings, automatic merged-branch deletion, or delete residual historical branches. Before Codex begins, the Founder must verify:

- MFA is enabled;
- `main` requires pull requests and the complete validation workflow;
- stale approvals are dismissed after new commits;
- review conversations must be resolved;
- force pushes and deletion of `main` are blocked;
- merged head branches are deleted automatically;
- historical branches no longer needed for evidence are removed.

## Cost, data, authority, and rollback

PCR-03 adds no required paid service or subscription. It uses existing GitHub repository capabilities and the current GitHub Actions gate.

Real client data remains prohibited. PCR-03 does not approve infrastructure, processors, external actions, private source import, restricted-oracle exposure, production security, or autonomous merge authority.

Before merge, rollback is closing PR `#18` and deleting its working branch. After merge, rollback is a reviewed revert of the PCR-03 merge commit; hosted settings must be rolled back separately by the Founder only when that does not weaken required security controls.
