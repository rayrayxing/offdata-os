from __future__ import annotations

import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from offdata_core.security_regionalisation import (
    MANDATORY_REAL_CLIENT_CONTROLS,
    AccessAction,
    AccessRequest,
    ActorSecurityContext,
    CrossRegionTransferRequest,
    DataClassification,
    DecisionDisposition,
    EvidenceStatus,
    IncidentSeverity,
    IncidentSignal,
    ProcessorApprovalStatus,
    ProcessorUseRequest,
    ProductionGateRequest,
    ProviderProcessorRecord,
    RecordSecurityContext,
    RegionPlacementRequest,
    RegionalCell,
    RegionalPolicy,
    RetentionDisposition,
    RetentionPolicy,
    RuntimeEnvironment,
    ScopeKind,
    SecurityControlEvidence,
    assess_incident,
    authorise_cross_region_transfer,
    authorise_processor_use,
    authorise_record_access,
    authorise_region_placement,
    build_security_baseline,
    evaluate_production_gate,
    evaluate_retention,
    looks_like_secret,
    make_current_control_evidence,
    most_restrictive_classification,
    scan_for_secret_like_values,
    verify_security_baseline,
    write_security_baseline,
)


NOW = datetime(2026, 8, 5, 4, 0, tzinfo=timezone.utc)


def _record(**overrides: object) -> RecordSecurityContext:
    values: dict[str, object] = {
        "record_id": "REC-001",
        "classification": DataClassification.CLIENT_CONFIDENTIAL,
        "scope_kind": ScopeKind.ENGAGEMENT,
        "tenant_id": "TENANT-001",
        "engagement_id": "ENG-001",
        "home_region": "singapore",
        "allowed_regions": ("singapore",),
        "retention_policy_id": "RET-CLIENT-DEFAULT",
        "client_content": True,
        "approved_processor_ids": ("PROC-SYNTH-SG-LLM-001",),
    }
    values.update(overrides)
    return RecordSecurityContext.model_validate(values)


def _actor(**overrides: object) -> ActorSecurityContext:
    values: dict[str, object] = {
        "actor_id": "USER-001",
        "actor_type": "human",
        "environment": RuntimeEnvironment.PRODUCTION,
        "tenant_id": "TENANT-001",
        "engagement_ids": ("ENG-001",),
        "authorised_regions": ("singapore",),
        "capabilities": ("record_read",),
        "mfa_verified": True,
        "founder_authority": False,
    }
    values.update(overrides)
    return ActorSecurityContext.model_validate(values)


def _access(action: AccessAction = AccessAction.READ, **overrides: object) -> AccessRequest:
    values: dict[str, object] = {
        "request_id": "REQ-001",
        "action": action,
        "actor": _actor(),
        "record": _record(),
        "requested_region": "singapore",
        "requested_at": NOW,
    }
    values.update(overrides)
    return AccessRequest.model_validate(values)


def _cell(**overrides: object) -> RegionalCell:
    values: dict[str, object] = {
        "cell_id": "CELL-SG-PROD-TEST",
        "region": "singapore",
        "country": "SG",
        "environment": RuntimeEnvironment.PRODUCTION,
        "status": "planned",
        "components": ("application_compute", "postgresql", "object_storage"),
        "permitted_classifications": (
            DataClassification.PUBLIC,
            DataClassification.INTERNAL,
        ),
        "client_data_enabled": False,
        "encryption_in_transit": True,
        "encryption_at_rest": True,
        "separate_encryption_keys": True,
        "logs_mode": "metadata_only",
        "backup_regions": (),
        "global_metadata_only": True,
        "gate_evidence_digest": None,
    }
    values.update(overrides)
    return RegionalCell.model_validate(values)


def _policy() -> RegionalPolicy:
    return RegionalPolicy(
        first_managed_region="singapore",
        synthetic_only_until_production_gate=True,
        client_data_cross_region_default="deny",
        global_metadata_fields=("stable_record_id", "source_region"),
        prohibited_global_metadata_fields=("client_name", "evidence_text"),
        approved_region_expansion_requires=("documented_need", "Founder_approval"),
    )


