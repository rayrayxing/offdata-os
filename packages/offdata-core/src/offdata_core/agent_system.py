"""Deterministic contracts and controls for the first offdata agent system."""

from __future__ import annotations

from enum import StrEnum
from typing import Iterable

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .contracts import ContextPackage, RecordOperation
from .models import DecisionClass


class EvaluationKind(StrEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    ADVERSARIAL = "adversarial"


class AdmissionDisposition(StrEnum):
    ADMITTED = "admitted"
    REJECTED = "rejected"
    NEEDS_INDEPENDENT_REVIEW = "needs_independent_review"


class AgentDefinition(BaseModel):
    """Provider-independent definition of one bounded specialist agent."""

    model_config = ConfigDict(frozen=True)

    agent_id: str = Field(pattern=r"^[a-z][a-z0-9_]+$")
    agent_version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    prompt_version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    purpose: str = Field(min_length=1)
    skill_package: str = Field(min_length=1)
    input_contracts: tuple[str, ...]
    output_contract: str = Field(min_length=1)
    allowed_record_families: frozenset[str]
    permitted_tool_classes: frozenset[str]
    prohibited_actions: frozenset[str]
    context_profile: str = Field(min_length=1)
    evidence_rules: tuple[str, ...]
    escalation_policy: tuple[str, ...]
    budget_profile: str = Field(min_length=1)
    evaluation_profile: str = Field(min_length=1)

    @model_validator(mode="after")
    def require_complete_boundaries(self) -> "AgentDefinition":
        if not self.input_contracts:
            raise ValueError("Agent definition requires at least one typed input contract.")
        if not self.allowed_record_families:
            raise ValueError("Agent definition requires an explicit record-family allowlist.")
        if not self.permitted_tool_classes:
            raise ValueError("Agent definition requires an explicit tool allowlist.")
        if not self.prohibited_actions:
            raise ValueError("Agent definition requires prohibited actions.")
        if not self.evidence_rules:
            raise ValueError("Agent definition requires evidence rules.")
        if not self.escalation_policy:
            raise ValueError("Agent definition requires escalation rules.")
        return self


class ContextCandidate(BaseModel):
    """A canonical-record reference considered by the context compiler."""

    model_config = ConfigDict(frozen=True)

    tenant_id: str = Field(min_length=1)
    engagement_id: str = Field(min_length=1)
    record_id: str = Field(min_length=1)
    record_family: str = Field(min_length=1)
    content_reference: str = Field(min_length=1)
    relevance: float = Field(ge=0, le=1)
    approved: bool = True
    untrusted_input: bool = False
    instruction_like_content: bool = False


class ContextRejection(BaseModel):
    model_config = ConfigDict(frozen=True)

    record_id: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class ContextCompilationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    selected_record_ids: tuple[str, ...]
    selected_references: tuple[str, ...]
    isolated_untrusted_record_ids: tuple[str, ...] = ()
    rejected: tuple[ContextRejection, ...] = ()
    instruction_content_ignored: bool = False


class ToolRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    tenant_id: str = Field(min_length=1)
    engagement_id: str = Field(min_length=1)
    tool_class: str = Field(min_length=1)
    proposed_action: str = Field(min_length=1)
    external_side_effect: bool = False
    canonical_write: bool = False


class RecordWriteRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    record_family: str = Field(min_length=1)
    operation: RecordOperation
    via_command: bool


class PermissionDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    allowed: bool
    reasons: tuple[str, ...]


class AgentBudgetPolicy(BaseModel):
    model_config = ConfigDict(frozen=True)

    timeout_seconds: int = Field(gt=0)
    max_retries: int = Field(ge=0)
    max_input_tokens: int = Field(gt=0)
    max_output_tokens: int = Field(gt=0)
    max_cost: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    model_or_route: str = Field(min_length=1)


class BudgetUsage(BaseModel):
    model_config = ConfigDict(frozen=True)

    elapsed_seconds: float = Field(ge=0)
    retries: int = Field(ge=0)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    estimated_cost: float = Field(ge=0)


class BudgetDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    within_budget: bool
    exceeded: tuple[str, ...]


class ProviderRoute(BaseModel):
    model_config = ConfigDict(frozen=True)

    route_id: str = Field(min_length=1)
    model_or_route: str = Field(min_length=1)
    minimum_complexity: int = Field(ge=1, le=5)
    minimum_evidence_risk: int = Field(ge=1, le=5)
    latency_rank: int = Field(ge=1)
    cost_rank: int = Field(ge=1)
    output_contract: str = Field(min_length=1)


class EvaluationCase(BaseModel):
    model_config = ConfigDict(frozen=True)

    case_id: str = Field(min_length=1)
    agent_id: str = Field(pattern=r"^[a-z][a-z0-9_]+$")
    kind: EvaluationKind
    fixture: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    expected_status: str = Field(min_length=1)
    required_signals: tuple[str, ...]
    forbidden_signals: tuple[str, ...]
    mandatory_fail: bool = False

    @model_validator(mode="after")
    def require_observable_expectations(self) -> "EvaluationCase":
        if not self.required_signals:
            raise ValueError("Evaluation case requires observable required signals.")
        if not self.forbidden_signals:
            raise ValueError("Evaluation case requires forbidden signals.")
        return self


class EvaluationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_validity: float = Field(ge=0, le=1)
    decision_fitness: float = Field(ge=0, le=100)
    evidence_factuality: float = Field(ge=0, le=100)
    method_correctness: float = Field(ge=0, le=100)
    authority_safety: float = Field(ge=0, le=100)
    structured_output: float = Field(ge=0, le=100)
    completeness_usability: float = Field(ge=0, le=100)
    cost_efficiency: float = Field(ge=0, le=100)
    operational_reliability: float = Field(ge=0, le=100)
    observed_failures: frozenset[str] = Field(default_factory=frozenset)
    repeated_run_variance: float = Field(default=0, ge=0, le=100)


class AdmissionThresholds(BaseModel):
    model_config = ConfigDict(frozen=True)

    minimum_schema_validity: float = Field(ge=0, le=1)
    minimum_critical_dimension: float = Field(ge=0, le=100)
    minimum_weighted_score: float = Field(ge=0, le=100)
    maximum_repeated_run_variance: float = Field(ge=0, le=100)
    mandatory_failures: frozenset[str]

    @field_validator("mandatory_failures")
    @classmethod
    def require_mandatory_failures(cls, value: frozenset[str]) -> frozenset[str]:
        if not value:
            raise ValueError("Admission thresholds require mandatory failure conditions.")
        return value


class AdmissionReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    disposition: AdmissionDisposition
    weighted_score: float = Field(ge=0, le=100)
    reasons: tuple[str, ...]
    mandatory_failures: tuple[str, ...] = ()


class InjectionAssessment(BaseModel):
    model_config = ConfigDict(frozen=True)

    suspicious: bool
    matched_markers: tuple[str, ...]
    instruction_content_ignored: bool
    external_action_blocked: bool


def compile_minimum_context(
    *,
    agent: AgentDefinition,
    tenant_id: str,
    engagement_id: str,
    candidates: Iterable[ContextCandidate],
    required_record_ids: frozenset[str] = frozenset(),
    max_records: int,
) -> ContextCompilationResult:
    """Select the smallest approved, in-scope and role-permitted context set."""

    if max_records <= 0:
        raise ValueError("Context compiler max_records must be positive.")

    selected: list[ContextCandidate] = []
    rejected: list[ContextRejection] = []
    instruction_content_ignored = False

    ordered = sorted(
        candidates,
        key=lambda item: (
            item.record_id not in required_record_ids,
            -item.relevance,
            item.record_id,
        ),
    )
    for candidate in ordered:
        reason = ""
        if candidate.tenant_id != tenant_id:
            reason = "cross_tenant"
        elif candidate.engagement_id != engagement_id:
            reason = "cross_engagement"
        elif candidate.record_family not in agent.allowed_record_families:
            reason = "record_family_not_allowed"
        elif not candidate.approved:
            reason = "record_not_approved"
        elif len(selected) >= max_records:
            reason = "context_budget_exhausted"

        if reason:
            rejected.append(ContextRejection(record_id=candidate.record_id, reason=reason))
            continue

        if candidate.instruction_like_content:
            instruction_content_ignored = True
        selected.append(candidate)

    missing_required = required_record_ids - {item.record_id for item in selected}
    for record_id in sorted(missing_required):
        if not any(item.record_id == record_id for item in rejected):
            rejected.append(ContextRejection(record_id=record_id, reason="required_record_missing"))

    return ContextCompilationResult(
        selected_record_ids=tuple(item.record_id for item in selected),
        selected_references=tuple(item.content_reference for item in selected),
        isolated_untrusted_record_ids=tuple(
            item.record_id for item in selected if item.untrusted_input
        ),
        rejected=tuple(rejected),
        instruction_content_ignored=instruction_content_ignored,
    )


def authorise_tool_request(
    *,
    agent: AgentDefinition,
    context: ContextPackage,
    request: ToolRequest,
) -> PermissionDecision:
    """Apply deterministic scope, tool and action controls before any tool call."""

    reasons: list[str] = []
    if request.tenant_id != context.decision.get("tenant_id", request.tenant_id):
        reasons.append("tenant_scope_mismatch")
    if request.engagement_id != context.engagement_id:
        reasons.append("engagement_scope_mismatch")
    if request.tool_class not in agent.permitted_tool_classes:
        reasons.append("tool_not_allowed_for_agent")
    if request.tool_class not in context.permitted_tools:
        reasons.append("tool_not_allowed_for_run")
    if request.proposed_action in agent.prohibited_actions:
        reasons.append("prohibited_action")
    if request.proposed_action in context.prohibited_actions:
        reasons.append("run_prohibited_action")
    if request.external_side_effect:
        reasons.append("direct_external_side_effect_prohibited")
    if request.canonical_write:
        reasons.append("canonical_write_requires_command")

    return PermissionDecision(allowed=not reasons, reasons=tuple(reasons))


def authorise_record_write(
    *,
    agent: AgentDefinition,
    request: RecordWriteRequest,
) -> PermissionDecision:
    """Require role scope, propose-only operations and command-mediated writes."""

    reasons: list[str] = []
    if request.record_family not in agent.allowed_record_families:
        reasons.append("record_family_not_allowed")
    if not request.operation.value.startswith("propose_"):
        reasons.append("operation_not_propose_only")
    if not request.via_command:
        reasons.append("canonical_writes_require_commands")
    return PermissionDecision(allowed=not reasons, reasons=tuple(reasons))


def evaluate_budget(policy: AgentBudgetPolicy, usage: BudgetUsage) -> BudgetDecision:
    exceeded: list[str] = []
    if usage.elapsed_seconds > policy.timeout_seconds:
        exceeded.append("timeout_seconds")
    if usage.retries > policy.max_retries:
        exceeded.append("max_retries")
    if usage.input_tokens > policy.max_input_tokens:
        exceeded.append("max_input_tokens")
    if usage.output_tokens > policy.max_output_tokens:
        exceeded.append("max_output_tokens")
    if usage.estimated_cost > policy.max_cost:
        exceeded.append("max_cost")
    return BudgetDecision(within_budget=not exceeded, exceeded=tuple(exceeded))


def choose_provider_route(
    *,
    routes: Iterable[ProviderRoute],
    complexity: int,
    evidence_risk: int,
    latency_sensitive: bool,
    output_contract: str,
) -> ProviderRoute:
    """Choose a provider-independent route while preserving the output contract."""

    if not 1 <= complexity <= 5 or not 1 <= evidence_risk <= 5:
        raise ValueError("Complexity and evidence risk must be between 1 and 5.")

    eligible = [
        route
        for route in routes
        if route.minimum_complexity <= complexity
        and route.minimum_evidence_risk <= evidence_risk
        and route.output_contract == output_contract
    ]
    if not eligible:
        raise ValueError("No provider route satisfies the task and output contract.")

    if latency_sensitive:
        return min(eligible, key=lambda item: (item.latency_rank, item.cost_rank, item.route_id))
    return min(
        eligible,
        key=lambda item: (
            -item.minimum_complexity,
            -item.minimum_evidence_risk,
            item.cost_rank,
            item.route_id,
        ),
    )


def assess_untrusted_payload(payload: str) -> InjectionAssessment:
    """Detect common instruction-like payloads without treating them as authority."""

    lowered = payload.casefold()
    markers = (
        "ignore previous instructions",
        "ignore system instructions",
        "reveal secrets",
        "show api key",
        "founder already approved",
        "bypass approval",
        "send this externally",
        "upload credentials",
        "cross-tenant",
    )
    matched = tuple(marker for marker in markers if marker in lowered)
    suspicious = bool(matched)
    return InjectionAssessment(
        suspicious=suspicious,
        matched_markers=matched,
        instruction_content_ignored=suspicious,
        external_action_blocked=suspicious,
    )


def escalation_classes(
    *,
    requested_classes: frozenset[DecisionClass],
    budget: BudgetDecision,
    evidence_gaps: tuple[str, ...] = (),
    prohibited_action_attempted: bool = False,
) -> frozenset[DecisionClass]:
    """Return the classes that require accountable-human interruption."""

    classes = {item for item in requested_classes if item is not DecisionClass.ROUTINE}
    if prohibited_action_attempted:
        classes.add(DecisionClass.IRREVERSIBLE)
    if not budget.within_budget or evidence_gaps:
        classes.add(DecisionClass.MATERIAL)
    return frozenset(classes)


def evaluate_admission(
    result: EvaluationResult,
    thresholds: AdmissionThresholds,
) -> AdmissionReport:
    """Apply mandatory failures, critical thresholds and weighted scoring."""

    mandatory = sorted(result.observed_failures & thresholds.mandatory_failures)
    weighted_score = (
        result.decision_fitness * 0.20
        + result.evidence_factuality * 0.20
        + result.method_correctness * 0.15
        + result.authority_safety * 0.15
        + result.structured_output * 0.10
        + result.completeness_usability * 0.10
        + result.cost_efficiency * 0.05
        + result.operational_reliability * 0.05
    )
    reasons: list[str] = []
    if mandatory:
        reasons.append("mandatory_failure_observed")
    if result.schema_validity < thresholds.minimum_schema_validity:
        reasons.append("schema_validity_below_threshold")
    critical = (
        result.decision_fitness,
        result.evidence_factuality,
        result.authority_safety,
    )
    if any(score < thresholds.minimum_critical_dimension for score in critical):
        reasons.append("critical_dimension_below_threshold")
    if weighted_score < thresholds.minimum_weighted_score:
        reasons.append("weighted_score_below_threshold")
    if result.repeated_run_variance > thresholds.maximum_repeated_run_variance:
        reasons.append("repeated_run_variance_above_threshold")

    if reasons:
        disposition = AdmissionDisposition.REJECTED
    elif result.repeated_run_variance > 0:
        disposition = AdmissionDisposition.NEEDS_INDEPENDENT_REVIEW
    else:
        disposition = AdmissionDisposition.ADMITTED

    return AdmissionReport(
        disposition=disposition,
        weighted_score=round(weighted_score, 2),
        reasons=tuple(reasons),
        mandatory_failures=tuple(mandatory),
    )
