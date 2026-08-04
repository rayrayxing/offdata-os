# Phase 5 independent validation evidence

## Status

**PASS** — Phase 1 contract, Phase 2 agent-system, Phase 3 analytical-oracle, Phase 4 deliverable-semantic and Phase 5 additional-fixture gates completed successfully.

Date: 2026-08-04

## GitHub Actions evidence

- workflow: `Machine contracts, agents, oracle, semantic deliverables and fixtures`
- run ID: `30930577653`
- job ID: `92063920986`
- validated branch head: `6fd5e6a7e8647d85e5ca72bb3059dccce533a2ad`
- validated pull-request merge reference: `fd001f4fc9e82d3ecc1c449baf3be4ce820bcacc`
- runner: Ubuntu 24.04
- Python: 3.11.15
- conclusion: success

Completion and development-status documentation is added after this evidence run. The complete pull-request gate is rerun with those documentation commits included before the PR is offered for Founder review.

## Fixture-programme scope

Phase 5 adds the next two primary fixtures in the governed sequence:

- `FIXTURE-STRAT-001` — HarborPeak portfolio and capital allocation;
- `FIXTURE-COST-001` — Meridian recurring cost and productivity.

The existing digital-and-AI audit plus these two fixtures bring the built primary-fixture count to three out of thirteen. The complete primary and compound fixture programme is not represented as complete.

## Corporate strategy fixture result

- deterministic visible-input seed: `41001`
- agent-visible inputs: 14
- selected actions: `ACT-STR-001`, `ACT-STR-003`, `ACT-STR-006`, `ACT-STR-009`, `ACT-STR-012`
- credible alternative: `ACT-STR-001`, `ACT-STR-004`, `ACT-STR-005`, `ACT-STR-009`, `ACT-STR-012`
- revenue: SGD 148 million
- EBITDA: SGD 18 million
- capital employed: SGD 139 million
- value-destroying capital employed: SGD 69 million
- highest business-unit ROIC: 24 percent
- gross investment: SGD 23 million
- divestiture proceeds: SGD 5 million
- net capital commitment: SGD 18 million
- base portfolio NPV: SGD 54 million
- downside portfolio NPV: SGD 8 million
- scenario probability total: 100 percent
- method selections: `STR-01`, `STR-07`, `STR-09`, `STR-10`, `STR-13`, `STR-14`
- method rejections: `GENERIC-PORTFOLIO-MATRIX`, `STR-02-ALONE`, `STR-11-AS-GOVERNING-METHOD`

The validation confirms that growth attractiveness does not override parenting advantage, ownership economics, returns, downside resilience or capital constraints. Changed recommendation actions invalidate a stale implementation roadmap.

## Cost and productivity fixture result

- deterministic visible-input seed: `43001`
- agent-visible inputs: 14
- selected actions: `ACT-COST-001`, `ACT-COST-002`, `ACT-COST-003`, `ACT-COST-005`
- credible alternative: `ACT-COST-001`, `ACT-COST-002`, `ACT-COST-005`
- rejected actions: `ACT-COST-004`, `ACT-COST-006`
- total site cost: SGD 37,090,000
- allocated overhead: SGD 4,350,000
- controllable cost: SGD 32,740,000
- annual jobs: 68,400
- unit cost: SGD 478.654971
- failure-demand hours: 24,418.8
- peak utilisation: 97 percent
- weighted first-time-fix rate: 78.646199 percent
- gross recurring cash savings: SGD 1,270,000
- overlapping savings removed: SGD 120,000
- net recurring cash savings: SGD 810,000
- one-time implementation cost: SGD 1,100,000
- released capacity: 18,000 hours
- cost avoidance: SGD 450,000
- payback: 16.296296 months
- immediate cash-releasing headcount benefit: SGD 0
- method selections: `C&P-01`, `C&P-02`, `C&P-06`, `C&P-07`, `C&P-09`, `C&P-16`
- method rejections: `BROAD-HEADCOUNT-BENCHMARK`, `C&P-08`, `C&P-12-ALONE`

