#!/usr/bin/env python3
"""Validate the complete chat-first Phase 7 security and regionalisation release."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from offdata_core.security_regionalisation import (
    MANDATORY_REAL_CLIENT_CONTROLS,
    DataClassification,
    DecisionDisposition,
    ProductionGateRequest,
    RegionalCell,
    build_security_baseline,
    evaluate_production_gate,
    verify_security_baseline,
)


def _object(path: Path) -> dict[str, Any]:
    value: Any
    if path.suffix in {".yaml", ".yml"}:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    else:
        value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected object: {path}")
    return value


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    security = root / "security"
    baseline_path = security / "security-regionalisation-baseline.json"
    verify_security_baseline(root, baseline_path)
    baseline = build_security_baseline(root)

    expected_counts = {
        "data_class_count": 4,
        "regional_cell_count": 3,
        "retention_policy_count": 4,
        "processor_record_count": 0,
        "processor_fixture_count": 3,
        "threat_count": 20,
        "control_count": 48,
        "test_case_count": 36,
        "incident_playbook_count": 12,
        "mandatory_real_client_control_count": 18,
    }
    for field, expected in expected_counts.items():
        actual = getattr(baseline, field)
        if actual != expected:
            raise ValueError(f"Unexpected {field}: {actual} != {expected}")
    if baseline.real_client_data_enabled:
        raise ValueError("Phase 7 must not enable real client data.")
    if baseline.first_managed_region != "singapore":
        raise ValueError("The first managed region must remain Singapore.")

    classification_doc = _object(security / "data-classification.yaml")
    classes = classification_doc.get("classes", [])
    if {item["classification"] for item in classes} != {
        item.value for item in DataClassification
    }:
        raise ValueError("Classification catalogue is incomplete.")
    for item in classes:
        if item["classification"] in {"client_confidential", "highly_restricted"}:
            if item["raw_payload_logging_allowed"] or item["provider_training_allowed"]:
                raise ValueError("Restricted data handling is too permissive.")

    cell_doc = _object(security / "regional-cells.yaml")
    cells = cell_doc.get("cells", [])
    production_cells = [item for item in cells if item["environment"] == "production"]
    if len(production_cells) != 1 or production_cells[0]["region"] != "singapore":
        raise ValueError("Exactly one planned Singapore production cell is required.")
    if production_cells[0]["client_data_enabled"]:
        raise ValueError("The planned production cell must remain synthetic-only.")

    processor_register = _object(security / "provider-processor-register.yaml")
    if processor_register.get("processors") != []:
        raise ValueError("No external processor is approved for real client data in Phase 7.")
    if processor_register.get("real_client_data_processor_approval") != "none":
        raise ValueError("Processor register must state that no real-client processor is approved.")

    controls = _object(security / "security-control-catalogue.yaml").get("controls", [])
    control_ids = {item["control_id"] for item in controls}
    if set(MANDATORY_REAL_CLIENT_CONTROLS) - control_ids:
        raise ValueError("Mandatory real-client controls are missing.")
    mandatory = {
        item["control_id"]
        for item in controls
        if item.get("mandatory_for_real_client_data")
    }
    if mandatory != set(MANDATORY_REAL_CLIENT_CONTROLS):
        raise ValueError("Mandatory control flags do not match the deterministic gate.")

    tests = _object(security / "security-test-catalogue.yaml").get("tests", [])
    test_ids = {item["test_id"] for item in tests}
    expected_deferred = {
        "IT-ENV-SEPARATION-001",
        "SEC-ENCRYPTION-001",
        "SEC-REGION-ISOLATION-001",
        "IT-BACKUP-RESTORE-001",
        "SEC-SUPPLY-CHAIN-001",
        "IT-OBSERVABILITY-001",
        "IT-RETENTION-001",
        "IT-ROLLBACK-001",
        "FA-PRODUCTION-GATE-001",
    }
    if not expected_deferred.issubset(test_ids):
        raise ValueError("Security test catalogue is missing required integration gates.")

    completed = _object(
        root / "requirements" / "completed-planned-tests-phase7.json"
    ).get("completed_test_ids")
    if completed != ["UT-PROCESSOR-REGISTER-001"]:
        raise ValueError("Phase 7 completed planned-test register is not exact.")
    planned = _object(root / "requirements" / "planned-test-mappings.json")
    for test_id in expected_deferred:
        if test_id not in planned:
            raise ValueError(f"Deferred integration test must remain planned: {test_id}")

    now = datetime(2026, 8, 5, 4, 0, tzinfo=timezone.utc)
    cell_data = production_cells[0]
    cell = RegionalCell.model_validate(cell_data)
    blocked = evaluate_production_gate(
        ProductionGateRequest(
            cell=cell,
            evidence=(),
            real_client_data_requested=True,
            evaluated_at=now,
        )
    )
    if blocked.disposition is not DecisionDisposition.DENY:
        raise ValueError("Empty evidence must block real-client production.")
    if set(blocked.missing_controls) != set(MANDATORY_REAL_CLIENT_CONTROLS):
        raise ValueError("Production gate missing-control report is incomplete.")

    print("PHASE 7 SECURITY AND REGIONALISATION VALIDATION PASSED")
    for item in (
        f"data_classes={baseline.data_class_count}",
        f"regional_cells={baseline.regional_cell_count}",
        f"retention_policies={baseline.retention_policy_count}",
        f"processor_records={baseline.processor_record_count}",
        f"processor_fixtures={baseline.processor_fixture_count}",
        f"threats={baseline.threat_count}",
        f"controls={baseline.control_count}",
        f"security_tests={baseline.test_case_count}",
        f"incident_playbooks={baseline.incident_playbook_count}",
        f"mandatory_real_client_controls={baseline.mandatory_real_client_control_count}",
        "first_managed_region=singapore",
        "real_client_data_enabled=false",
        "production_gate_default=deny",
        "founder_approval_boundary=preserved",
    ):
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, OSError, TypeError, ValueError) as exc:
        print(f"PHASE 7 SECURITY AND REGIONALISATION VALIDATION FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
