# 28 — Database and Persistence Specification

## Status

Canonical logical design v1.0. This specification is technology-compatible with PostgreSQL and is independent of the final ORM or migration tool.

## 1. Persistence principles

1. PostgreSQL is the canonical structured store.
2. Object storage contains original files, generated artefacts and large run outputs.
3. Search indexes and vector representations are derived and rebuildable.
4. Chat transcripts and provider memory are never canonical engagement truth.
5. Every material mutation creates an auditable event.
6. Tenant, engagement and data-region scope are explicit on every restricted record.
7. Released baselines are immutable.
8. Soft deletion does not substitute for configured retention and verified deletion.
9. External actions use durable intent, attempt and completion records.
10. Database migrations are forward-tested, reversible where practical and backed up before destructive change.

## 2. Schema namespaces

Recommended PostgreSQL schemas:

- `identity` — tenants, users, roles and service actors.
- `crm` — controlled CRM links and synchronisation state.
- `engagement` — engagement aggregates and consulting records.
- `knowledge` — global and tenant-scoped source and methodology records.
- `workflow` — commands, events, tasks, approvals and durable execution state.
- `analysis` — datasets, analytical runs, models and named outputs.
- `delivery` — stories, artefacts, manifests, render and release records.
- `implementation` — initiatives, adoption, outcomes and benefits.
- `audit` — immutable audit events and security-relevant activity.
- `ops` — provider, usage, cost, health and retention state.

The first implementation may use a single physical schema if migration tooling is simpler, but logical boundaries and table prefixes must remain clear.

## 3. Common columns

Material tables should include as applicable:

- `id` — stable prefixed ULID or UUID.
- `tenant_id`.
- `engagement_id`.
- `data_region`.
- `version`.
- `status`.
- `created_at`.
- `created_by_type`.
- `created_by_id`.
- `updated_at`.
- `updated_by_type`.
- `updated_by_id`.
- `valid_from`.
- `valid_to`.
- `supersedes_id`.
- `classification`.
- `retention_policy_id`.
- `correlation_id`.

Timestamps use UTC. Client-facing local time is a presentation concern.

## 4. Identity and access tables

### `identity.tenants`

- `tenant_id` primary key.
- legal and display names.
- default data region.
- status.
- retention defaults.
- created and closed timestamps.

### `identity.users`

- `user_id` primary key.
- tenant association.
- identity-provider subject.
- email and display name.
- status and MFA state.
- default locale and timezone.

### `identity.roles`

Initial roles:

- Founder.
- delegated Partner.
- engagement lead.
- reviewer.
- contributor.
- client reviewer.
- integration service.
- system operator.

### `identity.user_role_assignments`

Role grants are scoped by tenant, engagement and optional capability.

### `identity.service_actors`

Versioned records for agents, schedulers and integrations, including permitted scopes and owner.

## 5. CRM boundary tables

### `crm.organisation_links`

Maps offdata organisation IDs to HubSpot or future CRM IDs.

### `crm.contact_links`

Stores only controlled relationship identifiers and approved summary metadata.

### `crm.opportunity_links`

Links pipeline records to offdata opportunity dossiers and converted engagements.

### `crm.sync_runs`

Stores direction, cursor, counts, rate-limit state, errors and retry information.

### `crm.sync_conflicts`

Requires a deterministic or Founder-resolved decision. Never silently overwrites materially different records.

## 6. Engagement aggregate tables

### `engagement.engagements`

Core fields:

- `engagement_id`.
- `tenant_id`.
- `engagement_code`.
- `title`.
- `client_organisation_id`.
- `lifecycle_stage`.
- `operational_state`.
- `assurance_tier`.
- `data_region`.
- `aggregate_version`.
- `current_gate_id`.
- `supported_decision_id`.
- `started_at`, `target_end_at`, `closed_at`.

### `engagement.mandates`

Versioned mandate, supported decision, scope, exclusions, constraints, stakeholders, evidence position, assumptions and success tests.

### `engagement.decisions`

- decision owner and deadline.
- question and options.
- decision class.
- materiality and reversibility.
- required evidence and approval.
- status and selected option.
- consequences and fallback.

### `engagement.questions`

Decision-linked analytical questions and their priority.

### `engagement.hypotheses`

- statement.
- status.
- confidence.
- supporting and contradicting claim links.
- discriminating tests.
- consequences if true or false.

### `engagement.assumptions`

- statement.
- materiality.
- owner.
- validation action.
- expiry.
- status.

### `engagement.evidence_gaps`

