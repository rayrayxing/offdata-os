"""CRM, opportunity and controlled-outreach contracts."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class RelationshipStatus(StrEnum):
    PROSPECT = "prospect"
    ACTIVE_OPPORTUNITY = "active_opportunity"
    CLIENT = "client"
    FORMER_CLIENT = "former_client"
    PARTNER = "partner"
    DO_NOT_CONTACT = "do_not_contact"


class ConsentStatus(StrEnum):
    UNKNOWN = "unknown"
    PERMITTED = "permitted"
    OPTED_OUT = "opted_out"
    OBJECTED = "objected"
    SUPPRESSED = "suppressed"


class OpportunityStage(StrEnum):
    DETECTED = "detected"
    RESEARCHED = "researched"
    QUALIFIED = "qualified"
    OUTREACH_PROPOSED = "outreach_proposed"
    OUTREACH_APPROVED = "outreach_approved"
    CONVERSATION = "conversation"
    PROPOSAL = "proposal"
    WON = "won"
    LOST = "lost"
    DISQUALIFIED = "disqualified"


class OutreachDecision(StrEnum):
    PREPARE_ONLY = "prepare_only"
    REQUEST_APPROVAL = "request_approval"
    AUTHORISED = "authorised"
    PROHIBITED = "prohibited"


class Organisation(BaseModel):
    model_config = ConfigDict(frozen=True)

    organisation_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    aliases: tuple[str, ...] = ()
    registration_jurisdiction: str | None = None
    industry: str = ""
    sector: str = ""
    website: str | None = None
    domains: tuple[str, ...] = ()
    crm_identifiers: dict[str, str] = Field(default_factory=dict)
    relationship_status: RelationshipStatus = RelationshipStatus.PROSPECT
    data_residency_requirements: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()
    conflict_flags: tuple[str, ...] = ()


class Contact(BaseModel):
    model_config = ConfigDict(frozen=True)

    contact_id: str = Field(min_length=1)
    organisation_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    role: str = ""
    email: str | None = None
    phone: str | None = None
    relationship_owner: str = Field(min_length=1)
    consent_status: ConsentStatus = ConsentStatus.UNKNOWN
    source_reference: str = Field(min_length=1)
    lawful_use_basis: str = ""
    suppression_reason: str | None = None
    last_contacted_at: datetime | None = None

    @model_validator(mode="after")
    def validate_suppression(self) -> "Contact":
        if self.consent_status in {
            ConsentStatus.OPTED_OUT,
            ConsentStatus.OBJECTED,
            ConsentStatus.SUPPRESSED,
        } and not self.suppression_reason:
            raise ValueError("Suppressed or objected contacts require a suppression reason.")
        return self


class OpportunityDossier(BaseModel):
    model_config = ConfigDict(frozen=True)

    opportunity_id: str = Field(min_length=1)
    organisation_id: str = Field(min_length=1)
    detected_at: datetime
    trigger: str = Field(min_length=1)
    evidence_ids: tuple[str, ...]
    probable_business_issue: str = Field(min_length=1)
    alternative_explanations: tuple[str, ...]
    estimated_value_at_stake: str = ""
    likely_buyer_roles: tuple[str, ...]
    relevant_method_ids: tuple[str, ...]
    proposed_diagnostic: str = Field(min_length=1)
    proposed_outreach_angle: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    contactability: str = Field(min_length=1)
    jurisdiction: str = Field(min_length=1)
    legal_and_marketing_constraints: tuple[str, ...]
    stage: OpportunityStage = OpportunityStage.DETECTED
    next_action: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_evidence_and_alternatives(self) -> "OpportunityDossier":
        if not self.evidence_ids:
            raise ValueError("Opportunity dossier requires observed evidence.")
        if not self.alternative_explanations:
            raise ValueError("Opportunity dossier must consider alternative explanations.")
        if not self.likely_buyer_roles:
            raise ValueError("Opportunity dossier requires at least one likely buyer role.")
        return self


class OutreachControl(BaseModel):
    model_config = ConfigDict(frozen=True)

    campaign_id: str = Field(min_length=1)
    jurisdiction: str = Field(min_length=1)
    approved_sender_identity: str = Field(min_length=1)
    approved_proposition_ids: tuple[str, ...]
    approved_segments: tuple[str, ...]
    frequency_limit: int = Field(ge=1)
    frequency_window_days: int = Field(ge=1)
    suppression_list_reference: str = Field(min_length=1)
    opt_out_mechanism: str = Field(min_length=1)
    founder_approved: bool = False
    external_sending_enabled: bool = False

    @model_validator(mode="after")
    def validate_sending_authority(self) -> "OutreachControl":
        if self.external_sending_enabled and not self.founder_approved:
            raise ValueError("External sending cannot be enabled without Founder approval.")
        return self


class OutreachAssessment(BaseModel):
    model_config = ConfigDict(frozen=True)

    decision: OutreachDecision
    reasons: tuple[str, ...]
    required_actions: tuple[str, ...] = ()


def assess_outreach(
    *,
    contact: Contact,
    opportunity: OpportunityDossier,
    control: OutreachControl | None,
    proposed_proposition_id: str,
    proposed_segment: str,
) -> OutreachAssessment:
    """Assess whether an outreach message may be prepared or sent."""

    if contact.consent_status in {
        ConsentStatus.OPTED_OUT,
        ConsentStatus.OBJECTED,
        ConsentStatus.SUPPRESSED,
    }:
        return OutreachAssessment(
            decision=OutreachDecision.PROHIBITED,
            reasons=("Contact is opted out, objected or suppressed.",),
        )

    if control is None:
        return OutreachAssessment(
            decision=OutreachDecision.PREPARE_ONLY,
            reasons=("No approved campaign control exists; research and drafting only.",),
            required_actions=("Create and approve a jurisdiction-specific campaign control.",),
        )

    missing: list[str] = []
    if opportunity.jurisdiction != control.jurisdiction:
        missing.append("Campaign jurisdiction does not match opportunity jurisdiction.")
    if proposed_proposition_id not in control.approved_proposition_ids:
        missing.append("Proposition is outside the approved campaign scope.")
    if proposed_segment not in control.approved_segments:
        missing.append("Segment is outside the approved campaign scope.")
    if not control.founder_approved:
        missing.append("Founder has not approved the campaign.")
    if not control.external_sending_enabled:
        missing.append("External sending is not enabled.")

    if missing:
        return OutreachAssessment(
            decision=OutreachDecision.REQUEST_APPROVAL,
            reasons=("Outreach may be drafted but not sent.",),
            required_actions=tuple(missing),
        )

    return OutreachAssessment(
        decision=OutreachDecision.AUTHORISED,
        reasons=("Contact and campaign controls permit bounded outreach.",),
    )
