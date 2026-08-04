from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from pydantic import ValidationError

from offdata_core.ai_audit_deliverable import (
    DELIVERABLE_SEMANTIC_BASELINE_NAME,
    build_ai_audit_deliverable_semantic_model,
    deliverable_semantic_baseline_document,
    ensure_deliverable_semantic_baseline_isolation,
    grade_ai_audit_deliverable_semantic_model,
    serialise_deliverable_semantic_baseline,
    verify_committed_deliverable_semantic_baseline,
    write_deliverable_semantic_baseline,
)
from offdata_core.ai_audit_oracle import (
    ANSWER_KEY_NAME,
    ORACLE_BASELINE_NAME,
    build_ai_audit_oracle,
)
from offdata_core.deliverable_semantic import (
    CitationPresentation,
    DeliverableSemanticModel,
    RenderForm,
    SemanticObjectKind,
    SurfaceObjectRole,
    semantic_model_digest,
)
from offdata_core.delivery import DeliverableSurface, VisualArchetype


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "fixtures" / "digital-ai" / "FIXTURE-DAI-001"


def _copy_fixture(tmp_path: Path) -> Path:
    destination = tmp_path / "FIXTURE-DAI-001"
    shutil.copytree(FIXTURE_DIR, destination)
    return destination


def _model() -> DeliverableSemanticModel:
    oracle = build_ai_audit_oracle(FIXTURE_DIR)
    return build_ai_audit_deliverable_semantic_model(oracle)


def test_semantic_model_builds_from_oracle_and_independent_grade_passes() -> None:
    # Requirements: DELIV-001, OUT-002, QA-009
    oracle = build_ai_audit_oracle(FIXTURE_DIR)
    model = build_ai_audit_deliverable_semantic_model(oracle)
    grade = grade_ai_audit_deliverable_semantic_model(model, oracle)
    assert model.fixture_id == "FIXTURE-DAI-001"
    assert model.agent_visible is False
    assert grade.passed
    assert grade.checks_passed == grade.checks_run
    assert not grade.failures


def test_semantic_baseline_is_byte_reproducible_and_committed_baseline_is_current() -> None:
    # Requirements: DATA-003, DATA-008, DELIV-001
    first = serialise_deliverable_semantic_baseline(
        deliverable_semantic_baseline_document(FIXTURE_DIR)
    )
    second = serialise_deliverable_semantic_baseline(
        deliverable_semantic_baseline_document(FIXTURE_DIR)
    )
    assert first == second
    verify_committed_deliverable_semantic_baseline(FIXTURE_DIR)


def test_semantic_baseline_writer_and_stale_detection(tmp_path: Path) -> None:
    # Requirements: DATA-003, QA-005, TEST-005
    fixture = _copy_fixture(tmp_path)
    destination = write_deliverable_semantic_baseline(fixture)
    assert destination.name == DELIVERABLE_SEMANTIC_BASELINE_NAME
    verify_committed_deliverable_semantic_baseline(fixture)
    destination.write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="stale or non-reproducible"):
        verify_committed_deliverable_semantic_baseline(fixture)


def test_all_required_surfaces_share_one_story_and_version() -> None:
    # Requirements: DELIV-001, DELIV-003, DATA-008
    model = _model()
    assert {plan.manifest.surface for plan in model.surface_plans} == {
        DeliverableSurface.PPTX,
        DeliverableSurface.DOCX,
        DeliverableSurface.XLSX,
        DeliverableSurface.PDF,
        DeliverableSurface.SVG,
        DeliverableSurface.HTML,
    }
    assert all(
        plan.manifest.baseline_story_model_id == model.story.story_model_id
        and plan.manifest.baseline_story_model_version == model.story.version
        for plan in model.surface_plans
    )
    assert model.reconciliation.passed


def test_story_is_assertion_led_and_decision_first() -> None:
    # Requirements: DELIV-002, QA-001, OUT-002
    model = _model()
    titles = tuple(section.title for section in model.story.sections)
    assert titles[0] == "Approve a bounded quotation-drafting pilot—not autonomous AI"
    assert all(title not in {"Overview", "Analysis", "Recommendation", "Roadmap"} for title in titles)
    assert "approve one bounded AI pilot" in model.story.communication_objective
    assert "non-AI comparator" in model.story.governing_thought
    assert model.founder_review.decision


def test_material_numbers_reconcile_to_named_approved_oracle_outputs() -> None:
    # Requirements: DELIV-003, DELIV-008, MODEL-005, MODEL-008
    oracle = build_ai_audit_oracle(FIXTURE_DIR)
    model = build_ai_audit_deliverable_semantic_model(oracle)
    by_id = {item.number_id: item for item in model.numbers}
    assert len(by_id) == 18
    assert by_id["NUM-DAI-001"].value == oracle.quotation.annualised_volume
    assert by_id["NUM-DAI-011"].value == oracle.financial.downside_pilot_cost_sgd
    assert by_id["NUM-DAI-012"].value == oracle.maximum_initial_cash_commitment_sgd
    assert by_id["NUM-DAI-016"].value == 0
    assert all(item.approved for item in model.numbers)
    assert all(item.source_record_id == model.analytical_baseline_id for item in model.numbers)
    assert all(item.source_field for item in model.numbers)


