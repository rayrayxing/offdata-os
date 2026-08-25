# OFF/DATA VENTURE — Hermes Bootstrap

Version: 0.2

You are setting up **off/data venture**, a Hermes-native autonomous venture company.

## Non-negotiable operating principle

**LLMs think. Specialists argue. Skills teach procedures. Deterministic tools establish truth. Hooks enforce authority. Kanban carries durable work. The Venture Brain is canonical business truth.**

Profile memory is not authoritative venture state.

## Bootstrap sequence

1. Read `README.md`, `AGENTS.md`, `OFFDATA_MANIFEST.json`, every `spec/` and `policies/` file before making changes.
2. Run `python scripts/package_selftest.py` and `python scripts/preflight.py`.
3. Record the exact Hermes version/SHA, host, Python/Node/PostgreSQL versions and current model/provider configuration in `state/SETUP-READINESS.md`.
4. Inspect project Skills and plugin capabilities. Present security/capability findings before trusting/enabling them. Keep Skill writes approval-gated during bootstrap/certification.
5. Create the specialist profiles in `OFFDATA_MANIFEST.json`; use default authority mode `SHADOW`.
6. Locate the **actual current VentureOS source** and execute `policies/GATE_POLICY_IMPORT.md`. If unavailable, record `BLOCKED_SOURCE_REQUIRED`. Never invent missing G0–G10 policy.
7. Ask the owner every question in `policies/OWNER_POLICY_QUESTIONNAIRE.md`. Until answered and explicitly changed, LIVE spend and autonomous SEND remain zero/DRAFT_ONLY.
8. Ask `policies/BUSINESS_IDENTITY_QUESTIONNAIRE.md`. Put credentials in Hermes profile `.env` or an approved secret store, never in this repository or Venture Brain prose.
9. Qualify the primary Gemini/EasyCLIProxyAPI route and DeepSeek API fallback using `scripts/model_gateway_qualification.py`. Controlled autonomy requires a qualified primary and fallback.
10. Install/configure the real `last30days` Hermes Skill. It is research/discovery input only; never direct-buyer authority. Provider failure must be recorded honestly; do not synthesize research.
11. Configure portfolio and venture Kanban boards, PostgreSQL Venture Brain, guardrail hooks, audit, idempotency, Telegram AAR, backups and restore test.
12. Run `certification/CODEX_CERTIFICATION.md` independently. Builder self-attestation is not certification.
13. Finish with `state/SETUP-READINESS.md` showing PASS/BLOCKED/FAIL for every subsystem and explicit authorization states for customer outreach, LIVE spend, autonomous Skill evolution and no-seed venture trial.

## Safe partial setup

If owner/source/credential inputs are missing, continue only components that are safe in TEST/SHADOW. Never claim setup complete while a required external input is missing.