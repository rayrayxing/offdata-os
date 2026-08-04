# 33 — Phase 1 Machine-Contract Completion Report

## Status

**Chat-first Phase 1: complete.**

This release converts the existing offdata methodology, lifecycle, authority, quality, delivery and CRM logic into implementation-ready machine contracts. It does not claim that the contracts have yet been integrated into the Founder’s macOS environment or applied to a real PostgreSQL database.

Date: 2026-08-04

## 1. Completed contract surfaces

### 1.1 Canonical typed model registry

The registry generates portable JSON Schema from the Pydantic runtime contracts and currently covers 58 public model contracts across:

- lifecycle and transition decisions;
- authority and approval policy;
- agent envelopes, context packages and Founder decision packets;
- source, passage, method, archetype and methodology-candidate records;
- command, event and approval records;
- quality, defect, exception and independent-signoff records;
- story, visual, deliverable and reconciliation records;
- organisation, contact, opportunity and outreach records;
- engagement API requests, responses and Founder read models.

Canonical source:

- `packages/offdata-core/src/offdata_core/registry.py`
- `packages/offdata-core/src/offdata_core/api_contracts.py`

### 1.2 Generated contract release

A deterministic exporter materialises eight generated contract files:

1. `schemas/offdata-contract-bundle.schema.json`
2. `schemas/offdata-configs.schema.json`
3. `schemas/agent-envelope.schema.json`
4. `schemas/context-package.schema.json`
5. `schemas/founder-decision-packet.schema.json`
6. `contracts/model-registry.json`
7. `contracts/command-event-catalogue.json`
8. `api/openapi.json`

Run:

```bash
python scripts/build_test_registry.py
python scripts/export_machine_contracts.py
python scripts/validate_phase1_contracts.py
```

The JSON outputs are deterministic build artefacts. GitHub Actions retains them as a workflow artefact after each contract validation run.

### 1.3 Governed runtime configuration

The repository now contains machine-readable configurations for:

- all thirteen lifecycle stages and gates;
- operational states, regression, recovery, retry and kill-switch controls;
- all six decision classes and the strictest-class-governs policy;
- Founder decision-packet requirements;
- eleven bounded specialist-agent roles;
- allowed record families, tool classes and prohibited actions;
- propose-only agent writes and canonical writes through commands.

Files:

- `configs/lifecycle.yaml`
- `configs/policy.yaml`
- `configs/agents.yaml`

### 1.4 OpenAPI 3.1 contract

The OpenAPI builder defines 26 paths, including:

- engagement creation and retrieval;
- command submission, event history and timeline;
- pause, resume and cancellation;
- mandate, decisions, hypotheses, method selections, claims and evidence;
- analyses and recommendations;
- quality findings, approvals and release-gate evaluation;
- deliverables, implementation initiatives and benefits;
- Founder engagement summaries and decision inboxes.

All mutation responses use the command-response contract and may return `pending_approval` instead of executing a reserved action.

### 1.5 Command, event, concurrency and idempotency contracts

The catalogue covers ten commands and fifteen domain events.

Non-create commands require:

- engagement scope;
- an expected aggregate version;
- a correlation identifier;
- an idempotency key where approval, external effect, cancellation, agent-output admission or artefact release may be repeated accidentally.

The PostgreSQL baseline persists commands before effects, records immutable events and stores idempotency results so a retry can return the original outcome without repeating a completed effect.

### 1.6 PostgreSQL persistence baseline

`database/migrations/0001_core.sql` defines the first implementation migration for:

- tenants and actors;
- organisations, contacts and opportunities;
- engagements;
- commands, domain events and idempotency records;
- approval requests and decisions;
- source documents and passages;
- method selections and agent runs;
- quality reviews and defects;
- story models and deliverable manifests;
- audit events;
- tenant-scoped row-level security policies.

The migration is deliberately PostgreSQL-specific. It remains a design baseline until applied and tested against PostgreSQL by Codex.

## 2. Requirement and test traceability

The requirements catalogue contains 123 requirement IDs.

