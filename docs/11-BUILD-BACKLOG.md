# 11 — IMP phase-gated build backlog

## Namespace and backlog rules

The canonical implementation namespace is `IMP-P0` through `IMP-P12`.

- Build in `IMP-P0` to `IMP-P12` order.
- Task identifiers remain `P0.1`, `P1.1` and so on for compatibility.
- A completed `CF-P*`, `PCR-*` or `WS-*` package is not an implemented product phase.
- An implementation phase may contain parallel tasks only when dependencies permit.
- Each task requires tests, documentation and rollback instructions.
- Codex stops at every implementation phase gate.
- Paid services, OAuth, credentials, DNS and external communications require Founder action.
- Legacy numeric phase wording and the former Codex display name is a display alias only; it never changes authority.

## IMP-P0 — Controlled project foundation

### P0.1 Repository baseline

Deliver:

- Monorepo structure
- README and governing documentation
- Licence decision placeholder
- Code ownership and pull-request templates
- `.gitignore` and `.env.example`

Done when:

- Repository is private and accessible
- No secret is committed
- Read order is clear

### P0.2 Local development environment

Deliver:

- Next.js application shell
- FastAPI service shell
- Local PostgreSQL
- Local S3-compatible object-storage emulator
- Container orchestration
- One-command start and stop

Done when:

- Clean macOS setup can start all services
- Health checks pass
- No paid cloud resource is required

### P0.3 Engineering quality baseline

Deliver:

- Formatting, linting and type checks
- Unit-test runners
- Secret and dependency scanning
- GitHub Actions CI
- Pre-commit or equivalent local checks

Done when:

- A deliberate failing change blocks CI
- A safe change passes all checks

### P0.4 Security and operating documentation

Deliver:

- Threat-model skeleton
- Secret-handling guide
- Environment separation plan
- Founder action register
- Architecture decision template
- Build status ledger

### IMP-P0 gate

Founder receives a local demonstration and completion report. No substantive product workflow is required yet.

## IMP-P1 — Knowledge ingestion and method registry

### P1.1 Source import

- Import canonical and domain source files unchanged
- Calculate checksums
- Capture metadata
- Preserve versions
- Add copyright and confidentiality fields

### P1.2 Extraction pipeline

- Parse Markdown and DOCX
- Create stable chunks and source locations
- Separate source text from instructions
- Detect malformed or duplicate content

### P1.3 Canonical manifest and alias resolver

- Resolve inconsistent filenames and references
- Create canonical IDs
- Preserve original aliases
- Detect missing dependencies

### P1.4 Method and problem schemas

- Implement method, archetype, evidence, tool and quality records
- Validate required fields
- Quarantine incomplete records

### P1.5 Search and retrieval

- Lexical and semantic retrieval
- Source filters and access controls
- Retrieval evaluation set

### IMP-P1 gate

- Initial 150-plus method records are structured and searchable
- Every record links to original source
- Re-ingestion is deterministic

## IMP-P2 — Engagement system of record

### P2.1 Identity and tenancy

- Founder account
- Tenant and engagement boundaries
- Role scaffolding for future users

### P2.2 Core database

Implement organisations, contacts, opportunities, engagements, mandates, decisions, claims, evidence, methods, analyses, recommendations, approvals, deliverables, initiatives and benefits.

### P2.3 Versioning and audit

- Material record version history
- Actor and timestamp tracking
- Audit-event correlation
- Controlled archival

### P2.4 Founder cockpit shell

- Engagement list
- Current stage
- Decision inbox
- Blockers and risks
- Cost summary

### IMP-P2 gate

- Records survive restart
- Backup and restore works locally
- Engagement-isolation tests pass

## IMP-P3 — Lifecycle and durable workflow

### P3.1 Workflow abstraction

Define runtime-independent workflow contracts.

### P3.2 Restate integration

- Durable engagement workflow
- Checkpoints
- Approval waits
- Retries and blocked states
- Cancellation

### P3.3 Policy and decision classes

- D1–D4 rules
- Founder approval packets
- External-action idempotency
- Kill switches

### P3.4 Lifecycle user interface

- Stage timeline
- Entry and exit criteria
- Gate history
- Recycle and pause controls

### IMP-P3 gate

A synthetic engagement completes the lifecycle, survives interruption and does not duplicate actions.

## IMP-P4 — Initial specialist agents

### P4.1 Context compiler

Build minimum-sufficient context packages from canonical state.

### P4.2 Agent contracts

Implement typed contracts for:

- Engagement Partner
- Problem Architect
- Method Architect
- Research and Evidence
- Quantitative and Value
- Storyline
- Deliverable Production
- Implementation and Benefits
- Independent Quality

### P4.3 Model routing

- Provider abstraction
- Risk and complexity routing
- Cost limits
- Fallback behaviour

### P4.4 Agent evaluation harness

- Fixture prompts
- Schema and permission checks
- Grounding, escalation and injection tests

### IMP-P4 gate

Agents pass evaluation thresholds and cannot directly bypass policy or canonical APIs.

## IMP-P5 — Research and evidence layer

### P5.1 Research planning

- Mandate and question tree
- Source strategy
- Stopping criteria

### P5.2 Web and document tools

- Approved web search
- Page and document capture
- Source metadata
- Change detection

### P5.3 Claim and evidence ledger

- Support and contradiction links
- Evidence quality
- Confidence and gaps
- Client citation modes

### P5.4 Evidence QA

- Citation resolution
- Source-scope checks
- Staleness and broken-link checks

### IMP-P5 gate

A reviewer can trace a recommendation to source passages and contradicting evidence.

## IMP-P6 — Quantitative and modelling services

### P6.1 Governed analytical runtime

- Python environment
- Dependency lock
- Sandboxed execution
- Run metadata and reproducibility

