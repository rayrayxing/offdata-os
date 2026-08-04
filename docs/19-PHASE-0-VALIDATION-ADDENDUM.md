# 19 — Phase 0 Validation Addendum

Codex must treat the following files as pre-existing implementation inputs during Phase 0:

- `packages/offdata-core/`
- `config/lifecycle.yaml`
- `config/policy-matrix.yaml`
- `config/agent-roster.yaml`
- `schemas/agent-envelope.schema.json`
- `schemas/context-package.schema.json`
- `schemas/founder-decision-packet.schema.json`
- `fixtures/manifest.yaml`
- `third_party/registry.yaml`

## Required validation

1. Install `packages/offdata-core` in an isolated Python environment.
2. Run its complete test suite.
3. Add formatting, linting, strict type checking and coverage to repository-wide commands.
4. Validate all JSON schemas.
5. Validate all YAML configuration files.
6. Confirm the Python rules and machine-readable configuration do not materially conflict.
7. Add at least one CI test proving an invalid lifecycle transition is blocked.
8. Add at least one CI test proving an unauthorised external action cannot auto-execute.
9. Document any corrections as an architecture or requirements issue rather than silently changing governing intent.

## Current chat-built scope

The committed deterministic package now includes lifecycle, approval policy, typed agent and Founder contracts, knowledge and methodology records, commands and events, quality gates, deliverable reconciliation, CRM and controlled outreach. The repository currently contains 51 unit-test functions across these modules.

Incremental predecessor versions were exercised successfully in the chat development environment. The four latest contract groups were reviewed structurally but have not been executed in the Founder’s macOS environment. The authoritative result is the complete Codex macOS and GitHub Actions run; exact historical test counts in earlier documents are superseded by this addendum.
