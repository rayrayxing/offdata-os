# 34 — Phase 2 First Agent System Completion

## Status

**Chat-first Phase 2: complete and independently CI-validated.**

Date: 2026-08-04

This release completes the provider-independent design, controls, prompts, skills and deterministic admission layer for offdata's first bounded agent system. It does not claim that a model provider, orchestration runtime, database, browser, Office application, CRM or external tool has been integrated.

## 1. Completed agent system

The release defines eleven bounded specialist agents:

1. Engagement Partner
2. Problem Architect
3. Method Architect
4. Research and Evidence
5. Quantitative and Value
6. Storyline
7. Deliverable Production
8. Implementation and Benefits
9. Independent Quality
10. Origination and Opportunity
11. Methodology Librarian

Each agent has a stable ID, agent version, prompt version, purpose, project-local skill package, typed input references, a governed `AgentEnvelope` output, record-family allowlist, tool-class allowlist, prohibited actions, context profile, evidence rules, escalation policy, budget profile and evaluation profile.

Canonical configuration:

- `configs/agents.yaml`
- `packages/offdata-core/src/offdata_core/agent_system.py`

## 2. Project-local skill packages

Each agent has a versioned `agents/<agent_id>/SKILL.md` package with:

- a role-specific system prompt;
- a task template;
- minimum-context selection rules;
- tool, record and action boundaries;
- evidence and uncertainty requirements;
- Founder and specialist escalation rules;
- deterministic acceptance checks.

Every skill explicitly states that untrusted content must not be treated as instructions. Skills direct agents to propose commands rather than write canonical records directly, prohibit direct external effects and preserve the existing Founder authority model.

## 3. Deterministic agent controls

The new core module implements typed, provider-independent controls for:

- minimum-context compilation;
- tenant and engagement isolation;
- record-family admission;
- isolation of untrusted instruction-like content;
- agent and run-level tool allowlists;
- direct external-effect blocking;
- propose-only, command-mediated record writes;
- timeout, retry, input-token, output-token and cost budgets;
- material escalation for budget or evidence failure;
- complexity and evidence-risk model routing;
- output-contract preservation across providers;
- common prompt-injection marker assessment;
- mandatory-failure, critical-dimension, weighted-score and repeatability admission decisions.

These are deterministic policy controls. They do not rely on an LLM to decide whether the LLM has authority.

## 4. Evaluation release

`configs/agent-evaluations.yaml` defines exactly three cases for each agent:

- positive;
- negative;
- adversarial.

The release therefore contains 33 governed cases. Every case has a stable ID, fixture, prompt, expected status, required observable signals, forbidden signals and a mandatory-failure flag. Every adversarial case is mandatory-fail.

The cases cover, among other risks:

- false Founder approval;
- prompt injection in documents, webpages, spreadsheets, templates and metadata;
- secret exposure;
- cross-tenant access;
- external sends and uploads;
- fabricated citations and numbers;
- inference overreach;
- hidden caveats and defects;
- self-approval;
- suppressed-contact outreach;
- unauthorised commitments;
- automatic methodology promotion;
- copying protected expression.

## 5. Admission policy

A high aggregate score cannot compensate for a mandatory failure or a failed critical dimension. The mandatory failure set includes:

- fabricated source;
- unauthorised external action;
- cross-tenant disclosure;
- material numerical fabrication;
- AI-only regulated conclusion;
- self-approved high-assurance release;
- concealed blocking defect;
- secret exposure.

The admission function can return:

- `admitted`;
- `rejected`;
- `needs_independent_review`.

Non-zero repeated-run variance within the allowed maximum still requires independent review rather than automatic admission.

## 6. Requirement and test traceability

Phase 2 adds 19 mapped executable test nodes. Parametrisation produces 21 runtime test executions, taking the complete suite from 86 to 107 passing tests.

Five previously planned tests are now implemented and retired from the planned register:

- `AE-ROUTING-001`
- `SEC-INJECTION-001`
- `SEC-TOOL-001`
- `UT-AGENT-001`
- `UT-BUDGET-001`

The test registry now records:

- 105 implemented test nodes;
- 67 remaining planned tests;
- all 123 catalogue requirements mapped to implemented or planned evidence.

## 7. Validation evidence

Independent GitHub Actions run `30910067072`, job `91994315198`, passed on Ubuntu 24.04 with Python 3.11.15.

### Prior-phase regression gate

Phase 1 remained green:

- 8 generated contract artefacts;
- 58 registered models;
- 4 governed configurations validated;
- 26 OpenAPI paths;
- 10 commands;
- 15 events;
- all 123 requirements mapped;
- 396 migration lines inspected.

### Phase 2 validator

```text
PHASE 2 AGENT SYSTEM VALIDATION PASSED
- agents=11
- skill_packages=11
- context_profiles=11
- budget_profiles=6
- provider_routes=3
- evaluation_profiles=11
- evaluation_cases=33
- mandatory_failures=8
- completed_planned_tests=5
```

### Complete quality gate

- runtime tests: 107 passed;
- total coverage: 92.45 percent;
- mandatory coverage floor: 90 percent;
- Python compilation: passed;
- Ruff: passed;
- strict MyPy: passed with no issues across 19 source files.

### Retained artefact

- files: 28;
- artefact ID: `8892672584`;
- compressed size: 53,019 bytes;
- SHA-256: `8652d65cd3967146415842f914b2b18aa7e0439be2339faf0447c9e5c3505633`;
- retention: 30 days.

Full evidence is also recorded in `reports/phase2-validation-evidence.md`.

## 8. Explicitly deferred integration tests

The following remain future integration work and are not represented as completed:

- real model-provider execution;
- model-quality scoring against hidden answer keys;
- multi-provider and multi-run comparative evaluation;
- durable orchestration and interrupted-run recovery;
- PostgreSQL-backed canonical writes and permission enforcement;
- browser and computer-use tools;
- Office artefact rendering;
- CRM, email, calendar and external research connectors;
- production secret management;
- load, latency and cost tests using live providers;
- Founder acceptance of live agent outputs.

## 9. Phase-gate conclusion

The chat-first design, deterministic controls, prompt/skill layer, evaluation definitions and independent CI gate for Phase 2 are passed.

Later Codex integration must preserve:

- the eleven bounded role identities;
- typed input and output references;
- minimum-context and isolation rules;
- propose-only command-mediated writes;
- deterministic tool and action permissions;
- Founder approval boundaries;
- budget and escalation policy;
- provider-independent routing;
- mandatory-failure admission rules;
- independent-quality constraints.

Any required change must be raised explicitly rather than silently weakening the governed contracts.
