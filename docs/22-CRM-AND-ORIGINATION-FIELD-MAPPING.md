# 22 — CRM and Origination Field Mapping

## Status

Baseline v0.1. HubSpot Free is the initial external CRM; offdata remains the engagement system of record.

## 1. Ownership boundary

### HubSpot owns

- companies
- contacts
- deals and pipeline stage
- meetings and activities
- relationship owner
- external next action
- commercial value and probability
- consent, objection and suppression indicators

### offdata owns

- opportunity evidence dossier
- mandate and decision framing
- research, claims and evidence
- methods, analyses and models
- recommendations and approvals
- deliverables
- implementation and benefits

Detailed engagement evidence must not be copied into HubSpot by default.

## 2. Company mapping

| offdata field | HubSpot field | Direction | Rule |
|---|---|---|---|
| `organisation_id` | custom `offdata_organisation_id` | both | stable immutable link |
| `name` | company name | both | HubSpot may update display name |
| `domain` | company domain | both | normalise before matching |
| `country` | country/region | HubSpot to offdata | used for outreach and residency policy |
| `industry` | industry | HubSpot to offdata | treat as provisional classification |
| `account_tier` | custom | offdata to HubSpot | A/B/C or watchlist |
| `relationship_status` | custom | both | prospect, active, dormant, client, former client |
| `last_signal_at` | custom | offdata to HubSpot | latest approved opportunity signal |
| `confidentiality_level` | none | offdata only | never synchronise |

## 3. Contact mapping

| offdata field | HubSpot field | Direction | Rule |
|---|---|---|---|
| `contact_id` | custom `offdata_contact_id` | both | stable link |
| `first_name` | firstname | both | standard |
| `last_name` | lastname | both | standard |
| `email` | email | both | exact-match candidate only |
| `job_title` | jobtitle | both | time-sensitive |
| `buyer_role` | custom | offdata to HubSpot | economic buyer, sponsor, influencer, blocker, user |
| `relationship_strength` | custom | offdata to HubSpot | 0–5 with explanation in offdata |
| `contact_source` | original source/custom | HubSpot to offdata | provenance required |
| `outreach_status` | custom | both | not-contacted, drafted, approved, sent, replied, suppressed |
| `suppressed` | opt-out/custom | both | strictest value governs |
| `lawful_use_basis` | custom | offdata to HubSpot | jurisdiction-specific controlled value |
| `private_notes` | notes | neither by default | remain system-specific |

## 4. Opportunity/deal mapping

| offdata field | HubSpot field | Direction | Rule |
|---|---|---|---|
| `opportunity_id` | custom `offdata_opportunity_id` | both | stable link |
| `title` | deal name | both | standard |
| `organisation_id` | associated company | both | required |
| `stage` | deal stage | both | mapped through configuration |
| `estimated_value` | amount | offdata to HubSpot after Founder approval | not an AI commitment |
| `probability` | deal probability/custom | both | distinguish system score from commercial forecast |
| `expected_close_date` | close date | Founder/HubSpot to offdata | never inferred as a commitment |
| `origin_type` | custom | offdata to HubSpot | founder, referral, system-scouted, inbound, partner |
| `trigger_category` | custom | offdata to HubSpot | approved taxonomy |
| `offer_code` | custom | offdata to HubSpot | approved service offer |
| `fit_score` | custom | offdata to HubSpot | 0–100 |
| `urgency_score` | custom | offdata to HubSpot | 0–100 |
| `evidence_confidence` | custom | offdata to HubSpot | low, medium, high |
| `engagement_id` | custom | offdata to HubSpot | added on conversion |

## 5. Opportunity scoring

Total score is a configurable 0–100 weighted result:

- strategic fit: 20
- observable trigger strength: 15
- probable value at stake: 15
- urgency and timing: 15
- buyer accessibility: 10
- evidence confidence: 10
- offdata method and capability fit: 10
- delivery feasibility: 5

### Mandatory penalties

- legal or contactability concern: up to -100
- weak or single-source trigger: up to -20
- no credible buyer role: up to -15
- proposition depends on unsupported claims: up to -25
- conflict or independence concern: up to -100

### Suggested interpretation

- 80–100: Founder review for immediate tailored approach
- 60–79: research and nurture
- 40–59: watchlist
- below 40: no active outreach

A score never authorises external sending.

## 6. Opportunity dossier minimum fields

- company and trigger
- source records and dates
- observed facts
- reasoned problem hypothesis
- alternative explanations
- probable value at stake
- likely buyer and stakeholders
- relevant offdata domain and methods
- proposed diagnostic or offer
- fit, urgency and confidence scores
- outreach angle
- risks and policy restrictions
- next recommended action

## 7. Synchronisation rules

1. Start with a synthetic adapter and contract tests.
2. Use stable external IDs rather than name-only matching.
3. Never overwrite a newer record silently.
4. Record every sync operation and conflict.
5. Respect rate limits and retry with idempotency.
6. Suppression and objection changes propagate immediately.
7. Full evidence passages, model files and client-confidential analysis remain offdata-only.
8. OAuth revocation must disable sync without corrupting local state.

## 8. Outreach approval states

`drafted → policy_checked → founder_approved → scheduled → sent → replied|bounced|suppressed|closed`

The first release must require Founder approval for every external message or approved batch.

## 9. Acceptance tests

- create and update synthetic company, contact and deal records
- prevent duplicates using stable IDs and configured matching
- reject confidential-field synchronisation
- propagate suppression before any send action
- handle revoked OAuth and rate-limit responses
- convert an approved opportunity into an engagement
- preserve relationship history after conversion
- prove no external send occurs without a scoped approval
