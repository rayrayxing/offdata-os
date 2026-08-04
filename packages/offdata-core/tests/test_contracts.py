from datetime import UTC, datetime

import pytest

from offdata_core.contracts import (
    AgentEnvelope,
    AgentStatus,
    ContextBudget,
    ContextPackage,
    Escalation,
    FounderDecisionPacket,
    FounderOption,
)
from offdata_core.models import DecisionClass, LifecycleStage


def test_successful_agent_envelope_can_be_minimal() -> None:
    envelope = AgentEnvelope(status=AgentStatus.SUCCESS, summary="Completed bounded task.")
    assert not envelope.escalation.required


def test_blocked_envelope_requires_gap_or_escalation() -> None:
    with pytest.raises(ValueError, match="must identify"):
        AgentEnvelope(status=AgentStatus.BLOCKED, summary="Cannot continue.")


def test_required_escalation_needs_class_and_reason() -> None:
    with pytest.raises(ValueError, match="decision class"):
        Escalation(required=True, reason="Material issue")


def test_context_package_requires_tool_allowlist() -> None:
    with pytest.raises(ValueError, match="tool allowlist"):
        ContextPackage(
            engagement_id="ENG-001",
            current_stage=LifecycleStage.MANDATE_INTAKE,
            objective="Produce a first-cut mandate.",
            decision={},
            permitted_tools=frozenset(),
            output_contract="agent-envelope-v1",
            approval_classes=frozenset({DecisionClass.ROUTINE}),
            budget=ContextBudget(timeout_seconds=60, max_retries=1),
        )


def test_founder_packet_requires_two_options() -> None:
    with pytest.raises(ValueError, match="at least two"):
        FounderDecisionPacket(
            decision_required="Approve pilot scope.",
            latest_responsible_date=datetime(2026, 8, 10, tzinfo=UTC),
            decision_classes=frozenset({DecisionClass.MATERIAL}),
            reserved_reason="Scope materially changes cost and outcome.",
            options=(FounderOption(option="Option A", consequences={}),),
            recommendation="Option A",
            resulting_action="Issue revised plan.",
            fallback="Pause mobilisation.",
        )


def test_founder_packet_rejects_routine_only() -> None:
    options = (
        FounderOption(option="A", consequences={}),
        FounderOption(option="B", consequences={}),
    )
    with pytest.raises(ValueError, match="reserved decision class"):
        FounderDecisionPacket(
            decision_required="Choose formatting.",
            latest_responsible_date=datetime(2026, 8, 10, tzinfo=UTC),
            decision_classes=frozenset({DecisionClass.ROUTINE}),
            reserved_reason="Routine choice.",
            options=options,
            recommendation="A",
            resulting_action="Format output.",
            fallback="Use default.",
        )
