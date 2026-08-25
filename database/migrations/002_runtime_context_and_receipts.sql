BEGIN;
CREATE TABLE IF NOT EXISTS kanban_task_contexts(
 task_id text PRIMARY KEY, board text, venture_id uuid REFERENCES ventures(id), opportunity_id uuid REFERENCES opportunities(id),
 stage text NOT NULL, environment od_environment NOT NULL, operation_prefix text NOT NULL, authority_scope jsonb NOT NULL DEFAULT '{}'::jsonb,
 metadata jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS action_receipts(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), venture_id uuid REFERENCES ventures(id), operation_id text NOT NULL,
 tool_name text NOT NULL, action_class text, provider text, request_hash text NOT NULL, response_hash text,
 provider_request_id text, status text NOT NULL, retry_count integer NOT NULL DEFAULT 0, amount_sgd numeric(18,4) NOT NULL DEFAULT 0,
 latency_ms integer, correlation_id text, environment od_environment NOT NULL, task_id text,
 created_at timestamptz NOT NULL DEFAULT now());
CREATE UNIQUE INDEX IF NOT EXISTS ux_action_receipt_effect ON action_receipts(operation_id,tool_name,request_hash);

CREATE TABLE IF NOT EXISTS bootstrap_state(
 key text PRIMARY KEY, status text NOT NULL, value jsonb NOT NULL DEFAULT '{}'::jsonb, updated_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS integration_registry(
 integration_key text PRIMARY KEY, kind text NOT NULL, provider text NOT NULL, status text NOT NULL,
 profiles jsonb NOT NULL DEFAULT '[]'::jsonb, required_env jsonb NOT NULL DEFAULT '[]'::jsonb,
 tool_names jsonb NOT NULL DEFAULT '[]'::jsonb, details jsonb NOT NULL DEFAULT '{}'::jsonb, tested_at timestamptz,
 updated_at timestamptz NOT NULL DEFAULT now());

INSERT INTO schema_migrations(version) VALUES('002_runtime_context_and_receipts') ON CONFLICT DO NOTHING;
COMMIT;
