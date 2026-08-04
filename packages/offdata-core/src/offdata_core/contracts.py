"""Typed context, agent-output and Founder-decision contracts."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .models import DecisionClass, LifecycleStage, OperationalState


class AgentStatus(StrEnum):
    SUCCESS = "success"
    PARTIAL = "partial"
    BLOCKED = "blocked"
    FAILED = "failed"


class RecordOperation(StrEnum):
    PROPOSE_CREATE = "propose_create"
    PROPOSE_UPDATE = "propose_update"
    PROPOSE_ARCHIVE = "propose_archive"


class QualityResult(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    NOT_APPLICABLE = "not_applicable"


class RecordChange(BaseModel):
    model_config = ConfigDict(frozen=True)

    record_type: str = Field(min_length=1)
    record_id: str | None = None
    operation: RecordOperation
    payload: dict[str, Any]
    reason: str = ""


class QualityCheck(BaseModel):
    model_config = ConfigDict(frozen=True)

    check_id: str = Field(min_length=1)
    result: QualityResult
    details: str = ""


class Escalation(BaseModel):
    model_config = ConfigDict(frozen=True)

    required: bool
    decision_classes: frozenset[DecisionClass] = Field(default_factory=frozenset)
    reason: str = ""
    latest_responsible_date: datetime | None = None

    @model_validator(mode="after")
    def validate_required_details(self) -> "Escalation":
        if self.required:
            if not self.decision_classes:
                raise ValueError("Required escalation must identify at least one decision class.")
            if not self.reason.strip():
                raise ValueError("Required escalation must state a reason.")
        return self


class UsageRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    model: str = ""
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    estimated_cost: float = Field(default=0.0, ge=0)
    currency: str = "USD"


class AgentEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: AgentStatus
    summary: str = Field(min_length=1)
    artifacts: tuple[str, ...] = ()
    record_changes: tuple[RecordChange, ...] = ()
    assumptions: tuple[str, ...] = ()
    evidence_gaps: tuple[str, ...] = ()
    contradicting_evidence: tuple[str, ...] = ()
    quality_checks: tuple[QualityCheck, ...] = ()
    escalation: Escalation = Field(default_factory=lambda: Escalation(required=False))
    notes_for_next_actor: str = ""
    usage: UsageRecord | None = None

    @model_validator(mode="after")
    def validate_blocked_or_failed_output(self) -> "AgentEnvelope":
        if self.status in {AgentStatus.BLOCKED, AgentStatus.FAILED}:
            if not self.escalation.required and not self.evidence_gaps:
                raise ValueError(
                    "Blocked or failed output must identify an escalation or evidence gap."
                )
        return self


class ContextBudget(BaseModel):
    model_config = ConfigDict(frozen=True)

    timeout_seconds: int = Field(gt=0)
    max_retries: int = Field(ge=0)
    max_input_tokens: int | None = Field(default=None, ge=0)
    max_output_tokens: int | None = Field(default=None, ge=0)
    max_cost: float | None = Field(default=None, ge=0)
    currency: str = "USD"


class ContextPackage(BaseModel):
    model_config = ConfigDict(frozen=True)

    engagement_id: str = Field(min_length=1)
    current_stage: LifecycleStage
    operational_state: OperationalState = OperationalState.NORMAL
    objective: str = Field(min_length=1)
    decision: dict[str, Any]
    constraints: tuple[str, ...] = ()
    relevant_methods: tuple[str, ...] = ()
    relevant_claims: tuple[str, ...] = ()
    evidence_summary: tuple[str, ...] = ()
    evidence_gaps: tuple[str, ...] = ()
    approved_assumptions: tuple[str, ...] = ()
    prior_outputs: tuple[str, ...] = ()
    permitted_tools: frozenset[str]
    prohibited_actions: frozenset[str] = Field(default_factory=frozenset)
    output_contract: str = Field(min_length=1)
    quality_rubric: tuple[str, ...] = ()
    approval_classes: frozenset[DecisionClass]
    budget: ContextBudget

    @field_validator("permitted_tools")
    @classmethod
    def require_explicit_tool_scope(cls, value: frozenset[str]) -> frozenset[str]:
        if not value:
            raise ValueError("Context package must include an explicit tool allowlist.")
        return value


class FounderOption(BaseModel):
    model_config = ConfigDict(frozen=True)

    option: str = Field(min_length=1)
    consequences: dict[str, Any]
    risks: tuple[str, ...] = ()
    conditions: tuple[str, ...] = ()


class FounderDecisionPacket(BaseModel):
    model_config = ConfigDict(frozen=True)

    decision_required: str = Field(min_length=1)
    latest_responsible_date: datetime
    decision_classes: frozenset[DecisionClass]
    reserved_reason: str = Field(min_length=1)
    consequence_of_delay: str = ""
    facts: tuple[str, ...] = ()
    evidence_gaps: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    options: tuple[FounderOption, ...]
    recommendation: str = Field(min_length=1)
    rationale: tuple[str, ...] = ()
    resulting_action: str = Field(min_length=1)
    fallback: str = Field(min_length=1)

    @field_validator("decision_classes")
    @classmethod
    def exclude_routine_only(cls, value: frozenset[DecisionClass]) -> frozenset[DecisionClass]:
        if not value or value == {DecisionClass.ROUTINE}:
            raise ValueError("Founder packet requires at least one reserved decision class.")
        return value

    @field_validator("options")
    @classmethod
    def require_meaningful_choice(
        cls, value: tuple[FounderOption, ...]
    ) -> tuple[FounderOption, ...]:
        if len(value) < 2:
            raise ValueError("Founder packet must present at least two viable options.")
        return value
