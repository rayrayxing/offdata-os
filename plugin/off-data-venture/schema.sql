-- off/data venture Venture Brain baseline. PostgreSQL.
-- Bootstrap must install through versioned migrations; this file is the target schema reference.

CREATE TYPE od_environment AS ENUM ('TEST','SIMULATION','LIVE');
CREATE TYPE od_record_state AS ENUM ('CURRENT','STALE','SUPERSEDED','HISTORICAL');
CREATE TYPE od_claim_class AS ENUM ('OBSERVED','INFERRED','HYPOTHESIS');
CREATE TYPE od_evidence_purpose AS ENUM ('MARKET_RESEARCH','BEHAVIORAL_VALIDATION','DIRECT_BUYER','FINANCIAL','OPERATING');
CREATE TYPE od_admissibility AS ENUM ('ADMISSIBLE','INADMISSIBLE','QUARANTINED','PROVISIONAL');
CREATE TYPE od_concern_severity AS ENUM ('BLOCKING','MATERIAL_EXPERIMENT','DESIGN_CONSTRAINT','MONITOR');
CREATE TYPE od_concern_status AS ENUM ('OPEN','RESOLVED','ACCEPTED_RISK','INVALIDATED','SUPERSEDED');

CREATE TABLE portfolios (
 id uuid PRIMARY KEY, name text NOT NULL, environment od_environment NOT NULL,
 owner_policy jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE ventures (
 id uuid PRIMARY KEY, portfolio_id uuid NOT NULL REFERENCES portfolios(id), slug text NOT NULL, name text NOT NULL,
 environment od_environment NOT NULL, is_provisional boolean NOT NULL DEFAULT true, phase text NOT NULL,
 kill_switch boolean NOT NULL DEFAULT false, current_version integer NOT NULL DEFAULT 1,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE(portfolio_id,slug));

CREATE TABLE signals (
 id uuid PRIMARY KEY, venture_id uuid REFERENCES ventures(id), source_type text NOT NULL, source_ref text,
 occurred_at timestamptz, retrieved_at timestamptz NOT NULL DEFAULT now(), payload_hash text NOT NULL,
 environment od_environment NOT NULL, created_by text NOT NULL);

CREATE TABLE venture_theses (
 id uuid PRIMARY KEY, venture_id uuid NOT NULL REFERENCES ventures(id), revision int NOT NULL,
 thesis jsonb NOT NULL, input_fingerprint text NOT NULL, state od_record_state NOT NULL DEFAULT 'CURRENT',
 created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(venture_id, revision));

CREATE TABLE research_artifacts (
 id uuid PRIMARY KEY, venture_id uuid NOT NULL REFERENCES ventures(id), source_url text, source_type text NOT NULL,
 provider text NOT NULL, query_hash text, source_occurred_at timestamptz, retrieved_at timestamptz NOT NULL DEFAULT now(),
 author_identity text, raw_artifact_ref text, raw_hash text NOT NULL, role text NOT NULL CHECK(role IN ('SUPPORTING','CONTRARY','NEUTRAL')),
 confidence numeric(5,4), receipt_id uuid, environment od_environment NOT NULL, is_provisional boolean NOT NULL DEFAULT false);

CREATE TABLE claims (
 id uuid PRIMARY KEY, venture_id uuid NOT NULL REFERENCES ventures(id), revision int NOT NULL DEFAULT 1,
 statement text NOT NULL, claim_class od_claim_class NOT NULL, confidence numeric(5,4), disclosure_policy jsonb NOT NULL DEFAULT '{}'::jsonb,
 state od_record_state NOT NULL DEFAULT 'CURRENT', created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE evidence_artifacts (
 id uuid PRIMARY KEY, venture_id uuid NOT NULL REFERENCES ventures(id), purpose od_evidence_purpose NOT NULL,
 admissibility od_admissibility NOT NULL, inadmissible_reason text,
 account_identity text, actor_identity text, counterparty_role text, interaction_type text,
 occurred_at timestamptz, channel text, receipt_ref text, source_ref text, content_hash text NOT NULL,
 environment od_environment NOT NULL, is_provisional boolean NOT NULL DEFAULT false, is_contrary boolean NOT NULL DEFAULT false,
 created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE concerns (
 id uuid PRIMARY KEY, venture_id uuid NOT NULL REFERENCES ventures(id), description text NOT NULL,
 severity od_concern_severity NOT NULL, status od_concern_status NOT NULL DEFAULT 'OPEN', confidence numeric(5,4),
 owner_profile text, source_refs jsonb NOT NULL DEFAULT '[]'::jsonb, mitigation text, experiment_id uuid, review_at timestamptz,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE business_concepts (
 id uuid PRIMARY KEY, venture_id uuid NOT NULL REFERENCES ventures(id), revision int NOT NULL,
 concept jsonb NOT NULL, input_fingerprint text NOT NULL, state od_record_state NOT NULL DEFAULT 'CURRENT',
 created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(venture_id,revision));

CREATE TABLE experiments (
 id uuid PRIMARY KEY, venture_id uuid NOT NULL REFERENCES ventures(id), revision int NOT NULL DEFAULT 1,
 principal_uncertainty text NOT NULL, hypothesis text NOT NULL, experiment_type text NOT NULL, contract jsonb NOT NULL,
 state text NOT NULL, operation_id text NOT NULL UNIQUE, created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE prototypes (
 id uuid PRIMARY KEY, venture_id uuid NOT NULL REFERENCES ventures(id), experiment_id uuid REFERENCES experiments(id),
 revision int NOT NULL, artifact_ref text NOT NULL, artifact_hash text NOT NULL, is_simulation boolean NOT NULL DEFAULT true,
 isolation_verified boolean NOT NULL DEFAULT false, limitations jsonb NOT NULL DEFAULT '[]'::jsonb,
 state od_record_state NOT NULL DEFAULT 'CURRENT', operation_id text NOT NULL UNIQUE, created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE contacts (
 id uuid PRIMARY KEY, venture_id uuid NOT NULL REFERENCES ventures(id), account_identity text, person_identity text, email text,
 opt_out boolean NOT NULL DEFAULT false, last_contact_at timestamptz, next_allowed_contact_at timestamptz,
 relationship_state text, metadata jsonb NOT NULL DEFAULT '{}'::jsonb);

CREATE TABLE interactions (
 id uuid PRIMARY KEY, venture_id uuid NOT NULL REFERENCES ventures(id), contact_id uuid REFERENCES contacts(id),
 interaction_type text NOT NULL, channel text NOT NULL, occurred_at timestamptz NOT NULL, receipt_ref text,
 summary text, raw_ref text, operation_id text UNIQUE, created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE gate_snapshots (
 id uuid PRIMARY KEY, venture_id uuid NOT NULL REFERENCES ventures(id), gate text NOT NULL, policy_version text NOT NULL,
 predecessor_snapshot_id uuid REFERENCES gate_snapshots(id), input_fingerprint text NOT NULL, contributing_evidence jsonb NOT NULL,
 financial_snapshot_id uuid, result text NOT NULL CHECK(result IN ('PASS','FAIL','NOT_YET_PROVEN')),
 state od_record_state NOT NULL DEFAULT 'CURRENT', environment od_environment NOT NULL,
 operation_id text NOT NULL UNIQUE, created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE decisions (
 id uuid PRIMARY KEY, venture_id uuid NOT NULL REFERENCES ventures(id), decision_type text NOT NULL, question text NOT NULL,
 alternatives jsonb NOT NULL, selected jsonb NOT NULL, evidence_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
 contrary_refs jsonb NOT NULL DEFAULT '[]'::jsonb, concerns jsonb NOT NULL DEFAULT '[]'::jsonb,
 assumptions jsonb NOT NULL DEFAULT '[]'::jsonb, expected_value jsonb, confidence numeric(5,4), actor_profile text NOT NULL,
 gate_snapshot_id uuid REFERENCES gate_snapshots(id), operation_id text NOT NULL UNIQUE, created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE forecasts (
 id uuid PRIMARY KEY, venture_id uuid NOT NULL REFERENCES ventures(id), decision_id uuid REFERENCES decisions(id), actor_profile text NOT NULL,
 model_provider text, model_name text, outcome_definition text NOT NULL, probability numeric(5,4) NOT NULL CHECK(probability BETWEEN 0 AND 1),
 resolve_after timestamptz, realized boolean, score numeric, created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE journal_entries (
 id uuid PRIMARY KEY, venture_id uuid NOT NULL REFERENCES ventures(id), entry_date date NOT NULL, currency text NOT NULL,
 description text NOT NULL, lines jsonb NOT NULL, source_receipt_id uuid, environment od_environment NOT NULL,
 operation_id text NOT NULL UNIQUE, created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE financial_snapshots (
 id uuid PRIMARY KEY, venture_id uuid NOT NULL REFERENCES ventures(id), period_start date NOT NULL, period_end date NOT NULL,
 snapshot jsonb NOT NULL, input_fingerprint text NOT NULL, closed_at timestamptz NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(venture_id,period_start,period_end,input_fingerprint));

CREATE TABLE capital_authorizations (
 id uuid PRIMARY KEY, venture_id uuid NOT NULL REFERENCES ventures(id), purpose text NOT NULL, currency text NOT NULL,
 amount numeric(18,4) NOT NULL CHECK(amount>=0), spent numeric(18,4) NOT NULL DEFAULT 0 CHECK(spent>=0), action_classes jsonb NOT NULL,
 authorized_by text NOT NULL, gate_snapshot_id uuid REFERENCES gate_snapshots(id), valid_from timestamptz NOT NULL, expires_at timestamptz,
 revoked_at timestamptz, operation_id text NOT NULL UNIQUE, created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE authority_grants (
 id uuid PRIMARY KEY, profile_name text NOT NULL, venture_id uuid REFERENCES ventures(id), action_class text NOT NULL,
 tool_scope jsonb NOT NULL, target_scope jsonb NOT NULL, environment od_environment NOT NULL, valid_from timestamptz NOT NULL,
 expires_at timestamptz, revoked_at timestamptz, created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE action_receipts (
 id uuid PRIMARY KEY, venture_id uuid REFERENCES ventures(id), operation_id text NOT NULL UNIQUE, provider text NOT NULL,
 action_class text NOT NULL, request_hash text NOT NULL, response_hash text, provider_request_id text, status text NOT NULL,
 retry_count int NOT NULL DEFAULT 0, cost jsonb, latency_ms int, correlation_id text NOT NULL,
 environment od_environment NOT NULL, created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE audit_events (
 id uuid PRIMARY KEY, venture_id uuid REFERENCES ventures(id), operation_id text NOT NULL, correlation_id text NOT NULL,
 actor_profile text NOT NULL, action text NOT NULL, before_fingerprint text, after_fingerprint text,
 input_refs jsonb NOT NULL DEFAULT '[]'::jsonb, policy_version text, environment od_environment NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE skill_certifications (
 id uuid PRIMARY KEY, skill_name text NOT NULL, version text NOT NULL,
 state text NOT NULL CHECK(state IN ('DRAFT','TESTED','CERTIFIED','ACTIVE','DEPRECATED')), owner_profile text NOT NULL,
 tests jsonb NOT NULL DEFAULT '[]'::jsonb, known_failure_modes jsonb NOT NULL DEFAULT '[]'::jsonb, source_ref text, verified_at timestamptz,
 UNIQUE(skill_name,version));

CREATE TABLE learning_candidates (
 id uuid PRIMARY KEY, venture_id uuid REFERENCES ventures(id), learning_type text NOT NULL CHECK(learning_type IN ('FACT','PRIOR','PROCEDURE','POLICY_PROPOSAL')),
 content jsonb NOT NULL, evidence_refs jsonb NOT NULL DEFAULT '[]'::jsonb, status text NOT NULL, created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE aars (
 id uuid PRIMARY KEY, venture_id uuid REFERENCES ventures(id), aar_type text NOT NULL, payload jsonb NOT NULL,
 telegram_receipt_ref text, operation_id text NOT NULL UNIQUE, created_at timestamptz NOT NULL DEFAULT now());
