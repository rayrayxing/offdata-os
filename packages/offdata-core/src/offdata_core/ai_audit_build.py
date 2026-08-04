"""Build the restricted Northstar AI-audit analytical oracle."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, Sequence

from .ai_audit_decision import _financial_analysis, _risk_analysis, _use_case_assessments
from .ai_audit_io import _checksums, _read_csv, _read_yaml
from .ai_audit_models import (
    ALTERNATIVE_RECOMMENDATION_RULES,
    AIAuditOracleResult,
    CONTROL_METRICS,
    EvidenceFinding,
    EvidenceStatus,
    FIXTURE_ID,
    FounderEscalation,
    MANDATORY_QUALITY_DEFECT_IDS,
    METHOD_REJECTIONS,
    MethodRejection,
    ORACLE_VERSION,
    OUTCOME_METRICS,
    PRIMARY_PILOT_SCOPE,
    PROHIBITED_CONCLUSIONS,
    REQUIRED_FOUNDATIONS,
    REQUIRED_METHOD_STACK,
    SPECIALIST_REVIEW_REQUIREMENTS,
    STOP_CONDITIONS,
    SUPPORTING_PROBLEM_ARCHETYPES,
    UNCERTAINTY_STATEMENTS,
    OracleDisposition,
)
from .ai_audit_operational import (
    _customer_service_analysis,
    _quotation_analysis,
    _readiness_analysis,
    _untrusted_input_analysis,
    _workforce_analysis,
)


def _evidence_findings(
    quotation_rows: Sequence[Mapping[str, str]],
) -> tuple[EvidenceFinding, ...]:
    quote_ids = tuple(row["row_id"] for row in quotation_rows)
    return (
        EvidenceFinding(
            finding_id="EXP-EVID-001",
            conclusion=(
                "Sales leadership's fifty-percent administration estimate is not supported by "
                "the available operational evidence."
            ),
            epistemic_status=EvidenceStatus.REASONED_SYNTHESIS,
            source_ids=("CLIENT-SRC-002", "CLIENT-DATA-001"),
            row_ids=quote_ids,
            limitations=(
                "The dataset is aggregated and does not measure total seller capacity.",
                "Some informal specialist touch time is excluded.",
            ),
        ),
        EvidenceFinding(
            finding_id="EXP-EVID-002",
            conclusion="Quotation elapsed time is not equivalent to automatable touch time.",
            epistemic_status=EvidenceStatus.ESTABLISHED_FACT,
            source_ids=("CLIENT-DATA-001",),
            row_ids=quote_ids,
            limitations=("Some waiting causes cannot be distinguished from timestamps.",),
        ),
        EvidenceFinding(
            finding_id="EXP-EVID-003",
            conclusion=(
                "A high share of repeatable customer-service categories does not establish safe "
                "autonomous response."
            ),
            epistemic_status=EvidenceStatus.REASONED_SYNTHESIS,
            source_ids=("CLIENT-DATA-002", "CLIENT-SRC-003", "CLIENT-DATA-006"),
            limitations=("Resolution codes are missing for part of the underlying population.",),
        ),
        EvidenceFinding(
            finding_id="EXP-EVID-004",
            conclusion=(
                "Inventory forecasting is not ready for production pilot without demand-label and "
                "substitution remediation and a back-test."
            ),
            epistemic_status=EvidenceStatus.REASONED_SYNTHESIS,
            source_ids=("CLIENT-SRC-004", "CLIENT-DATA-003"),
            limitations=("No controlled Northstar back-test is available.",),
        ),
        EvidenceFinding(
            finding_id="EXP-EVID-005",
            conclusion=(
                "Unapproved public AI use is a current control gap independent of the selected pilot."
            ),
            epistemic_status=EvidenceStatus.REASONED_SYNTHESIS,
            source_ids=("CLIENT-DATA-004", "CLIENT-SRC-004", "CLIENT-DATA-006"),
            limitations=("Survey use is self-reported and may be understated.",),
        ),
        EvidenceFinding(
            finding_id="EXP-EVID-006",
            conclusion=(
                "The management financial case improperly treats released capacity and possible "
                "margin as immediate cash benefit."
            ),
            epistemic_status=EvidenceStatus.REASONED_SYNTHESIS,
            source_ids=("CLIENT-SRC-005", "CLIENT-DATA-005"),
            limitations=("Conversion uplift remains an unvalidated assumption.",),
        ),
    )


def build_ai_audit_oracle(fixture_dir: Path) -> AIAuditOracleResult:
    """Build the restricted analytical oracle from client-visible inputs only."""

    fixture_dir = fixture_dir.resolve()
    checksums, input_digest = _checksums(fixture_dir)
    company = _read_yaml(fixture_dir / "company-and-mandate.yaml")
    manifest = _read_yaml(fixture_dir / "source-manifest.yaml")
    if manifest.get("fixture_id") != FIXTURE_ID or manifest.get("real_client_data") is not False:
        raise ValueError("The oracle accepts only the governed synthetic Northstar fixture.")
    mandate = company.get("mandate")
    if not isinstance(mandate, dict):
        raise ValueError("Fixture mandate is missing or malformed.")
    constraints = mandate.get("constraints")
    if not isinstance(constraints, dict):
        raise ValueError("Fixture mandate constraints are missing or malformed.")
    maximum_commitment = float(constraints["maximum_initial_cash_commitment_sgd"])

    quotation_rows = _read_csv(fixture_dir / "quotation-activity.csv")
    customer_service_rows = _read_csv(fixture_dir / "customer-service-summary.csv")
    process_rows = _read_csv(fixture_dir / "process-inventory.csv")
    asset_rows = _read_csv(fixture_dir / "application-data-inventory.csv")
    use_case_rows = _read_csv(fixture_dir / "use-case-inventory.csv")
    workforce_rows = _read_csv(fixture_dir / "workforce-survey.csv")
    financial_rows = _read_csv(fixture_dir / "financial-baseline.csv")
    risk_rows = _read_csv(fixture_dir / "risk-and-controls.csv")
    assessments, primary = _use_case_assessments(use_case_rows, maximum_commitment)
    deferred = tuple(
        item.use_case_id
        for item in assessments
        if item.disposition in {OracleDisposition.DEFER, OracleDisposition.PREPARE}
    )
    source_documents = manifest.get("source_documents")
    if not isinstance(source_documents, list):
        raise ValueError("Source manifest source_documents must be a list.")
    retrieval_dates = {
        str(source["retrieval_date"])
        for source in source_documents
        if isinstance(source, dict) and "retrieval_date" in source
    }
    as_of_date = max(retrieval_dates) if retrieval_dates else "2026-08-04"

    return AIAuditOracleResult(
        fixture_id=FIXTURE_ID,
        oracle_version=ORACLE_VERSION,
        as_of_date=as_of_date,
        input_digest=input_digest,
        source_checksums=checksums,
        agent_visible=False,
        decision_owner=str(mandate["decision_owner"]),
        governing_decision=str(mandate["governing_decision"]),
        maximum_initial_cash_commitment_sgd=maximum_commitment,
        counterfactual=str(mandate["counterfactual"]),
        mandatory_problem_archetypes=(
            "AI opportunity portfolio and prioritisation",
            "Readiness and control assessment",
            "Pilot and causal learning design",
        ),
        supporting_problem_archetypes=SUPPORTING_PROBLEM_ARCHETYPES,
        quotation=_quotation_analysis(quotation_rows),
        customer_service=_customer_service_analysis(customer_service_rows),
        workforce=_workforce_analysis(workforce_rows),
        readiness=_readiness_analysis(process_rows, asset_rows),
        untrusted_input=_untrusted_input_analysis(
            manifest, (fixture_dir / "untrusted-input.txt").read_text(encoding="utf-8")
        ),
        financial=_financial_analysis(financial_rows, maximum_commitment),
        risks=_risk_analysis(risk_rows),
        use_cases=assessments,
        primary_pilot_use_case_id=primary,
        required_comparator_use_case_id="UC-008",
        primary_pilot_scope=PRIMARY_PILOT_SCOPE,
        required_foundations=REQUIRED_FOUNDATIONS,
        deferred_use_case_ids=deferred,
        required_method_stack=dict(REQUIRED_METHOD_STACK),
        method_rejections=tuple(
            MethodRejection(candidate=candidate, reasons=reasons)
            for candidate, reasons in METHOD_REJECTIONS
        ),
        required_specialist_reviews=SPECIALIST_REVIEW_REQUIREMENTS,
        acceptable_secondary_use_case_ids=("UC-002", "UC-005"),
        alternative_recommendation_rules=ALTERNATIVE_RECOMMENDATION_RULES,
        uncertainty_statements=UNCERTAINTY_STATEMENTS,
        evidence_findings=_evidence_findings(quotation_rows),
        outcome_metrics=OUTCOME_METRICS,
        control_metrics=CONTROL_METRICS,
        stop_conditions=STOP_CONDITIONS,
        founder_escalations=(
            FounderEscalation(
                escalation_id="ESC-DAI-001",
                decision="Approve recommended pilot scope and maximum cash commitment",
                required_classes=("material", "commercial"),
            ),
            FounderEscalation(
                escalation_id="ESC-DAI-002",
                decision="Approve named vendor selection and external pricing representation",
                required_classes=("external", "commercial"),
            ),
            FounderEscalation(
                escalation_id="ESC-DAI-003",
                decision=(
                    "Accept any residual high or critical data, security, technical or workforce risk"
                ),
                required_classes=("material", "irreversible"),
            ),
        ),
        mandatory_quality_defect_ids=MANDATORY_QUALITY_DEFECT_IDS,
        prohibited_conclusions=PROHIBITED_CONCLUSIONS,
    )
