BEGIN;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$ BEGIN CREATE TYPE od_environment AS ENUM ('TEST','SIMULATION','LIVE'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE od_record_state AS ENUM ('CURRENT','STALE','SUPERSEDED','HISTORICAL'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE od_claim_class AS ENUM ('OBSERVED','INFERRED','HYPOTHESIS'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE od_evidence_purpose AS ENUM ('MARKET_RESEARCH','BEHAVIORAL_VALIDATION','DIRECT_BUYER','FINANCIAL','OPERATING'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE od_admissibility AS ENUM ('ADMISSIBLE','INADMISSIBLE','QUARANTINED','PROVISIONAL'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE od_concern_severity AS ENUM ('BLOCKING','MATERIAL_EXPERIMENT','DESIGN_CONSTRAINT','MONITOR'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS od_operations(
 operation_id text PRIMARY KEY, correlation_id text NOT NULL, actor_profile text NOT NULL, action text NOT NULL,
 input_fingerprint text NOT NULL, environment od_environment NOT NULL, status text NOT NULL,
 result_json jsonb, error text, created_at timestamptz NOT NULL DEFAULT now(), completed_at timestamptz);

CREATE TABLE IF NOT EXISTS portfolios(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), name text NOT NULL, environment od_environment NOT NULL DEFAULT 'TEST',
 owner_policy_version text, owner_policy jsonb NOT NULL DEFAULT '{}'::jsonb,
 base_currency text NOT NULL DEFAULT 'SGD', created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS opportunities(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), portfolio_id uuid NOT NULL REFERENCES portfolios(id), slug text NOT NULL,
 name text NOT NULL, stage text NOT NULL DEFAULT 'DISCOVERED', environment od_environment NOT NULL,
 is_provisional boolean NOT NULL DEFAULT true, status text NOT NULL DEFAULT 'ACTIVE', payload jsonb NOT NULL DEFAULT '{}'::jsonb,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE(portfolio_id,slug));

CREATE TABLE IF NOT EXISTS ventures(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), portfolio_id uuid NOT NULL REFERENCES portfolios(id), opportunity_id uuid REFERENCES opportunities(id),
 slug text NOT NULL, name text NOT NULL, environment od_environment NOT NULL, is_provisional boolean NOT NULL DEFAULT true,
 phase text NOT NULL DEFAULT 'DISCOVERED', current_gate text, current_business_concept_revision integer,
 venture_gm text, kill_switch boolean NOT NULL DEFAULT false, status text NOT NULL DEFAULT 'ACTIVE',
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE(portfolio_id,slug));

CREATE TABLE IF NOT EXISTS signals(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), opportunity_id uuid REFERENCES opportunities(id), venture_id uuid REFERENCES ventures(id),
 source_type text NOT NULL, source_ref text, occurred_at timestamptz, retrieved_at timestamptz NOT NULL,
 payload jsonb NOT NULL, payload_hash text NOT NULL, environment od_environment NOT NULL, created_by text NOT NULL,
 operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS venture_theses(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), opportunity_id uuid REFERENCES opportunities(id), venture_id uuid REFERENCES ventures(id),
 revision integer NOT NULL, thesis jsonb NOT NULL, input_fingerprint text NOT NULL, state od_record_state NOT NULL DEFAULT 'CURRENT',
 operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());
CREATE UNIQUE INDEX IF NOT EXISTS ux_thesis_opp_rev ON venture_theses(opportunity_id,revision) WHERE opportunity_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS ux_thesis_venture_rev ON venture_theses(venture_id,revision) WHERE venture_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS capability_catalogue(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), capability_key text NOT NULL UNIQUE, kind text NOT NULL, provider text NOT NULL,
 version text, profiles jsonb NOT NULL DEFAULT '[]'::jsonb, status text NOT NULL, details jsonb NOT NULL DEFAULT '{}'::jsonb,
 tested_at timestamptz, updated_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS capability_readiness(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), opportunity_id uuid REFERENCES opportunities(id), venture_id uuid REFERENCES ventures(id),
 thesis_id uuid REFERENCES venture_theses(id), revision integer NOT NULL DEFAULT 1, required_domains jsonb NOT NULL DEFAULT '[]'::jsonb,
 required_capabilities jsonb NOT NULL DEFAULT '[]'::jsonb, missing_capabilities jsonb NOT NULL DEFAULT '[]'::jsonb,
 readiness text NOT NULL CHECK(readiness IN ('READY','READY_WITH_GAPS','NOT_READY')), details jsonb NOT NULL DEFAULT '{}'::jsonb,
 state od_record_state NOT NULL DEFAULT 'CURRENT', created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS skill_certifications(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), skill_name text NOT NULL, version text NOT NULL,
 state text NOT NULL CHECK(state IN ('DRAFT','TESTED','CERTIFIED','ACTIVE','DEPRECATED')),
 owner_profile text NOT NULL, tests jsonb NOT NULL DEFAULT '[]'::jsonb, known_failure_modes jsonb NOT NULL DEFAULT '[]'::jsonb,
 source_ref text, verified_at timestamptz, created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(skill_name,version));

CREATE TABLE IF NOT EXISTS research_missions(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), objective text NOT NULL,
 questions jsonb NOT NULL, freshness_days integer NOT NULL DEFAULT 30, max_cost_sgd numeric(18,4) NOT NULL DEFAULT 0,
 spent_sgd numeric(18,4) NOT NULL DEFAULT 0, min_source_diversity integer NOT NULL DEFAULT 3, require_contrary boolean NOT NULL DEFAULT true,
 status text NOT NULL DEFAULT 'OPEN', operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS research_queries(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), mission_id uuid NOT NULL REFERENCES research_missions(id), query_hash text NOT NULL,
 normalized_query text NOT NULL, provider text NOT NULL, status text NOT NULL DEFAULT 'PENDING', attempt_count integer NOT NULL DEFAULT 0,
 cost_sgd numeric(18,4) NOT NULL DEFAULT 0, provider_receipt jsonb, result_count integer, last_error text,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), UNIQUE(mission_id,query_hash,provider));

