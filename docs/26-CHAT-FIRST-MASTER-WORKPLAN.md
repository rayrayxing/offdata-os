# 26 — Chat-First Master Workplan

## Status

Canonical planning baseline v1.0. This document governs how offdata is developed before Codex integration work begins.

## 1. Governing decision

offdata will use a **chat-first, integration-later** build model.

The strongest available reasoning models should complete all work that can be represented as reviewed text, structured data, deterministic rules, schemas, algorithms, prompts, fixtures, tests or starter source code. Codex should be used only when a real execution environment is required.

The practical objective is to minimise Codex discovery and design work. Codex should receive implementation-ready contracts and spend its effort on installation, integration, execution, debugging, rendering, security testing and deployment.

## 2. Allocation rule

### Complete in ChatGPT before Codex where practical

- Product, functional and non-functional requirements.
- Consulting lifecycle, gates and authority rules.
- Canonical data, event, command and API contracts.
- Database semantics and migration expectations.
- Agent purposes, prompts, context packages and output envelopes.
- Methodology, source, evidence and method-selection schemas.
- Synthetic client records, transcripts, datasets and expected answers.
- Evaluation cases, quality rubrics and regression oracles.
- CRM fields, opportunity scoring and outreach policy.
- Storyline, slide, document, model and infographic specifications.
- Security threats, abuse cases and required controls.
- OpenAPI, JSON Schema, YAML configuration and deterministic starter code.
- Third-party tool adoption and licence records.
- Pull-request and test-evidence review.

### Reserve for Codex

- Inspecting and configuring the Founder’s macOS environment.
- Installing and resolving runtimes, package managers and dependencies.
- Running the complete test suite on the target machine.
- Building the Next.js, FastAPI, PostgreSQL and object-storage integration.
- Executing database migrations and recovery tests.
- Connecting model APIs, OAuth and external services.
- Browser, desktop and Office rendering tests.
- Visual-regression, performance, load and security execution.
- Cloud staging and production deployment.
- Producing machine-generated evidence, logs and screenshots.

### Reserve for the Founder

- Passwords, MFA and account recovery.
- API-key generation and secure entry.
- OAuth consent.
- Purchases, trials and spending limits.
- DNS and domain changes.
- External messages, campaigns and client access.
- Real-client-data approval.
- Material commercial, legal, regulatory and irreversible decisions.
- Final acceptance and release.

## 3. Phase programme

## Phase CF-0 — Governance baseline

### Chat deliverables

- Product vision and numbered requirements.
- Architecture and decision log.
- Build, security, test and approval rules.
- Third-party tool registry.
- Requirement-to-test traceability structure.

### Completion test

Every implementation task can identify its controlling requirement, acceptance test, owner and approval gate.

### Status

Substantially complete; traceability expansion remains active.

## Phase CF-1 — Deterministic consulting kernel

### Chat deliverables

- Lifecycle stage and operational-state rules.
- Transition validation.
- Decision and approval classification.
- Commands, events and idempotency contracts.
- Quality, defect, exception and release-gate logic.
- Agent envelope, context and Founder packet models.
- Unit tests for deterministic behaviour.

### Completion test

The kernel can reject illegal transitions, unapproved external action, self-approval, duplicate execution and release with blocking defects without an LLM.

### Status

Core contracts and initial unit tests are committed; target-machine and CI validation remain outstanding.

## Phase CF-2 — Canonical engagement and persistence design

### Chat deliverables

- Engagement aggregate and invariants.
- Entity and relationship model.
- Event and audit semantics.
- Persistence, versioning, concurrency and retention rules.
- API and error contracts.
- Founder cockpit read models.

### Completion test

Codex can implement storage and APIs without inventing material business rules.

## Phase CF-3 — Knowledge and methodology system

### Chat deliverables

- Source manifest and alias map.
- Source, passage, method, archetype and method-selection schemas.
- Ingestion acceptance cases.
- Retrieval evaluation questions.
- Methodology Radar candidate, novelty, copyright and promotion rules.
- Initial machine-readable domain-pack manifests.

### Completion test

Every derived method record can be traced to original source passages, and unresolved references are explicitly reported rather than silently repaired.

## Phase CF-4 — Synthetic engagement suite

### Chat deliverables

For each engagement type:

- Fictional client and mandate.
- Stakeholders and interview transcripts.
- Structured and unstructured data.
- Deliberate contradictions and quality defects.
- Expected problem archetypes and method selections.
- Expected rejected methods.
- Expected calculations and tolerances.
- Expected Founder escalations.
- Reference recommendation, implementation and benefits logic.
- Expected PPTX, DOCX, XLSX and HTML structure.

### Primary fixture families

1. Corporate and business-unit strategy.
2. Growth and commercial strategy.
3. Cost and productivity.
4. Customer experience.
5. Operating-model transformation.
6. Organisation and workforce.
7. Digital and AI transformation.
8. Risk and controls.
9. M&A and integration.
10. Carve-out and separation.
11. IPO, valuation and capital strategy.
12. Implementation and change.
13. Benefits realisation and performance improvement.

