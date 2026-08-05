# offdata OS

**offdata** is a Founder-governed, AI-native consulting operating system designed to execute most analyst, consultant and engagement-management work while preserving human accountability for material decisions, external commitments, commercial choices and client relationships.

This repository is the **canonical build repository** for the new offdata consulting platform. The older `rayrayxing/offdata` and `rayrayxing/offdata-clean` repositories are historical references only and must not be treated as controlling specifications.

## Current status

- Repository stage: chat-first pre-Codex foundation hardened through PCR-03
- Initial operator: Founder only
- Initial hosting/data region: Singapore
- Initial data: synthetic only; real client data remains prohibited
- Engineering execution: Codex, operating through gated phases
- Production orchestrator: not yet approved; the build must preserve replaceability
- Canonical release: Phase 1–7 reconciled by PCR-01
- Test and reference integrity: governed by PCR-02
- Repository and governance hygiene: governed by PCR-03

## Product objective

offdata should support the full consulting lifecycle from qualified opportunity and mandate intake through framing, research, analysis, recommendation, deliverable production, implementation and benefits verification. It should also support controlled origination, CRM continuity, methodology scouting and continuous quality improvement.

## Read order

1. `AGENTS.md`
2. `GOVERNANCE.md`
3. `SECURITY.md`
4. `CONTRIBUTING.md`
5. `docs/00-START-HERE.md`
6. `docs/01-PRODUCT-VISION.md`
7. `docs/02-FUNCTIONAL-REQUIREMENTS.md`
8. `docs/03-ARCHITECTURE.md`
9. `docs/10-TESTING-STRATEGY.md`
10. `docs/11-BUILD-BACKLOG.md`
11. `docs/14-CODEX-KICKOFF.md`
12. `docs/20-DEVELOPMENT-STATUS.md`
13. `docs/42-PCR-03-REPOSITORY-AND-GOVERNANCE-HYGIENE.md`

## Non-negotiable principles

1. **Operational autonomy, not accountability autonomy.** Routine internal work may be automated. Material, external, commercial, legal, irreversible or high-risk actions require Founder approval.
2. **The database is the system of record.** Chat history, model memory and agent sessions are not authoritative engagement truth.
3. **Evidence before assertion.** Material claims must be traceable internally to evidence, analysis, assumptions and review state.
4. **One story, many surfaces.** PPTX, DOCX, XLSX, PDF, SVG and HTML outputs must be rendered from a shared semantic engagement model.
5. **Deterministic calculations.** Models calculate; language models interpret and communicate. Numbers must never be invented by narration.
6. **Independent quality review.** The same agent or context that creates material work cannot be the sole approver of that work.
7. **Client separation.** No cross-engagement retrieval, memory or reuse of confidential client material without explicit authority.
8. **Specification-first, test-first, phase-gated.** Codex must not build ahead of the approved phase.
9. **No secrets in source control or chat.** Credentials are entered only through approved secret-management or OAuth interfaces.
10. **Copyright-safe methodology development.** External ideas may inform independently reconstructed methods; protected wording, diagrams, templates and confidential materials must not be copied.

## Initial build target

The first target is a local, synthetic-data prototype that can complete one end-to-end AI audit engagement, then expand into a permanent fixture suite covering each major engagement type.

## Repository structure

```text
offdata-os/
├── AGENTS.md
├── GOVERNANCE.md
├── SECURITY.md
├── CONTRIBUTING.md
├── docs/
├── configs/
├── repository/
├── requirements/
├── knowledge/
├── fixtures/
├── apps/
├── services/
├── packages/
├── infrastructure/
└── tests/
```

Application and operating-infrastructure directories are populated only through approved implementation phases.
