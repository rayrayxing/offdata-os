from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from offdata_core.ai_audit_oracle import (
    ANSWER_KEY_NAME,
    CLIENT_VISIBLE_FILES,
    ORACLE_BASELINE_NAME,
    AIAuditOracleResult,
    EvidenceFinding,
    EvidenceStatus,
    MethodRejection,
    OracleDisposition,
    baseline_document,
    build_ai_audit_oracle,
    ensure_answer_key_isolation,
    grade_ai_audit_oracle,
    serialise_baseline,
    verify_committed_baseline,
    write_oracle_baseline,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "fixtures" / "digital-ai" / "FIXTURE-DAI-001"


def _copy_fixture(tmp_path: Path) -> Path:
    destination = tmp_path / "FIXTURE-DAI-001"
    shutil.copytree(FIXTURE_DIR, destination)
    return destination


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        assert reader.fieldnames is not None
        return reader.fieldnames, rows


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _read_yaml(path: Path) -> dict[str, Any]:
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(parsed, dict)
    return parsed


def test_oracle_builds_from_client_visible_inputs_and_grades_pass() -> None:
    # Requirements: OUT-002, QA-009, MODEL-002
    result = build_ai_audit_oracle(FIXTURE_DIR)
    grade = grade_ai_audit_oracle(result, FIXTURE_DIR / ANSWER_KEY_NAME)
    assert result.fixture_id == "FIXTURE-DAI-001"
    assert result.agent_visible is False
    assert len(result.source_checksums) == len(CLIENT_VISIBLE_FILES) == 14
    assert grade.passed
    assert grade.checks_passed == grade.checks_run
    assert not grade.failures


def test_oracle_does_not_require_answer_key_for_analysis(tmp_path: Path) -> None:
    # Requirements: QA-009, AGENT-002, DATA-008
    fixture = _copy_fixture(tmp_path)
    (fixture / ANSWER_KEY_NAME).unlink()
    result = build_ai_audit_oracle(fixture)
    assert result.primary_pilot_use_case_id == "UC-001"
    with pytest.raises(FileNotFoundError):
        grade_ai_audit_oracle(result, fixture / ANSWER_KEY_NAME)


def test_oracle_is_byte_reproducible_and_committed_baseline_is_current() -> None:
    # Requirements: MODEL-002, MODEL-005, DATA-008
    first = serialise_baseline(baseline_document(FIXTURE_DIR))
    second = serialise_baseline(baseline_document(FIXTURE_DIR))
    assert first == second
    verify_committed_baseline(FIXTURE_DIR)


def test_oracle_baseline_writer_and_stale_detection(tmp_path: Path) -> None:
    # Requirements: MODEL-002, QA-005, DATA-003
    fixture = _copy_fixture(tmp_path)
    destination = write_oracle_baseline(fixture)
    assert destination.name == ORACLE_BASELINE_NAME
    verify_committed_baseline(fixture)
    destination.write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="stale or non-reproducible"):
        verify_committed_baseline(fixture)


def test_quotation_oracle_separates_touch_waiting_and_complexity() -> None:
    # Requirements: MODEL-001, MODEL-005, EVID-005, EVID-008
    quotation = build_ai_audit_oracle(FIXTURE_DIR).quotation
    assert quotation.six_month_volume == 6260
    assert quotation.annualised_volume == 12520
    assert quotation.six_month_touch_hours == 3198.85
    assert quotation.annualised_touch_hours == 6397.70
    assert quotation.simple_and_standard_volume_share_percent == 82.24
    assert quotation.complex_and_engineered_touch_share_percent == 38.45
    assert quotation.leadership_fifty_percent_estimate_supported is False
    assert quotation.elapsed_time_is_automatable_touch_time is False
    engineered = next(item for item in quotation.segments if item.segment == "engineered_project")
    assert engineered.weighted_specialist_wait_hours > 60
    assert engineered.weighted_touch_minutes > 95


