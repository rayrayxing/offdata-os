-- offdata core persistence baseline
-- PostgreSQL 16+
-- Requirements: DATA-001..010, LIFE-007, AUTH-001..009, AGENT-003..006, SEC-002..005

BEGIN;

CREATE OR REPLACE FUNCTION offdata_current_tenant()
RETURNS text
LANGUAGE sql
STABLE
AS $$
    SELECT NULLIF(current_setting('offdata.tenant_id', true), '')
$$;

CREATE TABLE tenants (
    tenant_id text PRIMARY KEY,
    name text NOT NULL,
    home_region text NOT NULL,
    status text NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'suspended', 'closed')),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE actors (
    actor_id text PRIMARY KEY,
    tenant_id text REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    actor_type text NOT NULL
        CHECK (actor_type IN ('founder', 'user', 'agent', 'system', 'integration')),
    display_name text NOT NULL DEFAULT '',
    agent_version text,
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE organisations (
    organisation_id text PRIMARY KEY,
    tenant_id text NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    name text NOT NULL,
    relationship_status text NOT NULL DEFAULT 'prospect',
    record jsonb NOT NULL DEFAULT '{}'::jsonb,
    version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, name)
);

CREATE TABLE contacts (
    contact_id text PRIMARY KEY,
    tenant_id text NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    organisation_id text NOT NULL REFERENCES organisations(organisation_id) ON DELETE CASCADE,
    name text NOT NULL,
    consent_status text NOT NULL DEFAULT 'unknown'
        CHECK (consent_status IN ('unknown', 'permitted', 'opted_out', 'objected', 'suppressed')),
    suppression_reason text,
    record jsonb NOT NULL DEFAULT '{}'::jsonb,
    version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CHECK (
        consent_status NOT IN ('opted_out', 'objected', 'suppressed')
        OR NULLIF(suppression_reason, '') IS NOT NULL
    )
);

CREATE TABLE opportunities (
    opportunity_id text PRIMARY KEY,
    tenant_id text NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    organisation_id text NOT NULL REFERENCES organisations(organisation_id) ON DELETE CASCADE,
    stage text NOT NULL DEFAULT 'detected',
    dossier jsonb NOT NULL,
    version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE engagements (
    engagement_id text PRIMARY KEY,
    tenant_id text NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    engagement_code text NOT NULL,
    title text NOT NULL,
    client_organisation_id text NOT NULL REFERENCES organisations(organisation_id),
    status text NOT NULL
        CHECK (status IN ('draft', 'active', 'paused', 'blocked', 'cancelled', 'completed', 'archived')),
    lifecycle_stage text NOT NULL
        CHECK (lifecycle_stage ~ '^LIFE-STAGE-(0[1-9]|1[0-3])$'),
    operational_state text NOT NULL
        CHECK (operational_state IN ('normal', 'waiting', 'blocked', 'retry', 'cancelled', 'completed')),
    assurance_tier text NOT NULL CHECK (assurance_tier IN ('T0', 'T1', 'T2', 'T3')),
    data_region text NOT NULL,
    supported_decision text NOT NULL,
    decision_owner text NOT NULL,
    mandate jsonb NOT NULL DEFAULT '{}'::jsonb,
    current_gate text,
    version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
    created_by text NOT NULL REFERENCES actors(actor_id),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, engagement_code),
    CHECK (operational_state <> 'cancelled' OR status = 'cancelled'),
    CHECK (operational_state <> 'completed' OR status IN ('completed', 'archived'))
);

