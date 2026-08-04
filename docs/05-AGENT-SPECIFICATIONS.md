# 05 — Initial Agent Specifications

## 1. Operating model

Agents are bounded role services coordinated by the engagement runtime. They do not own canonical state, approve their own material work or act outside explicit permissions.

Each agent must have:

- Stable agent ID and version
- Purpose and boundaries
- Typed input schema
- Typed output schema
- Permitted tools
- Prohibited actions
- Data-access scope
- Evidence requirements
- Escalation rules
- Retry, timeout and cost limits
- Quality rubric and evaluation suite
- Audit and trace requirements

## 2. Context compiler

Before invoking an agent, the system compiles a minimum sufficient context package:

```yaml
context_package:
  engagement_id:
  current_stage:
  objective:
  decision:
  constraints:
  relevant_methods:
  relevant_claims:
  evidence_summary:
  evidence_gaps:
  approved_assumptions:
  prior_outputs:
  permitted_tools:
  output_contract:
  quality_rubric:
  approval_class:
  budget:
```

The full knowledge base and full engagement history should not be inserted by default.

## 3. AI Engagement Partner

### Purpose

Coordinate the engagement, maintain decision focus, detect exceptions and prepare decision-ready Founder packets.

### Responsibilities

- Convert raw inputs into a first-cut mandate
- Track stage, workstreams, dependencies and unresolved material issues
- Coordinate specialist agents
- Summarise progress and risks
- Recommend gate outcomes
- Prepare Founder approvals

### Prohibited

- Final approval of material recommendations
- Commercial commitments
- External sending without policy approval
- Specialist legal, tax, audit or regulatory conclusions

### Key outputs

- Engagement brief
- Stage plan
- Work packages
- Decision packet
- Status and exception report

## 4. Problem Architect

### Purpose

Turn ambiguous mandates into decision-led problem structures and testable hypotheses.

### Responsibilities

- Define decision, problem and unit of analysis
- Create question, issue, hypothesis, logic or causal structures as appropriate
- Generate alternatives and falsifiers
- Link questions to evidence and analysis
- Detect premature framework use

### Key outputs

- Problem statement
- Question or issue structure
- Hypothesis ledger
- Falsification plan
- Decision implications

## 5. Method Architect

### Purpose

Select the minimum sufficient method stack from canonical and domain registries.

### Responsibilities

- Classify decision and problem archetypes
- Select primary and overlay methods
- Sequence methods
- Identify prerequisites, tools and reviewers
- Record rejected methods and conflicts

### Key outputs

- Method selection record
- Method sequence
- Tool and evidence requirements
- Reviewer plan

## 6. Research and Evidence Agent

### Purpose

Acquire, evaluate and organise evidence against engagement questions and claims.

### Responsibilities

- Build research mandate and question tree
- Search approved sources
- Preserve provenance and source scope
- Identify support and contradiction
- Maintain evidence gaps
- Stop when marginal research value is insufficient

### Prohibited

- Treating search snippets as authoritative evidence
- Bypassing paywalls or access controls
- Importing confidential client content into global knowledge
- Hiding contradictory evidence

### Key outputs

- Research plan
- Source and evidence records
- Evidence map
- Gap and contradiction register
- Research synthesis

## 7. Quantitative and Value Agent

### Purpose

Execute reproducible analysis, modelling and value conversion.

### Responsibilities

- Prepare analysis specifications
- Use deterministic analytical tools
- Validate inputs and assumptions
- Run scenarios and sensitivities
- Reconcile outputs
- Produce model documentation

### Prohibited

- Mental or free-form arithmetic for material outputs
- Inventing missing numbers
- Hiding model failures or uncertainty
- Writing unexplained hard-coded values

### Key outputs

- Analysis runs
- Model files
- Assumption register
- Scenario and sensitivity results
- Reconciliation report

## 8. Domain Specialist Agent

### Purpose

Apply the selected domain capability pack without replacing the common engagement kernel.

### Responsibilities

- Interpret domain-specific evidence and constraints
- Adapt method procedures
- Identify specialist standards and review needs
- Detect domain-specific failure modes

Domain specialisation is configured from method and overlay records. Separate monolithic agents should be introduced only when evaluation shows a material benefit.

## 9. Storyline Agent

### Purpose

Translate validated analysis into a decision-first proposition and coherent story.

### Responsibilities

- Develop governing thought
- Build proposition hierarchy and section contracts
- Draft assertions and recommendation logic
- Preserve evidence, uncertainty and alternatives
- Specify visual opportunities

### Key outputs

- Story model
- Section and slide plan
- Executive summary
- Recommendation narrative

## 10. Deliverable Production Agent

### Purpose

Render approved story and model records into client-ready artefacts.

### Responsibilities

- Produce PPTX, DOCX, XLSX, PDF, SVG and HTML
- Apply brand and layout rules
- Create editable infographics
- Reconcile numbers and terminology
- Run artefact validators

### Prohibited

- Introducing new material claims during rendering
- Recalculating numbers independently of approved models
- Rasterising labelled diagrams when editability is required

## 11. Implementation and Benefits Agent

### Purpose

Translate recommendations into controlled execution and verified outcomes.

### Responsibilities

- Define initiatives, milestones, owners and dependencies
- Select implementation archetype
- Define acceptance, adoption, outcome and benefit measures
- Track corrective actions and sustainment

### Key outputs

- Implementation roadmap
- Governance and control plan
- Adoption and outcome measures
- Benefits register
- Scale, adapt or stop recommendations

## 12. Independent Quality Agent

### Purpose

Challenge material work independently of the producing context.

### Responsibilities

- Test decision relevance
- Check evidence and citation validity
- Challenge hypotheses and alternatives
- Recalculate or independently verify material numbers
- Inspect feasibility, risk and implementation traceability
- Review deliverable consistency and visual quality
- Classify defects and block release where required

### Independence rules

- Separate run and context from creator
- Use a fixed rubric
- Prefer different model configuration for high-assurance reviews
- No access to hidden creator rationale not recorded in canonical state
- Cannot waive blocking defects without Founder authority

## 13. Policy and Security Controller

### Purpose

Enforce permissions, data access, approval classes and external-action controls.

### Responsibilities

- Authorise tool calls
- Check jurisdiction and data class
- Apply approval rules
- Enforce idempotency and rate limits
- Stop prohibited actions
- Record policy decisions

This controller should rely on deterministic rules wherever possible.

## 14. Methodology Librarian

### Purpose

Manage method records and methodology candidates.

### Responsibilities

- Deduplicate and classify records
- Compare new candidates with existing methods
- Preserve provenance
- Draft original offdata records
- Coordinate review and regression tests
- Version and publish approved library releases

### Prohibited

- Automatic canonical promotion
- Copying protected expression
- Treating consulting-firm marketing content as validated methodology

## 15. Initial evaluation requirements

Each agent must pass tests for:

- Schema validity
- Correct tool permissions
- Engagement isolation
- Factual grounding
- Evidence and uncertainty handling
- Escalation behaviour
- Prompt-injection resistance
- Sensitive-data leakage
- Cost and latency limits
- Recovery from tool failure
- Appropriate abstention
- Consistency across repeated runs

## 16. Agent expansion rule

Add a new agent only where:

- The role has a distinct objective and tool set
- Separation improves quality, security or scalability
- The role can be evaluated independently
- Coordination cost does not outweigh the benefit

Prefer new skills, method records or tool adapters over unnecessary agent proliferation.
