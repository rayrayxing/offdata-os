# 06 — Engagement Lifecycle and Gates

## 1. Lifecycle objective

The lifecycle controls where an engagement is, what must happen next, what evidence is sufficient to advance, what may be automated and which decisions require the Founder.

## 2. Canonical stages

### Stage 0 — Opportunity and qualification

Required outcomes:

- Organisation and opportunity record
- Trigger and initial evidence
- Fit, value, urgency and conflict assessment
- Proposed offer
- Outreach or engagement decision

Gate outcomes: pursue, nurture, reject or hold.

### Stage 1 — Mandate intake

Required outcomes:

- Raw client input preserved
- First-cut mandate
- Decision owner and date
- Scope, objectives and constraints
- Initial facts, assumptions and gaps

Gate outcomes: proceed to framing, request material clarification, pause or decline.

### Stage 2 — Framing and problem architecture

Required outcomes:

- Decision and problem statements
- Unit and boundary of analysis
- Question or issue structure
- Initial hypotheses and alternatives
- Evidence and analysis plan

Gate outcomes: approve frame, conditionally approve, recycle or stop.

### Stage 3 — Proposal and commercial definition

Required outcomes:

- Scope and workstreams
- Deliverables
- Approach and methods
- Timeline and responsibilities
- Commercial assumptions and exclusions
- Data and access requirements

External proposal release requires Founder approval.

### Stage 4 — Mobilisation

Required outcomes:

- Engagement workspace
- Governance and cadence
- Data-access controls
- Work plan and owners
- Method and tool readiness
- Initial risks and dependencies

### Stage 5 — Research and fact base

Required outcomes:

- Research mandate
- Source and evidence records
- Client data quality profile
- Claim and gap map
- Initial fact base

Gate test: sufficient evidence exists to begin material diagnosis, or gaps are explicitly accepted.

### Stage 6 — Diagnosis and hypothesis testing

Required outcomes:

- Tested hypotheses
- Root causes or explanatory mechanisms
- Contradictory evidence
- Confidence and limitations
- Updated problem structure

### Stage 7 — Options and value case

Required outcomes:

- Feasible alternatives including no/minimum change
- Costs, benefits, risks and dependencies
- Scenarios and sensitivities
- Value and feasibility assessment
- Reversal criteria

### Stage 8 — Recommendation and decision

Required outcomes:

- Preferred option
- Decision rationale
- Evidence and model traceability
- Trade-offs and uncertainty
- Implementation implications
- Founder decision packet

Material recommendation release requires Founder approval.

### Stage 9 — Storyline and deliverable production

Required outcomes:

- Approved story model
- PPTX, DOCX, XLSX, PDF, SVG or HTML as required
- Concise client citations and full internal provenance
- Cross-deliverable reconciliation
- Quality review and repair

### Stage 10 — Client decision and mobilisation to act

Required outcomes:

- Client decision or response
- Conditions and changes
- Agreed actions
- Updated engagement state

External commitments remain Founder-controlled.

### Stage 11 — Implementation and change

Required outcomes:

- Initiatives, owners, milestones and dependencies
- Acceptance and readiness criteria
- Adoption and outcome measures
- Risks, controls and corrective action

### Stage 12 — Benefits verification, close and learning

Required outcomes:

- Benefit evidence and attribution
- Sustainment assessment
- Closeout decision
- Sanitised lesson candidates
- Methodology and fixture updates proposed through governance

## 3. Gate outcomes

Every gate must support:

- Proceed
- Proceed with conditions
- Pause
- Recycle to a named stage
- Stop
- Close

The gate record must include decision owner, evidence, conditions, expiry and downstream effects.

## 4. Decision classes

### D1 — Routine, internal and reversible

May proceed autonomously within approved policy.

Examples:

- Drafting internal work products
- Running tests
- Searching approved sources
- Creating synthetic analyses
- Reformatting approved content

### D2 — Material internal decision

May be prepared autonomously but requires Founder or delegated approval before commitment.

Examples:

- Changing engagement scope
- Selecting a high-cost analytical path
- Accepting a material evidence gap
- Waiving a non-critical quality defect

### D3 — External, commercial or difficult-to-reverse action

Founder approval required before execution.

Examples:

- Sending proposals or outreach
- Changing DNS
- Purchasing services
- Deploying real client data
- Releasing material recommendations

### D4 — Prohibited or specialist-authorised action

Cannot be performed by offdata without required qualified authority.

Examples:

- Unlawful data processing
- Regulated opinions without qualified approval
- Circumventing access controls
- Misrepresentation
- Copying protected proprietary materials

## 5. Workflow control requirements

Every durable workflow must implement:

- Stable workflow and engagement IDs
- Checkpoints
- Idempotency keys for external actions
- Retry budgets by error type
- Exponential or policy-defined backoff
- Dead-letter or blocked state
- Timeout and cancellation
- Circuit breakers for failing integrations
- Human approval waits
- Global and engagement kill switches
- Recovery after process restart
- Compensating actions where rollback is impossible
- Complete event and cost history

## 6. Retry policy

- Validation errors: repair once, then escalate if unresolved.
- Transient integration errors: retry within documented budget.
- Authentication errors: stop and request Founder action.
- Policy denial: do not retry without changed approval or context.
- Material model disagreement: create a defect and route to independent review.
- Repeated hallucination or schema failure: switch model or stop the task.

## 7. Founder interruption packet

Every interruption should state:

- Decision required
- Why it matters now
- Recommended option
- Alternatives
- Supporting evidence
- Risks and consequences
- Cost and timing
- Reversibility
- Expiry or deadline
- Exact action requested

Do not ask broad or avoidable clarification questions when a safe first cut can be produced.

## 8. Release gate

No client-facing deliverable is releasable until:

- Required claims are supported or clearly qualified
- Material numbers reconcile
- Blocking defects are closed or explicitly waived by the Founder
- Confidentiality and citation presentation are correct
- Deliverables open and render successfully
- External release is approved

## 9. Learning gate

Lessons from an engagement may become methodology candidates only after:

- Client information is removed or properly sanitised
- The lesson is separated from case-specific facts
- Supporting evidence is recorded
- Copyright, confidentiality and conflict concerns are reviewed
- Regression tests are proposed
- Founder approves promotion into the canonical library