def _processor(**overrides: object) -> ProviderProcessorRecord:
    values: dict[str, object] = {
        "processor_id": "PROC-TEST-001",
        "legal_name": "Synthetic Processor",
        "service_name": "Synthetic Service",
        "purposes": ("controlled_model_inference",),
        "permitted_classifications": (
            DataClassification.PUBLIC,
            DataClassification.INTERNAL,
            DataClassification.CLIENT_CONFIDENTIAL,
        ),
        "approved_regions": ("singapore",),
        "retention_days": 0,
        "subprocessors": (),
        "credential_reference": "credential-ref://synthetic/test",
        "credential_owner": "Founder",
        "credential_value_stored": False,
        "provider_training_disabled": True,
        "dpa_status": "approved",
        "transfer_basis_status": "not_required",
        "deletion_verification_supported": True,
        "cost_model": "synthetic_zero_cost",
        "exit_plan": "Disable adapter and rebuild derived outputs from canonical records.",
        "approval_status": ProcessorApprovalStatus.APPROVED_CLIENT_CONFIDENTIAL,
        "last_reviewed_at": NOW - timedelta(days=1),
        "next_review_at": NOW + timedelta(days=365),
        "synthetic_fixture": False,
    }
    values.update(overrides)
    return ProviderProcessorRecord.model_validate(values)


def _retention_policy() -> RetentionPolicy:
    return RetentionPolicy(
        policy_id="RET-TEST",
        jurisdiction="configurable",
        classification=DataClassification.CLIENT_CONFIDENTIAL,
        active_retention_days=30,
        archive_after_days=90,
        delete_after_days=365,
        log_retention_days=180,
        legal_hold_supported=True,
        export_before_deletion=True,
        deletion_verification_required=True,
    )


def test_most_restrictive_classification_wins() -> None:
    result = most_restrictive_classification(
        (DataClassification.INTERNAL, DataClassification.HIGHLY_RESTRICTED)
    )
    assert result is DataClassification.HIGHLY_RESTRICTED


def test_most_restrictive_classification_requires_input() -> None:
    with pytest.raises(ValueError, match="At least one"):
        most_restrictive_classification(())


def test_engagement_record_requires_tenant_and_engagement_scope() -> None:
    with pytest.raises(ValidationError):
        _record(tenant_id=None)


def test_global_record_rejects_client_content() -> None:
    with pytest.raises(ValidationError):
        _record(
            scope_kind=ScopeKind.GLOBAL,
            tenant_id=None,
            engagement_id=None,
            client_content=True,
        )


def test_cross_tenant_access_is_denied() -> None:
    decision = authorise_record_access(_access(actor=_actor(tenant_id="TENANT-OTHER")))
    assert decision.disposition is DecisionDisposition.DENY
    assert "Tenant scope mismatch." in decision.reasons


def test_cross_engagement_access_is_denied() -> None:
    decision = authorise_record_access(_access(actor=_actor(engagement_ids=("ENG-OTHER",))))
    assert decision.disposition is DecisionDisposition.DENY
    assert "Engagement scope mismatch." in decision.reasons


def test_restricted_access_requires_mfa() -> None:
    decision = authorise_record_access(_access(actor=_actor(mfa_verified=False)))
    assert decision.disposition is DecisionDisposition.DENY
    assert any("MFA" in reason for reason in decision.reasons)


def test_restricted_client_content_is_prohibited_in_development() -> None:
    decision = authorise_record_access(
        _access(actor=_actor(environment=RuntimeEnvironment.DEVELOPMENT))
    )
    assert decision.disposition is DecisionDisposition.DENY
    assert any("development" in reason for reason in decision.reasons)


def test_read_access_allows_matching_scope_and_region() -> None:
    decision = authorise_record_access(_access())
    assert decision.allowed
    assert decision.required_controls == ("CTRL-AUDIT-EVENT", "CTRL-LEAST-PRIVILEGE")


def test_export_and_delete_require_founder_approval() -> None:
    for action in (AccessAction.EXPORT, AccessAction.DELETE):
        decision = authorise_record_access(_access(action))
        assert decision.disposition is DecisionDisposition.REQUIRE_FOUNDER_APPROVAL
        assert decision.founder_approval_required


