#!/usr/bin/env python3
"""Validate the complete chat-first Phase 4 deliverable semantic model."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from offdata_core.ai_audit_deliverable import (
    DELIVERABLE_SEMANTIC_BASELINE_NAME,
    build_ai_audit_deliverable_semantic_model,
    ensure_deliverable_semantic_baseline_isolation,
    grade_ai_audit_deliverable_semantic_model,
    verify_committed_deliverable_semantic_baseline,
)
from offdata_core.ai_audit_models import CLIENT_VISIBLE_FILES
from offdata_core.ai_audit_oracle import (
    ANSWER_KEY_NAME,
    ORACLE_BASELINE_NAME,
    build_ai_audit_oracle,
)
from offdata_core.deliverable_semantic import CitationPresentation, RenderForm
from offdata_core.delivery import DeliverableSurface, VisualArchetype


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict[str, Any]:
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return parsed


def main() -> int:
    root = repository_root()
    fixture = root / "fixtures" / "digital-ai" / "FIXTURE-DAI-001"
    ensure_deliverable_semantic_baseline_isolation(context_paths=CLIENT_VISIBLE_FILES)
    restricted_names = {
        ANSWER_KEY_NAME,
        ORACLE_BASELINE_NAME,
        DELIVERABLE_SEMANTIC_BASELINE_NAME,
    }
    if restricted_names & set(CLIENT_VISIBLE_FILES):
        raise ValueError("Restricted evaluation files are present in the client-visible allowlist.")

    baseline = read_json(fixture / DELIVERABLE_SEMANTIC_BASELINE_NAME)
    if baseline.get("classification") != "restricted_evaluation_semantic_model":
        raise ValueError("Deliverable semantic baseline classification is invalid.")
    if baseline.get("agent_visible") is not False:
        raise ValueError("Deliverable semantic baseline must declare agent_visible=false.")

    oracle = build_ai_audit_oracle(fixture)
    model = build_ai_audit_deliverable_semantic_model(oracle)
    grade = grade_ai_audit_deliverable_semantic_model(model, oracle)
    if not grade.passed:
        raise ValueError(f"Deliverable semantic grade failed: {grade.failures}")
    verify_committed_deliverable_semantic_baseline(fixture)

    surfaces = {plan.manifest.surface for plan in model.surface_plans}
    expected_surfaces = {
        DeliverableSurface.PPTX,
        DeliverableSurface.DOCX,
        DeliverableSurface.XLSX,
        DeliverableSurface.PDF,
        DeliverableSurface.SVG,
        DeliverableSurface.HTML,
    }
    if surfaces != expected_surfaces:
        raise ValueError("Required semantic output surfaces are incomplete.")
    if model.story.recommendation_ids != ("UC-001", "UC-008"):
        raise ValueError("Primary pilot or non-AI comparator was lost from the story model.")
    if len(model.numbers) != 18 or not all(item.approved for item in model.numbers):
        raise ValueError("Approved named number registry is incomplete.")
    if len(model.citations) != 6:
        raise ValueError("Citation registry is incomplete.")
    if not all(
        CitationPresentation.APPENDIX in item.presentation_modes
        and CitationPresentation.SOURCE_TAB in item.presentation_modes
        for item in model.citations
    ):
        raise ValueError("Citation presentation modes are incomplete.")
    expected_archetypes = {
        VisualArchetype.PORTFOLIO_MATRIX,
        VisualArchetype.PROCESS_FLOW,
        VisualArchetype.VALUE_DRIVER_TREE,
        VisualArchetype.LAYERED_STACK,
        VisualArchetype.ROADMAP,
        VisualArchetype.CAUSAL_NARRATIVE,
    }
    if {item.archetype for item in model.visuals} != expected_archetypes:
        raise ValueError("First visual grammar is incomplete.")
    if any(
        surface_object.render_form is RenderForm.TEXT
        for plan in model.surface_plans
        for surface_object in plan.objects
        if next(
            item
            for item in model.semantic_objects
            if item.semantic_object_id == surface_object.semantic_object_id
        ).visual_specification_ids
    ):
        raise ValueError("A labelled visual is represented as text-only content.")
    if not model.reconciliation.passed:
        raise ValueError("Cross-format semantic reconciliation did not pass.")
    if "do not issue" not in model.founder_review.exact_release_action.casefold():
        raise ValueError("Phase 4 incorrectly authorises external deliverable issuance.")

    completed = read_json(root / "requirements/completed-planned-tests-phase4.json").get(
        "completed_test_ids"
    )
    if not isinstance(completed, list) or len(completed) != 4:
        raise ValueError("Phase 4 completed planned-test register is incomplete.")

    print("PHASE 4 DELIVERABLE SEMANTIC MODEL VALIDATION PASSED")
    checks = (
        f"story_sections={len(model.story.sections)}",
        f"assertions={len(model.story.assertions)}",
        f"numbers={len(model.numbers)}",
        f"citations={len(model.citations)}",
        f"visuals={len(model.visuals)}",
        f"semantic_objects={len(model.semantic_objects)}",
        f"surface_plans={len(model.surface_plans)}",
        f"surface_objects={sum(len(plan.objects) for plan in model.surface_plans)}",
        f"semantic_grade_checks={grade.checks_run}",
        f"completed_planned_tests={len(completed)}",
    )
    for check in checks:
        print(f"- {check}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, OSError, TypeError, ValueError) as exc:
        print(f"PHASE 4 DELIVERABLE SEMANTIC MODEL VALIDATION FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
