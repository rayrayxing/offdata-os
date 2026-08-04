"""Financial, risk and use-case decisions for the Northstar AI-audit oracle."""

from __future__ import annotations

from typing import Mapping, Sequence

from .ai_audit_io import _float, _round
from .ai_audit_models import (
    FinancialAnalysis,
    OracleDisposition,
    PRIMARY_PILOT_SCOPE,
    RiskAnalysis,
    UseCaseAssessment,
)


def _financial_analysis(
    rows: Sequence[Mapping[str, str]], maximum_commitment: float
) -> FinancialAnalysis:
    by_id = {row["line_id"]: row for row in rows}
    required = {f"FIN-{index:03d}" for index in range(1, 17)}
    if set(by_id) != required:
        raise ValueError("Financial baseline must contain FIN-001 through FIN-016 exactly once.")
    pilot_rows = [by_id[f"FIN-{index:03d}"] for index in range(1, 6)]
    base_cost = sum(_float(row, "base_value") for row in pilot_rows)
    downside_cost = sum(_float(row, "downside_value") for row in pilot_rows)
    upside_cost = sum(_float(row, "upside_value") for row in pilot_rows)
    capacity = _float(by_id["FIN-008"], "base_value")
    eligible_margin = _float(by_id["FIN-009"], "base_value")
    margin = _float(by_id["FIN-011"], "base_value")
    recurring = _float(by_id["FIN-012"], "base_value")
    headcount = _float(by_id["FIN-013"], "base_value")
    claimed = _float(by_id["FIN-016"], "base_value")
    classification_labels = {
        "cash_cost": "cash cost",
        "released_capacity": "released capacity",
        "incremental_margin": "potential incremental margin",
        "cost_avoidance": "cost avoidance",
        "risk_avoidance": "risk avoidance",
        "cash_releasing": "cash releasing",
        "valuation_rate": "valuation rate",
        "revenue_pool": "revenue pool",
        "unvalidated_assumption": "unvalidated assumption",
    }
    classifications = tuple(
        sorted(
            {
                classification_labels.get(
                    row["cash_classification"], row["cash_classification"].replace("_", " ")
                )
                for row in rows
                if row["cash_classification"] != "mixed_and_invalid"
            }
        )
    )
    return FinancialAnalysis(
        base_pilot_cost_sgd=_round(base_cost),
        downside_pilot_cost_sgd=_round(downside_cost),
        upside_pilot_cost_sgd=_round(upside_cost),
        maximum_commitment_sgd=_round(maximum_commitment),
        downside_headroom_sgd=_round(maximum_commitment - downside_cost),
        annual_addressable_capacity_value_sgd=_round(capacity),
        annual_potential_incremental_gross_margin_sgd=_round(margin),
        annual_platform_and_support_cost_sgd=_round(recurring),
        immediate_cash_releasing_headcount_benefit_sgd=_round(headcount),
        recurring_support_break_even_capacity_redeployment_percent=_round(
            recurring / capacity * 100
        ),
        recurring_support_break_even_conversion_uplift_points=_round(
            recurring / eligible_margin * 100
        ),
        year_one_pilot_and_support_break_even_conversion_uplift_points=_round(
            (base_cost + recurring) / eligible_margin * 100
        ),
        invalid_management_claim_detected=(
            by_id["FIN-016"]["cash_classification"] == "mixed_and_invalid"
            and claimed == capacity + margin
        ),
        management_claimed_year_1_value_sgd=_round(claimed),
        classifications=classifications,
        prohibited_conclusion="The pilot will save SGD 355000 in cash during year one.",
    )


