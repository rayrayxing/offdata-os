"""Deterministic quality scoring, defect and release-gate contracts."""

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AssuranceTier(StrEnum):
    T0_LOW = "T0"
    T1_MODERATE = "T1"
    T2_HIGH = "T2"
    T3_CRITICAL = "T3"


class QualityGate(StrEnum):
    INTERNAL_WORKING = "internal_working"
    FOUNDER_READY = "founder_ready"
    EXTERNAL_RELEASE = "external_release"
    CRITICAL_RELEASE = "critical_release"


class DefectSeverity(StrEnum):
    S1_CRITICAL = "S1"
    S2_MAJOR = "S2"
    S3_MODERATE = "S3"
    S4_MINOR = "S4"


class ReviewConclusion(StrEnum):
    PASS = "pass"
    PASS_WITH_CONDITIONS = "pass_with_conditions"
    FAIL = "fail"


DIMENSION_WEIGHTS: dict[str, int] = {
    "QD-MAND-01": 12,
    "QD-EVID-01": 12,
    "QD-RCOV-01": 8,
    "QD-METH-01": 10,
    "QD-REAS-01": 12,
    "QD-CLNT-01": 8,
    "QD-FIN-01": 10,
    "QD-FEAS-01": 8,
    "QD-EXEC-01": 8,
    "QD-STOR-01": 5,
    "QD-PRES-01": 4,
    "QD-AUDT-01": 3,
}


class DimensionScore(BaseModel):
    model_config = ConfigDict(frozen=True)

    dimension_id: str
    score: int | None = Field(default=None, ge=0, le=4)
    not_applicable_reason: str | None = None
    evidence_reference: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_applicability(self) -> "DimensionScore":
        if self.dimension_id not in DIMENSION_WEIGHTS:
            raise ValueError(f"Unknown quality dimension: {self.dimension_id}")
        if self.score is None and not self.not_applicable_reason:
            raise ValueError("A non-applicable dimension requires a reason.")
        if self.score is not None and self.not_applicable_reason:
            raise ValueError("A scored dimension cannot also be marked not applicable.")
        return self


class Defect(BaseModel):
    model_config = ConfigDict(frozen=True)

    defect_id: str = Field(min_length=1)
    severity: DefectSeverity
    affected_object: str = Field(min_length=1)
    defect: str = Field(min_length=1)
    consequence: str = Field(min_length=1)
    required_repair: str = Field(min_length=1)
    required_retest: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    status: str = "open"
    creator_actor_id: str = Field(min_length=1)
    closer_actor_id: str | None = None
    independent_verification_reference: str | None = None
    accepted_exception_id: str | None = None

    @model_validator(mode="after")
    def validate_closure_independence(self) -> "Defect":
        if self.status == "closed" and self.severity in {
            DefectSeverity.S1_CRITICAL,
            DefectSeverity.S2_MAJOR,
        }:
            if self.closer_actor_id == self.creator_actor_id:
                if not self.independent_verification_reference:
                    raise ValueError("S1/S2 self-closure requires independent verification.")
        return self


class QualityReview(BaseModel):
    model_config = ConfigDict(frozen=True)

    review_id: str = Field(min_length=1)
    artefact_reference: str = Field(min_length=1)
    assurance_tier: AssuranceTier
    reviewer_id: str = Field(min_length=1)
    creator_id: str = Field(min_length=1)
    dimensions: tuple[DimensionScore, ...]
    defects: tuple[Defect, ...] = ()
    independent_signoff_reference: str | None = None

    @field_validator("dimensions")
    @classmethod
    def require_unique_dimensions(
        cls, value: tuple[DimensionScore, ...]
    ) -> tuple[DimensionScore, ...]:
        ids = [item.dimension_id for item in value]
        if len(ids) != len(set(ids)):
            raise ValueError("Quality dimensions must be unique.")
        if not value:
            raise ValueError("At least one quality dimension is required.")
        return value

    @model_validator(mode="after")
    def validate_reviewer_independence(self) -> "QualityReview":
        if self.assurance_tier in {AssuranceTier.T2_HIGH, AssuranceTier.T3_CRITICAL}:
            if self.reviewer_id == self.creator_id:
                raise ValueError("T2/T3 review cannot be signed off solely by the creator.")
        return self

    @property
    def weighted_score(self) -> float:
        applicable = [item for item in self.dimensions if item.score is not None]
        total_weight = sum(DIMENSION_WEIGHTS[item.dimension_id] for item in applicable)
        if total_weight == 0:
            raise ValueError("No applicable dimensions are available for scoring.")
        weighted = sum(
            item.score * DIMENSION_WEIGHTS[item.dimension_id]
            for item in applicable
            if item.score is not None
        )
        return round(weighted / total_weight, 2)


class GateAssessment(BaseModel):
    model_config = ConfigDict(frozen=True)

    gate: QualityGate
    conclusion: ReviewConclusion
    weighted_score: float
    blocking_reasons: tuple[str, ...] = ()
    conditions: tuple[str, ...] = ()


