# 71 — PCFA-04 Product-scope implementation addendum

## Purpose

PCFA-04 closes the remaining product-scope specification gaps before Codex without implementing product/runtime code. It preserves the existing `IMP-P0`–`IMP-P12` architecture and assigns every added obligation to existing implementation phases and integration points.

All PCFA-04 requirements are `planned_not_implemented`. PCFA-04 does not create migrations, APIs, UI components, agents, workflows, renderers, retrieval adapters, Office round-trip code, CRM integration or production infrastructure.

## Canonical machine record

The governed source is `configs/pcfa04-product-scope-implementation-addendum.yaml` and the generated current record is `repository/pcfa04-product-scope-implementation-addendum.json`.

The package contains 14 product areas and 29 requirements, including 15 explicit Consulting Craft `CQ-*` requirements.

## Product areas

### 1. Mandate Intake Workbench

Transform notes, transcripts, documents and CRM context into a governed mandate packet: decision statement and owner/date, problem, scope, constraints, options, facts, assumptions, interpretations, gaps, evidence standard, hypotheses, methods, data requests and engagement plan. Only material gaps should interrupt the Founder.

Primary ownership: `IMP-P2`, `IMP-P4`, `IMP-P5`.

### 2. Explicit Engagement Workspace

Provide the engagement as one coherent workspace with Overview, Mandate, Decisions, Hypotheses, Evidence, Methods, Analysis, Recommendations, Story, Deliverables, Implementation, Benefits, Quality and Audit surfaces. These are views over the canonical system of record, never a second state store.

Primary ownership: `IMP-P2` through `IMP-P7` as the relevant capabilities become available.

### 3. Quality and Assurance Console

Expose defects, severity/materiality, affected canonical records, creator, independent reviewer, rubric/test, blocking status, repair, disposition/waiver, rerun evidence and release impact. A presentation choice cannot hide a material blocking defect.

Primary ownership: `IMP-P2`, `IMP-P3`, `IMP-P4`, `IMP-P5`, `IMP-P6`, `IMP-P7`, `IMP-P11`.

### 4. Implementation and Benefits Workspace

Trace recommendation → initiative → milestone → dependency → owner → delivery → adoption → outcome → benefit → verification, while distinguishing work completed, adoption, outcome and realised benefit.

Primary ownership: `IMP-P2`, `IMP-P3`, `IMP-P12`.

### 5. Broader ingestion matrix and native provenance locators

Primary pre-authorisation formats are Markdown/TXT, DOCX, digital PDF, PPTX, XLSX, CSV and HTML/web snapshots. Later adapters may cover scanned documents/images/OCR, email packages, transcript/audio/video derivatives and archives.

Native locators must preserve PDF page/region, DOCX section/paragraph/table, PPTX slide/shape, XLSX sheet/cell/range/formula, HTML URL/snapshot/DOM/text location and transcript speaker/timestamp. Original bytes and checksums remain preserved.

Primary ownership: `IMP-P1`, `IMP-P5`.

### 6. Canonical library completeness gate

The old count-only expectation is insufficient. Library readiness must eventually prove that **100% of approved canonical library sources are accounted for** as structured records, ingested unstructured sources, duplicates, superseded items, quarantined items or explicit exclusions with reason.

Primary ownership: `IMP-P1`, final acceptance in `IMP-P12`.

### 7. Consulting Craft quality family

PCFA-04 introduces the explicit family:

- `CQ-DECISION` — decision relevance;
- `CQ-ANSWER` — answer-first communication;
- `CQ-TITLE` — assertion-led titles;
- `CQ-STORY` — storyline coherence;
- `CQ-MECE` — decomposition integrity where applicable;
- `CQ-ALT` — credible alternatives and trade-offs;
- `CQ-UNCERT` — calibrated uncertainty;
- `CQ-DENSITY` — professional information density;
- `CQ-VISUAL` — message-appropriate visual archetypes;
- `CQ-HIER` — visual hierarchy and whitespace;
- `CQ-REDUND` — redundancy control;
- `CQ-ACTION` — implementation specificity;
- `CQ-RISK` — risks, dependencies and reversibility;
- `CQ-AUDIENCE` — audience fit without semantic drift;
- `CQ-EXEC` — standalone decision-useful executive summary.

These should ultimately combine deterministic structural checks where possible, fixed-rubric independent model review, alternate reviewer checks and Founder scoring. They must not freeze exact prose as a golden answer.

Primary ownership: `IMP-P4`, `IMP-P7`, `IMP-P12`.

### 8. Broader golden-output programme

Golden evaluation must represent all engagement families—strategy, growth/pricing, cost/value, CX, operating model, organisation/workforce, AI/digital, risk/control, M&A, carve-out, valuation/capital, implementation and benefits—using semantic invariants, quality thresholds and numeric ranges rather than exact wording.

Primary ownership: `IMP-P7`, `IMP-P12`.

### 9. Office round-trip reconciliation

