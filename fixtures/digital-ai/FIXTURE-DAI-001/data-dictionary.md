# FIXTURE-DAI-001 — Data Dictionary and Known Limitations

## General conventions

- Currency: Singapore dollars.
- Percent fields: percentage points from 0 to 100.
- Time: calendar elapsed hours unless the field specifies touch minutes.
- All data is synthetic and intentionally simplified.
- Aggregates are designed to test consulting judgement, not production statistical precision.

## `quotation-activity.csv`

| Field | Meaning |
|---|---|
| `row_id` | Stable synthetic evidence-row identifier. |
| `month` | Calendar month. |
| `complexity_segment` | Operationally defined quotation class. |
| `quotation_count` | Number of quotations created. |
| `median_touch_minutes` | Median active human handling time. |
| `median_elapsed_hours` | Median time from complete-enquiry receipt to released quotation. |
| `median_specialist_wait_hours` | Median waiting time attributed to product or engineering specialist support. |
| `rework_percent` | Percentage returned for correction or completion. |
| `data_error_percent` | Percentage with item, quantity, unit, delivery-term or pricing-data defect. |
| `win_rate_percent` | Quoted opportunities recorded as won divided by quotations with known outcome. |
| `automated_extraction_candidate_percent` | Estimated percentage where enquiry fields are sufficiently structured for extraction support. |

Known limitations:

- Quotation outcomes are missing for approximately 12 percent of records.
- Complexity segment is assigned retrospectively and has not been independently validated.
- Touch-time capture excludes some informal product-specialist work.
- Elapsed time includes customer and supplier waiting where timestamps cannot distinguish the cause.
- The dataset does not prove that faster quotation response causes higher conversion.

## `customer-service-summary.csv`

| Field | Meaning |
|---|---|
| `annual_ticket_count` | Estimated annual category volume. |
| `share_percent` | Share of total ticket volume. |
| `first_contact_resolution_percent` | Resolved without a second customer contact or specialist handoff. |
| `median_handle_minutes` | Median active service-agent handling time. |
| `specialist_escalation_percent` | Share requiring product, technical, finance or quality specialist action. |
| `approved_knowledge_coverage_percent` | Estimated share covered by current approved and current knowledge. |
| `autonomous_response_suitability` | Initial safety and feasibility judgement, not a production decision. |

Known limitations:

- Resolution codes are missing for 28 percent of underlying tickets.
- `general_or_uncoded` may contain material subcategories.
- The product-compatibility category does not distinguish exact part confirmation from application engineering.
- Authentication and customer-specific permissions are not represented in the aggregate.

## `use-case-inventory.csv`

Initial scores use a 0–10 scale and are workshop estimates.

| Field | Meaning |
|---|---|
| `addressable_value_score` | Relative size and strategic relevance of potential value. |
| `feasibility_score` | Relative technical and operational implementability within constraints. |
| `data_readiness_score` | Availability, quality, access and governance of required information. |
| `risk_score` | Inherent risk before proposed pilot controls; higher is worse. |
| `human_judgement_dependency` | Degree to which accountable human decision remains required. |
| `recommended_initial_status` | Working status for analysis, not an approved decision. |

Known limitations:

- Scores must not be mechanically aggregated without explicit weighting and sensitivity.
- Workshop estimates may reflect sponsor preference.
- Non-AI alternatives are included and must remain in the comparison.

## `workforce-survey.csv`

| Field | Meaning |
|---|---|
| `respondents` | Completed responses by segment. |
| `public_ai_use_percent` | Self-reported work use of unapproved public AI tools. |
| `confidence_reviewing_ai_percent` | Respondents agreeing they can identify and correct incorrect AI output. |
| `interest_in_training_percent` | Respondents interested in role-relevant AI training. |
| `concern_job_reduction_percent` | Respondents concerned that AI will principally be used to remove jobs. |
| `concern_data_leakage_percent` | Respondents concerned about confidential-information leakage. |
| `manager_support_percent` | Respondents believing their manager will support safe adoption. |

Known limitations:

- Self-reporting may understate unapproved use.
- Small segment samples are not suitable for individual or employment decisions.
- Results do not establish adoption behaviour.

## `financial-baseline.csv`

| Field | Meaning |
|---|---|
| `base_value`, `downside_value`, `upside_value` | Scenario values before validation. |
| `cash_classification` | Economic type: cash cost, capacity, cost avoidance, margin, risk avoidance or invalid mixed claim. |
| `timing` | Expected period of effect. |
| `source_or_assumption` | Whether the value is based on a management baseline, calculation or unvalidated assumption. |

Critical interpretation rules:

- Released capacity is not cash saving unless payroll or external expenditure changes.
- Cost avoidance is not existing-cost removal.
- Potential incremental margin requires evidence that faster response changes customer behaviour.
- Do not sum capacity, margin, cost avoidance and risk avoidance as though they were equivalent cash benefits.
- The management-claimed SGD 355,000 year-one value is deliberately invalid.

## `risk-and-controls.csv`

| Field | Meaning |
|---|---|
| `inherent_severity` | Exposure before controls. |
| `existing_control` | Current stated control. |
| `control_design_status` | Initial design assessment only. |
| `operating_evidence` | Evidence, if any, that the control operated. |
| `residual_severity` | Working residual assessment after existing controls. |
| `required_pilot_control` | Minimum proposed control for the pilot. |

Known limitations:

- This is not a legal, regulatory, audit or cybersecurity opinion.
- Control design has not been technically validated.
- Residual risk requires accountable-human acceptance.
- Severity labels are ordinal and should not be treated as quantified expected loss.

## Cross-file joins

- `use_case_id` is the stable option identifier.
- `risk_id` links to use cases through analytical evaluation rather than a prefilled foreign key, forcing the agent to reason about applicability.
- `row_id` fields support passage- or row-level evidence citations.
- Financial drivers should be connected to observed quotation data and pilot outcomes, not assumed from use-case scores.