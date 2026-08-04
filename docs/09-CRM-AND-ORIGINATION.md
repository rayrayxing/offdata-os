# 09 — CRM, Opportunity Radar and Origination

## 1. Initial CRM decision

Use **HubSpot Free** initially for relationship and opportunity continuity. Do not purchase a Professional plan during the foundation build.

HubSpot owns:

- Organisations and contacts
- Relationship activities
- Opportunities and pipeline stage
- Meetings and basic tasks
- Outreach and engagement-conversion history
- Consent and suppression metadata

Offdata owns:

- Opportunity hypotheses and evidence
- Engagement mandates
- Consulting methods and analyses
- Claims, models and recommendations
- Deliverables
- Implementation and benefits
- Detailed quality and provenance records

Only approved summaries and stable IDs should cross the boundary.

## 2. Initial integration mode

Use a HubSpot private application or approved OAuth path during the integration phase. Until then:

- Define field mappings only
- Use synthetic CRM fixtures
- Do not create paid HubSpot resources
- Do not send external email

## 3. CRM data model mapping

### Company

- HubSpot company ID
- Offdata organisation ID
- Name, domains and sector
- Relationship owner
- Opportunity and engagement summary
- Residency and conflict flags where appropriate

### Contact

- HubSpot contact ID
- Offdata contact ID
- Organisation
- Role
- Relationship and activity summary
- Consent, lawful-use and suppression status

### Deal / Opportunity

- HubSpot deal ID
- Offdata opportunity ID
- Trigger and proposition summary
- Stage and expected value
- Founder owner
- Next external action
- Engagement conversion ID

## 4. Opportunity Radar

The radar should monitor approved sources for signals such as:

- Funding or capital events
- Acquisitions, divestitures and leadership changes
- New products, markets or locations
- Hiring and capability patterns
- AI, data and technology investment
- Cost-reduction or restructuring announcements
- Customer complaints and service failures
- Regulatory developments
- Public filings and procurement notices
- Operational incidents or outages
- Website, pricing and offer changes
- Publicly visible control, workforce or transformation gaps

## 5. Opportunity dossier

```yaml
opportunity_dossier:
  organisation:
  trigger:
  source_evidence:
  observed_condition:
  probable_business_issue:
  alternative_explanations:
  likely_decision_owner:
  value_at_stake_range:
  relevant_offdata_methods:
  proposed_diagnostic:
  proposed_outreach_angle:
  confidence:
  legal_and_marketing_constraints:
  recommended_next_action:
```

The system must distinguish observation, inference and recommendation.

## 6. Initial offers

The initial proposition library may include:

- AI opportunity and value audit
- AI risk and controls audit
- Process automation diagnostic
- Customer-experience friction audit
- Cost and productivity rapid scan
- Operating-model readiness assessment
- AI workforce-impact assessment
- Benefits leakage review
- Data and AI scalability assessment
- M&A technology and AI diligence

Every offer requires a defined decision, evidence request, method stack, output contract, duration, limitations and approval state.

## 7. Outreach workflow

1. Detect and record trigger.
2. Validate company and source identity.
3. Develop opportunity hypothesis and alternatives.
4. Identify an appropriate buyer role.
5. Match to an approved proposition.
6. Draft a tailored message.
7. Check jurisdiction, contact basis, suppression and frequency.
8. Present Founder approval packet.
9. Send only through an approved channel after approval.
10. Record outcome and update CRM.
11. Escalate objections, legal concerns, complaints or commercial questions.

## 8. External sending controls

The first version must not autonomously:

- Purchase contact data
- Scrape prohibited or access-controlled sources
- Send bulk cold outreach
- Misrepresent the sender or relationship
- Contact opted-out people
- Continue after a complaint
- Enter a new jurisdiction without policy review
- Make pricing, delivery or legal commitments

Campaign approval should define:

- Sender identity
- Audience and jurisdiction
- Proposition
- Source and contact basis
- Message templates and permitted personalisation
- Daily and weekly volume
- Follow-up limit
- Suppression and complaint handling
- Start and expiry dates

## 9. Continuity and engagement conversion

When an opportunity becomes an engagement:

- Preserve CRM identifiers
- Create the engagement and mandate records
- Copy only approved relationship context
- Link communications and meetings
- Preserve commercial stage separately from analytical truth
- Prevent sensitive engagement data from syncing back by default

## 10. Testing requirements

- Duplicate company and contact detection
- Stable ID mapping
- Create, update and conflict resolution
- Revoked OAuth handling
- Rate-limit and retry behaviour
- Suppression enforcement
- Jurisdiction-policy checks
- No leakage of confidential evidence into CRM
- Opportunity-to-engagement conversion
- Audit of external messages
- Safe recovery without duplicate sends

## 11. Upgrade criteria

Do not upgrade HubSpot merely for convenience. Reconsider paid CRM features when:

- Prospect volume creates measurable manual burden
- Native sequences or workflow automation are cheaper than building and operating offdata equivalents
- Advanced reporting affects commercial decisions
- Additional users require paid capabilities
- Integration support or limits become a documented constraint
