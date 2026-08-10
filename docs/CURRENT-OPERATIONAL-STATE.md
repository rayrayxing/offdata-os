# Current operational state

This document is the human-readable companion to `repository/current-operational-state.json`.

## Current status

The chat-first specification and reconciliation programme is complete through WS6.16, the permanent Workstream 6 release is valid, PCFA-01 repairs the real Codex Phase 0 launch semantics, PCFA-02 separates retained package-time snapshots from the live operational projection, PCFA-03 resolves repository visibility/licence posture, PCFA-04 defines the missing product-scope implementation addendum, PCFA-05 defines the Minimum Valuable Consulting Loop, PCFA-06 refreshes Hermes bounded-adoption policy against the current public Hermes documentation while retaining the v0.18.2 stable pin, PCFA-07 reconciles all corrective obligations into the existing Codex implementation backlog, and PCFA-08 completes the repository-side final cross-authority acceptance while leaving manual launch gates pending.

All 93 PCFA-04/05/06 obligations reconciled by PCFA-07 remain `planned_not_implemented`. PCFA-07 adds no IMP phase, no backlog task and no IMP-P0 obligation; it claims no product/workflow/Hermes runtime implementation.

`codex_start_authorized=false`.

PCFA-08 final repository-side cross-authority acceptance is complete; manual launch gates remain pending.

No Codex branch, IMP-P0 implementation, merge, IMP-P1, runtime/Hermes activation, public distribution, open-source distribution, external contribution, real client data, paid service, OAuth, DNS change, production deployment or external action is authorized by this state.

## Current machine authority

For current operational decisions, use this order after `AGENTS.md`:

1. `repository/current-operational-state.json` — sole live machine readiness and authority projection;
2. `repository/repository-visibility-and-licence-posture.json` — current PCFA-03 private/internal repository and licence posture;
3. `repository/pcfa04-product-scope-implementation-addendum.json` — current PCFA-04 product-scope implementation obligations;
4. `repository/pcfa05-minimum-valuable-consulting-loop.json` — current PCFA-05 Minimum Valuable Consulting Loop contract;
5. `repository/pcfa06-hermes-bounded-adoption-refresh.json` — current PCFA-06 Hermes bounded-adoption refresh;
6. `requirements/pcfa07-codex-implementation-backlog-reconciliation.json` — current PCFA-07 exact implementation-backlog reconciliation;
7. `repository/pcfa08-final-pre-codex-cross-authority-acceptance.json` — final repository-side cross-authority acceptance and exact 65-branch cleanup contract;
8. `docs/71-PCFA-04-PRODUCT-SCOPE-IMPLEMENTATION-ADDENDUM.md` — human-readable product-scope addendum;
9. `docs/72-PCFA-05-MINIMUM-VALUABLE-CONSULTING-LOOP.md` — human-readable MVCL specification;
10. `docs/73-PCFA-06-HERMES-BOUNDED-ADOPTION-REFRESH.md` — human-readable Hermes bounded-adoption specification;
11. `docs/74-PCFA-07-CODEX-IMPLEMENTATION-BACKLOG-RECONCILIATION.md` — human-readable backlog reconciliation;
12. `docs/75-PCFA-08-FINAL-PRE-CODEX-CROSS-AUTHORITY-ACCEPTANCE.md` — human-readable final repository-side acceptance;
13. `handoff/codex-phase0-current-handoff.json` — current machine execution handoff;
14. `contracts/pcfa01-launch-control-repair.json` — corrected release/launch SHA semantics;
15. `handoff/codex-phase0-current-issue.md` — current Issue #1 body to synchronize after integration;
16. `handoff/codex-phase0-current-hosted-controls-issue.md` — current Issue #19 body to synchronize after integration;
17. `releases/pre-codex-final-reconciliation-2026-08-06.json` — immutable WS6.16 release evidence;
18. `scripts/prepare_codex_phase0_launch.py` — fail-closed launch-permit entrypoint.

The current evidence templates use the neutral `handoff/codex-phase0-current-*` names.

## Repository visibility and licence posture

PCFA-03 resolves the current policy posture as follows:

- required GitHub repository visibility before Codex launch and IMP-P0 implementation: `private`;
- a live public repository is a launch blocker;
- the launch verifier independently queries GitHub repository metadata and cannot be overridden by an attestation;
- licence posture: **no public licence grant**, with machine mode `no_public_licence_grant_proprietary_internal`;
- selected open-source licence: none;
- implicit licence grant: false;
- public/open-source distribution: unauthorized;
- external contributions and client distribution: unauthorized;
- third-party dependencies retain their own licences.

The repository was observed as public when PCFA-03 was prepared on 2026-08-07. That observation is historical evidence only; it does not satisfy the private-visibility gate. The actual hosted setting must be changed to private and independently verified before a launch permit can exist.

