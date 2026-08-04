# 37 — Phase 5 Additional Engagement Fixtures Completion

## Status

**Chat-first Phase 5: complete and independently CI-validated.**

Date: 2026-08-05

Phase 5 implements the next two primary fixtures in the canonical suite build order: corporate strategy and cost/productivity. Together with the existing AI-audit fixture, offdata now has three governed primary engagement evidence rooms spanning materially different consulting patterns.

## Delivered fixtures

### FIXTURE-STRAT-001 — Meridian portfolio and capital allocation

The fictional Singapore industrial group must allocate a binding SGD 95 million capital envelope across five businesses whose requests total SGD 143 million. The fixture tests portfolio economics, corporate advantage, market and competitive position, option value, capital allocation and implementation feasibility.

It includes 25 structured evidence rows, conflicting return definitions, missing and stale evidence, management advocacy, an adversarial untrusted source, restricted expected results, explicit acceptable alternatives, specialist boundaries and Founder decisions.

### FIXTURE-COST-001 — HarbourCare cost and productivity transformation

The fictional field-service company must determine where recurring cost can be removed without damaging service, safety or resilience. The fixture tests cost decomposition, demand-process-capacity analysis, avoidability, productivity, initiative economics and benefit governance.

It includes 24 structured evidence rows, conflicting operational definitions, missing and stale evidence, a malicious benchmark source, restricted expected results and explicit separation of gross capacity, cost avoidance, avoidable cost and cash-releasing benefit.

## Shared fixture contract

`offdata_core.fixture_suite` now enforces:

- fictional identity and explicit difficulty;
- complete mandate, stakeholders, constraints and exclusions;
- required source manifest and client-visible evidence files;
- unique source identifiers and manifest-file integrity;
- at least one explicitly untrusted source;
- structured evidence schema and deliberate quality variation;
- restricted `expected-results.yaml` isolation from normal agent context;
- minimum method stack, calculation oracle, delivery oracle and complete defect pack;
- deterministic per-fixture input digests and suite digest.

The two restricted oracles are marked `agent_visible: false` and are absent from source manifests and normal context allowlists.

## Tests and failure behaviour

Phase 5 adds 13 mapped executable test nodes covering successful validation, deterministic digests, mandate completeness, fictional identity, restricted-material isolation, source integrity, untrusted inputs, evidence-quality variation, strategy and cost decision requirements, and fail-closed mutations for missing files, unknown sources and answer-key leakage.

The suite fails rather than silently normalising when:

- a required source is missing;
- an evidence row references an unknown source;
- the restricted oracle appears in a client source manifest;
- a fixture is not declared fictional;
- expected results are marked agent-visible;
- source IDs duplicate;
- evidence lacks required fields or quality variation.

## Independent validation

GitHub Actions run `30930102434`, job `92062300431`, validated branch head `7770ef59c6cef2f67a9ba72104cecb8a93ff33b9` on Ubuntu 24.04 and Python 3.11.15.

```text
PHASE 5 ADDITIONAL ENGAGEMENT FIXTURE VALIDATION PASSED
- fixtures=2
- strategy_sources=5
- strategy_evidence_rows=25
- cost_sources=5
- cost_evidence_rows=24
- checks=24
- suite_digest=472bb9c7ed62a3e4c83521e907809043d5f2fc6c063d86d5aedd14adbd225ff2
- restricted_oracles=2
- answer_key_leaks=0
- untrusted_sources=2
```

Complete Phase 1–5 gate:

- Phase 1 contract validator: passed;
- Phase 2 agent-system validator: passed;
- Phase 3 analytical-oracle validator: passed;
- Phase 4 semantic-model validator: passed;
- Phase 5 fixture validator: passed;
- clean regeneration of the test registry and restricted Phase 3–4 baselines: passed;
- implemented test nodes: 159;
- remaining planned tests: 57;
- all 123 catalogue requirements mapped;
- runtime tests: 161 passed;
- total coverage: 93.14 percent against a 90 percent floor;
- Python compilation: passed;
- Ruff: passed;
- strict MyPy: passed across 28 source files.

Retained release artefact:

- files: 51;
- artefact ID: `8900770925`;
- compressed size: 90,648 bytes;
- SHA-256: `b7a424511125e3173428b2c6d049b90a68e56b61be80dbe061539deb7741b20e`;
- retention: 30 days.

## Explicit boundary

Phase 5 does not complete the synthetic engagement suite. Current primary-fixture coverage is:

1. `FIXTURE-DAI-001` — AI opportunity, value and risk audit;
2. `FIXTURE-STRAT-001` — corporate portfolio and capital allocation;
3. `FIXTURE-COST-001` — cost and productivity transformation.

Ten primary fixtures and all five compound fixtures remain to be built. No full-engagement agent execution, physical deliverable generation or all-primary end-to-end result is claimed. `E2E-PRIMARY-FIXTURES-001` and `E2E-COMPOUND-FIXTURES-001` remain planned until their complete scopes exist and pass.

## Gate conclusion

Phase 5 is complete as the governed strategy-and-cost fixture tranche. The fixture contract and failure tests provide the reusable standard for the remaining primary and compound evidence rooms without exposing restricted answer keys or weakening prior Phase 1–4 controls.
