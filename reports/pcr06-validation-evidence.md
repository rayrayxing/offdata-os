# PCR-06 Validation Evidence

Date: 2026-08-05

## Scope

PCR-06 governs Hermes Agent adoption compatibility without installing or activating the runtime. It covers the assessed upstream release pin, skills and procedural-memory controls, worker-harness mapping, tool and gateway restrictions, memory boundaries, deterministic generation, schema validation, mutation rejection and complete retained regression compatibility.

## Upstream assessment

- Repository: `NousResearch/hermes-agent`
- Assessed release: `v0.18.2`
- Assessed tag: `v2026.7.7.2`
- Assessed commit: `9de9c25`
- Assessment date: 2026-08-05
- Update policy: pinned review required

## Controlling implementation evidence

- Branch: `governance/pcr06-hermes-compatibility`
- Stacked pull request: `#22 — Complete PCR-06 Hermes adoption and compatibility pack`
- Tested branch head: `5f189d0729c90fcd3351f522c9242306422fabdb`
- Tested stacked merge reference: `3e6851bfb12afc8d052e3b6b8244afa53291dab2`
- Stacked PCR-05 base: `ac5729379ff0e44af9a12a2fb8fd643b10ae2e1d`

### Hermes-specific gate

- Workflow run: `31009349236`
- Job: `92317193875`
- Result: all sixteen substantive build, clean-generation, validation, runtime, compilation, lint, type-check and artifact steps passed.

### Complete retained release gate

- Workflow run: `31009350034`
- Job: `92317215684`
- Result: all thirty-five substantive Phase 1–7 and PCR-01–05 steps passed on the same exact merge reference.

## Contract evidence

The deterministic PCR-06 validator reported:

- compatibility surfaces: 4;
- capability mappings: 5;
- repository skills: 11;
- controlled mutations rejected: 16;
- PCR-05 adapter: `hermes-worker-harness`;
- worker mode: foreground, concurrency 1, isolated branch;
- canonical writes: commands only;
- Hermes memory canonical: false;
- local prerequisites passed: true;
- runtime activation authorised: false;
- Hermes activation authorised: false.

PCR-05 remained green with four adapter kinds, eight profiles, twenty tool classes, eight typed samples, fourteen conformance cases and eighteen rejected mutations. PCR-04 remained green with four Phase 0 tasks, seventeen read-order files, six activation conditions and ten rejected mutations.

## Runtime and static-analysis evidence

The Hermes-specific gate passed:

- Pytest: 247 tests passed in 35.62 seconds;
- coverage: 93.14 percent across 4,604 statements against a 90 percent floor;
- Python compilation: passed;
- Ruff: all checks passed;
- strict MyPy: no issues in 32 source files.

The complete retained release workflow independently repeated the full Phase 1–7 and PCR-01–05 generation, validation, runtime and static-analysis sequence successfully.

## Retained artifacts

### PCR-06 compatibility artifact

- Artifact ID: `8931746527`
- Artifact name: `offdata-hermes-compatibility-3e6851bfb12afc8d052e3b6b8244afa53291dab2`
- Files: 9
- Size: 20,457 bytes
- ZIP SHA-256: `293d891744a2bf543dfb7c764029075179c3a4f2fd1d8623a8aa38930e140690`
- Retention: 30 days

### Complete release artifact

- Artifact ID: `8931759271`
- Artifact name: `offdata-chat-first-release-3e6851bfb12afc8d052e3b6b8244afa53291dab2`
- Size: 271,466 bytes
- ZIP SHA-256: `b1d3276b9423a21127927e2ba6a924018425f538231a0227d5dceb48cde6dec0`
- Retention: 30 days

## Independent review and repairs

The implementation gates found and repaired three defects without weakening adoption restrictions:

1. YAML parsed the assessment date as a date object that was not JSON serialisable; the builder now normalises it deterministically.
2. The first repository-skill compatibility check assumed a Markdown heading at the first byte and conflicted with the governed skill representation.
3. A second format-specific skill check still duplicated Phase 2 validation. PCR-06 now verifies skill presence and substance while the retained Phase 2 validator remains authoritative for detailed skill correctness.

All repairs preserved pinned-review updates, read-only/non-canonical Hermes skill copies, foreground single-worker execution, denied background fan-out, command-only canonical writes, non-canonical memory and every activation blocker.

The runner emitted a non-blocking warning that pinned action versions target Node.js 20 and were forced by GitHub to execute on Node.js 24. All actions completed successfully; Dependabot remains configured for supported updates.

## Activation boundary

A passing compatibility gate does not install or activate Hermes. Every condition remains mandatory:

1. PCR-03 merged to `main`;
2. PCR-04 retargeted, revalidated and merged to `main`;
3. PCR-05 retargeted, revalidated and merged to its governed base;
4. PCR-06 retargeted, revalidated and merged after PCR-05;
5. issue #19 hosted controls verified;
6. explicit Founder Phase 0 approval;
7. clean macOS environment available;
8. pinned Hermes version and checksum verified;
9. isolated synthetic-data Hermes sandbox conformance passed.

`runtime_activation_authorized=false`, `hermes_activation_authorized=false` and `codex_start_authorized=false` remain binding.

## Cost, data, authority and rollback

PCR-06 requires no new paid service or subscription. Provider gateways, OAuth, messaging channels, background delegation, autonomous skill or memory writes, `/yolo`, real client data, production deployment, external actions and autonomous merge remain prohibited. Founder accountability is preserved.

Before merge, rollback is closing PR #22 and deleting its branch. After merge, rollback is a reviewed revert of the PCR-06 merge commit without weakening PCR-03 governance, PCR-04 handoff, PCR-05 runtime contracts or any prior release gate.
