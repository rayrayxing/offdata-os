from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from offdata_core.fixture_programme import (
    ADDITIONAL_PRIMARY_FIXTURE_COUNT,
    NORTHSTAR_FIXTURE_ID,
    FixtureProgramme,
    build_fixture_programme,
    programme_digest,
    serialise_programme,
    verify_committed_programme,
    write_programme,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
SEED_PATH = REPO_ROOT / "fixtures" / "additional-primary-fixture-seeds.yaml"
BASELINE_PATH = REPO_ROOT / "fixtures" / "additional-primary-fixtures.json"
MANIFEST_PATH = REPO_ROOT / "fixtures" / "manifest.yaml"


def _programme() -> FixtureProgramme:
    return build_fixture_programme(SEED_PATH)


def _copy_seed(tmp_path: Path) -> Path:
    destination = tmp_path / SEED_PATH.name
    shutil.copy2(SEED_PATH, destination)
    return destination


def test_fixture_programme_builds_all_remaining_primary_engagement_types() -> None:
    # Requirements: TEST-002, QA-009
    programme = _programme()
    assert len(programme.fixtures) == ADDITIONAL_PRIMARY_FIXTURE_COUNT == 12
    assert NORTHSTAR_FIXTURE_ID not in {item.fixture_id for item in programme.fixtures}
    assert len({item.fixture_id for item in programme.fixtures}) == 12
    assert len({item.engagement_type for item in programme.fixtures}) == 12


def test_fixture_programme_matches_governed_manifest_primary_scope() -> None:
    # Requirements: TEST-002, DATA-008
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest_ids = {
        item["id"] for item in manifest["primary_engagements"] if item["id"] != NORTHSTAR_FIXTURE_ID
    }
    programme = _programme()
    assert {item.fixture_id for item in programme.fixtures} == manifest_ids


def test_every_fixture_contains_required_evidence_data_and_defects() -> None:
    # Requirements: EVID-003, EVID-005, QA-009
    for fixture in _programme().fixtures:
        assert len(fixture.evidence_records) == 5
        assert {item.record_type for item in fixture.evidence_records} == {
            "source_document",
            "interview_transcript",
        }
        assert len(fixture.structured_data) == 2
        assert len(fixture.data_quality_defects) == 2
        assert {item["severity"] for item in fixture.data_quality_defects} == {"high", "medium"}


def test_every_fixture_is_decision_led_and_contains_method_traps() -> None:
    # Requirements: KNOW-003, KNOW-004, KNOW-005, OUT-002
    for fixture in _programme().fixtures:
        assert fixture.mandate["decision"]
        assert fixture.mandate["decision_owner"]
        assert len(fixture.expected_problem_archetypes) >= 2
        assert len(fixture.acceptable_method_stacks) == 2
        assert all(len(stack) >= 3 for stack in fixture.acceptable_method_stacks)
        assert len(fixture.rejected_method_traps) == 2
        assert len(fixture.alternatives) == 2


def test_every_fixture_contains_quantitative_ranges_assumptions_and_falsifiers() -> None:
    # Requirements: MODEL-002, MODEL-004, MODEL-005
    for fixture in _programme().fixtures:
        assert len(fixture.expected_calculations) == 2
        assert all(item.valid_range[0] <= item.valid_range[1] for item in fixture.expected_calculations)
        assert len(fixture.material_assumptions) == 2
        assert len(fixture.falsifiers) == 2
        assert len(fixture.contradicting_evidence) == 2


def test_every_fixture_contains_story_implementation_benefits_and_founder_gates() -> None:
    # Requirements: DELIV-001, IMPL-001, IMPL-005, AUTH-003, AUTH-004
    for fixture in _programme().fixtures:
        assert fixture.expected_story_structure == (
            "Decision",
            "Evidence",
            "Options",
            "Recommendation",
            "Implementation",
            "Benefits and controls",
        )
        assert len(fixture.implementation_records) == 2
        assert len(fixture.benefit_records) == 2
        assert {item["decision_class"] for item in fixture.expected_founder_interruptions} == {
            "D3",
            "D4",
        }
        assert all(item["recognition_rule"] for item in fixture.benefit_records)


def test_fixture_programme_is_byte_reproducible_and_committed_baseline_is_current() -> None:
    # Requirements: DATA-003, DATA-008, TEST-005
    first = serialise_programme(_programme())
    second = serialise_programme(_programme())
    assert first == second
    assert programme_digest(_programme()) == programme_digest(_programme())
    verify_committed_programme(SEED_PATH, BASELINE_PATH)


def test_fixture_programme_writer_and_stale_detection(tmp_path: Path) -> None:
    # Requirements: QA-005, TEST-005
    seed = _copy_seed(tmp_path)
    destination = tmp_path / "additional-primary-fixtures.json"
    write_programme(seed, destination)
    verify_committed_programme(seed, destination)
    destination.write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="stale or non-reproducible"):
        verify_committed_programme(seed, destination)


def test_fixture_mutation_invalidates_programme_baseline(tmp_path: Path) -> None:
    # Requirements: DATA-008, QA-005, TEST-005
    seed = _copy_seed(tmp_path)
    destination = tmp_path / "additional-primary-fixtures.json"
    write_programme(seed, destination)
    text = seed.read_text(encoding="utf-8")
    seed.write_text(text.replace("Apex Field Services", "Apex Field Services Revised", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="stale or non-reproducible"):
        verify_committed_programme(seed, destination)


def test_fixture_contract_rejects_non_synthetic_client() -> None:
    # Requirements: DATA-002, QA-004, SEC-002
    payload = _programme().model_dump(mode="json")
    payload["fixtures"][0]["synthetic_client"]["classification"] = "real"
    with pytest.raises(ValidationError, match="explicitly synthetic"):
        FixtureProgramme(**payload)


def test_fixture_contract_rejects_missing_primary_fixture() -> None:
    # Requirements: TEST-002, QA-004
    payload = _programme().model_dump(mode="json")
    payload["fixtures"] = payload["fixtures"][:-1]
    with pytest.raises(ValidationError, match="twelve fixtures"):
        FixtureProgramme(**payload)


def test_fixture_contract_rejects_reversed_calculation_range() -> None:
    # Requirements: MODEL-002, QA-004
    payload = _programme().model_dump(mode="json")
    payload["fixtures"][0]["expected_calculations"][0]["valid_range"] = [10, 1]
    with pytest.raises(ValidationError, match="range is reversed"):
        FixtureProgramme(**payload)
