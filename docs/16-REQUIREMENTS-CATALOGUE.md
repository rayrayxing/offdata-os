# 16 — Numbered Requirements Catalogue

> Status: baseline v0.1. These requirements translate the canonical consulting materials and the Build Pack into testable product requirements. Each requirement must eventually map to one or more implementation tasks and tests.

## 1. Requirement language

- **MUST** — mandatory for a conforming release.
- **SHOULD** — expected unless a recorded decision justifies departure.
- **MAY** — optional.
- **Founder gate** — explicit human approval is required.

## 2. Product outcomes

### OUT-001 — Founder leverage

The system MUST remove routine analyst, consultant and engagement-management production work while preserving Founder accountability for material recommendations, commitments and external actions.

Acceptance: workload measurement distinguishes autonomous work, Founder review, corrections and residual manual work.

### OUT-002 — Decision fitness

Every engagement and deliverable MUST identify the executive decision, decision owner, decision date or gate, options, constraints and consequence of no decision.

Acceptance: release is blocked when the supported decision cannot be stated in one sentence.

### OUT-003 — End-to-end continuity

The system MUST support the complete chain from opportunity and mandate through evidence, recommendation, implementation, outcome and benefit.

Acceptance: every material recommendation can be traversed through stable records to evidence and forward to implementation and benefit records.

### OUT-004 — Replaceable runtimes

Model providers, agent harnesses, collaboration shells and coding agents MUST remain replaceable without migrating canonical engagement truth.

Acceptance: canonical records are stored in offdata-controlled APIs and databases, not provider chat history.

## 3. Lifecycle and engagement control

### LIFE-001 — Thirteen stages

The system MUST represent:

1. Mandate and intake.
2. Context and problem definition.
3. Research and evidence baseline.
4. Hypotheses and issue architecture.
5. Methodology and approach design.
6. Proposition and proposal.
7. Mobilisation.
8. Delivery and analysis.
9. Quality review and decision readiness.
10. Implementation and adoption.
11. Benefits realisation.
12. Closeout and knowledge capture.
13. Expansion and follow-on.

### LIFE-002 — Earliest unmet gate

Current stage MUST be determined by the earliest unmet mandatory gate, not by the document currently being produced.

### LIFE-003 — Compression without silent skipping

Stages MAY be compressed only when their minimum outputs and gate intent are evidenced in an approved combined record.

### LIFE-004 — Regression

A material new fact, invalidated assumption, scope change or failed quality gate MUST be able to return an engagement to the earliest affected stage.

### LIFE-005 — Operational state

Every active engagement MUST have exactly one operational state: `normal`, `waiting`, `blocked`, `retry`, `cancelled` or `completed`.

### LIFE-006 — Next best action

The system MUST prioritise harm prevention, mandate clarity, material evidence gaps, blockers, discriminating tests, numerical reconciliation, feasibility and presentation in that order unless binding requirements override it.

### LIFE-007 — Durable recovery

A workflow MUST resume after process interruption without repeating completed non-idempotent actions.

### LIFE-008 — Retry budget

Retries MUST be bounded, logged and stopped when the remaining issue is material or the configured budget is exhausted.

### LIFE-009 — Kill switch

The Founder MUST be able to pause or stop an engagement, agent, integration or external-action class immediately.

## 4. Decision authority and autonomy

### AUTH-001 — Multiple classification

Every proposed material action MUST be classified against all applicable classes: routine, material, external, commercial, legal/regulatory and irreversible. The strictest applicable control governs.

### AUTH-002 — Routine internal action

Reversible internal work within an approved brief MAY execute automatically when permissions and evidence conditions are met.

### AUTH-003 — Material judgement

The system MAY analyse and recommend a material choice but MUST obtain Founder or delegated accountable-human approval before commitment.

### AUTH-004 — External action

External communication, publication, upload, submission or representation MUST NOT occur without explicit authority.

