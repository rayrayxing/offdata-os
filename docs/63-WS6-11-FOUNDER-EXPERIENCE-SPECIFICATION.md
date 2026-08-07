# WS6.11 — Founder experience specification

> [!CAUTION]
> **SPECIFIED, NOT IMPLEMENTED OR AUTHORISED.** This package defines future Founder
> review and decision-state contracts. It does not activate a runtime, create an
> authorization, enable external sending, or authorize Codex.

## Purpose

Every material Founder decision must be findable, explainable, evidence-linked,
versioned and explicitly authorized before any governed action executes.

- PCR-10 Founder criteria: `8/8`.
- Governed surfaces: `6`.
- Explicit decision/workflow states: `13`.
- Planned acceptance cases: `32`; registered/executable tests: `0`.
- `codex_start_authorized=false`.

The defect register suggested `docs/54-FOUNDER-EXPERIENCE-SPEC.md`, but numeric
prefix `54` is immutable WS6.2 evidence. This document is the canonical WS6.11
specification.

## Core invariants

- Recommendation is not authorization.
- Founder authorization is exact, versioned, scoped and append-only.
- Execution cannot begin before authorization where approval is required.
- Any record, preview or action-digest drift invalidates prior authorization.
- `stale` work requires re-review; it never continues under old authority.
- External sending is disabled by default and cannot be autonomous.
- Evidence drill-through is read-only with respect to authorization.
- Accessibility alternatives preserve identical authorization semantics.

## Founder surfaces

| Surface | Route | Purpose |
|---|---|---|
| `founder_cockpit` | `/founder` | Engagement overview, current stage, blockers, risks and pending material decisions. |
| `decision_inbox` | `/founder/decisions` | Single ordered queue of every pending material Founder decision. |
| `decision_packet` | `/founder/decisions/{decision_id}` | Versioned recommendation, consequences, evidence, exact action preview and Founder decision. |
| `lifecycle_state` | `/founder/engagements/{engagement_id}/lifecycle` | Stage, gate and explicit workflow-state history with next allowed action. |
| `evidence_drillthrough` | `/founder/evidence/{claim_or_output_id}` | Read-only trace from material claim/number to source passages and named model outputs. |
| `controlled_send` | `/founder/outreach/{draft_id}/approval` | Final preview and exact scoped authorization for any future external send. |

## Decision packet

A material decision packet must expose the exact recommendation, consequences,
deadline, reversibility, evidence, action preview, state and version before a
Founder action is possible.

Required fields:

- `decision_id`
- `engagement_id`
- `decision_class`
- `title`
- `recommendation`
- `recommendation_owner`
- `consequence_if_approved`
- `consequence_if_rejected`
- `deadline_at`
- `reversibility`
- `reversibility_details`
- `exact_next_action`
- `action_target`
- `action_parameters_digest`
- `side_effects`
- `evidence_refs`
- `model_output_refs`
- `blockers`
- `current_state`
- `record_version`
- `approval_scope_digest`
- `updated_at`

Unknown reversibility or any missing material field blocks authorization.

## Authorization contract

- `recommendation_is_authorization`: `false`
- `founder_only`: `true`
- `exact_preview_required`: `true`
- `execution_before_authorization`: `false`
- `scope_fields`: `["decision_id", "record_version", "action_id", "action_parameters_digest", "next_action", "authorization_expires_at"]`
- `version_drift_invalidates`: `true`
- `preview_drift_invalidates`: `true`
- `stale_invalidates`: `true`
- `expiry_invalidates`: `true`
- `authorization_record_append_only`: `true`

## Explicit states

| State | Terminal | Meaning |
|---|:---:|---|
| `draft` | `false` | Decision record exists but has no reviewable recommendation. |
| `recommended` | `false` | A recommendation exists but grants no authority. |
| `pending_authorization` | `false` | Founder decision is required before the exact previewed action may execute. |
| `authorized` | `false` | Founder approved the exact versioned action scope; execution has not yet started. |
| `executing` | `false` | Only the exact authorized action is executing. |
| `waiting` | `false` | Progress is paused for a known dependency or scheduled condition. |
| `blocked` | `false` | Progress is prohibited until an explicit blocker is resolved. |
| `retrying` | `false` | A bounded retry is in progress after a retryable failure. |
| `failed` | `true` | Execution stopped on a terminal or exhausted failure and requires review. |
| `stale` | `false` | Inputs or action scope changed; prior authorization is invalid. |
| `complete` | `true` | The exact authorized action completed and evidence is recorded. |
| `rejected` | `true` | Founder rejected the recommendation or requested action. |
| `cancelled` | `true` | The decision/action was cancelled and cannot continue without a new scope. |

At minimum, `waiting`, `blocked`, `retrying`, `failed`, `stale` and `complete`
must remain visually and semantically distinct.

## Evidence drill-through

Material claims and numbers must resolve to versioned evidence references and/or
named model outputs while preserving the originating decision context. Unsupported
material items remain visibly unsupported. Drill-through cannot mutate decision state.

