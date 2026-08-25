BEGIN;
CREATE TABLE IF NOT EXISTS external_effects(
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), operation_id text NOT NULL UNIQUE, venture_id uuid REFERENCES ventures(id),
 provider text NOT NULL, effect_type text NOT NULL, request_hash text NOT NULL, state text NOT NULL CHECK(state IN ('RESERVED','COMPLETED','UNKNOWN','FAILED')),
 provider_id text, response_json jsonb, error text, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());

INSERT INTO tool_policies(tool_name,action_class,effect_class,default_requires_authorization,enabled,metadata) VALUES
('offdata_email_send','SEND_OUTREACH','EXTERNAL_WRITE',false,true,'{}'::jsonb),
('offdata_stripe_checkout_create','ACCEPT_PAYMENT','EXTERNAL_WRITE',false,true,'{"amount_field":"amount_sgd"}'::jsonb),
('offdata_stripe_invoice_create','CREATE_INVOICE','EXTERNAL_WRITE',false,true,'{"amount_field":"amount_sgd"}'::jsonb),
('offdata_stripe_sync','READ_FINANCE','READ',false,true,'{}'::jsonb),
('offdata_terminal_external_effect','TERMINAL_EXTERNAL_EFFECT','EXTERNAL_WRITE',true,true,'{}'::jsonb)
ON CONFLICT(tool_name) DO UPDATE SET action_class=excluded.action_class,effect_class=excluded.effect_class,default_requires_authorization=excluded.default_requires_authorization,enabled=true,metadata=excluded.metadata;

INSERT INTO schema_migrations(version) VALUES('003_external_effects_and_guard_policies') ON CONFLICT DO NOTHING;
COMMIT;