- missing evidence.
- consequence.
- owner.
- planned resolution.
- deadline.
- tolerated or blocking state.

### `engagement.options`

Alternative courses of action, including do-nothing and defer where relevant.

### `engagement.recommendations`

Links decision, evidence baseline, analysis outputs, conditions, risks, implementation and value expectations.

## 7. Knowledge and evidence tables

### `knowledge.source_documents`

Implements the committed `SourceDocument` contract.

Original source binaries are stored in object storage and addressed by immutable object reference and checksum.

### `knowledge.source_passages`

Passage text and exact location. Derived indexes refer to this ID.

### `knowledge.claims`

Fields:

- `claim_id`.
- text.
- epistemic status.
- scope.
- materiality.
- confidence.
- time sensitivity.
- current validation state.

### `knowledge.claim_evidence_links`

Many-to-many relationship with link type:

- supports.
- contradicts.
- contextualises.
- limits.
- supersedes.

Include reviewer, strength and rationale.

### `knowledge.methods`

Versioned canonical method records.

### `knowledge.problem_archetypes`

Versioned diagnostic signatures and method relationships.

### `knowledge.method_selections`

Engagement-specific selected, sequenced and rejected methods.

### `knowledge.methodology_candidates`

Radar candidates remain separated from canonical methods until approved promotion.

### `knowledge.aliases`

- alias.
- canonical target type and ID.
- source of alias.
- confidence.
- active range.
- resolution status.

No ambiguous alias is auto-resolved without a deterministic disambiguation rule.

## 8. Workflow and execution tables

### `workflow.commands`

Immutable command envelope and result state.

Unique constraints:

- `(tenant_id, command_id)`.
- `(tenant_id, actor_id, idempotency_key)` where key exists.

### `workflow.domain_events`

Append-only event records with aggregate version and correlation.

Unique constraint:

- `(engagement_id, aggregate_version)` for aggregate-changing events.

### `workflow.tasks`

- task type.
- owner actor.
- inputs and expected outputs.
- prerequisites.
- status.
- attempt count and retry budget.
- due and timeout fields.
- parent and workstream relationships.

### `workflow.approvals`

- approver and authority basis.
- scope expression.
- exact record or action versions.
- approval decision and conditions.
- expiry and revocation.

### `workflow.external_actions`

Durable states:

1. proposed.
2. approval_required.
3. approved.
4. intent_persisted.
5. executing.
6. succeeded.
7. failed_retryable.
8. failed_terminal.
9. compensated where possible.
10. cancelled.

Store provider request IDs and response checksums to prevent duplicate execution.

### `workflow.agent_runs`

- agent and contract version.
- provider and model.
- prompt and context package references.
- tool calls.
- start/end state.
- token, cost and latency.
- result envelope.
- evaluation and quality links.

## 9. Analysis and modelling tables

### `analysis.datasets`

Metadata, object reference, checksum, schema, classification, origin and row/column statistics.

### `analysis.dataset_versions`

Immutable versions and transformation lineage.

### `analysis.runs`

- run type.
- code and environment reference.
- dependency lock reference.
- inputs and assumptions.
- parameters and random seeds.
- outputs and diagnostics.
- status and reproducibility state.

### `analysis.named_outputs`

Stable outputs that can be used by stories and deliverables:

- value.
- unit.
- period.
- display format.
- uncertainty or interval.
- source run.
- approval state.

### `analysis.models`

Model purpose, owner, intended use, assurance tier and approved version.

### `analysis.model_checks`

Formula, unit, reconciliation, sensitivity, independent-calculation and limitation results.

## 10. Quality and release tables

### `engagement.quality_findings`

- object and version reviewed.
- requirement or rubric violated.
- defect statement.
- consequence.
- severity and blocking status.
- required repair and retest.
- reviewer independence.

### `engagement.quality_exceptions`

- unmet requirement.
- reason and alternatives.
- residual risk.
- compensating controls.
- authority and expiry.

### `engagement.release_gates`

- gate type and assurance tier.
- baseline references.
- required checks.
- results.
- decision.
- approver and timestamp.

### `engagement.signoffs`

Immutable checksum and reviewer conclusion.

## 11. Story and delivery tables

### `delivery.story_models`

Versioned semantic proposition hierarchy.

### `delivery.story_nodes`

Each node contains assertion, supporting claims, analysis outputs, implications, actions and visual intent.

### `delivery.visual_specs`

Structured visual-archetype parameters and data links.

### `delivery.deliverable_manifests`