CREATE TABLE IF NOT EXISTS research_artifacts(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), mission_id uuid REFERENCES research_missions(id),
 source_url text, source_type text NOT NULL, provider text NOT NULL, query_hash text, source_occurred_at timestamptz,
 retrieved_at timestamptz NOT NULL, author_identity text, raw_artifact_ref text, raw_hash text NOT NULL,
 role text NOT NULL CHECK(role IN ('SUPPORTING','CONTRARY','NEUTRAL')), extracted_claims jsonb NOT NULL DEFAULT '[]'::jsonb,
 confidence numeric(5,4), receipt jsonb NOT NULL DEFAULT '{}'::jsonb, environment od_environment NOT NULL,
 operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS ix_research_hash ON research_artifacts(venture_id,raw_hash);

CREATE TABLE IF NOT EXISTS claims(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), revision integer NOT NULL DEFAULT 1,
 statement text NOT NULL, claim_class od_claim_class NOT NULL, confidence numeric(5,4), disclosure_policy jsonb NOT NULL DEFAULT '{}'::jsonb,
 supporting_refs jsonb NOT NULL DEFAULT '[]'::jsonb, contrary_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
 state od_record_state NOT NULL DEFAULT 'CURRENT', operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS evidence_artifacts(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), purpose od_evidence_purpose NOT NULL,
 admissibility od_admissibility NOT NULL DEFAULT 'PROVISIONAL', inadmissible_reason text,
 account_identity text, actor_identity text, counterparty_role text, interaction_type text, occurred_at timestamptz,
 channel text, receipt_ref text, source_ref text, content_hash text NOT NULL, payload jsonb NOT NULL DEFAULT '{}'::jsonb,
 environment od_environment NOT NULL, is_provisional boolean NOT NULL DEFAULT true, is_contrary boolean NOT NULL DEFAULT false,
 operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS concerns(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), description text NOT NULL,
 severity od_concern_severity NOT NULL, status text NOT NULL DEFAULT 'OPEN', confidence numeric(5,4), owner_profile text,
 source_refs jsonb NOT NULL DEFAULT '[]'::jsonb, mitigation text, experiment_id uuid, review_at timestamptz,
 operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS business_concepts(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), revision integer NOT NULL,
 concept jsonb NOT NULL, input_fingerprint text NOT NULL, state od_record_state NOT NULL DEFAULT 'CURRENT',
 operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(venture_id,revision));