def test_number_mutation_is_detected_by_independent_semantic_grade() -> None:
    # Requirements: DELIV-008, QA-003, QA-005, TEST-005
    oracle = build_ai_audit_oracle(FIXTURE_DIR)
    model = build_ai_audit_deliverable_semantic_model(oracle)
    changed = model.numbers[10].model_copy(update={"value": 125000.0})
    mutated = model.model_copy(
        update={"numbers": model.numbers[:10] + (changed,) + model.numbers[11:]}
    )
    grade = grade_ai_audit_deliverable_semantic_model(mutated, oracle)
    assert grade.passed is False
    assert "NUM-DAI-011:value" in grade.failures


def test_recommendation_comparator_deferrals_and_human_authority_are_preserved() -> None:
    # Requirements: OUT-002, DELIV-003, AUTH-003, AUTH-004
    model = _model()
    text = " ".join(item.statement for item in model.story.assertions)
    assert "UC-001" in model.story.recommendation_ids
    assert "UC-008" in model.story.recommendation_ids
    assert "autonomous external chatbot" in text
    assert "Inventory forecasting is not production-ready" in text
    assert "Human technical approval, pricing authority and external release" in text
    assert "zero immediate cash-releasing headcount benefit" in text


def test_client_citations_are_proportionate_but_internal_provenance_is_complete() -> None:
    # Requirements: EVID-003, EVID-009, DELIV-009
    oracle = build_ai_audit_oracle(FIXTURE_DIR)
    model = build_ai_audit_deliverable_semantic_model(oracle)
    expected_sources = {
        source_id for finding in oracle.evidence_findings for source_id in finding.source_ids
    }
    actual_sources = {
        source_id for citation in model.citations for source_id in citation.source_ids
    }
    assert actual_sources == expected_sources
    assert all(citation.client_note for citation in model.citations)
    assert all(citation.internal_provenance for citation in model.citations)
    assert all(
        CitationPresentation.APPENDIX in citation.presentation_modes
        and CitationPresentation.SOURCE_TAB in citation.presentation_modes
        for citation in model.citations
    )


def test_visual_grammar_is_editable_and_not_raster_only() -> None:
    # Requirements: DELIV-004, DELIV-005, DELIV-006
    model = _model()
    assert {item.archetype for item in model.visuals} == {
        VisualArchetype.PORTFOLIO_MATRIX,
        VisualArchetype.PROCESS_FLOW,
        VisualArchetype.VALUE_DRIVER_TREE,
        VisualArchetype.LAYERED_STACK,
        VisualArchetype.ROADMAP,
        VisualArchetype.CAUSAL_NARRATIVE,
    }
    assert all(item.editable_output_required for item in model.visuals)
    render_forms = {
        surface_object.render_form
        for plan in model.surface_plans
        for surface_object in plan.objects
        if next(
            item
            for item in model.semantic_objects
            if item.semantic_object_id == surface_object.semantic_object_id
        ).visual_specification_ids
    }
    assert RenderForm.NATIVE_SHAPES in render_forms
    assert RenderForm.SVG in render_forms
    assert RenderForm.WEB_COMPONENT in render_forms
    assert RenderForm.CHART in render_forms


def test_surface_plans_match_manifest_scope_and_semantic_objects() -> None:
    # Requirements: DELIV-001, DELIV-003, DELIV-010
    model = _model()
    semantic_ids = {item.semantic_object_id for item in model.semantic_objects}
    mapped: set[str] = set()
    for plan in model.surface_plans:
        object_ids = {item.semantic_object_id for item in plan.objects}
        assert object_ids == set(plan.manifest.included_object_ids)
        assert object_ids <= semantic_ids
        assert plan.manifest.version == model.version
        assert plan.manifest.confidentiality_marking
        mapped.update(object_ids)
    assert mapped == semantic_ids


def test_workbook_semantics_separate_sources_calculations_outputs_and_checks() -> None:
    # Requirements: MODEL-007, MODEL-008, DELIV-003
    model = _model()
    workbook = next(
        plan for plan in model.surface_plans if plan.manifest.surface is DeliverableSurface.XLSX
    )
    roles = {item.role for item in workbook.objects}
    assert roles == {
        SurfaceObjectRole.README,
        SurfaceObjectRole.SOURCE_DATA,
        SurfaceObjectRole.ASSUMPTIONS,
        SurfaceObjectRole.CALCULATIONS,
        SurfaceObjectRole.OUTPUTS,
        SurfaceObjectRole.CHECKS,
    }
    assert any(item.render_form is RenderForm.FORMULA_SHEET for item in workbook.objects)
    assert any(item.semantic_object_id == "SEM-DAI-012" for item in workbook.objects)


