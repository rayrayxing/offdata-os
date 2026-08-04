import pytest

from offdata_core import (
    GateOutcome,
    LifecycleStage,
    OperationalState,
    TransitionRequest,
    detect_current_stage,
    evaluate_transition,
)


def test_missing_identity_stays_at_intake() -> None:
    result = detect_current_stage([], engagement_id_present=False)
    assert result.stage is LifecycleStage.MANDATE_INTAKE
    assert result.earliest_unmet_gate == "GATE-01"


def test_earliest_unmet_gate_selects_stage() -> None:
    result = detect_current_stage(["GATE-01", "GATE-02"])
    assert result.stage is LifecycleStage.RESEARCH_BASELINE
    assert result.earliest_unmet_gate == "GATE-03"


def test_compressed_stage_can_be_skipped_for_detection() -> None:
    result = detect_current_stage(
        ["GATE-01"], compressed_stages=[LifecycleStage.CONTEXT_PROBLEM]
    )
    assert result.stage is LifecycleStage.RESEARCH_BASELINE


def test_forward_transition_requires_current_gate() -> None:
    request = TransitionRequest(
        current_stage=LifecycleStage.MANDATE_INTAKE,
        target_stage=LifecycleStage.CONTEXT_PROBLEM,
        gate_outcome=GateOutcome.PROCEED,
    )
    result = evaluate_transition(request)
    assert not result.allowed
    assert result.resulting_state is OperationalState.BLOCKED


def test_forward_transition_passes_with_gate() -> None:
    request = TransitionRequest(
        current_stage=LifecycleStage.MANDATE_INTAKE,
        target_stage=LifecycleStage.CONTEXT_PROBLEM,
        gate_outcome=GateOutcome.PROCEED,
        completed_gates=frozenset({"GATE-01"}),
    )
    result = evaluate_transition(request)
    assert result.allowed
    assert result.resulting_stage is LifecycleStage.CONTEXT_PROBLEM


def test_silent_stage_skip_is_blocked() -> None:
    request = TransitionRequest(
        current_stage=LifecycleStage.MANDATE_INTAKE,
        target_stage=LifecycleStage.RESEARCH_BASELINE,
        gate_outcome=GateOutcome.PROCEED,
        completed_gates=frozenset({"GATE-01"}),
    )
    result = evaluate_transition(request)
    assert not result.allowed
    assert "silently skips" in result.reasons[0]


def test_documented_compression_allows_skip() -> None:
    request = TransitionRequest(
        current_stage=LifecycleStage.MANDATE_INTAKE,
        target_stage=LifecycleStage.RESEARCH_BASELINE,
        gate_outcome=GateOutcome.PROCEED,
        completed_gates=frozenset({"GATE-01"}),
        compressed_stages=frozenset({LifecycleStage.CONTEXT_PROBLEM}),
    )
    result = evaluate_transition(request)
    assert result.allowed


def test_recycle_requires_material_reason() -> None:
    with pytest.raises(ValueError, match="Regression requires"):
        TransitionRequest(
            current_stage=LifecycleStage.DELIVERY_ANALYSIS,
            target_stage=LifecycleStage.RESEARCH_BASELINE,
            gate_outcome=GateOutcome.RECYCLE,
        )


def test_recycle_returns_to_earlier_stage() -> None:
    request = TransitionRequest(
        current_stage=LifecycleStage.DELIVERY_ANALYSIS,
        target_stage=LifecycleStage.RESEARCH_BASELINE,
        gate_outcome=GateOutcome.RECYCLE,
        regression_reason="New evidence invalidated the governing assumption.",
    )
    result = evaluate_transition(request)
    assert result.allowed
    assert result.resulting_stage is LifecycleStage.RESEARCH_BASELINE


def test_stop_cancels_engagement() -> None:
    request = TransitionRequest(
        current_stage=LifecycleStage.DELIVERY_ANALYSIS,
        target_stage=LifecycleStage.DELIVERY_ANALYSIS,
        gate_outcome=GateOutcome.STOP,
    )
    result = evaluate_transition(request)
    assert result.allowed
    assert result.resulting_state is OperationalState.CANCELLED