### Compound fixtures

- AI transformation + workforce + operating model.
- M&A + separation + technology + benefits.
- Growth + customer experience + pricing.
- Cost + risk + controls.
- Strategy + capital allocation + implementation.

### Completion test

Each fixture contains enough evidence and ambiguity to test reasoning, but also contains explicit answer tolerances for objective evaluation.

## Phase CF-5 — Specialist agent pack

### Chat deliverables

For each agent:

- Mission and non-goals.
- Required and optional inputs.
- Minimum-sufficient context rules.
- Permitted tools and record scopes.
- Prohibited actions.
- Structured output schema.
- Evidence and uncertainty requirements.
- Escalation rules.
- Cost, timeout and retry defaults.
- Evaluation cases and expected behaviour.

### Initial agents

1. Engagement Partner.
2. Problem Architect.
3. Method Architect.
4. Research and Evidence Agent.
5. Quantitative and Value Agent.
6. Storyline Agent.
7. Deliverable Production Agent.
8. Implementation and Benefits Agent.
9. Independent Quality Agent.
10. Origination and Opportunity Agent.
11. Methodology Librarian.

### Completion test

Codex only needs to wire provider APIs and tool adapters; role logic and evaluations are already defined.

## Phase CF-6 — Research, analysis and modelling protocols

### Chat deliverables

- Research plan and stopping-rule templates.
- Claim and evidence rules.
- Source-quality and contradiction handling.
- Analytical run manifests.
- Financial-model and value-case standards.
- Scenario, sensitivity and break-even specifications.
- Spreadsheet architecture and reconciliation tests.
- Method-specific calculation examples.

### Completion test

All material calculations have deterministic specifications and expected-result tolerances.

## Phase CF-7 — Story, deliverable and infographic system

### Chat deliverables

- Shared semantic story model.
- Story patterns and section contracts.
- Slide, document, workbook and HTML manifests.
- Source-note and appendix rules.
- Visual archetype grammar.
- Example SVG and native-shape specifications.
- Golden screenshots and visual-quality rubrics.
- Cross-format reconciliation cases.

### Completion test

Renderers can be built from semantic specifications without asking Codex to invent consulting content or visual logic.

## Phase CF-8 — CRM and origination system

### Chat deliverables

- CRM/offdata system boundary.
- HubSpot Free field mapping.
- Stable identifier and synchronisation rules.
- Opportunity dossier and score.
- Trigger and source taxonomy.
- Outreach, suppression and approval policy.
- Synthetic CRM and campaign fixtures.

### Completion test

Codex can integrate against fixtures first and later replace the fixture adapter with OAuth-backed HubSpot access.

## Phase CF-9 — Security, privacy and regionalisation

### Chat deliverables

- Data classification.
- Threat model and abuse cases.
- Tenant and engagement isolation requirements.
- Singapore-first deployment requirements.
- Regional-cell expansion model.
- Retention, deletion and export rules.
- Provider and processor register schema.
- Security and incident test catalogue.

### Completion test

No real-client-data deployment can proceed without explicit evidence against every mandatory control.

## Phase CF-10 — Codex integration handoff

Codex receives:

- The complete controlling documentation.
- Machine-readable schemas and configuration.
- Deterministic core source code.
- Unit and evaluation tests.
- Synthetic fixtures.
- Expected outputs and tolerances.
- A phase-specific implementation issue.
- A definition of done and rollback procedure.

Codex must not silently redesign a contract. Where implementation reveals a problem, it opens a decision record and proposes alternatives.

## 4. Handoff quality standard

A task is ready for Codex only when it contains:

1. Objective.
2. Scope and explicit exclusions.
3. Inputs and dependencies.
4. Required outputs.
5. Data and interface contracts.
6. Acceptance tests.
7. Security and permission constraints.
8. Expected error behaviour.
9. Rollback or reversibility requirement.
10. Founder decisions, if any.

## 5. Credit-efficiency rules

- Do not ask Codex to brainstorm an architecture already decided here.
- Do not use Codex to draft long requirements or synthetic content.
- Do not use an agent for deterministic formatting, parsing or test execution.
- Give Codex one bounded issue at a time.
- Require a plan before execution but keep the plan implementation-specific.
- Require reuse of committed contracts and fixtures.
- Use cheaper models only after regression tests can detect quality loss.
- Preserve working context and prefer targeted repair over full restart.

## 6. Current priority order

1. Complete requirement-to-test traceability.
2. Complete persistence and API design.
3. Produce the full `FIXTURE-DAI-001` source and data pack.
4. Complete agent prompt and evaluation packs.
5. Complete knowledge ingestion test cases and domain manifests.
6. Produce story and infographic golden examples.
7. Produce CRM and Methodology Radar fixtures.
8. Complete security and regionalisation artefacts.
9. Hand the validated integration backlog to Codex.

## 7. Definition of overall chat-first completion

The chat-first stage is complete when Codex can build the first end-to-end synthetic engagement by reading repository artefacts and performing integration work only, with no need to invent material consulting logic, product behaviour, data semantics, agent roles, expected answers or quality standards.