CREATE TABLE IF NOT EXISTS experiments(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), concept_revision integer,
 principal_uncertainty text NOT NULL, hypothesis text NOT NULL, experiment_type text NOT NULL, target text NOT NULL, method text NOT NULL,
 success_signal text NOT NULL, failure_signal text NOT NULL, stopping_rule text NOT NULL, budget_sgd numeric(18,4) NOT NULL DEFAULT 0,
 deadline timestamptz, evidence_requirement jsonb NOT NULL DEFAULT '{}'::jsonb, analysis_method jsonb NOT NULL DEFAULT '{}'::jsonb,
 status text NOT NULL DEFAULT 'PLANNED', operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());
ALTER TABLE concerns DROP CONSTRAINT IF EXISTS concerns_experiment_id_fkey;
ALTER TABLE concerns ADD CONSTRAINT concerns_experiment_id_fkey FOREIGN KEY (experiment_id) REFERENCES experiments(id);

CREATE TABLE IF NOT EXISTS experiment_observations(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), experiment_id uuid NOT NULL REFERENCES experiments(id), observed_at timestamptz NOT NULL,
 observation jsonb NOT NULL, evidence_id uuid REFERENCES evidence_artifacts(id), operation_id text UNIQUE REFERENCES od_operations(operation_id),
 created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS prototypes(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), experiment_id uuid REFERENCES experiments(id),
 revision integer NOT NULL, artifact_ref text NOT NULL, artifact_hash text NOT NULL, is_simulation boolean NOT NULL DEFAULT true,
 critical_workflow text NOT NULL, isolation_verified boolean NOT NULL DEFAULT false, limitations jsonb NOT NULL DEFAULT '[]'::jsonb,
 state od_record_state NOT NULL DEFAULT 'CURRENT', operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(venture_id,revision));

CREATE TABLE IF NOT EXISTS validation_packages(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), revision integer NOT NULL DEFAULT 1,
 business_concept_id uuid REFERENCES business_concepts(id), prototype_id uuid REFERENCES prototypes(id), package jsonb NOT NULL,
 state od_record_state NOT NULL DEFAULT 'CURRENT', operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS contacts(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), account_identity text,
 person_identity text, email text, opt_out boolean NOT NULL DEFAULT false, opt_out_source text, bounce_state text,
 complaint_state text, last_contact_at timestamptz, next_allowed_contact_at timestamptz, relationship_state text,
 promises jsonb NOT NULL DEFAULT '[]'::jsonb, metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
 operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
CREATE UNIQUE INDEX IF NOT EXISTS ux_contact_venture_email ON contacts(venture_id,lower(email)) WHERE email IS NOT NULL;

CREATE TABLE IF NOT EXISTS interactions(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), contact_id uuid REFERENCES contacts(id),
 interaction_type text NOT NULL, channel text NOT NULL, occurred_at timestamptz NOT NULL, receipt_ref text, summary text, raw_ref text,
 environment od_environment NOT NULL, operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS commercial_offers(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), contact_id uuid REFERENCES contacts(id),
 offer_type text NOT NULL, currency text NOT NULL DEFAULT 'SGD', list_price numeric(18,4), offered_price numeric(18,4), discount_pct numeric(7,4),
 terms jsonb NOT NULL DEFAULT '{}'::jsonb, status text NOT NULL DEFAULT 'DRAFT', expires_at timestamptz,
 operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS customer_commitments(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), contact_id uuid REFERENCES contacts(id),
 offer_id uuid REFERENCES commercial_offers(id), commitment_type text NOT NULL, amount_sgd numeric(18,4), evidence_ref text,
 status text NOT NULL, occurred_at timestamptz NOT NULL, created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS delivery_obligations(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), commitment_id uuid REFERENCES customer_commitments(id),
 obligation text NOT NULL, due_at timestamptz, status text NOT NULL DEFAULT 'OPEN', delivery_receipt_ref text, created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS accounts(
 code text PRIMARY KEY, name text NOT NULL, account_type text NOT NULL CHECK(account_type IN ('ASSET','LIABILITY','EQUITY','REVENUE','EXPENSE')),
 active boolean NOT NULL DEFAULT true);