Support canonical → PPTX/DOCX/XLSX render → human external edit → re-import → semantic/numeric/layout diff → classification → Founder adopt/reject → canonical update → regeneration without overwriting human edits.

Changes must classify wording, title, number, formula, chart, layout, recommendation, assumption, citation and structure changes.

Primary ownership: `IMP-P7`, `IMP-P12`.

### 10. Founder / house-style profile

Maintain a versioned canonical preference profile for writing style, title conventions, slide density, number formats, chart/table preferences, terminology, risk phrasing, citation modes, templates/brand, fonts, executive-summary form and decision-packet density. This profile is canonical product state, not Hermes or model memory.

Primary ownership: `IMP-P2`, `IMP-P7`, `IMP-P12`.

### 11. Deliverable asset-rights provenance

Track provenance, owner, licence, permitted use, client-provided status, alteration/distribution rights, attribution and expiry for fonts, photos, icons, logos, templates, third-party charts/data and maps. External release must fail closed on unknown or incompatible material rights.

Primary ownership: `IMP-P1`, `IMP-P7`, `IMP-P11`.

### 12. Founder attention burden metrics

Measure material interruptions per engagement, Founder review minutes, false escalation count/rate, recycled decisions, stale-approval invalidation, outputs accepted unchanged/minor edit and material recommendation overrides. The system's leverage claim must be evaluated using Founder attention burden, not only automation volume or compute cost.

Primary ownership: `IMP-P2`, `IMP-P3`, `IMP-P12`.

### 13. Explicit deliverable variants

The same approved semantic story and material-number sources must support board deck, working-team deck, decision memo, detailed report, workbook, implementation plan and one-page executive summary. Audience adaptation must not create conflicting claims, recommendations or numbers.

Primary ownership: `IMP-P7`.

### 14. Review and change-request workflow

Support draft → review → anchored comment → resolve/reject → reissue with reviewer identity, affected semantic object, disposition and version history. Review state must survive reissue and cannot silently mutate approved canonical content.

Primary ownership: `IMP-P2`, `IMP-P3`, `IMP-P7`.

## Phase ownership overlay

PCFA-04 does not invent new IMP phases. It overlays the existing backlog as follows:

- `IMP-P0`: no new product-runtime scope; preserve extension points and governance boundaries only.
- `IMP-P1`: source matrix, native locators, library accounting, asset-rights provenance foundation.
- `IMP-P2`: mandate/workspace/QA/implementation-benefit/style/review canonical records and shells.
- `IMP-P3`: durable review/recycle and implementation/benefit lifecycle behaviours.
- `IMP-P4`: bounded mandate/context enhancement and Consulting Craft evaluators.
- `IMP-P5`: source-locator evidence adapters and research/evidence traceability.
- `IMP-P6`: existing quantitative reproducibility remains the numeric source for the new workspaces and QA.
- `IMP-P7`: Consulting Craft, variants, goldens, style application, rights checks and Office round trips.
- `IMP-P8`: CRM conversion must populate the same mandate/engagement model.
- `IMP-P9`: origination must feed the same CRM/opportunity/mandate path.
- `IMP-P10`: Radar must feed the governed method/source registry without automatic promotion.
- `IMP-P11`: mature QA/security release controls and material asset-rights enforcement.
- `IMP-P12`: Founder-attention, CQ, golden, round-trip, variant and library-completeness acceptance.

## PCFA-05 and PCFA-07 boundaries

PCFA-04 intentionally does **not** define the Minimum Valuable Consulting Loop as a machine contract; that remains PCFA-05.

PCFA-04 also does not yet rewrite the global implementation-obligation and test registries. PCFA-07 must assign every PCFA-04 requirement an exact task binding, planned test ID, evidence type, blocking phase gate and dependency mapping while preserving `planned_not_implemented` until implementation evidence exists.

## Acceptance invariants

PCFA-04 passes only when:

1. all 14 identified product areas are present;
2. all 29 requirements are unique and referenced by exactly one product-area ownership record;
3. all 15 `CQ-*` requirements are present;
4. all product areas have at least one owning IMP phase and existing integration point;
5. no product area is assigned as new `IMP-P0` product-runtime scope;
6. every requirement remains `planned_not_implemented`;
7. canonical-state/view invariants are explicit;
8. Founder accountability and fail-closed boundaries remain unchanged;
9. current operational authority binds the exact PCFA-04 record digest;
10. the launch verifier fails closed if the PCFA-04 current authority is removed or drifted;
11. all PCFA-01 through PCFA-03 checks and the immutable WS6.16 release remain valid;
12. full repository tests, coverage, Ruff, strict MyPy, compile checks and workflow matrix remain green.

## Authorization boundary

PCFA-04 is specification only. It does not authorize Codex, IMP-P0 implementation, merge, IMP-P1, runtime/Hermes activation, real client data, public distribution, paid services, OAuth, deployment or external action.

`codex_start_authorized=false`.
