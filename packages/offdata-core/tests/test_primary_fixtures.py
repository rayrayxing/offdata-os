from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from offdata_core.primary_fixtures import (
    ADDITIONAL_FIXTURE_PATHS,
    EXPECTED_RESULTS_NAME,
    FIXTURE_BASELINE_NAME,
    SUITE_BASELINE_NAME,
    FixtureExpectedResults,
    FixtureManifest,
    build_fixture_summary,
    build_phase5_fixture_suite,
    ensure_fixture_evaluation_isolation,
    fixture_baseline_document,
    grade_fixture_summary,
    grade_phase5_fixture_suite,
    serialise_fixture_baseline,
    suite_baseline_document,
    suite_digest,
    verify_committed_phase5_fixture_baselines,
    write_phase5_fixture_baselines,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURES_ROOT = REPO_ROOT / "fixtures"
STRATEGY_DIR = FIXTURES_ROOT / ADDITIONAL_FIXTURE_PATHS["FIXTURE-STRAT-001"]
COST_DIR = FIXTURES_ROOT / ADDITIONAL_FIXTURE_PATHS["FIXTURE-COST-001"]


def _read_yaml(path: Path) -> dict[str, Any]:
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(parsed, dict)
    return parsed


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        assert reader.fieldnames is not None
        return reader.fieldnames, rows


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _copy_fixtures(tmp_path: Path) -> Path:
    destination = tmp_path / "fixtures"
    shutil.copytree(FIXTURES_ROOT, destination)
    return destination


def _summary(path: Path):  # type: ignore[no-untyped-def]
    return build_fixture_summary(path)


def test_phase5_suite_builds_and_independent_grades_pass() -> None:
    # Requirements: QA-009, TEST-002, TEST-005
    suite = build_phase5_fixture_suite(FIXTURES_ROOT)
    grades = grade_phase5_fixture_suite(suite, FIXTURES_ROOT)
    assert suite.agent_visible is False
    assert {item.fixture_id for item in suite.fixtures} == set(ADDITIONAL_FIXTURE_PATHS)
    assert all(item.passed for item in grades)
    assert sum(item.checks_run for item in grades) == 144


def test_phase5_baselines_are_byte_reproducible_and_current() -> None:
    # Requirements: DATA-003, DATA-008, MODEL-002, TEST-005
    first = serialise_fixture_baseline(suite_baseline_document(FIXTURES_ROOT))
    second = serialise_fixture_baseline(suite_baseline_document(FIXTURES_ROOT))
    assert first == second
    verify_committed_phase5_fixture_baselines(FIXTURES_ROOT)


def test_phase5_baseline_writer_and_stale_detection(tmp_path: Path) -> None:
    # Requirements: DATA-003, QA-005, TEST-005
    fixtures_root = _copy_fixtures(tmp_path)
    destinations = write_phase5_fixture_baselines(fixtures_root)
    assert {item.name for item in destinations} == {FIXTURE_BASELINE_NAME, SUITE_BASELINE_NAME}
    verify_committed_phase5_fixture_baselines(fixtures_root)
    (fixtures_root / SUITE_BASELINE_NAME).write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="stale or non-reproducible"):
        verify_committed_phase5_fixture_baselines(fixtures_root)


def test_fixture_manifests_are_synthetic_complete_and_restricted() -> None:
    # Requirements: QA-009, DATA-001, DATA-005, DELIV-001
    for fixture_dir in (STRATEGY_DIR, COST_DIR):
        manifest = FixtureManifest(**_read_yaml(fixture_dir / "manifest.yaml")).fixture
        assert manifest.synthetic_only is True
        assert len(manifest.agent_visible_files) == 14
        assert set(manifest.expected_output_formats) == {"pptx", "docx", "xlsx", "pdf", "svg", "html"}
        assert EXPECTED_RESULTS_NAME in manifest.restricted_files
        assert FIXTURE_BASELINE_NAME in manifest.restricted_files
        assert not set(manifest.agent_visible_files) & set(manifest.restricted_files)


