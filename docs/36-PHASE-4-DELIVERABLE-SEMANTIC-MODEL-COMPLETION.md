# 36 — Phase 4 First Deliverable Semantic Model Completion

## Status

**Chat-first Phase 4: complete and independently CI-validated.**

Date: 2026-08-04

This release completes the first governed semantic model for a consulting deliverable. It converts the restricted Northstar AI-audit analytical oracle into one assertion-led, versioned and traceable story that can later be rendered into PowerPoint, Word, Excel, PDF, SVG and HTML without allowing each file format to invent its own conclusions, numbers or structure.

Phase 4 completes the semantic and reconciliation authority. It does **not** claim that final Office or browser artefacts have been rendered, opened, saved, visually inspected or accepted by the Founder.

## 1. Governing decision and immutable story

The shared story model is `STORY-DAI-001`, version `1.0.0`. It supports the same decision established by the Phase 3 oracle:

- approve one bounded quotation-drafting pilot, `UC-001`;
- retain `UC-008` as the mandatory non-AI quotation-process comparator;
- preserve human technical approval, pricing authority and external release;
- defer the autonomous external chatbot;
- defer production inventory forecasting until data remediation and controlled back-testing are complete;
- classify the value case as released capacity and potential incremental margin, not immediate cash savings;
- recognise zero immediate cash-releasing headcount benefit;
- scale only after outcome and control evidence passes;
- stop on material leakage, unauthorised release, control failure or value failure.

The communication objective, governing thought, recommendation identifiers and roadmap action identifiers are immutable references used by every surface plan.

## 2. Assertion-led executive story

The first story contains eight decision-led sections and twelve governed assertions. The opening section states the decision rather than presenting a generic overview:

1. Approve a bounded quotation-drafting pilot—not autonomous AI.
2. Quotation work is material, but elapsed time is not automatable touch time.
3. Customer service and inventory evidence do not support autonomous deployment.
4. Public-AI use creates a control gap while training interest supports managed adoption.
5. The pilot fits the ceiling, but value is capacity and potential margin—not cash savings.
6. Human authority and foundation controls must remain in the operating model.
7. Scale only after controlled evidence passes—and stop on material harm.
8. Appendix: sources, assumptions, methods and reconciliations.

Every material assertion carries an epistemic status and resolves to evidence or analysis references. Recommendations cannot exist without evidence or analytical support.

## 3. Named-number registry

The semantic model contains eighteen approved material-number records. Each record has:

- a stable `NUM-DAI-*` identifier;
- label, value, unit and period;
- the exact Phase 3 oracle record and field from which it was derived;
- an approval flag;
- controlled display precision.

The registry includes quotation volumes and touch time, customer-service readiness measures, workforce measures, pilot costs, commitment ceiling, addressable capacity, potential incremental margin, recurring support cost, zero immediate headcount cash benefit and break-even conditions.

A semantic surface cannot display an unapproved number. Unknown number references, altered values and stale analytical inputs fail validation.

## 4. Citation and provenance model

Six governed citation records preserve complete internal provenance for the six Phase 3 evidence findings while supporting proportionate client presentation.

Each citation provides:

- exact source IDs and evidence-finding IDs;
- detailed internal provenance and limitations;
- a concise client-facing source note;
- approved presentation modes for footnotes, speaker notes, appendices, workbook source tabs and on-demand disclosure.

The answer key, Phase 3 oracle baseline and Phase 4 semantic baseline are restricted evaluation materials and are blocked from normal agent context. They are not listed as generation sources in any deliverable manifest.

## 5. First visual grammar

Six editable visual specifications define the meaning and structure of the first deliverable’s labelled visuals:

- portfolio matrix for use-case disposition;
- process flow for bounded drafting and retained human gates;
- value-driver tree separating cash, capacity and potential margin;
- layered control stack;
- stage-gated roadmap;
- causal narrative connecting delivery, adoption, outcomes, value and scale.

Each visual specifies its message, entities, relationships, layout rules, accessibility requirements, allowed surfaces and editability requirement. Labelled visuals are mapped to native shapes, editable charts, SVG or web components rather than text-only or raster-only placeholders.

## 6. Semantic objects and surface plans

Twelve semantic objects form the reusable content layer:

- cover;
- executive decision;
- quotation analysis;
- customer-service and inventory evidence;
- workforce evidence;
- options;
- value case;
- control model;
- roadmap;
- Founder approval;
- appendix;
- workbook checks.

Six renderer-independent surface plans contain 55 surface objects:

| Surface | Semantic purpose |
|---|---|
| PPTX | Executive decision deck using editable native shapes |
| DOCX | Decision report with narrative, evidence and appendices |
| XLSX | Source register, assumptions, formula calculations, outputs and checks |
| PDF | Controlled distribution copy derived from the same story |
| SVG | Editable vector visual library |
| HTML | Responsive decision brief with progressive disclosure and on-demand provenance |

Every manifest references `STORY-DAI-001` version `1.0.0`, the same evidence baseline, the same analytical model version and stable semantic-object IDs.

