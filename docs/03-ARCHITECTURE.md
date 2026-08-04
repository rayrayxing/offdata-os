# 03 — Target Architecture

## 1. Architectural position

No single agent product should own all offdata responsibilities. The architecture separates:

- Human collaboration and operator interfaces
- Canonical engagement state
- Durable workflow control
- Agent reasoning and model routing
- Tool and execution workers
- Knowledge and evidence
- Analytics
- Deliverable rendering
- CRM and external systems
- Security, policy and observability

The offdata control plane must remain independent of OpenClaw, Hermes, Buzz, Codex, Claude Code, Pi or any single model provider.

## 2. Recommended initial stack

| Layer | Initial choice | Notes |
|---|---|---|
| Web application | Next.js + TypeScript | Founder cockpit and engagement surfaces |
| Backend API | Python + FastAPI | Consulting logic, analytics and integrations |
| Typed agent layer | Pydantic AI | Provider-flexible, structured contracts |
| Durable workflow | Restate | Long-running execution, waits, retries and recovery |
| Database | PostgreSQL | Canonical structured state |
| File/object storage | S3-compatible | Source files, models and deliverables |
| Retrieval | PostgreSQL lexical + vector initially | Avoid premature vector-database complexity |
| Analytics | Governed Python workers | Pandas, DuckDB, statistics, optimisation and simulation |
| CRM | HubSpot Free initially | Relationship and opportunity continuity |
| Deployment | Containers | Local, staging and production consistency |
| Observability | OpenTelemetry-compatible | Tracing, metrics and audit correlation |
| Testing | Pytest, TypeScript tests, Playwright and artefact validators | Layered test strategy |

These are approved design defaults, not permission to purchase or deploy services.

## 3. Logical architecture

```text
Founder / Partner
    |
    v
Founder Cockpit and Engagement Workspace
    |
    v
Offdata API + Policy Engine + Identity
    |
    +---------------------------+
    |                           |
    v                           v
Durable Engagement Runtime      CRM / External Integration Layer
    |                           |
    v                           v
Agent Coordination Layer        HubSpot, email, calendar, approved sources
    |
    +-------------------------------------------------------+
    |             |             |             |             |
    v             v             v             v             v
Knowledge     Evidence      Analytics      Artefact      Implementation
Registry      Graph         Workers        Studio        and Benefits
    |             |             |             |             |
    +-------------+-------------+-------------+-------------+
                          |
                          v
             PostgreSQL + Object Storage
```

## 4. Engagement control plane

The control plane owns:

- Engagement identity and tenancy
- Lifecycle stage and transitions
- Decisions and approvals
- Workstreams and tasks
- Claims, hypotheses, evidence and assumptions
- Method selections
- Models and outputs
- Quality defects and release status
- Deliverable versions
- Implementation and benefit records
- Audit history
- Costs and usage

No agent session, chat transcript or gateway memory may supersede these records.

## 5. Durable workflow design

A durable workflow runtime is required because engagements may:

- Run for months
- Wait for client evidence or Founder approval
- Contain parallel workstreams
- Retry failed tools
- Recycle to previous stages
- Resume after infrastructure failure
- Cancel external actions
- Require idempotent side effects

Restate is the initial recommendation. LangGraph remains the leading alternative where explicit graph topology becomes more valuable than implementation simplicity. The workflow interface must be abstracted so the runtime can be replaced.

## 6. Agent and model layer

Agents are bounded services, not persistent autonomous personalities. Each receives a compiled context package containing only relevant:

- Engagement state
- Decisions and constraints
- Approved methods
- Evidence and gaps
- Tool permissions
- Output schema
- Quality rubric
- Cost limit

Model routing should classify tasks by risk and complexity:

- Low-cost model: extraction, classification, simple formatting
- Mid-tier model: routine synthesis, research planning and drafting
- Premium model: material recommendation, complex reasoning and independent review
- Deterministic code: calculation, reconciliation, transformation and validation

## 7. Worker harnesses

Codex, Claude Code, Pi, Hermes or other execution harnesses may be used as bounded workers through a common contract:

```yaml
work_package:
  id:
  engagement_id:
  objective:
  inputs:
  permitted_tools:
  prohibited_actions:
  expected_outputs:
  acceptance_tests:
  cost_limit:
  timeout:
  data_classification:
```

Workers must return artefacts, structured results, logs and test evidence. They must not mutate canonical engagement state directly without validated API calls.

## 8. Gateway and collaboration options

### OpenClaw

Potential later role:

- Messaging gateway
- Scheduled operations
- Operator shell
- Launching bounded workers

It must not be the canonical engagement database.

### Hermes Agent

Potential later role:

- Persistent personalised Founder agent
- Morning briefings
- Methodology and opportunity monitoring

Its learning and memory must be quarantined from canonical methodology and client truth.

### Buzz

Potential later role:

- Human-agent consulting workroom
- Visible agent collaboration and approval discussions

It must not initially own evidence, CRM or lifecycle state.

These integrations are deferred until the core synthetic end-to-end workflow is stable.

## 9. Knowledge architecture

Use four related stores:

1. **Source library** — immutable original documents and metadata.
2. **Structured registry** — method, problem, evidence and quality records.
3. **Traceability graph** — relationships among decisions, claims, evidence, analyses, recommendations and benefits.
4. **Retrieval index** — lexical and semantic retrieval derived from controlled sources.

A context compiler selects the smallest sufficient context for each agent call. Avoid loading the full library into prompts.

## 10. Deliverable architecture

A canonical Engagement Semantic Model should contain:

- Governing thought
- Decision and audience
- Proposition hierarchy
- Claims and evidence
- Key numbers and model references
- Visual archetypes
- Section and slide specifications
- Citation mode
- Brand and accessibility rules

Format-specific renderers then produce PPTX, DOCX, XLSX, PDF, SVG and HTML. Cross-format reconciliation must be automated.

## 11. Regional and tenancy architecture

Initial deployment:

- Single Founder tenant
- Singapore data region
- Synthetic data until production approval

Future deployment:

- Regional deployment cells
- Client-specific workspaces and encryption boundaries
- Region-aware routing and storage
- Global methodology library separated from confidential client stores
- Explicit rules for cross-border transfer and support access

## 12. Environments

### Local

- Containers
- Local PostgreSQL
- Local object-storage emulator
- Synthetic data
- No billable dependencies required

### Staging

- Singapore-region managed services where available
- Synthetic or sanitised data
- Restricted access
- Automated deployments after approval

### Production

- Real client data only after security gate
- Managed backups
- Monitoring and incident controls
- Data-processing register
- Documented recovery objectives

## 13. Architecture decision process

Material architecture changes require an Architecture Decision Record containing:

- Context
- Options considered
- Decision
- Consequences
- Cost
- Security and residency impact
- Reversibility
- Migration plan
- Founder approval
