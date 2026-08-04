# 33 — Phase 1 Machine-Contract Completion Report

## Status

**Chat-first Phase 1: complete and independently CI-validated.**

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

The approval-policy implementation is fully type checked without a MyPy suppression. The registry preserves the stable public `offdata_core.policy` import path even though typed comparison helpers are maintained in internal modules.

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

The Phase 1 traceability system separates:

- **implemented executable tests** — tests that exist in the repository and produce evidence now;
- **planned tests** — integration, recovery, security, agent, artefact, end-to-end and Founder-acceptance tests that require later capabilities.

The deterministic test-registry generator produces:

- 86 implemented test nodes;
- 72 planned tests;
- coverage mapping for all 123 requirements;
- a hard failure when an executable test has no requirement mapping or a mapping points to a deleted test.

Source files:

- `requirements/implemented-test-mappings.json`
- `requirements/planned-test-mappings.json`
- `requirements/traceability.yaml`
- generated `requirements/test-registry.json`

## 3. Validation evidence

### 3.1 Chat development environment

Completed before independent CI:

- 86 deterministic tests passed;
- eight generated contract artefacts matched their source generators;
- all governed configurations parsed and validated;
- Draft 2020-12 JSON Schema self-validation passed;
- OpenAPI schema references resolved;
- command and event enum coverage passed;
- all 123 requirements had implemented or planned test coverage;
- Python source compilation passed.

### 3.2 Independent GitHub Actions validation

The final exact-main validation run completed successfully on Ubuntu 24.04 with Python 3.11.15.

Results:

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
- migration_lines=396
```

Additional mandatory gates:

- deterministic tests: 86 passed;
- total code coverage: 92.71 percent;
- enforced coverage minimum: 90 percent;
- Python compilation: passed;
- Ruff lint baseline: passed with no per-file exception;
- strict MyPy baseline: passed with no issues across 18 source files and no policy suppression;
- generated contract artefact: retained for 30 days.

The retained artefact contains 13 files, has artefact ID `8891437367`, compressed size 32,171 bytes and SHA-256 digest `b4f2fb086b60a29ab50838534ac3f21c74b19463582cdd3129db1542c4efeceb`.

Full evidence is recorded in `reports/phase1-validation-evidence.md`.

## 4. Checks deliberately deferred to the integration environment

The following are not represented as completed evidence:

- execution on the Founder’s macOS machine;
- applying and rolling back the migration on PostgreSQL 16;
- database row-level-security penetration tests;
- generated-client compatibility tests using selected OpenAPI tooling;
- browser, Office and artefact rendering;
- OAuth, CRM, model-provider or cloud integration;
- recovery of interrupted durable workflows;
- performance and load testing.

These are integration or runtime checks rather than remaining machine-contract design work.

## 5. CI contract

`.github/workflows/contracts.yml` now enforces the following on pushes and pull requests:

1. Python 3.11 and validation dependency installation;
2. deterministic test-registry generation;
3. JSON Schema, OpenAPI and catalogue generation;
4. complete Phase 1 contract validation;
5. deterministic test execution with a 90 percent coverage floor;
6. Python source compilation;
7. mandatory Ruff linting;
8. mandatory strict MyPy checking;
9. 30-day retention of generated machine contracts.

## 6. Phase gate conclusion

The **chat-first design, deterministic validation and independent CI gate for Phase 1 is passed**.

This means Codex should not redesign:

- lifecycle stages;
- decision classes;
- agent write boundaries;
- command and event shapes;
- approval packet structure;
- API semantics;
- persistence semantics;
- requirement and test traceability.

Codex’s later responsibility is to regenerate the artefacts, execute the same tests on macOS, apply the migration to PostgreSQL, implement the FastAPI service from the OpenAPI contract and report any integration defect without silently changing the governing contracts.

## 7. Next chat-first phase

The next phase is **Phase 2 — Complete the first agent system**:

- project-local skill packages;
- role-specific system and task prompts;
- input and output contracts;
- context-selection rules;
- tool and record permissions;
- positive, negative and adversarial evaluation cases;
- escalation and budget policies.
