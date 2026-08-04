# 20 — Development Status

## Snapshot

Date: 2026-08-04

### Completed in ChatGPT and committed

- Chat-first development plan.
- Numbered requirements catalogue.
- Third-party tool registry.
- Machine-readable lifecycle, policy and agent configuration.
- JSON schemas for agent, context and Founder decision contracts.
- Synthetic engagement fixture manifest.
- Deterministic `offdata-core` Python package covering:
  - lifecycle stages and transitions;
  - decision and approval policy;
  - agent envelopes, context packages and Founder packets;
  - source, passage, method, archetype, selection and methodology-candidate records;
  - commands, domain events and approval records;
  - quality scoring, defect severity, exceptions and release gates;
  - story models, visual specifications and cross-format reconciliation;
  - CRM, opportunity dossiers and controlled outreach.
- Fifty-one unit-test functions across the deterministic package.
- First complete synthetic SME AI-audit fixture specification.
- Founder cockpit information architecture.
- Updated Codex Phase 0 prompt and validation addendum.

### Preliminary validation

Incremental predecessor versions of the deterministic package were successfully exercised in the chat development environment, and JSON/YAML parsing was checked during development. The latest four contract groups and the full 51-test committed suite still require authoritative execution on the Founder’s macOS machine and through GitHub Actions. No claim is made that Phase 0 has passed until Codex produces that evidence.

### Current gate

Codex should now execute Issue #1, validate all committed contracts and tests, and then complete the local application shell. It must not duplicate lifecycle or policy logic already present in `offdata-core`.

### Next ChatGPT development candidates

1. JSON Schemas mirroring the new Pydantic knowledge, event, quality, delivery and CRM contracts.
2. Detailed source manifest and canonical alias map for the uploaded library.
3. Synthetic source files and datasets for `FIXTURE-DAI-001`.
4. Engagement aggregate and API specifications.
5. Quality fixture cases mapped from the canonical red-team rubric.
6. Story and infographic archetype examples.
7. CRM field mapping and opportunity-scoring specification.
8. Methodology Radar source-watch and promotion specification.