def test_founder_review_packet_requests_approval_but_blocks_external_issue() -> None:
    # Requirements: AUTH-003, AUTH-004, AUTH-009, DELIV-010
    review = _model().founder_review
    assert review.approval_required is True
    assert review.reconciliation_status == "passed"
    assert "SGD 120,000" in review.requested_action
    assert "do not issue" in review.exact_release_action.casefold()
    assert not review.open_defect_ids


def test_semantic_baseline_and_oracles_are_blocked_from_normal_agent_context() -> None:
    # Requirements: AGENT-002, AGENT-004, QA-009, SEC-002
    ensure_deliverable_semantic_baseline_isolation(
        context_paths=("company-and-mandate.yaml", "quotation-activity.csv")
    )
    for restricted in (
        ANSWER_KEY_NAME,
        ORACLE_BASELINE_NAME,
        DELIVERABLE_SEMANTIC_BASELINE_NAME,
    ):
        with pytest.raises(ValueError, match="Restricted evaluation material"):
            ensure_deliverable_semantic_baseline_isolation(context_paths=(restricted,))


def test_semantic_contract_rejects_unknown_number_reference() -> None:
    # Requirements: DELIV-008, QA-004
    payload = _model().model_dump(mode="json")
    semantic_objects = payload["semantic_objects"]
    assert isinstance(semantic_objects, list)
    first_decision_object = semantic_objects[1]
    assert isinstance(first_decision_object, dict)
    first_decision_object["number_ids"].append("NUM-DAI-999")
    with pytest.raises(ValidationError, match="unknown number IDs"):
        DeliverableSemanticModel(**payload)


def test_semantic_contract_rejects_story_version_drift() -> None:
    # Requirements: DATA-008, DELIV-003
    payload = _model().model_dump(mode="json")
    surface_plans = payload["surface_plans"]
    assert isinstance(surface_plans, list)
    first_plan = surface_plans[0]
    assert isinstance(first_plan, dict)
    manifest = first_plan["manifest"]
    assert isinstance(manifest, dict)
    manifest["baseline_story_model_version"] = "9.9.9"
    with pytest.raises(ValidationError, match="another story-model version"):
        DeliverableSemanticModel(**payload)


def test_semantic_contract_rejects_missing_required_surface() -> None:
    # Requirements: DELIV-001, DELIV-003, QA-004
    payload = _model().model_dump(mode="json")
    surface_plans = payload["surface_plans"]
    assert isinstance(surface_plans, list)
    payload["surface_plans"] = surface_plans[:-1]
    reconciliation = payload["reconciliation"]
    assert isinstance(reconciliation, dict)
    reconciliation["deliverable_ids"] = reconciliation["deliverable_ids"][:-1]
    with pytest.raises(ValidationError, match="surface set mismatch"):
        DeliverableSemanticModel(**payload)


def test_semantic_digest_changes_when_decision_content_changes() -> None:
    # Requirements: DATA-003, DATA-008, TEST-005
    model = _model()
    original = semantic_model_digest(model)
    changed_review = model.founder_review.model_copy(
        update={"recommendation": model.founder_review.recommendation + " Revised."}
    )
    mutated = model.model_copy(update={"founder_review": changed_review})
    assert semantic_model_digest(mutated) != original


def test_prohibited_conclusions_are_absent_from_semantic_story() -> None:
    # Requirements: QA-001, QA-009, DELIV-002
    model = _model()
    narrative = " ".join(
        [model.story.governing_thought]
        + [item.statement for item in model.story.assertions]
        + [item.title for item in model.semantic_objects]
    )
    assert all(conclusion not in narrative for conclusion in model.prohibited_conclusions)


def test_fixture_mutation_invalidates_committed_semantic_baseline(tmp_path: Path) -> None:
    # Requirements: DATA-008, MODEL-002, QA-005, TEST-005
    fixture = _copy_fixture(tmp_path)
    financial_path = fixture / "financial-baseline.csv"
    text = financial_path.read_text(encoding="utf-8")
    financial_path.write_text(text.replace("88000", "89000", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="stale or non-reproducible"):
        verify_committed_deliverable_semantic_baseline(fixture)


def test_semantic_model_contains_decision_value_control_roadmap_and_appendix_objects() -> None:
    # Requirements: DELIV-001, OUT-003, IMPL-001
    kinds = {item.kind for item in _model().semantic_objects}
    assert {
        SemanticObjectKind.EXECUTIVE_DECISION,
        SemanticObjectKind.VALUE_CASE,
        SemanticObjectKind.CONTROL_MODEL,
        SemanticObjectKind.ROADMAP,
        SemanticObjectKind.APPENDIX,
        SemanticObjectKind.WORKBOOK_CHECK,
    } <= kinds
