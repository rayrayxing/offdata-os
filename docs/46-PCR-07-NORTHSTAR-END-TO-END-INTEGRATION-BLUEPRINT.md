# 46 — PCR-07 Northstar End-to-End Integration Blueprint

## Purpose

PCR-07 turns the existing Northstar AI-audit fixture, analytical oracle, semantic deliverable model, lifecycle, agent system, runtime adapters and governance controls into one deterministic end-to-end integration contract. It is a blueprint only. It does not authorise Codex, activate a runtime, install Hermes, deploy infrastructure or process real client data.

The Northstar fixture is `FIXTURE-DAI-001`. The governing decision is whether Northstar should approve one or two bounded AI interventions, under what operating and control conditions, and what evidence is required before scale. The existing oracle and semantic model remain authoritative restricted evaluation baselines.

## End-to-end path

The blueprint aligns exactly to all thirteen lifecycle stages and `GATE-01` through `GATE-13`:

1. mandate and intake;
2. context and problem definition;
3. research and evidence baseline;
4. hypotheses and issue architecture;
5. methodology and approach design;
6. proposition and proposal;
7. mobilisation;
8. delivery and analysis;
9. quality review and decision readiness;
10. implementation and adoption;
11. benefits realisation;
12. closeout and knowledge capture;
13. expansion and follow-on.

Every stage has a durable checkpoint, a command-only write path, named inputs and outputs, bounded agents, an exit gate and an explicit Founder gate where material authority is required. The workflow must survive restart without replaying completed non-repeatable work.

## Integration topology

Thirteen components are connected by twenty governed edges:

- Founder cockpit and engagement workspace;
- API and policy engine;
- PostgreSQL canonical state;
- immutable object and artefact storage;
- durable workflow adapter;
- typed agent runtime adapter;
- bounded worker harness;
- declared tool runtime;
- knowledge, source and evidence services;
- deterministic analytics;
- semantic story and renderer boundary;
- independent quality and release control;
- implementation and benefits tracking.

Only PostgreSQL structured state and immutable object versions are canonical owners. Workflow checkpoints, agent memory, Hermes memory, tool sessions and chat history are not canonical engagement truth. All material changes pass through validated commands and produce replayable events.

## Northstar execution contract

The target path uses the restricted analytical oracle and `DSM-DAI-001` / `STORY-DAI-001` semantic baselines. Evidence and named analyses feed one versioned story model. Six format plans—PPTX, DOCX, XLSX, PDF, SVG and HTML—must reconcile before release.

Stage 9 requires independent quality, defect disposition, reconciliation and a scoped Founder approval. The only release mode in this blueprint is `internal_synthetic_only`; external client release and external sending remain prohibited.

Implementation and benefits records must preserve initiative owners, milestones, adoption measures, baseline, counterfactual, benefit ownership and verification. Scale, adapt, pause and stop decisions remain Founder-accountable.

## Required scenarios

PCR-07 defines seven end-to-end scenarios:

- synthetic happy path;
- restart after the analysis checkpoint;
- approval wait and resume;
- blocking quality defect and recycle;
- idempotent release replay;
- Founder cancellation;
- tenant or real-client-data boundary rejection.

These scenarios ensure the integration is not judged only by a happy path. A restart must resume from the last durable checkpoint; repeated release commands must create one effect; blocking defects must prevent release; cancellation must stop further execution; cross-tenant or real-client-data attempts must be denied and audited.

## Implementation waves

Eight ordered waves define the later Codex integration sequence: foundation, canonical state, durable lifecycle, bounded agents, evidence and analytics, semantic delivery, independent quality and release, then implementation and benefits. Each wave has a completion gate, and no wave may bypass its dependency.

The blueprint does not change the governed Phase 0 handoff. Codex may start only after all existing PCR-03 through PCR-06 merge and hosted-control conditions are satisfied, a clean macOS environment is available, and the Founder explicitly approves Phase 0. Northstar implementation requires a later explicit phase authorisation.

## Acceptance boundary

Completion requires deterministic fixture loading, all thirteen lifecycle stages, restart recovery, idempotent effects, evidence and number traceability, isolated independent quality, scoped Founder approval, six-surface reconciliation, tenant isolation, correlated audit history and verifiable benefits.

The following remain false:

- `runtime_activation_authorized=false`;
- `hermes_activation_authorized=false`;
- `codex_start_authorized=false`;
- `northstar_implementation_authorized=false`.

Founder accountability is preserved. Real client data, external actions, production deployment, paid services and autonomous merge remain prohibited. Rollback must not weaken any earlier governance, evidence, security, runtime or compatibility contract.
