"""Deterministic security, privacy and regionalisation controls for offdata.

This module deliberately evaluates policy and evidence. It does not provision cloud
infrastructure, grant legal authority, approve cross-border transfers or replace the
Founder production gate.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class FrozenModel(BaseModel):
    """Strict immutable base model used by security policy records."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class DataClassification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CLIENT_CONFIDENTIAL = "client_confidential"
    HIGHLY_RESTRICTED = "highly_restricted"


CLASSIFICATION_RANK: dict[DataClassification, int] = {
    DataClassification.PUBLIC: 0,
    DataClassification.INTERNAL: 1,
    DataClassification.CLIENT_CONFIDENTIAL: 2,
    DataClassification.HIGHLY_RESTRICTED: 3,
}


class RuntimeEnvironment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ScopeKind(str, Enum):
    GLOBAL = "global"
    TENANT = "tenant"
    ENGAGEMENT = "engagement"


class AccessAction(str, Enum):
    READ = "read"
    WRITE = "write"
    PROCESS = "process"
    EXPORT = "export"
    DELETE = "delete"
    SUPPORT = "support"
    DEBUG = "debug"


class DecisionDisposition(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_FOUNDER_APPROVAL = "require_founder_approval"
    QUARANTINE = "quarantine"
    ELIGIBLE_FOR_FOUNDER_APPROVAL = "eligible_for_founder_approval"
    SYNTHETIC_ONLY = "synthetic_only"


class RetentionDisposition(str, Enum):
    RETAIN = "retain"
    ARCHIVE = "archive"
    EXPORT_REQUIRED = "export_required"
    DELETE_ELIGIBLE_WITH_APPROVAL = "delete_eligible_with_approval"
    HOLD = "hold"


class EvidenceStatus(str, Enum):
    NOT_STARTED = "not_started"
    DESIGN_ONLY = "design_only"
    EXECUTED = "executed"
    PASSED = "passed"
    FAILED = "failed"
    EXPIRED = "expired"


class ProcessorApprovalStatus(str, Enum):
    CANDIDATE = "candidate"
    APPROVED_SYNTHETIC_ONLY = "approved_synthetic_only"
    APPROVED_INTERNAL = "approved_internal"
    APPROVED_CLIENT_CONFIDENTIAL = "approved_client_confidential"
    APPROVED_HIGHLY_RESTRICTED = "approved_highly_restricted"
    SUSPENDED = "suspended"
    EXITED = "exited"


class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataHandlingRule(FrozenModel):
    classification: DataClassification
    rank: int = Field(ge=0, le=3)
    tenant_scope_required: bool
    engagement_scope_required: bool
    mfa_required: bool
    encryption_in_transit_required: bool
    encryption_at_rest_required: bool
    raw_payload_logging_allowed: bool
    provider_training_allowed: bool
    external_processor_allowed: bool
    cross_region_transfer_allowed_by_default: bool
    client_content_allowed: bool
    default_log_mode: Literal["full", "redacted", "metadata_only", "none"]

    @model_validator(mode="after")
    def validate_rank(self) -> DataHandlingRule:
        expected = CLASSIFICATION_RANK[self.classification]
        if self.rank != expected:
            raise ValueError(
                f"Classification rank mismatch for {self.classification.value}: {self.rank} != {expected}"
            )
        if self.classification in {
            DataClassification.CLIENT_CONFIDENTIAL,
            DataClassification.HIGHLY_RESTRICTED,
        }:
            if self.raw_payload_logging_allowed:
                raise ValueError("Restricted client data cannot allow raw payload logging by default.")
            if self.provider_training_allowed:
                raise ValueError("Restricted client data cannot allow provider training by default.")
        return self


class RecordSecurityContext(FrozenModel):
    record_id: str = Field(min_length=3)
    classification: DataClassification
    scope_kind: ScopeKind
    tenant_id: str | None = None
    engagement_id: str | None = None
    home_region: str = Field(min_length=2)
    allowed_regions: tuple[str, ...] = Field(min_length=1)
    retention_policy_id: str = Field(min_length=3)
    client_content: bool = False
    personal_data: bool = False
    legal_hold: bool = False
    approved_processor_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_scope_and_region(self) -> RecordSecurityContext:
        if self.scope_kind is ScopeKind.GLOBAL:
            if self.tenant_id is not None or self.engagement_id is not None:
                raise ValueError("Global records cannot carry tenant or engagement scope.")
            if self.client_content:
                raise ValueError("Global records cannot contain client content.")
        elif self.scope_kind is ScopeKind.TENANT:
            if not self.tenant_id or self.engagement_id is not None:
                raise ValueError("Tenant records require tenant_id and cannot set engagement_id.")
        else:
            if not self.tenant_id or not self.engagement_id:
                raise ValueError("Engagement records require tenant_id and engagement_id.")
        if self.home_region not in self.allowed_regions:
            raise ValueError("home_region must be present in allowed_regions.")
        if self.client_content and self.classification in {
            DataClassification.PUBLIC,
            DataClassification.INTERNAL,
        }:
            raise ValueError("Client content must be client_confidential or highly_restricted.")
        return self


class ActorSecurityContext(FrozenModel):
    actor_id: str = Field(min_length=3)
    actor_type: Literal["human", "agent", "integration", "system"]
    environment: RuntimeEnvironment
    tenant_id: str | None = None
    engagement_ids: tuple[str, ...] = ()
    authorised_regions: tuple[str, ...] = Field(min_length=1)
    capabilities: tuple[str, ...] = ()
    mfa_verified: bool = False
    founder_authority: bool = False
    support_access_expires_at: datetime | None = None


class AccessRequest(FrozenModel):
    request_id: str = Field(min_length=3)
    action: AccessAction
    actor: ActorSecurityContext
    record: RecordSecurityContext
    requested_region: str = Field(min_length=2)
    processor_id: str | None = None
    external_target: bool = False
    requested_at: datetime


class PolicyDecision(FrozenModel):
    disposition: DecisionDisposition
    reasons: tuple[str, ...] = ()
    required_controls: tuple[str, ...] = ()
    founder_approval_required: bool = False

    @property
    def allowed(self) -> bool:
        return self.disposition is DecisionDisposition.ALLOW


class RegionalCell(FrozenModel):
    cell_id: str = Field(min_length=3)
    region: str = Field(min_length=2)
    country: str = Field(min_length=2)
    environment: RuntimeEnvironment
    status: Literal["local_only", "planned", "ready_for_synthetic", "production_approved"]
    components: tuple[str, ...] = Field(min_length=1)
    permitted_classifications: tuple[DataClassification, ...]
    client_data_enabled: bool
    encryption_in_transit: bool
    encryption_at_rest: bool
    separate_encryption_keys: bool
    logs_mode: Literal["full", "redacted", "metadata_only", "none"]
    backup_regions: tuple[str, ...] = ()
    global_metadata_only: bool = True
    gate_evidence_digest: str | None = None

    @model_validator(mode="after")
    def validate_production_cell(self) -> RegionalCell:
        if self.environment is RuntimeEnvironment.PRODUCTION and self.client_data_enabled:
            if self.status != "production_approved":
                raise ValueError("A client-data production cell must be production_approved.")
            if not self.gate_evidence_digest:
                raise ValueError("A client-data production cell requires gate evidence.")
            if not self.encryption_at_rest or not self.encryption_in_transit:
                raise ValueError("A client-data production cell requires encryption in transit and at rest.")
        return self


class RegionalPolicy(FrozenModel):
    first_managed_region: str = Field(min_length=2)
    synthetic_only_until_production_gate: bool
    client_data_cross_region_default: Literal["deny", "allow"]
    global_metadata_fields: tuple[str, ...]
    prohibited_global_metadata_fields: tuple[str, ...]
    approved_region_expansion_requires: tuple[str, ...]


class RegionPlacementRequest(FrozenModel):
    record: RecordSecurityContext
    cell: RegionalCell
    policy: RegionalPolicy


class CrossRegionTransferRequest(FrozenModel):
    transfer_id: str = Field(min_length=3)
    record: RecordSecurityContext
    source_region: str = Field(min_length=2)
    destination_region: str = Field(min_length=2)
    transfer_scope: Literal["full_record", "sanitised_extract", "approved_metadata"]
    documented_transfer_basis: bool = False
    founder_approved: bool = False
    destination_cell_approved: bool = False


class RetentionPolicy(FrozenModel):
    policy_id: str = Field(min_length=3)
    jurisdiction: str = Field(min_length=2)
    classification: DataClassification
    active_retention_days: int = Field(ge=0)
    archive_after_days: int = Field(ge=0)
    delete_after_days: int = Field(gt=0)
    log_retention_days: int = Field(ge=0)
    legal_hold_supported: bool
    export_before_deletion: bool
    deletion_verification_required: bool
    founder_approval_required_for_deletion: bool = True
    configurable_by_engagement: bool = True

    @model_validator(mode="after")
    def validate_windows(self) -> RetentionPolicy:
        if self.archive_after_days > self.delete_after_days:
            raise ValueError("archive_after_days cannot exceed delete_after_days.")
        if self.active_retention_days > self.delete_after_days:
            raise ValueError("active_retention_days cannot exceed delete_after_days.")
        return self


class RetentionEvaluation(FrozenModel):
    disposition: RetentionDisposition
    reason: str
    founder_approval_required: bool = False
    deletion_verification_required: bool = False


class ProviderProcessorRecord(FrozenModel):
    processor_id: str = Field(min_length=3)
    legal_name: str = Field(min_length=2)
    service_name: str = Field(min_length=2)
    purposes: tuple[str, ...] = Field(min_length=1)
    permitted_classifications: tuple[DataClassification, ...]
    approved_regions: tuple[str, ...]
    retention_days: int | None = Field(default=None, ge=0)
    subprocessors: tuple[str, ...] = ()
    credential_reference: str = Field(min_length=3)
    credential_owner: str = Field(min_length=2)
    credential_value_stored: bool = False
    provider_training_disabled: bool
    dpa_status: Literal["not_required", "pending", "approved", "rejected"]
    transfer_basis_status: Literal["not_required", "pending", "approved", "rejected"]
    deletion_verification_supported: bool
    cost_model: str = Field(min_length=2)
    exit_plan: str = Field(min_length=8)
    approval_status: ProcessorApprovalStatus
    last_reviewed_at: datetime
    next_review_at: datetime
    synthetic_fixture: bool = False

    @model_validator(mode="after")
    def validate_register_safety(self) -> ProviderProcessorRecord:
        if self.credential_value_stored:
            raise ValueError("Processor register must never store credential values.")
        if looks_like_secret(self.credential_reference):
            raise ValueError("credential_reference appears to contain a secret rather than a reference.")
        if self.next_review_at <= self.last_reviewed_at:
            raise ValueError("next_review_at must be after last_reviewed_at.")
        if self.approval_status in {
            ProcessorApprovalStatus.APPROVED_CLIENT_CONFIDENTIAL,
            ProcessorApprovalStatus.APPROVED_HIGHLY_RESTRICTED,
        }:
            if self.dpa_status != "approved":
                raise ValueError("Client-data processor approval requires approved DPA status.")
            if not self.provider_training_disabled:
                raise ValueError("Client-data processor approval requires provider training disabled.")
            if not self.approved_regions:
                raise ValueError("Client-data processor approval requires at least one approved region.")
        return self


class ProcessorUseRequest(FrozenModel):
    processor: ProviderProcessorRecord
    classification: DataClassification
    region: str = Field(min_length=2)
    purpose: str = Field(min_length=2)
    real_client_data: bool
    now: datetime


class SecurityControlEvidence(FrozenModel):
    control_id: str = Field(min_length=3)
    status: EvidenceStatus
    environment: RuntimeEnvironment
    region: str = Field(min_length=2)
    evidence_refs: tuple[str, ...] = ()
    tested_at: datetime | None = None
    expires_at: datetime | None = None
    independent_reviewer: str | None = None
    notes: str | None = None

    def is_current_pass(self, *, now: datetime, environment: RuntimeEnvironment, region: str) -> bool:
        if self.status is not EvidenceStatus.PASSED:
            return False
        if self.environment is not environment or self.region != region:
            return False
        if not self.evidence_refs or self.tested_at is None:
            return False
        return self.expires_at is None or self.expires_at > now


class ProductionGateRequest(FrozenModel):
    cell: RegionalCell
    evidence: tuple[SecurityControlEvidence, ...]
    real_client_data_requested: bool
    founder_approval_control_id: str = "CTRL-FOUNDER-PRODUCTION-APPROVAL"
    evaluated_at: datetime


class ProductionGateReport(FrozenModel):
    disposition: DecisionDisposition
    missing_controls: tuple[str, ...] = ()
    failed_or_expired_controls: tuple[str, ...] = ()
    passed_controls: tuple[str, ...] = ()
    founder_approval_required: bool
    reasons: tuple[str, ...]


class IncidentSignal(FrozenModel):
    incident_id: str = Field(min_length=3)
    detected_at: datetime
    suspected_classifications: tuple[DataClassification, ...] = ()
    secret_exposure: bool = False
    cross_tenant_access: bool = False
    cross_region_leakage: bool = False
    external_disclosure: bool = False
    integrity_compromise: bool = False
    service_disruption_minutes: int = Field(default=0, ge=0)
    material_workflow_failure: bool = False
    potentially_affected_tenants: int = Field(default=0, ge=0)


class IncidentAssessment(FrozenModel):
    severity: IncidentSeverity
    mandatory_actions: tuple[str, ...]
    founder_notification_required: bool
    client_notification_decision_required: bool
    autonomous_closure_allowed: bool = False


class ThreatModelEntry(FrozenModel):
    threat_id: str = Field(min_length=3)
    title: str = Field(min_length=4)
    assets: tuple[str, ...] = Field(min_length=1)
    threat_actor: str = Field(min_length=2)
    attack_or_failure_path: str = Field(min_length=8)
    consequences: tuple[str, ...] = Field(min_length=1)
    preventive_controls: tuple[str, ...] = Field(min_length=1)
    detective_controls: tuple[str, ...] = Field(min_length=1)
    response_playbook_id: str = Field(min_length=3)
    residual_risk: Literal["low", "medium", "high", "critical"]
    test_ids: tuple[str, ...] = Field(min_length=1)


class SecurityTestCase(FrozenModel):
    test_id: str = Field(min_length=3)
    title: str = Field(min_length=4)
    execution_stage: Literal["chat_first", "codex_integration", "production_gate"]
    kind: Literal[
        "unit",
        "mutation",
        "security",
        "integration",
        "recovery",
        "incident",
        "founder_acceptance",
    ]
    requirement_ids: tuple[str, ...] = Field(min_length=1)
    control_ids: tuple[str, ...] = Field(min_length=1)
    expected_result: str = Field(min_length=4)
    mandatory_for_real_client_data: bool


class SecurityBaseline(FrozenModel):
    version: str
    source_files: tuple[str, ...]
    data_class_count: int
    regional_cell_count: int
    retention_policy_count: int
    processor_record_count: int
    processor_fixture_count: int
    threat_count: int
    control_count: int
    test_case_count: int
    incident_playbook_count: int
    mandatory_real_client_control_count: int
    baseline_digest: str
    real_client_data_enabled: bool
    first_managed_region: str


_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\b(?:sk|rk|pk)_(?:live|test)_[A-Za-z0-9]{12,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
)


def _shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts: dict[str, int] = {}
    for char in value:
        counts[char] = counts.get(char, 0) + 1
    return -sum((count / len(value)) * math.log2(count / len(value)) for count in counts.values())


def looks_like_secret(value: str) -> bool:
    """Conservative secret detector used for fixtures and governed metadata.

    It intentionally does not claim to replace repository or provider secret scanning.
    """

    if any(pattern.search(value) for pattern in _SECRET_PATTERNS):
        return True
    candidate = value.strip()
    if len(candidate) >= 32 and " " not in candidate and _shannon_entropy(candidate) >= 4.2:
        safe_reference_prefixes = (
            "secret://",
            "vault://",
            "keychain://",
            "env://",
            "credential-ref://",
        )
        return not candidate.startswith(safe_reference_prefixes)
    return False


def scan_for_secret_like_values(value: Any, *, path: str = "$") -> tuple[str, ...]:
    """Return paths containing values that resemble credentials."""

    findings: list[str] = []
    if isinstance(value, str):
        if looks_like_secret(value):
            findings.append(path)
    elif isinstance(value, Mapping):
        for key, item in value.items():
            findings.extend(scan_for_secret_like_values(item, path=f"{path}.{key}"))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            findings.extend(scan_for_secret_like_values(item, path=f"{path}[{index}]"))
    return tuple(findings)


def most_restrictive_classification(
    classifications: Iterable[DataClassification],
) -> DataClassification:
    values = tuple(classifications)
    if not values:
        raise ValueError("At least one classification is required.")
    return max(values, key=CLASSIFICATION_RANK.__getitem__)


def authorise_record_access(request: AccessRequest) -> PolicyDecision:
    """Evaluate tenant, engagement, region, MFA, environment and action boundaries."""

    record = request.record
    actor = request.actor
    reasons: list[str] = []
    required_controls: list[str] = []

    if request.requested_region not in actor.authorised_regions:
        reasons.append("Actor is not authorised for the requested region.")
    if request.requested_region not in record.allowed_regions:
        reasons.append("Record policy does not permit access from the requested region.")

    if record.scope_kind is not ScopeKind.GLOBAL and actor.tenant_id != record.tenant_id:
        reasons.append("Tenant scope mismatch.")
    if record.scope_kind is ScopeKind.ENGAGEMENT and record.engagement_id not in actor.engagement_ids:
        reasons.append("Engagement scope mismatch.")

    restricted = record.classification in {
        DataClassification.CLIENT_CONFIDENTIAL,
        DataClassification.HIGHLY_RESTRICTED,
    }
    if restricted and not actor.mfa_verified:
        reasons.append("MFA is required for restricted records.")
    if restricted and actor.environment is RuntimeEnvironment.DEVELOPMENT:
        reasons.append("Real restricted client records are prohibited in development.")
    if request.processor_id and request.processor_id not in record.approved_processor_ids:
        reasons.append("Processor is not approved for this record.")

    if request.action in {AccessAction.SUPPORT, AccessAction.DEBUG}:
        if "time_limited_support" not in actor.capabilities:
            reasons.append("Support or debug access requires the time_limited_support capability.")
        if actor.support_access_expires_at is None or actor.support_access_expires_at <= request.requested_at:
            reasons.append("Support or debug access is absent or expired.")
        required_controls.extend(("CTRL-PRIVILEGED-ACCESS-LOG", "CTRL-SUPPORT-ACCESS-EXPIRY"))

    if reasons:
        return PolicyDecision(
            disposition=DecisionDisposition.DENY,
            reasons=tuple(reasons),
            required_controls=tuple(dict.fromkeys(required_controls)),
        )

    material_action = request.action in {AccessAction.EXPORT, AccessAction.DELETE}
    if material_action or request.external_target:
        return PolicyDecision(
            disposition=DecisionDisposition.REQUIRE_FOUNDER_APPROVAL,
            reasons=("Material export, deletion or external disclosure requires Founder authority.",),
            required_controls=(
                "CTRL-AUDIT-EVENT",
                "CTRL-FOUNDER-ACTION-APPROVAL",
                "CTRL-IDEMPOTENCY",
            ),
            founder_approval_required=True,
        )

    return PolicyDecision(
        disposition=DecisionDisposition.ALLOW,
        required_controls=tuple(
            dict.fromkeys(("CTRL-AUDIT-EVENT", "CTRL-LEAST-PRIVILEGE", *required_controls))
        ),
    )


def authorise_region_placement(request: RegionPlacementRequest) -> PolicyDecision:
    record = request.record
    cell = request.cell
    policy = request.policy
    reasons: list[str] = []

    if cell.region not in record.allowed_regions:
        reasons.append("Destination cell is outside the record's allowed regions.")
    if record.home_region != cell.region and record.client_content:
        reasons.append("Client content must remain in its home region unless a transfer is separately approved.")
    if record.classification not in cell.permitted_classifications:
        reasons.append("Destination cell does not permit the record classification.")
    if cell.environment is RuntimeEnvironment.PRODUCTION and cell.region != policy.first_managed_region:
        reasons.append("The first managed production cell must use the configured Singapore-first region.")
    if record.client_content and not cell.client_data_enabled:
        reasons.append("Destination cell is not enabled for client data.")
    if record.client_content and cell.status != "production_approved":
        reasons.append("Client content requires a production-approved cell.")
    if record.classification is DataClassification.HIGHLY_RESTRICTED and not cell.separate_encryption_keys:
        reasons.append("Highly restricted data requires separate encryption keys.")

    if reasons:
        return PolicyDecision(disposition=DecisionDisposition.DENY, reasons=tuple(reasons))
    return PolicyDecision(
        disposition=DecisionDisposition.ALLOW,
        required_controls=("CTRL-REGION-PINNING", "CTRL-AUDIT-EVENT"),
    )


def authorise_cross_region_transfer(request: CrossRegionTransferRequest) -> PolicyDecision:
    if request.source_region == request.destination_region:
        return PolicyDecision(disposition=DecisionDisposition.ALLOW)

    record = request.record
    if request.destination_region not in record.allowed_regions:
        return PolicyDecision(
            disposition=DecisionDisposition.DENY,
            reasons=("Destination region is not authorised for the record.",),
        )

    if record.scope_kind is ScopeKind.GLOBAL and not record.client_content:
        if request.transfer_scope == "approved_metadata":
            return PolicyDecision(
                disposition=DecisionDisposition.ALLOW,
                required_controls=("CTRL-METADATA-ALLOWLIST", "CTRL-AUDIT-EVENT"),
            )

    if not request.documented_transfer_basis or not request.destination_cell_approved:
        return PolicyDecision(
            disposition=DecisionDisposition.DENY,
            reasons=("Cross-region transfer requires a documented basis and approved destination cell.",),
        )
    if not request.founder_approved:
        return PolicyDecision(
            disposition=DecisionDisposition.REQUIRE_FOUNDER_APPROVAL,
            reasons=("Cross-region transfer requires explicit Founder approval.",),
            required_controls=("CTRL-TRANSFER-REGISTER", "CTRL-AUDIT-EVENT"),
            founder_approval_required=True,
        )
    return PolicyDecision(
        disposition=DecisionDisposition.ALLOW,
        required_controls=(
            "CTRL-TRANSFER-REGISTER",
            "CTRL-DATA-MINIMISATION",
            "CTRL-AUDIT-EVENT",
        ),
    )


def evaluate_retention(
    *,
    policy: RetentionPolicy,
    closed_at: datetime | None,
    evaluated_at: datetime,
    legal_hold: bool,
    export_completed: bool,
) -> RetentionEvaluation:
    if legal_hold:
        if not policy.legal_hold_supported:
            raise ValueError("Policy does not support a required legal hold.")
        return RetentionEvaluation(
            disposition=RetentionDisposition.HOLD,
            reason="Legal or contractual hold blocks archival and deletion.",
        )
    if closed_at is None:
        return RetentionEvaluation(
            disposition=RetentionDisposition.RETAIN,
            reason="Active records remain retained.",
        )
    if evaluated_at < closed_at:
        raise ValueError("evaluated_at cannot precede closed_at.")
    age_days = (evaluated_at - closed_at).days
    if age_days < policy.archive_after_days:
        return RetentionEvaluation(
            disposition=RetentionDisposition.RETAIN,
            reason="Record remains inside the active retention window.",
        )
    if age_days < policy.delete_after_days:
        return RetentionEvaluation(
            disposition=RetentionDisposition.ARCHIVE,
            reason="Record is eligible for controlled archival but not deletion.",
        )
    if policy.export_before_deletion and not export_completed:
        return RetentionEvaluation(
            disposition=RetentionDisposition.EXPORT_REQUIRED,
            reason="Controlled export must complete before deletion consideration.",
            founder_approval_required=policy.founder_approval_required_for_deletion,
        )
    return RetentionEvaluation(
        disposition=RetentionDisposition.DELETE_ELIGIBLE_WITH_APPROVAL,
        reason="Retention period elapsed; deletion remains an approved, verified action.",
        founder_approval_required=policy.founder_approval_required_for_deletion,
        deletion_verification_required=policy.deletion_verification_required,
    )


def authorise_processor_use(request: ProcessorUseRequest) -> PolicyDecision:
    processor = request.processor
    reasons: list[str] = []
    if request.now >= processor.next_review_at:
        reasons.append("Processor review is expired.")
    if processor.approval_status in {
        ProcessorApprovalStatus.CANDIDATE,
        ProcessorApprovalStatus.SUSPENDED,
        ProcessorApprovalStatus.EXITED,
    }:
        reasons.append("Processor is not currently approved for use.")
    if request.classification not in processor.permitted_classifications:
        reasons.append("Processor is not approved for the requested data classification.")
    if request.region not in processor.approved_regions:
        reasons.append("Processor is not approved in the requested region.")
    if request.purpose not in processor.purposes:
        reasons.append("Processor purpose is outside the approved register scope.")
    if request.real_client_data:
        if processor.synthetic_fixture:
            reasons.append("Synthetic processor fixtures cannot receive real client data.")
        if processor.dpa_status != "approved":
            reasons.append("Real client data requires approved data-processing terms.")
        if processor.transfer_basis_status == "rejected":
            reasons.append("Processor transfer basis is rejected.")
        if not processor.provider_training_disabled:
            reasons.append("Provider training must be disabled for real client data.")
        if not processor.deletion_verification_supported:
            reasons.append("Real client data requires supported deletion verification.")
    if reasons:
        return PolicyDecision(disposition=DecisionDisposition.DENY, reasons=tuple(reasons))
    return PolicyDecision(
        disposition=DecisionDisposition.ALLOW,
        required_controls=("CTRL-PROCESSOR-REGISTER", "CTRL-PROVIDER-CALL-LOG"),
    )


MANDATORY_REAL_CLIENT_CONTROLS: tuple[str, ...] = (
    "CTRL-STRONG-AUTH-MFA",
    "CTRL-LEAST-PRIVILEGE",
    "CTRL-ENVIRONMENT-SEPARATION",
    "CTRL-ENCRYPTION-IN-TRANSIT",
    "CTRL-ENCRYPTION-AT-REST",
    "CTRL-TENANT-ISOLATION",
    "CTRL-ENGAGEMENT-ISOLATION",
    "CTRL-REGION-PINNING",
    "CTRL-SECRET-SCANNING",
    "CTRL-SUPPLY-CHAIN-REVIEW",
    "CTRL-PROMPT-INJECTION-TEST",
    "CTRL-BACKUP-RESTORE-TEST",
    "CTRL-KILL-SWITCH-TEST",
    "CTRL-OBSERVABILITY-ALERTS",
    "CTRL-INCIDENT-PLAYBOOK",
    "CTRL-RETENTION-DELETION",
    "CTRL-PROCESSOR-REGISTER",
    "CTRL-AUDIT-EXPORT",
)


def evaluate_production_gate(request: ProductionGateRequest) -> ProductionGateReport:
    if not request.real_client_data_requested:
        return ProductionGateReport(
            disposition=DecisionDisposition.SYNTHETIC_ONLY,
            founder_approval_required=False,
            reasons=("Synthetic-data operation does not authorise real client data.",),
        )
    if request.cell.environment is not RuntimeEnvironment.PRODUCTION:
        return ProductionGateReport(
            disposition=DecisionDisposition.DENY,
            founder_approval_required=True,
            reasons=("Real client data requires a production cell.",),
        )

    evidence_by_id = {item.control_id: item for item in request.evidence}
    missing = tuple(sorted(set(MANDATORY_REAL_CLIENT_CONTROLS) - set(evidence_by_id)))
    failed_or_expired = tuple(
        sorted(
            control_id
            for control_id in MANDATORY_REAL_CLIENT_CONTROLS
            if control_id in evidence_by_id
            and not evidence_by_id[control_id].is_current_pass(
                now=request.evaluated_at,
                environment=request.cell.environment,
                region=request.cell.region,
            )
        )
    )
    passed = tuple(
        sorted(
            control_id
            for control_id in MANDATORY_REAL_CLIENT_CONTROLS
            if control_id in evidence_by_id
            and evidence_by_id[control_id].is_current_pass(
                now=request.evaluated_at,
                environment=request.cell.environment,
                region=request.cell.region,
            )
        )
    )
    if missing or failed_or_expired:
        return ProductionGateReport(
            disposition=DecisionDisposition.DENY,
            missing_controls=missing,
            failed_or_expired_controls=failed_or_expired,
            passed_controls=passed,
            founder_approval_required=True,
            reasons=("Mandatory production-security evidence is incomplete or not current.",),
        )

    founder_evidence = evidence_by_id.get(request.founder_approval_control_id)
    if founder_evidence is None or not founder_evidence.is_current_pass(
        now=request.evaluated_at,
        environment=request.cell.environment,
        region=request.cell.region,
    ):
        return ProductionGateReport(
            disposition=DecisionDisposition.ELIGIBLE_FOR_FOUNDER_APPROVAL,
            passed_controls=passed,
            founder_approval_required=True,
            reasons=("Technical evidence is complete; explicit Founder production approval remains required.",),
        )

    return ProductionGateReport(
        disposition=DecisionDisposition.ALLOW,
        passed_controls=passed + (request.founder_approval_control_id,),
        founder_approval_required=False,
        reasons=("Current mandatory evidence and explicit Founder approval are present.",),
    )


def assess_incident(signal: IncidentSignal) -> IncidentAssessment:
    classifications = signal.suspected_classifications
    most_restrictive = (
        most_restrictive_classification(classifications)
        if classifications
        else DataClassification.INTERNAL
    )
    critical = (
        signal.secret_exposure
        or signal.cross_tenant_access
        or signal.cross_region_leakage
        or (
            signal.external_disclosure
            and most_restrictive is DataClassification.HIGHLY_RESTRICTED
        )
        or signal.potentially_affected_tenants > 1
    )
    high = (
        signal.external_disclosure
        or signal.integrity_compromise
        or most_restrictive is DataClassification.CLIENT_CONFIDENTIAL
        or signal.service_disruption_minutes >= 240
    )
    medium = signal.material_workflow_failure or signal.service_disruption_minutes >= 30

    severity = (
        IncidentSeverity.CRITICAL
        if critical
        else IncidentSeverity.HIGH
        if high
        else IncidentSeverity.MEDIUM
        if medium
        else IncidentSeverity.LOW
    )
    actions = [
        "preserve_audit_evidence",
        "record_scope_and_timeline",
        "assign_incident_owner",
    ]
    if severity in {IncidentSeverity.HIGH, IncidentSeverity.CRITICAL}:
        actions.extend(
            (
                "disable_affected_agents_or_integrations",
                "quarantine_affected_engagements",
                "evaluate_credential_revocation",
                "perform_impact_assessment",
                "prepare_client_notification_decision_packet",
                "define_corrective_actions_and_regression_tests",
            )
        )
    if signal.secret_exposure:
        actions.append("revoke_and_rotate_exposed_credentials")
    if signal.cross_region_leakage:
        actions.append("stop_cross_region_transfer_path")

    return IncidentAssessment(
        severity=severity,
        mandatory_actions=tuple(dict.fromkeys(actions)),
        founder_notification_required=severity in {
            IncidentSeverity.HIGH,
            IncidentSeverity.CRITICAL,
        },
        client_notification_decision_required=signal.external_disclosure
        or signal.cross_tenant_access
        or signal.cross_region_leakage,
        autonomous_closure_allowed=False,
    )


def _load_yaml_object(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected YAML object: {path}")
    return value


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def _normalise_for_digest(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _normalise_for_digest(item) for key, item in sorted(value.items())}
    if isinstance(value, list):
        return [_normalise_for_digest(item) for item in value]
    return value


def build_security_baseline(root: Path) -> SecurityBaseline:
    security_root = root / "security"
    config_path = root / "configs" / "security-regionalisation.yaml"
    paths = (
        config_path,
        security_root / "data-classification.yaml",
        security_root / "regional-cells.yaml",
        security_root / "retention-policies.yaml",
        security_root / "provider-processor-register.yaml",
        security_root / "provider-processor-fixtures.yaml",
        security_root / "threat-model.yaml",
        security_root / "security-control-catalogue.yaml",
        security_root / "security-test-catalogue.yaml",
        security_root / "incident-playbooks.yaml",
    )
    documents = {path.relative_to(root).as_posix(): _load_yaml_object(path) for path in paths}

    config = documents[config_path.relative_to(root).as_posix()]
    data_classes = documents["security/data-classification.yaml"].get("classes", [])
    cells = documents["security/regional-cells.yaml"].get("cells", [])
    retention = documents["security/retention-policies.yaml"].get("policies", [])
    processors = documents["security/provider-processor-register.yaml"].get("processors", [])
    processor_fixtures = documents["security/provider-processor-fixtures.yaml"].get(
        "processors", []
    )
    threats = documents["security/threat-model.yaml"].get("threats", [])
    controls = documents["security/security-control-catalogue.yaml"].get("controls", [])
    tests = documents["security/security-test-catalogue.yaml"].get("tests", [])
    playbooks = documents["security/incident-playbooks.yaml"].get("playbooks", [])

    rules = tuple(DataHandlingRule.model_validate(item) for item in data_classes)
    if {rule.classification for rule in rules} != set(DataClassification):
        raise ValueError("Data-classification catalogue must contain exactly all four classes.")
    tuple(RegionalCell.model_validate(item) for item in cells)
    tuple(RetentionPolicy.model_validate(item) for item in retention)
    tuple(ProviderProcessorRecord.model_validate(item) for item in processors)
    tuple(ProviderProcessorRecord.model_validate(item) for item in processor_fixtures)
    tuple(ThreatModelEntry.model_validate(item) for item in threats)
    tuple(SecurityTestCase.model_validate(item) for item in tests)

    control_ids = {item["control_id"] for item in controls}
    if len(control_ids) != len(controls):
        raise ValueError("Security control IDs must be unique.")
    missing_mandatory = set(MANDATORY_REAL_CLIENT_CONTROLS) - control_ids
    if missing_mandatory:
        raise ValueError(f"Mandatory controls missing from catalogue: {sorted(missing_mandatory)}")
    test_ids = {item["test_id"] for item in tests}
    if len(test_ids) != len(tests):
        raise ValueError("Security test IDs must be unique.")
    threat_ids = {item["threat_id"] for item in threats}
    if len(threat_ids) != len(threats):
        raise ValueError("Threat IDs must be unique.")

    findings = scan_for_secret_like_values(documents)
    if findings:
        raise ValueError(f"Secret-like values found in governed security records: {findings}")

    digest_payload = _normalise_for_digest(documents)
    digest = hashlib.sha256(_canonical_json(digest_payload)).hexdigest()
    return SecurityBaseline(
        version=str(config["version"]),
        source_files=tuple(documents),
        data_class_count=len(data_classes),
        regional_cell_count=len(cells),
        retention_policy_count=len(retention),
        processor_record_count=len(processors),
        processor_fixture_count=len(processor_fixtures),
        threat_count=len(threats),
        control_count=len(controls),
        test_case_count=len(tests),
        incident_playbook_count=len(playbooks),
        mandatory_real_client_control_count=sum(
            bool(item.get("mandatory_for_real_client_data")) for item in controls
        ),
        baseline_digest=digest,
        real_client_data_enabled=bool(config["real_client_data_enabled"]),
        first_managed_region=str(config["first_managed_region"]),
    )


def write_security_baseline(root: Path) -> Path:
    destination = root / "security" / "security-regionalisation-baseline.json"
    baseline = build_security_baseline(root)
    destination.write_text(
        json.dumps(baseline.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination


def verify_security_baseline(root: Path, path: Path | None = None) -> None:
    baseline_path = path or root / "security" / "security-regionalisation-baseline.json"
    committed = SecurityBaseline.model_validate_json(baseline_path.read_text(encoding="utf-8"))
    regenerated = build_security_baseline(root)
    if committed != regenerated:
        raise ValueError("Committed security-regionalisation baseline is stale or has drifted.")


def make_current_control_evidence(
    control_ids: Iterable[str],
    *,
    environment: RuntimeEnvironment,
    region: str,
    evaluated_at: datetime,
) -> tuple[SecurityControlEvidence, ...]:
    """Create deterministic synthetic evidence used only by unit tests."""

    tested_at = evaluated_at - timedelta(hours=1)
    expires_at = evaluated_at + timedelta(days=30)
    return tuple(
        SecurityControlEvidence(
            control_id=control_id,
            status=EvidenceStatus.PASSED,
            environment=environment,
            region=region,
            evidence_refs=(f"synthetic-test://{control_id}",),
            tested_at=tested_at,
            expires_at=expires_at,
            independent_reviewer="synthetic-independent-reviewer",
        )
        for control_id in control_ids
    )


def utc_now() -> datetime:
    """Small helper kept explicit so production callers can inject time in tests."""

    return datetime.now(timezone.utc)
