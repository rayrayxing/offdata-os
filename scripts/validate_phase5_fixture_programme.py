#!/usr/bin/env python3
"""Validate the complete chat-first Phase 5 additional fixture programme."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

from offdata_core.fixture_programme import (
    NORTHSTAR_FIXTURE_ID,
    build_fixture_programme,
    verify_committed_programme,
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict[str, Any]:
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return parsed


def main() -> int:
    root = repository_root()
    seed = root / "fixtures" / "additional-primary-fixture-seeds.yaml"
    baseline = root / "fixtures" / "additional-primary-fixtures.json"
    manifest_path = root / "fixtures" / "manifest.yaml"
    programme = build_fixture_programme(seed)
    verify_committed_programme(seed, baseline)

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("Fixture manifest must be an object.")
    primary = manifest.get("primary_engagements")
    if not isinstance(primary, list):
        raise ValueError("Fixture manifest primary_engagements must be a list.")
    expected_ids = {
        item.get("id")
        for item in primary
        if isinstance(item, dict) and item.get("id") != NORTHSTAR_FIXTURE_ID
    }
    actual_ids = {item.fixture_id for item in programme.fixtures}
    if actual_ids != expected_ids:
        raise ValueError(
            f"Additional fixture scope differs from governed manifest: missing={sorted(expected_ids - actual_ids)}, extra={sorted(actual_ids - expected_ids)}"
        )

    planned = read_json(root / "requirements/planned-test-mappings.json")
    for test_id in ("E2E-PRIMARY-FIXTURES-001", "E2E-COMPOUND-FIXTURES-001"):
        if test_id not in planned:
            raise ValueError(f"Required end-to-end boundary was lost: {test_id}")

    for fixture in programme.fixtures:
        record_types = {item.record_type for item in fixture.evidence_records}
        if record_types != {"source_document", "interview_transcript"}:
            raise ValueError(f"{fixture.fixture_id} lacks source or interview evidence.")
        if {item["decision_class"] for item in fixture.expected_founder_interruptions} != {
            "D3",
            "D4",
        }:
            raise ValueError(f"{fixture.fixture_id} does not preserve Founder gates.")
        if not all(item["recognition_rule"] for item in fixture.benefit_records):
            raise ValueError(f"{fixture.fixture_id} has an ungoverned benefit record.")

    baseline_document = read_json(baseline)
    if baseline_document.get("agent_visible") is not True:
        raise ValueError("Synthetic fixture programme must be available to evaluation agents.")
    if baseline_document.get("classification") != "synthetic_golden_fixture_programme":
        raise ValueError("Fixture programme classification is incorrect.")

    print("PHASE 5 ADDITIONAL ENGAGEMENT FIXTURE VALIDATION PASSED")
    checks = (
        f"primary_fixtures={len(programme.fixtures)}",
        f"engagement_types={len({item.engagement_type for item in programme.fixtures})}",
        f"evidence_records={sum(len(item.evidence_records) for item in programme.fixtures)}",
        f"structured_datasets={sum(len(item.structured_data) for item in programme.fixtures)}",
        f"deliberate_data_defects={sum(len(item.data_quality_defects) for item in programme.fixtures)}",
        f"method_stacks={sum(len(item.acceptable_method_stacks) for item in programme.fixtures)}",
        f"method_traps={sum(len(item.rejected_method_traps) for item in programme.fixtures)}",
        f"calculation_expectations={sum(len(item.expected_calculations) for item in programme.fixtures)}",
        f"implementation_records={sum(len(item.implementation_records) for item in programme.fixtures)}",
        f"benefit_records={sum(len(item.benefit_records) for item in programme.fixtures)}",
        "planned_primary_e2e_boundary=preserved",
        "planned_compound_e2e_boundary=preserved",
    )
    for check in checks:
        print(f"- {check}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, OSError, TypeError, ValueError) as exc:
        print(f"PHASE 5 ADDITIONAL ENGAGEMENT FIXTURE VALIDATION FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