- format.
- template and brand version.
- story baseline.
- model baseline.
- evidence baseline.
- sections, pages or slides.
- status and approval state.

### `delivery.artefacts`

- object reference.
- checksum.
- MIME type.
- render engine and version.
- confidentiality and release state.

### `delivery.render_runs`

Input manifest, renderer logs, output references and visual-QA results.

## 12. Implementation and benefits tables

### `implementation.initiatives`

Recommendation link, owner, outputs, milestones, dependencies, resources, costs, risks, controls and acceptance criteria.

### `implementation.milestones`

Observable completion evidence and decision gates.

### `implementation.adoption_measures`

Behaviour, capability, workflow and utilisation indicators.

### `implementation.outcomes`

Observed business or public outcomes distinct from project outputs.

### `implementation.benefits`

- objective and outcome link.
- owner.
- baseline and counterfactual.
- measure, unit and timing.
- attribution method.
- gross, leakage, net and verified value.
- verification threshold and status.

### `implementation.benefit_observations`

Time-stamped measured values and evidence references.

## 13. Audit and operations tables

### `audit.audit_events`

Append-only security and business audit trail. Application roles cannot update or delete it.

### `ops.provider_registry`

Model, research, storage, CRM, rendering and monitoring providers with region, data-use and retention metadata.

### `ops.usage_ledger`

Costs and consumption by tenant, engagement, workstream, agent and task.

### `ops.retention_policies`

Retention and deletion behaviour by classification, jurisdiction and engagement.

### `ops.deletion_jobs`

Requested, approved, executed and verified deletion state.

### `ops.health_events`

Runtime and integration health, outages and recovery.

## 14. Row-level security

PostgreSQL row-level security should be used as defence in depth.

Every request establishes:

- tenant ID.
- user or actor ID.
- engagement scopes.
- role and capabilities.
- allowed data regions.

Application-level checks remain mandatory. RLS must not be the only permission layer.

## 15. Versioning model

Use optimistic concurrency:

- Mutating commands specify expected aggregate or record version.
- A mismatch returns `VERSION_CONFLICT`.
- Material record versions are immutable; the current pointer advances.
- Audit and event records remain append-only.
- Derived read models may be rebuilt from authoritative records and events.

## 16. Deletion model

Deletion requires:

1. Scope and authority validation.
2. Legal, contractual and retention checks.
3. Dependency inventory.
4. Backup and derived-index handling.
5. Execution.
6. Verification.
7. Audit record without retaining the deleted content.

Global canonical knowledge must not be contaminated by client content, reducing cross-client deletion complexity.

## 17. Backup and recovery

Minimum tests:

- full local database backup and restore.
- object-store checksum verification.
- point-in-time recovery in managed environments.
- restoration into an isolated environment.
- event/read-model reconstruction.
- deleted or superseded record behaviour.
- recovery after a partially completed external action.

## 18. Migration rules

- Every schema change uses a committed migration.
- Migrations run against representative synthetic volume.
- Destructive migrations require backup and explicit Founder approval in production.
- Expand-and-contract patterns are preferred for zero-downtime change.
- Rollback or forward-repair procedure is documented.
- Schema and application compatibility windows are explicit.

## 19. Initial implementation sequence

1. Identity and tenant scope.
2. Engagement aggregate, commands and events.
3. Mandate, decisions, hypotheses and approvals.
4. Source, passage, claim and evidence links.
5. Methods, archetypes and selections.
6. Analysis runs and named outputs.
7. Quality and release gates.
8. Story and deliverable manifests.
9. Initiatives and benefits.
10. CRM links and operational ledgers.

## 20. Persistence acceptance cases

1. A record from Tenant A is inaccessible in Tenant B context.
2. A record from Engagement A is inaccessible in Engagement B context unless explicitly shared by policy.
3. Stale expected version is rejected.
4. Identical idempotent command returns the original result.
5. Conflicting reuse of an idempotency key is rejected.
6. Event history reconstructs the same aggregate state.
7. Released baselines remain immutable.
8. Backup restoration reproduces record and object checksums.
9. A deletion job removes required content and rebuildable indexes while preserving a non-content audit record.
10. An interrupted external action does not execute twice.
11. A confidential source cannot be persisted without tenant scope.
12. A client source cannot enter the global methodology namespace.
13. A Methodology Radar candidate cannot become canonical without all promotion evidence.
14. Founder cockpit read models do not expose restricted passage text by default.
15. Every released artefact resolves to exact evidence, model and story baselines.