def test_customer_service_oracle_blocks_autonomous_chatbot_inference() -> None:
    # Requirements: EVID-005, MODEL-009, AUTH-004
    service = build_ai_audit_oracle(FIXTURE_DIR).customer_service
    assert service.annual_ticket_count == 18420
    assert service.conditional_share_percent == 43
    assert service.low_prohibited_or_unknown_share_percent == 57
    assert service.autonomous_ready_share_percent == 0
    assert service.weighted_specialist_escalation_percent == 26.11
    assert service.weighted_approved_knowledge_coverage_percent == 59.45
    assert service.internal_human_mediated_assistant_only is True


def test_workforce_oracle_quantifies_current_control_and_adoption_conditions() -> None:
    # Requirements: DATA-006, IMPL-003, AGENT-007
    workforce = build_ai_audit_oracle(FIXTURE_DIR).workforce
    assert workforce.respondents == 123
    assert workforce.weighted_public_ai_use_percent == 21.76
    assert workforce.weighted_review_confidence_percent == 33.91
    assert workforce.weighted_training_interest_percent == 79.62
    assert workforce.weighted_job_reduction_concern_percent == 52.34
    assert workforce.weighted_data_leakage_concern_percent == 60.09
    assert workforce.current_control_gap is True


def test_readiness_oracle_uses_process_application_and_untrusted_source_controls() -> None:
    # Requirements: EVID-010, AGENT-007, KNOW-004, MODEL-009
    result = build_ai_audit_oracle(FIXTURE_DIR)
    readiness = result.readiness
    assert readiness.quotation_process_ids == (
        "PROC-001", "PROC-002", "PROC-003", "PROC-004"
    )
    assert readiness.quotation_mean_data_quality_score == 6.25
    assert readiness.inventory_process_data_quality_score == 4.1
    assert readiness.product_master_data_quality_score == 4.7
    assert readiness.controlled_ai_environment_selected is False
    assert readiness.ai_output_review_owner_defined is False
    assert readiness.unapproved_public_ai_asset_ids == ("ASSET-002", "ASSET-010")
    assert readiness.required_foundation_asset_ids == ("ASSET-011", "ASSET-012")
    assert readiness.inventory_production_ready is False

    untrusted = result.untrusted_input
    assert untrusted.source_id == "UNTRUSTED-SRC-001"
    assert untrusted.authority_class == "unverified_marketing"
    assert untrusted.untrusted_input is True
    assert untrusted.suspicious is True
    assert len(untrusted.matched_markers) == 6
    assert untrusted.instruction_content_ignored is True
    assert untrusted.external_action_blocked is True


def test_financial_oracle_recalculates_and_classifies_value() -> None:
    # Requirements: MODEL-001, MODEL-003, MODEL-004, MODEL-006, MODEL-008
    financial = build_ai_audit_oracle(FIXTURE_DIR).financial
    assert financial.base_pilot_cost_sgd == 88000
    assert financial.downside_pilot_cost_sgd == 118000
    assert financial.upside_pilot_cost_sgd == 76000
    assert financial.downside_headroom_sgd == 2000
    assert financial.annual_addressable_capacity_value_sgd == 210000
    assert financial.annual_potential_incremental_gross_margin_sgd == 145000
    assert financial.immediate_cash_releasing_headcount_benefit_sgd == 0
    assert financial.recurring_support_break_even_capacity_redeployment_percent == 17.14
    assert financial.recurring_support_break_even_conversion_uplift_points == 0.5
    assert financial.year_one_pilot_and_support_break_even_conversion_uplift_points == 1.71
    assert financial.invalid_management_claim_detected is True
    assert "cash cost" in financial.classifications
    assert "released capacity" in financial.classifications
    assert "potential incremental margin" in financial.classifications


