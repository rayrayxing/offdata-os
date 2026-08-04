# 21 — Engagement Aggregate and API Specification

## Status

Baseline v0.1 for Codex implementation. This document defines the canonical engagement boundary and service contracts. It is runtime-independent.

## 1. Aggregate boundary

An `Engagement` is the consistency boundary for consulting delivery. It owns references to, but does not embed full binary artefacts or CRM records.

### Required identity

- `engagement_id`
- `tenant_id`
- `engagement_code`
- `title`
- `client_organisation_id`
- `status`
- `lifecycle_stage`
- `operational_state`
- `assurance_tier`
- `data_region`
- `created_at`
- `created_by`
- `version`

### Controlled child records

- mandate
- decisions
- questions
- hypotheses
- method selections
- research plans
- source and evidence references
- assumptions and gaps
- analyses and model runs
- options and recommendations
- quality findings and approvals
- story maps and deliverable manifests
- initiatives and benefits
- workflow commands and events

## 2. Invariants

1. Every engagement belongs to exactly one tenant and one active data region.
2. Every material record carries `engagement_id`, stable ID and version.
3. Current lifecycle stage is the earliest unmet mandatory gate.
4. `cancelled` and `completed` engagements reject new execution commands except authorised reopen or archival commands.
5. External actions require an approval record whose scope covers the exact action and current version.
6. Released deliverables reference immutable evidence, model and story baselines.
7. A record from one engagement must not be resolved through another engagement's API context.
8. Agent-written changes must arrive as commands and produce auditable domain events.

## 3. Command pattern

Every mutating request uses a command envelope:

```json
{
  "command_id": "CMD-...",
  "command_type": "engagement.create",
  "tenant_id": "TEN-...",
  "engagement_id": null,
  "actor": {
    "actor_type": "founder|user|agent|system|integration",
    "actor_id": "..."
  },
  "expected_version": null,
  "idempotency_key": "...",
  "requested_at": "ISO-8601",
  "approval_id": null,
  "payload": {}
}
```

### Command response

```json
{
  "command_id": "CMD-...",
  "status": "accepted|rejected|pending_approval|conflict|failed",
  "aggregate_id": "ENG-...",
  "aggregate_version": 1,
  "event_ids": ["EVT-..."],
  "errors": [],
  "approval_requirement": null
}
```

## 4. Initial REST endpoints

### Engagements

- `POST /v1/engagements`
- `GET /v1/engagements`
- `GET /v1/engagements/{engagement_id}`
- `POST /v1/engagements/{engagement_id}/commands`
- `GET /v1/engagements/{engagement_id}/events`
- `GET /v1/engagements/{engagement_id}/timeline`
- `POST /v1/engagements/{engagement_id}/pause`
- `POST /v1/engagements/{engagement_id}/resume`
- `POST /v1/engagements/{engagement_id}/cancel`

### Mandate and decisions

- `GET /v1/engagements/{id}/mandate`
- `PUT /v1/engagements/{id}/mandate`
- `GET /v1/engagements/{id}/decisions`
- `POST /v1/engagements/{id}/decisions`
- `POST /v1/engagements/{id}/decisions/{decision_id}/resolve`

### Analytical records

- `GET|POST /v1/engagements/{id}/hypotheses`
- `GET|POST /v1/engagements/{id}/method-selections`
- `GET|POST /v1/engagements/{id}/claims`
- `GET|POST /v1/engagements/{id}/evidence`
- `GET|POST /v1/engagements/{id}/analyses`
- `GET|POST /v1/engagements/{id}/recommendations`

### Quality and release

- `GET|POST /v1/engagements/{id}/quality-findings`
- `POST /v1/engagements/{id}/release-gates/{gate_id}/evaluate`
- `GET|POST /v1/engagements/{id}/approvals`
- `GET|POST /v1/engagements/{id}/deliverables`

### Implementation and benefits

- `GET|POST /v1/engagements/{id}/initiatives`
- `GET|POST /v1/engagements/{id}/benefits`

## 5. Read models

### Founder engagement summary

Must return:

- title and client
- supported decision
- lifecycle and operational state
- current gate and blockers
- pending Founder decisions
- evidence gaps
- material assumptions
- quality status
- next best action
- recent activity
- cost and run summary

### Decision inbox item

Must return:

- decision required
- latest decision date
- decision class
- why Founder authority is required
- facts, assumptions and gaps
- options and consequences
- system recommendation
- commitment created by approval
- fallback

## 6. Error contract

All API errors use:

```json
{
  "error_id": "ERR-...",
  "code": "VERSION_CONFLICT",
  "message": "Plain-language explanation",
  "details": {},
  "correlation_id": "COR-...",
  "retryable": false
}
```

Minimum codes:

- `VALIDATION_ERROR`
- `NOT_FOUND`
- `ACCESS_DENIED`
- `VERSION_CONFLICT`
- `APPROVAL_REQUIRED`
- `APPROVAL_SCOPE_MISMATCH`
- `INVALID_TRANSITION`
- `IDEMPOTENCY_CONFLICT`
- `ENGAGEMENT_BLOCKED`
- `REGION_RESTRICTION`
- `RELEASE_GATE_FAILED`

## 7. Concurrency and idempotency

- Mutating commands require `expected_version` after creation.
- Reusing an idempotency key with identical payload returns the original response.
- Reusing it with a different payload fails.
- External-action commands must persist intent before execution and completion after execution.
- Retries must never resend an already completed external action.

## 8. Acceptance tests

1. Create and retrieve an engagement.
2. Reject cross-tenant access.
3. Reject stale expected versions.
4. Return the same result for an identical idempotent retry.
5. Reject an external action without scoped approval.
6. Persist command and resulting events with one correlation ID.
7. Reconstruct the aggregate from its event history.
8. Pause and resume without losing pending work.
9. Reject illegal lifecycle transitions.
10. Produce the Founder summary from read models without exposing restricted source text.
