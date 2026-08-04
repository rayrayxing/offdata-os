from __future__ import annotations

import csv
import shutil
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from offdata_core.fixture_suite import (
    ExpectedResults,
    PrimaryFixture,
    ensure_restricted_fixture_isolation,
    fixture_suite_document,
    validate_primary_fixture,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
STRATEGY = REPO_ROOT / "fixtures/strategy/FIXTURE-STRAT-001"
COST = REPO_ROOT / "fixtures/cost-productivity/FIXTURE-COST-001"


def _copy_fixture(source: Path, tmp_path: Path) -> Path:
    destination = tmp_path / source.name
    shutil.copytree(source, destination)
    return destination


def _yaml(path: Path) -> dict[str, object]:
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(parsed, dict)
    return parsed


def test_strategy_and_cost_fixtures_pass_complete_contract() -> None:
    # Requirements: TEST-002, QA-009, DATA-006
    strategy = validate_primary_fixture(STRATEGY)
    cost = validate_primary_fixture(COST)
    assert strategy.fixture_id == "FIXTURE-STRAT-001"
    assert cost.fixture_id == "FIXTURE-COST-001"
    assert strategy.evidence_rows == 25
    assert cost.evidence_rows == 24
    assert strategy.source_count == cost.source_count == 5
    assert len(strategy.checks) == len(cost.checks) == 12


def test_suite_digest_is_deterministic() -> None:
    # Requirements: TEST-005, MODEL-002, DATA-008
    first = fixture_suite_document(REPO_ROOT)
    second = fixture_suite_document(REPO_ROOT)
    assert first == second
    assert len(first["suite_digest"]) == 64


def test_fixtures_are_fictional_advanced_and_have_complete_mandates() -> None:
    # Requirements: QA-009, OUT-002
    for path in (STRATEGY, COST):
        fixture = PrimaryFixture(**_yaml(path / "fixture.yaml"))
        assert fixture.fictional is True
        assert fixture.difficulty == "advanced"
        assert fixture.currency == "SGD"
        assert len(fixture.stakeholders) >= 4
        assert len(fixture.deliberate_traps) >= 5


def test_expected_results_are_restricted_and_structurally_complete() -> None:
    # Requirements: AGENT-002, AGENT-004, QA-009
    for path in (STRATEGY, COST):
        expected = ExpectedResults(**_yaml(path / "expected-results.yaml"))
        assert expected.agent_visible is False
        assert len(expected.mandatory_conclusions) >= 5
        assert len(expected.prohibited_conclusions) >= 4
        assert len(expected.minimum_method_stack) >= 5
        assert len(expected.defect_pack) == 10


def test_restricted_expected_results_cannot_enter_agent_context() -> None:
    # Requirements: AGENT-002, AGENT-004, SEC-002
    ensure_restricted_fixture_isolation(("fixture.yaml", "evidence.csv"))
    with pytest.raises(ValueError, match="Restricted fixture material"):
        ensure_restricted_fixture_isolation(("expected-results.yaml",))


def test_source_manifests_include_one_untrusted_source_and_exclude_answer_keys() -> None:
    # Requirements: AGENT-007, EVID-010, QA-009
    for path in (STRATEGY, COST):
        manifest = _yaml(path / "source-manifest.yaml")
        sources = manifest["sources"]
        assert isinstance(sources, list)
        assert len(sources) == 5
        assert sum(bool(item.get("untrusted_input")) for item in sources if isinstance(item, dict)) == 1
        assert all(
            item.get("filename") != "expected-results.yaml"
            for item in sources
            if isinstance(item, dict)
        )


def test_structured_evidence_has_quality_variation_and_known_sources() -> None:
    # Requirements: EVID-003, EVID-005, DATA-006
    for path in (STRATEGY, COST):
        manifest = _yaml(path / "source-manifest.yaml")
        raw_sources = manifest["sources"]
        assert isinstance(raw_sources, list)
        source_ids = {
            str(item["source_id"])
            for item in raw_sources
            if isinstance(item, dict)
        }
        with (path / "evidence.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert all(row["source_id"] in source_ids for row in rows)
        statuses = {row["quality_status"] for row in rows}
        assert "estimated" in statuses
        assert statuses & {"missing", "stale", "contradictory"}


def test_strategy_oracle_preserves_capital_constraint_and_portfolio_alternatives() -> None:
    # Requirements: MODEL-001, MODEL-004, KNOW-005, OUT-002
    expected = ExpectedResults(**_yaml(STRATEGY / "expected-results.yaml"))
    conclusions = " ".join(expected.mandatory_conclusions)
    assert "SGD 143 million" in conclusions
    assert "SGD 95 million" in conclusions
    assert any("partner" in item.casefold() for item in expected.acceptable_alternatives)
    assert any("divestment" in item.casefold() for item in expected.founder_decisions)


def test_cost_oracle_separates_capacity_avoidability_and_cash_benefit() -> None:
    # Requirements: MODEL-003, MODEL-004, MODEL-008, IMPL-005
    expected = ExpectedResults(**_yaml(COST / "expected-results.yaml"))
    conclusions = " ".join(expected.mandatory_conclusions)
    prohibited = " ".join(expected.prohibited_conclusions)
    assert "Gross automation capacity is not immediate cash benefit" in conclusions
    assert "Allocated shared-service cost" in conclusions
    assert "95 percent utilisation" in prohibited
    assert any("finance" in item.casefold() for item in expected.specialist_reviews)


def test_missing_source_file_fails_closed(tmp_path: Path) -> None:
    # Requirements: QA-004, EVID-002
    fixture = _copy_fixture(STRATEGY, tmp_path)
    (fixture / "interviews.md").unlink()
    with pytest.raises(ValueError, match="Fixture files missing"):
        validate_primary_fixture(fixture)


def test_unknown_evidence_source_fails_closed(tmp_path: Path) -> None:
    # Requirements: EVID-003, QA-004
    fixture = _copy_fixture(COST, tmp_path)
    path = fixture / "evidence.csv"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("COST-SRC-002", "COST-SRC-999", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="unknown source ID"):
        validate_primary_fixture(fixture)


def test_answer_key_in_source_manifest_fails_closed(tmp_path: Path) -> None:
    # Requirements: AGENT-002, QA-009, SEC-002
    fixture = _copy_fixture(STRATEGY, tmp_path)
    manifest = _yaml(fixture / "source-manifest.yaml")
    sources = manifest["sources"]
    assert isinstance(sources, list)
    sources.append(
        {
            "source_id": "STRAT-SRC-999",
            "filename": "expected-results.yaml",
            "source_type": "answer_key",
            "reliability": "restricted",
            "client_visible": False,
        }
    )
    (fixture / "source-manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="Restricted oracle"):
        validate_primary_fixture(fixture)


def test_contracts_reject_nonfictional_or_agent_visible_records() -> None:
    # Requirements: QA-009, AGENT-005
    fixture = _yaml(STRATEGY / "fixture.yaml")
    fixture["fictional"] = False
    with pytest.raises(ValidationError, match="fictional=true"):
        PrimaryFixture(**fixture)

    expected = _yaml(COST / "expected-results.yaml")
    expected["agent_visible"] = True
    with pytest.raises(ValidationError, match="never be agent-visible"):
        ExpectedResults(**expected)
