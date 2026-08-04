# 27 — Requirement-to-Test Traceability

## Status

Canonical traceability baseline v1.0. This document maps requirement families to implementation artefacts, deterministic tests, agent evaluations and Founder acceptance evidence.

## 1. Traceability rule

No requirement is considered implemented because code exists. A requirement is implemented only when:

1. A named artefact or service carries the behaviour.
2. One or more tests demonstrate the behaviour.
3. Test evidence is retained.
4. Any required independent or Founder review is recorded.
5. The requirement remains linked through future changes.

Each test must identify one or more requirement IDs. Each requirement must identify at least one planned or implemented test.

## 2. Test identifiers

- `UT-*` — deterministic unit test.
- `IT-*` — service or integration test.
- `E2E-*` — end-to-end engagement test.
- `AE-*` — agent evaluation.
- `SEC-*` — security or abuse test.
- `VIS-*` — visual or rendering test.
- `MODEL-*` — analytical or model test.
- `FOUNDER-*` — Founder acceptance test.

## 3. Product outcomes

| Requirements | Primary artefacts | Tests | Gate |
|---|---|---|---|
| OUT-001 | workload ledger, run ledger, Founder cockpit | E2E-WORKLOAD-001; FOUNDER-LEVERAGE-001 | Pilot gate |
| OUT-002 | mandate, decision and story records | UT-DECISION-001; AE-PARTNER-001; E2E-DECISION-001 | Engagement framing gate |
| OUT-003 | canonical truth chain and record links | IT-TRACE-001; E2E-TRACE-001 | Release gate |
| OUT-004 | provider and harness adapters | IT-ADAPTER-001; AE-MODEL-ROUTING-001 | Architecture gate |

## 4. Lifecycle and engagement control

| Requirements | Primary artefacts | Tests | Gate |
|---|---|---|---|
| LIFE-001 | lifecycle configuration | UT-LIFE-001 | Phase CF-1 |
| LIFE-002 | stage evaluator | UT-LIFE-002 | Every engagement stage |
| LIFE-003 | combined-gate evidence record | UT-LIFE-003 | Stage compression approval |
| LIFE-004 | regression command and events | UT-LIFE-004; E2E-RECYCLE-001 | Lifecycle gate |
| LIFE-005 | operational-state enum and invariant | UT-LIFE-005 | Runtime gate |
| LIFE-006 | next-best-action policy | UT-NBA-001; AE-PARTNER-002 | Founder cockpit gate |
| LIFE-007 | durable workflow adapter | IT-RECOVERY-001; E2E-RECOVERY-001 | Durable-runtime gate |
| LIFE-008 | retry policy | UT-RETRY-001; IT-RETRY-001 | Runtime gate |
| LIFE-009 | kill-switch service | IT-KILL-001; FOUNDER-KILL-001 | Production gate |

## 5. Authority and autonomy

| Requirements | Primary artefacts | Tests | Gate |
|---|---|---|---|
| AUTH-001 | action classifier | UT-AUTH-001 | Every action |
| AUTH-002 | policy evaluator | UT-AUTH-002 | Autonomous execution |
| AUTH-003 | approval requirement | UT-AUTH-003; AE-ESCALATE-001 | Founder decision gate |
| AUTH-004 | external-action gateway | UT-AUTH-004; IT-EXTERNAL-001 | External action gate |
| AUTH-005 | commercial policy | UT-AUTH-005 | Commercial gate |
| AUTH-006 | specialist-review rule | UT-AUTH-006; AE-BOUNDARY-001 | Regulated-work gate |
| AUTH-007 | irreversible-action policy | UT-AUTH-007 | Irreversible gate |
| AUTH-008 | reviewer independence rule | UT-QA-INDEP-001 | Quality gate |
| AUTH-009 | Founder packet schema | UT-PACKET-001; FOUNDER-PACKET-001 | Founder decision gate |
| AUTH-010 | interruption minimisation | AE-PARTNER-003; FOUNDER-NOISE-001 | User-experience gate |

## 6. Data and traceability

| Requirements | Primary artefacts | Tests | Gate |
|---|---|---|---|
| DATA-001 | ID service and schemas | UT-ID-001 | Record creation |
| DATA-002 | tenant and engagement scopes | UT-SCOPE-001; SEC-ISOLATION-001 | Security gate |
| DATA-003 | versioned record store | IT-VERSION-001 | Persistence gate |
| DATA-004 | audit-event ledger | IT-AUDIT-001 | Release and incident gate |
| DATA-005 | relationship graph | IT-TRACE-001; E2E-TRACE-001 | Release gate |
| DATA-006 | epistemic status enum | UT-EPISTEMIC-001; AE-EVIDENCE-001 | Evidence gate |
| DATA-007 | contradiction links | UT-EVIDENCE-002; AE-EVIDENCE-002 | Evidence gate |
| DATA-008 | immutable baselines | IT-BASELINE-001 | Release gate |
| DATA-009 | retention policy | IT-RETENTION-001; SEC-DELETION-001 | Production gate |
| DATA-010 | regional-cell architecture | IT-REGION-001; SEC-REGION-001 | Regional deployment gate |

