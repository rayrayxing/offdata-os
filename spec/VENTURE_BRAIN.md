# Venture Brain

Implement as a Hermes plugin backed by PostgreSQL. Profiles may only mutate authoritative state through validated tools.

## Entities

### Portfolio
Owner policy, environment, capital, risk limits, portfolio metrics.

### Venture
Slug/name, environment, provisional state, phase/gate, GM, current revisions, kill switch.

### Signal
Technology/regulatory/cost/behavioral change with provenance, occurrence/retrieval times and content hash.

### VentureThesis
Signals, insight, enabling capability, target context, proposed transformation, possible buyer, why-now, novelty and uncertainties.

### ResearchArtifact
Provider/source/query hash, URL/ref, source/retrieval times, author/account, raw artifact pointer/hash, SUPPORTING/CONTRARY/NEUTRAL role, confidence, receipt.

### Claim
`OBSERVED | INFERRED | HYPOTHESIS`, evidence/contrary refs, confidence, disclosure policy, immutable revision/state.

### EvidenceArtifact
Purpose: `MARKET_RESEARCH | BEHAVIORAL_VALIDATION | DIRECT_BUYER | FINANCIAL | OPERATING`.
Admissibility: `ADMISSIBLE | INADMISSIBLE | QUARANTINED | PROVISIONAL`.
Direct-buyer tuple fields are first-class.

### Concern
Severity `BLOCKING | MATERIAL_EXPERIMENT | DESIGN_CONSTRAINT | MONITOR`; status `OPEN | RESOLVED | ACCEPTED_RISK | INVALIDATED | SUPERSEDED`; evidence, confidence, owner, mitigation, review/experiment.

### BusinessConcept
Versioned canonical business narrative: enabling change; ICP/user/buyer; trigger/problem/current workflow/spend; proposed outcome/product/wedge; why now; business model; distribution; contrary case; assumptions/unknowns.

### Experiment / Observation
Principal uncertainty, hypothesis, target, method, success/failure, stopping rule, budget/time, analysis method, observations and evidence.

### Prototype
Experiment/concept revision, artifact/hash, simulation flag, critical workflow, isolation/security status, limitations, immutable revision.

### ValidationPackage
Audience, prototype, hypothesis, disclosure, communication, questions, validation method and evidence/attribution requirements.

### Contact / Interaction
Account/person identity, relationship, opt-out/contact frequency/promises; interactions include role/type/time/channel/receipt and resulting evidence.

### GateSnapshot
Gate/policy version/environment/predecessor/evidence IDs+fingerprints/financial snapshot/concerns/result/correlation. Immutable. May become STALE/SUPERSEDED.

### Decision / Forecast
Question/options/choice/evidence/contrary/assumptions/concerns/EV/confidence/actor/review; forecasts add probability, horizon, model and realized scoring.

### FinancialJournal / FinancialSnapshot
Append-only/double-entry-compatible journal; immutable closed snapshots used by authoritative economics/gates.

### CapitalAuthorization / AuthorityGrant
Purpose/amount/action classes/gate/validity/spent and profile/venture/tool/target/environment scopes.

### ActionReceipt / AuditEvent
Provider/action/request-response hashes/request ID/status/retry/cost/latency/correlation; AuditEvent written transactionally with authoritative mutations.

### SkillCertification / ModelEvaluation / LearningCandidate / AAR
Staged organizational learning and high-signal owner reporting.

## Derived artifact states

`CURRENT | STALE | SUPERSEDED | HISTORICAL`.

Never overwrite history to simulate revision. Upstream material change creates a new revision and propagates staleness where relevant.

## Certainty integrity

Communicators may not upgrade `HYPOTHESIS` to fact, `INFERRED` to guarantee, or unknown economics to a fabricated numeric claim.