def test_source_manifests_resolve_and_are_globally_unique() -> None:
    # Requirements: KNOW-001, KNOW-002, EVID-002, EVID-003
    all_ids: list[str] = []
    for fixture_dir in (STRATEGY_DIR, COST_DIR):
        source_manifest = _read_yaml(fixture_dir / "source-manifest.yaml")
        sources = source_manifest["source_documents"]
        assert isinstance(sources, list)
        assert len(sources) == 11
        for source in sources:
            assert isinstance(source, dict)
            all_ids.append(str(source["source_id"]))
            path = str(source["object_reference"]).split("#", maxsplit=1)[0]
            assert (fixture_dir / path).is_file()
            assert source["scope"]
            assert source["limitations"]
            assert source["usage_rights"] == "internal_synthetic_regression_only"
            assert source["agent_visible"] is True
        assert sum(bool(item["untrusted_input"]) for item in sources) == 1
    assert len(all_ids) == len(set(all_ids))


def test_strategy_fixture_reconciles_portfolio_economics_and_ceiling() -> None:
    # Requirements: MODEL-001, MODEL-004, MODEL-005, OUT-002
    summary = _summary(STRATEGY_DIR)
    metrics = {item.metric_id: item.value for item in summary.metrics}
    assert metrics["CALC-STRAT-001"] == 148
    assert metrics["CALC-STRAT-004"] == 69
    assert metrics["CALC-STRAT-008"] == 18
    assert metrics["CALC-STRAT-009"] == 54
    assert metrics["CALC-STRAT-010"] == 8
    assert summary.recommendation_action_ids == (
        "ACT-STR-001",
        "ACT-STR-003",
        "ACT-STR-006",
        "ACT-STR-009",
        "ACT-STR-012",
    )


def test_strategy_fixture_rejects_growth_and_management_preference_traps() -> None:
    # Requirements: KNOW-004, KNOW-005, EVID-005, TEST-004
    summary = _summary(STRATEGY_DIR)
    assert "ACT-STR-005" in summary.rejected_action_ids
    assert "ACT-STR-008" in summary.rejected_action_ids
    assert "ACT-STR-011" in summary.rejected_action_ids
    assert "STRAT-FIND-002" in summary.evidence_signal_ids
    assert "STRAT-FIND-003" in summary.evidence_signal_ids
    assert summary.selected_method_ids == (
        "STR-01",
        "STR-07",
        "STR-09",
        "STR-10",
        "STR-13",
        "STR-14",
    )
    assert "GENERIC-PORTFOLIO-MATRIX" in summary.rejected_method_ids


def test_cost_fixture_reconciles_cash_capacity_overlap_and_payback() -> None:
    # Requirements: MODEL-001, MODEL-003, MODEL-005, IMPL-004
    summary = _summary(COST_DIR)
    metrics = {item.metric_id: item.value for item in summary.metrics}
    assert metrics["CALC-COST-001"] == 37090000
    assert metrics["CALC-COST-002"] == 4350000
    assert metrics["CALC-COST-006"] == 24418.8
    assert metrics["CALC-COST-009"] == 1270000
    assert metrics["CALC-COST-010"] == 120000
    assert metrics["CALC-COST-011"] == 810000
    assert metrics["CALC-COST-013"] == 18000
    assert metrics["CALC-COST-016"] == 0
    assert metrics["CALC-COST-015"] == pytest.approx(16.296296)


def test_cost_fixture_blocks_blanket_headcount_and_capacity_as_cash() -> None:
    # Requirements: KNOW-005, MODEL-003, IMPL-004, TEST-004
    summary = _summary(COST_DIR)
    assert "ACT-COST-004" in summary.rejected_action_ids
    assert "ACT-COST-006" in summary.rejected_action_ids
    assert "COST-FIND-003" in summary.evidence_signal_ids
    assert "COST-FIND-005" in summary.evidence_signal_ids
    assert "COST-FIND-006" in summary.evidence_signal_ids
    assert summary.alternative_action_ids == (
        "ACT-COST-001",
        "ACT-COST-002",
        "ACT-COST-005",
    )