def test_external_target_requires_founder_approval() -> None:
    decision = authorise_record_access(_access(external_target=True))
    assert decision.disposition is DecisionDisposition.REQUIRE_FOUNDER_APPROVAL


def test_support_access_requires_capability_and_current_expiry() -> None:
    denied = authorise_record_access(_access(AccessAction.SUPPORT))
    assert denied.disposition is DecisionDisposition.DENY
    allowed = authorise_record_access(
        _access(
            AccessAction.SUPPORT,
            actor=_actor(
                capabilities=("time_limited_support",),
                support_access_expires_at=NOW + timedelta(hours=1),
            ),
        )
    )
    assert allowed.allowed
    assert "CTRL-PRIVILEGED-ACCESS-LOG" in allowed.required_controls


def test_unapproved_processor_for_record_is_denied() -> None:
    decision = authorise_record_access(_access(processor_id="PROC-OTHER"))
    assert decision.disposition is DecisionDisposition.DENY


def test_region_placement_denies_client_content_in_unapproved_cell() -> None:
    decision = authorise_region_placement(
        RegionPlacementRequest(record=_record(), cell=_cell(), policy=_policy())
    )
    assert decision.disposition is DecisionDisposition.DENY
    assert any("client data" in reason.lower() for reason in decision.reasons)


def test_region_placement_allows_internal_record_in_singapore() -> None:
    record = _record(
        classification=DataClassification.INTERNAL,
        scope_kind=ScopeKind.GLOBAL,
        tenant_id=None,
        engagement_id=None,
        client_content=False,
    )
    decision = authorise_region_placement(
        RegionPlacementRequest(record=record, cell=_cell(), policy=_policy())
    )
    assert decision.allowed


def test_region_placement_denies_non_singapore_first_production_cell() -> None:
    record = _record(
        classification=DataClassification.INTERNAL,
        scope_kind=ScopeKind.GLOBAL,
        tenant_id=None,
        engagement_id=None,
        client_content=False,
        home_region="australia",
        allowed_regions=("australia",),
    )
    cell = _cell(region="australia", country="AU")
    decision = authorise_region_placement(
        RegionPlacementRequest(record=record, cell=cell, policy=_policy())
    )
    assert decision.disposition is DecisionDisposition.DENY
    assert any("Singapore-first" in reason for reason in decision.reasons)


def test_same_region_transfer_is_allowed() -> None:
    decision = authorise_cross_region_transfer(
        CrossRegionTransferRequest(
            transfer_id="TR-001",
            record=_record(),
            source_region="singapore",
            destination_region="singapore",
            transfer_scope="full_record",
        )
    )
    assert decision.allowed


def test_cross_region_client_transfer_requires_basis_and_founder_approval() -> None:
    record = _record(allowed_regions=("singapore", "australia"))
    no_basis = authorise_cross_region_transfer(
        CrossRegionTransferRequest(
            transfer_id="TR-002",
            record=record,
            source_region="singapore",
            destination_region="australia",
            transfer_scope="sanitised_extract",
        )
    )
    assert no_basis.disposition is DecisionDisposition.DENY
    needs_founder = authorise_cross_region_transfer(
        CrossRegionTransferRequest(
            transfer_id="TR-003",
            record=record,
            source_region="singapore",
            destination_region="australia",
            transfer_scope="sanitised_extract",
            documented_transfer_basis=True,
            destination_cell_approved=True,
        )
    )
    assert needs_founder.disposition is DecisionDisposition.REQUIRE_FOUNDER_APPROVAL


def test_approved_global_metadata_transfer_is_allowed() -> None:
    record = _record(
        classification=DataClassification.INTERNAL,
        scope_kind=ScopeKind.GLOBAL,
        tenant_id=None,
        engagement_id=None,
        client_content=False,
        allowed_regions=("singapore", "australia"),
    )
    decision = authorise_cross_region_transfer(
        CrossRegionTransferRequest(
            transfer_id="TR-004",
            record=record,
            source_region="singapore",
            destination_region="australia",
            transfer_scope="approved_metadata",
        )
    )
    assert decision.allowed
    assert "CTRL-METADATA-ALLOWLIST" in decision.required_controls


