from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "configs" / "northstar-integration-blueprint.yaml"
OUTPUT_PATH = ROOT / "contracts" / "northstar-integration-blueprint.json"
LIFECYCLE_PATH = ROOT / "configs" / "lifecycle.yaml"
COMMANDS_PATH = ROOT / "contracts" / "command-event-catalogue.json"
MODELS_PATH = ROOT / "contracts" / "model-registry.json"
AGENTS_PATH = ROOT / "configs" / "agents.yaml"
ORACLE_PATH = ROOT / "fixtures" / "digital-ai" / "FIXTURE-DAI-001" / "oracle-baseline.json"
SEMANTIC_PATH = ROOT / "fixtures" / "digital-ai" / "FIXTURE-DAI-001" / "deliverable-semantic-baseline.json"
ADDITIONAL_FIXTURES_PATH = ROOT / "fixtures" / "additional-primary-fixtures.json"
PCR04_PATH = ROOT / "handoff" / "codex-phase0-handoff.json"
PCR05_PATH = ROOT / "contracts" / "runtime-adapter-contracts.json"
PCR06_PATH = ROOT / "contracts" / "hermes-compatibility-pack.json"


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def build_northstar_blueprint() -> dict[str, Any]:
    source = _load_yaml(SOURCE_PATH)
    lifecycle = _load_yaml(LIFECYCLE_PATH)
    catalogue = _load_json(COMMANDS_PATH)
    models = _load_json(MODELS_PATH)
    agents = _load_yaml(AGENTS_PATH)
    oracle = _load_json(ORACLE_PATH)
    semantic = _load_json(SEMANTIC_PATH)
    additional = _load_json(ADDITIONAL_FIXTURES_PATH)
    pcr04 = _load_json(PCR04_PATH)
    pcr05 = _load_json(PCR05_PATH)
    pcr06 = _load_json(PCR06_PATH)

    lifecycle_stages = lifecycle.get("stages", [])
    commands = catalogue.get("commands", {})
    events = catalogue.get("events", {})
    model_entries = models.get("models", {})
    agent_entries = agents.get("agents", [])
    oracle_data = oracle.get("oracle", {})
    semantic_data = semantic.get("semantic_model", {})
    journey = source.get("journey_stages", [])

    lifecycle_alignment = [
        (item.get("lifecycle_stage_id"), item.get("name"), item.get("exit_gate"))
        for item in journey
        if isinstance(item, dict)
    ] == [
        (item.get("id"), item.get("name"), item.get("exit_gate"))
        for item in lifecycle_stages
        if isinstance(item, dict)
    ]
    required_commands = {
        command
        for stage in journey
        if isinstance(stage, dict)
        for command in stage.get("command_sequence", [])
        if isinstance(command, str)
    }
    required_agents = {
        agent
        for stage in journey
        if isinstance(stage, dict)
        for agent in stage.get("primary_agents", [])
        if isinstance(agent, str)
    }
    declared_agents = {
        item.get("id") for item in agent_entries if isinstance(item, dict)
    }
    component_ids = {
        item.get("component_id")
        for item in source.get("integration_components", [])
        if isinstance(item, dict)
    }
    edges_valid = all(
        edge.get("from_component") in component_ids
        and edge.get("to_component") in component_ids
        for edge in source.get("integration_edges", [])
        if isinstance(edge, dict)
    )
    required_scenario_commands = {
        "cancel_engagement",
        "create_engagement",
        "propose_transition",
        "record_agent_output",
        "record_approval",
        "release_artefact",
        "request_approval",
        "update_mandate",
    }
    required_events = {
        "agent_output_recorded",
        "approval_recorded",
        "approval_requested",
        "artefact_released",
        "defect_recorded",
        "engagement_cancelled",
        "engagement_created",
        "mandate_updated",
        "transition_accepted",
        "transition_proposed",
        "workflow_blocked",
        "workflow_resumed",
    }
    idempotent_commands = {
        command_id
        for command_id, command in commands.items()
        if isinstance(command, dict) and command.get("idempotency") == "required"
    }
    checks = {
        "northstar_fixture_matches_oracle": oracle_data.get("fixture_id") == "FIXTURE-DAI-001",
        "northstar_fixture_matches_semantic": semantic_data.get("fixture_id")
        == "FIXTURE-DAI-001",
        "oracle_grade_passed": oracle.get("grade", {}).get("passed") is True,
        "semantic_grade_passed": semantic.get("grade", {}).get("passed") is True,
        "semantic_model_identity": semantic_data.get("semantic_model_id") == "DSM-DAI-001",
        "story_model_identity": semantic_data.get("story", {}).get("story_model_id")
        == "STORY-DAI-001",
        "lifecycle_alignment": lifecycle_alignment and len(journey) == 13,
        "required_commands_declared": required_commands <= set(commands),
        "required_scenario_commands_declared": required_scenario_commands <= set(commands),
        "required_events_declared": required_events <= set(events),
        "idempotent_release_and_cancel": {
            "release_artefact",
            "cancel_engagement",
        }
        <= idempotent_commands,
        "required_agents_declared": required_agents <= declared_agents,
        "component_edges_resolve": edges_valid,
        "model_contracts_available": all(
            name in model_entries
            for name in [
                "CommandEnvelope",
                "DomainEvent",
                "ContextPackage",
                "AgentEnvelope",
                "StoryModel",
                "DeliverableManifest",
                "QualityReview",
                "ApprovalRequest",
            ]
        ),
        "all_primary_fixture_types_present": len(additional.get("fixtures", [])) + 1 == 13,
        "pcr04_codex_start_unauthorized": pcr04.get("readiness_snapshot", {}).get(
            "codex_start_authorized"
        )
        is False,
        "pcr05_runtime_activation_unauthorized": pcr05.get("readiness_snapshot", {}).get(
            "runtime_activation_authorized"
        )
        is False,
        "pcr06_hermes_activation_unauthorized": pcr06.get("readiness_snapshot", {}).get(
            "hermes_activation_authorized"
        )
        is False,
    }
    readiness = {
        "lifecycle_stage_count": len(lifecycle_stages),
        "command_count": len(commands),
        "event_count": len(events),
        "model_count": len(model_entries),
        "agent_count": len(agent_entries),
        "primary_fixture_count": len(additional.get("fixtures", [])) + 1,
        "integration_component_count": len(source.get("integration_components", [])),
        "integration_edge_count": len(source.get("integration_edges", [])),
        "scenario_count": len(source.get("e2e_scenarios", [])),
        "implementation_wave_count": len(source.get("implementation_waves", [])),
        "oracle_grade_passed": checks["oracle_grade_passed"],
        "semantic_grade_passed": checks["semantic_grade_passed"],
        "pcr04_codex_start_authorized": False,
        "pcr05_runtime_activation_authorized": False,
        "pcr06_hermes_activation_authorized": False,
        "local_prerequisites_passed": all(checks.values()),
        "northstar_implementation_authorized": False,
    }
    output = dict(source)
    output["generated_from"] = "configs/northstar-integration-blueprint.yaml"
    output["readiness_snapshot"] = readiness
    return output


def main() -> None:
    output = build_northstar_blueprint()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(_canonical_json(output), encoding="utf-8")
    readiness = output["readiness_snapshot"]
    print(
        "Built PCR-07 Northstar integration blueprint: "
        f"{readiness['lifecycle_stage_count']} lifecycle stages, "
        f"{readiness['integration_component_count']} components, "
        f"{readiness['integration_edge_count']} edges, "
        f"{readiness['scenario_count']} scenarios, "
        f"local_prerequisites_passed={str(readiness['local_prerequisites_passed']).lower()}, "
        "northstar_implementation_authorized=false."
    )


if __name__ == "__main__":
    main()