## 7. Knowledge and methodology

| Requirements | Primary artefacts | Tests | Gate |
|---|---|---|---|
| KNOW-001 | source object store and manifest | IT-INGEST-001 | Knowledge gate |
| KNOW-002 | alias resolver | UT-ALIAS-001; IT-ALIAS-001 | Knowledge gate |
| KNOW-003 | method schema | UT-METHOD-001 | Promotion gate |
| KNOW-004 | method-selection engine | UT-SELECT-001; AE-METHOD-001 | Method gate |
| KNOW-005 | rejected-method record | UT-SELECT-002; AE-METHOD-002 | Method gate |
| KNOW-006 | domain and sector overlays | UT-OVERLAY-001; AE-METHOD-003 | Method gate |
| KNOW-007 | candidate promotion workflow | UT-RADAR-001; IT-RADAR-001 | Library release gate |
| KNOW-008 | usage-rights controls | UT-RIGHTS-001; FOUNDER-RIGHTS-001 | Promotion gate |
| KNOW-009 | scheduled Radar | IT-RADAR-002 | Methodology release gate |
| KNOW-010 | review and supersession | UT-SUPERSEDE-001; IT-SUPERSEDE-001 | Knowledge maintenance gate |

## 8. Research and evidence

| Requirements | Primary artefacts | Tests | Gate |
|---|---|---|---|
| EVID-001 | research plan and question tree | AE-RESEARCH-001 | Research-start gate |
| EVID-002 | source document schema | UT-SOURCE-001 | Source admission |
| EVID-003 | passage and claim links | UT-PASSAGE-001; IT-CITATION-001 | Evidence gate |
| EVID-004 | snippet rejection policy | AE-RESEARCH-002 | Evidence gate |
| EVID-005 | source-scope evaluator | AE-EVIDENCE-003 | Evidence gate |
| EVID-006 | evidence-burden policy | UT-BURDEN-001 | Decision and release gates |
| EVID-007 | staleness service | IT-STALENESS-001 | Release gate |
| EVID-008 | research stopping rule | AE-RESEARCH-003 | Research close gate |
| EVID-009 | citation projection | VIS-CITATION-001; E2E-CITATION-001 | Deliverable release |
| EVID-010 | untrusted-input boundary | SEC-INJECTION-001; SEC-DOCUMENT-001 | Security gate |

## 9. Analysis and modelling

| Requirements | Primary artefacts | Tests | Gate |
|---|---|---|---|
| MODEL-001 | analytical runtime | MODEL-CALC-001 | Model gate |
| MODEL-002 | run manifest | MODEL-REPRO-001 | Model gate |
| MODEL-003 | value-case schema | MODEL-VALUE-001 | Investment gate |
| MODEL-004 | scenario engine | MODEL-SCENARIO-001 | Recommendation gate |
| MODEL-005 | reconciliation service | MODEL-RECON-001 | Release gate |
| MODEL-006 | independent calculation | MODEL-INDEP-001 | Model sign-off |
| MODEL-007 | workbook architecture | VIS-XLSX-001; MODEL-XLSX-001 | Workbook release |
| MODEL-008 | unit and period metadata | MODEL-UNITS-001 | Model gate |
| MODEL-009 | limitation and failure records | MODEL-FAIL-001; AE-QUANT-001 | Model gate |

## 10. Agents and tools

| Requirements | Primary artefacts | Tests | Gate |
|---|---|---|---|
| AGENT-001 | agent registry and versioned contracts | UT-AGENT-001 | Agent admission |
| AGENT-002 | context compiler | UT-CONTEXT-001; AE-CONTEXT-001 | Agent admission |
| AGENT-003 | command API | IT-AGENT-WRITE-001 | Runtime gate |
| AGENT-004 | tool and record policy | SEC-TOOL-001; SEC-SCOPE-001 | Agent admission |
| AGENT-005 | typed envelope | UT-ENVELOPE-001 | Agent admission |
| AGENT-006 | run budget | UT-BUDGET-001; IT-BUDGET-001 | Runtime gate |
| AGENT-007 | adversarial test suite | SEC-INJECTION-001 through SEC-INJECTION-020 | Agent admission |
| AGENT-008 | provider router | AE-ROUTING-001; IT-ROUTING-001 | Model release |
| AGENT-009 | adapter contract | IT-ADAPTER-001 | Architecture gate |