The current private/internal posture intentionally does not require a repository `LICENSE` file. Any future public or open-source posture requires explicit Founder approval, a licence ADR, dependency-licence compatibility review, and legal review if material.

## PCFA-04 product-scope implementation addendum

PCFA-04 defines 14 product areas and 29 explicit requirements, all `planned_not_implemented`. The package covers:

- Mandate Intake Workbench;
- explicit Engagement Workspace;
- Quality and Assurance Console;
- Implementation and Benefits Workspace;
- broader ingestion formats and native provenance locators;
- 100% approved canonical-library source accounting;
- 15 Consulting Craft `CQ-*` requirements;
- broader golden-output coverage;
- Office round-trip reconciliation;
- Founder/house-style profile;
- deliverable asset-rights provenance;
- Founder attention burden metrics;
- explicit deliverable variants;
- review/change-request workflow.

The requirements are assigned to existing IMP-P1–P12 integration points. No new product-runtime work is added to IMP-P0. CRM, origination and Methodology Radar remain required to feed the same canonical mandate/engagement/method state rather than introducing new stores.

PCFA-05 fulfills the Minimum Valuable Consulting Loop dependency, and PCFA-07 now reconciles every PCFA-04 requirement, PCFA-05 stage/invariant/negative case/Founder interrupt and PCFA-06 Hermes capability into exact implementation-task, planned-test, evidence, dependency and blocking-phase-gate registrations.

The current operational state directly binds the SHA-256 of `repository/pcfa04-product-scope-implementation-addendum.json`, and the launch entrypoint rejects a missing, permissive or drifted PCFA-04 record.

## PCFA-05 Minimum Valuable Consulting Loop

PCFA-05 defines 19 consulting-loop stages, 15 cross-loop invariants, six Founder interrupt classes and 13 negative-path cases. Every stage remains `planned_not_implemented`.

The loop is `opportunity → mandate → engagement → decision framing → hypothesis tree → research plan → evidence → claim ledger → method → analysis and value → options → recommendation → Founder decision → storyline → deliverables → independent QA → implementation initiatives → benefits → closeout`.

The future runtime must be restart-safe and idempotent, bind approvals to exact versions, retain contrary evidence, reproduce material numbers, keep independent QA separate from creator context, reconcile formats, trace recommendations through implementation to benefits, and preserve Founder recycle/pause/cancel/stop control. PCFA-07 exact obligation/test registration is complete, and PCFA-08 final repository-side cross-authority acceptance is complete; manual launch evidence remains required.

The current operational state directly binds the SHA-256 of `repository/pcfa05-minimum-valuable-consulting-loop.json`, and the launch entrypoint rejects missing, reordered, falsely implemented or permissive MVCL state.

## PCFA-06 Hermes bounded-adoption refresh

PCFA-06 keeps the accepted stable Hermes pin at `v0.18.2` / `v2026.7.7.2` / `9de9c25` and separately snapshots current public Hermes documentation. The documentation snapshot is not treated as proof that every documented feature ships in that stable release.

The refresh records 11 Hermes capability assessments, all `planned_not_implemented`. offdata remains the control plane and canonical system of record. Raw `/goal` is not workflow authority; any future adapter must map completion to `WorkerPackage.acceptance`, use bounded turn budgets, persist checkpoints in offdata and allow Founder interrupts. Raw top-level background delegation, nested delegation and parallel fan-out are denied, with initial adapter concurrency fixed at one.

Hermes skills remain candidates rather than canonical offdata procedures. `/learn` is suggestion-only; `/journey` is read-only observability; curator and automatic skill/method promotion are disabled. Persistent Hermes memory is noncanonical and cannot carry client truth or cross-engagement state. Mixture-of-Agents is candidate-only behind the offdata model router, requires provider/cost/evaluation controls, and does not itself satisfy independent-QA separation.

MCP, tool gateway, unrestricted browser/terminal access, messaging, cron/background sessions and optional Codex app-server runtime remain deferred or denied pending their own processor, credential, data, durability and external-action reviews.

The current operational state directly binds the SHA-256 of `repository/pcfa06-hermes-bounded-adoption-refresh.json`, and the launch entrypoint rejects a missing, activated, background-enabled, learning-promoting or model-router-permissive PCFA-06 state. PCFA-07 carries the exact implementation/test/evidence/dependency/gate reconciliation; PCFA-08 now supplies the final repository-side cross-authority acceptance and exact branch-cleanup evidence contract.

## PCFA-07 Codex implementation backlog reconciliation

PCFA-07 reconciles **93** corrective obligations into the existing IMP backlog: 29 PCFA-04 requirements, 19 MVCL stages, 15 MVCL invariants, 13 MVCL negative cases, six Founder interrupt classes and 11 Hermes bounded-adoption capabilities.

