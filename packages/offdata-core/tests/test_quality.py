import pytest

from offdata_core.quality import (
    AssuranceTier,
    Defect,
    DefectSeverity,
    DimensionScore,
    QualityGate,
    QualityReview,
    ReviewConclusion,
    assess_gate,
)


def _scores(value: int) -> tuple[DimensionScore, ...]:
    ids = (
        "QD-MAND-01",
        "QD-EVID-01",
        "QD-RCOV-01",
        "QD-METH-01",
        "QD-REAS-01",
        "QD-CLNT-01",
        "QD-FIN-01",
        "QD-FEAS-01",
        "QD-EXEC-01",
        "QD-STOR-01",
        "QD-PRES-01",
        "QD-AUDT-01",
    )
    return tuple(
        DimensionScore(dimension_id=item, score=value, evidence_reference=f"EV-{item}")
        for item in ids
    )


def test_weighted_score_remains_on_four_point_scale() -> None:
    review = QualityReview(
        review_id="REV-1",
        artefact_reference="DELIV-1",
        assurance_tier=AssuranceTier.T1_MODERATE,
        reviewer_id="reviewer",
        creator_id="creator",
        dimensions=_scores(3),
    )
    assert review.weighted_score == 3.0


def test_founder_ready_passes_at_standard() -> None:
    review = QualityReview(
        review_id="REV-1",
        artefact_reference="DELIV-1",
        assurance_tier=AssuranceTier.T1_MODERATE,
        reviewer_id="reviewer",
        creator_id="creator",
        dimensions=_scores(3),
    )
    result = assess_gate(review, QualityGate.FOUNDER_READY)
    assert result.conclusion is ReviewConclusion.PASS


def test_s2_blocks_founder_ready() -> None:
    defect = Defect(
        defect_id="DEF-1",
        severity=DefectSeverity.S2_MAJOR,
        affected_object="Slide 2",
        defect="Material calculation mismatch.",
        consequence="Could change the recommendation.",
        required_repair="Recalculate and replace all occurrences.",
        required_retest="Reconcile to named workbook output.",
        owner="builder",
        creator_actor_id="reviewer",
    )
    review = QualityReview(
        review_id="REV-1",
        artefact_reference="DELIV-1",
        assurance_tier=AssuranceTier.T1_MODERATE,
        reviewer_id="reviewer",
        creator_id="creator",
        dimensions=_scores(4),
        defects=(defect,),
    )
    result = assess_gate(review, QualityGate.FOUNDER_READY)
    assert result.conclusion is ReviewConclusion.FAIL


def test_external_t2_requires_independent_signoff() -> None:
    review = QualityReview(
        review_id="REV-1",
        artefact_reference="DELIV-1",
        assurance_tier=AssuranceTier.T2_HIGH,
        reviewer_id="reviewer",
        creator_id="creator",
        dimensions=_scores(4),
    )
    result = assess_gate(review, QualityGate.EXTERNAL_RELEASE)
    assert result.conclusion is ReviewConclusion.FAIL
    assert "independent sign-off" in result.blocking_reasons[0]


def test_t2_creator_cannot_be_reviewer() -> None:
    with pytest.raises(ValueError, match="cannot be signed off"):
        QualityReview(
            review_id="REV-1",
            artefact_reference="DELIV-1",
            assurance_tier=AssuranceTier.T2_HIGH,
            reviewer_id="same",
            creator_id="same",
            dimensions=_scores(4),
        )


def test_s1_self_closure_needs_independent_verification() -> None:
    with pytest.raises(ValueError, match="independent verification"):
        Defect(
            defect_id="DEF-1",
            severity=DefectSeverity.S1_CRITICAL,
            affected_object="Report",
            defect="Fabricated source.",
            consequence="Unsafe external reliance.",
            required_repair="Remove and rebuild evidence chain.",
            required_retest="Independent source validation.",
            owner="creator",
            status="closed",
            creator_actor_id="creator",
            closer_actor_id="creator",
        )