### AUTH-005 — Commercial commitment

Price, fee, liability, scope, deadline, staffing, procurement or payment commitments require a Founder gate.

### AUTH-006 — Legal and regulated judgement

The system MUST NOT issue AI-only legal, tax, audit, securities, investment, safety or regulatory conclusions. Qualified review is required where judgement is involved.

### AUTH-007 — Irreversible action

Destructive changes, one-way disclosures, public announcements, terminations, binding votes and production cutovers MUST NOT execute autonomously.

### AUTH-008 — No self-approval

The creator of a material element MUST NOT be its sole approver. High-assurance review requires an isolated review context and, where appropriate, a different model configuration or qualified human.

### AUTH-009 — Founder interruption packet

Founder interruption MUST contain only: decision and deadline; reason reserved; facts, gaps and assumptions; viable options; consequences; recommendation; resulting commitment; and fallback.

### AUTH-010 — No nuisance interruption

The system SHOULD NOT interrupt merely to report progress, ask a non-material aesthetic preference, transfer analysis work or seek reassurance.

## 5. Canonical records and traceability

### DATA-001 — Stable identity

Every material record MUST have a stable ID that is never reused.

### DATA-002 — Tenant and engagement scope

Client records MUST include tenant and engagement scope and MUST be isolated from other engagements.

### DATA-003 — Versioning

Material records and released artefacts MUST be versioned with actor, timestamp and reason for change.

### DATA-004 — Audit events

Material actions, approvals, agent runs, tool calls and external actions MUST generate correlated audit events.

### DATA-005 — Truth chain

The system MUST support the path:

`opportunity → mandate → decision → question → hypothesis → evidence → analysis → option → recommendation → implementation → outcome → benefit`.

### DATA-006 — Epistemic status

Material working claims MUST distinguish established fact, accepted practice, reasoned synthesis, recommendation, assumption and evidence gap, even when the client-facing surface suppresses those labels.

### DATA-007 — Contradicting evidence

Credible contradicting evidence MUST be recorded, scoped and considered rather than suppressed.

### DATA-008 — Immutable release baseline

Released deliverables MUST reference immutable story, model and evidence baselines.

### DATA-009 — Deletion and retention

Retention, export, archival and deletion MUST be configurable by engagement and jurisdiction.

### DATA-010 — Regional cells

The architecture MUST support future regional deployment cells without cross-region leakage of restricted client content.

## 6. Knowledge and methodology

### KNOW-001 — Original source preservation

Imported source files MUST remain unchanged and be stored with checksum, version, classification, licence and provenance metadata.

### KNOW-002 — Canonical manifest

The system MUST resolve inconsistent filenames and stable-record aliases through a canonical manifest rather than inventing references.

### KNOW-003 — Method record

Each method MUST define decision supported, problem types, prerequisites, inputs, procedure, outputs, strengths, limitations, alternatives, tool needs, evidence burden, failure modes, quality tests and reviewer needs.

### KNOW-004 — Minimum sufficient stack

Method selection MUST choose the smallest non-duplicative stack that addresses the governing uncertainties.

### KNOW-005 — Rejected methods

Materially tempting but unnecessary or invalid methods MUST be recorded with rejection reasons.

### KNOW-006 — Domain overlays

Domain and sector packs MUST alter hypotheses, evidence, methods, tools, metrics, constraints and reviewer needs without pre-deciding the answer.

### KNOW-007 — No automatic promotion

Discovered methodology candidates MUST NOT enter the canonical library without provenance review, original reconstruction, tests and Founder approval.

### KNOW-008 — Copyright control

The system MUST distinguish underlying ideas and methods from protected expression and MUST NOT copy proprietary wording, templates or distinctive diagrams.

### KNOW-009 — Scheduled Methodology Radar

The system SHOULD support scheduled discovery, deduplication, novelty assessment, candidate drafting and controlled release.

### KNOW-010 — Source volatility

