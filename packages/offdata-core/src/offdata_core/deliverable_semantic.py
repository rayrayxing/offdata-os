"""Semantic deliverable contracts shared by all rendered output surfaces."""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .delivery import (
    ArtefactApprovalStatus,
    CrossFormatReconciliation,
    DeliverableManifest,
    DeliverableSurface,
    StoryModel,
    VisualSpecification,
)


class CitationPresentation(StrEnum):
    FOOTNOTE = "footnote"
    SPEAKER_NOTES = "speaker_notes"
    APPENDIX = "appendix"
    SOURCE_TAB = "source_tab"
    ON_DEMAND = "on_demand"
    INTERNAL_ONLY = "internal_only"


class NumberSourceKind(StrEnum):
    MODEL_OUTPUT = "model_output"
    CONTROLLED_SOURCE = "controlled_source"


class SemanticObjectKind(StrEnum):
    COVER = "cover"
    EXECUTIVE_DECISION = "executive_decision"
    EVIDENCE = "evidence"
    ANALYSIS = "analysis"
    OPTIONS = "options"
    RECOMMENDATION = "recommendation"
    VALUE_CASE = "value_case"
    CONTROL_MODEL = "control_model"
    ROADMAP = "roadmap"
    APPROVAL = "approval"
    APPENDIX = "appendix"
    WORKBOOK_CHECK = "workbook_check"


class SurfaceObjectRole(StrEnum):
    COVER = "cover"
    EXECUTIVE_SUMMARY = "executive_summary"
    CONTENT = "content"
    APPENDIX = "appendix"
    README = "readme"
    SOURCE_DATA = "source_data"
    ASSUMPTIONS = "assumptions"
    CALCULATIONS = "calculations"
    OUTPUTS = "outputs"
    CHECKS = "checks"


class RenderForm(StrEnum):
    TEXT = "text"
    TABLE = "table"
    CHART = "chart"
    NATIVE_SHAPES = "native_shapes"
    SVG = "svg"
    FORMULA_SHEET = "formula_sheet"
    WEB_COMPONENT = "web_component"


class NumberReference(BaseModel):
    model_config = ConfigDict(frozen=True)

    number_id: str = Field(pattern=r"^NUM-[A-Z0-9-]+$")
    label: str = Field(min_length=1)
    value: float
    unit: str = Field(min_length=1)
    period: str = Field(min_length=1)
    source_kind: NumberSourceKind
    source_record_id: str = Field(min_length=1)
    source_field: str = Field(min_length=1)
    approved: bool
    display_precision: int = Field(ge=0, le=4)


class CitationReference(BaseModel):
    model_config = ConfigDict(frozen=True)

    citation_id: str = Field(pattern=r"^CITE-[A-Z0-9-]+$")
    source_ids: tuple[str, ...] = ()
    evidence_finding_ids: tuple[str, ...] = ()
    internal_provenance: str = Field(min_length=1)
    client_note: str = Field(min_length=1)
    presentation_modes: frozenset[CitationPresentation]
    material: bool = True

    @model_validator(mode="after")
    def require_traceable_support(self) -> "CitationReference":
        if not (self.source_ids or self.evidence_finding_ids):
            raise ValueError("Citation requires source IDs or evidence-finding IDs.")
        if CitationPresentation.INTERNAL_ONLY in self.presentation_modes and len(
            self.presentation_modes
        ) > 1:
            raise ValueError("Internal-only citation mode cannot be combined with client modes.")
        return self


class SemanticObject(BaseModel):
    model_config = ConfigDict(frozen=True)

    semantic_object_id: str = Field(pattern=r"^SEM-[A-Z0-9-]+$")
    kind: SemanticObjectKind
    title: str = Field(min_length=1)
    decision_purpose: str = Field(min_length=1)
    assertion_ids: tuple[str, ...] = ()
    number_ids: tuple[str, ...] = ()
    citation_ids: tuple[str, ...] = ()
    visual_specification_ids: tuple[str, ...] = ()
    recommendation_ids: tuple[str, ...] = ()
    roadmap_action_ids: tuple[str, ...] = ()
    uncertainty_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def require_decision_content(self) -> "SemanticObject":
        if self.kind not in {SemanticObjectKind.COVER, SemanticObjectKind.APPENDIX} and not (
            self.assertion_ids
            or self.number_ids
            or self.visual_specification_ids
            or self.recommendation_ids
            or self.roadmap_action_ids
        ):
            raise ValueError("Decision content object is empty.")
        return self