INSERT INTO accounts(code,name,account_type) VALUES
('1000','Cash','ASSET'),('1100','Accounts Receivable','ASSET'),('2000','Accounts Payable','LIABILITY'),('3000','Owner Capital','EQUITY'),
('4000','Revenue','REVENUE'),('5000','Cost of Revenue','EXPENSE'),('6000','Research & Experiments','EXPENSE'),('6100','Software & Data','EXPENSE'),('6200','Growth & Sales','EXPENSE')
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS journal_entries(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), entry_date date NOT NULL,
 currency text NOT NULL DEFAULT 'SGD', description text NOT NULL, source_receipt_ref text, environment od_environment NOT NULL,
 operation_id text UNIQUE REFERENCES od_operations(operation_id), posted_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS journal_lines(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), entry_id uuid NOT NULL REFERENCES journal_entries(id) ON DELETE RESTRICT,
 account_code text NOT NULL REFERENCES accounts(code), debit numeric(18,4) NOT NULL DEFAULT 0 CHECK(debit>=0),
 credit numeric(18,4) NOT NULL DEFAULT 0 CHECK(credit>=0), memo text, CHECK(NOT (debit>0 AND credit>0)));

CREATE TABLE IF NOT EXISTS financial_periods(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), period_start date NOT NULL,
 period_end date NOT NULL, status text NOT NULL DEFAULT 'OPEN', closed_at timestamptz, UNIQUE(venture_id,period_start,period_end));

CREATE TABLE IF NOT EXISTS financial_snapshots(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), period_start date NOT NULL,
 period_end date NOT NULL, snapshot jsonb NOT NULL, input_fingerprint text NOT NULL, closed_at timestamptz NOT NULL,
 operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS invoices(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), contact_id uuid REFERENCES contacts(id),
 provider text, provider_invoice_id text, currency text NOT NULL DEFAULT 'SGD', amount numeric(18,4) NOT NULL, status text NOT NULL,
 due_at timestamptz, receipt_ref text, operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS payments(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), invoice_id uuid REFERENCES invoices(id),
 provider text NOT NULL, provider_payment_id text NOT NULL, currency text NOT NULL DEFAULT 'SGD', amount numeric(18,4) NOT NULL,
 status text NOT NULL, receipt_ref text, occurred_at timestamptz NOT NULL, environment od_environment NOT NULL,
 operation_id text UNIQUE REFERENCES od_operations(operation_id), UNIQUE(provider,provider_payment_id));

