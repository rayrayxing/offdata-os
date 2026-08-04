from datetime import UTC, datetime, timedelta

import pytest

from offdata_core.events import (
    ActorRef,
    ActorType,
    ApprovalOutcome,
    ApprovalRecord,
    ApprovalRequest,
    CommandEnvelope,
    CommandType,
)
from offdata_core.models import DecisionClass


NOW = datetime(2026, 8, 4, tzinfo=UTC)
ACTOR = ActorRef(actor_id="founder-1", actor_type=ActorType.FOUNDER)


def test_non_create_command_requires_engagement_scope() -> None:
    with pytest.raises(ValueError, match="engagement_id"):
        CommandEnvelope(
            command_id="CMD-1",
            command_type=CommandType.UPDATE_MANDATE,
            occurred_at=NOW,
            actor=ACTOR,
            tenant_id="TEN-1",
            correlation_id="COR-1",
            payload={},
        )


def test_side_effect_command_requires_idempotency() -> None:
    with pytest.raises(ValueError, match="idempotency"):
        CommandEnvelope(
            command_id="CMD-2",
            command_type=CommandType.EXECUTE_EXTERNAL_ACTION,
            occurred_at=NOW,
            actor=ACTOR,
            tenant_id="TEN-1",
            engagement_id="ENG-1",
            expected_version=1,
            correlation_id="COR-1",
            payload={},
        )


def test_non_create_command_requires_expected_version() -> None:
    with pytest.raises(ValueError, match="expected_version"):
        CommandEnvelope(
            command_id="CMD-3",
            command_type=CommandType.UPDATE_MANDATE,
            occurred_at=NOW,
            actor=ACTOR,
            tenant_id="TEN-1",
            engagement_id="ENG-1",
            correlation_id="COR-1",
            payload={},
        )


def test_routine_only_approval_request_is_invalid() -> None:
    with pytest.raises(ValueError, match="reserved decision class"):
        ApprovalRequest(
            approval_request_id="APR-1",
            engagement_id="ENG-1",
            requested_at=NOW,
            requested_by=ACTOR,
            decision_classes=frozenset({DecisionClass.ROUTINE}),
            decision_required="Choose formatting.",
            supporting_packet_reference="PACK-1",
            required_approver_roles=("Founder",),
            latest_responsible_date=NOW + timedelta(days=1),
        )


def test_conditional_approval_requires_conditions() -> None:
    with pytest.raises(ValueError, match="explicit conditions"):
        ApprovalRecord(
            approval_id="APP-1",
            approval_request_id="APR-1",
            engagement_id="ENG-1",
            decided_at=NOW,
            decided_by=ACTOR,
            outcome=ApprovalOutcome.CONDITIONAL,
            evidence_reference="DECISION-LOG-1",
        )
