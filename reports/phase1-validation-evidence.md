# Phase 1 independent validation evidence

## Status

**PASS** — all mandatory Phase 1 GitHub Actions gates completed successfully against the exact final `main` state.

Date: 2026-08-04

Validation mechanism: temporary draft pull request against `main`; no validation-only file was merged.

## GitHub Actions evidence

- Workflow: `Machine contracts`
- Run ID: `30906975338`
- Job ID: `91984219718`
- Runner: Ubuntu 24.04
- Python: 3.11.15
- Result: success
- Validated merge reference: `dbc9d0aaf2c3f7e54077a9c32642be7b3e6fc44e`

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
- duration: 1.87 seconds
- total coverage: 92.71 percent
- enforced minimum coverage: 90 percent

### Static controls

- Python source compilation: passed
- Ruff lint baseline: passed — `All checks passed!`
- strict MyPy baseline: passed — no issues in 18 source files
- MyPy suppression for approval-policy evidence comparison: removed
- Ruff per-file exception for CRM imports: removed

### Retained contract artefact

- files: 13
- artefact ID: `8891437367`
- compressed size: 32,171 bytes
- SHA-256: `b4f2fb086b60a29ab50838534ac3f21c74b19463582cdd3129db1542c4efeceb`
- retention: 30 days

The retained bundle contains:

- generated OpenAPI;
- generated JSON Schemas;
- generated model and command/event catalogues;
- generated requirement test registry;
- governed lifecycle, policy and agent configurations;
- PostgreSQL migration baseline.

## Contract-stability checks

The final run also confirmed:

- the typed policy implementation retains the stable public `offdata_core.policy` import path in the model registry;
- all generated schema references resolve;
- every command and domain event is catalogued;
- every executable test has requirement mappings;
- all 123 requirements have implemented or explicitly planned test coverage;
- no validation-only file entered `main`.

## Scope boundary

This evidence establishes the chat-first Phase 1 machine-contract release on an independent Linux CI runner. It does not substitute for the later macOS, PostgreSQL runtime, browser, Office, OAuth, model-provider, CRM, recovery, load or deployment tests explicitly assigned to Codex integration phases.

## Gate conclusion

Phase 1 is closed as **chat-first complete and independently CI-validated**. Later implementation must conform to these contracts or raise an explicit architecture-decision request; it must not silently redefine them.