def test_retention_active_archive_export_and_delete_states() -> None:
    policy = _retention_policy()
    active = evaluate_retention(
        policy=policy,
        closed_at=None,
        evaluated_at=NOW,
        legal_hold=False,
        export_completed=False,
    )
    assert active.disposition is RetentionDisposition.RETAIN
    archived = evaluate_retention(
        policy=policy,
        closed_at=NOW - timedelta(days=120),
        evaluated_at=NOW,
        legal_hold=False,
        export_completed=False,
    )
    assert archived.disposition is RetentionDisposition.ARCHIVE
    export = evaluate_retention(
        policy=policy,
        closed_at=NOW - timedelta(days=400),
        evaluated_at=NOW,
        legal_hold=False,
        export_completed=False,
    )
    assert export.disposition is RetentionDisposition.EXPORT_REQUIRED
    delete = evaluate_retention(
        policy=policy,
        closed_at=NOW - timedelta(days=400),
        evaluated_at=NOW,
        legal_hold=False,
        export_completed=True,
    )
    assert delete.disposition is RetentionDisposition.DELETE_ELIGIBLE_WITH_APPROVAL
    assert delete.founder_approval_required
    assert delete.deletion_verification_required


def test_legal_hold_blocks_retention_progression() -> None:
    result = evaluate_retention(
        policy=_retention_policy(),
        closed_at=NOW - timedelta(days=1000),
        evaluated_at=NOW,
        legal_hold=True,
        export_completed=True,
    )
    assert result.disposition is RetentionDisposition.HOLD


def test_retention_rejects_invalid_dates_and_windows() -> None:
    with pytest.raises(ValueError, match="precede"):
        evaluate_retention(
            policy=_retention_policy(),
            closed_at=NOW + timedelta(days=1),
            evaluated_at=NOW,
            legal_hold=False,
            export_completed=False,
        )
    with pytest.raises(ValidationError):
        RetentionPolicy(
            policy_id="RET-BAD",
            jurisdiction="configurable",
            classification=DataClassification.INTERNAL,
            active_retention_days=10,
            archive_after_days=400,
            delete_after_days=365,
            log_retention_days=30,
            legal_hold_supported=True,
            export_before_deletion=False,
            deletion_verification_required=True,
        )


def test_processor_register_rejects_credential_values() -> None:
    with pytest.raises(ValidationError, match="credential values"):
        _processor(credential_value_stored=True)
    with pytest.raises(ValidationError, match="appears to contain a secret"):
        _processor(credential_reference="ghp_abcdefghijklmnopqrstuvwxyz123456")


def test_processor_register_requires_client_data_controls() -> None:
    with pytest.raises(ValidationError, match="DPA"):
        _processor(dpa_status="pending")
    with pytest.raises(ValidationError, match="training"):
        _processor(provider_training_disabled=False)


def test_processor_use_requires_current_scope_region_purpose_and_terms() -> None:
    allowed = authorise_processor_use(
        ProcessorUseRequest(
            processor=_processor(),
            classification=DataClassification.CLIENT_CONFIDENTIAL,
            region="singapore",
            purpose="controlled_model_inference",
            real_client_data=True,
            now=NOW,
        )
    )
    assert allowed.allowed
    denied = authorise_processor_use(
        ProcessorUseRequest(
            processor=_processor(next_review_at=NOW - timedelta(seconds=1)),
            classification=DataClassification.CLIENT_CONFIDENTIAL,
            region="australia",
            purpose="other_purpose",
            real_client_data=True,
            now=NOW,
        )
    )
    assert denied.disposition is DecisionDisposition.DENY
    assert len(denied.reasons) >= 3


