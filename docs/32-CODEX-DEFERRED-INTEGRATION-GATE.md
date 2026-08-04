# 32 — Codex Deferred Integration Gate

## Decision

Codex integration is intentionally deferred while chat-first heavy lifting continues.

## Rationale

The highest-value use of strong reasoning models is to complete consulting logic, specifications, schemas, fixtures, prompts and expected answers before using Codex credits for execution. Starting Codex too early would cause it to spend time rediscovering requirements, generating synthetic content and making architecture choices that can be completed more deliberately in the repository first.

## Codex may start only when the Founder approves this gate

Minimum required inputs:

- governing Build Pack and `AGENTS.md`;
- numbered requirements and traceability baseline;
- deterministic core package and tests;
- engagement aggregate, API and persistence specifications;
- complete `FIXTURE-DAI-001` evidence room and answer key;
- agent role and evaluation pack;
- knowledge ingestion contracts;
- security and setup constraints;
- bounded implementation issue.

## First Codex scope

When approved, Codex should perform only:

1. Inspect and report the macOS environment.
2. Install approved local prerequisites.
3. Install and run the committed `offdata-core` package.
4. Execute and repair integration problems without weakening contracts.
5. Validate YAML, JSON and CSV fixtures.
6. Create the local Next.js, FastAPI, PostgreSQL and object-storage shells.
7. Add GitHub Actions and security scans.
8. Open a draft pull request with test evidence.
9. Stop for Founder review.

## Explicit exclusions

The first Codex run must not:

- redesign the consulting lifecycle;
- replace the approval or quality policy;
- create new product requirements without a decision record;
- purchase or configure cloud services;
- use real client data;
- configure CRM, OAuth, DNS or external email;
- install OpenClaw, Hermes, Buzz, Conductor, Reasonix or other deferred harnesses;
- build the final deliverable studio;
- proceed beyond the approved issue.

## Gate owner

Founder.

## Current state

`deferred_chat_first_build_active`

## Exit evidence

Before changing the state to `approved_for_codex_phase_0`, record:

- remaining chat-first gaps;
- repository commit SHA;
- approved first Codex issue;
- expected cost and time budget;
- Founder availability for permissions and review;
- rollback point.