## Accessibility

- Target: `WCAG_2_2_AA`.
- Minimum normal-text contrast: `4.5:1`.
- Minimum large-text contrast: `3.0:1`.
- All Founder tasks are keyboard-completable with visible focus and readable errors.
- State changes are announced without unexpected focus loss.
- No authorization shortcut may exist for an alternate input mode.

## Controlled external send

Client/prospect sending remains disabled unless the current version has exact scoped
Founder authorization and a final recipient/channel/content preview. Recipient,
content or action drift invalidates authorization. Autonomous sending remains prohibited.

## Criterion contracts

| Criterion | Phase/task | Component | Surface | Planned cases |
|---|---|---|---|---:|
| `FX-INBOX` | `IMP-P2` / `P2.4` | `COMP-UI` | `decision_inbox` | `4` |
| `FX-CONSEQUENCE` | `IMP-P2` / `P2.4` | `COMP-UI` | `decision_packet` | `4` |
| `FX-AUTH` | `IMP-P3` / `P3.3` | `COMP-UI` | `decision_packet` | `4` |
| `FX-PREVIEW` | `IMP-P3` / `P3.3` | `COMP-UI` | `decision_packet` | `4` |
| `FX-EVIDENCE` | `IMP-P5` / `P5.3` | `COMP-KNOWLEDGE` | `evidence_drillthrough` | `4` |
| `FX-STATES` | `IMP-P3` / `P3.4` | `COMP-UI` | `lifecycle_state` | `4` |
| `FX-ACCESS` | `IMP-P3` / `P3.4` | `COMP-UI` | `founder_cockpit` | `4` |
| `FX-SEND` | `IMP-P9` / `P9.4` | `COMP-API` | `controlled_send` | `4` |

### `FX-INBOX`

- Owner: `IMP-P2` / `P2.4` / `COMP-UI`.
- Surface: `decision_inbox`.
- Required fields: `decision_id`, `engagement_id`, `title`, `decision_class`, `current_state`, `urgency`, `deadline_at`, `blockers`, `updated_at`.
- Invariants: `all_pending_material_decisions_visible`, `target_scan_seconds_60`, `stale_state_visible`.

| Case | Scenario |
|---|---|
| `happy_path` | With multiple engagements and mixed priorities, every pending material decision appears in one inbox with urgency, deadline, stage and blocker context; a reviewer can identify all pending material decisions within 60 seconds. |
| `missing_required_data` | A material decision missing deadline, engagement identity or current state is visibly incomplete and cannot be silently omitted from the inbox. |
| `authorization_safety` | Recommendations shown in the inbox never expose an execution control as if authorization already exists. |
| `stale_or_version_drift` | When a decision becomes stale or changes version, its inbox state and urgency update and any prior authorization is visibly invalid. |

### `FX-CONSEQUENCE`

- Owner: `IMP-P2` / `P2.4` / `COMP-UI`.
- Surface: `decision_packet`.
- Required fields: `consequence_if_approved`, `consequence_if_rejected`, `deadline_at`, `reversibility`, `reversibility_details`.
- Invariants: `missing_material_consequence_blocks_authorization`, `unknown_reversibility_blocks_authorization`.

| Case | Scenario |
|---|---|
| `happy_path` | A decision packet shows consequences of approval and rejection, deadline, reversibility class and reversibility detail before a Founder choice is available. |
| `missing_required_data` | If consequence, deadline or reversibility data is missing, the packet is marked incomplete and authorization is blocked. |
| `authorization_safety` | Unknown reversibility or missing material consequence cannot be bypassed by recommendation confidence or UI defaults. |
| `stale_or_version_drift` | Changing consequence, deadline or reversibility creates a new record version and invalidates prior authorization. |

### `FX-AUTH`

- Owner: `IMP-P3` / `P3.3` / `COMP-UI`.
- Surface: `decision_packet`.
- Required fields: `decision_id`, `record_version`, `action_id`, `action_parameters_digest`, `next_action`, `authorization_expires_at`, `authorized_by`, `authorized_at`.
- Invariants: `recommendation_never_authorizes`, `founder_only_authorization`, `authorization_is_exact_scope`.

| Case | Scenario |
|---|---|
| `happy_path` | Recommendation and Founder authorization use distinct labels, visual treatments, audit fields and actions; only Founder authorization creates an authorization record. |
| `missing_required_data` | An authorization attempt without decision ID, record version, action ID, parameters digest, next action and expiry is rejected. |
| `authorization_safety` | Recommendation, agent output, workflow state or prior approval never implicitly grants authorization. |
| `stale_or_version_drift` | Any record-version or action-digest drift changes state to stale and invalidates authorization. |

### `FX-PREVIEW`

- Owner: `IMP-P3` / `P3.3` / `COMP-UI`.
- Surface: `decision_packet`.
- Required fields: `action_type`, `action_target`, `action_parameters_digest`, `side_effects`, `externality`, `reversibility`, `rollback_path`.
- Invariants: `preview_before_authorization`, `execution_matches_approved_scope`, `preview_change_invalidates_authorization`.

