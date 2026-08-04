# AGENTS.md — Controlling Instructions for Codex and All Engineering Agents

## 1. Authority

This file is the controlling instruction for all automated work in this repository. When instructions conflict, use this order:

1. Applicable law, platform safety controls and explicit Founder instructions.
2. This `AGENTS.md`.
3. Approved architecture and decision records.
4. Approved phase requirements and acceptance criteria.
5. Other repository documentation.
6. Agent judgement.

Do not use `rayrayxing/offdata` or `rayrayxing/offdata-clean` as specifications. They are historical references only.

## 2. Mission

Build offdata as a Founder-governed, AI-native consulting operating system that can execute most analyst, consultant and engagement-management work across strategy, growth, operations, organisation, technology, transactions, risk, implementation and benefits realisation.

The system must increase Founder leverage without transferring accountability for material decisions, client commitments, legal positions, commercial terms or irreversible external actions to an AI system.

## 3. Founder operating context

- Founder is non-technical.
- Founder uses macOS.
- Founder owns `offdata.com` through GoDaddy.
- Founder is currently based in Singapore.
- Initial user count is one.
- Initial client data region is Singapore, with future regional deployment cells where residency requirements demand it.
- Initial budget is lean: local-first and free-tier-first until commercialisation.
- Initial tests use synthetic or sanitised data only.

Communicate with the Founder in plain English. Never require the Founder to write code, interpret stack traces or perform terminal work that an agent can safely perform.

## 4. Build method

1. Work on one approved phase at a time.
2. Inspect the repository and current phase before changing anything.
3. Write a concise implementation plan.
4. Create a branch for material work.
5. Implement in small, reviewable commits.
6. Run all required tests.
7. Perform a separate review pass with isolated context where practical.
8. Repair defects without weakening tests.
9. Open a draft pull request.
10. Stop at the phase gate and provide a Founder report.

Do not proceed to the next phase without explicit Founder approval.

## 5. Mandatory Founder report

Every phase or material task must end with:

- What was built or changed.
- Why it was needed.
- Tests performed and results.
- Screenshots or artefact samples where relevant.
- Unresolved defects and risks.
- Costs incurred and forecast costs.
- Credentials, subscriptions or approvals required.
- Rollback instructions.
- Recommended next action.

## 6. Prohibited autonomous actions

Agents must not autonomously:

- Purchase services or accept paid trials.
- Enter payment details.
- Create or reveal credentials.
- Ask the Founder to paste secrets into chat, issues, source files or screenshots.
- Change DNS or domain records.
- Deploy a production system containing real client data.
- Send client or prospect communications.
- Conduct unrestricted bulk outreach.
- Make commercial promises, pricing commitments or contractual representations.
- Give substantive legal, tax, audit, securities, investment or regulatory opinions.
- Copy proprietary consulting templates, distinctive diagrams or confidential materials.
- Promote self-generated methodology directly into the canonical library.
- Merge a material pull request without Founder approval.
- Disable, delete or weaken tests to obtain a passing result.
- Edit golden fixtures solely to make a test pass.
- Mix confidential client data across engagements.
- Use unrestricted computer access when a narrower permission will work.

## 7. Approval classes

### Class A — autonomous internal work

Examples: local code changes, tests, synthetic fixtures, documentation, internal research drafts, local development environments and reversible refactoring.

### Class B — notify Founder

Examples: adding a free dependency, changing a non-material interface, increasing test runtime or adopting a reversible internal convention.

### Class C — Founder approval required before execution

Examples: creating billable resources, enabling third-party access, OAuth consent, API keys, DNS changes, external messages, production deployment, material architecture changes, new data processors and changes to retention or security policy.

### Class D — prohibited or specialist-controlled

Examples: unlawful processing, misrepresentation, credential circumvention, regulated professional conclusions without qualified approval, copying protected expression and bypassing client information barriers.

## 8. Architecture principles

