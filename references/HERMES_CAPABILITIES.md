# Hermes Capability Assumptions to Verify at Pin

The package is designed around current documented Hermes surfaces:
- persistent profiles with separate config/credentials/memory/sessions/Skills/state;
- project-local and installable Skills with trust/security scanning and approval-gated writes;
- durable single-host Kanban with idempotency keys, dependencies, attempts/review, crash/stale reclamation and circuit breaking;
- plugins/custom deterministic tools and lifecycle hooks including pre-tool vetoes;
- allowlisted MCP/tool surfaces;
- cron/gateway/Telegram;
- dashboard extensibility;
- external CLI worker-lane contract;
- Codex runtime integration.

Hermes evolves quickly. Bootstrap must validate each surface against the exact pinned release rather than treating current web documentation as proof of a historical release.