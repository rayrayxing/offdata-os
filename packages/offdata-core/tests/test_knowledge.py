from datetime import UTC, date, datetime

import pytest

from offdata_core.knowledge import (
    AuthorityClass,
    CandidateDecision,
    ConfidentialityClass,
    MethodRecord,
    MethodSelection,
    MethodologyCandidate,
    PromotionState,
    SourceDocument,
    SourcePassage,
    SourceType,
)


def test_source_requires_valid_sha256() -> None:
    with pytest.raises(ValueError, match="SHA-256"):
        SourceDocument(
            source_id="SRC-1",
            original_filename="source.pdf",
            checksum_sha256="bad",
            title="Source",
            retrieval_date=date(2026, 8, 4),
            source_type=SourceType.PUBLIC_WEB,
            authority_class=AuthorityClass.SECONDARY_RELIABLE,
            object_reference="s3://source.pdf",
            confidentiality=ConfidentialityClass.PUBLIC,
        )


def test_client_confidential_source_requires_tenant_scope() -> None:
    with pytest.raises(ValueError, match="tenant scope"):
        SourceDocument(
            source_id="SRC-1",
            original_filename="client.docx",
            checksum_sha256="a" * 64,
            title="Client document",
            retrieval_date=date(2026, 8, 4),
            source_type=SourceType.CLIENT_DOCUMENT,
            authority_class=AuthorityClass.PRIMARY_AUTHORITATIVE,
            object_reference="s3://client.docx",
            confidentiality=ConfidentialityClass.CLIENT_CONFIDENTIAL,
        )


def test_passage_requires_location() -> None:
    with pytest.raises(ValueError, match="requires a page"):
        SourcePassage(
            passage_id="PASS-1",
            source_id="SRC-1",
            text="Evidence text",
            extraction_method="parser",
            extraction_confidence=1.0,
        )


def test_method_requires_substantive_fields() -> None:
    with pytest.raises(ValueError, match="missing required content"):
        MethodRecord(
            method_id="M-1",
            name="Method",
            domains=(),
            method_family="diagnostic",
            decisions_supported=(),
            inference_types=frozenset(),
            appropriate_problem_types=(),
            preconditions=(),
            minimum_evidence="E2",
            inputs=(),
            procedure=(),
            outputs=(),
            limitations=(),
            when_not_to_use=(),
            failure_modes=(),
            quality_tests=(),
            falsification_tests=(),
            source_ids=(),
            usage_rights_status="reviewed",
            version="0.1.0",
            promotion_state=PromotionState.DRAFT,
        )


def test_method_selection_requires_role_for_each_method() -> None:
    with pytest.raises(ValueError, match="missing roles"):
        MethodSelection(
            selection_id="SEL-1",
            engagement_id="ENG-1",
            decision_id="DEC-1",
            governing_archetype="ARCH-1",
            selected_methods=("M-1", "M-2"),
            sequence_rationale=("M-1 before M-2",),
            method_roles={"M-1": "diagnostic"},
            required_data=("Data",),
        )


def test_candidate_cannot_promote_without_controls() -> None:
    with pytest.raises(ValueError, match="Promotion decision missing"):
        MethodologyCandidate(
            candidate_id="CAND-1",
            discovered_at=datetime(2026, 8, 4, tzinfo=UTC),
            discovery_source_ids=("SRC-1",),
            claimed_name="New method",
            claimed_description="Claimed method",
            novelty_assessment="Potentially distinct",
            existing_method_comparison={},
            primary_support_ids=("SRC-1",),
            copyright_assessment="Underlying method only",
            original_reconstruction={},
            evaluation_fixture_ids=("FIX-1",),
            evaluation_results={},
            decision=CandidateDecision.PROMOTE,
        )