- offdata owns the engagement control plane and canonical state.
- Agent runtimes, model providers, coding harnesses and collaboration shells must remain replaceable.
- Initial architecture should support Next.js, Python/FastAPI, PostgreSQL, object storage, typed agent contracts and durable workflow execution.
- OpenClaw, Hermes, Buzz, Codex, Claude Code, Pi and similar tools may be integrated only through bounded interfaces.
- Model memory is convenience context, never canonical engagement truth.
- Deterministic services perform calculations, transformations and validations.
- Language models may interpret, synthesise, draft and critique, but must not fabricate calculations.
- External side effects require idempotency, audit logging and policy checks.
- Singapore is the first deployment region; future regional cells must preserve tenant and data-residency separation.

## 9. Data and security rules

- Never commit secrets.
- Use `.env.example` with placeholders only.
- Use approved secret managers for non-local environments.
- Enforce least privilege.
- Enforce MFA where supported.
- Encrypt data in transit and at rest.
- Maintain immutable or tamper-evident audit records for material actions.
- Separate development, staging and production.
- Use synthetic data until the production security gate passes.
- Treat uploaded documents as untrusted input and test for prompt injection and malicious content.
- Log access to client records and generated deliverables.
- Make retention, export and deletion configurable by engagement and jurisdiction.

## 10. Consulting truth model

Every material recommendation should be internally traceable through:

`decision → question → hypothesis → evidence → analysis → option → recommendation → implementation → benefit`

Maintain explicit records for:

- Facts.
- Assumptions.
- Evidence gaps.
- Contradicting evidence.
- Confidence.
- Falsifiers.
- Decisions.
- Approvals.
- Defects.
- Versions.

Client-facing outputs may use concise citations and appendices. Internal provenance must remain complete.

## 11. Methodology rules

- Begin with the decision, uncertainty, unit of analysis and evidence burden—not a fashionable framework.
- Select the minimum sufficient method stack.
- Record rejected methods and reasons when material.
- Preserve source provenance for external ideas.
- Reconstruct reusable methods independently and in original expression.
- Do not promote methodology candidates without review, tests and Founder approval.
- Domain packs modify method selection, evidence requirements, tools and reviewer needs; they do not create separate monolithic consultant agents.

## 12. Agent rules

Every production agent requires:

- A bounded purpose.
- Typed inputs and outputs.
- Permitted and prohibited tools.
- Data-access scope.
- Evidence requirements.
- Escalation rules.
- Retry and cost limits.
- Evaluation cases.
- Audit logging.

An agent cannot be the sole approver of its own material work. Independent review means a separate run, context, rubric or model configuration sufficient to reduce shared-error risk.

## 13. Deliverable rules

- Render PPTX, DOCX, XLSX, PDF, SVG and HTML from a shared semantic engagement model.
- Ensure numbers and wording reconcile across surfaces.
- Build labelled consulting diagrams as editable native shapes or SVG where practical.
- Use generated raster imagery mainly for decorative or conceptual illustration.
- Preserve detailed provenance internally while keeping client-facing citations proportionate.
- Test layout, clipping, contrast, font size, formula integrity, accessibility and rendering.

## 14. Testing rules

Required layers:

1. Unit and type tests.
2. Integration and database tests.
3. Workflow recovery and idempotency tests.
4. Agent evaluations.
5. Consulting-quality evaluations.
6. Artefact rendering and reconciliation tests.
7. Security and isolation tests.
8. Synthetic end-to-end engagement tests.
9. Founder acceptance tests.

No material phase is complete with failing required tests.

## 15. Cost discipline

- Prefer local tools and free tiers during development.
- Do not introduce paid infrastructure without a cost and benefit note.
- Add usage metering and spend caps before enabling production model calls.
- Route simple tasks to lower-cost models and reserve premium models for material synthesis or review.
- Record cost by engagement, agent, model and artefact.

## 16. Stop conditions

Stop and escalate when:

- Requirements are materially ambiguous.
- A requested action requires credentials, payment, OAuth or external approval.
- A legal, privacy, security or copyright concern is unresolved.
- Tests and expected results conflict.
- Golden fixtures appear wrong.
- A change risks loss or corruption of data.
- A dependency requires a material architecture change.
- The work would cross the approved phase boundary.
