# 35 — Phase 3 AI-Audit Analytical Oracle Completion

## Status

**Chat-first Phase 3: complete and independently CI-validated.**

Date: 2026-08-04

This release completes a restricted, deterministic and provider-independent analytical oracle for the synthetic Northstar SME AI audit. The oracle is an evaluation and regression authority; it is not normal agent context, a canned client answer or evidence that a live model provider can reproduce the result.

## 1. Governing decision and scope

The oracle preserves the client-visible mandate:

- decision owner: Founder;
- decision: whether to approve one controlled AI pilot and supporting foundations;
- maximum initial cash commitment: SGD 120,000;
- counterfactual: continue process and data improvement without an AI pilot.

The oracle uses fourteen client-visible fixture files and separately grades the generated result against the restricted answer key. Neither `expected-results.yaml` nor `oracle-baseline.json` is permitted in normal agent context.

## 2. Deterministic analytical system

The Phase 3 modules implement typed and reproducible analysis for:

- quotation volume, touch time, elapsed time, specialist waiting, rework, data errors and extraction candidacy;
- customer-service category suitability, specialist escalation and approved-knowledge coverage;
- workforce AI use, review confidence, training interest and workforce or leakage concerns;
- process, data, application, identity, platform and review-owner readiness;
- adversarial-document and prompt-injection handling;
- pilot costs, recurring costs, released capacity, incremental margin and break-even conditions;
- risk severity, control weakness, mandatory human authority and Founder acceptance;
- use-case scoring, affordability, disposition, comparator retention and recommendation switching;
- method selection, rejected methods, evidence findings, uncertainties and specialist review;
- outcome, control, scale and stop conditions.

All material calculations are performed in deterministic Python. The language-model layer is not used to calculate or grade the oracle.

## 3. Core analytical conclusions

### Quotation analysis

- six-month quotation volume: 6,260;
- annualised quotation volume: 12,520;
- six-month measured touch time: 3,198.85 hours;
- annualised measured touch time: 6,397.70 hours;
- simple and standard quotations: 82.24 percent of volume;
- complex and engineered quotations: 38.45 percent of measured touch time.

The evidence does not establish that administration consumes half of seller capacity. Elapsed time is not treated as automatable touch time.

### Customer-service analysis

- annual tickets: 18,420;
- conditionally suitable categories: 43 percent;
- low, prohibited or unknown autonomous suitability: 57 percent;
- established autonomous-ready share: zero;
- weighted specialist-escalation rate: 26.11 percent;
- weighted approved-knowledge coverage: 59.45 percent.

The evidence supports only a controlled internal, human-mediated knowledge assistant after knowledge, identity and review controls improve. It does not support an autonomous external chatbot.

### Workforce analysis

- respondents: 123;
- weighted public-AI use: 21.76 percent;
- confidence reviewing AI output: 33.91 percent;
- interest in training: 79.62 percent;
- concern about job reduction: 52.34 percent;
- concern about data leakage: 60.09 percent.

Unapproved public-AI use is therefore treated as a current control gap, while adoption depends on approved tools, transparent role design, verification training and limits on telemetry use.

### Financial analysis

- base pilot cost: SGD 88,000;
- downside pilot cost: SGD 118,000;
- upside pilot cost: SGD 76,000;
- downside headroom below the approved ceiling: SGD 2,000;
- annual addressable capacity value: SGD 210,000;
- potential annual incremental gross margin: SGD 145,000;
- recurring platform and support cost: SGD 36,000;
- immediate cash-releasing headcount benefit: SGD 0;
- recurring-support break-even capacity redeployment: 17.14 percent;
- recurring-support break-even conversion uplift: 0.50 percentage points;
- year-one pilot-and-support break-even conversion uplift: 1.71 percentage points.

The oracle rejects the management claim that released capacity and possible gross-margin uplift constitute immediate year-one cash savings.

## 4. Recommendation oracle

The preferred first pilot is `UC-001`, a bounded quotation-drafting assistant. Its scope is limited to:

- extracting enquiry fields into a structured draft;
- retrieving approved, current product and prior-quotation evidence;
- identifying missing information and required approvals;
- retaining human technical approval;
- retaining human pricing and discount authority;
- retaining human external release.

`UC-008`, the non-AI quotation-process comparator, remains mandatory. `UC-003`, the autonomous customer-facing chatbot, is deferred. `UC-004`, inventory forecasting, requires demand-label and substitution remediation plus a controlled back-test before production consideration.

A mutation test confirms that when `UC-001` exceeds the SGD 120,000 ceiling, the oracle does not force the preferred answer: it switches to the next bounded eligible option, `UC-005`.

## 5. Method and evidence oracle

The required method roles are represented by:

- `DAI-02` strategic focus;
- `DAI-03` process and decision mapping;
- `DAI-05` opportunity identification;
- `DAI-06` readiness and feasibility;
- `DAI-07` risk and governance;
- `DAI-10` staged value case;
- `DAI-11` pilot and scale evidence;
- `DAI-12` task and human-role design.