The Phase 1 traceability system now separates:

- **implemented executable tests** — tests that exist in the repository and can produce evidence now;
- **planned tests** — integration, recovery, security, agent, artefact, end-to-end and Founder-acceptance tests that require later capabilities.

The deterministic test-registry generator currently produces:

- 86 implemented test nodes;
- 72 planned tests;
- coverage mapping for all 123 requirements;
- a hard failure when an executable test has no requirement mapping or a mapping points to a deleted test.

Source files:

- `requirements/implemented-test-mappings.json`
- `requirements/planned-test-mappings.json`
- `requirements/traceability.yaml`
- generated `requirements/test-registry.json`

## 3. Validation performed in the chat development environment

### 3.1 Deterministic Python tests

Result:

```text
86 passed
```

The suite covers the existing lifecycle, policy, agent-contract, knowledge, quality, delivery, CRM and synthetic AI-audit fixture tests, plus the new machine-contract tests.

### 3.2 Contract exporter drift check

Result:

```text
8 generated contract files are current.
```

### 3.3 Complete Phase 1 validator

Result:

```text
PHASE 1 CONTRACT VALIDATION PASSED
- generated_contracts=8
- registered_models=58
- validated_configs=4
- openapi_paths=26
- commands=10
- events=15
- catalogue_requirements=123
- implemented_tests=86
- planned_tests=72
```

The migration length reported in the chat environment reflected the more detailed local draft. The committed migration is a shorter implementation baseline with the same required tenant, event, approval, idempotency and row-level-security markers. PostgreSQL execution remains pending.

### 3.4 Additional checks

Completed:

- Python source compilation with `compileall`;
- JSON parsing of generated contract outputs;
- YAML parsing and JSON Schema validation of lifecycle, policy, agent and test-registry configuration;
- Draft 2020-12 JSON Schema self-validation;
- OpenAPI 3.1 path and external-schema-reference resolution;
- command and event enum coverage;
- requirement catalogue coverage;
- editable package installation using the available local package environment.

## 4. Checks deliberately deferred to the integration environment

The following are not represented as completed evidence:

- execution on the Founder’s macOS machine;
- GitHub Actions evidence from the connected repository;
- applying and rolling back the migration on PostgreSQL 16;
- database row-level-security penetration tests;
- official OpenAPI tooling and generated-client compatibility tests;
- browser, Office and artefact rendering;
- OAuth, CRM, model-provider or cloud integration;
- recovery of interrupted durable workflows;
- performance and load testing.

`ruff` and `mypy` were not available in the chat execution environment. The GitHub Actions workflow runs them as an advisory baseline so findings are visible without misrepresenting the existing repository as already type-clean.

## 5. CI contract

`.github/workflows/contracts.yml` performs the following on pushes and pull requests:

1. installs Python 3.11 and the validation dependencies;
2. builds the test registry;
3. generates JSON Schema, OpenAPI and catalogue artefacts;
4. runs the Phase 1 validator;
5. runs the deterministic test suite with coverage;
6. compiles Python sources;
7. runs advisory lint and type checks;
8. retains generated machine contracts as a 30-day workflow artefact.

## 6. Phase gate conclusion

The **chat-first design and deterministic-validation gate for Phase 1 is passed**.

This means Codex should not redesign:

- lifecycle stages;
- decision classes;
- agent write boundaries;
- command and event shapes;
- approval packet structure;
- API semantics;
- persistence semantics;
- requirement and test traceability.

Codex’s later responsibility is to regenerate the artefacts, execute the same tests on macOS and GitHub Actions, apply the migration to PostgreSQL, implement the FastAPI service from the OpenAPI contract and report any integration defect without silently changing the governing contracts.

## 7. Next chat-first phase

The next phase is **Phase 2 — Complete the first agent system**:

- project-local skill packages;
- role-specific system and task prompts;
- input and output contracts;
- context-selection rules;
- tool and record permissions;
- positive, negative and adversarial evaluation cases;
- escalation and budget policies.
