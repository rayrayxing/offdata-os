"""Command, event and approval records for the offdata control plane."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import DecisionClass


class ActorType(StrEnum):
    FOUNDER = "founder"
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    INTEGRATION = "integration"


class CommandType(StrEnum):
    CREATE_ENGAGEMENT = "create_engagement"
    UPDATE_MANDATE = "update_mandate"
    PROPOSE_TRANSITION = "propose_transition"
    REQUEST_APPROVAL = "request_approval"
    RECORD_APPROVAL = "record_approval"
    PROPOSE_EXTERNAL_ACTION = "propose_external_action"
    EXECUTE_EXTERNAL_ACTION = "execute_external_action"
    CANCEL_ENGAGEMENT = "cancel_engagement"
    RECORD_AGENT_OUTPUT = "record_agent_output"
    RELEASE_ARTEFACT = "release_artefact"


class EventType(StrEnum):
    ENGAGEMENT_CREATED = "engagement_created"
    MANDATE_UPDATED = "mandate_updated"
    TRANSITION_PROPOSED = "transition_proposed"
    TRANSITION_ACCEPTED = "transition_accepted"
    TRANSITION_REJECTED = "transition_rejected"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_RECORDED = "approval_recorded"
    EXTERNAL_ACTION_PROPOSED = "external_action_proposed"
    EXTERNAL_ACTION_EXECUTED = "external_action_executed"
    ENGAGEMENT_CANCELLED = "engagement_cancelled"
    AGENT_OUTPUT_RECORDED = "agent_output_recorded"
    ARTEFACT_RELEASED = "artefact_released"
    DEFECT_RECORDED = "defect_recorded"
    WORKFLOW_BLOCKED = "workflow_blocked"
    WORKFLOW_RESUMED = "workflow_resumed"


class ApprovalOutcome(StrEnum):
    APPROVED = "approved"
    CONDITIONAL = "conditional"
    REJECTED = "rejected"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"


_IDEMPOTENCY_REQUIRED = {
    CommandType.REQUEST_APPROVAL,
    CommandType.RECORD_APPROVAL,
    CommandType.PROPOSE_EXTERNAL_ACTION,
    CommandType.EXECUTE_EXTERNAL_ACTION,
    CommandType.CANCEL_ENGAGEMENT,
    CommandType.RECORD_AGENT_OUTPUT,
    CommandType.RELEASE_ARTEFACT,
}


class ActorRef(BaseModel):
    model_config = ConfigDict(frozen=True)

    actor_id: str = Field(min_length=1)
    actor_type: ActorType
    display_name: str = ""
    agent_version: str | None = None


class CommandEnvelope(BaseModel):
    """A requested state change before policy and domain validation."""

    model_config = ConfigDict(frozen=True)

    command_id: str = Field(min_length=1)
    command_type: CommandType
    occurred_at: datetime
    actor: ActorRef
    tenant_id: str = Field(min_length=1)
    engagement_id: str | None = None
    expected_version: int | None = Field(default=None, ge=1)
    correlation_id: str = Field(min_length=1)
    causation_id: str | None = None
    idempotency_key: str | None = None
    approval_id: str | None = None
    payload: dict[str, Any]

    @model_validator(mode="after")
    def validate_scope_and_idempotency(self) -> "CommandEnvelope":
        if self.command_type is not CommandType.CREATE_ENGAGEMENT and not self.engagement_id:
            raise ValueError("Non-create commands require engagement_id.")
        if self.command_type in _IDEMPOTENCY_REQUIRED and not self.idempotency_key:
            raise ValueError(f"{self.command_type.value} requires an idempotency key.")
        if self.command_type is not CommandType.CREATE_ENGAGEMENT and self.expected_version is None:
            raise ValueError("Non-create commands require expected_version.")
        return self


class DomainEvent(BaseModel):
    """An immutable fact emitted after a command is accepted."""

    model_config = ConfigDict(frozen=True)

    event_id: str = Field(min_length=1)
    event_type: EventType
    occurred_at: datetime
    actor: ActorRef
    tenant_id: str = Field(min_length=1)
    engagement_id: str | None = None
    aggregate_type: str = Field(min_length=1)
    aggregate_id: str = Field(min_length=1)
    aggregate_version: int = Field(ge=1)
    correlation_id: str = Field(min_length=1)
    causation_id: str | None = None
    idempotency_key: str | None = None
    payload: dict[str, Any]


class ApprovalRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    approval_request_id: str = Field(min_length=1)
    engagement_id: str = Field(min_length=1)
    requested_at: datetime
    requested_by: ActorRef
    decision_classes: frozenset[DecisionClass]
    decision_required: str = Field(min_length=1)
    supporting_packet_reference: str = Field(min_length=1)
    required_approver_roles: tuple[str, ...]
    latest_responsible_date: datetime
    expires_at: datetime | None = None

    @model_validator(mode="after")
    def validate_reserved_approval(self) -> "ApprovalRequest":
        if not self.decision_classes or self.decision_classes == {DecisionClass.ROUTINE}:
            raise ValueError("Approval request requires a reserved decision class.")
        if not self.required_approver_roles:
            raise ValueError("Approval request requires at least one approver role.")
        if self.expires_at and self.expires_at <= self.requested_at:
            raise ValueError("expires_at must be later than requested_at.")
        return self


class ApprovalRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    approval_id: str = Field(min_length=1)
    approval_request_id: str = Field(min_length=1)
    engagement_id: str = Field(min_length=1)
    decided_at: datetime
    decided_by: ActorRef
    outcome: ApprovalOutcome
    conditions: tuple[str, ...] = ()
    rationale: str = ""
    evidence_reference: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_conditional_approval(self) -> "ApprovalRecord":
        if self.outcome is ApprovalOutcome.CONDITIONAL and not self.conditions:
            raise ValueError("Conditional approval requires explicit conditions.")
        return self
