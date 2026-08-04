# Phase 1 independent validation evidence

## Status

**PASS** — all mandatory Phase 1 GitHub Actions gates completed successfully.

Date: 2026-08-04

Validation mechanism: temporary draft pull request against `main`; no validation-only file was merged.

## GitHub Actions evidence

- Workflow: `Machine contracts`
- Run ID: `30905935641`
- Job ID: `91980886780`
- Runner: Ubuntu 24.04
- Python: 3.11.15
- Result: success

## Mandatory results

### Contract generation and validation

- generated contract files: 8
- registered Pydantic models: 58
- validated governed configurations: 4
- OpenAPI paths: 26
- command definitions: 10
- event definitions: 15
- catalogue requirements: 123
- implemented executable tests: 86
- planned tests: 72
- PostgreSQL migration lines inspected: 396

### Deterministic tests

- result: 86 passed
- duration: 2.35 seconds
- total coverage: 92.67 percent
- enforced minimum coverage: 90 percent

### Static controls

- Python source compilation: passed
- Ruff lint baseline: passed — `All checks passed!`
- strict MyPy baseline: passed — no issues in 16 source files

### Retained contract artefact

- files: 13
- artefact ID: `8891031568`
- compressed size: 32,171 bytes
- SHA-256: `bcc2bd233370ba60ef7453446e65eb3d98133d23fa9f2615620796fdc9f6fc22`
- retention: 30 days

The retained bundle contains:

- generated OpenAPI;
- generated JSON Schemas;
- generated model and command/event catalogues;
- generated requirement test registry;
- governed lifecycle, policy and agent configurations;
- PostgreSQL migration baseline.

## Scope boundary

This evidence establishes the chat-first Phase 1 machine-contract release on an independent Linux CI runner. It does not substitute for the later macOS, PostgreSQL runtime, browser, Office, OAuth, model-provider, CRM, recovery, load or deployment tests explicitly assigned to Codex integration phases.

## Gate conclusion

Phase 1 is closed as **chat-first complete and independently CI-validated**. Later implementation must conform to these contracts or raise an explicit architecture-decision request; it must not silently redefine them.
