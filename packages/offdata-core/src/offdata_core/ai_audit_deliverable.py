"""Deterministic first deliverable semantic model for the Northstar AI audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .ai_audit_models import AIAuditOracleResult
from .ai_audit_oracle import ANSWER_KEY_NAME, ORACLE_BASELINE_NAME, build_ai_audit_oracle
from .deliverable_semantic import (
    CitationPresentation,
    CitationReference,
    DeliverableSemanticModel,
    FounderReviewSummary,
    NumberReference,
    NumberSourceKind,
    RenderForm,
    SemanticModelGrade,
    SemanticObject,
    SemanticObjectKind,
    SurfaceObject,
    SurfaceObjectRole,
    SurfacePlan,
    semantic_model_digest,
)
from .delivery import (
    ArtefactApprovalStatus,
    ArtefactAuthority,
    Assertion,
    CrossFormatReconciliation,
    DeliverableManifest,
    DeliverableSurface,
    EpistemicStatus,
    ReconciliationCheck,
    ReconciliationResult,
    StoryModel,
    StorySection,
    VisualArchetype,
    VisualEntity,
    VisualRelationship,
    VisualSpecification,
)

DELIVERABLE_MODEL_VERSION = "1.0.0"
DELIVERABLE_SEMANTIC_BASELINE_NAME = "deliverable-semantic-baseline.json"
DELIVERABLE_SEMANTIC_MODEL_ID = "DSM-DAI-001"
STORY_MODEL_ID = "STORY-DAI-001"
DECISION_ID = "DEC-DAI-001"

_REQUIRED_SURFACES = (
    DeliverableSurface.PPTX,
    DeliverableSurface.DOCX,
    DeliverableSurface.XLSX,
    DeliverableSurface.PDF,
    DeliverableSurface.SVG,
    DeliverableSurface.HTML,
)
_DECISION_SURFACES = frozenset(
    {
        DeliverableSurface.PPTX,
        DeliverableSurface.DOCX,
        DeliverableSurface.PDF,
        DeliverableSurface.SVG,
        DeliverableSurface.HTML,
    }
)
_ALL_VISUAL_SURFACES = frozenset(set(_DECISION_SURFACES) | {DeliverableSurface.XLSX})


class _CheckCollector:
    def __init__(self) -> None:
        self.count = 0
        self.failures: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        self.count += 1
        if not condition:
            self.failures.append(message)


def _number(
    number_id: str,
    label: str,
    value: float,
    unit: str,
    period: str,
    source_record_id: str,
    source_field: str,
    precision: int,
) -> NumberReference:
    return NumberReference(
        number_id=number_id,
        label=label,
        value=value,
        unit=unit,
        period=period,
        source_kind=NumberSourceKind.MODEL_OUTPUT,
        source_record_id=source_record_id,
        source_field=source_field,
        approved=True,
        display_precision=precision,
    )


def _citation(
    citation_id: str,
    source_ids: tuple[str, ...],
    evidence_finding_ids: tuple[str, ...],
    internal_provenance: str,
    client_note: str,
) -> CitationReference:
    return CitationReference(
        citation_id=citation_id,
        source_ids=source_ids,
        evidence_finding_ids=evidence_finding_ids,
        internal_provenance=internal_provenance,
        client_note=client_note,
        presentation_modes=frozenset(
            {
                CitationPresentation.FOOTNOTE,
                CitationPresentation.SPEAKER_NOTES,
                CitationPresentation.APPENDIX,
                CitationPresentation.SOURCE_TAB,
                CitationPresentation.ON_DEMAND,
            }
        ),
    )


def _surface_object(
    surface: DeliverableSurface,
    index: int,
    semantic_object_id: str,
    role: SurfaceObjectRole,
    title: str,
    render_form: RenderForm,
    *,
    editable_required: bool = False,
) -> SurfaceObject:
    return SurfaceObject(
        surface_object_id=f"SURF-DAI-{surface.value.upper()}-{index:03d}",
        surface=surface,
        semantic_object_id=semantic_object_id,
        sequence=index,
        role=role,
        title=title,
        render_form=render_form,
        editable_required=editable_required,
    )


def _manifest(
    surface: DeliverableSurface,
    filename: str,
    purpose: str,
    audience_roles: tuple[str, ...],
    included_object_ids: tuple[str, ...],
    source_ids: tuple[str, ...],
) -> DeliverableManifest:
    return DeliverableManifest(
        file_id=f"FILE-DAI-{surface.value.upper()}-001",
        filename=filename,
        surface=surface,
        purpose=purpose,
        audience_roles=audience_roles,
        authority=ArtefactAuthority.DERIVED,
        version=DELIVERABLE_MODEL_VERSION,
        baseline_story_model_id=STORY_MODEL_ID,
        baseline_story_model_version=DELIVERABLE_MODEL_VERSION,
        model_version_ids=("FIXTURE-DAI-001:oracle:1.0.0",),
        evidence_baseline_ids=source_ids,
        owner="Deliverable Production Agent",
        approval_status=ArtefactApprovalStatus.APPROVED,
        included_object_ids=included_object_ids,
        excluded_content={
            "autonomous_chatbot": "Deferred because the evidence does not establish safe autonomous response.",
            "headcount_savings": "No immediate cash-releasing headcount benefit is recognised.",
        },
        generated_from=(DELIVERABLE_SEMANTIC_MODEL_ID, "FIXTURE-DAI-001:oracle:1.0.0"),
        last_reconciliation_reference="RECON-DAI-001",
        confidentiality_marking="Confidential — synthetic evaluation fixture",
    )


def build_ai_audit_deliverable_semantic_model(
    oracle: AIAuditOracleResult,
) -> DeliverableSemanticModel:
    """Build one shared semantic model for every required output surface."""

    analytical_baseline_id = f"{oracle.fixture_id}:oracle:{oracle.oracle_version}"
    finding_by_id = {item.finding_id: item for item in oracle.evidence_findings}
    evidence_source_ids = tuple(
        sorted({source_id for item in oracle.evidence_findings for source_id in item.source_ids})
    )

    numbers = (
        _number(
            "NUM-DAI-001",
            "Annualised quotation volume",
            float(oracle.quotation.annualised_volume),
            "quotations",
            "annualised",
            analytical_baseline_id,
            "quotation.annualised_volume",
            0,
        ),
        _number(
            "NUM-DAI-002",
            "Annualised measured quotation touch time",
            oracle.quotation.annualised_touch_hours,
            "hours",
            "annualised",
            analytical_baseline_id,
            "quotation.annualised_touch_hours",
            1,
        ),
        _number(
            "NUM-DAI-003",
            "Simple and standard share of quotation volume",
            oracle.quotation.simple_and_standard_volume_share_percent,
            "percent",
            "six_month_observation",
            analytical_baseline_id,
            "quotation.simple_and_standard_volume_share_percent",
            2,
        ),
        _number(
            "NUM-DAI-004",
            "Complex and engineered share of measured touch time",
            oracle.quotation.complex_and_engineered_touch_share_percent,
            "percent",
            "six_month_observation",
            analytical_baseline_id,
            "quotation.complex_and_engineered_touch_share_percent",
            2,
        ),
        _number(
            "NUM-DAI-005",
            "Annual customer-service tickets",
            float(oracle.customer_service.annual_ticket_count),
            "tickets",
            "annual",
            analytical_baseline_id,
            "customer_service.annual_ticket_count",
            0,
        ),
        _number(
            "NUM-DAI-006",
            "Autonomous-ready customer-service share",
            oracle.customer_service.autonomous_ready_share_percent,
            "percent",
            "current",
            analytical_baseline_id,
            "customer_service.autonomous_ready_share_percent",
            1,
        ),
        _number(
            "NUM-DAI-007",
            "Approved-knowledge coverage",
            oracle.customer_service.weighted_approved_knowledge_coverage_percent,
            "percent",
            "current",
            analytical_baseline_id,
            "customer_service.weighted_approved_knowledge_coverage_percent",
            2,
        ),
        _number(
            "NUM-DAI-008",
            "Public-AI use",
            oracle.workforce.weighted_public_ai_use_percent,
            "percent",
            "survey",
            analytical_baseline_id,
            "workforce.weighted_public_ai_use_percent",
            2,
        ),
        _number(
            "NUM-DAI-009",
            "Interest in AI training",
            oracle.workforce.weighted_training_interest_percent,
            "percent",
            "survey",
            analytical_baseline_id,
            "workforce.weighted_training_interest_percent",
            2,
        ),
        _number(
            "NUM-DAI-010",
            "Base pilot cost",
            oracle.financial.base_pilot_cost_sgd,
            "SGD",
            "pilot",
            analytical_baseline_id,
            "financial.base_pilot_cost_sgd",
            0,
        ),
        _number(
            "NUM-DAI-011",
            "Downside pilot cost",
            oracle.financial.downside_pilot_cost_sgd,
            "SGD",
            "pilot",
            analytical_baseline_id,
            "financial.downside_pilot_cost_sgd",
            0,
        ),
        _number(
            "NUM-DAI-012",
            "Maximum initial cash commitment",
            oracle.maximum_initial_cash_commitment_sgd,
            "SGD",
            "pilot",
            analytical_baseline_id,
            "maximum_initial_cash_commitment_sgd",
            0,
        ),
        _number(
            "NUM-DAI-013",
            "Annual addressable capacity value",
            oracle.financial.annual_addressable_capacity_value_sgd,
            "SGD",
            "annual",
            analytical_baseline_id,
            "financial.annual_addressable_capacity_value_sgd",
            0,
        ),
        _number(
            "NUM-DAI-014",
            "Potential annual incremental gross margin",
            oracle.financial.annual_potential_incremental_gross_margin_sgd,
            "SGD",
            "annual",
            analytical_baseline_id,
            "financial.annual_potential_incremental_gross_margin_sgd",
            0,
        ),
        _number(
            "NUM-DAI-015",
            "Annual platform and support cost",
            oracle.financial.annual_platform_and_support_cost_sgd,
            "SGD",
            "annual",
            analytical_baseline_id,
            "financial.annual_platform_and_support_cost_sgd",
            0,
        ),
        _number(
            "NUM-DAI-016",
            "Immediate cash-releasing headcount benefit",
            oracle.financial.immediate_cash_releasing_headcount_benefit_sgd,
            "SGD",
            "year_one",
            analytical_baseline_id,
            "financial.immediate_cash_releasing_headcount_benefit_sgd",
            0,
        ),
        _number(
            "NUM-DAI-017",
            "Recurring-support break-even capacity redeployment",
            oracle.financial.recurring_support_break_even_capacity_redeployment_percent,
            "percent",
            "annual",
            analytical_baseline_id,
            "financial.recurring_support_break_even_capacity_redeployment_percent",
            2,
        ),
        _number(
            "NUM-DAI-018",
            "Year-one pilot-and-support break-even conversion uplift",
            oracle.financial.year_one_pilot_and_support_break_even_conversion_uplift_points,
            "percentage_points",
            "year_one",
            analytical_baseline_id,
            "financial.year_one_pilot_and_support_break_even_conversion_uplift_points",
            2,
        ),
    )

    citations = (
        _citation(
            "CITE-DAI-001",
            finding_by_id["EXP-EVID-001"].source_ids,
            ("EXP-EVID-001",),
            "Quotation activity rows QA-001 to QA-024 and the sales-leadership interview; limitations retained in the evidence ledger.",
            "Company interviews and quotation activity; offdata analysis.",
        ),
        _citation(
            "CITE-DAI-002",
            finding_by_id["EXP-EVID-002"].source_ids,
            ("EXP-EVID-002",),
            "Quotation timestamps and measured touch-time fields; waiting causes remain partly unresolved.",
            "Company quotation activity; offdata analysis.",
        ),
        _citation(
            "CITE-DAI-003",
            finding_by_id["EXP-EVID-003"].source_ids,
            ("EXP-EVID-003",),
            "Customer-service summary, stakeholder interview and risk/control data; missing resolution codes retained as a limitation.",
            "Company service data and interviews; offdata analysis.",
        ),
        _citation(
            "CITE-DAI-004",
            finding_by_id["EXP-EVID-004"].source_ids,
            ("EXP-EVID-004",),
            "Inventory-process, application and data evidence; no controlled Northstar back-test exists.",
            "Company process and data inventories; offdata analysis.",
        ),
        _citation(
            "CITE-DAI-005",
            finding_by_id["EXP-EVID-005"].source_ids,
            ("EXP-EVID-005",),
            "Workforce survey, stakeholder interview and risk/control records; survey use is self-reported.",
            "Company workforce survey and controls data; offdata analysis.",
        ),
        _citation(
            "CITE-DAI-006",
            finding_by_id["EXP-EVID-006"].source_ids,
            ("EXP-EVID-006",),
            "Management financial case and controlled financial baseline; conversion uplift remains unvalidated.",
            "Company financial baseline; offdata analysis.",
        ),
    )

    assertions = (
        Assertion(
            assertion_id="AST-DAI-001",
            statement="Northstar should approve one bounded quotation-drafting pilot, retain the non-AI comparator and defer scale until evidence and controls pass.",
            epistemic_status=EpistemicStatus.RECOMMENDATION,
            evidence_ids=("EXP-EVID-001", "EXP-EVID-006"),
            analysis_ids=(analytical_baseline_id,),
            conditions=oracle.required_foundations,
        ),
        Assertion(
            assertion_id="AST-DAI-002",
            statement="Quotation workload is material and segmented, but the evidence does not establish that administration consumes half of seller capacity.",
            epistemic_status=EpistemicStatus.REASONED_SYNTHESIS,
            evidence_ids=("EXP-EVID-001",),
            analysis_ids=(analytical_baseline_id,),
        ),
        Assertion(
            assertion_id="AST-DAI-003",
            statement="Quotation elapsed time is not equivalent to automatable touch time.",
            epistemic_status=EpistemicStatus.ESTABLISHED_FACT,
            evidence_ids=("EXP-EVID-002",),
        ),
        Assertion(
            assertion_id="AST-DAI-004",
            statement="Customer-service evidence supports only an internal human-mediated assistant after knowledge and identity controls improve—not an autonomous external chatbot.",
            epistemic_status=EpistemicStatus.REASONED_SYNTHESIS,
            evidence_ids=("EXP-EVID-003",),
            analysis_ids=(analytical_baseline_id,),
        ),
        Assertion(
            assertion_id="AST-DAI-005",
            statement="Inventory forecasting is not production-ready without demand-label and substitution remediation and a controlled back-test.",
            epistemic_status=EpistemicStatus.REASONED_SYNTHESIS,
            evidence_ids=("EXP-EVID-004",),
            analysis_ids=(analytical_baseline_id,),
        ),
        Assertion(
            assertion_id="AST-DAI-006",
            statement="Unapproved public-AI use is a current control gap, while strong training interest supports managed adoption with verification and role safeguards.",
            epistemic_status=EpistemicStatus.REASONED_SYNTHESIS,
            evidence_ids=("EXP-EVID-005",),
            analysis_ids=(analytical_baseline_id,),
        ),
        Assertion(
            assertion_id="AST-DAI-007",
            statement="The pilot value case is capacity and potential incremental margin, not immediate cash savings.",
            epistemic_status=EpistemicStatus.REASONED_SYNTHESIS,
            evidence_ids=("EXP-EVID-006",),
            analysis_ids=(analytical_baseline_id,),
        ),
        Assertion(
            assertion_id="AST-DAI-008",
            statement="The current evidence supports zero immediate cash-releasing headcount benefit.",
            epistemic_status=EpistemicStatus.REASONED_SYNTHESIS,
            evidence_ids=("EXP-EVID-006",),
            analysis_ids=(analytical_baseline_id,),
        ),
        Assertion(
            assertion_id="AST-DAI-009",
            statement="The downside pilot cost remains within the approved SGD 120,000 ceiling, with only SGD 2,000 headroom.",
            epistemic_status=EpistemicStatus.REASONED_SYNTHESIS,
            evidence_ids=("EXP-EVID-006",),
            analysis_ids=(analytical_baseline_id,),
        ),
        Assertion(
            assertion_id="AST-DAI-010",
            statement="Human technical approval, pricing authority and external release must remain mandatory throughout the pilot.",
            epistemic_status=EpistemicStatus.RECOMMENDATION,
            evidence_ids=("EXP-EVID-001", "EXP-EVID-003"),
            analysis_ids=(analytical_baseline_id,),
        ),
        Assertion(
            assertion_id="AST-DAI-011",
            statement="Approved AI environment, identity, source versioning, logging, training and incident controls are required in parallel with the pilot.",
            epistemic_status=EpistemicStatus.RECOMMENDATION,
            evidence_ids=("EXP-EVID-003", "EXP-EVID-005"),
            analysis_ids=(analytical_baseline_id,),
        ),
        Assertion(
            assertion_id="AST-DAI-012",
            statement="Scale should occur only after outcome and control evidence passes; material leakage, unauthorised release or value failure must stop the pilot.",
            epistemic_status=EpistemicStatus.RECOMMENDATION,
            evidence_ids=("EXP-EVID-003", "EXP-EVID-005", "EXP-EVID-006"),
            analysis_ids=(analytical_baseline_id,),
            conditions=oracle.stop_conditions,
        ),
    )

    sections = (
        StorySection(
            section_id="SEC-DAI-001",
            title="Approve a bounded quotation-drafting pilot—not autonomous AI",
            purpose="State the governing decision, recommendation and commitment requested.",
            assertion_ids=("AST-DAI-001", "AST-DAI-009", "AST-DAI-010"),
            visual_specification_ids=("VIS-DAI-001",),
            required_number_ids=("NUM-DAI-010", "NUM-DAI-011", "NUM-DAI-012"),
            required_source_ids=("CLIENT-DATA-001", "CLIENT-DATA-005"),
        ),
        StorySection(
            section_id="SEC-DAI-002",
            title="Quotation work is material, but elapsed time is not automatable touch time",
            purpose="Correct the burden claim and identify the bounded drafting opportunity.",
            assertion_ids=("AST-DAI-002", "AST-DAI-003"),
            visual_specification_ids=("VIS-DAI-002",),
            required_number_ids=("NUM-DAI-001", "NUM-DAI-002", "NUM-DAI-003", "NUM-DAI-004"),
            required_source_ids=finding_by_id["EXP-EVID-001"].source_ids,
        ),
        StorySection(
            section_id="SEC-DAI-003",
            title="Customer service and inventory evidence do not support autonomous deployment",
            purpose="Define the options that must be deferred or constrained.",
            assertion_ids=("AST-DAI-004", "AST-DAI-005"),
            required_number_ids=("NUM-DAI-005", "NUM-DAI-006", "NUM-DAI-007"),
            required_source_ids=tuple(
                sorted(
                    set(finding_by_id["EXP-EVID-003"].source_ids)
                    | set(finding_by_id["EXP-EVID-004"].source_ids)
                )
            ),
        ),
        StorySection(
            section_id="SEC-DAI-004",
            title="Public-AI use creates a control gap while training interest supports managed adoption",
            purpose="Connect workforce evidence to implementation conditions.",
            assertion_ids=("AST-DAI-006",),
            required_number_ids=("NUM-DAI-008", "NUM-DAI-009"),
            required_source_ids=finding_by_id["EXP-EVID-005"].source_ids,
        ),
        StorySection(
            section_id="SEC-DAI-005",
            title="The pilot fits the ceiling, but value is capacity and potential margin—not cash savings",
            purpose="Present the reconciled value case, sensitivities and invalid management claim.",
            assertion_ids=("AST-DAI-007", "AST-DAI-008", "AST-DAI-009"),
            visual_specification_ids=("VIS-DAI-003",),
            required_number_ids=(
                "NUM-DAI-010",
                "NUM-DAI-011",
                "NUM-DAI-012",
                "NUM-DAI-013",
                "NUM-DAI-014",
                "NUM-DAI-015",
                "NUM-DAI-016",
                "NUM-DAI-017",
                "NUM-DAI-018",
            ),
            required_source_ids=finding_by_id["EXP-EVID-006"].source_ids,
        ),
        StorySection(
            section_id="SEC-DAI-006",
            title="Human authority and foundation controls must remain in the operating model",
            purpose="Define the control stack and non-delegable authority.",
            assertion_ids=("AST-DAI-010", "AST-DAI-011"),
            visual_specification_ids=("VIS-DAI-004",),
            required_source_ids=tuple(
                sorted(
                    set(finding_by_id["EXP-EVID-003"].source_ids)
                    | set(finding_by_id["EXP-EVID-005"].source_ids)
                )
            ),
        ),
        StorySection(
            section_id="SEC-DAI-007",
            title="Scale only after controlled evidence passes—and stop on material harm",
            purpose="Set the pilot roadmap, scale gate, stop conditions and Founder approvals.",
            assertion_ids=("AST-DAI-012",),
            visual_specification_ids=("VIS-DAI-005", "VIS-DAI-006"),
            required_source_ids=evidence_source_ids,
        ),
        StorySection(
            section_id="SEC-DAI-008",
            title="Appendix: sources, assumptions, methods and reconciliations",
            purpose="Preserve complete internal provenance without cluttering executive surfaces.",
            assertion_ids=("AST-DAI-001", "AST-DAI-007", "AST-DAI-012"),
            required_source_ids=evidence_source_ids,
        ),
    )

    story = StoryModel(
        story_model_id=STORY_MODEL_ID,
        version=DELIVERABLE_MODEL_VERSION,
        engagement_id=oracle.fixture_id,
        decision_id=DECISION_ID,
        audience_roles=("Northstar CEO", "Northstar CFO", "Northstar COO"),
        communication_objective=(
            "Enable the Founder and Northstar leadership to decide whether to approve one bounded AI "
            "pilot, its cash ceiling, operating controls and evidence required before scale."
        ),
        governing_thought=(
            "Approve a bounded quotation-drafting pilot with a non-AI comparator and retained human "
            "authority; do not recognise immediate cash savings or scale before evidence and controls pass."
        ),
        assertions=assertions,
        sections=sections,
        key_number_ids=tuple(item.number_id for item in numbers),
        recommendation_ids=(oracle.primary_pilot_use_case_id, oracle.required_comparator_use_case_id),
        roadmap_action_ids=(
            "ACT-DAI-FOUNDATIONS",
            "ACT-DAI-PILOT",
            "ACT-DAI-EVALUATE",
            "ACT-DAI-SCALE-OR-STOP",
        ),
        source_ids=evidence_source_ids,
    )

    visuals = (
        VisualSpecification(
            visual_specification_id="VIS-DAI-001",
            archetype=VisualArchetype.PORTFOLIO_MATRIX,
            message="UC-001 is the bounded first pilot; UC-008 remains the comparator while autonomous chatbot and inventory forecasting are deferred.",
            entities=(
                VisualEntity(entity_id="UC-001", label="Quotation drafting", category="pilot"),
                VisualEntity(entity_id="UC-008", label="Non-AI process comparator", category="comparator"),
                VisualEntity(entity_id="UC-003", label="Autonomous chatbot", category="defer"),
                VisualEntity(entity_id="UC-004", label="Inventory forecasting", category="defer"),
                VisualEntity(entity_id="UC-005", label="Bounded secondary option", category="secondary"),
            ),
            layout_rules=("two_axis_decision_matrix", "show_disposition_labels", "highlight_primary_and_comparator"),
            editable_output_required=True,
            accessibility_rules=("direct_labels", "text_alternative", "do_not_rely_on_colour"),
            allowed_surfaces=_DECISION_SURFACES,
        ),
        VisualSpecification(
            visual_specification_id="VIS-DAI-002",
            archetype=VisualArchetype.PROCESS_FLOW,
            message="Drafting can be bounded, while technical judgement, pricing and external release remain human-controlled.",
            entities=(
                VisualEntity(entity_id="ENQUIRY", label="Customer enquiry"),
                VisualEntity(entity_id="DRAFT", label="Structured draft"),
                VisualEntity(entity_id="TECH", label="Technical approval"),
                VisualEntity(entity_id="PRICE", label="Pricing approval"),
                VisualEntity(entity_id="RELEASE", label="Human external release"),
            ),
            relationships=(
                VisualRelationship(source_entity_id="ENQUIRY", target_entity_id="DRAFT", relationship="supports"),
                VisualRelationship(source_entity_id="DRAFT", target_entity_id="TECH", relationship="requires"),
                VisualRelationship(source_entity_id="TECH", target_entity_id="PRICE", relationship="precedes"),
                VisualRelationship(source_entity_id="PRICE", target_entity_id="RELEASE", relationship="precedes"),
            ),
            layout_rules=("left_to_right", "human_gates_visually_distinct", "show_waiting_separately_from_touch"),
            editable_output_required=True,
            accessibility_rules=("numbered_steps", "text_alternative", "minimum_contrast"),
            allowed_surfaces=_ALL_VISUAL_SURFACES,
        ),
        VisualSpecification(
            visual_specification_id="VIS-DAI-003",
            archetype=VisualArchetype.VALUE_DRIVER_TREE,
            message="The value case separates cash cost, released capacity, potential margin and zero immediate headcount cash benefit.",
            entities=(
                VisualEntity(entity_id="PILOT_COST", label="Pilot cash cost", data_reference="NUM-DAI-010"),
                VisualEntity(entity_id="SUPPORT_COST", label="Recurring support cost", data_reference="NUM-DAI-015"),
                VisualEntity(entity_id="CAPACITY", label="Addressable capacity value", data_reference="NUM-DAI-013"),
                VisualEntity(entity_id="MARGIN", label="Potential incremental margin", data_reference="NUM-DAI-014"),
                VisualEntity(entity_id="CASH_BENEFIT", label="Immediate headcount cash benefit", data_reference="NUM-DAI-016"),
            ),
            relationships=(
                VisualRelationship(source_entity_id="PILOT_COST", target_entity_id="CAPACITY", relationship="investment_enables"),
                VisualRelationship(source_entity_id="SUPPORT_COST", target_entity_id="MARGIN", relationship="reduces_net_value"),
                VisualRelationship(source_entity_id="CAPACITY", target_entity_id="MARGIN", relationship="may_convert_to"),
            ),
            layout_rules=("driver_tree", "separate_cash_from_capacity", "show_uncertainty_on_margin"),
            editable_output_required=True,
            accessibility_rules=("direct_value_labels", "text_alternative", "currency_units_explicit"),
            allowed_surfaces=_ALL_VISUAL_SURFACES,
        ),
        VisualSpecification(
            visual_specification_id="VIS-DAI-004",
            archetype=VisualArchetype.LAYERED_STACK,
            message="The pilot requires approved sources, identity, logging, human review and an effective kill switch.",
            entities=(
                VisualEntity(entity_id="SOURCES", label="Approved sources and version control"),
                VisualEntity(entity_id="IDENTITY", label="Identity and role-based access"),
                VisualEntity(entity_id="LOGGING", label="Logging and audit"),
                VisualEntity(entity_id="HUMAN", label="Human technical, pricing and release authority"),
                VisualEntity(entity_id="KILL", label="Incident response and kill switch"),
            ),
            relationships=(
                VisualRelationship(source_entity_id="SOURCES", target_entity_id="IDENTITY", relationship="foundation_for"),
                VisualRelationship(source_entity_id="IDENTITY", target_entity_id="LOGGING", relationship="controlled_by"),
                VisualRelationship(source_entity_id="LOGGING", target_entity_id="HUMAN", relationship="supports_accountability"),
                VisualRelationship(source_entity_id="HUMAN", target_entity_id="KILL", relationship="can_trigger"),
            ),
            layout_rules=("bottom_to_top_stack", "human_authority_prominent", "kill_switch_boundary"),
            editable_output_required=True,
            accessibility_rules=("ordered_layers", "text_alternative", "do_not_rely_on_colour"),
            allowed_surfaces=_DECISION_SURFACES,
        ),
        VisualSpecification(
            visual_specification_id="VIS-DAI-005",
            archetype=VisualArchetype.ROADMAP,
            message="Build foundations, run a bounded pilot with comparator, evaluate evidence, then scale or stop.",
            entities=(
                VisualEntity(entity_id="FOUNDATIONS", label="Build foundations"),
                VisualEntity(entity_id="PILOT", label="Run bounded pilot and comparator"),
                VisualEntity(entity_id="EVALUATE", label="Evaluate outcomes and controls"),
                VisualEntity(entity_id="DECIDE", label="Scale, recycle or stop"),
            ),
            relationships=(
                VisualRelationship(source_entity_id="FOUNDATIONS", target_entity_id="PILOT", relationship="precedes"),
                VisualRelationship(source_entity_id="PILOT", target_entity_id="EVALUATE", relationship="produces_evidence_for"),
                VisualRelationship(source_entity_id="EVALUATE", target_entity_id="DECIDE", relationship="gates"),
            ),
            layout_rules=("stage_gate", "show_founder_gate", "show_stop_path"),
            editable_output_required=True,
            accessibility_rules=("numbered_stages", "text_alternative", "milestones_have_dates_or_gates"),
            allowed_surfaces=_DECISION_SURFACES,
        ),
        VisualSpecification(
            visual_specification_id="VIS-DAI-006",
            archetype=VisualArchetype.CAUSAL_NARRATIVE,
            message="Pilot activity is not benefit: adoption and operating outcomes must precede verified value and scale.",
            entities=(
                VisualEntity(entity_id="DELIVERY", label="Pilot delivered"),
                VisualEntity(entity_id="ADOPTION", label="Users adopt and verify"),
                VisualEntity(entity_id="OUTCOME", label="Touch, rework and response outcomes improve"),
                VisualEntity(entity_id="VALUE", label="Capacity or margin is evidenced"),
                VisualEntity(entity_id="SCALE", label="Scale decision"),
            ),
            relationships=(
                VisualRelationship(source_entity_id="DELIVERY", target_entity_id="ADOPTION", relationship="does_not_guarantee"),
                VisualRelationship(source_entity_id="ADOPTION", target_entity_id="OUTCOME", relationship="enables"),
                VisualRelationship(source_entity_id="OUTCOME", target_entity_id="VALUE", relationship="may_create"),
                VisualRelationship(source_entity_id="VALUE", target_entity_id="SCALE", relationship="informs"),
            ),
            layout_rules=("left_to_right_causal_chain", "show_leakage_between_stages", "show_stop_conditions"),
            editable_output_required=True,
            accessibility_rules=("relationship_labels", "text_alternative", "uncertainty_explicit"),
            allowed_surfaces=_DECISION_SURFACES,
        ),
    )

    semantic_objects = (
        SemanticObject(
            semantic_object_id="SEM-DAI-001",
            kind=SemanticObjectKind.COVER,
            title="Northstar AI pilot decision",
            decision_purpose="Identify the decision, audience, status and confidentiality of the deliverable.",
        ),
        SemanticObject(
            semantic_object_id="SEM-DAI-002",
            kind=SemanticObjectKind.EXECUTIVE_DECISION,
            title="Approve a bounded quotation-drafting pilot—not autonomous AI",
            decision_purpose="Enable the executive decision and commitment request.",
            assertion_ids=("AST-DAI-001", "AST-DAI-009", "AST-DAI-010"),
            number_ids=("NUM-DAI-010", "NUM-DAI-011", "NUM-DAI-012"),
            citation_ids=("CITE-DAI-001", "CITE-DAI-006"),
            recommendation_ids=(oracle.primary_pilot_use_case_id, oracle.required_comparator_use_case_id),
        ),
        SemanticObject(
            semantic_object_id="SEM-DAI-003",
            kind=SemanticObjectKind.ANALYSIS,
            title="Quotation work is material, but elapsed time is not automatable touch time",
            decision_purpose="Establish the bounded process opportunity without overstating burden or automation potential.",
            assertion_ids=("AST-DAI-002", "AST-DAI-003"),
            number_ids=("NUM-DAI-001", "NUM-DAI-002", "NUM-DAI-003", "NUM-DAI-004"),
            citation_ids=("CITE-DAI-001", "CITE-DAI-002"),
            visual_specification_ids=("VIS-DAI-002",),
            uncertainty_ids=("UNC-DAI-001", "UNC-DAI-002"),
        ),
        SemanticObject(
            semantic_object_id="SEM-DAI-004",
            kind=SemanticObjectKind.EVIDENCE,
            title="Customer service and inventory evidence do not support autonomous deployment",
            decision_purpose="Defer unsafe or unready options while preserving bounded alternatives.",
            assertion_ids=("AST-DAI-004", "AST-DAI-005"),
            number_ids=("NUM-DAI-005", "NUM-DAI-006", "NUM-DAI-007"),
            citation_ids=("CITE-DAI-003", "CITE-DAI-004"),
            uncertainty_ids=("UNC-DAI-003", "UNC-DAI-004"),
        ),
        SemanticObject(
            semantic_object_id="SEM-DAI-005",
            kind=SemanticObjectKind.EVIDENCE,
            title="Public-AI use creates a control gap while training interest supports managed adoption",
            decision_purpose="Define workforce conditions for safe adoption.",
            assertion_ids=("AST-DAI-006",),
            number_ids=("NUM-DAI-008", "NUM-DAI-009"),
            citation_ids=("CITE-DAI-005",),
            uncertainty_ids=("UNC-DAI-005",),
        ),
        SemanticObject(
            semantic_object_id="SEM-DAI-006",
            kind=SemanticObjectKind.OPTIONS,
            title="UC-001 is the first pilot and UC-008 remains the comparator",
            decision_purpose="Show the option dispositions and switching logic.",
            assertion_ids=("AST-DAI-001", "AST-DAI-004", "AST-DAI-005"),
            citation_ids=("CITE-DAI-001", "CITE-DAI-003", "CITE-DAI-004"),
            visual_specification_ids=("VIS-DAI-001",),
            recommendation_ids=(oracle.primary_pilot_use_case_id, oracle.required_comparator_use_case_id),
        ),
        SemanticObject(
            semantic_object_id="SEM-DAI-007",
            kind=SemanticObjectKind.VALUE_CASE,
            title="Value is capacity and potential margin—not immediate cash savings",
            decision_purpose="Reconcile cost, potential value, break-even conditions and invalid management claims.",
            assertion_ids=("AST-DAI-007", "AST-DAI-008", "AST-DAI-009"),
            number_ids=tuple(item.number_id for item in numbers if item.number_id >= "NUM-DAI-010"),
            citation_ids=("CITE-DAI-006",),
            visual_specification_ids=("VIS-DAI-003",),
            uncertainty_ids=("UNC-DAI-006",),
        ),
        SemanticObject(
            semantic_object_id="SEM-DAI-008",
            kind=SemanticObjectKind.CONTROL_MODEL,
            title="Human authority and foundation controls must remain",
            decision_purpose="Define the minimum operating and control model for the pilot.",
            assertion_ids=("AST-DAI-010", "AST-DAI-011"),
            citation_ids=("CITE-DAI-003", "CITE-DAI-005"),
            visual_specification_ids=("VIS-DAI-004",),
        ),
        SemanticObject(
            semantic_object_id="SEM-DAI-009",
            kind=SemanticObjectKind.ROADMAP,
            title="Scale only after evidence passes—and stop on material harm",
            decision_purpose="Specify the implementation sequence, scale gate and stop paths.",
            assertion_ids=("AST-DAI-012",),
            citation_ids=("CITE-DAI-003", "CITE-DAI-005", "CITE-DAI-006"),
            visual_specification_ids=("VIS-DAI-005", "VIS-DAI-006"),
            roadmap_action_ids=(
                "ACT-DAI-FOUNDATIONS",
                "ACT-DAI-PILOT",
                "ACT-DAI-EVALUATE",
                "ACT-DAI-SCALE-OR-STOP",
            ),
        ),
        SemanticObject(
            semantic_object_id="SEM-DAI-010",
            kind=SemanticObjectKind.APPROVAL,
            title="Founder approval is required for scope, commitment and residual risk",
            decision_purpose="Present the exact accountable-human decisions required before execution or release.",
            assertion_ids=("AST-DAI-001", "AST-DAI-009", "AST-DAI-010", "AST-DAI-012"),
            number_ids=("NUM-DAI-011", "NUM-DAI-012"),
            recommendation_ids=(oracle.primary_pilot_use_case_id,),
        ),
        SemanticObject(
            semantic_object_id="SEM-DAI-011",
            kind=SemanticObjectKind.APPENDIX,
            title="Sources, assumptions, methods and reconciliation",
            decision_purpose="Retain complete internal provenance and transparent limitations.",
            citation_ids=tuple(item.citation_id for item in citations),
            uncertainty_ids=tuple(f"UNC-DAI-{index:03d}" for index in range(1, 7)),
        ),
        SemanticObject(
            semantic_object_id="SEM-DAI-012",
            kind=SemanticObjectKind.WORKBOOK_CHECK,
            title="Value model checks reconcile every displayed material number",
            decision_purpose="Provide a deterministic calculation and reconciliation surface.",
            assertion_ids=("AST-DAI-007", "AST-DAI-008", "AST-DAI-009"),
            number_ids=tuple(item.number_id for item in numbers),
            citation_ids=("CITE-DAI-006",),
        ),
    )

    pptx_ids = tuple(item.semantic_object_id for item in semantic_objects if item.semantic_object_id != "SEM-DAI-012")
    docx_ids = pptx_ids
    pdf_ids = pptx_ids
    html_ids = pptx_ids
    xlsx_ids = ("SEM-DAI-001", "SEM-DAI-003", "SEM-DAI-007", "SEM-DAI-011", "SEM-DAI-012")
    svg_ids = ("SEM-DAI-003", "SEM-DAI-006", "SEM-DAI-007", "SEM-DAI-008", "SEM-DAI-009")

    surface_plans = (
        SurfacePlan(
            manifest=_manifest(
                DeliverableSurface.PPTX,
                "northstar-ai-audit-decision-deck-v1.0.0.pptx",
                "Executive decision deck for pilot approval.",
                story.audience_roles,
                pptx_ids,
                evidence_source_ids,
            ),
            objects=tuple(
                _surface_object(
                    DeliverableSurface.PPTX,
                    index,
                    semantic_id,
                    SurfaceObjectRole.COVER if index == 1 else (
                        SurfaceObjectRole.EXECUTIVE_SUMMARY if index == 2 else (
                            SurfaceObjectRole.APPENDIX if semantic_id == "SEM-DAI-011" else SurfaceObjectRole.CONTENT
                        )
                    ),
                    next(item.title for item in semantic_objects if item.semantic_object_id == semantic_id),
                    RenderForm.NATIVE_SHAPES,
                    editable_required=bool(
                        next(item.visual_specification_ids for item in semantic_objects if item.semantic_object_id == semantic_id)
                    ),
                )
                for index, semantic_id in enumerate(pptx_ids, start=1)
            ),
        ),
        SurfacePlan(
            manifest=_manifest(
                DeliverableSurface.DOCX,
                "northstar-ai-audit-decision-report-v1.0.0.docx",
                "Decision report with executive narrative, evidence and appendices.",
                story.audience_roles,
                docx_ids,
                evidence_source_ids,
            ),
            objects=tuple(
                _surface_object(
                    DeliverableSurface.DOCX,
                    index,
                    semantic_id,
                    SurfaceObjectRole.COVER if index == 1 else (
                        SurfaceObjectRole.APPENDIX if semantic_id == "SEM-DAI-011" else SurfaceObjectRole.CONTENT
                    ),
                    next(item.title for item in semantic_objects if item.semantic_object_id == semantic_id),
                    RenderForm.SVG if next(
                        item.visual_specification_ids for item in semantic_objects if item.semantic_object_id == semantic_id
                    ) else RenderForm.TEXT,
                    editable_required=bool(
                        next(item.visual_specification_ids for item in semantic_objects if item.semantic_object_id == semantic_id)
                    ),
                )
                for index, semantic_id in enumerate(docx_ids, start=1)
            ),
        ),
        SurfacePlan(
            manifest=_manifest(
                DeliverableSurface.XLSX,
                "northstar-ai-audit-value-model-v1.0.0.xlsx",
                "Reconciled value model, source register, calculations, outputs and checks.",
                ("Northstar CFO", "Northstar COO"),
                xlsx_ids,
                evidence_source_ids,
            ),
            objects=(
                _surface_object(DeliverableSurface.XLSX, 1, "SEM-DAI-001", SurfaceObjectRole.README, "Read-me and model purpose", RenderForm.TEXT),
                _surface_object(DeliverableSurface.XLSX, 2, "SEM-DAI-011", SurfaceObjectRole.SOURCE_DATA, "Source and provenance register", RenderForm.TABLE),
                _surface_object(DeliverableSurface.XLSX, 3, "SEM-DAI-003", SurfaceObjectRole.ASSUMPTIONS, "Quotation inputs and segment assumptions", RenderForm.CHART, editable_required=True),
                _surface_object(DeliverableSurface.XLSX, 4, "SEM-DAI-007", SurfaceObjectRole.CALCULATIONS, "Value calculations and sensitivities", RenderForm.FORMULA_SHEET),
                _surface_object(DeliverableSurface.XLSX, 5, "SEM-DAI-007", SurfaceObjectRole.OUTPUTS, "Approved value outputs", RenderForm.CHART, editable_required=True),
                _surface_object(DeliverableSurface.XLSX, 6, "SEM-DAI-012", SurfaceObjectRole.CHECKS, "Checks and cross-format reconciliation", RenderForm.FORMULA_SHEET),
            ),
        ),
        SurfacePlan(
            manifest=_manifest(
                DeliverableSurface.PDF,
                "northstar-ai-audit-decision-pack-v1.0.0.pdf",
                "Controlled distribution copy derived from the approved semantic story.",
                story.audience_roles,
                pdf_ids,
                evidence_source_ids,
            ),
            objects=tuple(
                _surface_object(
                    DeliverableSurface.PDF,
                    index,
                    semantic_id,
                    SurfaceObjectRole.COVER if index == 1 else (
                        SurfaceObjectRole.APPENDIX if semantic_id == "SEM-DAI-011" else SurfaceObjectRole.CONTENT
                    ),
                    next(item.title for item in semantic_objects if item.semantic_object_id == semantic_id),
                    RenderForm.SVG if next(
                        item.visual_specification_ids for item in semantic_objects if item.semantic_object_id == semantic_id
                    ) else RenderForm.TEXT,
                )
                for index, semantic_id in enumerate(pdf_ids, start=1)
            ),
        ),
        SurfacePlan(
            manifest=_manifest(
                DeliverableSurface.SVG,
                "northstar-ai-audit-visual-library-v1.0.0.svg",
                "Editable vector visual specifications for the decision pack.",
                story.audience_roles,
                svg_ids,
                evidence_source_ids,
            ),
            objects=tuple(
                _surface_object(
                    DeliverableSurface.SVG,
                    index,
                    semantic_id,
                    SurfaceObjectRole.CONTENT,
                    next(item.title for item in semantic_objects if item.semantic_object_id == semantic_id),
                    RenderForm.SVG,
                    editable_required=True,
                )
                for index, semantic_id in enumerate(svg_ids, start=1)
            ),
        ),
        SurfacePlan(
            manifest=_manifest(
                DeliverableSurface.HTML,
                "northstar-ai-audit-decision-brief-v1.0.0.html",
                "Responsive decision brief with on-demand provenance and progressive disclosure.",
                story.audience_roles,
                html_ids,
                evidence_source_ids,
            ),
            objects=tuple(
                _surface_object(
                    DeliverableSurface.HTML,
                    index,
                    semantic_id,
                    SurfaceObjectRole.COVER if index == 1 else (
                        SurfaceObjectRole.APPENDIX if semantic_id == "SEM-DAI-011" else SurfaceObjectRole.CONTENT
                    ),
                    next(item.title for item in semantic_objects if item.semantic_object_id == semantic_id),
                    RenderForm.WEB_COMPONENT,
                    editable_required=bool(
                        next(item.visual_specification_ids for item in semantic_objects if item.semantic_object_id == semantic_id)
                    ),
                )
                for index, semantic_id in enumerate(html_ids, start=1)
            ),
        ),
    )

    reconciliation = CrossFormatReconciliation(
        reconciliation_id="RECON-DAI-001",
        story_model_id=STORY_MODEL_ID,
        deliverable_ids=tuple(plan.manifest.file_id for plan in surface_plans),
        results=tuple(
            ReconciliationResult(
                check=check,
                passed=True,
                details={
                    ReconciliationCheck.HEADLINE: "All executive surfaces use the approved assertion-led section titles.",
                    ReconciliationCheck.ASSUMPTION: "Material assumptions and uncertainties are referenced from one semantic model.",
                    ReconciliationCheck.NUMBER: "All displayed material numbers resolve to approved named oracle fields.",
                    ReconciliationCheck.RECOMMENDATION: "UC-001, UC-008 and deferred options are consistent across surfaces.",
                    ReconciliationCheck.ROADMAP: "Foundation, pilot, evaluate and scale-or-stop actions share stable IDs.",
                    ReconciliationCheck.SOURCE: "All client notes resolve to the complete internal citation register.",
                    ReconciliationCheck.VERSION: "Every manifest references STORY-DAI-001 version 1.0.0.",
                    ReconciliationCheck.RENDERED_INSPECTION: "Semantic inspection passed; renderer and Office inspection remain a later execution gate.",
                }[check],
            )
            for check in ReconciliationCheck
        ),
        reviewer_id="Independent Quality Agent",
    )

    founder_review = FounderReviewSummary(
        decision=oracle.governing_decision,
        requested_action="Approve the bounded UC-001 pilot scope and a maximum initial cash commitment of SGD 120,000, subject to the stated controls and evidence gates.",
        recommendation="Approve UC-001 with UC-008 as the mandatory non-AI comparator; defer autonomous chatbot and production inventory forecasting.",
        material_assumptions=(
            "Released capacity can be redeployed to productive work.",
            "Any conversion uplift remains unvalidated until the controlled pilot produces evidence.",
        ),
        material_uncertainties=oracle.uncertainty_statements,
        open_defect_ids=(),
        reconciliation_status="passed",
        client_citation_approach="Use concise company-data and offdata-analysis notes on executive pages, fuller notes and appendices, and a complete source tab in the workbook.",
        exact_release_action="Approve the semantic model for renderer implementation; do not issue an external client artefact from this phase.",
        approval_required=True,
    )

    return DeliverableSemanticModel(
        semantic_model_id=DELIVERABLE_SEMANTIC_MODEL_ID,
        version=DELIVERABLE_MODEL_VERSION,
        fixture_id=oracle.fixture_id,
        analytical_baseline_id=analytical_baseline_id,
        analytical_baseline_version=oracle.oracle_version,
        analytical_input_digest=oracle.input_digest,
        agent_visible=False,
        story=story,
        numbers=numbers,
        citations=citations,
        visuals=visuals,
        semantic_objects=semantic_objects,
        surface_plans=surface_plans,
        reconciliation=reconciliation,
        founder_review=founder_review,
        prohibited_conclusions=oracle.prohibited_conclusions,
    )


def grade_ai_audit_deliverable_semantic_model(
    model: DeliverableSemanticModel,
    oracle: AIAuditOracleResult,
) -> SemanticModelGrade:
    """Independently grade the semantic model against the analytical oracle."""

    checks = _CheckCollector()
    checks.check(model.semantic_model_id == DELIVERABLE_SEMANTIC_MODEL_ID, "semantic_model_id")
    checks.check(model.version == DELIVERABLE_MODEL_VERSION, "semantic_model_version")
    checks.check(model.fixture_id == oracle.fixture_id, "fixture_id")
    checks.check(model.agent_visible is False, "semantic_model_must_be_restricted")
    checks.check(model.analytical_input_digest == oracle.input_digest, "analytical_input_digest")
    checks.check(model.story.story_model_id == STORY_MODEL_ID, "story_model_id")
    checks.check(model.story.decision_id == DECISION_ID, "decision_id")
    checks.check(model.story.engagement_id == oracle.fixture_id, "engagement_id")
    checks.check("bounded quotation-drafting pilot" in model.story.governing_thought, "governing_thought_primary_pilot")
    checks.check("non-AI comparator" in model.story.governing_thought, "governing_thought_comparator")
    checks.check("immediate cash savings" in model.story.governing_thought, "governing_thought_value_classification")

    surfaces = {plan.manifest.surface for plan in model.surface_plans}
    checks.check(surfaces == set(_REQUIRED_SURFACES), "required_surface_set")
    checks.check(len(model.surface_plans) == 6, "surface_plan_count")
    checks.check(len(model.story.sections) == 8, "story_section_count")
    checks.check(len(model.story.assertions) == 12, "assertion_count")
    checks.check(len(model.numbers) == 18, "number_count")
    checks.check(len(model.citations) == 6, "citation_count")
    checks.check(len(model.visuals) == 6, "visual_count")
    checks.check(len(model.semantic_objects) == 12, "semantic_object_count")

    expected_numbers = {
        "NUM-DAI-001": float(oracle.quotation.annualised_volume),
        "NUM-DAI-002": oracle.quotation.annualised_touch_hours,
        "NUM-DAI-003": oracle.quotation.simple_and_standard_volume_share_percent,
        "NUM-DAI-004": oracle.quotation.complex_and_engineered_touch_share_percent,
        "NUM-DAI-005": float(oracle.customer_service.annual_ticket_count),
        "NUM-DAI-006": oracle.customer_service.autonomous_ready_share_percent,
        "NUM-DAI-007": oracle.customer_service.weighted_approved_knowledge_coverage_percent,
        "NUM-DAI-008": oracle.workforce.weighted_public_ai_use_percent,
        "NUM-DAI-009": oracle.workforce.weighted_training_interest_percent,
        "NUM-DAI-010": oracle.financial.base_pilot_cost_sgd,
        "NUM-DAI-011": oracle.financial.downside_pilot_cost_sgd,
        "NUM-DAI-012": oracle.maximum_initial_cash_commitment_sgd,
        "NUM-DAI-013": oracle.financial.annual_addressable_capacity_value_sgd,
        "NUM-DAI-014": oracle.financial.annual_potential_incremental_gross_margin_sgd,
        "NUM-DAI-015": oracle.financial.annual_platform_and_support_cost_sgd,
        "NUM-DAI-016": oracle.financial.immediate_cash_releasing_headcount_benefit_sgd,
        "NUM-DAI-017": oracle.financial.recurring_support_break_even_capacity_redeployment_percent,
        "NUM-DAI-018": oracle.financial.year_one_pilot_and_support_break_even_conversion_uplift_points,
    }
    actual_numbers = {item.number_id: item for item in model.numbers}
    checks.check(set(actual_numbers) == set(expected_numbers), "number_ids")
    for number_id, value in expected_numbers.items():
        number = actual_numbers.get(number_id)
        checks.check(number is not None, f"{number_id}:present")
        if number is not None:
            checks.check(number.value == value, f"{number_id}:value")
            checks.check(number.approved, f"{number_id}:approved")
            checks.check(number.source_record_id == model.analytical_baseline_id, f"{number_id}:source")

    assertion_text = " ".join(item.statement for item in model.story.assertions)
    checks.check(oracle.primary_pilot_use_case_id in model.story.recommendation_ids, "primary_pilot")
    checks.check(oracle.required_comparator_use_case_id in model.story.recommendation_ids, "non_ai_comparator")
    checks.check("autonomous external chatbot" in assertion_text, "chatbot_deferral")
    checks.check("Inventory forecasting is not production-ready" in assertion_text, "inventory_deferral")
    checks.check("Human technical approval, pricing authority and external release" in assertion_text, "human_authority")
    checks.check("zero immediate cash-releasing headcount benefit" in assertion_text, "zero_cash_headcount_benefit")

    expected_source_ids = {source_id for item in oracle.evidence_findings for source_id in item.source_ids}
    actual_source_ids = {source_id for citation in model.citations for source_id in citation.source_ids}
    checks.check(actual_source_ids == expected_source_ids, "citation_source_scope")
    checks.check(all(citation.client_note for citation in model.citations), "client_notes")
    checks.check(all(citation.internal_provenance for citation in model.citations), "internal_provenance")
    checks.check(
        all(CitationPresentation.APPENDIX in citation.presentation_modes for citation in model.citations),
        "appendix_citation_mode",
    )
    checks.check(
        all(CitationPresentation.SOURCE_TAB in citation.presentation_modes for citation in model.citations),
        "workbook_source_tab_mode",
    )

    required_visuals = {
        VisualArchetype.PORTFOLIO_MATRIX,
        VisualArchetype.PROCESS_FLOW,
        VisualArchetype.VALUE_DRIVER_TREE,
        VisualArchetype.LAYERED_STACK,
        VisualArchetype.ROADMAP,
        VisualArchetype.CAUSAL_NARRATIVE,
    }
    checks.check({item.archetype for item in model.visuals} == required_visuals, "visual_archetypes")
    checks.check(all(item.editable_output_required for item in model.visuals), "visual_editability")
    checks.check(
        all(
            surface_object.render_form is not RenderForm.TEXT
            for plan in model.surface_plans
            for surface_object in plan.objects
            if next(
                item
                for item in model.semantic_objects
                if item.semantic_object_id == surface_object.semantic_object_id
            ).visual_specification_ids
        ),
        "labelled_visual_not_text_only",
    )

    checks.check(model.reconciliation.passed, "cross_format_reconciliation")
    checks.check(
        all(
            plan.manifest.baseline_story_model_id == STORY_MODEL_ID
            and plan.manifest.baseline_story_model_version == DELIVERABLE_MODEL_VERSION
            for plan in model.surface_plans
        ),
        "immutable_story_baseline",
    )
    checks.check(
        all(plan.manifest.confidentiality_marking for plan in model.surface_plans),
        "confidentiality_marking",
    )
    checks.check(
        all(plan.manifest.approval_status is ArtefactApprovalStatus.APPROVED for plan in model.surface_plans),
        "approval_state",
    )
    checks.check(model.founder_review.approval_required, "founder_approval_required")
    checks.check("do not issue" in model.founder_review.exact_release_action.casefold(), "no_external_issue")
    checks.check(
        set(model.founder_review.material_uncertainties) == set(oracle.uncertainty_statements),
        "uncertainty_scope",
    )
    checks.check(
        all(conclusion not in assertion_text for conclusion in oracle.prohibited_conclusions),
        "prohibited_conclusions_absent",
    )
    checks.check(
        all(
            name not in generated
            for plan in model.surface_plans
            for generated in plan.manifest.generated_from
            for name in (ANSWER_KEY_NAME, ORACLE_BASELINE_NAME, DELIVERABLE_SEMANTIC_BASELINE_NAME)
        ),
        "restricted_files_not_generation_sources",
    )

    failures = tuple(checks.failures)
    return SemanticModelGrade(
        passed=not failures,
        checks_run=checks.count,
        checks_passed=checks.count - len(failures),
        failures=failures,
    )


def deliverable_semantic_baseline_document(fixture_dir: Path) -> dict[str, Any]:
    oracle = build_ai_audit_oracle(fixture_dir)
    model = build_ai_audit_deliverable_semantic_model(oracle)
    grade = grade_ai_audit_deliverable_semantic_model(model, oracle)
    if not grade.passed:
        raise ValueError(f"Deliverable semantic model failed independent grade: {grade.failures}")
    return {
        "classification": "restricted_evaluation_semantic_model",
        "agent_visible": False,
        "analytical_input_digest": oracle.input_digest,
        "semantic_model_digest": semantic_model_digest(model),
        "semantic_model": model.model_dump(mode="json"),
        "grade": grade.model_dump(mode="json"),
    }


def serialise_deliverable_semantic_baseline(document: Mapping[str, Any]) -> str:
    return json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_deliverable_semantic_baseline(fixture_dir: Path) -> Path:
    destination = fixture_dir / DELIVERABLE_SEMANTIC_BASELINE_NAME
    destination.write_text(
        serialise_deliverable_semantic_baseline(
            deliverable_semantic_baseline_document(fixture_dir)
        ),
        encoding="utf-8",
    )
    return destination


def verify_committed_deliverable_semantic_baseline(fixture_dir: Path) -> None:
    destination = fixture_dir / DELIVERABLE_SEMANTIC_BASELINE_NAME
    if not destination.is_file():
        raise ValueError(
            f"Missing committed deliverable semantic baseline: {DELIVERABLE_SEMANTIC_BASELINE_NAME}"
        )
    expected = serialise_deliverable_semantic_baseline(
        deliverable_semantic_baseline_document(fixture_dir)
    )
    actual = destination.read_text(encoding="utf-8")
    if actual != expected:
        raise ValueError("Committed deliverable semantic baseline is stale or non-reproducible.")


def ensure_deliverable_semantic_baseline_isolation(
    *,
    context_paths: Iterable[str],
    restricted_paths: Iterable[str] = (
        ANSWER_KEY_NAME,
        ORACLE_BASELINE_NAME,
        DELIVERABLE_SEMANTIC_BASELINE_NAME,
    ),
) -> None:
    restricted = {Path(path).name for path in restricted_paths}
    leaked = sorted(path for path in context_paths if Path(path).name in restricted)
    if leaked:
        raise ValueError(f"Restricted evaluation material in agent context: {leaked}")
