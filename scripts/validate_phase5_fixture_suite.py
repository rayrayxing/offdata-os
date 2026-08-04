#!/usr/bin/env python3
"""Validate the complete chat-first Phase 5 additional-fixture release."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

from offdata_core.primary_fixtures import (
    ADDITIONAL_FIXTURE_PATHS,
    EXPECTED_RESULTS_NAME,
    FIXTURE_BASELINE_NAME,
    SUITE_BASELINE_NAME,
    build_phase5_fixture_suite,
    ensure_fixture_evaluation_isolation,
    grade_phase5_fixture_suite,
    verify_committed_phase5_fixture_baselines,
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


def main() -> int:
    root = repository_root()
    fixtures_root = root / "fixtures"
    root_manifest = read_yaml(fixtures_root / "manifest.yaml")
    primary = root_manifest.get("primary_engagements")
    if not isinstance(primary, list):
        raise ValueError("Fixture root manifest primary_engagements must be a list.")
    by_id = {
        str(item.get("id")): item
        for item in primary
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    required_built = {"FIXTURE-DAI-001", *ADDITIONAL_FIXTURE_PATHS}
    if not required_built <= set(by_id):
        raise ValueError("Fixture root manifest is missing a completed primary fixture.")
    for fixture_id in required_built:
        record = by_id[fixture_id]
        if record.get("status") != "built_foundation":
            raise ValueError(f"Fixture {fixture_id} is not marked built_foundation.")
        path = record.get("path")
        if not isinstance(path, str) or not (fixtures_root / path).is_dir():
            raise ValueError(f"Fixture {fixture_id} has an invalid manifest path.")

    suite = build_phase5_fixture_suite(fixtures_root)
    grades = grade_phase5_fixture_suite(suite, fixtures_root)
    failures = [failure for grade in grades for failure in grade.failures]
    if failures:
        raise ValueError(f"Phase 5 fixture grades failed: {failures}")
    verify_committed_phase5_fixture_baselines(fixtures_root)

    global_source_ids: list[str] = []
    for summary in suite.fixtures:
        fixture_dir = fixtures_root / ADDITIONAL_FIXTURE_PATHS[summary.fixture_id]
        manifest = read_yaml(fixture_dir / "manifest.yaml")["fixture"]
        if not isinstance(manifest, dict):
            raise ValueError("Malformed fixture manifest.")
        visible = manifest.get("agent_visible_files")
        restricted = manifest.get("restricted_files")
        if not isinstance(visible, list) or not isinstance(restricted, list):
            raise ValueError("Fixture visibility lists are malformed.")
        ensure_fixture_evaluation_isolation(str(item) for item in visible)
        if EXPECTED_RESULTS_NAME not in restricted or FIXTURE_BASELINE_NAME not in restricted:
            raise ValueError("Fixture restricted evaluation records are not declared.")
        expected = read_yaml(fixture_dir / EXPECTED_RESULTS_NAME)
        if expected.get("agent_visible") is not False:
            raise ValueError("Fixture answer key must declare agent_visible=false.")
        baseline = read_json(fixture_dir / FIXTURE_BASELINE_NAME)
        if baseline.get("agent_visible") is not False:
            raise ValueError("Fixture baseline must declare agent_visible=false.")
        global_source_ids.extend(summary.source_ids)
        if len(summary.governing_uncertainties) < 4:
            raise ValueError("Fixture has insufficient governing uncertainties.")
        if not summary.alternative_action_ids:
            raise ValueError("Fixture has no credible alternative action set.")
        if not summary.implementation_initiative_ids or not summary.benefit_ids:
            raise ValueError("Fixture implementation or benefit records are incomplete.")
    if len(global_source_ids) != len(set(global_source_ids)):
        raise ValueError("Source IDs collide across the additional fixtures.")

    suite_baseline = read_json(fixtures_root / SUITE_BASELINE_NAME)
    if suite_baseline.get("agent_visible") is not False:
        raise ValueError("Fixture-suite baseline must declare agent_visible=false.")
    registry = read_json(root / "requirements/test-registry.json")
    planned = registry.get("planned_tests")
    implemented = registry.get("implemented_tests")
    if not isinstance(planned, list) or not isinstance(implemented, list):
        raise ValueError("Requirement test registry is malformed.")
    if any(isinstance(item, dict) and item.get("test_id") == "IT-FIXTURE-001" for item in planned):
        raise ValueError("The fixture integration test remains incorrectly planned.")
    phase5_nodes = [
        item
        for item in implemented
        if isinstance(item, dict)
        and str(item.get("node_id", "")).startswith(
            "packages/offdata-core/tests/test_primary_fixtures.py::"
        )
    ]
    if len(phase5_nodes) != 22:
        raise ValueError("Phase 5 implemented-test mapping set is incomplete.")
    if not any(
        isinstance(item, dict) and item.get("test_id") == "E2E-PRIMARY-FIXTURES-001"
        for item in planned
    ):
        raise ValueError("The full thirteen-fixture end-to-end test was incorrectly retired.")

    print("PHASE 5 ADDITIONAL ENGAGEMENT FIXTURE VALIDATION PASSED")
    checks = (
        f"additional_fixtures={len(suite.fixtures)}",
        f"built_primary_fixtures={len(required_built)}",
        f"agent_visible_inputs={sum(len(item.source_checksums) for item in suite.fixtures)}",
        f"source_records={len(global_source_ids)}",
        f"calculated_metrics={sum(len(item.metrics) for item in suite.fixtures)}",
        f"recommendation_actions={sum(len(item.recommendation_action_ids) for item in suite.fixtures)}",
        f"credible_alternative_actions={sum(len(item.alternative_action_ids) for item in suite.fixtures)}",
        f"method_selections={sum(len(item.selected_method_ids) for item in suite.fixtures)}",
        f"method_rejections={sum(len(item.rejected_method_ids) for item in suite.fixtures)}",
        f"grade_checks={sum(item.checks_run for item in grades)}",
        f"phase5_implemented_test_nodes={len(phase5_nodes)}",
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
