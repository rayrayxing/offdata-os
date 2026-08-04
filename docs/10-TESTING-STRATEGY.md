# 10 — Testing and Evaluation Strategy

## 1. Testing objective

Prove that offdata is technically reliable, analytically defensible, secure, recoverable and capable of producing professional consulting outputs.

“The application runs” is not sufficient evidence.

## 2. Test pyramid

### Level 1 — Code quality

- Unit tests
- Type checks
- Formatting and linting
- Static analysis
- Dependency and licence checks
- Secret scanning

### Level 2 — Component and integration

- API contracts
- Database migrations and rollback
- Object storage
- Retrieval
- Authentication and authorisation
- CRM and external connectors
- Renderer components

### Level 3 — Workflow durability

- Checkpoint and resume
- Human approval waits
- Retry budgets
- Cancellation
- Blocked states
- Circuit breakers
- Idempotency
- Compensation and rollback
- Duplicate external-action prevention

### Level 4 — Agent evaluations

- Schema validity
- Tool permission compliance
- Factuality and grounding
- Evidence use
- Contradiction handling
- Appropriate confidence
- Escalation and abstention
- Prompt-injection resistance
- Sensitive-data leakage
- Cost and latency
- Repeat-run consistency

### Level 5 — Consulting quality

- Decision relevance
- Problem framing
- Hypothesis quality
- Alternative coverage
- Method-selection quality
- Evidence sufficiency
- Quantitative integrity
- Recommendation logic
- Feasibility and trade-offs
- Implementation and benefit traceability
- Red-team findings

### Level 6 — Artefact quality

- PowerPoint layout and editability
- Word pagination and structure
- Excel formulas and reconciliation
- PDF rendering
- SVG correctness
- HTML responsiveness and accessibility
- Cross-format consistency
- Infographic message accuracy

### Level 7 — Security and operations

- Authentication bypass
- Role and tenant escalation
- Engagement isolation
- Malicious file ingestion
- Prompt injection and exfiltration
- OAuth revocation
- Backup restoration
- Kill switches
- Audit integrity
- Retention and deletion

### Level 8 — End-to-end engagements

Complete synthetic engagements from opportunity through closeout and benefits.

### Level 9 — Founder acceptance

- Can the Founder understand the system?
- Is the decision packet useful?
- Can the Founder correct and stop work?
- Are outputs client-ready?
- Does the system materially reduce workload?

## 3. Synthetic engagement fixture library

Create one primary fixture for each engagement type:

1. Corporate and business-unit strategy
2. Growth and commercial strategy
3. Cost and productivity
4. Customer experience
5. Operating-model transformation
6. Organisation and workforce
7. Digital and AI transformation
8. Risk and controls
9. M&A and integration
10. Carve-out and separation
11. IPO, valuation and capital strategy
12. Implementation and change
13. Benefits realisation and performance improvement

Create compound fixtures after primary cases:

- AI transformation + workforce + operating model
- M&A + technology separation + benefits
- Growth + customer experience + pricing
- Cost reduction + risk and controls
- Strategy + capital allocation + implementation

## 4. Fixture contents

Every fixture should include:

- Synthetic client profile
- Founder mandate
- Opportunity and CRM records
- Interview transcripts and meeting notes
- Structured and unstructured datasets
- Intentional data-quality defects
- Expected problem archetypes
- Acceptable and unacceptable method combinations
- Evidence corpus with contradictions
- Expected calculations and ranges
- Material assumptions and falsifiers
- Reference recommendation and alternatives
- Expected storyline and deliverable structure
- Known quality defects
- Implementation and benefit expectations

Golden expectations should define valid ranges and invariants rather than requiring one exact prose output.

## 5. Golden fixture rules

- Do not modify a golden fixture solely to pass a failing test.
- If the implementation and golden expectation conflict, stop and investigate.
- Changes to golden expectations require a rationale, independent review and Founder approval for material cases.
- Preserve prior fixture versions for regression analysis.

## 6. Method-selection evaluation

For each fixture, test whether the system:

- Identifies the correct executive decision
- Selects relevant problem archetypes
- Chooses a minimum sufficient method stack
- Avoids framework soup
- Identifies prerequisites and evidence needs
- Rejects tempting but inappropriate methods
- Identifies specialist review requirements

## 7. Evidence evaluation

Measure:

- Citation accuracy
- Passage support
- Source quality and timeliness
- Scope fidelity
- Contradiction recall
- Unsupported claim rate
- Evidence-gap detection
- Correct separation of fact, assumption, synthesis and recommendation

## 8. Quantitative evaluation

Required tests include:

- Independent recalculation
- Dimensional and unit checks
- Reconciliation to controlled totals
- Formula and reference consistency
- Scenario and sensitivity behaviour
- Missing-value and outlier handling
- Random-seed reproducibility
- Model limitations
- Cross-deliverable number consistency

## 9. Independent review tiers

### Tier 1 — automated deterministic checks

Run on all relevant changes and artefacts.

### Tier 2 — isolated model review

Separate context and fixed rubric. Run on material analytical outputs.

### Tier 3 — alternative-model or alternative-method review

Use for high-impact recommendations, value cases and difficult evidence disputes.

### Tier 4 — Founder or qualified specialist review

Required for material release, risk acceptance and specialist conclusions.

## 10. Defect severity

### Critical

Could cause unlawful action, client harm, serious confidentiality breach, materially false recommendation or irreversible external impact. Blocks release.

### High

Could materially change the decision, economics, risk or feasibility. Blocks release unless explicitly resolved.

### Medium

Reduces clarity, completeness or reliability but is unlikely to alter the core decision alone. Must be resolved or conditionally accepted.

### Low

Cosmetic or minor usability issue. May be deferred with a recorded owner.

## 11. Quality thresholds

Initial thresholds are provisional and must be calibrated with fixtures.

- Zero critical defects for any release
- Zero open high defects for client-facing release
- 100% material-number reconciliation
- 100% citation resolution for cited material facts
- Zero known cross-engagement data leaks
- Zero committed secrets
- All required workflow recovery tests pass
- Office artefacts open without repair warnings

## 12. Visual regression

For PPTX, DOCX, PDF and HTML:

- Render pages or slides to images
- Compare dimensions and layout against approved baselines
- Detect overlap, clipping and missing assets
- Review changed visuals through Computer Use or browser testing
- Store approved visual baselines as versioned test artefacts

Visual comparison must tolerate harmless rendering differences while detecting decision-relevant defects.

## 13. Cost and performance evaluation

Track by engagement and task:

- Model and tool cost
- Token usage
- Latency
- Retry count
- Human correction effort
- Total task completion time
- Quality per cost

Do not optimise cost by silently reducing quality on material work.

## 14. Continuous integration

Every pull request should run the tests appropriate to its changed components. The complete fixture suite may run on scheduled or release workflows where runtime is excessive.

Required checks should include:

- Formatting and linting
- Types
- Unit tests
- Integration tests
- Secret scan
- Dependency scan
- Schema compatibility
- Migration checks
- Selected agent evaluations
- Selected fixture regression

## 15. Release evidence

Every release candidate must produce:

- Test summary
- Coverage and skipped-test report
- Security scan results
- Migration and rollback evidence
- Fixture results
- Open defects and waivers
- Cost estimate
- Artefact samples
- Founder approval request
