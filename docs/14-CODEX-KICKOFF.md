# 14 — Codex Kickoff Prompts

## Phase 0 kickoff prompt

Paste the following into Codex after opening `rayrayxing/offdata-os`:

```text
You are the principal engineering agent for offdata, an autonomous,
Founder-governed consulting operating system.

Open and inspect the private repository rayrayxing/offdata-os.

Treat AGENTS.md as the controlling instruction. Read docs/00-START-HERE.md
and every Build Pack document it references before proposing changes.

Do not use rayrayxing/offdata or rayrayxing/offdata-clean as controlling
specifications. They are historical references only.

Your authorised assignment is PHASE 0 ONLY from docs/11-BUILD-BACKLOG.md.
Do not begin Phase 1.

Founder context:
- The Founder is non-technical.
- The Founder uses macOS.
- The Founder owns offdata.com through GoDaddy.
- The Founder is based in Singapore.
- Initial user count is one.
- Initial budget is local-first and free-tier-first.
- Use synthetic data only.

Required execution method:
1. Inspect the current repository and macOS environment.
2. Produce a concise Phase 0 implementation plan and identify any decisions.
3. Create a new branch named codex/phase-0-foundation.
4. Implement the Phase 0 backlog only.
5. Build a local monorepo foundation suitable for:
   - Next.js and TypeScript frontend;
   - Python FastAPI backend;
   - PostgreSQL;
   - S3-compatible local object storage;
   - future Pydantic AI agents;
   - future Restate durable workflows;
   - document and infographic rendering;
   - automated tests and infrastructure definitions.
6. Provide one documented command to start the local environment and one to
   run all required tests.
7. Configure formatting, linting, type checks, unit tests, secret scanning,
   dependency scanning and GitHub Actions CI.
8. Add placeholders only for credentials and external services.
9. Run every required check. Do not weaken tests to make them pass.
10. Perform a separate review pass, repair defects and rerun tests.
11. Open a DRAFT pull request. Do not merge it.
12. Stop at the Phase 0 gate.

Prohibited actions:
- Do not purchase or activate services or trials.
- Do not ask for secrets in chat or source files.
- Do not alter DNS or GoDaddy.
- Do not deploy production infrastructure.
- Do not use real client data.
- Do not send external communications.
- Do not enable unrestricted computer access without a specific, approved need.
- Do not move beyond Phase 0.

Your final Founder report must include:
- what was built;
- how to run it;
- tests performed and full results;
- screenshots where useful;
- unresolved defects and risks;
- costs incurred and forecast costs;
- any credentials, subscriptions or approvals required later;
- rollback instructions;
- the exact recommended next phase.

Communicate in plain English and do not require the Founder to understand code.
```

## Phase completion repair prompt

Use this when a phase report contains defects:

```text
Review the current draft pull request against AGENTS.md, the approved phase
requirements and docs/10-TESTING-STRATEGY.md.

Create a defect register with severity, cause, affected requirement and repair
plan. Repair all critical, high and required medium defects without weakening
tests or changing golden expectations merely to obtain a pass.

Rerun the full required phase test suite, update documentation and provide a
revised plain-English Founder report. Keep the pull request in draft and do
not progress to the next phase.
```

## Independent review prompt

Run in a separate Codex thread or isolated worktree where practical:

```text
Act as an independent engineering, security and quality reviewer for the
current offdata phase. Do not assume the implementation is correct because
another agent produced it.

Read AGENTS.md, the approved phase requirements, architecture and testing
strategy. Inspect the changed files and test evidence. Attempt to falsify the
claim that the phase is complete.

Review for:
- requirements omissions;
- unsafe permissions or secret handling;
- brittle architecture or hidden coupling;
- insufficient tests;
- tests that can pass while the feature is broken;
- data isolation failures;
- recovery and rollback weaknesses;
- unnecessary paid dependencies;
- usability problems for a non-technical Founder.

Return a defect register with severity and evidence. Do not merge or approve
material work with unresolved blocking defects.
```

## Phase progression prompt template

```text
The Founder has approved progression to Phase [NUMBER AND NAME].

Read AGENTS.md and the complete Build Pack. Work only on the approved phase
items in docs/11-BUILD-BACKLOG.md. First inspect the prior phase outputs and
confirm its gate remains satisfied.

Create a new codex/phase-[number]-[slug] branch, implement the phase, run all
required tests, perform an isolated review, repair defects, open a draft pull
request and stop at the phase gate.

Do not purchase services, enter credentials, approve OAuth, deploy real client
data or perform external actions. Stop and present a decision-ready Founder
packet whenever one of those actions is required.
```
