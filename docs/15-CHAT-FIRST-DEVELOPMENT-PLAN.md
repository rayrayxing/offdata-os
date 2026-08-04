# 15 — Chat-First Development Plan

> Status: draft foundation. This document defines which offdata work should be completed through architecture/specification work in ChatGPT and which work should be reserved for Codex or another computer-operating engineering harness.

## 1. Objective

Reduce Codex credit consumption without weakening engineering quality. ChatGPT should complete work that can be expressed, reviewed and versioned as text or deterministic source code. Codex should concentrate on work that requires a real computer environment, package installation, browser or desktop interaction, credentials, integration debugging, rendering, deployment and repeated execution.

## 2. Governing rule

Use the cheapest reliable execution mode:

1. Deterministic code for known transformations and checks.
2. Chat-based architecture and specification for requirements, schemas and test design.
3. Codex for repository-wide implementation, environment execution and integration.
4. Founder action for credentials, OAuth, subscriptions, DNS, external sending and release approval.

No phase advances merely because an agent produced output. It advances only when the applicable acceptance tests and approval gate pass.

## 3. Work allocation

### ChatGPT is well suited to

- Product and consulting requirements.
- Architecture decisions and option analysis.
- Canonical data, event and API contracts.
- Lifecycle, decision-class and approval policy definitions.
- Agent purposes, boundaries, prompts and typed envelopes.
- Method and knowledge schemas.
- Synthetic engagement specifications.
- Evaluation rubrics and expected results.
- Threat scenarios and security requirements.
- CRM and origination operating rules.
- Story model, deliverable and infographic specifications.
- Starter deterministic Python or TypeScript modules.
- Unit-test definitions for deterministic logic.
- Third-party tool assessment and registry maintenance.
- Review of GitHub changes, pull requests and test evidence.

### Codex is required for

- Inspecting and configuring the Founder’s macOS environment.
- Installing approved runtimes, package managers and development tools.
- Creating and running the monorepo application shells.
- Launching PostgreSQL, object storage and other local services.
- Resolving dependency and operating-system issues.
- Running complete test suites and coverage tools.
- Browser and desktop testing.
- Rendering and inspecting PPTX, DOCX, XLSX, PDF and HTML.
- OAuth application configuration and integration testing.
- Cloud deployment, observability and backup configuration.
- Performance, load, recovery and end-to-end tests.
- Opening implementation pull requests with machine-produced evidence.

### Founder action is required for

- Passwords, MFA and account recovery.
- API key generation and secure entry.
- OAuth consent.
- Paid subscriptions or trials.
- DNS and domain changes.
- Production deployment with real client information.
- Client or prospect communication.
- Commercial, legal, regulatory and irreversible decisions.
- Final release and engagement approval.

## 4. Development phases

### Phase A — Requirements and control contracts

Complete in ChatGPT:

- Numbered functional and non-functional requirements.
- Lifecycle and operational-state configuration.
- Decision-class and approval matrix.
- Founder interruption packet.
- Core record and event schemas.
- Agent envelope and context-package schemas.
- Third-party tool registry.

Gate: requirements are internally consistent, traceable to the Build Pack and contain explicit acceptance tests.

### Phase B — Deterministic core package

Complete primarily in ChatGPT, verified by Codex:

- Lifecycle stage detection.
- Transition validation.
- Approval policy evaluation.
- Typed domain enums and records.
- Unit tests for deterministic rules.

Gate: package installs locally and all deterministic tests pass.

### Phase C — Local engineering foundation

Complete in Codex:

- Next.js and FastAPI shells.
- PostgreSQL and S3-compatible local storage.
- Containers and one-command startup.
- CI, formatting, type checking, tests and security scanning.

Gate: clean macOS setup starts and tests the system without paid infrastructure.

### Phase D — Knowledge ingestion

Shared:

- ChatGPT defines canonical schemas, alias rules and extraction acceptance cases.
- Codex builds parsers, checksums, storage, retrieval and ingestion tests.

Gate: source records are deterministic, traceable and searchable; original files remain unchanged.

### Phase E — Engagement system of record

Shared:

- ChatGPT defines record semantics, workflow events and screen requirements.
- Codex implements migrations, APIs, audit logs, backup and the Founder cockpit shell.

Gate: engagement isolation, version recovery and backup restoration pass.

### Phase F — Durable lifecycle and policy engine

Shared:

- ChatGPT defines transitions, gates, escalation and failure cases.
- Codex integrates Restate or the approved durable runtime and exercises interruption/recovery.

Gate: a synthetic engagement survives restart, waits for approval and does not duplicate actions.

### Phase G — Specialist agents and evaluations

Shared:

- ChatGPT develops prompts, contracts, rubrics, fixture inputs and expected outcomes.
- Codex integrates model APIs, tool permissions, tracing and evaluation execution.

Gate: every agent passes schema, grounding, escalation, isolation, injection and cost tests.

### Phase H — Research, analytics and modelling

Shared:

- ChatGPT specifies evidence rules, analysis protocols and model checks.
- Codex builds web/document tools, analytical runtimes, Excel generation and reproducibility controls.

Gate: a recommendation traces to evidence and a value model reproduces from controlled inputs.

### Phase I — Deliverable and infographic studio

Shared:

- ChatGPT defines story, visual and cross-format contracts.
- Codex builds and visually tests the renderers.

Gate: PPTX, DOCX, XLSX, PDF, SVG and HTML agree on material claims, numbers and recommendations.

### Phase J — CRM and origination

Shared:

- ChatGPT defines CRM objects, opportunity scoring, outreach policies and approval rules.
- Codex integrates HubSpot fixtures and later OAuth.

Gate: opportunity-to-engagement continuity works without exposing confidential engagement records.

### Phase K — Methodology Radar

Shared:

- ChatGPT defines discovery taxonomy, novelty tests, copyright controls and promotion rubric.
- Codex implements scheduled discovery, source capture, deduplication and candidate workflows.

Gate: candidates can be found and tested but cannot promote themselves.

### Phase L — Production readiness and engagement suite

Shared:

- ChatGPT defines thirteen primary engagement fixtures and compound cases.
- Codex runs security, recovery, performance, artifact and end-to-end suites.

Gate: Founder approves a controlled client pilot.

## 5. Immediate next work

The next repository additions should be:

1. Numbered requirements catalogue.
2. Machine-readable lifecycle and policy configuration.
3. Deterministic `offdata-core` Python package.
4. Unit tests for lifecycle and approval rules.
5. Third-party tool and skill registry.
6. Synthetic engagement fixture manifest.
7. Founder decision-packet and agent-envelope schemas.

These items can be created before Codex begins Phase 0. Codex should then validate, integrate and extend them rather than rediscovering the requirements.