def _risk_analysis(rows: Sequence[Mapping[str, str]]) -> RiskAnalysis:
    critical = tuple(
        row["risk_id"] for row in rows if row["inherent_severity"] == "critical"
    )
    high_residual = tuple(
        row["risk_id"]
        for row in rows
        if row["residual_severity"] in {"high", "critical"}
    )
    weak = tuple(
        row["risk_id"]
        for row in rows
        if row["control_design_status"] in {"absent", "weak"}
    )
    authority = tuple(
        row["risk_id"]
        for row in rows
        if any(
            phrase in row["required_pilot_control"].casefold()
            for phrase in (
                "mandatory specialist approval",
                "no autonomous pricing decision",
                "human release remains mandatory",
            )
        )
    )
    return RiskAnalysis(
        critical_inherent_risks=critical,
        high_or_critical_residual_risks=high_residual,
        absent_or_weak_control_risks=weak,
        mandatory_human_authority_risks=authority,
        founder_acceptance_required=True,
    )


def _use_case_score(row: Mapping[str, str]) -> float:
    return (
        _float(row, "addressable_value_score") * 0.35
        + _float(row, "feasibility_score") * 0.25
        + _float(row, "data_readiness_score") * 0.20
        + (10 - _float(row, "risk_score")) * 0.20
    )


def _use_case_assessments(
    rows: Sequence[Mapping[str, str]], maximum_commitment: float
) -> tuple[tuple[UseCaseAssessment, ...], str]:
    assessments: list[UseCaseAssessment] = []
    for row in rows:
        use_case_id = row["use_case_id"]
        cost = _float(row, "estimated_pilot_cost_sgd")
        within_commitment = cost <= maximum_commitment
        initial = row["recommended_initial_status"]
        reasons: list[str] = [row["notes"]]
        controls: tuple[str, ...] = ()
        if use_case_id == "UC-008":
            disposition = OracleDisposition.COMPARATOR
            reasons.append("Retain the non-AI process alternative as comparator and prerequisite.")
        elif use_case_id == "UC-003":
            disposition = OracleDisposition.DEFER
            reasons.append("External response, authentication and technical-judgement risk are excessive.")
        elif use_case_id == "UC-004":
            disposition = OracleDisposition.PREPARE
            reasons.append("Demand labels, substitutions and lost-sales treatment require remediation and back-test.")
        elif use_case_id in {"UC-006", "UC-007"}:
            disposition = OracleDisposition.FOUNDATION
        elif initial in {"secondary_candidate", "alternative_pilot"}:
            disposition = OracleDisposition.SECONDARY
        else:
            disposition = OracleDisposition.PILOT
        if not within_commitment:
            disposition = OracleDisposition.DEFER
            reasons.append("Estimated pilot cost exceeds the approved commitment ceiling.")
        if use_case_id == "UC-001":
            controls = PRIMARY_PILOT_SCOPE[3:]
        elif use_case_id == "UC-002":
            controls = (
                "internal human-mediated use only",
                "approved current knowledge only",
                "no autonomous external response",
            )
        assessments.append(
            UseCaseAssessment(
                use_case_id=use_case_id,
                name=row["use_case_name"],
                decision_score=_round(_use_case_score(row), 3),
                estimated_pilot_cost_sgd=_round(cost),
                within_commitment=within_commitment,
                disposition=disposition,
                reasons=tuple(reasons),
                required_controls=controls,
            )
        )
    viable_ai = [
        item
        for item in assessments
        if item.disposition in {OracleDisposition.PILOT, OracleDisposition.SECONDARY}
        and item.use_case_id != "UC-008"
    ]
    if not viable_ai:
        raise ValueError("No bounded AI pilot remains within the commitment ceiling.")
    primary = max(viable_ai, key=lambda item: (item.decision_score, item.use_case_id)).use_case_id
    # UC-001 is preferred when viable because the process evidence supports a bounded scope and
    # the comparator is available. A mutation that makes it non-viable allows the score frontier.
    uc001 = next(item for item in assessments if item.use_case_id == "UC-001")
    if uc001.disposition is OracleDisposition.PILOT:
        primary = "UC-001"
    return tuple(sorted(assessments, key=lambda item: item.use_case_id)), primary
