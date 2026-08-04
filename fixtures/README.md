# Synthetic Engagement Fixture Library

## Purpose

Fixtures are controlled synthetic engagements used to test the complete offdata lifecycle, method selection, evidence handling, quantitative analysis, deliverable semantics, implementation planning and benefits verification. No real client data is permitted in the initial suite.

## Current governed coverage

| Fixture | Engagement type | Status |
|---|---|---|
| `FIXTURE-DAI-001` | Digital and AI transformation | Built foundation; analytical oracle and semantic model complete |
| `FIXTURE-STRAT-001` | Corporate and business-unit strategy | Built foundation in Phase 5 |
| `FIXTURE-COST-001` | Cost and productivity | Built foundation in Phase 5 |
| Remaining ten primary fixtures | Other governed engagement types | Planned |
| Compound fixtures | Cross-domain engagements | Planned |

Phase 5 deliberately adds the two fixtures next in the canonical build order. It does not claim completion of the full thirteen-fixture end-to-end suite.

## Primary fixture programme

1. `corporate-strategy/FIXTURE-STRAT-001`
2. `growth-commercial/FIXTURE-GROWTH-001`
3. `cost-productivity/FIXTURE-COST-001`
4. `customer-experience/FIXTURE-CX-001`
5. `operating-model/FIXTURE-OM-001`
6. `organisation-workforce/FIXTURE-WF-001`
7. `digital-ai/FIXTURE-DAI-001`
8. `risk-controls/FIXTURE-RISK-001`
9. `ma-integration/FIXTURE-MA-001`
10. `carveout-separation/FIXTURE-CARVE-001`
11. `ipo-valuation-capital/FIXTURE-IPO-001`
12. `implementation-change/FIXTURE-CHANGE-001`
13. `benefits-performance/FIXTURE-BEN-001`

Legacy IDs are retained as aliases in `fixtures/manifest.yaml` rather than silently discarded.

## Governed Phase 5 fixture contract

Each built fixture contains:

- a synthetic client profile, mandate, decision owner and Founder gates;
- opportunity and CRM continuity records;
- stakeholder interviews and meeting evidence;
- structured datasets with intentional defects and contradictions;
- a source manifest with scope, limitations, rights and one adversarial source;
- expected problem and method choices, including rejected method traps;
- independently recalculable metrics and tolerances;
- a preferred recommendation, credible alternative and prohibited choices;
- governing uncertainties and falsifiers;
- implementation initiatives linked to recommendation actions;
- benefit records linked to initiatives, owners and verification thresholds;
- semantic output expectations for PPTX, DOCX, XLSX, PDF, SVG and HTML;
- a restricted answer key and reproducible restricted fixture baseline.

The client-visible fixture generator never reads or writes restricted expected results. Golden expectations define invariants and ranges, not an exact prose answer.

## Evaluation boundaries

`expected-results.yaml`, `fixture-baseline.json` and the suite baseline are restricted evaluation material and must not enter normal agent context. A failing implementation must be investigated rather than repaired by weakening a golden expectation. Changes to material expectations require a rationale and Founder review.

Physical Office and browser artefacts, visual regression, full lifecycle execution and the remaining ten primary fixtures are outside this Phase 5 tranche.
