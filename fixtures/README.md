# Synthetic Engagement Fixture Library

## Purpose

Fixtures are controlled synthetic engagements used to test the complete offdata lifecycle, method selection, evidence handling, quantitative analysis, deliverable production, implementation planning and benefits verification.

No real client data should be used in the initial fixture suite.

## Primary fixtures

Create one fixture for each engagement type:

1. `corporate-strategy/`
2. `growth-commercial/`
3. `cost-productivity/`
4. `customer-experience/`
5. `operating-model/`
6. `organisation-workforce/`
7. `digital-ai/`
8. `risk-controls/`
9. `ma-integration/`
10. `carveout-separation/`
11. `ipo-valuation-capital/`
12. `implementation-change/`
13. `benefits-performance/`

## Compound fixtures

After primary fixtures:

- `compound-ai-workforce-operating-model/`
- `compound-ma-technology-benefits/`
- `compound-growth-cx-pricing/`
- `compound-cost-risk-controls/`
- `compound-strategy-capital-implementation/`

## Fixture structure

```text
fixture-name/
├── manifest.yaml
├── mandate/
├── crm/
├── interviews/
├── documents/
├── data/
├── evidence/
├── expected/
│   ├── framing.yaml
│   ├── method-selection.yaml
│   ├── calculations/
│   ├── recommendation.yaml
│   ├── storyline.yaml
│   ├── implementation.yaml
│   └── benefits.yaml
├── defects/
└── artefact-baselines/
```

## Fixture manifest

```yaml
fixture:
  id:
  name:
  engagement_types:
  decision:
  synthetic_client:
  difficulty:
  material_risks:
  intentional_data_issues:
  expected_problem_archetypes:
  acceptable_method_stacks:
  unacceptable_methods:
  required_escalations:
  expected_output_formats:
  version:
```

## Design requirements

Each fixture must contain:

- A credible client and commercial context
- An incomplete initial mandate
- Ambiguous or contradictory evidence
- At least one tempting but incorrect method choice
- Material assumptions and falsifiers
- Quantitative data with known expected ranges
- Data-quality defects
- An alternative to the preferred recommendation
- Implementation constraints
- Benefits timing and attribution issues
- Visual and deliverable requirements

## Golden expectations

Golden expectations should define:

- Required invariants
- Acceptable ranges
- Required records and traceability
- Prohibited conclusions
- Material defects that must be detected
- Visual and technical artefact checks

Do not require one exact prose formulation. Do not change a golden expectation solely to make a failing implementation pass.

## First pilot

The first fixture should be a fictional small or medium-sized business considering an AI programme. It should exercise:

- Opportunity and CRM conversion
- AI audit mandate
- Strategy and value framing
- AI use-case selection
- Data and technology readiness
- Risk and controls
- Workforce and operating-model effects
- Pilot design
- Value case
- Executive deck, report, model and interactive summary
- Implementation roadmap and benefit measures