def test_implementation_and_benefits_trace_to_recommendations() -> None:
    # Requirements: IMPL-001, IMPL-002, IMPL-005, IMPL-006
    for fixture_dir in (STRATEGY_DIR, COST_DIR):
        summary = _summary(fixture_dir)
        roadmap = _read_yaml(fixture_dir / "implementation-roadmap.yaml")["initiatives"]
        benefits = _read_yaml(fixture_dir / "benefit-plan.yaml")["benefits"]
        assert isinstance(roadmap, list)
        assert isinstance(benefits, list)
        assert {item["recommendation_action_id"] for item in roadmap} == set(summary.recommendation_action_ids)
        initiative_ids = {item["initiative_id"] for item in roadmap}
        assert all(set(item["initiative_ids"]) <= initiative_ids for item in benefits)
        assert all(item["owner"] and item["verification_threshold"] for item in benefits)


def test_untrusted_fixture_inputs_fail_closed() -> None:
    # Requirements: EVID-010, AGENT-004, AGENT-007, AUTH-004
    for fixture_dir in (STRATEGY_DIR, COST_DIR):
        assessment = _summary(fixture_dir).untrusted_input
        assert assessment.suspicious
        assert len(assessment.matched_markers) >= 3
        assert assessment.instruction_content_ignored
        assert assessment.external_action_blocked


def test_expected_results_and_baselines_are_isolated_from_normal_context() -> None:
    # Requirements: AGENT-002, AGENT-004, QA-009, SEC-002
    ensure_fixture_evaluation_isolation(("manifest.yaml", "interviews.md"))
    for restricted in (
        EXPECTED_RESULTS_NAME,
        FIXTURE_BASELINE_NAME,
        SUITE_BASELINE_NAME,
        "oracle-baseline.json",
        "deliverable-semantic-baseline.json",
    ):
        with pytest.raises(ValueError, match="Restricted fixture evaluation material"):
            ensure_fixture_evaluation_isolation((restricted,))


def test_strategy_input_mutation_changes_portfolio_and_fails_grade(tmp_path: Path) -> None:
    # Requirements: MODEL-004, QA-003, QA-005, TEST-005
    fixtures_root = _copy_fixtures(tmp_path)
    fixture_dir = fixtures_root / ADDITIONAL_FIXTURE_PATHS["FIXTURE-STRAT-001"]
    path = fixture_dir / "capital-options.csv"
    fieldnames, rows = _read_csv(path)
    next(row for row in rows if row["option_id"] == "ACT-STR-006")["downside_npv_sgd_m"] = "-40"
    _write_csv(path, fieldnames, rows)
    with pytest.raises(ValueError, match="does not trace"):
        build_fixture_summary(fixture_dir)
    with pytest.raises(ValueError, match="does not trace|stale or non-reproducible"):
        verify_committed_phase5_fixture_baselines(fixtures_root)


def test_cost_input_mutation_is_detected_by_independent_grade(tmp_path: Path) -> None:
    # Requirements: MODEL-006, QA-003, QA-005, TEST-005
    fixtures_root = _copy_fixtures(tmp_path)
    fixture_dir = fixtures_root / ADDITIONAL_FIXTURE_PATHS["FIXTURE-COST-001"]
    path = fixture_dir / "initiative-options.csv"
    fieldnames, rows = _read_csv(path)
    next(row for row in rows if row["option_id"] == "ACT-COST-002")["gross_cash_savings_sgd"] = "620000"
    _write_csv(path, fieldnames, rows)
    summary = build_fixture_summary(fixture_dir)
    grade = grade_fixture_summary(summary, fixture_dir / EXPECTED_RESULTS_NAME)
    assert grade.passed is False
    assert "CALC-COST-009:value" in grade.failures


def test_missing_source_file_fails_closed(tmp_path: Path) -> None:
    # Requirements: EVID-002, QA-004, QA-009
    fixtures_root = _copy_fixtures(tmp_path)
    fixture_dir = fixtures_root / ADDITIONAL_FIXTURE_PATHS["FIXTURE-COST-001"]
    (fixture_dir / "service-performance.csv").unlink()
    with pytest.raises(ValueError, match="Missing agent-visible fixture file"):
        build_fixture_summary(fixture_dir)


def test_unknown_implementation_reference_fails_closed(tmp_path: Path) -> None:
    # Requirements: IMPL-001, IMPL-002, QA-004
    fixtures_root = _copy_fixtures(tmp_path)
    fixture_dir = fixtures_root / ADDITIONAL_FIXTURE_PATHS["FIXTURE-STRAT-001"]
    roadmap = _read_yaml(fixture_dir / "implementation-roadmap.yaml")
    initiatives = roadmap["initiatives"]
    assert isinstance(initiatives, list)
    initiatives[0]["recommendation_action_id"] = "ACT-STR-999"
    (fixture_dir / "implementation-roadmap.yaml").write_text(
        yaml.safe_dump(roadmap, sort_keys=False), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="does not trace"):
        build_fixture_summary(fixture_dir)


