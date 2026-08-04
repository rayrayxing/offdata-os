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

The chat development environment exercised 26 unit tests successfully using the package source on an isolated Python path. This is preliminary evidence only; the authoritative result is the Codex macOS and GitHub Actions run.