def test_candidate_and_synthetic_processor_cannot_receive_real_client_data() -> None:
    candidate = _processor(
        approval_status=ProcessorApprovalStatus.CANDIDATE,
        permitted_classifications=(DataClassification.PUBLIC,),
        dpa_status="pending",
        provider_training_disabled=False,
        deletion_verification_supported=False,
    )
    decision = authorise_processor_use(
        ProcessorUseRequest(
            processor=candidate,
            classification=DataClassification.PUBLIC,
            region="singapore",
            purpose="controlled_model_inference",
            real_client_data=False,
            now=NOW,
        )
    )
    assert decision.disposition is DecisionDisposition.DENY
    synthetic = _processor(synthetic_fixture=True)
    real_data = authorise_processor_use(
        ProcessorUseRequest(
            processor=synthetic,
            classification=DataClassification.CLIENT_CONFIDENTIAL,
            region="singapore",
            purpose="controlled_model_inference",
            real_client_data=True,
            now=NOW,
        )
    )
    assert real_data.disposition is DecisionDisposition.DENY


def test_secret_detection_finds_known_formats_and_nested_paths() -> None:
    assert looks_like_secret("ghp_abcdefghijklmnopqrstuvwxyz123456")
    assert looks_like_secret("-----BEGIN PRIVATE KEY-----")
    assert not looks_like_secret("credential-ref://provider/api-key")
    findings = scan_for_secret_like_values(
        {"safe": "env://SAFE_REFERENCE", "nested": ["ghp_abcdefghijklmnopqrstuvwxyz123456"]}
    )
    assert findings == ("$.nested[0]",)


def test_production_gate_blocks_missing_and_wrong_region_evidence() -> None:
    cell = _cell()
    report = evaluate_production_gate(
        ProductionGateRequest(
            cell=cell,
            evidence=(),
            real_client_data_requested=True,
            evaluated_at=NOW,
        )
    )
    assert report.disposition is DecisionDisposition.DENY
    assert set(report.missing_controls) == set(MANDATORY_REAL_CLIENT_CONTROLS)

    wrong_region = make_current_control_evidence(
        MANDATORY_REAL_CLIENT_CONTROLS,
        environment=RuntimeEnvironment.PRODUCTION,
        region="australia",
        evaluated_at=NOW,
    )
    wrong_report = evaluate_production_gate(
        ProductionGateRequest(
            cell=cell,
            evidence=wrong_region,
            real_client_data_requested=True,
            evaluated_at=NOW,
        )
    )
    assert wrong_report.disposition is DecisionDisposition.DENY
    assert set(wrong_report.failed_or_expired_controls) == set(MANDATORY_REAL_CLIENT_CONTROLS)


def test_complete_technical_evidence_still_requires_founder_approval() -> None:
    cell = _cell()
    evidence = make_current_control_evidence(
        MANDATORY_REAL_CLIENT_CONTROLS,
        environment=RuntimeEnvironment.PRODUCTION,
        region="singapore",
        evaluated_at=NOW,
    )
    report = evaluate_production_gate(
        ProductionGateRequest(
            cell=cell,
            evidence=evidence,
            real_client_data_requested=True,
            evaluated_at=NOW,
        )
    )
    assert report.disposition is DecisionDisposition.ELIGIBLE_FOR_FOUNDER_APPROVAL
    assert report.founder_approval_required


def test_founder_approval_plus_current_controls_satisfies_gate() -> None:
    cell = _cell()
    evidence = make_current_control_evidence(
        MANDATORY_REAL_CLIENT_CONTROLS + ("CTRL-FOUNDER-PRODUCTION-APPROVAL",),
        environment=RuntimeEnvironment.PRODUCTION,
        region="singapore",
        evaluated_at=NOW,
    )
    report = evaluate_production_gate(
        ProductionGateRequest(
            cell=cell,
            evidence=evidence,
            real_client_data_requested=True,
            evaluated_at=NOW,
        )
    )
    assert report.disposition is DecisionDisposition.ALLOW
    assert not report.founder_approval_required


def test_synthetic_request_never_implies_real_client_authorisation() -> None:
    report = evaluate_production_gate(
        ProductionGateRequest(
            cell=_cell(),
            evidence=(),
            real_client_data_requested=False,
            evaluated_at=NOW,
        )
    )
    assert report.disposition is DecisionDisposition.SYNTHETIC_ONLY