The validation confirms that allocated overhead, released hours and overlapping initiatives cannot be counted as additive cash savings, and that blanket headcount reduction is not supported while capacity and service constraints remain material.

## Source and restricted-material controls

Across the two fixtures:

- agent-visible inputs: 28
- registered source records: 22
- source identifiers are unique within their fixture
- all visible inputs are checksummed
- each aggregate input digest is stable
- untrusted sources are explicitly classified
- adversarial instruction content is ignored
- external action from untrusted content is blocked
- expected-result and fixture-baseline files are marked `agent_visible: false`
- restricted material is unnecessary for analysis construction
- restricted material in normal context fails
- client-visible generation cannot overwrite restricted evaluation files

## Independent grade and mutation evidence

- calculated metrics: 27
- recommendation actions: 9
- credible-alternative actions: 8
- method selections: 12
- method rejections: 6
- independent grade checks: 144

Mutation and negative tests cover:

- changed strategy economics;
- changed cost assumptions;
- changed recommendation actions;
- stale implementation-roadmap references;
- stale restricted baselines;
- missing fixture inputs;
- malformed manifests;
- duplicate source identifiers;
- restricted evaluation material in normal context;
- prohibited conclusions;
- untrusted-source instruction handling.

## Prior-phase regression results

### Phase 1

- generated contract files: 8
- registered models: 58
- governed configurations: 4
- OpenAPI paths: 26
- commands: 10
- events: 15
- requirements in catalogue: 123
- implemented test nodes: 168
- planned test nodes: 57
- PostgreSQL migration lines inspected: 396

### Phase 2

- bounded agents: 11
- skill packages: 11
- context profiles: 11
- budget profiles: 6
- provider routes: 3
- evaluation profiles: 11
- evaluation cases: 33
- mandatory admission failures: 8

### Phase 3

- client-visible inputs: 14
- source documents: 15
- evidence findings: 6
- required method roles: 8
- method rejections: 4
- independent oracle checks: 74

### Phase 4

- story sections: 8
- assertions: 12
- named numbers: 18
- citations: 6
- visual specifications: 6
- semantic objects: 12
- surface plans: 6
- surface objects: 55
- independent semantic checks: 115

## Complete deterministic quality gate

- Phase 1 validator: passed
- Phase 2 validator: passed
- Phase 3 validator: passed
- Phase 4 validator: passed
- Phase 5 validator: passed
- clean generated-record gate: passed
- runtime tests: 170 passed
- total code coverage: 92.84 percent
- enforced coverage floor: 90 percent
- Python compilation: passed
- Ruff: passed
- strict MyPy: passed across 28 source files

## Requirement traceability

- catalogue requirements: 123
- implemented test nodes: 168
- remaining planned test nodes: 57
- completed planned-test IDs: 15
- Phase 5 executable test nodes added: 22
- all requirements mapped to implemented or planned evidence

`E2E-PRIMARY-FIXTURES-001` remains planned because ten primary fixtures remain unbuilt.

## Retained release artefact

- files: 69
- artefact ID: `8900963732`
- compressed size: 111,836 bytes
- SHA-256: `7130726a853a1e73328cdb49ff1feea05d3e365be019052e6a75f984583d5e9e`
- retention: 30 days

The retained release includes generated contracts, complete requirement traceability, agent skill packages, the Phase 3 oracle, Phase 4 semantic baseline, both new Phase 5 fixture packs and their restricted reproducible baselines.

## Boundary

This evidence validates synthetic evidence-room construction, deterministic analysis, independent grading and regression protection. It does not validate live client data, production ingestion, physical deliverables for the two new engagements, the remaining ten primary fixtures, compound fixtures or Founder acceptance of future client-facing outputs.

## Gate conclusion

Phase 5 passes as the next controlled fixture tranche. Corporate strategy and cost and productivity are now independently reproducible engagement fixtures, and all prior chat-first components remain green under the combined Phase 1–5 gate.
