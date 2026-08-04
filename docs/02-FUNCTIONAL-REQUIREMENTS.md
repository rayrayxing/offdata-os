# 02 — Functional Requirements

## 1. Founder and identity

The system must:

- Support one Founder initially and multiple users later.
- Use strong authentication and MFA.
- Present material decisions in a clear Founder inbox.
- Explain decisions, evidence, risks, costs and recommended action in plain English.
- Allow the Founder to approve, condition, reject, pause, recycle, stop or close work.
- Provide a global kill switch for external actions and agent execution.

## 2. CRM and opportunity management

The system must:

- Maintain organisations, contacts, relationships, activities, opportunities and engagement-conversion history.
- Integrate with HubSpot Free initially without making HubSpot the engagement system of record.
- Detect duplicate organisations and contacts.
- Record consent, suppression and outreach restrictions.
- Preserve stable cross-system identifiers.
- Create opportunity dossiers from approved public sources.
- Route proposed outreach through policy and Founder approval.

## 3. Mandate and engagement intake

The system must:

- Convert notes, transcripts and documents into a first-cut mandate without demanding non-material clarification first.
- Identify the decision owner, decision date, scope, constraints, known options and required standard of proof.
- Distinguish facts, assumptions, gaps and proposed interpretations.
- Identify likely engagement types and compound-domain needs.
- Generate a structured brief, initial hypothesis set, data request and engagement plan.

## 4. Lifecycle and gates

The system must:

- Track a controlled engagement state from opportunity through closeout and benefits.
- Define entry criteria, required records, exit criteria and gate outcomes for each stage.
- Support retries, waiting, blocking, recycling and cancellation.
- Resume safely after interruption.
- Prevent duplicate external actions.
- Maintain a complete stage and approval history.

## 5. Problem framing and hypothesis management

The system must:

- Create decision statements, problem statements and issue/question/hypothesis structures.
- Distinguish descriptive, predictive, causal and normative claims.
- Maintain alternatives and falsification tests.
- Link hypotheses to required evidence and analyses.
- Update claims and confidence when contrary evidence appears.
- Record what would change the recommendation.

## 6. Method selection

The system must:

- Match decisions and problem archetypes to methods.
- Select minimum sufficient method stacks with distinct roles.
- Record prerequisites, inputs, outputs, limitations and required tools.
- Detect incompatible, redundant or superficial framework combinations.
- Record rejected methods and reasons when material.
- Dynamically load domain overlays without duplicating the core lifecycle.

## 7. Research and evidence

The system must:

- Build research mandates and question trees.
- Search approved internal and external sources.
- Preserve source location, date, access basis and usage rights.
- Link evidence to claims and analyses.
- Record supporting, neutral and contradicting evidence.
- Assign evidence quality and confidence.
- Identify stale, broken or scope-mismatched sources.
- Support concise client-facing citations and complete internal provenance.

## 8. Quantitative analysis and value modelling

The system must:

- Execute reproducible calculations in governed analytical runtimes.
- Separate inputs, assumptions, transformations and outputs.
- Support financial, operational, statistical, causal, optimisation, simulation and uncertainty methods.
- Produce scenario and sensitivity analysis.
- Reconcile figures across models and deliverables.
- Block unexplained hard-coded values.
- Label missing data rather than fabricating estimates.

## 9. Storyline and recommendation

The system must:

- Develop a governing thought and decision-first storyline.
- Express slide and section titles as assertions where appropriate.
- Link recommendations to evidence, options, trade-offs and implementation.
- Preserve alternative views and unresolved uncertainties.
- Reconcile terminology and numbers across all surfaces.

## 10. Deliverables and infographics

The system must:

- Generate PPTX, DOCX, XLSX, PDF, SVG and interactive HTML.
- Use a canonical semantic story model.
- Produce editable diagrams for labelled consulting concepts.
- Support maturity curves, radial frameworks, layered stacks, causal chains, value trees, roadmaps, process flows, operating models, journeys, portfolios, governance models and other visual archetypes.
- Validate layout, clipping, readability, contrast, formulas, accessibility and cross-format consistency.
- Preserve detailed provenance internally without cluttering client outputs.

## 11. Quality assurance

The system must:

- Apply deterministic checks, rubric-based review, red teaming and release gates.
- Prevent creators from solely approving their own material work.
- Classify defect severity and blocking status.
- Repair defects and rerun affected tests.
- Retain all review findings, dispositions and waivers.
- Compare outputs against synthetic exemplars and golden expectations.

## 12. Implementation and benefits

The system must:

- Translate recommendations into initiatives, owners, milestones, dependencies, acceptance criteria and controls.
- Separate delivery completion, adoption, operational outcomes and benefit realisation.
- Link benefit claims to baselines, causal logic, costs and owners.
- Support pilots, waves, shadow mode, parallel runs and risk-tiered deployment.
- Continue tracking until benefits are verified or formally closed.

## 13. Origination

The system must:

- Monitor approved sources for company and market triggers.
- Develop evidence-based opportunity hypotheses.
- Identify likely buyer roles.
- Match opportunities to approved offdata propositions.
- Draft personalised outreach and follow-up.
- Enforce jurisdiction, consent, suppression, frequency and sender policies.
- Require approval before new campaigns or external sending.

## 14. Methodology Radar

The system must:

- Run scheduled scans for new methods, procedures, evaluation designs, modelling approaches, operating practices and visual representations.
- Cover consulting firms, academia, standards bodies, regulators, governments, professional bodies and adjacent disciplines.
- Distinguish genuine methods from renamed concepts or promotional content.
- Locate primary or authoritative support.
- Compare candidates with existing records.
- Draft copyright-safe, original offdata method records.
- Require review and regression testing before promotion.

## 15. Administration and operations

The system must:

- Meter cost by engagement, model, agent and artefact.
- Provide audit logs and operational dashboards.
- Back up and restore data.
- Support export, retention and deletion policies.
- Separate development, staging and production.
- Support Singapore deployment first and future regional deployment cells.
- Allow model, orchestrator and worker replacement through stable contracts.

## 16. Initial non-functional targets

- Local development startup through one documented command.
- Required automated checks on every pull request.
- No secrets committed.
- Synthetic end-to-end fixture completes after interruption and restart.
- All material records are versioned and auditable.
- Engagement isolation tests pass.
- Generated Office files open without repair warnings.
- Founder can understand every required decision without reading code.
