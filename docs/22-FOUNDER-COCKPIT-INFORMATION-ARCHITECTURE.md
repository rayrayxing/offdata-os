# 22 — Founder Cockpit Information Architecture

## 1. Product principle

The Founder cockpit is an exception-and-decision interface, not a transcript viewer. It should show what requires judgement, why it matters, what offdata has completed, what is blocked and whether the work is safe and ready for reliance.

The default experience must minimise operational detail while preserving drill-through to complete evidence, records, agent runs and audit events.

## 2. Primary navigation

1. Home
2. Opportunities
3. Engagements
4. Decisions
5. Deliverables
6. Methodology
7. Operations
8. Settings

## 3. Home

### Founder briefing

- Decisions due today and this week.
- Engagements at risk.
- Material evidence or quality changes.
- External actions awaiting approval.
- New qualified opportunities.
- System cost and incident exceptions.

### Portfolio summary

- Active engagements by stage and state.
- Waiting and blocked engagements.
- Founder review queue.
- Deliverables approaching release.
- Benefits at risk or behind plan.
- Current monthly model and infrastructure cost.

### Rules

- Do not show routine agent activity unless abnormal.
- Do not use activity count as a proxy for progress.
- Prioritise consequence, deadline and reversibility.

## 4. Opportunities

### Opportunity list

- Organisation.
- Trigger and detection date.
- Probable issue.
- Proposed diagnostic or offer.
- Likely buyer.
- Confidence, urgency and estimated value.
- CRM stage.
- Next action.
- Outreach policy state.

### Opportunity dossier

- Observed evidence.
- Alternative explanations.
- Client or market hypothesis.
- Relevant offdata methods and engagement types.
- Suggested outreach angle.
- Contactability and jurisdiction constraints.
- Founder approve, revise, hold or reject.

### Controls

- No send button without an approved campaign, contact check and external-action policy result.
- Suppressed or objected contacts cannot be overridden through the normal interface.

## 5. Engagements

### Engagement portfolio

- Client and engagement name.
- Engagement type and domain overlays.
- Current lifecycle stage.
- Operational state.
- Current gate.
- Decision deadline.
- Overall health.
- Material blockers.
- Latest approved deliverable.
- Cost to date.

### Engagement workspace

#### Decision header

- Executive decision.
- Decision owner.
- Deadline or gate.
- Current best answer and confidence.
- Consequence of no decision.

#### Lifecycle

- Thirteen-stage timeline.
- Current stage determined by earliest unmet gate.
- Entry and exit criteria.
- Gate history.
- Compressed stages and evidence.
- Regressions and reasons.
- Pause, recycle, stop and close controls.

#### Workstreams

- Objective and method stack.
- Work package state.
- Owner agent or human.
- Dependencies.
- Required evidence.
- Output and acceptance status.

#### Evidence and reasoning

- Question and hypothesis tree.
- Supporting and contradicting evidence.
- Assumptions and evidence gaps.
- Selected and rejected methods.
- Analysis and model runs.
- Confidence and falsifiers.

#### Quality

- Assurance tier.
- Current gate score.
- Dimension scores.
- Open defects by severity.
- Independent reviewer and sign-off.
- Exceptions and residual risk.

#### Implementation and benefits

- Recommendations to initiatives.
- Owners, milestones and dependencies.
- Adoption and outcome measures.
- Forecast and realised benefits.
- Scale, adapt, pause or stop decisions.

#### Audit

- Material commands and events.
- Approvals.
- Agent and tool runs.
- Version and release history.
- Cost and usage.

## 6. Founder decision inbox

### Decision card

- Decision required.
- Latest responsible date.
- Decision classes.
- Why it is reserved.
- Consequence of delay.
- Recommended option.
- Confidence and material assumptions.
- Action that follows approval.

### Decision detail

- Facts.
- Evidence gaps.
- Assumptions.
- Two or more viable options.
- Commercial, delivery, value and risk consequences.
- Recommendation and rationale.
- Fallback if no decision is made.
- Supporting records and artefacts.

### Actions

- Approve.
- Approve with conditions.
- Reject.
- Request targeted analysis.
- Pause engagement.

### Prohibited interaction patterns

- Generic approve button without consequences.
- Long transcript as the primary evidence.
- Hidden assumptions.
- Bundling unrelated material decisions into one approval.
- Presenting an agent recommendation as already authorised.

## 7. Deliverables

### Deliverable library

- Engagement and purpose.
- Surface: PPTX, DOCX, XLSX, PDF, SVG or HTML.
- Story and model baseline.
- Version and status.
- Quality gate.
- Reconciliation state.
- Release authority.

### Review workspace

- Rendered preview.
- Assertion and source drill-through.
- Number-to-model reconciliation.
- Open comments and defects.
- Cross-format comparison.
- Approve internal, Founder-ready or external-release state according to authority.

## 8. Methodology

### Canonical library

- Problem archetypes.
- Methods and aliases.
- Domains and sectors.
- Inputs, procedure and outputs.
- Compatibility, conflicts and rejected combinations.
- Evidence and reviewer requirements.
- Current version and source provenance.

### Candidate queue

- Discovery source and date.
- Claimed novelty.
- Existing-method comparison.
- Copyright, trademark and licence review.
- Original offdata reconstruction.
- Fixture and regression results.
- Promote, merge, reject, hold or supersede decision.

No candidate can be promoted through the same action that created it.

## 9. Operations

### System health

- Workflow failures and retries.
- Blocked integrations.
- Security incidents.
- Backup and restore status.
- Scheduled-job health.
- Provider availability.

### Cost

- Cost by engagement, agent, model, tool and deliverable.
- Monthly limits and forecast.
- Abnormal usage.
- Expensive runs without accepted output.

### Agent registry

- Agent purpose and version.
- Enabled tools.
- Data scope.
- Evaluations and latest pass date.
- Cost and reliability.
- Kill switch.

## 10. Settings

- Founder profile and delegated authorities.
- Regional data cells.
- Retention policies.
- Model-provider configuration.
- Integrations and credential references.
- Outreach policies.
- Brand and deliverable system.
- Notification preferences.
- Feature flags.

## 11. Initial screen priority

Phase 2 should implement only:

1. Home briefing shell.
2. Engagement portfolio.
3. Engagement decision header and lifecycle timeline.
4. Founder decision inbox.
5. Basic quality and blocker summary.
6. Audit-event list.

Opportunities, Methodology Radar, advanced deliverable review and benefits dashboards should use the same design system but arrive in their corresponding phases.

## 12. Acceptance criteria

- Founder can identify every pending material decision in under one minute.
- Founder can see why an engagement is at its current stage.
- Founder can distinguish waiting, blocked and retry conditions.
- Every approval shows the action that will follow.
- No client or prospect message can be sent from an unapproved screen state.
- Every displayed material claim and number can be drilled through to its source or model output.
- Routine agent activity does not dominate the interface.
- Interface is usable without reading code, logs or raw JSON.
