# PCFA-05 — Minimum Valuable Consulting Loop

## Purpose

PCFA-05 defines the minimum end-to-end consulting loop that offdata must be able to execute before it can claim the product is operationally useful as a consulting operating system.

This is a chat-first specification package. It does **not** implement the workflow runtime, product UI, agents, analytical services, renderers, CRM integrations or production infrastructure. Every PCFA-05 stage remains `planned_not_implemented` until later IMP work supplies registered tests and implementation evidence.

The machine authority is `repository/pcfa05-minimum-valuable-consulting-loop.json`, generated from `configs/pcfa05-minimum-valuable-consulting-loop.yaml`.

## Minimum loop

The required truth-bearing sequence is:

`opportunity → mandate → engagement → decision framing → hypothesis tree → research plan → evidence → claim ledger → method → analysis and value → options → recommendation → Founder decision → storyline → deliverables → independent QA → implementation initiatives → benefits → closeout`

The sequence is deliberately more explicit than a generic project lifecycle. It encodes the consulting truth model into an executable future workflow so that the system cannot jump from an intake prompt directly to a recommendation or deliverable without the governed intermediate records.

### 1. Opportunity

Establish a governed opportunity or internal consulting need, preserving source context, relationship continuity and the initial fit/value hypothesis.

### 2. Mandate

Create the governed mandate packet: decision, owner, scope, constraints, evidence standard, key gaps and the material commitment boundary. The Founder is required for material mandate or scope commitment.

### 3. Engagement

Create one stable engagement identity, tenancy boundary, lifecycle instance and accountable-Founder link. The Engagement Workspace must remain a view over this canonical state rather than a second store.

### 4. Decision framing

Record decision questions, criteria, uncertainty and unit of analysis. A material change to the governing frame can trigger Founder review.

### 5. Hypothesis tree

Create the issue architecture, testable hypotheses, rival explanations, falsifiers and evidence needs.

### 6. Research plan

Define the source strategy, stopping criteria, access scope and evidence-quality expectation before broad acquisition begins.

### 7. Evidence

Acquire and preserve source evidence with original versions, provenance locators, access controls and quarantine behaviour for malformed or malicious inputs.

### 8. Claim ledger

Record material claims with support, contradiction, confidence, gaps and falsifiers. Contrary evidence must remain visible.

### 9. Method

Select the minimum sufficient method stack, record dependencies and justify material rejected alternatives.

### 10. Analysis and value

Execute governed deterministic analysis, value modelling, scenarios and sensitivities with reproducibility metadata.

### 11. Options

Develop credible alternatives with explicit trade-offs, risks, dependencies and reversibility.

### 12. Recommendation

Form the answer-first recommendation with rationale, value linkage, risk summary, actions and success conditions.

### 13. Founder decision

Present an exact-version decision packet. The Founder can approve, reject, recycle, pause or stop. Any material change after approval makes the approval stale.

### 14. Storyline

Translate the approved recommendation into a governing thought, proposition hierarchy, section contracts and visual plan without changing canonical meaning.

### 15. Deliverables

Render PPTX, DOCX, XLSX, PDF, SVG and HTML as applicable from shared semantic state. Deliverable files do not become independent truth stores.

### 16. Independent QA

A separate review context tests evidence, calculations, consulting craft, rendering, cross-format reconciliation, blocking defects and release readiness. A creator cannot be the sole approver of its own material work.

### 17. Implementation initiatives

Translate approved recommendations into governed initiatives, owners, milestones, dependencies, adoption measures and delivery evidence.

### 18. Benefits

Track outcomes and realised benefits against approved baselines, counterfactuals, owners and verification methods. The Founder controls scale/adapt/stop decisions.

### 19. Closeout

Close with a complete audit trail, engagement archive, lessons, method candidates, retention disposition and explicit Founder closure. Method candidates are not automatically promoted to the canonical library.

## Global invariants

The future implementation must preserve all of the following across the entire loop:

1. one stable engagement ID;
2. one canonical state, with model/runtime memory noncanonical;
3. traceability for every material claim;
4. reproducibility for every material number;
5. retention of contrary evidence, gaps and falsifiers;
6. justified method selection and rejected material alternatives;
7. idempotent command and side-effect handling;
8. Founder approval bound to the exact version/action/scope;
9. restart-safe durable checkpoints;
10. independent QA before material release or decision;
11. cross-format reconciliation from one semantic source;
12. recommendation → implementation → benefit traceability;
13. complete material audit history;
14. Founder control to recycle, pause, cancel or stop; and
15. no sole self-approval by the creator context, agent, worker or model.