CREATE TABLE IF NOT EXISTS refunds(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), payment_id uuid NOT NULL REFERENCES payments(id),
 provider_refund_id text, amount numeric(18,4) NOT NULL, status text NOT NULL, receipt_ref text,
 operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS capital_requests(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), purpose text NOT NULL,
 amount_sgd numeric(18,4) NOT NULL CHECK(amount_sgd>0), expected_value jsonb NOT NULL DEFAULT '{}'::jsonb,
 gate_snapshot_id uuid, status text NOT NULL DEFAULT 'PENDING', expires_at timestamptz,
 operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS capital_authorizations(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), request_id uuid REFERENCES capital_requests(id), venture_id uuid NOT NULL REFERENCES ventures(id),
 purpose text NOT NULL, amount_sgd numeric(18,4) NOT NULL CHECK(amount_sgd>=0), action_classes jsonb NOT NULL DEFAULT '[]'::jsonb,
 authorized_by text NOT NULL, gate_snapshot_id uuid, valid_from timestamptz NOT NULL DEFAULT now(), expires_at timestamptz,
 revoked_at timestamptz, operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS authority_grants(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), profile_name text NOT NULL, venture_id uuid REFERENCES ventures(id), action_class text NOT NULL,
 tool_scope jsonb NOT NULL, target_scope jsonb NOT NULL, environment od_environment NOT NULL,
 valid_from timestamptz NOT NULL DEFAULT now(), expires_at timestamptz, revoked_at timestamptz, created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS action_authorizations(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), actor_profile text NOT NULL,
 action_class text NOT NULL, tool_scope jsonb NOT NULL, target_scope jsonb NOT NULL, environment od_environment NOT NULL,
 amount_sgd numeric(18,4) NOT NULL DEFAULT 0, reason text NOT NULL, status text NOT NULL DEFAULT 'PENDING',
 valid_from timestamptz, expires_at timestamptz, resolved_by text, resolved_at timestamptz,
 operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS tool_policies(
 tool_name text PRIMARY KEY, action_class text NOT NULL, effect_class text NOT NULL CHECK(effect_class IN ('READ','WRITE','MONEY','DEPLOY','CONTACT','DESTRUCTIVE')),
 default_requires_authorization boolean NOT NULL DEFAULT true, enabled boolean NOT NULL DEFAULT true, metadata jsonb NOT NULL DEFAULT '{}'::jsonb);

CREATE TABLE IF NOT EXISTS policy_registry(
 policy_type text NOT NULL, version text NOT NULL, policy jsonb NOT NULL, policy_hash text NOT NULL,
 status text NOT NULL CHECK(status IN ('DRAFT','RATIFIED','ACTIVE','SUPERSEDED')), ratified_by text, activated_at timestamptz,
 PRIMARY KEY(policy_type,version));

CREATE TABLE IF NOT EXISTS gate_snapshots(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), gate text NOT NULL,
 policy_version text NOT NULL, predecessor_snapshot_id uuid REFERENCES gate_snapshots(id), input_fingerprint text NOT NULL,
 financial_snapshot_id uuid REFERENCES financial_snapshots(id), result text NOT NULL CHECK(result IN ('PASS','FAIL','NOT_YET_PROVEN')),
 state od_record_state NOT NULL DEFAULT 'CURRENT', environment od_environment NOT NULL,
 operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());
ALTER TABLE capital_requests DROP CONSTRAINT IF EXISTS capital_requests_gate_snapshot_id_fkey;
ALTER TABLE capital_requests ADD CONSTRAINT capital_requests_gate_snapshot_id_fkey FOREIGN KEY(gate_snapshot_id) REFERENCES gate_snapshots(id);
ALTER TABLE capital_authorizations DROP CONSTRAINT IF EXISTS capital_authorizations_gate_snapshot_id_fkey;
ALTER TABLE capital_authorizations ADD CONSTRAINT capital_authorizations_gate_snapshot_id_fkey FOREIGN KEY(gate_snapshot_id) REFERENCES gate_snapshots(id);

CREATE TABLE IF NOT EXISTS gate_snapshot_evidence(
 gate_snapshot_id uuid NOT NULL REFERENCES gate_snapshots(id) ON DELETE CASCADE,
 evidence_id uuid NOT NULL REFERENCES evidence_artifacts(id), evidence_fingerprint text NOT NULL,
 PRIMARY KEY(gate_snapshot_id,evidence_id));

CREATE TABLE IF NOT EXISTS decisions(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), decision_type text NOT NULL,
 question text NOT NULL, alternatives jsonb NOT NULL, selected jsonb NOT NULL, evidence_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
 contrary_refs jsonb NOT NULL DEFAULT '[]'::jsonb, concerns jsonb NOT NULL DEFAULT '[]'::jsonb,
 assumptions jsonb NOT NULL DEFAULT '[]'::jsonb, expected_value jsonb, confidence numeric(5,4), actor_profile text NOT NULL,
 gate_snapshot_id uuid REFERENCES gate_snapshots(id), operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS forecasts(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid REFERENCES ventures(id), decision_id uuid REFERENCES decisions(id),
 actor_profile text NOT NULL, model_provider text, model_name text, outcome_definition text NOT NULL,
 probability numeric(5,4) NOT NULL CHECK(probability>=0 AND probability<=1), resolve_after timestamptz,
 realized boolean, score numeric, created_at timestamptz NOT NULL DEFAULT now(), resolved_at timestamptz);

