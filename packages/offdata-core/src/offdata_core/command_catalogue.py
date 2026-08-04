"""Deterministic command and event catalogue builder."""

from typing import Any

from .contract_constants import CONTRACT_VERSION


def build_command_event_catalogue() -> dict[str, Any]:
    """Return the deterministic command/event routing and control catalogue."""

    commands: dict[str, Any] = {
        "create_engagement": {
            "requires_engagement_id": False,
            "idempotency": "recommended",
            "allowed_actor_types": ["founder", "user", "system"],
            "decision_classes": ["DEC-MATERIAL"],
            "approval": "Founder-approved mandate or delegated creation authority",
            "success_events": ["engagement_created"],
            "failure_events": ["workflow_blocked"],
            "requirements": ["DATA-001", "DATA-002", "AUTH-003"],
        },
        "update_mandate": {
            "requires_engagement_id": True,
            "idempotency": "recommended",
            "allowed_actor_types": ["founder", "user", "agent"],
            "decision_classes": ["DEC-ROUTINE", "DEC-MATERIAL"],
            "approval": "Required when scope, intended use, deadline, fee or commitment changes",
            "success_events": ["mandate_updated"],
            "failure_events": ["workflow_blocked"],
            "requirements": ["OUT-002", "AUTH-003", "DATA-003"],
        },
        "propose_transition": {
            "requires_engagement_id": True,
            "idempotency": "recommended",
            "allowed_actor_types": ["founder", "user", "agent", "system"],
            "decision_classes": ["DEC-ROUTINE", "DEC-MATERIAL"],
            "approval": "Deterministic gate; Founder approval where gate is reserved",
            "success_events": ["transition_proposed", "transition_accepted"],
            "failure_events": ["transition_proposed", "transition_rejected", "workflow_blocked"],
            "requirements": ["LIFE-002", "LIFE-003", "LIFE-004", "AUTH-003"],
        },
        "request_approval": {
            "requires_engagement_id": True,
            "idempotency": "required",
            "allowed_actor_types": ["user", "agent", "system"],
            "decision_classes": [
                "DEC-MATERIAL",
                "DEC-EXTERNAL",
                "DEC-COMMERCIAL",
                "DEC-LEGALREG",
                "DEC-IRREVERSIBLE",
            ],
            "approval": "Creates a request only; does not grant authority",
            "success_events": ["approval_requested"],
            "failure_events": ["workflow_blocked"],
            "requirements": ["AUTH-001", "AUTH-009", "DATA-004"],
        },
        "record_approval": {
            "requires_engagement_id": True,
            "idempotency": "required",
            "allowed_actor_types": ["founder", "user"],
            "decision_classes": [
                "DEC-MATERIAL",
                "DEC-EXTERNAL",
                "DEC-COMMERCIAL",
                "DEC-LEGALREG",
                "DEC-IRREVERSIBLE",
            ],
            "approval": "Approver identity and scope are validated before recording",
            "success_events": ["approval_recorded", "workflow_resumed"],
            "failure_events": ["workflow_blocked"],
            "requirements": ["AUTH-003", "AUTH-004", "AUTH-005", "AUTH-007", "DATA-004"],
        },
        "propose_external_action": {
            "requires_engagement_id": True,
            "idempotency": "required",
            "allowed_actor_types": ["founder", "user", "agent", "system"],
            "decision_classes": ["DEC-EXTERNAL"],
            "approval": "Proposal only; exact external action must be scoped in approval",
            "success_events": ["external_action_proposed", "approval_requested"],
            "failure_events": ["workflow_blocked"],
            "requirements": ["AUTH-004", "SEC-002"],
        },
        "execute_external_action": {
            "requires_engagement_id": True,
            "idempotency": "required",
            "allowed_actor_types": ["founder", "user", "integration", "system"],
            "decision_classes": ["DEC-EXTERNAL"],
            "approval": "Exact current-version action requires unexpired scoped approval",
            "success_events": ["external_action_executed"],
            "failure_events": ["workflow_blocked"],
            "requirements": ["AUTH-004", "LIFE-007", "DATA-004"],
        },
        "cancel_engagement": {
            "requires_engagement_id": True,
            "idempotency": "required",
            "allowed_actor_types": ["founder", "user"],
            "decision_classes": ["DEC-MATERIAL", "DEC-IRREVERSIBLE"],
            "approval": "Founder or delegated accountable owner",
            "success_events": ["engagement_cancelled"],
            "failure_events": ["workflow_blocked"],
            "requirements": ["LIFE-009", "AUTH-007", "DATA-004"],
        },
        "record_agent_output": {
            "requires_engagement_id": True,
            "idempotency": "required",
            "allowed_actor_types": ["agent", "system"],
            "decision_classes": ["DEC-ROUTINE"],
            "approval": "Output remains proposed until canonical command validation succeeds",
            "success_events": ["agent_output_recorded"],
            "failure_events": ["defect_recorded", "workflow_blocked"],
            "requirements": ["AGENT-003", "AGENT-004", "AGENT-005", "DATA-004"],
        },
        "release_artefact": {
            "requires_engagement_id": True,
            "idempotency": "required",
            "allowed_actor_types": ["founder", "user", "system"],
            "decision_classes": ["DEC-EXTERNAL", "DEC-MATERIAL"],
            "approval": "Release gate, scoped approval and immutable baselines required",
            "success_events": ["artefact_released"],
            "failure_events": ["defect_recorded", "workflow_blocked"],
            "requirements": ["DELIV-003", "DELIV-010", "QA-002", "AUTH-004"],
        },
    }

    events: dict[str, Any] = {
        "engagement_created": {"aggregate_change": True, "replay_required": True},
        "mandate_updated": {"aggregate_change": True, "replay_required": True},
        "transition_proposed": {"aggregate_change": False, "replay_required": True},
        "transition_accepted": {"aggregate_change": True, "replay_required": True},
        "transition_rejected": {"aggregate_change": False, "replay_required": True},
        "approval_requested": {"aggregate_change": True, "replay_required": True},
        "approval_recorded": {"aggregate_change": True, "replay_required": True},
        "external_action_proposed": {"aggregate_change": True, "replay_required": True},
        "external_action_executed": {
            "aggregate_change": True,
            "replay_required": True,
            "non_repeatable_side_effect": True,
        },
        "engagement_cancelled": {"aggregate_change": True, "replay_required": True},
        "agent_output_recorded": {"aggregate_change": True, "replay_required": True},
        "artefact_released": {
            "aggregate_change": True,
            "replay_required": True,
            "non_repeatable_side_effect": True,
        },
        "defect_recorded": {"aggregate_change": True, "replay_required": True},
        "workflow_blocked": {"aggregate_change": True, "replay_required": True},
        "workflow_resumed": {"aggregate_change": True, "replay_required": True},
    }

    return {
        "version": CONTRACT_VERSION,
        "command_schema": "../schemas/offdata-contract-bundle.schema.json#/$defs/CommandEnvelope",
        "event_schema": "../schemas/offdata-contract-bundle.schema.json#/$defs/DomainEvent",
        "commands": commands,
        "events": events,
    }
