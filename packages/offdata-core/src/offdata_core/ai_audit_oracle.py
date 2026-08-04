"""Restricted grading and baseline facade for the Northstar AI-audit oracle."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .ai_audit_build import build_ai_audit_oracle
from .ai_audit_io import _read_yaml, _sha256
from .ai_audit_models import (
    ANSWER_KEY_NAME,
    CLIENT_VISIBLE_FILES,
    ORACLE_BASELINE_NAME,
    AIAuditOracleResult,
    EvidenceFinding,
    EvidenceStatus,
    FinancialAnalysis,
    MethodRejection,
    OracleDisposition,
    OracleGrade,
    QuotationAnalysis,
    ReadinessAnalysis,
    RiskAnalysis,
    SegmentAnalysis,
    SourceChecksum,
    UntrustedInputAnalysis,
    UseCaseAssessment,
    WorkforceAnalysis,
)

__all__ = [
    "ANSWER_KEY_NAME",
    "CLIENT_VISIBLE_FILES",
    "ORACLE_BASELINE_NAME",
    "AIAuditOracleResult",
    "EvidenceFinding",
    "EvidenceStatus",
    "FinancialAnalysis",
    "MethodRejection",
    "OracleDisposition",
    "OracleGrade",
    "QuotationAnalysis",
    "ReadinessAnalysis",
    "RiskAnalysis",
    "SegmentAnalysis",
    "SourceChecksum",
    "UntrustedInputAnalysis",
    "UseCaseAssessment",
    "WorkforceAnalysis",
    "baseline_document",
    "build_ai_audit_oracle",
    "ensure_answer_key_isolation",
    "grade_ai_audit_oracle",
    "serialise_baseline",
    "verify_committed_baseline",
    "write_oracle_baseline",
]


class _CheckCollector:
    def __init__(self) -> None:
        self.count = 0
        self.failures: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        self.count += 1
        if not condition:
            self.failures.append(message)


def _expected_set(value: Any, *, key: str) -> set[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"Expected a list of strings at {key}.")
    return set(value)


def _counterfactual_key(value: str) -> str:
    """Normalise only the documented mandate/answer-key wording discrepancy."""

    return " ".join(
        value.casefold().replace("non-ai ", "").replace("improvements", "improvement").split()
    )


def grade_ai_audit_oracle(
    result: AIAuditOracleResult, expected_results_path: Path
) -> OracleGrade:
    """Independently compare a generated result with the restricted answer key."""

    expected = _read_yaml(expected_results_path)
    checks = _CheckCollector()
    frame = expected["mandatory_decision_frame"]
    checks.check(result.fixture_id == expected["fixture_id"], "fixture_id")
    checks.check(result.agent_visible is False, "oracle_must_be_restricted")
    checks.check(result.decision_owner == frame["decision_owner"], "decision_owner")
    checks.check(
        result.maximum_initial_cash_commitment_sgd
        == float(frame["maximum_initial_cash_commitment_sgd"]),
        "maximum_commitment",
    )
    expected_counterfactual = str(frame["counterfactual"])
    checks.check(
        _counterfactual_key(result.counterfactual)
        == _counterfactual_key(expected_counterfactual),
        "counterfactual",
    )

    archetypes = expected["mandatory_problem_archetypes"]
    checks.check(
        set(result.mandatory_problem_archetypes) == set(archetypes["primary"]),
        "problem_archetypes",
    )
    checks.check(
        set(result.supporting_problem_archetypes)
        == set(archetypes["supporting_any_of"]),
        "supporting_problem_archetypes",
    )
    expected_findings = {
        item["finding_id"]: item for item in expected["mandatory_evidence_findings"]
    }
    actual_findings = {item.finding_id: item for item in result.evidence_findings}
    checks.check(set(actual_findings) == set(expected_findings), "evidence_finding_ids")
    for finding_id, expected_finding in expected_findings.items():
        actual = actual_findings.get(finding_id)
        checks.check(actual is not None, f"{finding_id}:present")
        if actual is not None:
            checks.check(
                set(actual.source_ids) == set(expected_finding["required_sources"]),
                f"{finding_id}:sources",
            )
            checks.check(bool(actual.limitations), f"{finding_id}:limitations")

    expected_methods = expected["expected_method_selection"]["required_roles"]
    checks.check(set(result.required_method_stack) == set(expected_methods), "method_roles")
    for role, value in expected_methods.items():
        checks.check(
            result.required_method_stack.get(role) in set(value["acceptable_method_ids"]),
            f"method:{role}",
        )
    expected_rejections = {
        item["candidate"]: tuple(str(reason).casefold() for reason in item["reason_contains"])
        for item in expected["expected_method_selection"]["required_rejections"]
    }
    actual_rejections = {item.candidate: item for item in result.method_rejections}
    checks.check(set(actual_rejections) == set(expected_rejections), "method_rejections")
    for candidate, reason_fragments in expected_rejections.items():
        actual = actual_rejections.get(candidate)
        if actual is not None:
            reason_text = " ".join(actual.reasons).casefold()
            for fragment in reason_fragments:
                checks.check(fragment in reason_text, f"method_rejection:{candidate}:{fragment}")

    recommendation = expected["preferred_recommendation"]
    checks.check(
        result.primary_pilot_use_case_id
        == recommendation["primary_pilot"]["use_case_id"],
        "primary_pilot",
    )
    checks.check(
        set(result.primary_pilot_scope)
        == _expected_set(
            recommendation["primary_pilot"]["mandatory_scope"],
            key="primary_pilot.mandatory_scope",
        ),
        "primary_pilot_scope",
    )
    checks.check(
        set(result.required_foundations)
        == _expected_set(
            recommendation["required_parallel_foundation"],
            key="required_parallel_foundation",
        ),
        "required_foundations",
    )
    checks.check(
        set(recommendation["deferred_options"])
        <= set(result.deferred_use_case_ids),
        "deferred_options",
    )
    checks.check(result.required_comparator_use_case_id == "UC-008", "non_ai_comparator")
    expected_secondary = {
        item["use_case_id"] for item in recommendation["acceptable_secondary_options"]
    }
    checks.check(
        set(result.acceptable_secondary_use_case_ids) <= expected_secondary,
        "acceptable_secondary_options",
    )
    checks.check(
        set(result.alternative_recommendation_rules)
        == _expected_set(
            expected["acceptable_alternative_recommendation_rules"],
            key="acceptable_alternative_recommendation_rules",
        ),
        "alternative_recommendation_rules",
    )
    checks.check(bool(result.required_specialist_reviews), "specialist_reviews")
    checks.check(bool(result.uncertainty_statements), "uncertainty_statements")

    scale_gate = expected["mandatory_scale_gate"]
    checks.check(
        set(result.outcome_metrics)
        == _expected_set(scale_gate["outcome_metrics"], key="outcome_metrics"),
        "outcome_metrics",
    )
    checks.check(
        set(result.control_metrics)
        == _expected_set(scale_gate["control_metrics"], key="control_metrics"),
        "control_metrics",
    )
    checks.check(
        set(result.stop_conditions)
        == _expected_set(
            scale_gate["mandatory_stop_conditions"], key="mandatory_stop_conditions"
        ),
        "stop_conditions",
    )

    expected_financial = expected["financial_oracle"]
    numeric_checks = {
        "base_pilot_cost_sgd": result.financial.base_pilot_cost_sgd,
        "downside_pilot_cost_sgd": result.financial.downside_pilot_cost_sgd,
        "maximum_approved_commitment_sgd": result.financial.maximum_commitment_sgd,
        "annual_addressable_capacity_value_sgd": (
            result.financial.annual_addressable_capacity_value_sgd
        ),
        "annual_potential_incremental_gross_margin_sgd": (
            result.financial.annual_potential_incremental_gross_margin_sgd
        ),
        "annual_platform_and_support_cost_sgd": (
            result.financial.annual_platform_and_support_cost_sgd
        ),
        "immediate_cash_releasing_headcount_benefit_sgd": (
            result.financial.immediate_cash_releasing_headcount_benefit_sgd
        ),
    }
    for key, actual in numeric_checks.items():
        checks.check(actual == float(expected_financial[key]), f"financial:{key}")
    checks.check(
        set(expected_financial["required_classifications"])
        <= set(result.financial.classifications),
        "financial_classifications",
    )
    checks.check(result.financial.invalid_management_claim_detected, "invalid_value_claim")
    checks.check(
        result.financial.prohibited_conclusion
        == expected_financial["prohibited_financial_conclusion"],
        "prohibited_financial_conclusion",
    )

    expected_escalations = {
        item["escalation_id"]: item for item in expected["required_founder_escalations"]
    }
    actual_escalations = {item.escalation_id: item for item in result.founder_escalations}
    checks.check(set(actual_escalations) == set(expected_escalations), "escalation_ids")
    for escalation_id, expected_escalation in expected_escalations.items():
        actual = actual_escalations.get(escalation_id)
        if actual is not None:
            checks.check(
                set(actual.required_classes) == set(expected_escalation["required_classes"]),
                f"{escalation_id}:classes",
            )

    expected_defects = {
        str(key).split(":", maxsplit=1)[0]
        for item in expected["mandatory_quality_defects_to_detect"]
        for key in (item.keys() if isinstance(item, dict) else [item])
    }
    checks.check(
        set(result.mandatory_quality_defect_ids) == expected_defects,
        "quality_defect_ids",
    )
    checks.check(
        set(result.prohibited_conclusions)
        == _expected_set(expected["prohibited_conclusions"], key="prohibited_conclusions"),
        "prohibited_conclusions",
    )
    failures = tuple(checks.failures)
    return OracleGrade(
        passed=not failures,
        checks_run=checks.count,
        checks_passed=checks.count - len(failures),
        failures=failures,
    )


def baseline_document(fixture_dir: Path) -> dict[str, Any]:
    """Create the deterministic restricted baseline document."""

    result = build_ai_audit_oracle(fixture_dir)
    expected_path = fixture_dir / ANSWER_KEY_NAME
    expected = _read_yaml(expected_path)
    expected_counterfactual = str(expected["mandatory_decision_frame"]["counterfactual"])
    source_discrepancies: tuple[str, ...] = ()
    if result.counterfactual != expected_counterfactual:
        source_discrepancies = (
            "The client-visible mandate says 'Continue process and data improvement without an AI "
            "pilot'; the restricted answer key says 'Continue non-AI process and data improvements "
            "without an AI pilot'. The mandate wording is preserved and the equivalent intent is "
            "graded through a documented normalisation.",
        )
    grade = grade_ai_audit_oracle(result, expected_path)
    if not grade.passed:
        raise ValueError(f"Analytical oracle does not match answer key: {grade.failures}")
    return {
        "classification": "restricted_evaluation_oracle",
        "agent_visible": False,
        "answer_key_checksum": _sha256(expected_path),
        "source_discrepancies": source_discrepancies,
        "oracle": result.model_dump(mode="json"),
        "grade": grade.model_dump(mode="json"),
    }


def serialise_baseline(document: Mapping[str, Any]) -> str:
    return json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_oracle_baseline(fixture_dir: Path) -> Path:
    destination = fixture_dir / ORACLE_BASELINE_NAME
    destination.write_text(serialise_baseline(baseline_document(fixture_dir)), encoding="utf-8")
    return destination


def verify_committed_baseline(fixture_dir: Path) -> None:
    destination = fixture_dir / ORACLE_BASELINE_NAME
    if not destination.is_file():
        raise ValueError(f"Missing committed analytical oracle: {ORACLE_BASELINE_NAME}")
    expected = serialise_baseline(baseline_document(fixture_dir))
    actual = destination.read_text(encoding="utf-8")
    if actual != expected:
        raise ValueError("Committed analytical oracle is stale or non-reproducible.")


def ensure_answer_key_isolation(
    *,
    context_paths: Iterable[str],
    oracle_paths: Iterable[str] = (ANSWER_KEY_NAME, ORACLE_BASELINE_NAME),
) -> None:
    """Block restricted oracle material from any normal agent context."""

    restricted = {Path(path).name for path in oracle_paths}
    leaked = sorted(path for path in context_paths if Path(path).name in restricted)
    if leaked:
        raise ValueError(f"Restricted oracle material in agent context: {leaked}")