Four tempting approaches are explicitly rejected: a maturity score as the governing decision method, an autonomous external chatbot as first pilot, production inventory forecasting as first pilot, and a headcount-reduction business case.

Six evidence findings preserve epistemic status, exact source IDs, row references where applicable and limitations. The independent restricted grader performs 74 checks against the answer key.

## 6. Source integrity and disclosed discrepancies

The oracle preserves original fixture files and records SHA-256 checksums for all fourteen client-visible inputs.

Two source-level defects are handled without silent correction:

1. One quotation row has no numeric extraction-candidate percentage and its narrative note occupies that field. The value is treated as missing and excluded from that one weighted estimate; it is not imputed.
2. The client-visible mandate says “Continue process and data improvement without an AI pilot,” while the restricted answer key says “Continue non-AI process and data improvements without an AI pilot.” The mandate wording remains canonical. The grader recognises only this documented semantic equivalent.

The adversarial vendor document is admitted only as an unverified marketing claim. Its embedded instructions, approval claim, credential request, upload request and deployment request are ignored and blocked.

## 7. Restricted baseline and anti-overfitting controls

`oracle-baseline.json` is:

- classified as a restricted evaluation oracle;
- marked `agent_visible: false`;
- generated from client-visible inputs only;
- independently graded against the restricted answer key;
- byte-reproducible;
- protected by a clean-generation CI gate;
- excluded from normal context packages.

Mutation tests ensure that the implementation is not merely returning a fixed answer. They test affordability switching, financial-defect detection, stale-baseline detection, malformed input, missing input, restricted-context leakage and invalid answer-key shape.

## 8. Requirement and test traceability

Phase 3 adds twenty mapped executable test nodes and retires six planned tests:

- `IT-FIXTURE-001`;
- `IT-INDEPENDENT-RECALC-001`;
- `UT-BURDEN-001`;
- `UT-DECISION-FITNESS-001`;
- `UT-EPISTEMIC-001`;
- `UT-REPRODUCIBILITY-001`.

The combined registry now records:

- 125 implemented test nodes;
- 61 remaining planned tests;
- all 123 catalogue requirements mapped to implemented or planned evidence.

## 9. Independent validation evidence

GitHub Actions run `30917129738`, job `92017989740`, validated pull-request merge reference `fec683a622da2974be3f0f5cae7dbc7371a80af7` on Ubuntu 24.04 and Python 3.11.15.

### Prior-phase regression gates

Phase 1 passed with:

- eight generated contract artefacts;
- 58 registered models;
- four governed configurations;
- 26 OpenAPI paths;
- ten commands and fifteen events;
- all 123 requirements mapped;
- the 396-line PostgreSQL baseline inspected.

Phase 2 passed with:

- eleven agents and eleven skill packages;
- eleven context profiles;
- six budget profiles;
- three provider routes;
- eleven evaluation profiles and 33 evaluation cases;
- eight mandatory failure conditions.

### Phase 3 gate

```text
PHASE 3 AI-AUDIT ANALYTICAL ORACLE VALIDATION PASSED
- client_visible_inputs=14
- source_documents=15
- quotation_rows=24
- customer_service_rows=8
- process_rows=10
- asset_rows=12
- use_cases=8
- workforce_segments=6
- financial_lines=16
- risks=12
- evidence_findings=6
- method_roles=8
- method_rejections=4
- oracle_grade_checks=74
- completed_planned_tests=6
```

### Complete quality gate

- runtime tests: 127 passed;
- total coverage: 93.32 percent;
- mandatory coverage floor: 90 percent;
- Python compilation: passed;
- Ruff: passed;
- strict MyPy: passed with no issues across 25 source files;
- clean generation of the restricted oracle and test registry: passed.

### Retained artefact

- files: 31;
- artefact ID: `8895523204`;
- compressed size: 62,327 bytes;
- SHA-256: `56759d85a15faa9573e4eb385f56f1d5a72e0e31f680277edfcb57acc30d6d12`;
- retention: 30 days.

## 10. Explicitly deferred evidence

This phase does not establish:

- live model-provider output quality;
- comparative multi-model or repeated-run evaluation against the hidden oracle;
- durable orchestration or interrupted-run recovery;
- PostgreSQL-backed runtime write and permission enforcement;
- browser, computer-use or Office execution;
- CRM, email, calendar or external research connectors;
- production secret management;
- live provider cost, latency or load performance;
- Founder acceptance of live agent outputs.

## 11. Phase-gate conclusion

The chat-first analytical logic, restricted baseline, independent grader, source controls, mutation suite, requirement traceability and complete Phase 1–3 CI gate are passed.

Later integration must preserve the restricted-oracle boundary, client-visible-input construction, deterministic calculations, source discrepancies, human authority controls, non-AI comparator, value classifications, mutation tests and clean-generation gate. Any required change must be raised explicitly rather than silently changing the answer key, source evidence or governing conclusion.
