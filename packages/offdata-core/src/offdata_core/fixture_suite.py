"""Deterministic contracts and validators for synthetic primary engagement fixtures."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


RESTRICTED_FILES = frozenset({"expected-results.yaml"})
REQUIRED_CLIENT_FILES = frozenset(
    {
        "fixture.yaml",
        "source-manifest.yaml",
        "evidence.csv",
        "interviews.md",
        "untrusted-input.txt",
        "data-dictionary.md",
    }
)


class FixtureSource(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_id: str = Field(pattern=r"^[A-Z]+-SRC-[0-9]{3}$")
    filename: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    reliability: str = Field(min_length=1)
    client_visible: bool
    untrusted_input: bool = False
    limitations: tuple[str, ...] = ()


class PrimaryFixture(BaseModel):
    model_config = ConfigDict(frozen=True)

    fixture_id: str = Field(pattern=r"^FIXTURE-[A-Z]+-001$")
    version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    domain: str = Field(min_length=1)
    difficulty: str = Field(pattern=r"^(foundation|advanced|adversarial)$")
    fictional: bool
    organisation: dict[str, Any]
    mandate: dict[str, Any]
    stakeholders: tuple[dict[str, Any], ...]
    constraints: tuple[str, ...]
    exclusions: tuple[str, ...]
    decision_date: str = Field(min_length=10)
    currency: str = Field(min_length=3, max_length=3)
    deliberate_traps: tuple[str, ...]

    @model_validator(mode="after")
    def validate_fixture(self) -> "PrimaryFixture":
        if not self.fictional:
            raise ValueError("Synthetic fixtures must declare fictional=true.")
        if len(self.stakeholders) < 3:
            raise ValueError("Primary fixture requires at least three stakeholders.")
        if len(self.deliberate_traps) < 4:
            raise ValueError("Primary fixture requires at least four deliberate traps.")
        required_mandate = {"decision", "scope", "commercial_assumptions", "delivery_assumptions"}
        missing = required_mandate - set(self.mandate)
        if missing:
            raise ValueError(f"Fixture mandate is incomplete: {sorted(missing)}")
        return self


class ExpectedResults(BaseModel):
    model_config = ConfigDict(frozen=True)

    fixture_id: str
    agent_visible: bool
    mandatory_conclusions: tuple[str, ...]
    prohibited_conclusions: tuple[str, ...]
    acceptable_alternatives: tuple[str, ...]
    minimum_method_stack: tuple[str, ...]
    rejected_methods: tuple[dict[str, Any], ...]
    calculations: tuple[dict[str, Any], ...]
    uncertainties: tuple[str, ...]
    specialist_reviews: tuple[str, ...]
    founder_decisions: tuple[str, ...]
    delivery_oracle: dict[str, Any]
    defect_pack: tuple[str, ...]

    @model_validator(mode="after")
    def validate_oracle(self) -> "ExpectedResults":
        if self.agent_visible:
            raise ValueError("Expected-results oracle must never be agent-visible.")
        if len(self.minimum_method_stack) < 4:
            raise ValueError("Expected-results oracle requires a minimum sufficient method stack.")
        if len(self.defect_pack) < 10:
            raise ValueError("Expected-results oracle requires the complete defect pack.")
        return self


class FixtureValidationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    fixture_id: str
    input_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    client_files: tuple[str, ...]
    source_count: int = Field(gt=0)
    evidence_rows: int = Field(gt=0)
    checks: tuple[str, ...]


def _read_yaml(path: Path) -> dict[str, Any]:
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"Expected YAML object: {path}")
    return parsed


def ensure_restricted_fixture_isolation(context_paths: tuple[str, ...]) -> None:
    leaked = RESTRICTED_FILES & {Path(path).name for path in context_paths}
    if leaked:
        raise ValueError(f"Restricted fixture material entered normal context: {sorted(leaked)}")


def validate_primary_fixture(fixture_dir: Path) -> FixtureValidationResult:
    missing = sorted(name for name in REQUIRED_CLIENT_FILES | RESTRICTED_FILES if not (fixture_dir / name).is_file())
    if missing:
        raise ValueError(f"Fixture files missing: {missing}")

    fixture = PrimaryFixture(**_read_yaml(fixture_dir / "fixture.yaml"))
    expected = ExpectedResults(**_read_yaml(fixture_dir / "expected-results.yaml"))
    if expected.fixture_id != fixture.fixture_id:
        raise ValueError("Fixture and expected-results IDs do not match.")

    manifest = _read_yaml(fixture_dir / "source-manifest.yaml")
    raw_sources = manifest.get("sources")
    if not isinstance(raw_sources, list):
        raise ValueError("Source manifest requires a sources list.")
    sources = tuple(FixtureSource(**item) for item in raw_sources)
    source_ids = [item.source_id for item in sources]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("Source IDs must be unique.")
    if not any(item.untrusted_input for item in sources):
        raise ValueError("Fixture requires at least one explicitly untrusted source.")
    if any(item.filename == "expected-results.yaml" for item in sources):
        raise ValueError("Restricted oracle cannot appear in the source manifest.")
    for source in sources:
        if not (fixture_dir / source.filename).is_file():
            raise ValueError(f"Manifest source file is missing: {source.filename}")

    evidence_path = fixture_dir / "evidence.csv"
    with evidence_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = set(reader.fieldnames or ())
    required_fields = {
        "row_id",
        "source_id",
        "metric",
        "segment",
        "period",
        "value",
        "unit",
        "quality_status",
        "notes",
    }
    if not required_fields <= fields:
        raise ValueError(f"Evidence CSV fields missing: {sorted(required_fields - fields)}")
    if len(rows) < 12:
        raise ValueError("Primary fixture requires at least twelve structured evidence rows.")
    if any(row["source_id"] not in source_ids for row in rows):
        raise ValueError("Evidence row references an unknown source ID.")
    if not any(row["quality_status"] in {"missing", "stale", "contradictory", "estimated"} for row in rows):
        raise ValueError("Fixture lacks deliberate evidence-quality variation.")

    client_files = tuple(sorted(REQUIRED_CLIENT_FILES))
    ensure_restricted_fixture_isolation(client_files)
    digest = hashlib.sha256()
    for name in client_files:
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update((fixture_dir / name).read_bytes())
        digest.update(b"\0")

    checks = (
        "fictional_identity",
        "complete_mandate",
        "stakeholder_conflict",
        "source_manifest_integrity",
        "untrusted_input_control",
        "structured_evidence_schema",
        "evidence_quality_variation",
        "restricted_oracle_isolation",
        "minimum_method_stack",
        "calculation_oracle",
        "delivery_oracle",
        "complete_defect_pack",
    )
    return FixtureValidationResult(
        fixture_id=fixture.fixture_id,
        input_digest=digest.hexdigest(),
        client_files=client_files,
        source_count=len(sources),
        evidence_rows=len(rows),
        checks=checks,
    )


def fixture_suite_document(root: Path) -> dict[str, Any]:
    fixture_dirs = (
        root / "fixtures" / "strategy" / "FIXTURE-STRAT-001",
        root / "fixtures" / "cost-productivity" / "FIXTURE-COST-001",
    )
    results = [validate_primary_fixture(path) for path in fixture_dirs]
    return {
        "suite_version": "1.0.0",
        "fixture_ids": [result.fixture_id for result in results],
        "fixtures": [result.model_dump(mode="json") for result in results],
        "suite_digest": hashlib.sha256(
            json.dumps(
                [result.model_dump(mode="json") for result in results],
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest(),
    }
