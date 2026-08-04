"""Typed knowledge, source and methodology records."""

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SourceType(StrEnum):
    PUBLIC_WEB = "public_web"
    STANDARD = "standard"
    REGULATOR = "regulator"
    GOVERNMENT = "government"
    ACADEMIC = "academic"
    PROFESSIONAL_BODY = "professional_body"
    CLIENT_DOCUMENT = "client_document"
    CLIENT_DATASET = "client_dataset"
    INTERVIEW = "interview"
    SURVEY = "survey"
    INTERNAL_METHOD = "internal_method"


class AuthorityClass(StrEnum):
    PRIMARY_BINDING = "primary_binding"
    PRIMARY_AUTHORITATIVE = "primary_authoritative"
    SECONDARY_RELIABLE = "secondary_reliable"
    PRACTITIONER = "practitioner"
    MARKETING = "marketing"
    UNVERIFIED = "unverified"


class ConfidentialityClass(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CLIENT_CONFIDENTIAL = "client_confidential"
    RESTRICTED = "restricted"


class PromotionState(StrEnum):
    DRAFT = "draft"
    QUARANTINED = "quarantined"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class InferenceType(StrEnum):
    DESCRIPTIVE = "descriptive"
    PREDICTIVE = "predictive"
    CAUSAL = "causal"
    NORMATIVE = "normative"


class CandidateDecision(StrEnum):
    HOLD = "hold"
    PROMOTE = "promote"
    REJECT = "reject"
    MERGE = "merge"
    SUPERSEDE = "supersede"


class SourceDocument(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_id: str = Field(min_length=1)
    original_filename: str = Field(min_length=1)
    checksum_sha256: str
    title: str = Field(min_length=1)
    author: str = ""
    issuer: str = ""
    version: str = ""
    publication_date: date | None = None
    retrieval_date: date
    review_date: date | None = None
    source_type: SourceType
    authority_class: AuthorityClass
    object_reference: str = Field(min_length=1)
    licence: str = ""
    copyright_notes: str = ""
    usage_restrictions: tuple[str, ...] = ()
    confidentiality: ConfidentialityClass
    tenant_id: str | None = None
    engagement_id: str | None = None
    jurisdiction: str | None = None
    time_sensitive: bool = False
    superseded_by: str | None = None

    @field_validator("checksum_sha256")
    @classmethod
    def validate_sha256(cls, value: str) -> str:
        normalized = value.lower()
        if len(normalized) != 64 or any(char not in "0123456789abcdef" for char in normalized):
            raise ValueError("checksum_sha256 must be a 64-character hexadecimal SHA-256.")
        return normalized

    @model_validator(mode="after")
    def validate_confidential_scope(self) -> "SourceDocument":
        if self.confidentiality in {
            ConfidentialityClass.CLIENT_CONFIDENTIAL,
            ConfidentialityClass.RESTRICTED,
        } and not self.tenant_id:
            raise ValueError("Confidential client sources require tenant scope.")
        return self


class SourcePassage(BaseModel):
    model_config = ConfigDict(frozen=True)

    passage_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    page: int | None = Field(default=None, ge=1)
    section: str | None = None
    paragraph: int | None = Field(default=None, ge=1)
    start_line: int | None = Field(default=None, ge=1)
    end_line: int | None = Field(default=None, ge=1)
    table_or_figure_reference: str | None = None
    extraction_method: str = Field(min_length=1)
    extraction_confidence: float = Field(ge=0, le=1)
    lexical_index_reference: str | None = None
    semantic_index_reference: str | None = None

    @model_validator(mode="after")
    def require_location(self) -> "SourcePassage":
        if not any(
            value is not None and value != ""
            for value in (self.page, self.section, self.paragraph, self.start_line)
        ):
            raise ValueError("Source passage requires a page, section, paragraph or line location.")
        if self.start_line and self.end_line and self.end_line < self.start_line:
            raise ValueError("end_line cannot be earlier than start_line.")
        return self


class MethodRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    method_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    aliases: tuple[str, ...] = ()
    domains: tuple[str, ...]
    method_family: str = Field(min_length=1)
    decisions_supported: tuple[str, ...]
    inference_types: frozenset[InferenceType]
    appropriate_problem_types: tuple[str, ...]
    preconditions: tuple[str, ...]
    minimum_evidence: str = Field(pattern="^E[1-4]$")
    inputs: tuple[str, ...]
    procedure: tuple[str, ...]
    outputs: tuple[str, ...]
    strengths: tuple[str, ...] = ()
    limitations: tuple[str, ...]
    when_not_to_use: tuple[str, ...]
    alternatives: tuple[str, ...] = ()
    compatible_overlays: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    redundancies: tuple[str, ...] = ()
    tool_requirements: tuple[str, ...] = ()
    specialist_review_requirements: tuple[str, ...] = ()
    failure_modes: tuple[str, ...]
    quality_tests: tuple[str, ...]
    falsification_tests: tuple[str, ...]
    source_ids: tuple[str, ...]
    usage_rights_status: str = Field(min_length=1)
    version: str = Field(min_length=1)
    promotion_state: PromotionState

    @model_validator(mode="after")
    def validate_minimum_content(self) -> "MethodRecord":
        required_collections = {
            "domains": self.domains,
            "decisions_supported": self.decisions_supported,
            "inference_types": self.inference_types,
            "appropriate_problem_types": self.appropriate_problem_types,
            "preconditions": self.preconditions,
            "inputs": self.inputs,
            "procedure": self.procedure,
            "outputs": self.outputs,
            "limitations": self.limitations,
            "when_not_to_use": self.when_not_to_use,
            "failure_modes": self.failure_modes,
            "quality_tests": self.quality_tests,
            "falsification_tests": self.falsification_tests,
            "source_ids": self.source_ids,
        }
        missing = [name for name, values in required_collections.items() if not values]
        if missing:
            raise ValueError("Method record missing required content: " + ", ".join(missing))
        return self


class ProblemArchetype(BaseModel):
    model_config = ConfigDict(frozen=True)

    archetype_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    domains: tuple[str, ...]
    diagnostic_signature: tuple[str, ...]
    governing_decision_question: str = Field(min_length=1)
    unit_of_analysis: str = Field(min_length=1)
    typical_hypotheses: tuple[str, ...]
    rival_explanations: tuple[str, ...]
    primary_methods: tuple[str, ...]
    optional_overlays: tuple[str, ...] = ()
    evidence_indicators: tuple[str, ...]
    failure_modes: tuple[str, ...]
    escalation_conditions: tuple[str, ...]


class MethodSelection(BaseModel):
    model_config = ConfigDict(frozen=True)

    selection_id: str = Field(min_length=1)
    engagement_id: str = Field(min_length=1)
    decision_id: str = Field(min_length=1)
    governing_archetype: str = Field(min_length=1)
    supporting_archetypes: tuple[str, ...] = ()
    selected_methods: tuple[str, ...]
    sequence_rationale: tuple[str, ...]
    method_roles: dict[str, str]
    rejected_methods: dict[str, str] = Field(default_factory=dict)
    required_data: tuple[str, ...]
    required_tools: tuple[str, ...] = ()
    required_reviewers: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    evidence_gaps: tuple[str, ...] = ()
    founder_approval_required: bool = False

    @model_validator(mode="after")
    def validate_roles(self) -> "MethodSelection":
        if not self.selected_methods:
            raise ValueError("At least one method must be selected.")
        missing_roles = [method for method in self.selected_methods if method not in self.method_roles]
        if missing_roles:
            raise ValueError("Selected methods missing roles: " + ", ".join(missing_roles))
        return self


class MethodologyCandidate(BaseModel):
    model_config = ConfigDict(frozen=True)

    candidate_id: str = Field(min_length=1)
    discovered_at: datetime
    discovery_source_ids: tuple[str, ...]
    claimed_name: str = Field(min_length=1)
    claimed_description: str = Field(min_length=1)
    novelty_assessment: str = Field(min_length=1)
    existing_method_comparison: dict[str, str]
    primary_support_ids: tuple[str, ...]
    copyright_assessment: str = Field(min_length=1)
    trademark_assessment: str = ""
    licence_assessment: str = ""
    original_reconstruction: dict[str, Any]
    evaluation_fixture_ids: tuple[str, ...]
    evaluation_results: dict[str, Any]
    provenance_review_complete: bool = False
    regression_tests_passed: bool = False
    reviewer: str = ""
    founder_approved: bool = False
    decision: CandidateDecision = CandidateDecision.HOLD

    @model_validator(mode="after")
    def validate_promotion(self) -> "MethodologyCandidate":
        if self.decision in {
            CandidateDecision.PROMOTE,
            CandidateDecision.MERGE,
            CandidateDecision.SUPERSEDE,
        }:
            missing: list[str] = []
            if not self.provenance_review_complete:
                missing.append("provenance review")
            if not self.regression_tests_passed:
                missing.append("regression tests")
            if not self.reviewer.strip():
                missing.append("reviewer")
            if not self.founder_approved:
                missing.append("Founder approval")
            if missing:
                raise ValueError("Promotion decision missing: " + ", ".join(missing))
        return self
