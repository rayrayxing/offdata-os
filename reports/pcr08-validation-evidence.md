# PCR-08 Validation Evidence

Date: 2026-08-05

PCR-08 initial operating-control source, generated machine contract, JSON Schema, full security-control assignment, authority and activation gates, switch configuration, cost and provider posture, incident and retention reconciliation, evidence-state honesty, mutation rejection and prior-phase regression validation.

## Controlling implementation evidence

- Branch: `governance/pcr08-initial-operating-controls`
- Stacked pull request: `#24 — Complete PCR-08 initial operating-control configuration`
- Tested implementation head: `4debf217dd794c3ab75dfc1571dcb831d9fe875c`
- Tested stacked pull-request merge reference: `5ce49458a76056c4e9ea65ebb35067163eb0bca0`
- Stacked PCR-07 base: `7ac87d4b6dbbf2ba6741757c36d83ad081a51bfe`

### PCR-08 gate

- Workflow run: `31018666893`
- Job: `92349368427`
- Result: all twenty substantive deterministic build, clean-generation, PCR-04–08 validation, runtime, compilation, lint, type-check and artifact-retention steps passed.

### PCR-07 retained gate

- Workflow run: `31018664184`
- Job: `92349360774`
- Result: all eighteen substantive PCR-07 and retained PCR-04–06 steps passed on the same exact merge reference.

### Hermes retained gate

- Workflow run: `31018664317`
- Job: `92349359042`
- Result: all sixteen substantive PCR-06 and retained PCR-04–05 steps passed on the same exact merge reference.

### Complete retained release gate

- Workflow run: `31018664040`
- Job: `92349358352`
- Result: all thirty-five substantive Phase 1–7 and PCR-01–05 steps passed on the same exact merge reference.

The pull request is stacked because PCR-03 through PCR-07 remain subject to their governed Founder review and merge sequence. After prerequisite merges, PR #24 must be retargeted and the complete exact merge-reference gates must pass again before PCR-08 merge.

## Contract evidence

The deterministic PCR-08 validator reported:

- decision classes: 6;
- operating-control domains: 10;
- security controls assigned exactly once: 48;
- mandatory controls for any future real-client-data gate: 18;
- unauthorised operating gates: 8;
- fail-closed switches initially denied: 6;
- incident playbooks: 12;
- retention policies: 4;
- agent budget profiles: 6;
- commands requiring idempotency: 7;
- approved real-client processors: 0;
- configured operating cadences: 7;
- controlled mutations rejected: 39;
- local prerequisite records passed: true;
- initial operating-control activation authorised: false.

The configuration is Founder-only, local, synthetic, Singapore-first and limited to public and internal data. Canonical writes remain command-only. Network access denies by default, the paid-provider hard cap is zero, and every provider, credential, processor, external-action, production and merge boundary remains disabled.

All forty-eight Phase 7 security controls are assigned exactly once across identity and access, data and region, secrets and supply chain, runtime and agent use, canonical workflow integrity, decision and release authority, backup and retention, processors, incidents, and environment/change control.

## PCR-04 handoff reconciliation

The same exact merge reference validated the expanded machine-readable Codex handoff with:

- four Phase 0 tasks;
- twenty-three mandatory read-order files;
- eight prerequisite records;
- nine activation conditions;
- fifteen controlled mutations rejected;
- `codex_start_authorized=false`.

PCR-06, PCR-07 and PCR-08 are now explicit prerequisites. The handoff preserves every inactive runtime, Hermes, Northstar and operating-control state, and records hosted, operating-environment and production evidence as incomplete.

## Runtime and static-analysis evidence

The PCR-08 gate passed:

- Pytest: 247 tests passed in 35.34 seconds;
- coverage: 93.14 percent across 4,604 statements, with 316 missed, against a 90 percent floor;
- Python compilation: passed;
- Ruff: all checks passed;
- strict MyPy: no issues in 32 source files.

The complete retained release workflow independently repeated the full Phase 1–7 and PCR-01–05 generation, validation, runtime and static-analysis sequence. The PCR-07 and Hermes workflows independently repeated their retained prerequisite boundaries.

## Retained artifacts

### PCR-08 operating-control artifact

- Artifact ID: `8935642446`
- Artifact name: `offdata-initial-operating-controls-5ce49458a76056c4e9ea65ebb35067163eb0bca0`
- Files: 15
- Size: 49,985 bytes
- ZIP SHA-256: `19c70052b404b30720a71a0e16edf8727c3793bb0e687ff4bf042cbb8abd4c03`
- Retention: 30 days

### Complete release artifact

- Artifact ID: `8935656236`
- Artifact name: `offdata-chat-first-release-5ce49458a76056c4e9ea65ebb35067163eb0bca0`
- Size: 294,893 bytes
- ZIP SHA-256: `abc50fbfd0a71cf6f81002c6057396a0bc1481f0a65b3e0432154d9b07e82db7`
- Retention: 30 days

## Independent review and repairs

The implementation review found and repaired two quality defects before the controlling gates:

1. the first generated projection duplicated verbose security-catalogue evidence already governed by the canonical source and cross-contract builder, creating unnecessary review and schema surface; the generated contract was compacted while retaining every control assignment and deterministic catalogue reconciliation;
2. the PCR-08 mutation validator contained two nested-function spacing defects that would fail Ruff despite successful Python compilation; both were repaired and the validator rerun before opening the pull request.

The compact projection, source contract, schema and validator were rerun together. No security control, evidence requirement, activation blocker, data boundary, authority boundary, provider restriction or mutation was removed or weakened.

The runner emitted a non-blocking warning that pinned actions target Node.js 20 and were forced by GitHub to execute on Node.js 24. All actions completed successfully; Dependabot remains configured for supported updates.

## Evidence boundary

Chat-first configuration evidence is current. Hosted controls, operating-environment evidence, backup and restore evidence, measured recovery objectives and production evidence remain incomplete. Passing PCR-08 does not activate an operating environment and must not be represented as production evidence.

## Activation boundary

Every condition remains mandatory:

1. PCR-03 merged to `main`;
2. PCR-04 retargeted, revalidated and merged to `main`;
3. PCR-05 retargeted, revalidated and merged through its governed base;
4. PCR-06 retargeted, revalidated and merged after PCR-05;
5. PCR-07 retargeted, revalidated and merged after PCR-06;
6. PCR-08 retargeted, revalidated and merged after PCR-07;
7. issue #19 hosted controls verified;
8. explicit Founder Phase 0 approval;
9. a clean macOS environment.

`initial_operating_controls_activation_authorized=false`, `codex_start_authorized=false`, `runtime_activation_authorized=false`, `hermes_activation_authorized=false` and `northstar_implementation_authorized=false` remain mandatory.

## Cost, data, authority and rollback

PCR-08 requires no new paid service or subscription. Real client data, external actions, paid services, production deployment, provider gateways, OAuth, credential values and autonomous merge remain prohibited. Founder accountability is preserved.

Before merge, rollback is closing PR #24 and deleting its branch. After merge, rollback is a reviewed revert of the PCR-08 merge commit without weakening PCR-03 governance, PCR-04 handoff, PCR-05 runtime contracts, PCR-06 Hermes restrictions, PCR-07 Northstar boundaries or any prior release gate.