## 7. Workbook semantic architecture

The Excel plan explicitly separates:

- read-me and purpose;
- source and provenance register;
- assumptions;
- calculations;
- approved outputs;
- checks and cross-format reconciliation.

This phase defines the workbook semantics and formula-bearing role of the calculation sheets. Physical workbook generation, formula execution in Excel and open-and-save inspection remain renderer-integration evidence.

## 8. Cross-format reconciliation

`RECON-DAI-001` performs eight deterministic semantic reconciliation checks:

- headline;
- assumption;
- number;
- recommendation;
- roadmap;
- source;
- version;
- rendered-inspection boundary.

The first seven checks confirm that every planned surface shares the same approved semantic baseline. The rendered-inspection record states explicitly that semantic inspection passed while renderer and Office inspection remain a later execution gate.

The independent semantic grader performs 115 checks covering identity, versioning, story logic, complete surfaces, number reconciliation, recommendation preservation, citation scope, visual grammar, immutable baselines, confidentiality, Founder authority and restricted-material isolation.

## 9. Founder review boundary

The Founder review summary requests approval of the semantic model for later renderer implementation. It does not authorise client issuance.

The exact release action states that no external client artefact may be issued from this phase. Founder approval remains required for pilot scope, commitment, residual risk and any later external release.

## 10. Restricted reproducible baseline

`deliverable-semantic-baseline.json` is:

- classified as a restricted evaluation semantic model;
- marked `agent_visible: false`;
- linked to the exact Phase 3 analytical input digest;
- protected by a semantic-model SHA-256 digest;
- generated using deterministic ordering for set-valued fields;
- byte-reproducible across independent Python processes;
- protected by a read-only clean-generation CI gate;
- excluded from normal agent context.

Mutation tests confirm that changed analytical inputs, altered displayed numbers, missing surfaces, unknown references, story-version drift and stale baselines fail rather than being silently normalised.

## 11. Requirement and test traceability

Phase 4 adds twenty-one mapped executable test nodes and converts four planned tests into executable evidence:

- `AE-STORY-001`;
- `UT-ARTEFACT-001`;
- `UT-RECON-002`;
- `UT-VISUAL-002`.

The combined registry now records:

- 146 implemented test nodes;
- 57 remaining planned tests;
- 15 completed planned-test IDs across the chat-first phases;
- all 123 catalogue requirements mapped to implemented or planned evidence.

## 12. Independent validation evidence

GitHub Actions run `30923198327`, job `92038774955`, validated branch head `615579a419a49aa93a6ce945375e54c4806e7fd4` and its pull-request merge reference on Ubuntu 24.04 and Python 3.11.15.

### Phase 4 validator

```text
PHASE 4 DELIVERABLE SEMANTIC MODEL VALIDATION PASSED
- story_sections=8
- assertions=12
- numbers=18
- citations=6
- visuals=6
- semantic_objects=12
- surface_plans=6
- surface_objects=55
- semantic_grade_checks=115
- completed_planned_tests=4
```

### Complete Phase 1–4 quality gate

- Phase 1 contract validator: passed;
- Phase 2 agent-system validator: passed;
- Phase 3 analytical-oracle validator: passed;
- Phase 4 deliverable-semantic validator: passed;
- clean generation of the requirement registry, Phase 3 oracle and Phase 4 semantic baseline: passed;
- runtime tests: 148 passed;
- total coverage: 93.29 percent;
- mandatory coverage floor: 90 percent;
- Python compilation: passed;
- Ruff: passed;
- strict MyPy: passed with no issues across 27 source files.

### Retained release artefact

- files: 34;
- artefact ID: `8897969065`;
- compressed size: 74,583 bytes;
- SHA-256: `e23ffdad4be9d69ad87ba70c486803226ca459dc7477905ce13259e3a178563a`;
- retention: 30 days.

## 13. Explicitly deferred evidence

Phase 4 does not establish:

- production rendering of PPTX, DOCX, XLSX, PDF, SVG or HTML files;
- PowerPoint, Word or Excel open-and-save integrity;
- native Office editability in generated files;
- rendered visual-regression approval;
- pixel-level layout quality;
- workbook formula recalculation in Excel;
- browser accessibility execution;
- client citation placement in physical artefacts;
- live-model narrative quality;
- Founder acceptance of rendered deliverables.

The remaining renderer-dependent tests include `VIS-CITATION-001`, `VIS-EDIT-001` and `VIS-PPTX-001`. They must not be marked complete until physical artefacts exist and are independently inspected.

## 14. Phase-gate conclusion

The first deliverable semantic model is complete as a restricted, reproducible, assertion-led and independently validated authority for all planned output surfaces.

Later renderer implementation must preserve the immutable story and number identifiers, source provenance, citation policy, visual specifications, recommendation and comparator, human-authority controls, value classifications, Founder release boundary, cross-format reconciliation and clean-generation gate. Any required change must be raised explicitly rather than allowing a renderer or agent to silently alter the consulting conclusion.
