# 37 — Phase 5 Additional Engagement Fixtures Completion

## Status

**Chat-first Phase 5: complete and independently CI-validated on the review branch.**

Date: 2026-08-04

This phase adds the next two primary engagement fixtures in the governed synthetic-engagement sequence:

1. `FIXTURE-STRAT-001` — corporate strategy, portfolio and capital allocation;
2. `FIXTURE-COST-001` — cost and productivity transformation.

Together with the existing Northstar digital-and-AI audit, offdata now has three built primary fixtures out of the governed thirteen-primary-fixture programme. Phase 5 does not claim that the remaining ten primary fixtures or five compound fixtures have been built.

## 1. Governing fixture contract

Both fixtures follow the same controlled architecture:

- one synthetic company and bounded decision mandate;
- deterministic client-visible evidence inputs;
- a source manifest with stable source identifiers and trust classifications;
- a data dictionary;
- interviews and controlled operational or financial datasets;
- scenario, option or initiative records;
- implementation-roadmap and benefits records;
- CRM context;
- one explicitly untrusted source containing adversarial instructions;
- a restricted expected-results record;
- a restricted byte-reproducible evaluation baseline;
- an independent deterministic grader;
- mutation, stale-baseline, traceability and isolation tests.

Each fixture contains fourteen agent-visible inputs. The two restricted files, `expected-results.yaml` and `fixture-baseline.json`, are marked `agent_visible: false`, excluded from generation context and blocked by the normal-context isolation controls.

Client-visible fixture inputs are reproducibly generated using fixed seeds:

- corporate strategy: `41001`;
- cost and productivity: `43001`.

The generation script may recreate the client-visible inputs but cannot overwrite the restricted answer material.

## 2. Corporate strategy fixture

`FIXTURE-STRAT-001` concerns HarborPeak's portfolio and capital-allocation decision.

The governing decision is which business units to invest in, restructure, partner, divest or close. The fixture deliberately creates a superficially attractive Energy Systems growth story while ownership advantage, returns and downside evidence remain weak. It also includes allocated overhead, uncertain divestiture proceeds, incomplete digital evidence and an adversarial vendor memo.

### Decision result

The deterministic recommendation selects:

- `ACT-STR-001`;
- `ACT-STR-003`;
- `ACT-STR-006`;
- `ACT-STR-009`;
- `ACT-STR-012`.

The credible alternative preserves:

- `ACT-STR-001`;
- `ACT-STR-004`;
- `ACT-STR-005`;
- `ACT-STR-009`;
- `ACT-STR-012`.

The analysis keeps recommendation and alternative action sets separate and requires the implementation roadmap to trace to the selected recommendation. A mutation that changes the recommendation while leaving the roadmap stale fails closed rather than silently accepting an inconsistent implementation record.

### Reconciled analytical outputs

The controlled result includes:

- revenue: SGD 148 million;
- EBITDA: SGD 18 million;
- capital employed: SGD 139 million;
- value-destroying capital employed: SGD 69 million;
- highest business-unit ROIC: 24 percent;
- gross investment requirement: SGD 23 million;
- estimated divestiture proceeds: SGD 5 million;
- net capital commitment: SGD 18 million;
- base-case portfolio NPV: SGD 54 million;
- downside portfolio NPV: SGD 8 million;
- scenario probabilities reconciling to 100 percent.

The grader prevents growth rate, market attractiveness or allocated overhead from being used as substitutes for ownership advantage, relevant economics, returns, downside resilience and capital constraints.

### Method selection

The selected strategy method stack uses the provided methodology-reference identifiers:

- `STR-01`;
- `STR-07`;
- `STR-09`;
- `STR-10`;
- `STR-13`;
- `STR-14`.

Recorded method rejections are:

- `GENERIC-PORTFOLIO-MATRIX`;
- `STR-02-ALONE`;
- `STR-11-AS-GOVERNING-METHOD`.

The original methodology reference document is not committed. Only governed method identifiers and fixture-specific selection or rejection logic appear in the repository.

## 3. Cost and productivity fixture

`FIXTURE-COST-001` concerns Meridian's recurring-cost and productivity decision.

The fixture tests relevant-cost analysis, activity and practical-capacity analysis, failure demand, flow, service constraints, benefit classification and implementation ownership. It deliberately presents a uniform headcount reduction and treats released hours and allocated overhead as cash savings. Controlled evidence instead shows high peak utilisation, repeat visits, closure-code defects and overlapping route and dispatch benefits.

### Decision result

The deterministic recommendation selects:

- `ACT-COST-001`;
- `ACT-COST-002`;
- `ACT-COST-003`;
- `ACT-COST-005`.

The credible alternative preserves:

- `ACT-COST-001`;
- `ACT-COST-002`;
- `ACT-COST-005`.

The controlled result rejects:

- `ACT-COST-004`;
- `ACT-COST-006`.

The fixture therefore distinguishes practical process and demand interventions from unsupported blanket headcount reduction.

### Reconciled analytical outputs

The controlled result includes:

- total site cost: SGD 37,090,000;
- allocated overhead: SGD 4,350,000;
- controllable cost: SGD 32,740,000;
- annual jobs: 68,400;
- unit cost: SGD 478.654971;
- failure-demand hours: 24,418.8;
- peak utilisation: 97 percent;
- weighted first-time-fix rate: 78.646199 percent;
- gross recurring cash savings: SGD 1,270,000;
- overlapping savings removed: SGD 120,000;
- net recurring cash savings: SGD 810,000;
- one-time implementation cost: SGD 1,100,000;
- released capacity: 18,000 hours;
- cost avoidance: SGD 450,000;
- payback: 16.296296 months;
- immediate cash-releasing headcount benefit: SGD 0.

The grader prevents allocated overhead, released hours and overlapping initiatives from being counted as additive cash savings.

### Method selection

The selected cost and productivity method stack uses the provided methodology-reference identifiers:

- `C&P-01`;
- `C&P-02`;
- `C&P-06`;
- `C&P-07`;
- `C&P-09`;
- `C&P-16`.

Recorded method rejections are:

- `BROAD-HEADCOUNT-BENCHMARK`;
- `C&P-08`;
- `C&P-12-ALONE`.

The original methodology reference document is not committed. Only governed method identifiers and fixture-specific selection or rejection logic appear in the repository.

## 4. Source integrity and adversarial controls

Across the two fixtures:

- 28 client-visible inputs are independently checksummed;
- 22 source records are registered;
- source identifiers are unique within each fixture;
- trusted, unverified and untrusted material remain distinguishable;
- the adversarial source is deterministically marked untrusted;
- instruction-like content in an untrusted source is ignored;
- restricted answer material is never required to construct the analytical result;
- restricted baselines and expected results are blocked from normal agent context.

Missing required files, malformed manifests, duplicate identifiers and inconsistent roadmap references fail closed.

## 5. Independent grading and mutation evidence

The two independent fixture graders perform 144 deterministic checks in total.

Checks cover:

- fixture identity and version;
- exact source-input digests;
- selected recommendation and credible alternative;
- rejected actions;
- reconciled financial and operating metrics;
- method selections and rejections;
- scenario or initiative logic;
- implementation traceability;
- benefits classification;
- prohibited conclusions;
- untrusted-source controls;
- restricted-material isolation;
- byte reproducibility.

Mutation tests verify that changed source economics, changed action recommendations, stale baselines, broken roadmap traceability, missing files and restricted answer material in normal context are detected rather than silently normalised.

## 6. Requirement and test traceability

Phase 5 adds twenty-two mapped executable test nodes.

The combined test registry now records:

- 168 implemented test nodes;
- 57 remaining planned test nodes;
- 15 previously planned test IDs completed across the chat-first phases;
- all 123 catalogue requirements mapped to implemented or planned evidence.

`E2E-PRIMARY-FIXTURES-001` correctly remains planned because the complete thirteen-primary-fixture programme is not yet built.

## 7. Independent validation evidence

GitHub Actions run `30930577653`, job `92063920986`, validated branch head `6fd5e6a7e8647d85e5ca72bb3059dccce533a2ad` through pull-request merge reference `fd001f4fc9e82d3ecc1c449baf3be4ce820bcacc` on Ubuntu 24.04 and Python 3.11.15.

### Phase 5 validator

```text
PHASE 5 ADDITIONAL ENGAGEMENT FIXTURE VALIDATION PASSED
- additional_fixtures=2
- built_primary_fixtures=3
- agent_visible_inputs=28
- source_records=22
- calculated_metrics=27
- recommendation_actions=9
- credible_alternative_actions=8
- method_selections=12
- method_rejections=6
- grade_checks=144
- phase5_implemented_test_nodes=22
```

### Complete Phase 1–5 quality gate

- Phase 1 contract validator: passed;
- Phase 2 agent-system validator: passed;
- Phase 3 analytical-oracle validator: passed;
- Phase 4 deliverable-semantic validator: passed;
- Phase 5 additional-fixture validator: passed;
- clean regeneration of the test registry and all governed Phase 3–5 baselines and fixture inputs: passed;
- runtime tests: 170 passed;
- total code coverage: 92.84 percent;
- mandatory coverage floor: 90 percent;
- Python compilation: passed;
- Ruff: passed;
- strict MyPy: passed with no issues across 28 source files.

### Retained release artefact

- files: 69;
- artefact ID: `8900963732`;
- compressed size: 111,836 bytes;
- SHA-256: `7130726a853a1e73328cdb49ff1feea05d3e365be019052e6a75f984583d5e9e`;
- retention: 30 days.

## 8. Explicit boundary and remaining fixture programme

Phase 5 establishes three of the thirteen primary fixtures:

- digital and AI transformation or audit;
- corporate strategy;
- cost and productivity.

It does not establish completion of the remaining primary fixtures for growth and commercial strategy, customer experience, operating model, organisation and workforce, risk and controls, M&A and integration, carve-out, IPO and capital strategy, implementation and change, or benefits realisation and performance improvement. Compound fixtures also remain future work.

It also does not claim live-client validation, production data ingestion, rendered deliverables for the two new fixtures or Founder acceptance of their future client-facing outputs.

## 9. Phase-gate conclusion

Phase 5 is complete as the next governed tranche of the synthetic engagement suite. The corporate-strategy and cost-productivity fixtures are deterministic, independently graded, adversarially tested, traceable to selected methodology identifiers, reproducible without their restricted answer material and protected by the complete Phase 1–5 CI gate.
