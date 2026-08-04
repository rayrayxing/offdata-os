#!/usr/bin/env python3
"""Validate the complete chat-first Phase 3 AI-audit analytical oracle."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from offdata_core.ai_audit_oracle import (
    ANSWER_KEY_NAME,
    CLIENT_VISIBLE_FILES,
    ORACLE_BASELINE_NAME,
    build_ai_audit_oracle,
    ensure_answer_key_isolation,
    grade_ai_audit_oracle,
    verify_committed_baseline,
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_yaml(path: Path) -> dict[str, Any]:
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"Expected YAML object: {path}")
    return parsed


def read_json(path: Path) -> dict[str, Any]:
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return parsed


def csv_row_count(path: Path) -> int:
    with path.open(encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def main() -> int:
    root = repository_root()
    fixture = root / "fixtures" / "digital-ai" / "FIXTURE-DAI-001"
    ensure_answer_key_isolation(context_paths=CLIENT_VISIBLE_FILES)
    if ANSWER_KEY_NAME in CLIENT_VISIBLE_FILES or ORACLE_BASELINE_NAME in CLIENT_VISIBLE_FILES:
        raise ValueError("Restricted oracle files are present in the client-visible allowlist.")

    expected = read_yaml(fixture / ANSWER_KEY_NAME)
    if expected.get("agent_visible") is not False:
        raise ValueError("Restricted answer key must declare agent_visible=false.")
    baseline = read_json(fixture / ORACLE_BASELINE_NAME)
    if baseline.get("agent_visible") is not False:
        raise ValueError("Restricted oracle baseline must declare agent_visible=false.")

    manifest = read_yaml(fixture / "source-manifest.yaml")
    source_documents = manifest.get("source_documents")
    if not isinstance(source_documents, list):
        raise ValueError("Source manifest source_documents must be a list.")
    source_ids = [
        source.get("source_id") for source in source_documents if isinstance(source, dict)
    ]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("Source manifest IDs are not unique.")
    untrusted = next(
        (
            source
            for source in source_documents
            if isinstance(source, dict) and source.get("source_id") == "UNTRUSTED-SRC-001"
        ),
        None,
    )
    if not isinstance(untrusted, dict) or untrusted.get("untrusted_input") is not True:
        raise ValueError("The adversarial source is not deterministically marked untrusted.")

    result = build_ai_audit_oracle(fixture)
    grade = grade_ai_audit_oracle(result, fixture / ANSWER_KEY_NAME)
    if not grade.passed:
        raise ValueError(f"Oracle grade failed: {grade.failures}")
    verify_committed_baseline(fixture)

    if result.primary_pilot_use_case_id != "UC-001":
        raise ValueError("Expected bounded quotation pilot is not the primary recommendation.")
    if result.required_comparator_use_case_id != "UC-008":
        raise ValueError("The non-AI quotation comparator was lost.")
    if result.quotation.six_month_volume != 6260:
        raise ValueError("Quotation activity no longer reconciles to 6,260 records.")
    if result.customer_service.annual_ticket_count != 18420:
        raise ValueError("Customer-service activity no longer reconciles to 18,420 tickets.")
    if result.workforce.respondents != 123:
        raise ValueError("Workforce survey no longer reconciles to 123 respondents.")
    if result.financial.base_pilot_cost_sgd != 88000:
        raise ValueError("Base pilot cost no longer recalculates to SGD 88,000.")
    if result.financial.immediate_cash_releasing_headcount_benefit_sgd != 0:
        raise ValueError("The oracle improperly recognises immediate headcount cash benefit.")
    if not result.untrusted_input.suspicious or not result.untrusted_input.external_action_blocked:
        raise ValueError("The fixture prompt-injection control did not fail closed.")

    completed = read_json(root / "requirements/completed-planned-tests-phase3.json").get(
        "completed_test_ids"
    )
    if not isinstance(completed, list) or len(completed) < 6:
        raise ValueError("Phase 3 completed planned-test register is incomplete.")

    row_counts = {
        "quotation_rows": csv_row_count(fixture / "quotation-activity.csv"),
        "customer_service_rows": csv_row_count(fixture / "customer-service-summary.csv"),
        "process_rows": csv_row_count(fixture / "process-inventory.csv"),
        "asset_rows": csv_row_count(fixture / "application-data-inventory.csv"),
        "use_cases": csv_row_count(fixture / "use-case-inventory.csv"),
        "workforce_segments": csv_row_count(fixture / "workforce-survey.csv"),
        "financial_lines": csv_row_count(fixture / "financial-baseline.csv"),
        "risks": csv_row_count(fixture / "risk-and-controls.csv"),
    }
    print("PHASE 3 AI-AUDIT ANALYTICAL ORACLE VALIDATION PASSED")
    checks = (
        f"client_visible_inputs={len(CLIENT_VISIBLE_FILES)}",
        f"source_documents={len(source_documents)}",
        *(f"{name}={value}" for name, value in row_counts.items()),
        f"evidence_findings={len(result.evidence_findings)}",
        f"method_roles={len(result.required_method_stack)}",
        f"method_rejections={len(result.method_rejections)}",
        f"oracle_grade_checks={grade.checks_run}",
        f"completed_planned_tests={len(completed)}",
    )
    for check in checks:
        print(f"- {check}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, OSError, TypeError, ValueError) as exc:
        print(f"PHASE 3 AI-AUDIT ANALYTICAL ORACLE VALIDATION FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
