"""Deterministic approval-policy evaluation for proposed offdata actions."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from .models import ApprovalDecision, DecisionClass, EvidenceLevel
from .policy_rank import evidence_rank, higher_evidence


class ActionType(StrEnum):
    INTERNAL_RESEARCH = "internal_research"
    INTERNAL_DRAFT = "internal_draft"
    CLIENT_FACING_DRAFT = "client_facing_draft"
    USE_CLIENT_DATA = "use_client_data"
    EXPORT_INTERNAL_ARTEFACT = "export_internal_artefact"
    SEND_EXTERNAL = "send_external"
    COMMERCIAL_COMMITMENT = "commercial_commitment"
    LEGAL_REGULATORY_CONCLUSION = "legal_regulatory_conclusion"
    PRODUCTION_OR_DESTRUCTIVE_CHANGE = "production_or_destructive_change"
    METHODOLOGY_PROMOTION = "methodology_promotion"


class PolicyContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    data_access_authorised: bool = False
    purpose_and_retention_known: bool = False
    draft_marked_not_approved: bool = False
    internal_destination_approved: bool = False
    source_rights_checked: bool = False
    confidentiality_reviewed: bool = False
    qualified_specialist_review: bool = False
    independent_challenge_complete: bool = False
    founder_approved: bool = False
    external_release_authorised: bool = False
    versioned_inputs: bool = False
    idempotency_key_present: bool = False
    regression_tests_passed: bool = False
    provenance_review_complete: bool = False


class ProposedAction(BaseModel):
    model_config = ConfigDict(frozen=True)

    action_type: ActionType
    decision_classes: frozenset[DecisionClass] = Field(default_factory=frozenset)
    context: PolicyContext = Field(default_factory=PolicyContext)


class PolicyResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    decision: ApprovalDecision
    minimum_evidence: EvidenceLevel
    required_approvals: tuple[str, ...] = ()
    unmet_conditions: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()


_CLASS_EVIDENCE = {
    DecisionClass.ROUTINE: EvidenceLevel.E1,
    DecisionClass.MATERIAL: EvidenceLevel.E2,
    DecisionClass.EXTERNAL: EvidenceLevel.E2,
    DecisionClass.COMMERCIAL: EvidenceLevel.E3,
    DecisionClass.LEGAL_REGULATORY: EvidenceLevel.E3,
    DecisionClass.IRREVERSIBLE: EvidenceLevel.E4,
}


def _minimum_evidence(classes: frozenset[DecisionClass]) -> EvidenceLevel:
    if not classes:
        return EvidenceLevel.E1
    return max((_CLASS_EVIDENCE[item] for item in classes), key=evidence_rank)


def evaluate_action(action: ProposedAction) -> PolicyResult:
    """Return the strictest policy decision for a proposed action."""

    classes = set(action.decision_classes)
    ctx = action.context
    required: set[str] = set()
    unmet: list[str] = []

    inferred_class = {
        ActionType.SEND_EXTERNAL: DecisionClass.EXTERNAL,
        ActionType.COMMERCIAL_COMMITMENT: DecisionClass.COMMERCIAL,
        ActionType.LEGAL_REGULATORY_CONCLUSION: DecisionClass.LEGAL_REGULATORY,
        ActionType.PRODUCTION_OR_DESTRUCTIVE_CHANGE: DecisionClass.IRREVERSIBLE,
        ActionType.METHODOLOGY_PROMOTION: DecisionClass.MATERIAL,
    }.get(action.action_type)
    if inferred_class is not None:
        classes.add(inferred_class)

    evidence = _minimum_evidence(frozenset(classes))

    if action.action_type is ActionType.USE_CLIENT_DATA:
        if not ctx.data_access_authorised:
            unmet.append("Client-data access is not authorised.")
        if not ctx.purpose_and_retention_known:
            unmet.append("Purpose and retention rules are not recorded.")
        if unmet:
            return PolicyResult(
                decision=ApprovalDecision.PROHIBIT,
                minimum_evidence=higher_evidence(evidence, EvidenceLevel.E2),
                unmet_conditions=tuple(unmet),
                reasons=(
                    "Client data may be used only within authorised purpose and retention rules.",
                ),
            )

    if action.action_type is ActionType.CLIENT_FACING_DRAFT and not ctx.draft_marked_not_approved:
        return PolicyResult(
            decision=ApprovalDecision.PROHIBIT,
            minimum_evidence=higher_evidence(evidence, EvidenceLevel.E2),
            unmet_conditions=("Draft is not marked DRAFT — NOT APPROVED.",),
            reasons=("Unapproved client-facing work must not imply agreement or release.",),
        )

    if action.action_type is ActionType.EXPORT_INTERNAL_ARTEFACT:
        if not ctx.internal_destination_approved:
            unmet.append("Internal destination is not approved.")
        if not ctx.versioned_inputs:
            unmet.append("Artefact inputs and version are not controlled.")
        if unmet:
            return PolicyResult(
                decision=ApprovalDecision.PROHIBIT,
                minimum_evidence=evidence,
                unmet_conditions=tuple(unmet),
                reasons=(
                    "Internal exports require an approved destination and visible version state.",
                ),
            )

    if DecisionClass.LEGAL_REGULATORY in classes:
        required.update({"Founder", "Qualified specialist"})
        if not ctx.qualified_specialist_review:
            unmet.append("Qualified legal, regulatory or compliance review is missing.")
        if not ctx.founder_approved:
            unmet.append("Founder approval is missing.")
        if unmet:
            return PolicyResult(
                decision=ApprovalDecision.PROHIBIT,
                minimum_evidence=evidence,
                required_approvals=tuple(sorted(required)),
                unmet_conditions=tuple(unmet),
                reasons=("AI-only legal or regulated judgement is prohibited.",),
            )

    if DecisionClass.IRREVERSIBLE in classes:
        required.add("Founder")
        if not ctx.independent_challenge_complete:
            unmet.append("Independent challenge is incomplete.")
        if not ctx.founder_approved:
            unmet.append("Founder approval is missing.")
        if not ctx.idempotency_key_present:
            unmet.append("Idempotency or duplicate-action control is missing.")
        if unmet:
            return PolicyResult(
                decision=ApprovalDecision.REQUEST_APPROVAL,
                minimum_evidence=evidence,
                required_approvals=tuple(sorted(required)),
                unmet_conditions=tuple(unmet),
                reasons=("Irreversible or hard-to-reverse actions cannot execute autonomously.",),
            )

    if action.action_type is ActionType.SEND_EXTERNAL or DecisionClass.EXTERNAL in classes:
        required.add("Founder or delegated external-action approver")
        if not ctx.source_rights_checked:
            unmet.append("Source and usage rights are not checked.")
        if not ctx.confidentiality_reviewed:
            unmet.append("Confidentiality review is incomplete.")
        if not ctx.external_release_authorised:
            unmet.append("External release is not authorised.")
        if not ctx.idempotency_key_present:
            unmet.append("Idempotency key is missing.")
        if unmet:
            return PolicyResult(
                decision=ApprovalDecision.REQUEST_APPROVAL,
                minimum_evidence=evidence,
                required_approvals=tuple(sorted(required)),
                unmet_conditions=tuple(unmet),
                reasons=("External action requires explicit release authority.",),
            )

    if action.action_type is ActionType.COMMERCIAL_COMMITMENT or DecisionClass.COMMERCIAL in classes:
        required.add("Founder")
        if not ctx.founder_approved:
            unmet.append("Founder commercial approval is missing.")
        if unmet:
            return PolicyResult(
                decision=ApprovalDecision.REQUEST_APPROVAL,
                minimum_evidence=evidence,
                required_approvals=tuple(sorted(required)),
                unmet_conditions=tuple(unmet),
                reasons=("Commercial commitments remain Founder-controlled.",),
            )

    if action.action_type is ActionType.METHODOLOGY_PROMOTION:
        required.add("Founder or Methodology Library Owner")
        if not ctx.provenance_review_complete:
            unmet.append("Provenance and copyright review is incomplete.")
        if not ctx.regression_tests_passed:
            unmet.append("Methodology regression tests have not passed.")
        if not ctx.founder_approved:
            unmet.append("Founder or library-owner approval is missing.")
        if unmet:
            return PolicyResult(
                decision=ApprovalDecision.REQUEST_APPROVAL,
                minimum_evidence=higher_evidence(evidence, EvidenceLevel.E2),
                required_approvals=tuple(sorted(required)),
                unmet_conditions=tuple(unmet),
                reasons=("Methodology candidates cannot promote themselves.",),
            )

    if DecisionClass.MATERIAL in classes:
        required.add("Founder or delegated accountable human")
        if not ctx.founder_approved:
            return PolicyResult(
                decision=ApprovalDecision.REQUEST_APPROVAL,
                minimum_evidence=evidence,
                required_approvals=tuple(sorted(required)),
                unmet_conditions=("Material approval is missing.",),
                reasons=(
                    "The system may analyse and recommend but cannot commit a material choice.",
                ),
            )

    if action.action_type is ActionType.CLIENT_FACING_DRAFT:
        return PolicyResult(
            decision=ApprovalDecision.EXECUTE_WITH_CONDITIONS,
            minimum_evidence=higher_evidence(evidence, EvidenceLevel.E2),
            reasons=("Draft may be created internally when clearly marked unapproved.",),
        )

    return PolicyResult(
        decision=ApprovalDecision.AUTO_EXECUTE,
        minimum_evidence=evidence,
        reasons=("Action is bounded, reversible and internal within the supplied policy context.",),
    )