Time-sensitive methods, standards and regulatory guidance MUST have review cadence and supersession triggers.

## 7. Research and evidence

### EVID-001 — Decision-linked research

Research MUST be driven by decision-linked questions and hypotheses, not broad topic collection.

### EVID-002 — Source admission

Every admitted source MUST record issuer, title, date, retrieval date, type, access basis, scope, limitations and usage rights.

### EVID-003 — Passage-level provenance

Material claims MUST link to exact source passages, client records or named model outputs.

### EVID-004 — Search snippet limitation

Search-result snippets MUST NOT be treated as sufficient evidence for material conclusions.

### EVID-005 — Source scope

A citation supports only the proposition assigned to it; title similarity is insufficient.

### EVID-006 — Evidence threshold

Evidence burden MUST increase with materiality, external reliance, commercial consequence, legal/regulatory judgement and irreversibility.

### EVID-007 — Staleness

The system MUST identify date-sensitive claims, superseded sources, broken links and changed source status.

### EVID-008 — Research stopping

Research SHOULD stop when expected decision value from further evidence is lower than its cost, delay or commitment impact, subject to minimum evidence gates.

### EVID-009 — Client-facing citation mode

Client deliverables MAY use concise source notes, appendices and linked notes while the internal evidence ledger remains complete.

### EVID-010 — Untrusted input

Uploaded documents and retrieved pages MUST be treated as untrusted input and isolated from system instructions.

## 8. Analysis and modelling

### MODEL-001 — Deterministic calculation

Material calculations MUST run through reproducible code, formulae or controlled models rather than free-form language-model arithmetic.

### MODEL-002 — Reproducibility

Analysis runs MUST record code, environment, dependencies, inputs, assumptions, parameters, random seeds, outputs and diagnostics.

### MODEL-003 — Baseline and counterfactual

Value and causal analysis MUST distinguish baseline, counterfactual, gross impact, leakage, cost, timing, attribution and realised benefit.

### MODEL-004 — Scenario and sensitivity

Material recommendations MUST be tested under decision-relevant downside, upside, break-even and switching conditions.

### MODEL-005 — Reconciliation

Model inputs and outputs MUST reconcile to controlled data and named outputs.

### MODEL-006 — Independent verification

Material models require independent recalculation or verification proportionate to intended-use risk.

### MODEL-007 — Spreadsheet architecture

Generated workbooks MUST separate inputs, calculations, outputs and checks and MUST avoid unexplained hard-coded values.

### MODEL-008 — Units and rounding

Units, periods, denominators, currencies, inflation treatment and rounding MUST be explicit and consistent.

### MODEL-009 — Failure visibility

Missing data, model failure, uncertainty and limitations MUST be surfaced rather than hidden.

## 9. Agents and tools

### AGENT-001 — Bounded role

Every agent MUST have a stable version, purpose, typed inputs and outputs, tool permissions, prohibited actions, data scope, evidence rules, escalation rules, budgets and evaluations.

### AGENT-002 — Context compiler

Agents MUST receive a minimum-sufficient context package rather than the entire knowledge base or engagement history by default.

### AGENT-003 — Canonical writes

Agents MUST write through controlled APIs and MUST NOT treat conversational memory as canonical truth.

### AGENT-004 — Permission enforcement

Tool access and record access MUST be enforced deterministically where practical.

### AGENT-005 — Structured envelope

Agent outputs MUST use typed envelopes with status, summary, artefacts, record changes, assumptions, gaps, escalation and notes for the next actor.

### AGENT-006 — Cost and time budget

Every run MUST have configurable model, token, cost, timeout and retry limits.

### AGENT-007 — Injection resistance

Agents MUST be tested against prompt injection, tool misuse, malicious documents and data exfiltration.

### AGENT-008 — Provider routing

The system SHOULD route by task complexity, evidence risk, latency and cost while preserving output contracts.