_FOUNDER_FLOORS = {
    "QD-MAND-01": 3,
    "QD-EVID-01": 3,
    "QD-METH-01": 3,
    "QD-REAS-01": 3,
    "QD-EXEC-01": 3,
}


def assess_gate(review: QualityReview, gate: QualityGate) -> GateAssessment:
    """Assess a quality review against canonical score and defect thresholds."""

    score = review.weighted_score
    dimension_map = {
        item.dimension_id: item.score for item in review.dimensions if item.score is not None
    }
    blockers: list[str] = []
    conditions: list[str] = []
    open_defects = [item for item in review.defects if item.status != "closed"]

    if gate is QualityGate.INTERNAL_WORKING:
        if score < 2.50:
            blockers.append("Weighted score is below 2.50.")
        for dimension_id in ("QD-MAND-01", "QD-EVID-01", "QD-REAS-01"):
            value = dimension_map.get(dimension_id)
            if value is None or value < 2:
                blockers.append(f"{dimension_id} is below the internal floor of 2.")
        if any(value == 0 for value in dimension_map.values()):
            blockers.append("An applicable quality dimension scored 0.")
        if any(item.severity is DefectSeverity.S1_CRITICAL for item in open_defects):
            blockers.append("An unresolved S1 defect blocks all use.")
        if any(item.severity is DefectSeverity.S2_MAJOR for item in open_defects):
            conditions.append("S2 defects require explicit quarantine and no downstream reliance.")

    elif gate is QualityGate.FOUNDER_READY:
        if score < 3.00:
            blockers.append("Weighted score is below 3.00.")
        for dimension_id, floor in _FOUNDER_FLOORS.items():
            value = dimension_map.get(dimension_id)
            if value is None or value < floor:
                blockers.append(f"{dimension_id} is below the Founder-ready floor of {floor}.")
        financial = dimension_map.get("QD-FIN-01")
        if financial is not None and financial < 3:
            blockers.append("QD-FIN-01 is below 3 where financial integrity applies.")
        for dimension_id, value in dimension_map.items():
            if value < 2:
                blockers.append(f"{dimension_id} is below the general floor of 2.")
        if any(
            item.severity in {DefectSeverity.S1_CRITICAL, DefectSeverity.S2_MAJOR}
            for item in open_defects
        ):
            blockers.append("Founder-ready work cannot contain unresolved S1 or S2 defects.")
        if any(item.severity is DefectSeverity.S3_MODERATE for item in open_defects):
            conditions.append("Open S3 defects require an owner and due point.")

    elif gate in {QualityGate.EXTERNAL_RELEASE, QualityGate.CRITICAL_RELEASE}:
        if score < 3.20:
            blockers.append("Weighted score is below 3.20.")
        for dimension_id, value in dimension_map.items():
            if value < 3:
                blockers.append(f"{dimension_id} is below the external-release floor of 3.")
        if any(
            item.severity in {
                DefectSeverity.S1_CRITICAL,
                DefectSeverity.S2_MAJOR,
                DefectSeverity.S3_MODERATE,
            }
            and not item.accepted_exception_id
            for item in open_defects
        ):
            blockers.append("External release has unresolved S1, S2 or unaccepted S3 defects.")
        if review.assurance_tier in {AssuranceTier.T2_HIGH, AssuranceTier.T3_CRITICAL}:
            if not review.independent_signoff_reference:
                blockers.append("T2/T3 external release requires independent sign-off.")
        if gate is QualityGate.CRITICAL_RELEASE and review.assurance_tier is not AssuranceTier.T3_CRITICAL:
            blockers.append("Critical release requires T3 assurance classification.")

    if blockers:
        conclusion = ReviewConclusion.FAIL
    elif conditions:
        conclusion = ReviewConclusion.PASS_WITH_CONDITIONS
    else:
        conclusion = ReviewConclusion.PASS

    return GateAssessment(
        gate=gate,
        conclusion=conclusion,
        weighted_score=score,
        blocking_reasons=tuple(blockers),
        conditions=tuple(conditions),
    )


class ExceptionRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    exception_id: str = Field(min_length=1)
    unmet_rule: str = Field(min_length=1)
    artefact_reference: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    alternatives_considered: tuple[str, ...]
    residual_risk: str = Field(min_length=1)
    affected_stakeholders: tuple[str, ...]
    compensating_controls: tuple[str, ...]
    review_or_expiry_date: date
    decision_authority: str = Field(min_length=1)
    accepted: bool
    evidence_of_decision: str = Field(min_length=1)


class IndependentSignoff(BaseModel):
    model_config = ConfigDict(frozen=True)

    signoff_id: str = Field(min_length=1)
    artefact_reference: str = Field(min_length=1)
    artefact_checksum: str = Field(min_length=1)
    reviewer_name_or_role: str = Field(min_length=1)
    competence_basis: str = Field(min_length=1)
    independence_level: str = Field(min_length=1)
    conflicts_or_impairments: tuple[str, ...] = ()
    scope_of_review: str = Field(min_length=1)
    tests_performed: tuple[str, ...]
    unresolved_limitations: tuple[str, ...] = ()
    conclusion: ReviewConclusion
    record_reference: str = Field(min_length=1)
    date: date