class SurfaceObject(BaseModel):
    model_config = ConfigDict(frozen=True)

    surface_object_id: str = Field(pattern=r"^SURF-[A-Z0-9-]+$")
    surface: DeliverableSurface
    semantic_object_id: str = Field(pattern=r"^SEM-[A-Z0-9-]+$")
    sequence: int = Field(gt=0)
    role: SurfaceObjectRole
    title: str = Field(min_length=1)
    render_form: RenderForm
    editable_required: bool = False


class SurfacePlan(BaseModel):
    model_config = ConfigDict(frozen=True)

    manifest: DeliverableManifest
    objects: tuple[SurfaceObject, ...]

    @model_validator(mode="after")
    def validate_surface_plan(self) -> "SurfacePlan":
        object_ids = [item.surface_object_id for item in self.objects]
        if len(object_ids) != len(set(object_ids)):
            raise ValueError("Surface object IDs must be unique within a plan.")
        sequences = [item.sequence for item in self.objects]
        if len(sequences) != len(set(sequences)):
            raise ValueError("Surface object sequence values must be unique.")
        if any(item.surface is not self.manifest.surface for item in self.objects):
            raise ValueError("Surface plan contains an object for another surface.")
        mapped_objects = {item.semantic_object_id for item in self.objects}
        if mapped_objects != set(self.manifest.included_object_ids):
            raise ValueError("Surface plan objects do not match the manifest object scope.")
        return self


class FounderReviewSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    decision: str = Field(min_length=1)
    requested_action: str = Field(min_length=1)
    recommendation: str = Field(min_length=1)
    material_assumptions: tuple[str, ...]
    material_uncertainties: tuple[str, ...]
    open_defect_ids: tuple[str, ...] = ()
    reconciliation_status: str = Field(min_length=1)
    client_citation_approach: str = Field(min_length=1)
    exact_release_action: str = Field(min_length=1)
    approval_required: bool = True


_REQUIRED_SURFACES = frozenset(
    {
        DeliverableSurface.PPTX,
        DeliverableSurface.DOCX,
        DeliverableSurface.XLSX,
        DeliverableSurface.PDF,
        DeliverableSurface.SVG,
        DeliverableSurface.HTML,
    }
)


class DeliverableSemanticModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    semantic_model_id: str = Field(pattern=r"^DSM-[A-Z0-9-]+$")
    version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    fixture_id: str = Field(min_length=1)
    analytical_baseline_id: str = Field(min_length=1)
    analytical_baseline_version: str = Field(min_length=1)
    analytical_input_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    agent_visible: bool
    story: StoryModel
    numbers: tuple[NumberReference, ...]
    citations: tuple[CitationReference, ...]
    visuals: tuple[VisualSpecification, ...]
    semantic_objects: tuple[SemanticObject, ...]
    surface_plans: tuple[SurfacePlan, ...]
    reconciliation: CrossFormatReconciliation
    founder_review: FounderReviewSummary
    prohibited_conclusions: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_semantic_integrity(self) -> "DeliverableSemanticModel":
        number_ids = _unique_ids(self.numbers, "number_id", "Number")
        citation_ids = _unique_ids(self.citations, "citation_id", "Citation")
        visual_ids = _unique_ids(
            self.visuals, "visual_specification_id", "Visual specification"
        )
        semantic_ids = _unique_ids(
            self.semantic_objects, "semantic_object_id", "Semantic object"
        )
        if not all(item.approved for item in self.numbers):
            raise ValueError("Semantic deliverables may display only approved numbers.")

        assertion_ids = {item.assertion_id for item in self.story.assertions}
        represented_assertions: set[str] = set()
        represented_visuals: set[str] = set()
        for item in self.semantic_objects:
            _require_subset(item.assertion_ids, assertion_ids, item.semantic_object_id, "assertion")
            _require_subset(item.number_ids, number_ids, item.semantic_object_id, "number")
            _require_subset(item.citation_ids, citation_ids, item.semantic_object_id, "citation")
            _require_subset(
                item.visual_specification_ids,
                visual_ids,
                item.semantic_object_id,
                "visual",
            )
            represented_assertions.update(item.assertion_ids)
            represented_visuals.update(item.visual_specification_ids)
        if represented_assertions != assertion_ids:
            missing = sorted(assertion_ids - represented_assertions)
            raise ValueError(f"Story assertions are not represented by semantic objects: {missing}")
        if represented_visuals != visual_ids:
            missing = sorted(visual_ids - represented_visuals)
            raise ValueError(f"Visual specifications are not represented: {missing}")

        plans_by_surface = {item.manifest.surface: item for item in self.surface_plans}
        if len(plans_by_surface) != len(self.surface_plans):
            raise ValueError("Only one surface plan is allowed per output surface.")
        if set(plans_by_surface) != _REQUIRED_SURFACES:
            missing = sorted(surface.value for surface in _REQUIRED_SURFACES - set(plans_by_surface))
            extra = sorted(surface.value for surface in set(plans_by_surface) - _REQUIRED_SURFACES)
            raise ValueError(f"Semantic model surface set mismatch; missing={missing}, extra={extra}")

        mapped_semantic_ids: set[str] = set()
        deliverable_ids: set[str] = set()
        for plan in self.surface_plans:
            manifest = plan.manifest
            deliverable_ids.add(manifest.file_id)
            if manifest.baseline_story_model_id != self.story.story_model_id:
                raise ValueError("Deliverable manifest references another story model.")
            if manifest.baseline_story_model_version != self.story.version:
                raise ValueError("Deliverable manifest references another story-model version.")
            if manifest.approval_status not in {
                ArtefactApprovalStatus.REVIEW,
                ArtefactApprovalStatus.APPROVED,
            }:
                raise ValueError("Semantic release plans must be in review or approved state.")
            _require_subset(
                manifest.included_object_ids,
                semantic_ids,
                manifest.file_id,
                "semantic object",
            )
            mapped_semantic_ids.update(manifest.included_object_ids)
            for surface_object in plan.objects:
                semantic = next(
                    item
                    for item in self.semantic_objects
                    if item.semantic_object_id == surface_object.semantic_object_id
                )
                if semantic.visual_specification_ids and surface_object.editable_required:
                    if surface_object.render_form not in {
                        RenderForm.CHART,
                        RenderForm.NATIVE_SHAPES,
                        RenderForm.SVG,
                        RenderForm.WEB_COMPONENT,
                    }:
                        raise ValueError(
                            "Editable labelled visual is not mapped to an editable render form."
                        )
                for visual_id in semantic.visual_specification_ids:
                    visual = next(
                        item
                        for item in self.visuals
                        if item.visual_specification_id == visual_id
                    )
                    if plan.manifest.surface not in visual.allowed_surfaces:
                        raise ValueError(
                            f"Visual {visual_id} is not allowed on {plan.manifest.surface.value}."
                        )
        if mapped_semantic_ids != semantic_ids:
            missing = sorted(semantic_ids - mapped_semantic_ids)
            raise ValueError(f"Semantic objects are absent from all surfaces: {missing}")

        if self.reconciliation.story_model_id != self.story.story_model_id:
            raise ValueError("Reconciliation references another story model.")
        if set(self.reconciliation.deliverable_ids) != deliverable_ids:
            raise ValueError("Reconciliation deliverable scope does not match the surface plans.")
        if not self.reconciliation.passed:
            raise ValueError("The first semantic model must pass deterministic reconciliation.")
        if self.founder_review.reconciliation_status.casefold() != "passed":
            raise ValueError("Founder review summary must report passed reconciliation.")
        if not self.founder_review.approval_required:
            raise ValueError("Founder approval is required before external deliverable release.")
        return self


class SemanticModelGrade(BaseModel):
    model_config = ConfigDict(frozen=True)

    passed: bool
    checks_run: int = Field(ge=0)
    checks_passed: int = Field(ge=0)
    failures: tuple[str, ...]

    @model_validator(mode="after")
    def validate_counts(self) -> "SemanticModelGrade":
        if self.checks_passed + len(self.failures) != self.checks_run:
            raise ValueError("Semantic-model grade counts do not reconcile.")
        if self.passed != (not self.failures):
            raise ValueError("Semantic-model grade status does not match failures.")
        return self


def semantic_model_digest(model: DeliverableSemanticModel) -> str:
    payload = json.dumps(
        model.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _unique_ids(items: tuple[BaseModel, ...], field: str, label: str) -> set[str]:
    values = [str(getattr(item, field)) for item in items]
    if len(values) != len(set(values)):
        raise ValueError(f"{label} IDs must be unique.")
    return set(values)


def _require_subset(
    values: tuple[str, ...],
    allowed: set[str],
    owner: str,
    label: str,
) -> None:
    missing = set(values) - allowed
    if missing:
        raise ValueError(f"{owner} references unknown {label} IDs: {sorted(missing)}")