### AGENT-009 — Replaceability

No production workflow may depend on undocumented behaviour unique to one chat product or harness.

## 10. Quality and release

### QA-001 — Decision relevance before polish

A polished artefact that does not support the intended decision MUST fail.

### QA-002 — Proportionate assurance

Every deliverable receives a quality gate; assurance depth and independence increase with consequence and complexity.

### QA-003 — Defect record

Critique MUST name the object, defect, consequence, repair and re-test.

### QA-004 — Severity

Defects MUST be assigned severity and blocking status; material defects block release unless an authorised exception is recorded.

### QA-005 — Repair loop

Repairs MUST create a new version, preserve the original review record and rerun targeted regression tests.

### QA-006 — Exception record

Exceptions MUST document unmet rule, reason, alternatives, residual risk, compensating controls, expiry, authority and evidence of acceptance.

### QA-007 — Independent sign-off

Sign-off MUST record artefact checksum, reviewer competence, independence, scope, tests, limitations and conclusion.

### QA-008 — Same-model limitation

Same-model critique MAY support repair but MUST NOT be represented as independent sign-off for high-consequence work.

### QA-009 — Golden fixtures

Synthetic and sanitised exemplars MUST serve as regression tests, not canned answers or client facts.

## 11. Storyline, deliverables and infographics

### DELIV-001 — Shared semantic story

PPTX, DOCX, XLSX, PDF, SVG and HTML MUST derive from one approved story model.

### DELIV-002 — Assertion-led structure

Executive pages and slides SHOULD use decision-relevant assertions rather than topic labels.

### DELIV-003 — Cross-format reconciliation

Headlines, assumptions, numbers, recommendations, roadmap actions, sources and versions MUST reconcile across released formats.

### DELIV-004 — Native editability

Labelled consulting diagrams SHOULD be editable native shapes or SVG where practical.

### DELIV-005 — Infographic grammar

The system MUST support at least maturity curves, radial frameworks, layered stacks, causal narratives, driver trees, roadmaps, journeys, process flows, governance models and operating models.

### DELIV-006 — Raster-image limitation

Generated raster images SHOULD be used mainly for conceptual or decorative illustration, not as the sole representation of complex labelled analysis.

### DELIV-007 — Visual QA

Deliverables MUST be tested for clipping, overlap, font size, contrast, reading order, stale page numbers, hidden notes, broken links and accessibility.

### DELIV-008 — Number source

Displayed material numbers MUST resolve to approved named model outputs or controlled source records.

### DELIV-009 — Citation proportionality

Source notes MUST remain decision-useful and proportionate while full provenance remains available internally.

### DELIV-010 — Release status

Every exported artefact MUST display status, version, confidentiality and approval state as appropriate.

## 12. Implementation and benefits

### IMPL-001 — Recommendation trace

Every implementation initiative MUST trace to an approved recommendation and intended outcome.

### IMPL-002 — Executable record

Initiatives MUST include owner, outputs, observable milestones, dependencies, resources, costs, acceptance criteria, risks and controls.

### IMPL-003 — Adoption distinction

The system MUST distinguish intervention failure from implementation or adoption failure.

### IMPL-004 — Benefit distinction

Project outputs and go-live events MUST NOT be labelled as realised benefits without verified outcome evidence.

### IMPL-005 — Benefit ownership

Every material benefit MUST have owner, baseline, counterfactual, timing, attribution method and verification threshold.

### IMPL-006 — Scale/adapt/stop

Implementation and benefits evidence MUST support explicit scale, adapt, pause or stop decisions.

## 13. CRM and origination

### CRM-001 — CRM boundary

The CRM owns organisations, contacts, opportunities, activities, meetings, pipeline and commercial continuity. offdata owns engagement reasoning, evidence, models, decisions, deliverables and benefits.

### CRM-002 — Stable linkage

CRM and offdata records MUST share stable external identifiers and controlled summary fields.

