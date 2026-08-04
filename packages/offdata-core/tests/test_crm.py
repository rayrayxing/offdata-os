from datetime import UTC, datetime

import pytest

from offdata_core.crm import (
    ConsentStatus,
    Contact,
    OpportunityDossier,
    OutreachControl,
    OutreachDecision,
    assess_outreach,
)


NOW = datetime(2026, 8, 4, tzinfo=UTC)


def _contact(**overrides: object) -> Contact:
    values = {
        "contact_id": "CON-1",
        "organisation_id": "ORG-1",
        "name": "Alex Tan",
        "relationship_owner": "Founder",
        "source_reference": "SRC-PUBLIC-1",
    }
    values.update(overrides)
    return Contact(**values)


def _opportunity() -> OpportunityDossier:
    return OpportunityDossier(
        opportunity_id="OPP-1",
        organisation_id="ORG-1",
        detected_at=NOW,
        trigger="Public hiring for AI operations roles.",
        evidence_ids=("EVID-1",),
        probable_business_issue="AI use cases are not governed or prioritised.",
        alternative_explanations=("Routine team expansion",),
        likely_buyer_roles=("COO", "CIO"),
        relevant_method_ids=("DAI-05", "DAI-07"),
        proposed_diagnostic="AI opportunity and risk audit",
        proposed_outreach_angle="Prioritise value while establishing controls.",
        confidence=0.7,
        contactability="Named corporate contact",
        jurisdiction="Singapore",
        legal_and_marketing_constraints=("B2B outreach policy",),
        next_action="Prepare a tailored dossier.",
    )


def test_suppressed_contact_requires_reason() -> None:
    with pytest.raises(ValueError, match="suppression reason"):
        _contact(consent_status=ConsentStatus.SUPPRESSED)


def test_suppressed_contact_cannot_be_contacted() -> None:
    contact = _contact(
        consent_status=ConsentStatus.OPTED_OUT,
        suppression_reason="Recipient opted out.",
    )
    result = assess_outreach(
        contact=contact,
        opportunity=_opportunity(),
        control=None,
        proposed_proposition_id="OFFER-AI-AUDIT",
        proposed_segment="SME",
    )
    assert result.decision is OutreachDecision.PROHIBITED


def test_no_campaign_control_means_prepare_only() -> None:
    result = assess_outreach(
        contact=_contact(),
        opportunity=_opportunity(),
        control=None,
        proposed_proposition_id="OFFER-AI-AUDIT",
        proposed_segment="SME",
    )
    assert result.decision is OutreachDecision.PREPARE_ONLY


def test_sending_cannot_be_enabled_without_founder() -> None:
    with pytest.raises(ValueError, match="Founder approval"):
        OutreachControl(
            campaign_id="CAMP-1",
            jurisdiction="Singapore",
            approved_sender_identity="founder@offdata.com",
            approved_proposition_ids=("OFFER-AI-AUDIT",),
            approved_segments=("SME",),
            frequency_limit=2,
            frequency_window_days=30,
            suppression_list_reference="SUPPRESS-1",
            opt_out_mechanism="Reply unsubscribe",
            external_sending_enabled=True,
        )


def test_approved_campaign_authorises_bounded_outreach() -> None:
    control = OutreachControl(
        campaign_id="CAMP-1",
        jurisdiction="Singapore",
        approved_sender_identity="founder@offdata.com",
        approved_proposition_ids=("OFFER-AI-AUDIT",),
        approved_segments=("SME",),
        frequency_limit=2,
        frequency_window_days=30,
        suppression_list_reference="SUPPRESS-1",
        opt_out_mechanism="Reply unsubscribe",
        founder_approved=True,
        external_sending_enabled=True,
    )
    result = assess_outreach(
        contact=_contact(),
        opportunity=_opportunity(),
        control=control,
        proposed_proposition_id="OFFER-AI-AUDIT",
        proposed_segment="SME",
    )
    assert result.decision is OutreachDecision.AUTHORISED
