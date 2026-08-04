from __future__ import annotations

import ast
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import yaml
from jsonschema import Draft202012Validator

from offdata_core.api_contracts import (
    ApiError,
    ApprovalRequirement,
    CommandDisposition,
    CommandResponse,
    EngagementStatus,
    EngagementView,
)
from offdata_core.events import ActorRef, ActorType, CommandType, EventType
from offdata_core.models import DecisionClass, LifecycleStage, OperationalState
from offdata_core.quality import AssuranceTier
from offdata_core.registry import (
    MODEL_REGISTRY,
    build_alias_schema,
    build_command_event_catalogue,
    build_config_schema,
    build_model_registry_document,
    build_openapi_document,
    build_schema_bundle,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def _read_json(path: str) -> dict[str, Any]:
    parsed = json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(parsed, dict)
    return parsed


def _read_yaml(path: str) -> dict[str, Any]:
    parsed = yaml.safe_load((REPO_ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(parsed, dict)
    return parsed


def _normalised(document: dict[str, Any]) -> str:
    return json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _collect_external_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str) and ref.startswith("../schemas/"):
            refs.add(ref)
        for child in value.values():
            refs.update(_collect_external_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_collect_external_refs(child))
    return refs


def _collected_test_nodes() -> set[str]:
    nodes: set[str] = set()
    tests_root = REPO_ROOT / "packages" / "offdata-core" / "tests"
    for path in sorted(tests_root.glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        relative = path.relative_to(REPO_ROOT).as_posix()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
                "test_"
            ):
                nodes.add(f"{relative}::{node.name}")
    return nodes


def test_model_registry_contains_all_public_contract_families() -> None:
    # Requirements: AGENT-009, DATA-001
    required = {
        "StageDetectionResult",
        "PolicyResult",
        "AgentEnvelope",
        "FounderDecisionPacket",
        "SourceDocument",
        "MethodRecord",
        "CommandEnvelope",
        "DomainEvent",
        "QualityReview",
        "StoryModel",
        "VisualSpecification",
        "Organisation",
        "OpportunityDossier",
        "EngagementView",
        "CommandResponse",
    }
    assert required <= set(MODEL_REGISTRY)
    assert len(MODEL_REGISTRY) >= 58


def test_schema_bundle_is_valid_draft_2020_12() -> None:
    # Requirements: AGENT-005, DATA-005
    bundle = build_schema_bundle()
    Draft202012Validator.check_schema(bundle)
    assert bundle["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert set(MODEL_REGISTRY) <= set(bundle["$defs"])


def test_committed_schema_bundle_matches_pydantic_models() -> None:
    # Requirements: DATA-003, AGENT-009
    committed = _read_json("schemas/offdata-contract-bundle.schema.json")
    assert _normalised(committed) == _normalised(build_schema_bundle())


def test_standalone_schema_aliases_point_to_canonical_bundle() -> None:
    # Requirements: AGENT-005, AGENT-009, DATA-005
    aliases = {
        "schemas/agent-envelope.schema.json": (
            "AgentEnvelope",
            "agent-envelope.schema.json",
            "Offdata Agent Envelope",
        ),
        "schemas/context-package.schema.json": (
            "ContextPackage",
            "context-package.schema.json",
            "Offdata Minimum-Sufficient Context Package",
        ),
        "schemas/founder-decision-packet.schema.json": (
            "FounderDecisionPacket",
            "founder-decision-packet.schema.json",
            "Offdata Founder Decision Packet",
        ),
    }
    for path, arguments in aliases.items():
        committed = _read_json(path)
        expected = build_alias_schema(*arguments)
        Draft202012Validator.check_schema(committed)
        assert committed == expected
        assert committed["$ref"].endswith(f"#/$defs/{arguments[0]}")


def test_config_documents_validate_against_committed_config_schema() -> None:
    # Requirements: LIFE-001, AUTH-001, AGENT-001, QA-002
    committed = _read_json("schemas/offdata-configs.schema.json")
    expected = build_config_schema()
    Draft202012Validator.check_schema(committed)
    assert committed == expected

    validators = {
        "configs/lifecycle.yaml": "LifecycleConfig",
        "configs/policy.yaml": "PolicyConfig",
        "configs/agents.yaml": "AgentsConfig",
        "requirements/test-registry.json": "TestRegistry",
    }
    for path, definition in validators.items():
        document = _read_json(path) if path.endswith(".json") else _read_yaml(path)
        validation_schema = {
            "$schema": committed["$schema"],
            "$defs": committed["$defs"],
            "$ref": f"#/$defs/{definition}",
        }
        Draft202012Validator(validation_schema).validate(document)


def test_model_registry_references_existing_schema_definitions() -> None:
    # Requirements: DATA-005
    document = build_model_registry_document()
    definitions = set(build_schema_bundle()["$defs"])
    for record in document["models"].values():
        definition = record["schema_ref"].split("#/$defs/", maxsplit=1)[1]
        assert definition in definitions


def test_openapi_is_31_and_has_required_paths() -> None:
    # Requirements: DATA-005, OUT-003
    document = build_openapi_document()
    assert document["openapi"].startswith("3.1.")
    required_paths = {
        "/health",
        "/v1/engagements",
        "/v1/engagements/{engagement_id}",
        "/v1/engagements/{engagement_id}/commands",
        "/v1/engagements/{engagement_id}/events",
        "/v1/engagements/{engagement_id}/timeline",
        "/v1/engagements/{engagement_id}/pause",
        "/v1/engagements/{engagement_id}/resume",
        "/v1/engagements/{engagement_id}/cancel",
        "/v1/engagements/{engagement_id}/mandate",
        "/v1/engagements/{engagement_id}/decisions",
        "/v1/engagements/{engagement_id}/hypotheses",
        "/v1/engagements/{engagement_id}/method-selections",
        "/v1/engagements/{engagement_id}/claims",
        "/v1/engagements/{engagement_id}/evidence",
        "/v1/engagements/{engagement_id}/analyses",
        "/v1/engagements/{engagement_id}/recommendations",
        "/v1/engagements/{engagement_id}/quality-findings",
        "/v1/engagements/{engagement_id}/approvals",
        "/v1/engagements/{engagement_id}/deliverables",
        "/v1/engagements/{engagement_id}/initiatives",
        "/v1/engagements/{engagement_id}/benefits",
    }
    assert required_paths <= set(document["paths"])


def test_openapi_external_schema_references_resolve() -> None:
    # Requirements: DATA-005
    document = build_openapi_document()
    definitions = set(build_schema_bundle()["$defs"])
    refs = _collect_external_refs(document)
    assert refs
    for ref in refs:
        assert ref.startswith("../schemas/offdata-contract-bundle.schema.json#/$defs/")
        assert ref.split("#/$defs/", maxsplit=1)[1] in definitions


def test_command_catalogue_covers_every_command_enum() -> None:
    # Requirements: DATA-004
    catalogue = build_command_event_catalogue()
    assert set(catalogue["commands"]) == {item.value for item in CommandType}


def test_event_catalogue_covers_every_event_enum() -> None:
    # Requirements: DATA-004
    catalogue = build_command_event_catalogue()
    assert set(catalogue["events"]) == {item.value for item in EventType}


def test_non_repeatable_commands_require_idempotency() -> None:
    # Requirements: LIFE-007, DATA-004
    commands = build_command_event_catalogue()["commands"]
    required = {
        CommandType.REQUEST_APPROVAL.value,
        CommandType.RECORD_APPROVAL.value,
        CommandType.PROPOSE_EXTERNAL_ACTION.value,
        CommandType.EXECUTE_EXTERNAL_ACTION.value,
        CommandType.CANCEL_ENGAGEMENT.value,
        CommandType.RECORD_AGENT_OUTPUT.value,
        CommandType.RELEASE_ARTEFACT.value,
    }
    assert all(commands[name]["idempotency"] == "required" for name in required)


def test_lifecycle_config_matches_python_stage_order() -> None:
    # Requirements: LIFE-001, LIFE-002
    config = _read_yaml("configs/lifecycle.yaml")
    stages = config["stages"]
    assert [stage["id"] for stage in stages] == [stage.value for stage in LifecycleStage]
    assert [stage["exit_gate"] for stage in stages] == [
        f"GATE-{index:02d}" for index in range(1, 14)
    ]
    assert config["stage_selection_rule"] == "earliest_unmet_mandatory_gate"


def test_policy_config_covers_every_decision_class() -> None:
    # Requirements: AUTH-001
    config = _read_yaml("configs/policy.yaml")
    assert set(config["decision_classes"]) == {item.value for item in DecisionClass}
    assert config["strictest_class_governs"] is True


def test_agent_config_has_bounded_roles_and_propose_only_writes() -> None:
    # Requirements: AGENT-001, AGENT-003, AGENT-004
    config = _read_yaml("configs/agents.yaml")
    agents = config["agents"]
    assert len(agents) == 11
    assert len({agent["id"] for agent in agents}) == 11
    assert config["default_write_mode"] == "propose_only"
    assert config["canonical_writes_via_commands_only"] is True
    assert all(agent["prohibited_actions"] for agent in agents)
    assert all("external_send" not in agent["permitted_tool_classes"] for agent in agents)


def test_every_collected_test_has_requirement_mapping() -> None:
    # Requirements: QA-002, DATA-004
    registry = _read_json("requirements/test-registry.json")
    mapped = {item["node_id"] for item in registry["implemented_tests"]}
    collected = _collected_test_nodes()
    assert collected <= mapped, f"Unmapped tests: {sorted(collected - mapped)}"
    assert all(item["requirements"] for item in registry["implemented_tests"])


def test_traceability_declares_test_or_planned_test_for_every_family_requirement() -> None:
    # Requirements: QA-002
    traceability = _read_yaml("requirements/traceability.yaml")
    registry = _read_json("requirements/test-registry.json")
    covered = {
        requirement
        for test in registry["implemented_tests"] + registry["planned_tests"]
        for requirement in test["requirements"]
    }
    for family in traceability["families"].values():
        assert family["implemented_tests"] or family["planned_tests"]
        assert set(family["requirements"]) <= covered


def test_sql_migration_contains_tenant_scope_event_store_and_idempotency() -> None:
    # Requirements: DATA-002, DATA-004, LIFE-007, SEC-002
    sql = (REPO_ROOT / "database/migrations/0001_core.sql").read_text(encoding="utf-8")
    lower = sql.lower()
    assert "begin;" in lower[:1000]
    assert lower.rstrip().endswith("commit;")
    for required in (
        "create table tenants",
        "create table engagements",
        "create table commands",
        "create table domain_events",
        "create table idempotency_records",
        "tenant_id",
        "enable row level security",
        "create policy",
    ):
        assert required in lower


def test_api_command_response_enforces_accepted_shape() -> None:
    # Requirements: DATA-004
    response = CommandResponse(
        command_id="CMD-1",
        status=CommandDisposition.ACCEPTED,
        aggregate_id="ENG-1",
        aggregate_version=1,
        event_ids=("EVT-1",),
    )
    assert response.aggregate_version == 1
    with pytest.raises(ValueError, match="emitted event"):
        CommandResponse(
            command_id="CMD-2",
            status=CommandDisposition.ACCEPTED,
            aggregate_id="ENG-1",
            aggregate_version=2,
        )


def test_api_pending_approval_requires_requirement() -> None:
    # Requirements: AUTH-003, AUTH-009
    with pytest.raises(ValueError, match="approval_requirement"):
        CommandResponse(command_id="CMD-1", status=CommandDisposition.PENDING_APPROVAL)

    requirement = ApprovalRequirement(
        decision_classes=frozenset({DecisionClass.MATERIAL}),
        required_approver_roles=("Founder",),
        supporting_packet_reference="PACK-1",
        latest_responsible_date=datetime(2026, 8, 5, tzinfo=UTC),
        reason="Material pilot commitment.",
    )
    response = CommandResponse(
        command_id="CMD-2",
        status=CommandDisposition.PENDING_APPROVAL,
        approval_requirement=requirement,
    )
    assert response.approval_requirement is not None


def test_engagement_view_enforces_status_alignment() -> None:
    # Requirements: LIFE-005
    actor = ActorRef(actor_id="founder", actor_type=ActorType.FOUNDER)
    now = datetime(2026, 8, 4, tzinfo=UTC)
    with pytest.raises(ValueError, match="cancelled status"):
        EngagementView(
            engagement_id="ENG-1",
            tenant_id="TEN-1",
            engagement_code="E-001",
            title="Test",
            client_organisation_id="ORG-1",
            status=EngagementStatus.ACTIVE,
            lifecycle_stage=LifecycleStage.MANDATE_INTAKE,
            operational_state=OperationalState.CANCELLED,
            assurance_tier=AssuranceTier.T1_MODERATE,
            data_region="sg",
            supported_decision="Select pilot.",
            version=1,
            created_at=now,
            created_by=actor,
            updated_at=now,
        )


def test_rejected_api_response_requires_error() -> None:
    error = ApiError(
        error_id="ERR-1",
        code="VALIDATION_ERROR",
        message="Invalid input.",
        correlation_id="COR-1",
    )
    response = CommandResponse(
        command_id="CMD-1",
        status=CommandDisposition.REJECTED,
        errors=(error,),
    )
    assert response.errors[0].code == "VALIDATION_ERROR"
