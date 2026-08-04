# 15 — Architecture and Product Decision Log

Record material decisions here until a dedicated ADR directory is created.

## DEC-001 — Canonical repository

**Status:** Approved  
**Decision:** `rayrayxing/offdata-os` is the canonical build repository.  
**Reason:** It was private and empty, avoiding conflicts with prior offdata concepts.  
**Consequence:** `rayrayxing/offdata` and `rayrayxing/offdata-clean` remain historical references only.

## DEC-002 — Founder operating model

**Status:** Approved  
**Decision:** Founder is product owner and final accountable reviewer; Codex performs engineering execution.  
**Reason:** Founder is non-technical and requires decision-ready rather than code-centric interaction.  
**Consequence:** Every phase must end with a plain-English Founder report and approval gate.

## DEC-003 — Initial user and region

**Status:** Approved  
**Decision:** Initial user is the Founder only. Initial production-region preference is Singapore.  
**Reason:** Current operating location and lean initial scope.  
**Consequence:** Architecture must support future multi-user roles and regional deployment cells without requiring them in Phase 0.

## DEC-004 — Budget posture

**Status:** Approved  
**Decision:** Local-first and free-tier-first until commercialisation.  
**Reason:** Minimise cost before product validation.  
**Consequence:** No paid resources or trials without Founder approval and an explicit cost-benefit note.

## DEC-005 — CRM direction

**Status:** Provisional  
**Decision:** Use HubSpot Free as the initial relationship and opportunity CRM.  
**Reason:** Sufficient basic contacts, companies and deal continuity without paid automation.  
**Consequence:** offdata owns opportunity intelligence, engagement state and automation. Reassess only when volume justifies paid CRM capabilities.

## DEC-006 — Initial application architecture

**Status:** Approved as design default; implementation subject to Phase 0 validation  
**Decision:** Next.js frontend, Python/FastAPI backend, PostgreSQL, S3-compatible storage and containerised local development.  
**Reason:** Strong fit for web experience, consulting analytics and reproducible local development.  
**Consequence:** Codex must report material reasons before substituting core components.

## DEC-007 — Agent and durable workflow direction

**Status:** Provisional for later phases  
**Decision:** Pydantic AI is the initial typed agent-layer recommendation; Restate is the initial durable workflow recommendation.  
**Reason:** Typed Python contracts and strong long-running workflow semantics.  
**Consequence:** Interfaces must remain replaceable; no implementation is authorised before the relevant phase.

## DEC-008 — Existing agent platforms

**Status:** Deferred  
**Decision:** OpenClaw, Hermes and Buzz are potential bounded integrations, not the canonical system of record.  
**Reason:** They offer useful gateway, personal-agent and collaboration capabilities but should not own client truth or governance.  
**Consequence:** Pilot only after the core synthetic engagement workflow is stable.

## DEC-009 — Testing scope

**Status:** Approved  
**Decision:** Build one synthetic primary fixture for each of thirteen engagement types plus compound fixtures.  
**Reason:** Cross-domain methodology and deliverable performance must be proven systematically.  
**Consequence:** Fixture creation is a product asset, not disposable test data.

## DEC-010 — Knowledge and copyright

**Status:** Approved  
**Decision:** Preserve original source files and provenance; independently reconstruct reusable methods and visuals.  
**Reason:** Protect traceability while avoiding copying proprietary expression.  
**Consequence:** Methodology candidates require source, novelty, copyright and regression review before promotion.

## Decision template

```markdown
## DEC-XXX — Title

**Status:** Proposed / Approved / Rejected / Superseded  
**Date:** YYYY-MM-DD  
**Owner:** Founder or delegated authority

### Context

### Options considered

### Decision

### Reasons

### Consequences

### Cost and security impact

### Reversibility and migration

### Approval
```
