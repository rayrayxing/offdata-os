"""Deterministic lifecycle stage detection and transition validation."""

from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import GateOutcome, LifecycleStage, OperationalState

STAGE_ORDER: tuple[LifecycleStage, ...] = tuple(LifecycleStage)
_STAGE_INDEX = {stage: index for index, stage in enumerate(STAGE_ORDER)}


def gate_id(stage: LifecycleStage) -> str:
    """Return the canonical exit-gate identifier for a lifecycle stage."""

    return f"GATE-{stage.value.removeprefix('LIFE-STAGE-')}"


class StageDetectionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    stage: LifecycleStage
    operational_state: OperationalState
    earliest_unmet_gate: str | None
    reasons: tuple[str, ...] = ()


class TransitionRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    current_stage: LifecycleStage
    target_stage: LifecycleStage
    gate_outcome: GateOutcome
    completed_gates: frozenset[str] = Field(default_factory=frozenset)
    compressed_stages: frozenset[LifecycleStage] = Field(default_factory=frozenset)
    regression_reason: str | None = None
    operational_state: OperationalState = OperationalState.NORMAL

    @model_validator(mode="after")
    def validate_regression_reason(self) -> "TransitionRequest":
        if _STAGE_INDEX[self.target_stage] < _STAGE_INDEX[self.current_stage]:
            if not self.regression_reason or not self.regression_reason.strip():
                raise ValueError("Regression requires a recorded material reason.")
        return self


class TransitionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    allowed: bool
    resulting_stage: LifecycleStage
    resulting_state: OperationalState
    reasons: tuple[str, ...]


def detect_current_stage(
    completed_gates: Iterable[str],
    *,
    compressed_stages: Iterable[LifecycleStage] = (),
    operational_state: OperationalState = OperationalState.NORMAL,
    engagement_id_present: bool = True,
    founder_present: bool = True,
) -> StageDetectionResult:
    """Detect current stage using the earliest unmet gate rule."""

    if operational_state is OperationalState.CANCELLED:
        return StageDetectionResult(
            stage=LifecycleStage.MANDATE_INTAKE,
            operational_state=operational_state,
            earliest_unmet_gate=None,
            reasons=("Engagement is cancelled; no progression is permitted.",),
        )

    if not engagement_id_present or not founder_present:
        missing = []
        if not engagement_id_present:
            missing.append("engagement identity")
        if not founder_present:
            missing.append("accountable Founder")
        return StageDetectionResult(
            stage=LifecycleStage.MANDATE_INTAKE,
            operational_state=operational_state,
            earliest_unmet_gate=gate_id(LifecycleStage.MANDATE_INTAKE),
            reasons=(f"Missing {', '.join(missing)}.",),
        )

    completed = set(completed_gates)
    compressed = set(compressed_stages)
    for stage in STAGE_ORDER:
        if stage in compressed:
            continue
        required_gate = gate_id(stage)
        if required_gate not in completed:
            return StageDetectionResult(
                stage=stage,
                operational_state=operational_state,
                earliest_unmet_gate=required_gate,
                reasons=("Selected by earliest unmet mandatory gate.",),
            )

    return StageDetectionResult(
        stage=LifecycleStage.EXPANSION_FOLLOW_ON,
        operational_state=OperationalState.COMPLETED,
        earliest_unmet_gate=None,
        reasons=("All lifecycle gates are complete.",),
    )


