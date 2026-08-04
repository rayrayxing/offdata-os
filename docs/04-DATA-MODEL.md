# 04 — Canonical Data Model

## 1. Design objective

The data model must make consulting reasoning, evidence, decisions, delivery and benefits traceable without treating chat history as the record of truth.

Every material recommendation should support the path:

`opportunity → mandate → decision → question → hypothesis → evidence → analysis → option → recommendation → implementation → outcome → benefit`

## 2. Common fields

All material records should include:

- Stable UUID
- Tenant ID
- Engagement ID where applicable
- Status
- Version
- Created and updated timestamps
- Created and updated actors
- Source or parent reference
- Data classification
- Jurisdiction or residency constraint where relevant
- Confidence where relevant
- Approval status where relevant
- Audit correlation ID

Records should use soft deletion or controlled archival where legal and operational requirements demand recovery or auditability.

## 3. Relationship and commercial entities

### Organisation

- Name and aliases
- Registration and jurisdiction fields
- Industry and sector
- Website and domains
- CRM identifiers
- Relationship status
- Data residency requirements
- Risk and conflict flags

### Contact

- Organisation
- Name and role
- Contact channels
- Relationship owner
- Consent and suppression status
- Source and lawful-use metadata
- Activity history reference

### Opportunity

- Organisation and contacts
- Trigger event
- Opportunity hypothesis
- Likely buyer
- Proposed offer
- Evidence and confidence
- Estimated value and urgency
- CRM stage
- Outreach approval state
- Conversion history

### Engagement

- Client organisation
- Engagement name and ID
- Founder owner
- Engagement type and domain overlays
- Commercial status
- Data classification
- Region
- Lifecycle state
- Start, decision and expected close dates
- Workspace and storage references

## 4. Mandate and decision entities

### Mandate

- Raw mandate source
- Structured decision statement
- Decision owner
- Decision date or gate
- Objectives and desired outcomes
- Scope and boundaries
- Constraints
- Known options
- Counterfactual
- Required standard of proof
- Initial facts, assumptions and gaps

### Decision

- Decision statement
- Decision owner and authorised approvers
- Options
- Criteria and constraints
- Required evidence threshold
- Materiality class
- Reversibility
- Current recommendation
- Outcome and conditions
- Approval history

### Approval

- Requested action
- Decision class
- Supporting packet
- Approver
- Outcome
- Conditions
- Expiry
- Timestamp
- Related external action

## 5. Problem-solving entities

### Problem Statement

- Observed condition
- Desired condition
- Decision implication
- Unit of analysis
- Scope
- Materiality

### Question Node

- Parent and children
- Question type
- Decision implication
- Priority
- Required evidence
- Status

### Hypothesis

- Claim
- Type: descriptive, predictive, causal or normative
- Alternative hypotheses
- Supporting conditions
- Falsifier
- Required discriminating evidence
- Confidence
- Status and update history

### Assumption

- Statement
- Owner
- Materiality
- Evidence basis
- Test or expiry date
- Current state
- Impact if false

### Evidence Gap

- Missing information
- Decision impact
- Acquisition plan
- Owner
- Due date
- Resolution state

## 6. Knowledge and methodology entities

### Source Document

- Original filename
- Checksum
- Title and version
- Publisher and author
- Publication and retrieval date
- Source type
- Access URL or object reference
- Licence and usage notes
- Confidentiality
- Superseded status

### Source Passage

- Source document
- Page, section or line location
- Extracted text
- Embedding and lexical index references
- Extraction method and confidence

### Method Record

- Stable method ID
- Name and aliases
- Domain and method family
- Decision supported
- Appropriate problem types
- When to use and not use
- Prerequisites
- Inputs
- Procedure
- Outputs
- Strengths and limitations
- Alternatives
- Compatible overlays
- Conflicts and redundancies
- Tool requirements
- Evidence burden
- Failure modes
- Quality and falsification tests
- Specialist reviewer requirements
- Source provenance
- Copyright and licensing status
- Version and promotion state

### Problem Archetype

