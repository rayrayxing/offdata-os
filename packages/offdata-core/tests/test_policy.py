from offdata_core import ApprovalDecision, DecisionClass, EvidenceLevel
from offdata_core.policy import ActionType, PolicyContext, ProposedAction, evaluate_action


def test_routine_internal_research_auto_executes() -> None:
    result = evaluate_action(
        ProposedAction(
            action_type=ActionType.INTERNAL_RESEARCH,
            decision_classes=frozenset({DecisionClass.ROUTINE}),
        )
    )
    assert result.decision is ApprovalDecision.AUTO_EXECUTE
    assert result.minimum_evidence is EvidenceLevel.E1


def test_client_draft_requires_unapproved_marking() -> None:
    result = evaluate_action(ProposedAction(action_type=ActionType.CLIENT_FACING_DRAFT))
    assert result.decision is ApprovalDecision.PROHIBIT


def test_marked_client_draft_can_be_prepared() -> None:
    result = evaluate_action(
        ProposedAction(
            action_type=ActionType.CLIENT_FACING_DRAFT,
            context=PolicyContext(draft_marked_not_approved=True),
        )
    )
    assert result.decision is ApprovalDecision.EXECUTE_WITH_CONDITIONS
    assert result.minimum_evidence is EvidenceLevel.E2


def test_client_data_without_authority_is_prohibited() -> None:
    result = evaluate_action(ProposedAction(action_type=ActionType.USE_CLIENT_DATA))
    assert result.decision is ApprovalDecision.PROHIBIT
    assert len(result.unmet_conditions) == 2


def test_external_send_requests_approval() -> None:
    result = evaluate_action(ProposedAction(action_type=ActionType.SEND_EXTERNAL))
    assert result.decision is ApprovalDecision.REQUEST_APPROVAL
    assert result.minimum_evidence is EvidenceLevel.E2
    assert "External release is not authorised." in result.unmet_conditions


def test_fully_authorised_external_send_can_execute() -> None:
    result = evaluate_action(
        ProposedAction(
            action_type=ActionType.SEND_EXTERNAL,
            context=PolicyContext(
                source_rights_checked=True,
                confidentiality_reviewed=True,
                external_release_authorised=True,
                idempotency_key_present=True,
            ),
        )
    )
    assert result.decision is ApprovalDecision.AUTO_EXECUTE


def test_legal_conclusion_without_specialist_is_prohibited() -> None:
    result = evaluate_action(
        ProposedAction(action_type=ActionType.LEGAL_REGULATORY_CONCLUSION)
    )
    assert result.decision is ApprovalDecision.PROHIBIT
    assert "Qualified specialist" in result.required_approvals


def test_irreversible_action_requires_challenge_and_approval() -> None:
    result = evaluate_action(
        ProposedAction(action_type=ActionType.PRODUCTION_OR_DESTRUCTIVE_CHANGE)
    )
    assert result.decision is ApprovalDecision.REQUEST_APPROVAL
    assert result.minimum_evidence is EvidenceLevel.E4


def test_methodology_promotion_requires_governance() -> None:
    result = evaluate_action(ProposedAction(action_type=ActionType.METHODOLOGY_PROMOTION))
    assert result.decision is ApprovalDecision.REQUEST_APPROVAL
    assert "Methodology regression tests have not passed." in result.unmet_conditions


def test_approved_methodology_promotion_can_execute() -> None:
    result = evaluate_action(
        ProposedAction(
            action_type=ActionType.METHODOLOGY_PROMOTION,
            context=PolicyContext(
                provenance_review_complete=True,
                regression_tests_passed=True,
                founder_approved=True,
            ),
        )
    )
    assert result.decision is ApprovalDecision.AUTO_EXECUTE
