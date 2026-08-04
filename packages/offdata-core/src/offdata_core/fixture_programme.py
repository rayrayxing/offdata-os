"""Deterministic expansion and validation of the additional primary engagement fixtures."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

ADDITIONAL_PRIMARY_FIXTURE_COUNT = 12
NORTHSTAR_FIXTURE_ID = "FIXTURE-DAI-001"


class FixtureEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    record_id: str = Field(min_length=1)
    record_type: str = Field(min_length=1)
    title: str = Field(min_length=1)
    authority: str = Field(min_length=1)
    signal: str = Field(min_length=1)


class FixtureCalculation(BaseModel):
    model_config = ConfigDict(frozen=True)

    calculation_id: str
    metric: str
    valid_range: tuple[float, float]
    unit: str

    @model_validator(mode="after")
    def validate_range(self) -> "FixtureCalculation":
        if self.valid_range[0] > self.valid_range[1]:
            raise ValueError("Calculation range is reversed.")
        return self


class PrimaryEngagementFixture(BaseModel):
    model_config = ConfigDict(frozen=True)

    fixture_id: str = Field(pattern=r"^FIXTURE-[A-Z]+-001$")
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    status: str
    engagement_type: str
    working_title: str
    synthetic_client: dict[str, Any]
    mandate: dict[str, Any]
    opportunity: dict[str, Any]
    crm_records: tuple[dict[str, Any], ...]
    evidence_records: tuple[FixtureEvidence, ...]
    structured_data: tuple[dict[str, Any], ...]
    data_quality_defects: tuple[dict[str, Any], ...]
    expected_problem_archetypes: tuple[str, ...]
    acceptable_method_stacks: tuple[tuple[str, ...], ...]
    rejected_method_traps: tuple[dict[str, str], ...]
    contradicting_evidence: tuple[dict[str, str], ...]
    expected_calculations: tuple[FixtureCalculation, ...]
    material_assumptions: tuple[str, ...]
    falsifiers: tuple[str, ...]
    reference_recommendation: str
    alternatives: tuple[str, ...]
    expected_story_structure: tuple[str, ...]
    known_quality_defects: tuple[str, ...]
    expected_founder_interruptions: tuple[dict[str, str], ...]
    implementation_records: tuple[dict[str, str], ...]
    benefit_records: tuple[dict[str, str], ...]
    specialist_reviews: tuple[str, ...]
    prohibited_conclusions: tuple[str, ...]

    @model_validator(mode="after")
    def validate_fixture(self) -> "PrimaryEngagementFixture":
        if self.synthetic_client.get("classification") != "synthetic":
            raise ValueError("Fixture client must be explicitly synthetic.")
        if self.synthetic_client.get("jurisdiction") != "Singapore":
            raise ValueError("Initial fixture jurisdiction must be Singapore.")
        if len(self.evidence_records) < 5:
            raise ValueError("Fixture requires source and interview evidence.")
        if len(self.structured_data) < 2 or len(self.data_quality_defects) < 2:
            raise ValueError("Fixture requires structured data and deliberate defects.")
        if len(self.acceptable_method_stacks) < 2 or any(
            len(item) < 3 for item in self.acceptable_method_stacks
        ):
            raise ValueError("Fixture requires two minimum-sufficient method stacks.")
        if len(self.rejected_method_traps) < 2 or len(self.contradicting_evidence) < 2:
            raise ValueError("Fixture requires method traps and contradictions.")
        if len(self.expected_calculations) < 2:
            raise ValueError("Fixture requires quantitative expectations.")
        if len(self.expected_story_structure) < 6:
            raise ValueError("Fixture requires a complete decision-led story structure.")
        if len(self.implementation_records) < 2 or len(self.benefit_records) < 2:
            raise ValueError("Fixture requires implementation and benefit expectations.")
        return self


class FixtureProgramme(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str
    classification: str
    fixtures: tuple[PrimaryEngagementFixture, ...]

    @model_validator(mode="after")
    def validate_programme(self) -> "FixtureProgramme":
        if len(self.fixtures) != ADDITIONAL_PRIMARY_FIXTURE_COUNT:
            raise ValueError("Additional primary fixture programme must contain twelve fixtures.")
        ids = [item.fixture_id for item in self.fixtures]
        types = [item.engagement_type for item in self.fixtures]
        if len(ids) != len(set(ids)) or len(types) != len(set(types)):
            raise ValueError("Fixture IDs and engagement types must be unique.")
        if NORTHSTAR_FIXTURE_ID in ids:
            raise ValueError("The Phase 3 Northstar fixture must not be duplicated.")
        return self


def _read_yaml(path: Path) -> dict[str, Any]:
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError(f"Expected YAML object: {path}")
    return parsed


def build_fixture_programme(seed_path: Path) -> FixtureProgramme:
    source = _read_yaml(seed_path)
    defaults = source.get("defaults")
    seeds = source.get("fixtures")
    if not isinstance(defaults, dict) or not isinstance(seeds, list):
        raise ValueError("Fixture seed file requires defaults and fixtures.")
    fixtures = tuple(
        _expand_seed(seed, defaults, index) for index, seed in enumerate(seeds, 1)
    )
    return FixtureProgramme(
        version=str(source.get("version", "")),
        classification="synthetic_golden_fixture_programme",
        fixtures=fixtures,
    )


def _expand_seed(seed: Any, defaults: dict[str, Any], index: int) -> PrimaryEngagementFixture:
    if not isinstance(seed, dict):
        raise ValueError("Fixture seed must be an object.")
    fixture_id = str(seed["fixture_id"])
    owner = str(seed["decision_owner"])
    methods = tuple(str(item) for item in seed["method_stack"])
    evidence = (
        FixtureEvidence(record_id=f"{fixture_id}-SRC-001", record_type="source_document", title="Management case", authority="management", signal="Urgency and stated objective; confidence may be overstated."),
        FixtureEvidence(record_id=f"{fixture_id}-SRC-002", record_type="source_document", title="Operational baseline", authority="controlled_internal", signal="Current performance, activity and economics."),
        FixtureEvidence(record_id=f"{fixture_id}-SRC-003", record_type="source_document", title="Independent challenge note", authority="independent_review", signal="Risks, contradictions and alternatives."),
        FixtureEvidence(record_id=f"{fixture_id}-INT-001", record_type="interview_transcript", title=f"Interview with {owner}", authority="decision_owner", signal="Supports action but overstates certainty."),
        FixtureEvidence(record_id=f"{fixture_id}-INT-002", record_type="interview_transcript", title="Front-line manager interview", authority="operational_witness", signal="Identifies operational constraints and adoption risk."),
    )
    return PrimaryEngagementFixture(
        fixture_id=fixture_id,
        version="1.0.0",
        status="golden_chat_first",
        engagement_type=str(seed["engagement_type"]),
        working_title=str(seed["working_title"]),
        synthetic_client={"name": seed["client_name"], "jurisdiction": defaults["jurisdiction"], "classification": defaults["classification"], "employees": 400 + index * 37},
        mandate={"decision": seed["decision"], "scope": defaults["scope"], "constraints": defaults["constraints"], "decision_owner": owner, "decision_gate": "GATE-RECOMMENDATION"},
        opportunity={"opportunity_id": f"OPP-{index:03d}", "stage": "qualified", "estimated_fee_sgd": 80000 + index * 5000, "relationship_summary": "Synthetic referral with a defined executive decision and incomplete evidence."},
        crm_records=({"record_type": "company", "record_id": f"CRM-COMP-{index:03d}"}, {"record_type": "deal", "record_id": f"CRM-DEAL-{index:03d}"}),
        evidence_records=evidence,
        structured_data=(
            {"dataset_id": f"{fixture_id}-DATA-001", "name": "Performance baseline", "rows": 24 + index, "fields": ["period", "segment", "volume", "cost", "quality"], "controlled_total": 1000 + index * 25},
            {"dataset_id": f"{fixture_id}-DATA-002", "name": "Option economics", "rows": 3, "fields": ["option", "investment", "benefit", "risk"], "controlled_total": 3},
        ),
        data_quality_defects=(
            {"defect_id": f"{fixture_id}-DQ-001", "severity": "high", "description": "Management total does not reconcile to segment detail."},
            {"defect_id": f"{fixture_id}-DQ-002", "severity": "medium", "description": "One period or segment contains a missing observation."},
        ),
        expected_problem_archetypes=tuple(seed["problem_archetypes"]),
        acceptable_method_stacks=(methods, (methods[0], "assumption and falsifier review", "implementation feasibility")),
        rejected_method_traps=(
            {"candidate": "generic maturity model", "reason": "Does not resolve the executive choice or economics."},
            {"candidate": "framework catalogue", "reason": "Adds breadth without evidence or decision relevance."},
        ),
        contradicting_evidence=(
            {"contradiction_id": f"{fixture_id}-CON-001", "statement": str(seed["management_overclaim"])},
            {"contradiction_id": f"{fixture_id}-CON-002", "statement": str(seed["frontline_constraint"])},
        ),
        expected_calculations=(
            FixtureCalculation(calculation_id=f"{fixture_id}-CALC-001", metric="base_case_value_sgd", valid_range=tuple(seed["base_case_value_range_sgd"]), unit="SGD"),
            FixtureCalculation(calculation_id=f"{fixture_id}-CALC-002", metric="downside_headroom_percent", valid_range=(0, 25), unit="percent"),
        ),
        material_assumptions=tuple(defaults["assumptions"]),
        falsifiers=tuple(defaults["falsifiers"]),
        reference_recommendation=str(seed["reference_recommendation"]),
        alternatives=tuple(seed["alternatives"]),
        expected_story_structure=tuple(defaults["story_structure"]),
        known_quality_defects=("Unsupported certainty in the management case.", "A tempting alternative double counts value or ignores a control."),
        expected_founder_interruptions=(
            {"decision_class": "D3", "reason": "Approve recommendation and material commitment."},
            {"decision_class": "D4", "reason": "Approve any external issue or irreversible action."},
        ),
        implementation_records=(
            {"initiative_id": f"{fixture_id}-INIT-001", "owner": owner, "stage": "design", "dependency": "Validated baseline"},
            {"initiative_id": f"{fixture_id}-INIT-002", "owner": "Programme lead", "stage": "pilot", "dependency": "Founder approval"},
        ),
        benefit_records=(
            {"benefit_id": f"{fixture_id}-BEN-001", "classification": "released_capacity", "owner": "Finance", "recognition_rule": "Recognise only after measured redeployment."},
            {"benefit_id": f"{fixture_id}-BEN-002", "classification": "potential_incremental_value", "owner": owner, "recognition_rule": "Recognise only after controlled outcome evidence."},
        ),
        specialist_reviews=("Finance or risk specialist review where the recommendation affects valuation, controls or workforce.",),
        prohibited_conclusions=tuple(defaults["prohibited_conclusions"]),
    )


def programme_document(programme: FixtureProgramme) -> dict[str, Any]:
    payload = programme.model_dump(mode="json")
    payload["programme_digest"] = programme_digest(programme)
    payload["agent_visible"] = True
    return payload


def programme_digest(programme: FixtureProgramme) -> str:
    payload = json.dumps(programme.model_dump(mode="json"), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def serialise_programme(programme: FixtureProgramme) -> str:
    return json.dumps(programme_document(programme), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_programme(seed_path: Path, destination: Path) -> Path:
    destination.write_text(serialise_programme(build_fixture_programme(seed_path)), encoding="utf-8")
    return destination


def verify_committed_programme(seed_path: Path, destination: Path) -> None:
    expected = serialise_programme(build_fixture_programme(seed_path))
    if not destination.exists() or destination.read_text(encoding="utf-8") != expected:
        raise ValueError("Committed additional primary fixture programme is stale or non-reproducible.")
