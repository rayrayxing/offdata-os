"""Deterministic canonical release reconciliation for offdata.

This module reconciles immutable Phase 1-7 release evidence. It does not create
new approval authority, enable real client data or replace operating validation.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class FrozenModel(BaseModel):
    """Strict immutable base model for release evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class ReleaseArtifact(FrozenModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=3)
    file_count: int = Field(gt=0)
    compressed_size_bytes: int = Field(gt=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    retention_days: int = Field(gt=0)
    created_at: datetime
    expires_at: datetime

    @model_validator(mode="after")
    def validate_retention(self) -> ReleaseArtifact:
        if self.expires_at <= self.created_at:
            raise ValueError("Artifact expiry must follow creation.")
        return self


class ControllingRelease(FrozenModel):
    main_merge_commit: str = Field(pattern=r"^[0-9a-f]{40}$")
    pull_request: int = Field(gt=0)
    pull_request_head: str = Field(pattern=r"^[0-9a-f]{40}$")
    pull_request_merge_reference: str = Field(pattern=r"^[0-9a-f]{40}$")
    merged_at: datetime


class FinalValidation(FrozenModel):
    workflow_name: str = Field(min_length=3)
    run_id: int = Field(gt=0)
    job_id: int = Field(gt=0)
    conclusion: Literal["success"]
    runner: str = Field(min_length=3)
    python: str = Field(pattern=r"^3\.11(?:\.\d+)?$")
    artifact: ReleaseArtifact


class SupersededValidationSnapshot(FrozenModel):
    run_id: int = Field(gt=0)
    job_id: int = Field(gt=0)
    branch_head: str = Field(pattern=r"^[0-9a-f]{40}$")
    pull_request_merge_reference: str = Field(pattern=r"^[0-9a-f]{40}$")
    artifact_id: int = Field(gt=0)
    artifact_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    reason: str = Field(min_length=10)


class QualitySummary(FrozenModel):
    implemented_test_nodes: int = Field(gt=0)
    remaining_planned_tests: int = Field(ge=0)
    completed_planned_test_ids: int = Field(ge=0)
    catalogue_requirements: int = Field(gt=0)
    runtime_tests_passed: int = Field(gt=0)
    coverage_percent: float = Field(ge=0, le=100)
    coverage_floor_percent: float = Field(ge=0, le=100)
    mypy_source_files: int = Field(gt=0)
    phase_validators_passed: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_quality(self) -> QualitySummary:
        if self.coverage_percent < self.coverage_floor_percent:
            raise ValueError("Coverage is below the governed floor.")
        if self.phase_validators_passed != 7:
            raise ValueError("PCR-01 requires all seven phase validators.")
        return self


class GovernedRecordSpec(FrozenModel):
    path: str = Field(min_length=3)
    role: str = Field(min_length=3)
    restricted: bool


class SourceProfileExpectations(FrozenModel):
    total_sources: int = Field(gt=0)
    core_markdown_sources: int = Field(gt=0)
    domain_docx_sources: int = Field(gt=0)
    original_files_committed: Literal[False]
    import_status: Literal["profiled_original_not_committed"]
    aggregate_profile_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    aggregate_profile_bytes: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_counts(self) -> SourceProfileExpectations:
        if self.core_markdown_sources + self.domain_docx_sources != self.total_sources:
            raise ValueError("Source-profile class counts do not reconcile.")
        return self


class ReleaseBoundaries(FrozenModel):
    real_client_data_enabled: Literal[False]
    original_methodology_binaries_committed: Literal[False]
    restricted_evaluation_material_agent_visible: Literal[False]
    external_actions_authorised: Literal[False]
    production_security_operating_evidence_complete: Literal[False]
    founder_accountability_preserved: Literal[True]


class ReleaseRules(FrozenModel):
    final_validation_is_authoritative: Literal[True]
    superseded_snapshots_are_preserved_not_controlling: Literal[True]
    governed_record_digests_are_computed_from_repository_bytes: Literal[True]
    source_profile_checksums_are_preserved: Literal[True]
    manifest_generation_must_be_byte_reproducible: Literal[True]
    missing_or_changed_governed_record_fails: Literal[True]


class CanonicalReleaseConfig(FrozenModel):
    version: Literal["1.0.0"]
    status: Literal["governed_chat_first"]
    release_id: str = Field(min_length=3)
    scope: Literal["canonical_phase_1_to_7_release_reconciliation"]
    repository: Literal["rayrayxing/offdata-os"]
    phases: tuple[int, ...]
    controlling_release: ControllingRelease
    final_validation: FinalValidation
    superseded_validation_snapshots: tuple[SupersededValidationSnapshot, ...]
    quality_summary: QualitySummary
    governed_records: tuple[GovernedRecordSpec, ...]
    source_profile_expectations: SourceProfileExpectations
    boundaries: ReleaseBoundaries
    rules: ReleaseRules

    @model_validator(mode="after")
    def validate_release_identity(self) -> CanonicalReleaseConfig:
        if self.phases != tuple(range(1, 8)):
            raise ValueError("Canonical release phases must be exactly 1 through 7.")
        paths = [item.path for item in self.governed_records]
        if len(paths) != len(set(paths)):
            raise ValueError("Governed release paths must be unique.")
        final_run = self.final_validation.run_id
        final_artifact = self.final_validation.artifact.id
        if any(item.run_id == final_run for item in self.superseded_validation_snapshots):
            raise ValueError("Final validation cannot also be superseded.")
        if any(item.artifact_id == final_artifact for item in self.superseded_validation_snapshots):
            raise ValueError("Final artifact cannot also be superseded.")
        return self


class GovernedRecordDigest(FrozenModel):
    path: str
    role: str
    restricted: bool
    size_bytes: int = Field(gt=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class SourceProfileDigest(FrozenModel):
    source_id: str = Field(min_length=3)
    checksum_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    byte_size: int = Field(gt=0)
    import_status: Literal["profiled_original_not_committed"]
    rights_status: str = Field(min_length=3)
    external_redistribution_allowed: Literal[False]


class SourceProfileSummary(FrozenModel):
    total_sources: int = Field(gt=0)
    core_markdown_sources: int = Field(gt=0)
    domain_docx_sources: int = Field(gt=0)
    aggregate_profile_bytes: int = Field(gt=0)
    aggregate_profile_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    profiles: tuple[SourceProfileDigest, ...]


class CanonicalReleaseBody(FrozenModel):
    version: Literal["1.0.0"]
    status: Literal["canonical_governed_release"]
    release_id: str
    scope: str
    repository: str
    phases: tuple[int, ...]
    controlling_release: ControllingRelease
    final_validation: FinalValidation
    superseded_validation_snapshots: tuple[SupersededValidationSnapshot, ...]
    quality_summary: QualitySummary
    governed_records: tuple[GovernedRecordDigest, ...]
    source_profiles: SourceProfileSummary
    boundaries: ReleaseBoundaries
    rules: ReleaseRules


class CanonicalReleaseManifest(CanonicalReleaseBody):
    manifest_digest: str = Field(pattern=r"^[0-9a-f]{64}$")


def _load_yaml_object(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected YAML object: {path}")
    return value


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_sha256(path: Path) -> str:
    """Return the SHA-256 digest of exact repository bytes."""

    return _sha256_bytes(path.read_bytes())


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def load_release_config(root: Path) -> CanonicalReleaseConfig:
    """Load and strictly validate the governed reconciliation source."""

    return CanonicalReleaseConfig.model_validate(
        _load_yaml_object(root / "configs" / "canonical-release.yaml")
    )


def _governed_record_digests(
    root: Path, config: CanonicalReleaseConfig
) -> tuple[GovernedRecordDigest, ...]:
    records: list[GovernedRecordDigest] = []
    for spec in config.governed_records:
        path = root / spec.path
        if not path.is_file():
            raise ValueError(f"Missing governed release record: {spec.path}")
        raw = path.read_bytes()
        if spec.restricted:
            parsed = json.loads(raw)
            if not isinstance(parsed, dict) or parsed.get("agent_visible") is not False:
                raise ValueError(f"Restricted record must remain agent-invisible: {spec.path}")
        records.append(
            GovernedRecordDigest(
                path=spec.path,
                role=spec.role,
                restricted=spec.restricted,
                size_bytes=len(raw),
                sha256=_sha256_bytes(raw),
            )
        )
    return tuple(records)


def _source_profile_summary(root: Path, config: CanonicalReleaseConfig) -> SourceProfileSummary:
    document = _load_yaml_object(root / "knowledge" / "source-manifest.yaml")
    core = document.get("canonical_core_sources")
    domain = document.get("domain_methodology_sources")
    if not isinstance(core, list) or not isinstance(domain, list):
        raise ValueError("Source manifest must contain core and domain source lists.")
    profiles: list[SourceProfileDigest] = []
    for raw in core + domain:
        if not isinstance(raw, dict):
            raise ValueError("Source profile must be an object.")
        profiles.append(SourceProfileDigest.model_validate(raw))
    profiles.sort(key=lambda item: item.source_id)
    if len({item.source_id for item in profiles}) != len(profiles):
        raise ValueError("Source profile IDs must be unique.")
    canonical_profiles = [item.model_dump(mode="json") for item in profiles]
    aggregate_digest = _sha256_bytes(_canonical_bytes(canonical_profiles))
    summary = SourceProfileSummary(
        total_sources=len(profiles),
        core_markdown_sources=len(core),
        domain_docx_sources=len(domain),
        aggregate_profile_bytes=sum(item.byte_size for item in profiles),
        aggregate_profile_sha256=aggregate_digest,
        profiles=tuple(profiles),
    )
    expected = config.source_profile_expectations
    if (
        summary.total_sources != expected.total_sources
        or summary.core_markdown_sources != expected.core_markdown_sources
        or summary.domain_docx_sources != expected.domain_docx_sources
        or summary.aggregate_profile_bytes != expected.aggregate_profile_bytes
        or summary.aggregate_profile_sha256 != expected.aggregate_profile_sha256
    ):
        raise ValueError("Source profile summary does not match governed expectations.")
    return summary


def build_canonical_release_manifest(root: Path) -> CanonicalReleaseManifest:
    """Build the immutable Phase 1-7 canonical release manifest."""

    config = load_release_config(root)
    body = CanonicalReleaseBody(
        version="1.0.0",
        status="canonical_governed_release",
        release_id=config.release_id,
        scope=config.scope,
        repository=config.repository,
        phases=config.phases,
        controlling_release=config.controlling_release,
        final_validation=config.final_validation,
        superseded_validation_snapshots=config.superseded_validation_snapshots,
        quality_summary=config.quality_summary,
        governed_records=_governed_record_digests(root, config),
        source_profiles=_source_profile_summary(root, config),
        boundaries=config.boundaries,
        rules=config.rules,
    )
    digest = _sha256_bytes(_canonical_bytes(body.model_dump(mode="json")))
    return CanonicalReleaseManifest(**body.model_dump(), manifest_digest=digest)


def canonical_release_document(root: Path) -> dict[str, Any]:
    """Return the JSON-ready canonical release document."""

    return build_canonical_release_manifest(root).model_dump(mode="json")


def write_canonical_release_manifest(root: Path, destination: Path) -> None:
    """Write the byte-reproducible canonical release manifest."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(
            canonical_release_document(root),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def verify_canonical_release_manifest(root: Path, committed: Path) -> None:
    """Fail when the committed manifest differs from independent generation."""

    expected = json.dumps(
        canonical_release_document(root),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    ) + "\n"
    actual = committed.read_text(encoding="utf-8")
    if actual != expected:
        raise ValueError("Committed canonical release manifest is stale or modified.")
    parsed = CanonicalReleaseManifest.model_validate_json(actual)
    body = CanonicalReleaseBody.model_validate(parsed.model_dump(exclude={"manifest_digest"}))
    expected_digest = _sha256_bytes(_canonical_bytes(body.model_dump(mode="json")))
    if parsed.manifest_digest != expected_digest:
        raise ValueError("Canonical release manifest digest is invalid.")