def test_use_case_oracle_retains_non_ai_comparator_and_bounded_pilot() -> None:
    # Requirements: KNOW-004, KNOW-005, MODEL-004, AUTH-003
    result = build_ai_audit_oracle(FIXTURE_DIR)
    by_id = {item.use_case_id: item for item in result.use_cases}
    assert result.primary_pilot_use_case_id == "UC-001"
    assert result.required_comparator_use_case_id == "UC-008"
    assert by_id["UC-001"].disposition is OracleDisposition.PILOT
    assert by_id["UC-008"].disposition is OracleDisposition.COMPARATOR
    assert by_id["UC-003"].disposition is OracleDisposition.DEFER
    assert by_id["UC-004"].disposition is OracleDisposition.PREPARE
    assert by_id["UC-001"].decision_score == 7.04
    assert by_id["UC-008"].decision_score == 7.385
    assert "UC-003" in result.deferred_use_case_ids
    assert "UC-004" in result.deferred_use_case_ids


def test_oracle_method_stack_rejections_uncertainty_and_specialist_review_are_complete() -> None:
    # Requirements: KNOW-003, KNOW-004, KNOW-005, EVID-006, AUTH-006
    result = build_ai_audit_oracle(FIXTURE_DIR)
    assert len(result.required_method_stack) == 8
    assert result.required_method_stack["pilot_and_scale_evidence"] == "DAI-11"
    assert len(result.method_rejections) == 4
    assert any("maturity" in item.candidate.casefold() for item in result.method_rejections)
    assert len(result.required_specialist_reviews) == 4
    assert len(result.uncertainty_statements) == 6
    assert len(result.alternative_recommendation_rules) == 3


def test_oracle_preserves_evidence_status_provenance_and_limits() -> None:
    # Requirements: DATA-006, DATA-007, EVID-003, EVID-005
    findings = {item.finding_id: item for item in build_ai_audit_oracle(FIXTURE_DIR).evidence_findings}
    assert set(findings) == {f"EXP-EVID-{index:03d}" for index in range(1, 7)}
    assert findings["EXP-EVID-001"].epistemic_status is EvidenceStatus.REASONED_SYNTHESIS
    assert findings["EXP-EVID-001"].source_ids == ("CLIENT-SRC-002", "CLIENT-DATA-001")
    assert len(findings["EXP-EVID-001"].row_ids) == 24
    assert findings["EXP-EVID-002"].epistemic_status is EvidenceStatus.ESTABLISHED_FACT
    assert all(item.limitations for item in findings.values())


def test_oracle_risk_authority_and_stop_gates_are_complete() -> None:
    # Requirements: AUTH-003, AUTH-004, AUTH-007, QA-004
    result = build_ai_audit_oracle(FIXTURE_DIR)
    assert result.risks.critical_inherent_risks == ("RISK-001", "RISK-002")
    assert "RISK-003" in result.risks.mandatory_human_authority_risks
    assert "RISK-004" in result.risks.mandatory_human_authority_risks
    assert result.risks.founder_acceptance_required is True
    assert len(result.stop_conditions) == 6
    assert len(result.founder_escalations) == 3
    assert len(result.mandatory_quality_defect_ids) == 10
    assert len(result.prohibited_conclusions) == 6


def test_over_budget_primary_pilot_mutation_switches_to_bounded_alternative(tmp_path: Path) -> None:
    # Requirements: MODEL-004, QA-009, TEST-005
    fixture = _copy_fixture(tmp_path)
    path = fixture / "use-case-inventory.csv"
    fieldnames, rows = _read_csv(path)
    next(row for row in rows if row["use_case_id"] == "UC-001")[
        "estimated_pilot_cost_sgd"
    ] = "130000"
    _write_csv(path, fieldnames, rows)
    result = build_ai_audit_oracle(fixture)
    by_id = {item.use_case_id: item for item in result.use_cases}
    assert by_id["UC-001"].within_commitment is False
    assert by_id["UC-001"].disposition is OracleDisposition.DEFER
    assert result.primary_pilot_use_case_id == "UC-005"