def test_invalid_manifest_cannot_expose_answer_key() -> None:
    # Requirements: DATA-005, AGENT-002, QA-009
    payload = _read_yaml(STRATEGY_DIR / "manifest.yaml")
    fixture = payload["fixture"]
    assert isinstance(fixture, dict)
    fixture["agent_visible_files"].append(EXPECTED_RESULTS_NAME)
    with pytest.raises(ValidationError, match="Restricted fixture files are agent-visible"):
        FixtureManifest(**payload)


def test_expected_results_contract_rejects_agent_visibility() -> None:
    # Requirements: AGENT-002, QA-009
    payload = _read_yaml(COST_DIR / EXPECTED_RESULTS_NAME)
    payload["agent_visible"] = True
    with pytest.raises(ValidationError, match="agent_visible=false"):
        FixtureExpectedResults(**payload)


def test_suite_digest_changes_when_fixture_inputs_change(tmp_path: Path) -> None:
    # Requirements: DATA-003, DATA-008, TEST-005
    original = suite_digest(build_phase5_fixture_suite(FIXTURES_ROOT))
    fixtures_root = _copy_fixtures(tmp_path)
    fixture_dir = fixtures_root / ADDITIONAL_FIXTURE_PATHS["FIXTURE-COST-001"]
    interviews = fixture_dir / "interviews.md"
    interviews.write_text(interviews.read_text(encoding="utf-8") + "\nSynthetic addendum.\n", encoding="utf-8")
    changed = suite_digest(build_phase5_fixture_suite(fixtures_root))
    assert changed != original


def test_additional_fixtures_are_analytically_distinct() -> None:
    # Requirements: TEST-002, KNOW-004, KNOW-006
    strategy = _summary(STRATEGY_DIR)
    cost = _summary(COST_DIR)
    assert strategy.engagement_type != cost.engagement_type
    assert set(strategy.selected_method_ids).isdisjoint(cost.selected_method_ids)
    assert set(strategy.source_ids).isdisjoint(cost.source_ids)
    assert set(strategy.recommendation_action_ids).isdisjoint(cost.recommendation_action_ids)
    assert strategy.random_seed != cost.random_seed


def test_root_fixture_manifest_uses_canonical_ids_and_preserves_aliases() -> None:
    # Requirements: KNOW-002, QA-009, TEST-002
    root_manifest = _read_yaml(FIXTURES_ROOT / "manifest.yaml")
    primary = root_manifest["primary_engagements"]
    assert isinstance(primary, list)
    by_id = {item["id"]: item for item in primary}
    assert len(by_id) == 13
    assert by_id["FIXTURE-DAI-001"]["status"] == "built_foundation"
    assert by_id["FIXTURE-STRAT-001"]["status"] == "built_foundation"
    assert by_id["FIXTURE-COST-001"]["status"] == "built_foundation"
    assert "FIXTURE-STRATEGY-001" in by_id["FIXTURE-STRAT-001"]["aliases"]
    assert "FIXTURE-WORKFORCE-001" in by_id["FIXTURE-WF-001"]["aliases"]
    assert "FIXTURE-CARVEOUT-001" in by_id["FIXTURE-CARVE-001"]["aliases"]
    assert "FIXTURE-BENEFITS-001" in by_id["FIXTURE-BEN-001"]["aliases"]


def test_per_fixture_baseline_contains_grade_and_expected_checksum() -> None:
    # Requirements: DATA-003, DATA-008, QA-009
    for fixture_dir in (STRATEGY_DIR, COST_DIR):
        document = fixture_baseline_document(fixture_dir)
        assert document["classification"] == "restricted_evaluation_primary_fixture"
        assert document["agent_visible"] is False
        assert len(document["expected_results_sha256"]) == 64
        assert document["grade"]["passed"] is True
        committed = json.loads((fixture_dir / FIXTURE_BASELINE_NAME).read_text(encoding="utf-8"))
        assert committed == document