## 11. Quality and release

| Requirements | Primary artefacts | Tests | Gate |
|---|---|---|---|
| QA-001 | decision-relevance rubric | AE-QA-001; FOUNDER-DECISION-001 | Release gate |
| QA-002 | assurance-tier policy | UT-QA-001 | Engagement setup |
| QA-003 | defect record | UT-DEFECT-001 | Quality gate |
| QA-004 | severity and blocking rules | UT-DEFECT-002 | Release gate |
| QA-005 | repair workflow | IT-REPAIR-001 | Release gate |
| QA-006 | exception record | UT-EXCEPTION-001 | Exception gate |
| QA-007 | sign-off record | UT-SIGNOFF-001 | Release gate |
| QA-008 | same-model independence rule | UT-QA-INDEP-001 | High-assurance gate |
| QA-009 | fixture registry | IT-FIXTURE-001 | Regression gate |

## 12. Deliverables and visuals

| Requirements | Primary artefacts | Tests | Gate |
|---|---|---|---|
| DELIV-001 | semantic story model | UT-STORY-001 | Story gate |
| DELIV-002 | proposition and page contracts | AE-STORY-001 | Story gate |
| DELIV-003 | reconciliation service | UT-RECON-001; E2E-RECON-001 | Release gate |
| DELIV-004 | visual specification | VIS-EDIT-001 | Visual gate |
| DELIV-005 | archetype registry | UT-VISUAL-001; VIS-ARCH-001 | Visual gate |
| DELIV-006 | image-use policy | UT-VISUAL-002 | Visual gate |
| DELIV-007 | rendering QA | VIS-PPTX-001; VIS-DOCX-001; VIS-XLSX-001; VIS-HTML-001 | Release gate |
| DELIV-008 | named model output links | UT-RECON-002 | Release gate |
| DELIV-009 | citation projection | VIS-CITATION-001 | Release gate |
| DELIV-010 | artefact metadata | UT-ARTEFACT-001 | Release gate |

## 13. Implementation and benefits

| Requirements | Primary artefacts | Tests | Gate |
|---|---|---|---|
| IMPL-001 | initiative trace link | UT-IMPL-001 | Implementation gate |
| IMPL-002 | initiative schema | UT-IMPL-002 | Mobilisation gate |
| IMPL-003 | intervention/implementation distinction | AE-IMPLEMENT-001 | Implementation review |
| IMPL-004 | benefit verification rule | UT-BENEFIT-001 | Benefit gate |
| IMPL-005 | benefit schema | UT-BENEFIT-002 | Benefits baseline gate |
| IMPL-006 | scale/adapt/stop decision | AE-BENEFIT-001; E2E-BENEFIT-001 | Benefits review |

## 14. CRM and origination

| Requirements | Primary artefacts | Tests | Gate |
|---|---|---|---|
| CRM-001 | CRM boundary and adapters | IT-CRM-001 | CRM integration gate |
| CRM-002 | external ID map | IT-CRM-002 | Sync gate |
| CRM-003 | field allowlist | SEC-CRM-001 | Sync gate |
| ORIG-001 | opportunity dossier | UT-ORIG-001; AE-ORIG-001 | Opportunity qualification |
| ORIG-002 | outreach approval | UT-OUTREACH-001; IT-OUTREACH-001 | External action gate |
| ORIG-003 | suppression ledger | UT-SUPPRESSION-001 | Campaign gate |
| ORIG-004 | identity and factuality policy | AE-OUTREACH-001 | Campaign gate |

## 15. Security and operations

| Requirements | Primary artefacts | Tests | Gate |
|---|---|---|---|
| SEC-001 | secret-management policy | SEC-SECRET-001 | CI and production gates |
| SEC-002 | role and tool permissions | SEC-LEAST-001 | Security gate |
| SEC-003 | environment architecture | IT-ENV-001 | Deployment gate |
| SEC-004 | encrypted storage and transport | SEC-ENCRYPT-001 | Production gate |
| SEC-005 | Singapore deployment configuration | SEC-REGION-001 | Staging gate |
| SEC-006+ | threat model and operational controls | SEC-* catalogue | Production gate |

## 16. Evidence retention

For every automated test run, retain:

- repository commit SHA;
- environment and dependency versions;
- test IDs executed;
- result and duration;
- failure details;
- produced artefacts or screenshots;
- responsible actor or agent;
- remediation link;
- approval or exception record.

## 17. Immediate traceability work

1. Add requirement IDs to every current unit test.
2. Generate a machine-readable `requirements/traceability.yaml`.
3. Prevent CI from accepting mandatory requirements without tests.
4. Add fixture IDs to every agent evaluation.
5. Require pull requests to list requirements changed and tests executed.
6. Produce coverage reports by requirement family, not only by source-code line.