These invariants are product requirements, not implementation suggestions. PCFA-07 must map each invariant to concrete planned test IDs and blocking phase gates.

## Founder interrupts

The Founder remains accountable for material decisions rather than becoming a passive observer of an autonomous workflow.

PCFA-05 therefore defines six interrupt classes: material mandate/scope commitment; material evidence, method, risk or external-access exception; recommendation decision; artefact release after independent QA; benefit scale/adapt/stop decision; and a discretionary control available across every stage.

The Founder can recycle work to the affected prior stage. The workflow must preserve the reason, prior evidence, versions and completed effects when this occurs. The Founder can recycle, pause, cancel or stop at any stage; cancellation prohibits further execution until a new governed action explicitly starts something else.

## Transition semantics

Forward sequence is required by default. Stage skipping is not the default behaviour.

Recycle is allowed only to the affected prior stage with an auditable reason. Pause/resume requires a durable checkpoint. Blocking defects prevent release. A stale approval prevents resume. Duplicate effects are prohibited even when commands or workflow steps are replayed.

Supported terminal control states are `completed`, `cancelled`, `blocked` and `paused`.

## Required negative-path programme

A happy-path synthetic engagement is insufficient. The future test programme must explicitly prove behaviour for:

- missing material evidence;
- material contradicting evidence;
- approval wait;
- stale approval after a material change;
- restart after checkpoint;
- duplicate command/action replay;
- Founder cancellation;
- blocking independent-QA defect and recycle;
- cross-engagement access attempt;
- malicious or instruction-bearing documents;
- provider or agent-runtime failure;
- numeric/formula defect; and
- renderer or cross-format reconciliation defect.

The expected response is fail-closed and auditable. None of these cases may silently downgrade evidence quality, mutate canonical truth from runtime memory, duplicate effects or release a materially defective artefact.

## Relationship to existing authority

### `AGENTS.md`

PCFA-05 operationalises the existing consulting truth model and preserves Founder accountability, evidence traceability, deterministic calculations, independent review and no-self-approval rules.

### Northstar integration blueprint

The existing Northstar blueprint remains valid as the broader 13-stage architecture and integration blueprint. PCFA-05 does not replace it. Instead it introduces a more explicit minimum consulting truth loop inside the same canonical engagement, workflow, agent, evidence, analytical, deliverable, QA and benefits components.

The accepted Northstar restart, approval-wait, blocking-QA recycle, idempotent replay, Founder cancellation and tenant-boundary cases remain mandatory predecessors and are cross-checked by the PCFA-05 validator.

### PCFA-04 product-scope addendum

PCFA-05 fulfills the PCFA-04 requirement for an explicit Minimum Valuable Consulting Loop and consumes the same Mandate, Engagement Workspace, QA, review, Office round-trip, implementation and benefits concepts. It does not create parallel product stores or new implementation phases.

### IMP backlog

All 19 stages bind only to existing IMP-P1 through IMP-P12 tasks. There is no new product-runtime work in IMP-P0. PCFA-07 must later replace family-level planning with exact requirement/stage/invariant/negative-case → task → test → evidence → dependency → phase-gate registration.

## Acceptance for PCFA-05

PCFA-05 is repository-complete only when all of the following are true:

- governed YAML, JSON schema, generated machine contract and evidence report agree deterministically;
- the exact 19-stage sequence is present;
- all 15 loop invariants are present;
- all six Founder interrupt classes are present;
- all 13 negative-path cases are present;
- every stage references existing IMP tasks and no stage assigns product-runtime ownership to IMP-P0;
- the contract preserves Northstar and PCFA-04 predecessor requirements;
- current operational state and Codex handoff bind the exact PCFA-05 contract digest;
- the launch verifier fails closed if PCFA-05 is missing, drifted, falsely marked implemented, reordered or made permissive;
- all inherited repository validators, runtime tests, coverage, compilation, Ruff and MyPy pass; and
- the exact PR head and merge ref pass the complete workflow matrix with retained evidence.

## Explicit non-implementation boundary

PCFA-05 does not authorise:

- product or workflow runtime implementation;
- Codex Phase 0 implementation;
- a Codex branch;
- merge of this or any dependency PR;
- Phase 1;
- Hermes/runtime activation;
- public distribution;
- real client data;
- paid services, OAuth or credentials;
- DNS changes; or
- staging/production deployment.

`codex_start_authorized=false` remains mandatory.

PCFA-07 global obligation/test reconciliation and PCFA-08 final cross-authority/pre-Codex acceptance remain required after this package.
