# WS6.4 — Canonical authority and evidence registry

## Purpose

WS6.4 removes ambiguity between current authority, supporting requirements, retained predecessor evidence, superseded handoffs and external issue state.

The package closes exactly:

- `WS6-CONSIST-001` — canonical authority and supersession classes were not machine-readable;
- `WS6-CONSIST-007` — retained reports, attachments and predecessor handoffs lacked a complete current-authority classification.

`WS6-BLOCK-006` remains open. Codex remains unauthorized.

## Canonical registry

The governed source is:

`configs/workstream6-canonical-authority.yaml`

The machine-readable registry is:

`repository/canonical-authority-registry.json`

The registry is byte-identical to its governed source. It defines:

- the six-level authority precedence inherited from `AGENTS.md`;
- 35 exact authority or evidence records;
- 11 ordered fallback classification rules;
- three external GitHub issue records;
- one controlling instruction;
- one current authority registry;
- one current machine handoff;
- one current launch contract;
- one current generated issue body;
- one current actionable assignment, issue #1;
- one current manual gate, issue #19;
- issue #2 as a superseded duplicate.

## Classification model

Exact records override fallback rules. The registry distinguishes:

- controlling instructions and policies;
- current status, architecture, requirement and launch surfaces;
- current deterministic contracts, schemas and source configuration;
- current evidence templates and launch entrypoints;
- current package evidence;
- retained package, validation, release, attachment and handoff evidence;
- superseded issue bodies and machine snapshots.

Historical material is never deleted merely because it is superseded. Supersession changes authority, not evidence retention.

## Read-order reconciliation

The validator parses both:

- `handoff/codex-phase0-handoff.json`;
- `handoff/codex-phase0-issue-final.md`.

It unions those read orders with every exact record marked `read_order_required=true`. Every resulting path must exist and resolve to one classification. The registry itself is a required pre-handoff authority layer, while the already rebound WS6.1 and WS6.2 handoff and issue-body bytes remain unchanged.

## Evidence coverage

The validator recursively scans:

- `configs/`;
- `contracts/`;
- `docs/`;
- `handoff/`;
- `reports/`;
- `releases/`;
- `repository/`;
- `schemas/`;
- `attachments/` when present.

Every file must resolve through an exact record or an ordered rule. Unknown evidence cannot silently become current authority.

## Validation

The WS6.4 gate requires:

- JSON Schema validation;
- byte-deterministic source-to-registry generation;
- deterministic evidence-report generation;
- unique exact paths and rule identifiers;
- all authority uniqueness constraints;
- at least 45 machine-handoff read-order entries;
- at least 49 canonical-issue read-order entries;
- at least 51 combined classified authority entries;
- recursive classification of every configured evidence root;
- exactly one current machine handoff and one current generated issue body;
- explicit supersession of earlier issue bodies and the PCR-09 handoff snapshot;
- issue #1 current/open, issue #19 current/open and issue #2 closed/duplicate classification;
- 23 deliberate semantic and structural mutations rejected;
- all prior builders, validators, runtime tests, compilation, Ruff, strict MyPy and launch self-tests.

The dedicated status check is:

`Validate WS6.4 canonical authority registry and complete prior components`

This is a WS6 subphase check. It does not replace the future permanent final branch-protection identity.

## Boundaries

WS6.4 does not:

- issue a launch permit;
- create `codex/phase-0-foundation`;
- authorize Phase 0 implementation, merge or Phase 1;
- activate a runtime, Hermes or Northstar implementation;
- enable real client data, paid services, OAuth, external actions or deployment;
- close issue #19 or infer hosted/environment evidence;
- create the permanent final WS6 release.

## Completion state

WS6.4 is complete when the registry, schema, report, documentation and workflow are merged with every retained prior component green.

The next permitted chat-first work package is `WS6.5` — phase namespace normalization.

## Rollback

Before merge, close the pull request and delete only `governance/workstream6-canonical-authority-registry`.

After merge, revert WS6.4 as one unit. Preserve all historical evidence and keep every authorization boundary false.
