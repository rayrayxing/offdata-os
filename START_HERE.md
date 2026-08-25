# OFF/DATA VENTURE — Hermes Operational Setup v0.2 FINAL

You are configuring **OFF/DATA VENTURE**, a Hermes-native autonomous venture company. The package contains executable Venture Brain, Gate/authority/finance primitives, specialist manifests, task Skills, workflow hooks, controlled customer/payment rails, cron routines, dashboard, Mac operations and tests.

## Operating principle
**LLMs think. Specialists argue. Skills teach procedures. Deterministic tools establish truth. Hooks enforce authority. Kanban carries durable work. Venture Brain is canonical business truth.**

## Setup sequence
1. Read `AGENTS.md`, `OFFDATA_MANIFEST.json`, `spec/`, `policies/`, `manifests/` and `certification/CODEX_CERTIFICATION.md`.
2. Run `python3 scripts/package_selftest.py`, then `python3 scripts/preflight.py`.
3. Put local secrets/identity in a local `.env`; never commit them. Load the owner payload supplied with the private distribution.
4. Set `OFFDATA_DATABASE_URL`; run `python3 scripts/offdata_setup.py deps`, `plugin`, then `migrate`.
5. Locate the actual on-device VentureOS checkout in `VENTUREOS_PATH`. Run `python3 scripts/import_ventureos_audits.py "$VENTUREOS_PATH" --strict`. Extract the exact G0-G10 policy per `policies/GATE_POLICY_IMPORT.md`; compile with `scripts/compile_gate_policy.py`. Never invent a missing gate.
6. Qualify Gemini/EasyCLIProxyAPI and DeepSeek fallback using `scripts/model_gateway_qualification.py` before unattended inference.
7. Run `python3 scripts/reconcile_profiles.py` and `python3 scripts/materialize_skills.py`. Install/verify real `last30days`; it is research only, never direct-buyer authority.
8. Run `python3 scripts/inventory_capabilities.py`. Capability Architect/Steward must consult this catalogue before creating new Skills/tools.
9. Configure Telegram gateway with the single owner control bot, Google Workspace sender, Stripe TEST, and other integration credentials as available. Customer SEND must use `offdata_email_send`; Stripe effects must use OFF/DATA Stripe tools. Terminal bypass attempts are blocked.
10. Run `python3 scripts/reconcile_cron.py`. Scans and routine operations are cron-driven; venture progression itself is hook/Kanban driven.
11. Run `hermes gateway install` (or the current Hermes-recommended macOS user service) and verify `hermes cron status`.
12. Run `python3 scripts/capture_dependency_lock.py`, `python3 tests/run_all.py`, `python3 scripts/validate_package.py`, `python3 scripts/generate_checksums.py`.
13. Run backup and restore rehearsal using `ops/macos/backup.sh` and `ops/macos/restore.sh` against a disposable restore database.
14. Run independent Codex certification. Do not weaken its failures. Only after certification should SHADOW progress to CONTROLLED/LIVE authority according to the owner policy.
15. Finish `state/SETUP-READINESS.md` with PASS/BLOCKED/FAIL for Gate Policy, model routes, profiles, Skills, capability catalogue, research, customer interaction, Stripe TEST/LIVE readiness, finance, Telegram, cron, backup/restore, dashboard and independent certification.

## Safe failure rule
If a required source, credential, legal identity, provider or policy input is missing, continue safe TEST/SHADOW work but record `BLOCKED:<exact reason>`. Never turn missing external reality into synthetic PASS.
