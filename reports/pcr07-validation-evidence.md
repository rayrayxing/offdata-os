# PCR-07 Validation Evidence

Date: 2026-08-05

PCR-07 Northstar end-to-end integration blueprint, generated machine contract, JSON Schema, cross-contract reconciliation, lifecycle alignment, execution scenarios, mutation rejection and complete prior-phase regression validation.

## Controlling implementation evidence

- Branch: `governance/pcr07-northstar-integration`
- Stacked pull request: `#23 — Complete PCR-07 Northstar end-to-end integration blueprint`
- Tested branch head: `c6e5264ac7ec86f87b88164108bbe3795cdddf64`
- Tested stacked pull-request merge reference: `cfb89e7393655640c6473bcfb343db56939d359f`
- Stacked PCR-06 base: `856252914af5d2504b4c7c018eb64f46d3532788`

### PCR-07 gate

- Workflow run: `31012984306`
- Job: `92329689059`
- Result: all eighteen substantive build, clean-generation, PCR-04–07 validation, runtime, compilation, lint, type-check and artifact steps passed.

### Complete retained release gate

- Workflow run: `31012984329`
- Job: `92329688363`
- Result: all thirty-five substantive Phase 1–7 and PCR-01–05 steps passed on the same exact merge reference.

### Retained Hermes compatibility gate

- Workflow run: `31012984768`
- Job: `92329690344`
- Result: all sixteen substantive PCR-06 and retained PCR-04–05 steps passed on the same exact merge reference.

The pull request is stacked because PCR-03 through PCR-06 remain subject to their governed Founder review and merge sequence. After the prerequisite pull requests merge, PR #23 must be retargeted and the complete exact merge-reference gates must pass again before PCR-07 merge.

## Contract evidence

The deterministic PCR-07 validator reported:

- thirteen lifecycle stages aligned to `LIFE-STAGE-01` through `LIFE-STAGE-13`;
- thirteen exit gates aligned to `GATE-01` through `GATE-13`;
- thirteen integration components;
- twenty governed integration edges;
- seven end-to-end scenarios;
- eight dependency-ordered implementation waves;
- sixteen acceptance obligations;
- twenty-three controlled mutations rejected;
- ten commands and fifteen events reconciled;
- fifty-eight models and eleven agents reconciled;
- thirteen primary fixture types reconciled;
- the existing Northstar analytical oracle grade passed;
- the existing `DSM-DAI-001` / `STORY-DAI-001` semantic grade passed;
- local prerequisite records passed;
- Northstar implementation authorised: false.

The integration path binds the existing synthetic Northstar AI-audit fixture `FIXTURE-DAI-001` to the canonical lifecycle, command/event interfaces, agent roles, PCR-05 runtime boundaries, PCR-06 Hermes restrictions, analytical oracle, semantic story baseline, multi-format delivery boundary, independent quality, Founder approval, implementation records and benefit verification.

Only PostgreSQL structured state and immutable object versions are canonical owners. Runtime checkpoints, agent memory, Hermes memory, tool sessions and chat history remain non-canonical. Every canonical change remains command-only.

## Required scenarios

The governed scenario suite covers:

1. synthetic happy path;
2. restart after the analysis checkpoint;
3. approval wait and resume;
4. blocking quality defect and recycle;
5. idempotent release replay;
6. Founder cancellation;
7. tenant and real-client-data boundary rejection.

The release stage requires a separate independent-quality agent, defect disposition, cross-format reconciliation, scoped approval for the exact version and the idempotent `release_artefact` command. Release remains `internal_synthetic_only`.

## Runtime and static-analysis evidence

The PCR-07 gate passed:

- Pytest: 247 tests passed in 30.20 seconds;
- coverage: 93.14 percent across 4,604 statements against a 90 percent floor;
- Python compilation: passed;
- Ruff: all checks passed;
- strict MyPy: no issues in 32 source files.

The complete retained release workflow independently repeated the full Phase 1–7 and PCR-01–05 generation, validation, runtime and static-analysis sequence. The Hermes workflow independently repeated PCR-06 and its retained PCR-04–05 boundaries.

## Retained artifacts

### PCR-07 blueprint artifact

- Artifact ID: `8933277649`
- Artifact name: `offdata-northstar-blueprint-cfb89e7393655640c6473bcfb343db56939d359f`
- Files: 10
- Size: 29,555 bytes
- ZIP SHA-256: `ba3244c8aa88f544d29ce5c1069a96f33c9c03fe8b0f8ca4ace640d457d7258f`
- Retention: 30 days

### Complete release artifact

- Artifact ID: `8933287566`
- Artifact name: `offdata-chat-first-release-cfb89e7393655640c6473bcfb343db56939d359f`
- Size: 281,135 bytes
- ZIP SHA-256: `51abdc696f72e82668c7ab2721d9f8434fc65c5edefa579acec635909e7086f9`
- Retention: 30 days

## Independent review and repairs

The implementation review found and repaired two defects before the controlling GitHub gates:

1. the initial JSON Schema required at least four outputs per lifecycle stage, but the canonical final stage legitimately has three required outputs; the schema minimum was corrected to three and the complete schema and mutation suite rerun;
2. the initial workflow artifact path used a hyphen instead of an underscore in the PCR-07 validator filename; the retained-evidence path was corrected before the pull-request gates.

Both repairs preserved the canonical lifecycle, exact release controls, all denied activation states and every data, authority, provider, runtime and write boundary. The first exact pull-request gates then passed without further defect.

The runner emitted a non-blocking warning that pinned actions target Node.js 20 and were forced by GitHub to execute on Node.js 24. All actions completed successfully; Dependabot remains configured for supported updates.

## Activation boundary

A passing PCR-07 gate does not authorise implementation or runtime activation. Every condition remains mandatory:

1. PCR-03 merged to `main`;
2. PCR-04 retargeted, revalidated and merged to `main`;
3. PCR-05 retargeted, revalidated and merged through its governed base;
4. PCR-06 retargeted, revalidated and merged after PCR-05;
5. PCR-07 retargeted, revalidated and merged after PCR-06;
6. issue #19 hosted controls verified;
7. explicit Founder Phase 0 approval;
8. clean macOS environment available;
9. any later Northstar implementation phase explicitly approved.

`northstar_implementation_authorized=false`, `runtime_activation_authorized=false`, `hermes_activation_authorized=false` and `codex_start_authorized=false` remain binding.

## Cost, data, authority and rollback

PCR-07 requires no new paid service or subscription. Real client data, external actions, external sending, provider gateways, production deployment, paid services and autonomous merge remain prohibited. Founder accountability is preserved.

Before merge, rollback is closing PR #23 and deleting its branch. After merge, rollback is a reviewed revert of the PCR-07 merge commit without weakening PCR-03 governance, PCR-04 handoff, PCR-05 runtime contracts, PCR-06 Hermes restrictions or any prior release gate.
