# 00 — Start Here

## Purpose

This document tells Codex and the Founder how to use the offdata Build Pack.

## Current authorised scope

The repository is in **Phase 0: controlled project foundation**. No production infrastructure, real client data, external outreach or paid service activation is authorised.

A deterministic starter package now exists in `packages/offdata-core/`. Codex must validate and integrate it during Phase 0 rather than re-deriving lifecycle and approval rules from scratch.

## Canonical repository

`rayrayxing/offdata-os` is the only controlling build repository.

The following repositories are historical references only:

- `rayrayxing/offdata`
- `rayrayxing/offdata-clean`

Do not merge their specifications into this project unless a proposal is separately reviewed and approved.

## Read order for Codex

1. `AGENTS.md`
2. This file
3. `01-PRODUCT-VISION.md`
4. `02-FUNCTIONAL-REQUIREMENTS.md`
5. `03-ARCHITECTURE.md`
6. `04-DATA-MODEL.md`
7. `05-AGENT-SPECIFICATIONS.md`
8. `06-LIFECYCLE-AND-GATES.md`
9. `07-SECURITY-AND-DATA-RESIDENCY.md`
10. `08-DELIVERABLE-STUDIO.md`
11. `09-CRM-AND-ORIGINATION.md`
12. `10-TESTING-STRATEGY.md`
13. `11-BUILD-BACKLOG.md`
14. `12-APPROVAL-MATRIX.md`
15. `13-FOUNDER-OPERATING-GUIDE.md`
16. `14-CODEX-KICKOFF.md`
17. `15-CHAT-FIRST-DEVELOPMENT-PLAN.md`
18. `16-REQUIREMENTS-CATALOGUE.md`
19. `17-THIRD-PARTY-TOOL-REGISTRY.md`
20. `config/lifecycle.yaml`
21. `config/policy-matrix.yaml`
22. `config/agent-roster.yaml`
23. `fixtures/manifest.yaml`
24. `schemas/`
25. `packages/offdata-core/`

## Build sequence

The system is designed as a whole but built in gated phases:

- Phase 0 — repository, local environment, CI, security baseline and documentation
- Phase 1 — knowledge ingestion and method registry
- Phase 2 — engagement system of record
- Phase 3 — lifecycle and durable workflow control
- Phase 4 — bounded specialist agents
- Phase 5 — research and evidence layer
- Phase 6 — quantitative and modelling services
- Phase 7 — storyline, infographics and deliverable studio
- Phase 8 — CRM integration
- Phase 9 — controlled origination engine
- Phase 10 — methodology radar
- Phase 11 — security and production readiness
- Phase 12 — synthetic pilot suite and launch gate

Codex must stop after each phase and obtain Founder approval.

## Chat-first work allocation

Architecture, requirements, schemas, deterministic policy logic, fixture design and review may be developed through ChatGPT and committed to this repository. Codex should focus on work that requires a real computer environment: installation, integration, execution, debugging, OAuth, rendering and deployment.

All chat-built source code remains provisional until Codex runs the repository tests in the approved macOS environment and reports the result.

## Build Pack source context

The design is informed by the uploaded canonical consulting lifecycle and methodology standards plus domain methodology packs covering:

- Corporate and business-unit strategy
- Growth and commercial strategy
- Cost and productivity
- Customer experience
- Operating-model transformation
- Organisation and workforce
- Digital and AI transformation
- Risk and controls
- M&A, carve-out and integration
- IPO, valuation and capital strategy
- Implementation and change
- Benefits realisation and performance improvement

The original source files are not yet committed. They must be imported later into `knowledge/source/` unchanged, checksummed and access-controlled. Extracted records must retain source provenance.

## Founder operating model

The Founder:

- Provides product decisions and business judgement.
- Creates accounts and subscriptions.
- Enters credentials through secure interfaces.
- Completes OAuth approvals.
- Reviews demonstrations and deliverables.
- Approves production, external communications and material changes.

Codex:

- Builds and tests the platform.
- Configures local and approved cloud environments.
- Creates documentation and rollback points.
- Reports issues in plain English.
- Stops for required Founder decisions.

ChatGPT:

- Develops and reviews architecture, requirements, schemas, policies, fixtures and bounded starter code.
- Pushes approved textual and deterministic development into GitHub.
- Reviews Codex pull requests and test evidence when requested.
- Does not replace computer-environment validation.

## Definition of done for any phase

A phase is complete only when:

- Approved requirements are implemented.
- Required tests pass.
- A separate review pass is complete.
- Documentation is updated.
- Costs and risks are disclosed.
- Rollback instructions exist.
- The Founder receives a plain-English completion report.
- The Founder explicitly approves progression.