def test_expired_or_failed_control_evidence_fails_gate() -> None:
    evidence = list(
        make_current_control_evidence(
            MANDATORY_REAL_CLIENT_CONTROLS,
            environment=RuntimeEnvironment.PRODUCTION,
            region="singapore",
            evaluated_at=NOW,
        )
    )
    evidence[0] = SecurityControlEvidence(
        control_id=evidence[0].control_id,
        status=EvidenceStatus.FAILED,
        environment=RuntimeEnvironment.PRODUCTION,
        region="singapore",
        evidence_refs=("synthetic-test://failed",),
        tested_at=NOW - timedelta(hours=1),
    )
    report = evaluate_production_gate(
        ProductionGateRequest(
            cell=_cell(),
            evidence=tuple(evidence),
            real_client_data_requested=True,
            evaluated_at=NOW,
        )
    )
    assert report.disposition is DecisionDisposition.DENY
    assert evidence[0].control_id in report.failed_or_expired_controls


def test_incident_assessment_escalates_secret_and_cross_tenant_events() -> None:
    assessment = assess_incident(
        IncidentSignal(
            incident_id="INC-001",
            detected_at=NOW,
            suspected_classifications=(DataClassification.CLIENT_CONFIDENTIAL,),
            secret_exposure=True,
            cross_tenant_access=True,
            external_disclosure=True,
            potentially_affected_tenants=2,
        )
    )
    assert assessment.severity is IncidentSeverity.CRITICAL
    assert assessment.founder_notification_required
    assert assessment.client_notification_decision_required
    assert not assessment.autonomous_closure_allowed
    assert "revoke_and_rotate_exposed_credentials" in assessment.mandatory_actions


def test_incident_assessment_keeps_low_event_open_for_human_control() -> None:
    assessment = assess_incident(
        IncidentSignal(incident_id="INC-002", detected_at=NOW)
    )
    assert assessment.severity is IncidentSeverity.LOW
    assert not assessment.autonomous_closure_allowed


def test_security_baseline_builds_expected_scope() -> None:
    root = Path(__file__).resolve().parents[3]
    baseline = build_security_baseline(root)
    assert baseline.data_class_count == 4
    assert baseline.regional_cell_count == 3
    assert baseline.retention_policy_count == 4
    assert baseline.processor_record_count == 0
    assert baseline.processor_fixture_count == 3
    assert baseline.threat_count == 20
    assert baseline.control_count >= 40
    assert baseline.test_case_count >= 35
    assert baseline.incident_playbook_count == 12
    assert baseline.mandatory_real_client_control_count == len(MANDATORY_REAL_CLIENT_CONTROLS)
    assert baseline.real_client_data_enabled is False
    assert baseline.first_managed_region == "singapore"


def test_security_baseline_is_reproducible_and_verified(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[3]
    first = build_security_baseline(root)
    second = build_security_baseline(root)
    assert first == second
    output = write_security_baseline(root)
    verify_security_baseline(root, output)
    committed = json.loads(output.read_text(encoding="utf-8"))
    assert committed["baseline_digest"] == first.baseline_digest

    copied = tmp_path / "repo"
    shutil.copytree(root / "configs", copied / "configs")
    shutil.copytree(root / "security", copied / "security")
    classification_path = copied / "security" / "data-classification.yaml"
    text = classification_path.read_text(encoding="utf-8")
    classification_path.write_text(text.replace("default_log_mode: redacted", "default_log_mode: metadata_only"), encoding="utf-8")
    mutated = build_security_baseline(copied)
    assert mutated.baseline_digest != first.baseline_digest
    with pytest.raises(ValueError, match="stale"):
        verify_security_baseline(copied)


def test_regional_cell_requires_gate_evidence_when_client_data_enabled() -> None:
    with pytest.raises(ValidationError, match="gate evidence"):
        _cell(
            status="production_approved",
            client_data_enabled=True,
            permitted_classifications=(
                DataClassification.PUBLIC,
                DataClassification.INTERNAL,
                DataClassification.CLIENT_CONFIDENTIAL,
            ),
            gate_evidence_digest=None,
        )
