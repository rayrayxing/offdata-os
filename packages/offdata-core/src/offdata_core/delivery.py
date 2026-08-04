"""Story, visual specification and cross-deliverable reconciliation contracts."""

from enum import StrEnum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)


class EpistemicStatus(StrEnum):
    ESTABLISHED_FACT = "established_fact"
    ACCEPTED_PRACTICE = "accepted_practice"
    REASONED_SYNTHESIS = "reasoned_synthesis"
    RECOMMENDATION = "recommendation"
    ASSUMPTION = "assumption"
    EVIDENCE_GAP = "evidence_gap"


class DeliverableSurface(StrEnum):
    PPTX = "pptx"
    DOCX = "docx"
    XLSX = "xlsx"
    PDF = "pdf"
    SVG = "svg"
    HTML = "html"
    OTHER = "other"


class ArtefactAuthority(StrEnum):
    CANONICAL = "canonical"
    DERIVED = "derived"
    WORKING = "working"
    ARCHIVE = "archive"


class ArtefactApprovalStatus(StrEnum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    ISSUED = "issued"
    SUPERSEDED = "superseded"


class VisualArchetype(StrEnum):
    MATURITY_CURVE = "maturity_curve"
    RADIAL_FRAMEWORK = "radial_framework"
    LAYERED_STACK = "layered_stack"
    CAUSAL_NARRATIVE = "causal_narrative"
    VALUE_DRIVER_TREE = "value_driver_tree"
    ROADMAP = "roadmap"
    JOURNEY = "journey"
    PROCESS_FLOW = "process_flow"
    GOVERNANCE_MODEL = "governance_model"
    OPERATING_MODEL = "operating_model"
    PORTFOLIO_MATRIX = "portfolio_matrix"
    WATERFALL = "waterfall"
    NETWORK_MAP = "network_map"
    SCENARIO_CONE = "scenario_cone"


class Assertion(BaseModel):
    model_config = ConfigDict(frozen=True)

    assertion_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    epistemic_status: EpistemicStatus
    evidence_ids: tuple[str, ...] = ()
    analysis_ids: tuple[str, ...] = ()
    assumption_ids: tuple[str, ...] = ()
    conditions: tuple[str, ...] = ()
    material: bool = True

    @model_validator(mode="after")
    def validate_support(self) -> "Assertion":
        if self.epistemic_status in {
            EpistemicStatus.ESTABLISHED_FACT,
            EpistemicStatus.ACCEPTED_PRACTICE,
        } and not self.evidence_ids:
            raise ValueError("Fact and accepted-practice assertions require evidence IDs.")
        if self.epistemic_status is EpistemicStatus.RECOMMENDATION and not (
            self.evidence_ids or self.analysis_ids
        ):
            raise ValueError("Recommendation assertions require evidence or analysis support.")
        return self


class StorySection(BaseModel):
    model_config = ConfigDict(frozen=True)

    section_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    assertion_ids: tuple[str, ...]
    visual_specification_ids: tuple[str, ...] = ()
    required_number_ids: tuple[str, ...] = ()
    required_source_ids: tuple[str, ...] = ()


class StoryModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    story_model_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    engagement_id: str = Field(min_length=1)
    decision_id: str = Field(min_length=1)
    audience_roles: tuple[str, ...]
    communication_objective: str = Field(min_length=1)
    governing_thought: str = Field(min_length=1)
    assertions: tuple[Assertion, ...]
    sections: tuple[StorySection, ...]
    key_number_ids: tuple[str, ...] = ()
    recommendation_ids: tuple[str, ...] = ()
    roadmap_action_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_story_references(self) -> "StoryModel":
        assertion_ids = {item.assertion_id for item in self.assertions}
        if len(assertion_ids) != len(self.assertions):
            raise ValueError("Story assertions require unique IDs.")
        for section in self.sections:
            missing = set(section.assertion_ids) - assertion_ids
            if missing:
                raise ValueError(
                    f"Section {section.section_id} references missing assertions: {sorted(missing)}"
                )
        return self


class VisualEntity(BaseModel):
    model_config = ConfigDict(frozen=True)

    entity_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    description: str = ""
    data_reference: str | None = None
    category: str = ""


class VisualRelationship(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_entity_id: str = Field(min_length=1)
    target_entity_id: str = Field(min_length=1)
    relationship: str = Field(min_length=1)
    label: str = ""


class VisualSpecification(BaseModel):
    model_config = ConfigDict(frozen=True)

    visual_specification_id: str = Field(min_length=1)
    archetype: VisualArchetype
    message: str = Field(min_length=1)
    entities: tuple[VisualEntity, ...]
    relationships: tuple[VisualRelationship, ...] = ()
    layout_rules: tuple[str, ...]
    editable_output_required: bool = True
    accessibility_rules: tuple[str, ...]
    allowed_surfaces: frozenset[DeliverableSurface]
    decorative_image_reference: str | None = None

    @field_serializer("allowed_surfaces")
    def serialise_allowed_surfaces(
        self, value: frozenset[DeliverableSurface]
    ) -> list[str]:
        return sorted(item.value for item in value)

    @model_validator(mode="after")
    def validate_relationship_entities(self) -> "VisualSpecification":
        entity_ids = {item.entity_id for item in self.entities}
        if not entity_ids:
            raise ValueError("Visual specification requires at least one entity.")
        for relationship in self.relationships:
            if relationship.source_entity_id not in entity_ids:
                raise ValueError("Visual relationship references an unknown source entity.")
            if relationship.target_entity_id not in entity_ids:
                raise ValueError("Visual relationship references an unknown target entity.")
        return self


class DeliverableManifest(BaseModel):
    model_config = ConfigDict(frozen=True)

    file_id: str = Field(min_length=1)
    filename: str = Field(min_length=1)
    surface: DeliverableSurface
    purpose: str = Field(min_length=1)
    audience_roles: tuple[str, ...]
    authority: ArtefactAuthority
    version: str = Field(min_length=1)
    baseline_story_model_id: str = Field(min_length=1)
    baseline_story_model_version: str = Field(min_length=1)
    model_version_ids: tuple[str, ...] = ()
    evidence_baseline_ids: tuple[str, ...] = ()
    owner: str = Field(min_length=1)
    approval_status: ArtefactApprovalStatus
    included_object_ids: tuple[str, ...]
    excluded_content: dict[str, str] = Field(default_factory=dict)
    generated_from: tuple[str, ...]
    last_reconciliation_reference: str | None = None
    confidentiality_marking: str = ""


class ReconciliationCheck(StrEnum):
    HEADLINE = "headline"
    ASSUMPTION = "assumption"
    NUMBER = "number"
    RECOMMENDATION = "recommendation"
    ROADMAP = "roadmap"
    SOURCE = "source"
    VERSION = "version"
    RENDERED_INSPECTION = "rendered_inspection"


_REQUIRED_RECONCILIATION_CHECKS = frozenset(ReconciliationCheck)


class ReconciliationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    check: ReconciliationCheck
    passed: bool
    details: str = Field(min_length=1)
    defect_ids: tuple[str, ...] = ()


class CrossFormatReconciliation(BaseModel):
    model_config = ConfigDict(frozen=True)

    reconciliation_id: str = Field(min_length=1)
    story_model_id: str = Field(min_length=1)
    deliverable_ids: tuple[str, ...]
    results: tuple[ReconciliationResult, ...]
    reviewer_id: str = Field(min_length=1)

    @field_validator("deliverable_ids")
    @classmethod
    def require_multiple_surfaces(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) < 2:
            raise ValueError("Cross-format reconciliation requires at least two deliverables.")
        return value

    @model_validator(mode="after")
    def require_complete_reconciliation(self) -> "CrossFormatReconciliation":
        checks = {item.check for item in self.results}
        missing = _REQUIRED_RECONCILIATION_CHECKS - checks
        if missing:
            raise ValueError(
                "Reconciliation is missing checks: "
                + ", ".join(sorted(item.value for item in missing))
            )
        if len(checks) != len(self.results):
            raise ValueError("Reconciliation checks must be unique.")
        return self

    @property
    def passed(self) -> bool:
        return all(item.passed for item in self.results)