CREATE TABLE IF NOT EXISTS resource_allocations(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid NOT NULL REFERENCES ventures(id), resource_type text NOT NULL,
 quantity numeric(18,4) NOT NULL, unit text NOT NULL, valid_from timestamptz NOT NULL DEFAULT now(), expires_at timestamptz,
 status text NOT NULL DEFAULT 'ACTIVE', operation_id text UNIQUE REFERENCES od_operations(operation_id));

CREATE TABLE IF NOT EXISTS learning_candidates(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid REFERENCES ventures(id), learning_type text NOT NULL CHECK(learning_type IN ('FACT','PRIOR','PROCEDURE','POLICY_PROPOSAL')),
 content jsonb NOT NULL, evidence_refs jsonb NOT NULL DEFAULT '[]'::jsonb, status text NOT NULL DEFAULT 'CANDIDATE',
 operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS model_evaluations(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), role text NOT NULL, task_class text NOT NULL, provider text NOT NULL, model text NOT NULL,
 latency_ms integer, cost_sgd numeric(18,6), schema_valid boolean, reviewer_score numeric(7,4), downstream_outcome jsonb,
 created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS aars(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid REFERENCES ventures(id), aar_type text NOT NULL, payload jsonb NOT NULL,
 telegram_receipt_ref text, operation_id text UNIQUE REFERENCES od_operations(operation_id), created_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS audit_events(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid REFERENCES ventures(id), operation_id text NOT NULL, correlation_id text NOT NULL,
 actor_profile text NOT NULL, action text NOT NULL, before_fingerprint text, after_fingerprint text, input_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
 policy_version text, environment od_environment NOT NULL, metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
 created_at timestamptz NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS ix_audit_venture_time ON audit_events(venture_id,created_at DESC);
CREATE INDEX IF NOT EXISTS ix_evidence_venture_purpose ON evidence_artifacts(venture_id,purpose,admissibility);
CREATE INDEX IF NOT EXISTS ix_gate_venture_gate ON gate_snapshots(venture_id,gate,created_at DESC);

CREATE OR REPLACE FUNCTION od_stale_gates_on_evidence_change() RETURNS trigger AS $$
BEGIN
 IF OLD.admissibility IS DISTINCT FROM NEW.admissibility OR OLD.content_hash IS DISTINCT FROM NEW.content_hash OR OLD.is_provisional IS DISTINCT FROM NEW.is_provisional THEN
   UPDATE gate_snapshots gs SET state='STALE'
   WHERE gs.id IN (SELECT gate_snapshot_id FROM gate_snapshot_evidence WHERE evidence_id=NEW.id)
     AND gs.state='CURRENT';
 END IF;
 RETURN NEW;
END; $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_od_evidence_stale_gates ON evidence_artifacts;
CREATE TRIGGER trg_od_evidence_stale_gates AFTER UPDATE ON evidence_artifacts FOR EACH ROW EXECUTE FUNCTION od_stale_gates_on_evidence_change();

CREATE OR REPLACE FUNCTION od_validate_balanced_entry() RETURNS trigger AS $$
DECLARE d numeric; c numeric;
BEGIN
 SELECT COALESCE(sum(debit),0),COALESCE(sum(credit),0) INTO d,c FROM journal_lines WHERE entry_id=NEW.entry_id;
 IF d <> c THEN RAISE EXCEPTION 'UNBALANCED_JOURNAL_ENTRY % debit=% credit=%',NEW.entry_id,d,c; END IF;
 RETURN NULL;
END; $$ LANGUAGE plpgsql;
-- Balance is validated explicitly by the handler after all lines are inserted in the same transaction.

CREATE TABLE IF NOT EXISTS schema_migrations(version text PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now());
INSERT INTO schema_migrations(version) VALUES('001_offdata_v02_final') ON CONFLICT DO NOTHING;
COMMIT;
