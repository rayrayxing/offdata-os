# 23 — Methodology Radar Specification

## Purpose

Continuously identify analytical methods, evaluation designs, diagnostic procedures, modelling approaches, operating practices and quality controls that may improve offdata without copying protected expression or automatically altering the canonical methodology library.

## 1. Source classes

Priority order:

1. Standards bodies, regulators and governments
2. Peer-reviewed research and universities
3. Professional institutes
4. Public consulting-firm publications
5. Technology and software organisations
6. Think tanks and recognised practitioner sources
7. Lower-authority discovery sources used only to locate stronger evidence

The Radar must not circumvent paywalls, access restrictions, robots controls, licences or terms.

## 2. Discovery taxonomy

Candidates are classified as:

- analytical method
- diagnostic method
- measurement or metric system
- evaluation or causal design
- quantitative model
- decision rule
- implementation practice
- governance or assurance control
- visual representation
- operating routine
- framework or taxonomy
- failure mode or anti-pattern

A named framework is not presumed to be a method.

## 3. Cadence

### Daily discovery

- poll approved feeds, searches and watch lists
- record new or changed source metadata
- create fingerprints and deduplicate
- assign preliminary domain and candidate type
- do not generate canonical records

### Weekly triage

- retrieve authoritative source material
- distinguish genuinely new content from renamed existing concepts
- compare with current methods and aliases
- assess applicability and evidence strength
- reject obvious promotional content or unsupported claims

### Monthly candidate pack

- prepare candidate method records
- identify primary support and criticism
- assess copyright, trademark and licence concerns
- propose original offdata procedure
- identify tests and exemplar engagements
- route to Methodology Librarian and Founder review

### Quarterly release

- promote approved candidates
- update aliases, compatibility and conflict relationships
- deprecate or supersede records
- rerun regression suite
- issue versioned release notes

## 4. Candidate record

Required fields:

- `candidate_id`
- title and candidate type
- domain and problem archetypes
- discovery source and retrieval date
- primary and supporting sources
- underlying idea or analytical function
- novelty assessment
- closest existing methods
- proposed independent offdata procedure
- inputs, steps and outputs
- evidence burden
- strengths and limitations
- failure modes
- compatibility and conflicts
- required tools and reviewers
- copyright, licence and trademark assessment
- proposed tests
- status and review history

## 5. Novelty decision

Classify as:

- `new_method`
- `material_extension`
- `new_application`
- `renamed_existing_method`
- `framework_only`
- `insufficient_evidence`
- `out_of_scope`
- `prohibited_or_licensed`

Promotion is possible only for the first three categories.

## 6. Copyright and provenance controls

1. Preserve the external source and provenance internally.
2. Extract the underlying idea or function, not distinctive wording or visual expression.
3. Seek primary, public and independent supporting sources.
4. Do not reproduce consulting templates, diagrams, proprietary maturity levels or confidential examples.
5. Draft the offdata procedure independently.
6. Retain required open-source licence notices for incorporated code.
7. Record trademark concerns where a branded name is referenced.
8. Require human approval before canonical promotion.

## 7. Promotion gate

A candidate may be promoted only when:

- the executive decision and analytical purpose are explicit
- it is not duplicative without material incremental value
- procedure, inputs and outputs are implementable
- evidence and limitations are recorded
- compatibility and conflicts are assessed
- at least one fixture or regression test exists
- copyright and licence review passes
- Methodology Librarian recommends approval
- Founder approves the release

## 8. Automation safeguards

- Discovery jobs run read-only against public sources.
- Candidate drafting writes only to quarantine storage.
- No candidate can update canonical records directly.
- Scheduled tasks have cost, source-count and runtime limits.
- Source changes generate review tasks rather than silent replacement.
- Legal, regulatory and standards changes are marked time-sensitive.

## 9. Initial watch domains

- strategy and capital allocation
- growth, pricing and customer economics
- customer and service design
- operating models and organisation design
- workforce planning and AI workforce impact
- productivity, operations research and process improvement
- digital, data and AI transformation
- AI evaluation, assurance and governance
- risk, controls, resilience and cybersecurity
- transactions, valuation and integration
- implementation science and change
- benefits realisation and causal evaluation
- presentation, information design and decision communication

## 10. Acceptance tests

1. Duplicate publications resolve to one source family.
2. A branded renaming of an existing method is not treated as novel.
3. A candidate cannot promote itself.
4. A candidate without primary support is flagged.
5. Copyright-risk cases enter manual review.
6. Superseded standards create review tasks.
7. Approved promotion creates a new immutable method version.
8. Regression failure blocks quarterly release.
9. A rollback restores the prior canonical release.
10. Every promoted record retains its provenance and transformation history.