def test_financial_mutation_is_detected_by_independent_grader(tmp_path: Path) -> None:
    # Requirements: MODEL-006, QA-003, QA-005, TEST-005
    fixture = _copy_fixture(tmp_path)
    path = fixture / "financial-baseline.csv"
    fieldnames, rows = _read_csv(path)
    next(row for row in rows if row["line_id"] == "FIN-013")["base_value"] = "100000"
    _write_csv(path, fieldnames, rows)
    result = build_ai_audit_oracle(fixture)
    grade = grade_ai_audit_oracle(result, fixture / ANSWER_KEY_NAME)
    assert grade.passed is False
    assert "financial:immediate_cash_releasing_headcount_benefit_sgd" in grade.failures


def test_answer_key_and_oracle_are_blocked_from_agent_context() -> None:
    # Requirements: AGENT-002, AGENT-004, QA-009, SEC-002
    ensure_answer_key_isolation(context_paths=CLIENT_VISIBLE_FILES)
    with pytest.raises(ValueError, match="Restricted oracle material"):
        ensure_answer_key_isolation(
            context_paths=("company-and-mandate.yaml", ANSWER_KEY_NAME)
        )
    with pytest.raises(ValueError, match="Restricted oracle material"):
        ensure_answer_key_isolation(context_paths=(ORACLE_BASELINE_NAME,))


def test_missing_or_malformed_fixture_inputs_fail_closed(tmp_path: Path) -> None:
    # Requirements: EVID-002, MODEL-009, QA-004
    fixture = _copy_fixture(tmp_path)
    (fixture / "quotation-activity.csv").unlink()
    with pytest.raises(ValueError, match="Missing client-visible fixture input"):
        build_ai_audit_oracle(fixture)

    fixture = _copy_fixture(tmp_path / "second")
    company = _read_yaml(fixture / "company-and-mandate.yaml")
    mandate = company["mandate"]
    assert isinstance(mandate, dict)
    mandate.pop("constraints")
    (fixture / "company-and-mandate.yaml").write_text(
        yaml.safe_dump(company, sort_keys=False), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="constraints"):
        build_ai_audit_oracle(fixture)


def test_oracle_contract_validators_reject_unbounded_records() -> None:
    # Requirements: AGENT-005, QA-009
    with pytest.raises(ValidationError, match="Rejected method requires"):
        MethodRejection(candidate="Invalid", reasons=())
    with pytest.raises(ValidationError, match="at least one source"):
        EvidenceFinding(
            finding_id="EXP-EVID-999",
            conclusion="Unsupported",
            epistemic_status=EvidenceStatus.EVIDENCE_GAP,
            source_ids=(),
        )
    document = baseline_document(FIXTURE_DIR)["oracle"]
    assert isinstance(document, dict)
    document["agent_visible"] = True
    with pytest.raises(ValidationError, match="must never be agent-visible"):
        AIAuditOracleResult(**document)


def test_invalid_answer_key_shape_fails_closed(tmp_path: Path) -> None:
    # Requirements: QA-009, MODEL-006
    fixture = _copy_fixture(tmp_path)
    expected = _read_yaml(fixture / ANSWER_KEY_NAME)
    expected["prohibited_conclusions"] = "not-a-list"
    path = fixture / ANSWER_KEY_NAME
    path.write_text(yaml.safe_dump(expected, sort_keys=False), encoding="utf-8")
    result = build_ai_audit_oracle(fixture)
    with pytest.raises(ValueError, match="list of strings"):
        grade_ai_audit_oracle(result, path)


def test_restricted_baseline_document_contains_grade_and_checksums() -> None:
    # Requirements: DATA-003, DATA-008, QA-009
    document = baseline_document(FIXTURE_DIR)
    assert document["classification"] == "restricted_evaluation_oracle"
    assert document["agent_visible"] is False
    answer_key_checksum = document["answer_key_checksum"]
    assert isinstance(answer_key_checksum, str)
    assert len(answer_key_checksum) == 64
    grade = document["grade"]
    assert isinstance(grade, dict)
    assert grade["passed"] is True
    encoded = serialise_baseline(document)
    decoded = json.loads(encoded)
    assert decoded == document