The machine record preserves every original obligation ID and assigns exact existing task bindings, one primary implementation task, component bindings, dependency tasks, a blocking IMP phase gate, one unique `PCFA07-TST-*` planned test identity and an evidence type. All 93 entries remain `planned_not_implemented`, and all 93 planned tests remain `planned_not_executed`.

No new IMP phase or task is created. No PCFA-07 obligation is assigned to IMP-P0. The launch target remains exactly P0.1–P0.4. The PCFA-07 planned test registry is implementation-planning evidence only and does not rewrite the historical PCR-02 semantic-test counts.

The current operational state directly binds the SHA-256 of `requirements/pcfa07-codex-implementation-backlog-reconciliation.json` and `repository/pcfa08-final-pre-codex-cross-authority-acceptance.json`. The launch entrypoint rejects missing PCFA-07 coverage, P0 widening, false implementation/evidence claims, duplicate planned tests, missing task/component/dependency/gate mappings, PCFA-08 drift, incomplete deleted-branch SHA evidence, or a live branch inventory containing anything other than `main`.

## Historical package snapshots

The following remain valid evidence of their own package boundaries, but their embedded readiness, next-phase, blocker, authority or licence-decision labels must not be interpreted as current operational state:

- `contracts/codex-phase0-launch-control.json` — WS6.2;
- `contracts/workstream6-final-launch-control.json` — WS6.2;
- `contracts/workstream6-current-status.json` — WS6.3;
- `repository/canonical-authority-registry.json` — WS6.4;
- `configs/workstream6-phase0-licence-decision-placeholder.yaml` — WS6.13 licence placeholder;
- `contracts/hermes-compatibility-pack.json` — PCR-06 package-time Hermes compatibility snapshot superseded for current adoption policy by PCFA-06;
- `handoff/codex-phase0-handoff.json` — PCR-04/WS6.1 successor snapshot;
- `handoff/codex-phase0-issue-final.md` — WS6.2 generated Issue #1 body;
- `handoff/codex-phase0-hosted-controls-issue-final.md` — pre-PCFA Issue #19 body;
- WS6.2 and PCFA-01 evidence-template snapshots named in the current operational-state contract.

They are preserved rather than rewritten so deterministic package reconstruction and audit history remain intact.

## Release versus launch SHA

The permanent WS6.16 record stores `release_parent_main_sha`, meaning the exact integrated `main` immediately before the permanent release-record commit. That historical SHA is not the future launch SHA.

At permit time:

- the release parent must be an ancestor of the approved launch `main`;
- the permanent release-record commit must be an ancestor of the approved launch `main`;
- both historical release SHAs are excluded from current-launch SHA equality;
- Founder approval, hosted-controls evidence, clean-macOS evidence, doctor `HEAD`, local `HEAD` and remote `main` must all bind one exact current `main` SHA;
- all launch evidence must bind the immutable release digest and the digest of `repository/current-operational-state.json`;
- the current operational-state digest transitively binds the exact PCFA-03 repository-posture digest;
- current authority directly binds the exact PCFA-04 product-scope addendum digest;
- current authority directly binds the exact PCFA-05 MVCL digest;
- current authority directly binds the exact PCFA-06 Hermes bounded-adoption refresh digest;
- current authority directly binds the exact PCFA-07 implementation-backlog reconciliation digest.

## Remaining gates

Before a permit can exist, all of the following must be independently evidenced against the then-current exact `main` SHA:

1. live GitHub repository visibility is `private`;
2. GitHub hosted controls in Issue #19;
3. exact-allowlist cleanup of the 65 PCFA-08-governed non-`main` branches with a final SHA retained for every deleted ref, ending with only `main` before launch;
4. clean supported macOS doctor evidence and Founder environment attestation;
5. explicit Founder authorization for IMP-P0 tasks P0.1–P0.4 only against one exact current `main` SHA;
6. live Issue #1 and Issue #19 bodies synchronized to the current files;
7. a successful real run of `scripts/prepare_codex_phase0_launch.py` producing the local single-use permit.

The permit becomes stale after any approved-main, permanent-release, current-operational-state, repository-posture, product-scope, MVCL, Hermes bounded-adoption, PCFA-07 backlog-reconciliation, current issue-body, evidence, required-check or scope change.

## Integration boundary

PCFA-08 is stacked on PCFA-07, which is stacked on PCFA-06, PCFA-05, PCFA-04, PCFA-03, PCFA-02 and PCFA-01. The current Issue #1 and Issue #19 files must not be synchronized to GitHub until the repository changes that introduce them are integrated. Until then, live issue-body mismatch and public repository visibility are intentional fail-closed conditions.