- Stable ID
- Domain
- Diagnostic signature
- Core decision question
- Primary and overlay methods
- Evidence indicators
- Common failure modes

### Method Selection

- Engagement and decision
- Problem archetypes
- Selected methods and sequence
- Role of each method
- Rejected methods and reasons
- Required tools and evidence
- Reviewer requirements
- Founder approval where material

### Methodology Candidate

- Discovery source
- Claimed method or practice
- Novelty assessment
- Existing-record comparison
- Primary-source support
- Copyright and trademark review
- Draft original record
- Evaluation results
- Reviewer decision
- Promotion or rejection state

## 7. Evidence and analysis entities

### Evidence Item

- Source passage or client dataset
- Claim supported or contradicted
- Evidence type
- Quality and relevance
- Date and scope
- Limitations
- Access basis
- Reviewer state

### Claim

- Statement
- Claim class
- Materiality
- Supporting and contradicting evidence
- Analysis references
- Confidence
- Citation presentation mode
- Review and release status

### Dataset

- Source and owner
- Schema
- Time coverage
- Unit of analysis
- Data classification
- Quality profile
- Transformation lineage
- Access restrictions

### Analysis Run

- Method record
- Code or notebook version
- Inputs and assumptions
- Parameters and random seed
- Environment and dependency versions
- Outputs
- Diagnostics
- Test results
- Reviewer state

### Model

- Model type and objective
- Inputs
- Assumptions
- Calculation graph
- Scenarios
- Sensitivities
- Outputs
- Version
- Reconciliation status

### Option

- Description
- Counterfactual
- Benefits and disbenefits
- Costs
- Risks
- Feasibility
- Dependencies
- Timing
- Reversibility
- Evidence and confidence

### Recommendation

- Recommended option
- Decision rationale
- Evidence and analysis
- Trade-offs
- Assumptions and uncertainty
- Conditions and signposts
- Reversal criteria
- Owner and timing
- Approval state

## 8. Delivery and quality entities

### Story Model

- Audience and decision
- Governing thought
- Proposition hierarchy
- Section contracts
- Claims and evidence references
- Key numbers
- Visual specifications
- Citation mode

### Deliverable

- Type and purpose
- Audience
- Story model version
- Renderer version
- File object reference
- Status
- Quality results
- Release approval

### Visual Specification

- Archetype
- Message
- Entities and relationships
- Labels and data references
- Layout rules
- Editable-output requirement
- Accessibility rules

### Quality Review

- Review tier
- Reviewer identity or isolated run
- Rubric
- Findings
- Score
- Blocking status
- Disposition
- Waiver and approver

### Defect

- Severity
- Affected record or artefact
- Description
- Evidence
- Required repair
- Owner
- Status
- Regression test

## 9. Implementation and benefits entities

### Initiative

- Recommendation reference
- Objective
- Owner
- Deliverables
- Milestones as observable states
- Dependencies
- Resources and costs
- Acceptance criteria
- Risks and controls
- Implementation archetype

### Adoption Measure

- Target population
- Required behaviour
- Baseline
- Target
- Observation method
- Owner
- Results

### Outcome

- Operational or stakeholder outcome
- Baseline and target
- Measurement period
- Causal link
- Result and confidence

### Benefit

- Objective contribution
- Benefit type
- Owner
- Baseline and counterfactual
- Amount or measure
- Timing
- Costs and disbenefits
- Attribution method
- Verification threshold
- Realisation status

## 10. System entities

- User and role
- Policy and permission
- Agent definition and version
- Agent run
- Work package
- Tool call
- External action
- Workflow instance and checkpoint
- Cost and token usage
- Audit event
- Retention policy
- Regional deployment cell
- Integration credential reference
- Sync state and error

## 11. Required constraints

- Stable IDs cannot be reused.
- Engagement-scoped records require tenant and engagement keys.
- Material records are versioned.
- Evidence cannot be silently detached from released claims.
- External actions require idempotency keys.
- Client confidential records cannot be indexed into the global methodology library.
- Methodology promotion requires review status and regression evidence.
- Released deliverables reference immutable story and model versions.