| Case | Scenario |
|---|---|
| `happy_path` | Before authorization, the packet previews exact action type, target, parameters digest, side effects, externality, reversibility and rollback path. |
| `missing_required_data` | Authorization controls remain disabled when the exact next action or its target/digest/side effects are incomplete. |
| `authorization_safety` | Execution cannot begin from preview alone and must match the approved action scope byte-for-byte. |
| `stale_or_version_drift` | A preview change after authorization marks the decision stale and requires a new Founder decision. |

### `FX-EVIDENCE`

- Owner: `IMP-P5` / `P5.3` / `COMP-KNOWLEDGE`.
- Surface: `evidence_drillthrough`.
- Required fields: `claim_id`, `materiality`, `evidence_refs`, `model_output_refs`, `source_version_refs`.
- Invariants: `material_items_have_resolvable_drillthrough`, `drillthrough_preserves_context`, `drillthrough_is_read_only`.

| Case | Scenario |
|---|---|
| `happy_path` | Every material claim and number opens a drill-through preserving decision context and resolving to source passages and/or named model outputs. |
| `missing_required_data` | A material claim or number without resolvable evidence/model references is visibly unsupported and cannot be presented as verified. |
| `authorization_safety` | Evidence drill-through is read-only with respect to authorization and cannot mutate canonical decision state. |
| `stale_or_version_drift` | Changed source/model versions are surfaced as stale and require evidence revalidation before relying on the prior packet. |

### `FX-STATES`

- Owner: `IMP-P3` / `P3.4` / `COMP-UI`.
- Surface: `lifecycle_state`.
- Required fields: `current_state`, `state_reason`, `state_owner`, `state_changed_at`, `correlation_id`, `next_allowed_action`.
- Invariants: `six_required_states_distinct`, `transition_history_append_only`, `approval_gate_not_skippable`.

| Case | Scenario |
|---|---|
| `happy_path` | Waiting, blocked, retrying, failed, stale and complete are visually and semantically distinct, with reason, owner and next allowed action. |
| `missing_required_data` | A state transition without actor, reason, timestamp and correlation ID is rejected from canonical history. |
| `authorization_safety` | No state transition can skip pending authorization when Founder approval is required. |
| `stale_or_version_drift` | Input or scope drift transitions authorized work to stale rather than continuing execution under old authority. |

### `FX-ACCESS`

- Owner: `IMP-P3` / `P3.4` / `COMP-UI`.
- Surface: `founder_cockpit`.
- Required fields: `accessible_name`, `focus_order`, `focus_visible`, `status_semantics`, `error_association`.
- Invariants: `keyboard_complete`, `wcag_2_2_aa`, `no_color_only`, `authorization_parity_across_input_modes`.

| Case | Scenario |
|---|---|
| `happy_path` | All Founder review, drill-through and approval tasks are completable by keyboard with visible focus, readable labels, compliant contrast and accessible status/error semantics. |
| `missing_required_data` | Controls lacking an accessible name, focus behavior or readable error association fail acceptance. |
| `authorization_safety` | Accessibility alternatives preserve the same authorization confirmation and do not introduce a shortcut around approval. |
| `stale_or_version_drift` | Dynamic stale/state changes announce updated status without moving focus unexpectedly or hiding the required reauthorization action. |

### `FX-SEND`

- Owner: `IMP-P9` / `P9.4` / `COMP-API`.
- Surface: `controlled_send`.
- Required fields: `recipient`, `channel`, `content_digest`, `authorization_scope_digest`, `suppression_status`, `frequency_status`, `final_preview_confirmed`.
- Invariants: `send_default_disabled`, `exact_authorization_required`, `stale_or_mismatch_denies_send`, `no_autonomous_send`.

| Case | Scenario |
|---|---|
| `happy_path` | A client/prospect send control becomes available only after exact scoped Founder authorization and still requires a final preview/confirmation of recipient, channel and content digest. |
| `missing_required_data` | Missing recipient, channel, content digest, suppression check, frequency check or authorization keeps sending disabled. |
| `authorization_safety` | Unauthorized, expired, stale, mismatched or recommendation-only states cannot invoke any external-send adapter. |
| `stale_or_version_drift` | Recipient/content/action changes invalidate send authorization and require a fresh Founder decision. |

## Completion boundary

WS6.11 closes only `WS6-QUALITY-003`. It does not implement the Founder cockpit,
register executable tests, satisfy implementation evidence, authorize external
sending, or alter any Codex/IMP-P0 boundary. `WS6-CODEXPREP-002` and
`WS6-BLOCK-006` remain open.

The next permitted package is WS6.12 after the governed WS6.8 → WS6.9 → WS6.10
→ WS6.11 integration sequence.

## Rollback

Before merge, close the WS6.11 pull request and delete only its branch. After merge,
revert this specification package as one unit. No Founder runtime exists to roll back.
