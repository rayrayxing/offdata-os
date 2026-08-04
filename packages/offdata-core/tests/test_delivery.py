import pytest

from offdata_core.delivery import (
    Assertion,
    CrossFormatReconciliation,
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


def test_fact_assertion_requires_evidence() -> None:
    with pytest.raises(ValueError, match="require evidence"):
        Assertion(
            assertion_id="A-1",
            statement="Revenue declined.",
            epistemic_status=EpistemicStatus.ESTABLISHED_FACT,
        )


def test_story_section_cannot_reference_missing_assertion() -> None:
    assertion = Assertion(
        assertion_id="A-1",
        statement="A controlled pilot is recommended.",
        epistemic_status=EpistemicStatus.RECOMMENDATION,
        analysis_ids=("AN-1",),
    )
    with pytest.raises(ValueError, match="missing assertions"):
        StoryModel(
            story_model_id="STORY-1",
            version="1.0.0",
            engagement_id="ENG-1",
            decision_id="DEC-1",
            audience_roles=("CEO",),
            communication_objective="Obtain pilot approval.",
            governing_thought="Pilot before scaling.",
            assertions=(assertion,),
            sections=(
                StorySection(
                    section_id="SEC-1",
                    title="Recommendation",
                    purpose="Present the decision.",
                    assertion_ids=("A-2",),
                ),
            ),
        )


def test_visual_relationship_requires_known_entities() -> None:
    with pytest.raises(ValueError, match="unknown target"):
        VisualSpecification(
            visual_specification_id="VIS-1",
            archetype=VisualArchetype.CAUSAL_NARRATIVE,
            message="A leads to B.",
            entities=(VisualEntity(entity_id="A", label="A"),),
            relationships=(
                VisualRelationship(
                    source_entity_id="A",
                    target_entity_id="B",
                    relationship="causes",
                ),
            ),
            layout_rules=("left_to_right",),
            accessibility_rules=("text_alternative",),
            allowed_surfaces=frozenset({DeliverableSurface.PPTX}),
        )


def test_reconciliation_requires_all_eight_checks() -> None:
    with pytest.raises(ValueError, match="missing checks"):
        CrossFormatReconciliation(
            reconciliation_id="REC-1",
            story_model_id="STORY-1",
            deliverable_ids=("PPTX-1", "DOCX-1"),
            results=(
                ReconciliationResult(
                    check=ReconciliationCheck.HEADLINE,
                    passed=True,
                    details="Headlines match.",
                ),
            ),
            reviewer_id="reviewer",
        )


def test_complete_reconciliation_passes() -> None:
    results = tuple(
        ReconciliationResult(check=check, passed=True, details=f"{check.value} passed")
        for check in ReconciliationCheck
    )
    reconciliation = CrossFormatReconciliation(
        reconciliation_id="REC-1",
        story_model_id="STORY-1",
        deliverable_ids=("PPTX-1", "DOCX-1"),
        results=results,
        reviewer_id="reviewer",
    )
    assert reconciliation.passed
