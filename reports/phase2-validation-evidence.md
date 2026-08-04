# Phase 2 independent validation evidence

## Status

**PASS** — all Phase 1 regression and Phase 2 agent-system gates completed successfully.

Date: 2026-08-04

## GitHub Actions evidence

- workflow: `Machine contracts and agent system`
- run ID: `30910067072`
- job ID: `91994315198`
- validated pull-request merge reference: `5669af541167861a4bedc7094ea2e20c5fd2202a`
- runner: Ubuntu 24.04
- Python: 3.11.15
- conclusion: success

The later completion-report commits change documentation only. They do not alter the executable agent system, governed configurations, tests or workflow validated by this run. The pull-request gate is rerun after those documentation commits before merge.

## Phase 1 regression result

- generated contract files: 8
- registered models: 58
- governed configurations validated: 4
- OpenAPI paths: 26
- commands: 10
- events: 15
- requirements in catalogue: 123
- implemented test nodes after Phase 2: 105
- remaining planned tests: 67
- PostgreSQL migration lines inspected: 396

## Phase 2 result

- bounded agents: 11
- project-local skills: 11
- context profiles: 11
- budget profiles: 6
- provider routes: 3
- evaluation profiles: 11
- evaluation cases: 33
- mandatory admission failures: 8
- completed planned-test IDs: 5

## Complete deterministic quality gate

- runtime tests: 107 passed
- total code coverage: 92.45 percent
- enforced coverage minimum: 90 percent
- Python compilation: passed
- Ruff lint: passed
- strict MyPy: passed across 19 source files

## Retained release artefact

- files: 28
- artefact ID: `8892672584`
- compressed size: 53,019 bytes
- SHA-256: `8652d65cd3967146415842f914b2b18aa7e0439be2339faf0447c9e5c3505633`
- retention: 30 days

The retained release includes generated contracts, requirement traceability, lifecycle/policy/agent/evaluation configuration, all eleven skill packages and the PostgreSQL baseline.

## Scope boundary

This evidence establishes the chat-first design and deterministic validation of the first agent system. It does not establish live-provider model quality, database enforcement, durable workflow recovery, browser or Office execution, connector security, production performance or Founder acceptance of live outputs.

## Gate conclusion

Phase 2 is complete as a provider-independent, bounded and independently CI-validated agent-system release. Runtime integration must conform to these controls or raise an explicit architecture decision.