def evaluate_transition(request: TransitionRequest) -> TransitionResult:
    """Validate a requested stage transition without executing side effects."""

    current_index = _STAGE_INDEX[request.current_stage]
    target_index = _STAGE_INDEX[request.target_stage]

    if request.operational_state in {OperationalState.CANCELLED, OperationalState.COMPLETED}:
        return TransitionResult(
            allowed=False,
            resulting_stage=request.current_stage,
            resulting_state=request.operational_state,
            reasons=(f"No transition is permitted from {request.operational_state.value}.",),
        )

    if request.gate_outcome is GateOutcome.STOP:
        return TransitionResult(
            allowed=True,
            resulting_stage=request.current_stage,
            resulting_state=OperationalState.CANCELLED,
            reasons=("Authorised stop outcome cancels the engagement.",),
        )

    if request.gate_outcome is GateOutcome.PAUSE:
        return TransitionResult(
            allowed=target_index == current_index,
            resulting_stage=request.current_stage,
            resulting_state=OperationalState.WAITING,
            reasons=(
                "Pause retains the current stage and moves the engagement to waiting."
                if target_index == current_index
                else "Pause cannot advance or regress the lifecycle stage.",
            ),
        )

    if request.gate_outcome is GateOutcome.RECYCLE:
        if target_index >= current_index:
            return TransitionResult(
                allowed=False,
                resulting_stage=request.current_stage,
                resulting_state=OperationalState.BLOCKED,
                reasons=("Recycle must target an earlier affected stage.",),
            )
        return TransitionResult(
            allowed=True,
            resulting_stage=request.target_stage,
            resulting_state=OperationalState.NORMAL,
            reasons=(f"Regression authorised: {request.regression_reason}",),
        )

    if target_index < current_index:
        return TransitionResult(
            allowed=False,
            resulting_stage=request.current_stage,
            resulting_state=OperationalState.BLOCKED,
            reasons=("Backward movement requires the recycle gate outcome.",),
        )

    if target_index == current_index:
        return TransitionResult(
            allowed=request.gate_outcome is GateOutcome.PROCEED_WITH_CONDITIONS,
            resulting_stage=request.current_stage,
            resulting_state=(
                OperationalState.WAITING
                if request.gate_outcome is GateOutcome.PROCEED_WITH_CONDITIONS
                else OperationalState.BLOCKED
            ),
            reasons=(
                "Conditional proceed may retain the current stage while conditions are resolved."
                if request.gate_outcome is GateOutcome.PROCEED_WITH_CONDITIONS
                else "Proceed must advance to a successor stage.",
            ),
        )

    if request.gate_outcome is GateOutcome.CLOSE:
        allowed = request.current_stage in {
            LifecycleStage.CLOSEOUT_KNOWLEDGE,
            LifecycleStage.EXPANSION_FOLLOW_ON,
        }
        return TransitionResult(
            allowed=allowed,
            resulting_stage=request.target_stage if allowed else request.current_stage,
            resulting_state=OperationalState.COMPLETED if allowed else OperationalState.BLOCKED,
            reasons=(
                "Close outcome completes the engagement."
                if allowed
                else "Close is permitted only from closeout or expansion.",
            ),
        )

    if request.gate_outcome not in {
        GateOutcome.PROCEED,
        GateOutcome.PROCEED_WITH_CONDITIONS,
    }:
        return TransitionResult(
            allowed=False,
            resulting_stage=request.current_stage,
            resulting_state=OperationalState.BLOCKED,
            reasons=("Gate outcome does not authorise forward progression.",),
        )

    stages_between = STAGE_ORDER[current_index + 1 : target_index]
    missing_compression = [
        stage for stage in stages_between if stage not in request.compressed_stages
    ]
    if missing_compression:
        return TransitionResult(
            allowed=False,
            resulting_stage=request.current_stage,
            resulting_state=OperationalState.BLOCKED,
            reasons=(
                "Forward transition silently skips stages: "
                + ", ".join(stage.value for stage in missing_compression),
            ),
        )

    required_gate = gate_id(request.current_stage)
    if required_gate not in request.completed_gates:
        return TransitionResult(
            allowed=False,
            resulting_stage=request.current_stage,
            resulting_state=OperationalState.BLOCKED,
            reasons=(f"Current-stage exit gate {required_gate} is not complete.",),
        )

    return TransitionResult(
        allowed=True,
        resulting_stage=request.target_stage,
        resulting_state=(
            OperationalState.WAITING
            if request.gate_outcome is GateOutcome.PROCEED_WITH_CONDITIONS
            else OperationalState.NORMAL
        ),
        reasons=("Transition satisfies gate and compression rules.",),
    )
