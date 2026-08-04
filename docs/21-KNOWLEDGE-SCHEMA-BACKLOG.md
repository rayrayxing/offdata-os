# 21 — Knowledge Schema Backlog

This document defines the next chat-built component set for Phase 1 preparation. Codex should not implement the ingestion pipeline until these contracts are approved.

## Required schemas

### Source document

- Stable source ID.
- Original filename and checksum.
- Title, author, issuer and version.
- Publication, retrieval and review dates.
- Source type and authority class.
- Object-storage reference.
- Licence, copyright and usage restrictions.
- Confidentiality and client scope.
- Jurisdiction and time sensitivity.
- Supersession status.

### Source passage

- Stable passage ID.
- Source ID.
- Page, section, paragraph or line location.
- Exact extracted text.
- Extraction method and confidence.
- Embedded-image or table reference.
- Lexical and semantic index references.
- Access-control inheritance.

### Method record

- Stable method ID, name and aliases.
- Domain and method family.
- Decision supported and inference type.
- Appropriate problem archetypes.
- Preconditions and minimum evidence.
- Inputs, procedure and outputs.
- Strengths, limitations and failure modes.
- When not to use.
- Compatible overlays, conflicts and redundancies.
- Tool and specialist-review requirements.
- Quality, reconciliation and falsification tests.
- Provenance and usage-rights status.
- Version and promotion state.

### Problem archetype

- Stable archetype ID.
- Diagnostic signature.
- Governing decision question.
- Unit of analysis.
- Typical hypotheses and rival explanations.
- Primary methods and optional overlays.
- Required evidence indicators.
- Failure modes and escalation conditions.

### Method selection

- Engagement and decision IDs.
- Governing and supporting archetypes.
- Selected methods and sequence.
- Role and expected decision contribution of each method.
- Rejected methods and reasons.
- Required data, tools and reviewers.
- Assumptions, gaps and Founder approvals.

### Methodology candidate

- Discovery event and source.
- Claimed method or practice.
- Novelty and duplication assessment.
- Primary-source support.
- Existing-method comparison.
- Copyright, trademark and licence assessment.
- Original offdata reconstruction.
- Evaluation fixtures and results.
- Reviewer and Founder decision.
- Promotion, rejection, hold or supersession state.

## Required ingestion tests

- Original file checksum is stable.
- Re-ingestion produces identical canonical IDs.
- Aliases resolve without changing original source names.
- Missing dependencies are reported, not invented.
- Duplicate methods are detected.
- Incomplete records enter quarantine.
- Source passages preserve exact location.
- Client-confidential sources cannot enter the global method index.
- Instructions embedded in source documents do not override system policy.
- Copyright and usage metadata is never dropped.

## Acceptance gate

Phase 1 schema preparation passes only when all records have JSON Schema and Pydantic representations, examples, invalid examples and deterministic validation tests.