### P6.2 Core analytical libraries

- Financial models
- Scenario and sensitivity
- Statistics and causal inference
- Optimisation
- Simulation
- Network analysis
- Cohort and survival

### P6.3 Excel model generator

- Standard workbook architecture
- Formula validation
- Reconciliation checks

### P6.4 Model QA

- Independent recalculation
- Units and dimensions
- Missing data
- Random-seed reproducibility

### IMP-P6 gate

A complete value case reproduces from source inputs and reconciles to approved outputs.

## IMP-P7 — Storyline and deliverable studio

### P7.1 Semantic story model

- Governing thought
- Proposition hierarchy
- Section and slide contracts
- Visual specifications

### P7.2 PowerPoint renderer

- Editable shapes
- Charts and notes
- Template and brand support

### P7.3 Word, Excel, PDF and HTML renderers

- Shared story and model references
- Accessibility and print views

### P7.4 Infographic library

Implement priority archetypes:

- Maturity and commitment curve
- Radial framework
- Layered stack or iceberg
- Causal narrative
- Value-driver tree
- Roadmap
- Process and journey
- Governance and operating model

### P7.5 Visual QA

- Rendering to images
- Clipping and overlap checks
- Office open-and-save tests where available
- Cross-format reconciliation

### IMP-P7 gate

One engagement produces consistent, professional PPTX, DOCX, XLSX, PDF, SVG and HTML outputs.

## IMP-P8 — HubSpot Free integration

### P8.1 Synthetic CRM adapter

Build against fixtures before credentials.

### P8.2 HubSpot connection

Founder completes private-app or OAuth setup and enters credentials securely.

### P8.3 Synchronisation

- Companies, contacts and deals
- Stable IDs
- Conflict handling
- Rate limits and retry
- Approved summary fields only

### P8.4 Engagement conversion

Convert an opportunity into an engagement while preserving relationship continuity.

### IMP-P8 gate

CRM continuity works without leaking confidential engagement content.

## IMP-P9 — Controlled origination engine

### P9.1 Source watch lists

Configure approved public sources and trigger categories.

### P9.2 Opportunity scoring

Fit, urgency, value, evidence and buyer-role scoring.

### P9.3 Proposition matching

Match approved offers and methods to opportunity hypotheses.

### P9.4 Outreach drafting and approval

- Policy checks
- Founder preview
- Suppression and frequency
- No autonomous external sending initially

### IMP-P9 gate

The system identifies and prepares qualified opportunities from synthetic and public test cases.

## IMP-P10 — Methodology Radar

### P10.1 Scheduled discovery

Daily source monitoring and change detection.

### P10.2 Candidate analysis

- Novelty
- Primary support
- Existing-method comparison
- Copyright and trademark risk

### P10.3 Candidate drafting

Original offdata method record and tests.

### P10.4 Promotion workflow

Review, regression, Founder approval and versioned library release.

### IMP-P10 gate

New candidates can be found and evaluated without automatic canonical promotion.

## IMP-P11 — Security and production readiness

### P11.1 Managed Singapore staging

Only after Founder approval and cost review.

### P11.2 Production controls

- Managed secrets
- Backups
- Monitoring
- Incident controls
- Retention and deletion
- Provider and processor register

### P11.3 Security testing

- Isolation
- Authentication
- Injection
- Exfiltration
- Malicious documents
- Recovery
- Kill switch

### IMP-P11 gate

Formal production-readiness report and Founder approval before real client data.

## IMP-P12 — Synthetic engagement suite and launch

### P12.1 Primary engagement fixtures

Build and pass all thirteen engagement types.

### P12.2 Compound fixtures

Build cross-domain cases.

### P12.3 Workload and quality measurement

Measure human time saved, correction effort, output quality, cost and reliability.

### P12.4 Launch readiness

- Operating guide
- Service and data policies
- Pricing assumptions
- Pilot protocol
- Support and incident process

### IMP-P12 gate

Founder approves a controlled real-client pilot.

## PCFA-07 reconciled corrective obligation overlay

PCFA-07 does not add a new IMP phase or task. It binds the corrective PCFA-04, PCFA-05 and PCFA-06 specifications into this existing backlog through the machine authority `requirements/pcfa07-codex-implementation-backlog-reconciliation.json`.

The overlay contains exactly 93 `planned_not_implemented` obligations: 29 PCFA-04 product/consulting-craft requirements, 19 MVCL stages, 15 MVCL invariants, 13 MVCL negative-path cases, six Founder interrupt classes and 11 Hermes bounded-adoption capabilities. Each obligation has exact existing task bindings, a primary implementation task, component bindings, dependency tasks, one blocking IMP phase gate, one unique `PCFA07-TST-*` planned test identity and one evidence type.

No PCFA-07 obligation is assigned to IMP-P0. The Codex launch scope remains only P0.1–P0.4. The PCFA-07 planned tests are not executed evidence; implementation status can change only during the bound later IMP tasks with required evidence and gate acceptance. PCFA-08 final cross-authority acceptance remains required.

## PCFA-08 final pre-Codex acceptance overlay

PCFA-08 adds no IMP phase, task or implementation obligation. It accepts the repository-side cross-authority consistency of PCFA-01 through PCFA-07 and freezes the remaining manual launch contract. The Codex launch scope remains exactly P0.1–P0.4. The 65 governed non-`main` branches must be cleaned only after dependency-order integration with final-SHA evidence for every deleted ref, and live GitHub must show only `main` before the single-use permit can be issued.

`codex_start_authorized=false` until all manual launch gates and the permit pass.

## Deferred integrations

OpenClaw, Hermes, Buzz, additional model providers, paid CRM tiers, enrichment services and advanced research subscriptions remain deferred until a documented problem justifies them.