CREATE TABLE commands (
    command_id text PRIMARY KEY,
    tenant_id text NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    engagement_id text REFERENCES engagements(engagement_id) ON DELETE CASCADE,
    command_type text NOT NULL,
    occurred_at timestamptz NOT NULL,
    actor_id text NOT NULL REFERENCES actors(actor_id),
    correlation_id text NOT NULL,
    causation_id text,
    idempotency_key text,
    approval_id text,
    expected_version integer CHECK (expected_version IS NULL OR expected_version >= 1),
    payload jsonb NOT NULL,
    payload_sha256 char(64) NOT NULL,
    status text NOT NULL
        CHECK (status IN ('received', 'accepted', 'rejected', 'pending_approval', 'conflict', 'failed')),
    result jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (command_type = 'create_engagement' OR engagement_id IS NOT NULL),
    CHECK (command_type = 'create_engagement' OR expected_version IS NOT NULL)
);

CREATE UNIQUE INDEX commands_tenant_idempotency_unique
    ON commands (tenant_id, idempotency_key)
    WHERE idempotency_key IS NOT NULL;
CREATE INDEX commands_engagement_occurred_idx
    ON commands (tenant_id, engagement_id, occurred_at);

CREATE TABLE domain_events (
    event_id text PRIMARY KEY,
    tenant_id text NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    engagement_id text REFERENCES engagements(engagement_id) ON DELETE CASCADE,
    event_type text NOT NULL,
    occurred_at timestamptz NOT NULL,
    actor_id text NOT NULL REFERENCES actors(actor_id),
    aggregate_type text NOT NULL,
    aggregate_id text NOT NULL,
    aggregate_version integer NOT NULL CHECK (aggregate_version >= 1),
    correlation_id text NOT NULL,
    causation_id text,
    idempotency_key text,
    payload jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, aggregate_type, aggregate_id, aggregate_version)
);
CREATE INDEX domain_events_engagement_idx
    ON domain_events (tenant_id, engagement_id, occurred_at, event_id);
CREATE INDEX domain_events_correlation_idx
    ON domain_events (tenant_id, correlation_id);

CREATE TABLE idempotency_records (
    tenant_id text NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    idempotency_key text NOT NULL,
    command_id text NOT NULL REFERENCES commands(command_id) ON DELETE CASCADE,
    request_sha256 char(64) NOT NULL,
    response_status integer,
    response_body jsonb,
    external_action_completed boolean NOT NULL DEFAULT false,
    completed_at timestamptz,
    expires_at timestamptz,
    PRIMARY KEY (tenant_id, idempotency_key)
);

CREATE TABLE approval_requests (
    approval_request_id text PRIMARY KEY,
    tenant_id text NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    engagement_id text NOT NULL REFERENCES engagements(engagement_id) ON DELETE CASCADE,
    requested_at timestamptz NOT NULL,
    requested_by text NOT NULL REFERENCES actors(actor_id),
    decision_classes jsonb NOT NULL,
    decision_required text NOT NULL,
    supporting_packet_reference text NOT NULL,
    required_approver_roles jsonb NOT NULL,
    latest_responsible_date timestamptz NOT NULL,
    expires_at timestamptz,
    status text NOT NULL DEFAULT 'pending',
    aggregate_version integer NOT NULL CHECK (aggregate_version >= 1),
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (expires_at IS NULL OR expires_at > requested_at)
);

CREATE TABLE approval_records (
    approval_id text PRIMARY KEY,
    tenant_id text NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    approval_request_id text NOT NULL REFERENCES approval_requests(approval_request_id),
    engagement_id text NOT NULL REFERENCES engagements(engagement_id) ON DELETE CASCADE,
    decided_at timestamptz NOT NULL,
    decided_by text NOT NULL REFERENCES actors(actor_id),
    outcome text NOT NULL
        CHECK (outcome IN ('approved', 'conditional', 'rejected', 'expired', 'withdrawn')),
    conditions jsonb NOT NULL DEFAULT '[]'::jsonb,
    rationale text NOT NULL DEFAULT '',
    evidence_reference text NOT NULL,
    approved_aggregate_version integer NOT NULL CHECK (approved_aggregate_version >= 1),
    scope_sha256 char(64) NOT NULL,
    expires_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (outcome <> 'conditional' OR jsonb_array_length(conditions) > 0)
);
ALTER TABLE commands
    ADD CONSTRAINT commands_approval_fk
    FOREIGN KEY (approval_id) REFERENCES approval_records(approval_id);

