"""Pydantic-first API request, response and read-model contracts."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .events import ActorRef
from .models import DecisionClass, LifecycleStage, OperationalState
from .quality import AssuranceTier


class EngagementStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class CommandDisposition(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PENDING_APPROVAL = "pending_approval"
    CONFLICT = "conflict"
    FAILED = "failed"


class ApiError(BaseModel):
    """Stable error payload returned by every API operation."""

    model_config = ConfigDict(frozen=True)

    error_id: str = Field(min_length=1)
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    details: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str = Field(min_length=1)
    retryable: bool = False


class ApprovalRequirement(BaseModel):
    """Approval information returned instead of executing a reserved action."""

    model_config = ConfigDict(frozen=True)

    decision_classes: frozenset[DecisionClass]
    required_approver_roles: tuple[str, ...]
    supporting_packet_reference: str = Field(min_length=1)
    latest_responsible_date: datetime
    reason: str = Field(min_length=1)

    @field_validator("decision_classes")
    @classmethod
    def require_reserved_class(
        cls, value: frozenset[DecisionClass]
    ) -> frozenset[DecisionClass]:
        if not value or value == {DecisionClass.ROUTINE}:
            raise ValueError("Approval requirement needs a reserved decision class.")
        return value

    @field_validator("required_approver_roles")
    @classmethod
    def require_approver(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value:
            raise ValueError("At least one approver role is required.")
        return value


class CommandResponse(BaseModel):
    """Result of submitting a command to an aggregate."""

    model_config = ConfigDict(frozen=True)

    command_id: str = Field(min_length=1)
    status: CommandDisposition
    aggregate_id: str | None = None
    aggregate_version: int | None = Field(default=None, ge=1)
    event_ids: tuple[str, ...] = ()
    errors: tuple[ApiError, ...] = ()
    approval_requirement: ApprovalRequirement | None = None

    @model_validator(mode="after")
    def validate_disposition(self) -> "CommandResponse":
        if self.status is CommandDisposition.ACCEPTED:
            if not self.aggregate_id or self.aggregate_version is None:
                raise ValueError("Accepted command requires aggregate identity and version.")
            if not self.event_ids:
                raise ValueError("Accepted command requires at least one emitted event.")
            if self.errors:
                raise ValueError("Accepted command cannot contain errors.")
        if self.status is CommandDisposition.PENDING_APPROVAL:
            if self.approval_requirement is None:
                raise ValueError("Pending approval requires approval_requirement.")
        elif self.approval_requirement is not None:
            raise ValueError("approval_requirement is valid only for pending approval.")
        if self.status in {
            CommandDisposition.REJECTED,
            CommandDisposition.CONFLICT,
            CommandDisposition.FAILED,
        } and not self.errors:
            raise ValueError("Rejected, conflict or failed command requires an error.")
        return self


class EngagementCreateRequest(BaseModel):
    """Founder-authorised request to initialise an engagement aggregate."""

    model_config = ConfigDict(frozen=True)

    engagement_code: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=240)
    client_organisation_id: str = Field(min_length=1)
    supported_decision: str = Field(min_length=1)
    decision_owner: str = Field(min_length=1)
    data_region: str = Field(min_length=2, max_length=32)
    assurance_tier: AssuranceTier = AssuranceTier.T1_MODERATE
    created_by: ActorRef
    initial_mandate: dict[str, Any] = Field(default_factory=dict)

    @field_validator("data_region")
    @classmethod
    def normalise_region(cls, value: str) -> str:
        normalised = value.strip().lower()
        if not normalised:
            raise ValueError("data_region cannot be blank.")
        return normalised


class EngagementView(BaseModel):
    """Canonical API representation of an engagement."""

    model_config = ConfigDict(frozen=True)

    engagement_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    engagement_code: str = Field(min_length=1)
    title: str = Field(min_length=1)
    client_organisation_id: str = Field(min_length=1)
    status: EngagementStatus
    lifecycle_stage: LifecycleStage
    operational_state: OperationalState
    assurance_tier: AssuranceTier
    data_region: str = Field(min_length=1)
    supported_decision: str = Field(min_length=1)
    version: int = Field(ge=1)
    created_at: datetime
    created_by: ActorRef
    updated_at: datetime

    @model_validator(mode="after")
    def validate_status_alignment(self) -> "EngagementView":
        if self.operational_state is OperationalState.CANCELLED:
            if self.status is not EngagementStatus.CANCELLED:
                raise ValueError("Cancelled operational state requires cancelled status.")
        if self.operational_state is OperationalState.COMPLETED:
            if self.status not in {EngagementStatus.COMPLETED, EngagementStatus.ARCHIVED}:
                raise ValueError(
                    "Completed operational state requires completed or archived status."
                )
        return self


class EngagementListResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: tuple[EngagementView, ...]
    next_cursor: str | None = None
    total: int = Field(ge=0)


class TimelineItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    item_id: str = Field(min_length=1)
    item_type: str = Field(min_length=1)
    occurred_at: datetime
    actor: ActorRef
    title: str = Field(min_length=1)
    summary: str = ""
    correlation_id: str = Field(min_length=1)
    references: tuple[str, ...] = ()


class FounderEngagementSummary(BaseModel):
    """Minimum read model for the Founder cockpit."""

    model_config = ConfigDict(frozen=True)

    engagement_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    client_organisation_id: str = Field(min_length=1)
    supported_decision: str = Field(min_length=1)
    lifecycle_stage: LifecycleStage
    operational_state: OperationalState
    current_gate: str | None = None
    blockers: tuple[str, ...] = ()
    pending_founder_decision_ids: tuple[str, ...] = ()
    evidence_gaps: tuple[str, ...] = ()
    material_assumptions: tuple[str, ...] = ()
    quality_status: str = Field(min_length=1)
    next_best_action: str = Field(min_length=1)
    recent_activity: tuple[TimelineItem, ...] = ()
    run_cost: float = Field(default=0.0, ge=0)
    run_cost_currency: str = "USD"
    last_updated_at: datetime


class DecisionInboxOption(BaseModel):
    model_config = ConfigDict(frozen=True)

    option_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    consequences: tuple[str, ...]
    risks: tuple[str, ...] = ()
    conditions: tuple[str, ...] = ()


class DecisionInboxItem(BaseModel):
    """Decision packet shaped for the Founder cockpit."""

    model_config = ConfigDict(frozen=True)

    decision_id: str = Field(min_length=1)
    engagement_id: str = Field(min_length=1)
    decision_required: str = Field(min_length=1)
    latest_responsible_date: datetime
    decision_classes: frozenset[DecisionClass]
    reserved_reason: str = Field(min_length=1)
    facts: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    evidence_gaps: tuple[str, ...] = ()
    options: tuple[DecisionInboxOption, ...]
    recommendation: str = Field(min_length=1)
    resulting_commitment: str = Field(min_length=1)
    fallback: str = Field(min_length=1)
    approval_request_id: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_decision_packet(self) -> "DecisionInboxItem":
        if len(self.options) < 2:
            raise ValueError("Decision inbox item requires at least two viable options.")
        if not self.decision_classes or self.decision_classes == {DecisionClass.ROUTINE}:
            raise ValueError("Decision inbox item requires a reserved decision class.")
        return self


class RecordCollectionResponse(BaseModel):
    """Generic collection response for record families not yet given specialised views."""

    model_config = ConfigDict(frozen=True)

    record_type: str = Field(min_length=1)
    items: tuple[dict[str, Any], ...]
    next_cursor: str | None = None
    total: int = Field(ge=0)


class HealthResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: str = Field(pattern="^(ok|degraded)$")
    service: str = "offdata-api"
    version: str = Field(min_length=1)
    checked_at: datetime
    dependencies: dict[str, str] = Field(default_factory=dict)
