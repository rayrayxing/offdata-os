from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from offdata_core.release_reconciliation import (
    CanonicalReleaseConfig,
    build_canonical_release_manifest,
    load_release_config,
    verify_canonical_release_manifest,
    write_canonical_release_manifest,
)


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "releases" / "canonical-chat-first-phase1-7-release.json"


def _copy_inputs(tmp_path: Path) -> Path:
    target = tmp_path / "repository"
    paths = [
        "configs/canonical-release.yaml",
        "requirements/test-registry.json",
        "fixtures/additional-primary-fixtures.json",
        "fixtures/digital-ai/FIXTURE-DAI-001/oracle-baseline.json",
        "fixtures/digital-ai/FIXTURE-DAI-001/deliverable-semantic-baseline.json",
        "knowledge/knowledge-ingestion-baseline.json",
        "knowledge/source-manifest.yaml",
        "security/security-regionalisation-baseline.json",
    ]
    for relative in paths:
        source = ROOT / relative
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    return target


def _rewrite_yaml(path: Path, mutation: callable) -> None:  # type: ignore[type-arg]
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    mutation(value)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def test_canonical_release_builds_expected_identity() -> None:
    manifest = build_canonical_release_manifest(ROOT)
    assert manifest.release_id == "CHAT-FIRST-PHASE1-7-2026-08-05"
    assert manifest.phases == tuple(range(1, 8))
    assert manifest.controlling_release.main_merge_commit == (
        "7dc5531e641158e5a84fbbb9fdf07cefefd4782b"
    )
    assert manifest.final_validation.run_id == 30976222896
    assert manifest.final_validation.job_id == 92210649514
    assert manifest.final_validation.artifact.id == 8918355687
    assert len(manifest.superseded_validation_snapshots) == 2


def test_governed_record_digests_match_exact_repository_bytes() -> None:
    manifest = build_canonical_release_manifest(ROOT)
    assert len(manifest.governed_records) == 7
    for record in manifest.governed_records:
        raw = (ROOT / record.path).read_bytes()
        assert record.size_bytes == len(raw)
        assert record.sha256 == hashlib.sha256(raw).hexdigest()


def test_source_profile_summary_preserves_all_founder_sources() -> None:
    manifest = build_canonical_release_manifest(ROOT)
    summary = manifest.source_profiles
    assert summary.total_sources == 23
    assert summary.core_markdown_sources == 11
    assert summary.domain_docx_sources == 12
    assert len(summary.profiles) == 23
    assert len({item.source_id for item in summary.profiles}) == 23
    assert all(item.import_status == "profiled_original_not_committed" for item in summary.profiles)
    assert all(not item.external_redistribution_allowed for item in summary.profiles)


def test_canonical_release_manifest_is_reproducible_and_verified(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    write_canonical_release_manifest(ROOT, first)
    write_canonical_release_manifest(ROOT, second)
    assert first.read_bytes() == second.read_bytes()
    verify_canonical_release_manifest(ROOT, MANIFEST)
    committed = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert committed["manifest_digest"] == build_canonical_release_manifest(ROOT).manifest_digest


def test_changed_governed_record_invalidates_committed_manifest(tmp_path: Path) -> None:
    copied = _copy_inputs(tmp_path)
    record = copied / "security" / "security-regionalisation-baseline.json"
    record.write_text(record.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="stale or modified"):
        verify_canonical_release_manifest(copied, MANIFEST)


def test_changed_source_profile_checksum_fails_governed_expectation(tmp_path: Path) -> None:
    copied = _copy_inputs(tmp_path)
    source_manifest = copied / "knowledge" / "source-manifest.yaml"

    def mutate(value: dict[str, object]) -> None:
        records = value["canonical_core_sources"]
        assert isinstance(records, list)
        first = records[0]
        assert isinstance(first, dict)
        first["checksum_sha256"] = "0" * 64

    _rewrite_yaml(source_manifest, mutate)
    with pytest.raises(ValueError, match="Source profile summary"):
        build_canonical_release_manifest(copied)


def test_final_validation_cannot_also_be_superseded() -> None:
    raw = yaml.safe_load(
        (ROOT / "configs" / "canonical-release.yaml").read_text(encoding="utf-8")
    )
    raw["superseded_validation_snapshots"][0]["run_id"] = raw["final_validation"]["run_id"]
    with pytest.raises(ValidationError, match="cannot also be superseded"):
        CanonicalReleaseConfig.model_validate(raw)


def test_restricted_oracles_must_remain_agent_invisible(tmp_path: Path) -> None:
    copied = _copy_inputs(tmp_path)
    oracle = copied / "fixtures" / "digital-ai" / "FIXTURE-DAI-001" / "oracle-baseline.json"
    value = json.loads(oracle.read_text(encoding="utf-8"))
    value["agent_visible"] = True
    oracle.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="agent-invisible"):
        build_canonical_release_manifest(copied)


def test_release_boundaries_cannot_enable_real_client_data() -> None:
    raw = yaml.safe_load(
        (ROOT / "configs" / "canonical-release.yaml").read_text(encoding="utf-8")
    )
    raw["boundaries"]["real_client_data_enabled"] = True
    with pytest.raises(ValidationError):
        CanonicalReleaseConfig.model_validate(raw)


def test_missing_governed_record_fails_reconciliation(tmp_path: Path) -> None:
    copied = _copy_inputs(tmp_path)
    (copied / "requirements" / "test-registry.json").unlink()
    with pytest.raises(ValueError, match="Missing governed release record"):
        build_canonical_release_manifest(copied)


def test_governed_release_config_loads_without_implicit_correction() -> None:
    config = load_release_config(ROOT)
    assert config.final_validation.conclusion == "success"
    assert config.boundaries.real_client_data_enabled is False
    assert config.boundaries.founder_accountability_preserved is True