### CRM-003 — Confidentiality boundary

Detailed confidential evidence and analysis MUST NOT be synchronised into the CRM by default.

### ORIG-001 — Opportunity dossier

Each detected opportunity SHOULD record trigger, evidence, problem hypothesis, alternatives, likely buyer, proposed diagnostic, value, confidence and next action.

### ORIG-002 — Outreach approval

New campaigns, jurisdictions, propositions and external sends require policy checks and Founder approval until a later explicit delegation.

### ORIG-003 — Consent and suppression

Contact source, consent or lawful-use basis, suppression, objection and frequency controls MUST be recorded.

### ORIG-004 — No misrepresentation

Automated outreach MUST NOT misrepresent identity, evidence, credentials, client results or the degree of human involvement.

## 14. Security and operations

### SEC-001 — Secret handling

Secrets MUST NOT be committed, pasted into chat or stored in test fixtures.

### SEC-002 — Least privilege

Users, agents, tools and integrations MUST receive the minimum permissions required.

### SEC-003 — Environment separation

Development, staging and production MUST be separated.

### SEC-004 — Encryption

Client data MUST be encrypted in transit and at rest in non-local environments.

### SEC-005 — Singapore first region

The first managed environment MUST use a Singapore data region where the selected providers support it.

### SEC-006 — Backup and restore

Production readiness requires tested backup and restoration.

### SEC-007 — Processor register

Every third-party processor MUST record purpose, data exposure, region, retention, subprocessors, credentials, cost and exit plan.

### SEC-008 — Supply-chain review

External skills, hooks and packages MUST be version-pinned, licence-recorded and reviewed before project or global installation.

### SEC-009 — Monitoring

Material errors, security events, cost anomalies and failed workflows MUST generate observable alerts.

### SEC-010 — Incident and rollback

Every production change MUST have rollback instructions and incident ownership.

## 15. Testing and measurement

### TEST-001 — Test hierarchy

The system MUST include unit, type, integration, recovery, agent, consulting-quality, artefact, security, end-to-end and Founder-acceptance tests.

### TEST-002 — Thirteen primary fixtures

The suite MUST include corporate strategy, growth, cost/productivity, customer experience, operating model, organisation/workforce, digital/AI, risk/controls, M&A/integration, carve-out/separation, IPO/capital strategy, implementation/change and benefits/performance engagements.

### TEST-003 — Compound fixtures

The suite SHOULD include cross-domain cases with conflicting evidence and dependencies.

### TEST-004 — False-positive and false-negative traps

Evaluation sets MUST test both over-rejection and under-detection of defects, contradictions and materiality.

### TEST-005 — Repeatability

Deterministic ingestion and calculation tests MUST produce stable outputs; agent evaluations MUST measure variance across repeated runs.

### TEST-006 — Workload measure

Pilots MUST measure Founder time, system time, correction effort, task offload, cost, reliability and output quality.

## 16. Cost and commercial readiness

### COST-001 — Local-first

Development SHOULD use local services and free tiers until a managed environment is justified.

### COST-002 — Spend control

Model and infrastructure usage MUST have budgets, metering and alerts before production use.

### COST-003 — Cost attribution

Cost SHOULD be attributable by engagement, agent, model, tool and artefact.

### COST-004 — Paid dependency decision

A paid service requires a documented benefit, alternative, trial plan, cancellation method and Founder approval.

## 17. Initial release priorities

The first controlled pilot release MUST prioritise:

1. Canonical knowledge ingestion.
2. Engagement record and lifecycle.
3. Founder approvals.
4. Research and evidence traceability.
5. Deterministic analysis.
6. Storyline and PPTX/DOCX/XLSX/HTML production.
7. Independent QA.
8. One synthetic AI-audit engagement.

CRM automation, autonomous outreach, Methodology Radar, OpenClaw, Hermes and Buzz remain subordinate to a stable engagement kernel.
