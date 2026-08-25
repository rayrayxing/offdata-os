# off-data-venture plugin

Deterministic domain plugin for canonical venture state/policy. `tools.py` contains model-free primitives; `schema.sql` is target schema reference. Bootstrap must turn schema into versioned migrations and validate plugin API/capabilities against the exact pinned Hermes release.

Authoritative tool families to implement fully: venture-state, venture-research, venture-decisions, venture-experiments, venture-contacts, venture-finance, venture-authority, venture-learning. All authoritative DB mutations must be transactional with AuditEvent and idempotency.