CREATE TABLE source_documents (
    source_id text PRIMARY KEY,
    tenant_id text REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    engagement_id text REFERENCES engagements(engagement_id) ON DELETE CASCADE,
    original_filename text NOT NULL,
    checksum_sha256 char(64) NOT NULL,
    title text NOT NULL,
    metadata jsonb NOT NULL,
    object_reference text NOT NULL,
    confidentiality text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE source_passages (
    passage_id text PRIMARY KEY,
    source_id text NOT NULL REFERENCES source_documents(source_id) ON DELETE CASCADE,
    tenant_id text REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    engagement_id text REFERENCES engagements(engagement_id) ON DELETE CASCADE,
    location jsonb NOT NULL,
    text_content text NOT NULL,
    extraction_method text NOT NULL,
    extraction_confidence numeric(5,4) NOT NULL
        CHECK (extraction_confidence BETWEEN 0 AND 1),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE method_selections (
    selection_id text PRIMARY KEY,
    tenant_id text NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    engagement_id text NOT NULL REFERENCES engagements(engagement_id) ON DELETE CASCADE,
    decision_id text NOT NULL,
    record jsonb NOT NULL,
    version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE agent_runs (
    run_id text PRIMARY KEY,
    tenant_id text NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    engagement_id text NOT NULL REFERENCES engagements(engagement_id) ON DELETE CASCADE,
    agent_id text NOT NULL,
    agent_version text NOT NULL,
    context_reference text NOT NULL,
    output_reference text,
    status text NOT NULL,
    budget jsonb NOT NULL,
    usage_record jsonb,
    correlation_id text NOT NULL,
    started_at timestamptz NOT NULL,
    completed_at timestamptz
);

CREATE TABLE quality_reviews (
    review_id text PRIMARY KEY,
    tenant_id text NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    engagement_id text NOT NULL REFERENCES engagements(engagement_id) ON DELETE CASCADE,
    artefact_reference text NOT NULL,
    assurance_tier text NOT NULL CHECK (assurance_tier IN ('T0', 'T1', 'T2', 'T3')),
    reviewer_id text NOT NULL REFERENCES actors(actor_id),
    creator_id text NOT NULL REFERENCES actors(actor_id),
    review jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE defects (
    defect_id text PRIMARY KEY,
    tenant_id text NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    engagement_id text NOT NULL REFERENCES engagements(engagement_id) ON DELETE CASCADE,
    review_id text REFERENCES quality_reviews(review_id) ON DELETE SET NULL,
    severity text NOT NULL CHECK (severity IN ('S1', 'S2', 'S3', 'S4')),
    status text NOT NULL DEFAULT 'open',
    defect jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    closed_at timestamptz
);

CREATE TABLE story_models (
    story_model_id text NOT NULL,
    version text NOT NULL,
    tenant_id text NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    engagement_id text NOT NULL REFERENCES engagements(engagement_id) ON DELETE CASCADE,
    decision_id text NOT NULL,
    record jsonb NOT NULL,
    checksum_sha256 char(64) NOT NULL,
    approval_status text NOT NULL DEFAULT 'draft',
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (story_model_id, version)
);

CREATE TABLE deliverable_manifests (
    file_id text PRIMARY KEY,
    tenant_id text NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    engagement_id text NOT NULL REFERENCES engagements(engagement_id) ON DELETE CASCADE,
    filename text NOT NULL,
    surface text NOT NULL,
    version text NOT NULL,
    approval_status text NOT NULL,
    baseline_story_model_id text NOT NULL,
    baseline_story_model_version text NOT NULL,
    manifest jsonb NOT NULL,
    artefact_checksum char(64),
    object_reference text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (baseline_story_model_id, baseline_story_model_version)
        REFERENCES story_models(story_model_id, version)
);

CREATE TABLE audit_events (
    audit_event_id text PRIMARY KEY,
    tenant_id text NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    engagement_id text REFERENCES engagements(engagement_id) ON DELETE CASCADE,
    occurred_at timestamptz NOT NULL,
    actor_id text REFERENCES actors(actor_id),
    action text NOT NULL,
    object_type text NOT NULL,
    object_id text NOT NULL,
    correlation_id text NOT NULL,
    details jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX engagement_status_idx
    ON engagements (tenant_id, status, lifecycle_stage, operational_state);
CREATE INDEX approvals_pending_idx
    ON approval_requests (tenant_id, engagement_id, status, latest_responsible_date);
CREATE INDEX audit_events_object_idx
    ON audit_events (tenant_id, object_type, object_id, occurred_at);

-- Application roles must set SET LOCAL offdata.tenant_id before accessing tenant data.
ALTER TABLE actors ENABLE ROW LEVEL SECURITY;
ALTER TABLE organisations ENABLE ROW LEVEL SECURITY;
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE engagements ENABLE ROW LEVEL SECURITY;
ALTER TABLE commands ENABLE ROW LEVEL SECURITY;
ALTER TABLE domain_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE idempotency_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE source_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE source_passages ENABLE ROW LEVEL SECURITY;
ALTER TABLE method_selections ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE quality_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE defects ENABLE ROW LEVEL SECURITY;
ALTER TABLE story_models ENABLE ROW LEVEL SECURITY;
ALTER TABLE deliverable_manifests ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY actors_tenant_isolation ON actors
    USING (tenant_id IS NULL OR tenant_id = offdata_current_tenant());
CREATE POLICY organisations_tenant_isolation ON organisations
    USING (tenant_id = offdata_current_tenant());
CREATE POLICY contacts_tenant_isolation ON contacts
    USING (tenant_id = offdata_current_tenant());
CREATE POLICY opportunities_tenant_isolation ON opportunities
    USING (tenant_id = offdata_current_tenant());
CREATE POLICY engagements_tenant_isolation ON engagements
    USING (tenant_id = offdata_current_tenant());
CREATE POLICY commands_tenant_isolation ON commands
    USING (tenant_id = offdata_current_tenant());
CREATE POLICY domain_events_tenant_isolation ON domain_events
    USING (tenant_id = offdata_current_tenant());
CREATE POLICY idempotency_tenant_isolation ON idempotency_records
    USING (tenant_id = offdata_current_tenant());
CREATE POLICY approval_requests_tenant_isolation ON approval_requests
    USING (tenant_id = offdata_current_tenant());
CREATE POLICY approval_records_tenant_isolation ON approval_records
    USING (tenant_id = offdata_current_tenant());
CREATE POLICY source_documents_tenant_isolation ON source_documents
    USING (tenant_id IS NULL OR tenant_id = offdata_current_tenant());
CREATE POLICY source_passages_tenant_isolation ON source_passages
    USING (tenant_id IS NULL OR tenant_id = offdata_current_tenant());
CREATE POLICY method_selections_tenant_isolation ON method_selections
    USING (tenant_id = offdata_current_tenant());
CREATE POLICY agent_runs_tenant_isolation ON agent_runs
    USING (tenant_id = offdata_current_tenant());
CREATE POLICY quality_reviews_tenant_isolation ON quality_reviews
    USING (tenant_id = offdata_current_tenant());
CREATE POLICY defects_tenant_isolation ON defects
    USING (tenant_id = offdata_current_tenant());
CREATE POLICY story_models_tenant_isolation ON story_models
    USING (tenant_id = offdata_current_tenant());
CREATE POLICY deliverables_tenant_isolation ON deliverable_manifests
    USING (tenant_id = offdata_current_tenant());
CREATE POLICY audit_events_tenant_isolation ON audit_events
    USING (tenant_id = offdata_current_tenant());

COMMIT;
