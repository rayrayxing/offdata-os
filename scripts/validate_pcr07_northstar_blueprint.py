from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Callable

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from build_pcr07_northstar_blueprint import build_northstar_blueprint

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "configs" / "northstar-integration-blueprint.yaml"
CONTRACT_PATH = ROOT / "contracts" / "northstar-integration-blueprint.json"
SCHEMA_PATH = ROOT / "schemas" / "northstar-integration-blueprint.schema.json"
DOC_PATH = ROOT / "docs" / "46-PCR-07-NORTHSTAR-END-TO-END-INTEGRATION-BLUEPRINT.md"
Mutation = Callable[[dict[str, Any]], None]


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _set_path(value: dict[str, Any], path: tuple[str, ...], replacement: Any) -> None:
    cursor: dict[str, Any] = value
    for key in path[:-1]:
        next_value = cursor[key]
        if not isinstance(next_value, dict):
            raise AssertionError(f"Mutation path is not a mapping: {path}")
        cursor = next_value
    cursor[path[-1]] = replacement


def _validate_semantics(contract: dict[str, Any]) -> None:
    activation = contract["activation"]
    boundaries = contract["boundaries"]
    readiness = contract["readiness_snapshot"]
    _assert(contract["phase_id"] == "PCR-07", "Phase identity drifted")
    _assert(contract["status"] == "integration_blueprint_only", "Blueprint status drifted")
    _assert(contract["northstar_fixture"]["fixture_id"] == "FIXTURE-DAI-001", "Fixture drifted")
    _assert(contract["northstar_fixture"]["semantic_model_id"] == "DSM-DAI-001", "Semantic model drifted")
    _assert(contract["northstar_fixture"]["story_model_id"] == "STORY-DAI-001", "Story model drifted")
    denied = [
        "implementation_authorized",
        "runtime_activation_authorized",
        "hermes_activation_authorized",
        "codex_start_authorized",
        "real_client_data_enabled",
        "external_actions_authorized",
        "production_deployment_authorized",
        "paid_services_authorized",
        "autonomous_merge_authorized",
    ]
    _assert(all(activation[key] is False for key in denied), "A denied activation was enabled")
    _assert(boundaries["founder_accountability_preserved"] is True, "Founder accountability removed")
    _assert(boundaries["canonical_write_mode"] == "commands_only", "Command-only writes weakened")
    _assert(boundaries["runtime_memory_is_canonical"] is False, "Runtime memory became canonical")
    _assert(boundaries["release_mode"] == "internal_synthetic_only", "External release enabled")
    _assert(
        all(
            boundaries[key] is False
            for key in [
                "external_send_enabled",
                "real_client_data_enabled",
                "production_deployment_enabled",
                "paid_services_enabled",
                "autonomous_merge_enabled",
                "phase_progression_authorized",
            ]
        ),
        "A prohibited boundary was enabled",
    )

    stages = contract["journey_stages"]
    _assert(len(stages) == 13, "Exactly thirteen lifecycle stages are required")
    _assert([stage["sequence"] for stage in stages] == list(range(1, 14)), "Stage sequence drifted")
    _assert(
        [stage["lifecycle_stage_id"] for stage in stages]
        == [f"LIFE-STAGE-{index:02d}" for index in range(1, 14)],
        "Lifecycle identity drifted",
    )
    _assert(
        [stage["exit_gate"] for stage in stages]
        == [f"GATE-{index:02d}" for index in range(1, 14)],
        "Gate sequence drifted",
    )
    _assert(all(stage["restart_safe"] is True for stage in stages), "A stage is not restart-safe")
    _assert(all(stage["canonical_write_mode"] == "commands_only" for stage in stages), "A stage bypasses commands")
    release_stage = stages[8]
    _assert(release_stage["founder_gate_required"] is True, "Release Founder gate removed")
    _assert("independent_quality" in release_stage["primary_agents"], "Independent quality removed")
    _assert("record_approval" in release_stage["command_sequence"], "Release approval missing")
    _assert("release_artefact" in release_stage["command_sequence"], "Release command missing")

    components = {item["component_id"]: item for item in contract["integration_components"]}
    _assert(len(components) == 13, "Exactly thirteen integration components are required")
    canonical = {key for key, item in components.items() if item["canonical_owner"]}
    _assert(canonical == {"COMP-STATE", "COMP-OBJECT"}, "Canonical ownership drifted")
    _assert(len(contract["integration_edges"]) == 20, "Exactly twenty integration edges are required")
    _assert(
        all(
            edge["from_component"] in components and edge["to_component"] in components
            for edge in contract["integration_edges"]
        ),
        "An integration edge is unresolved",
    )

    scenarios = {item["name"]: item for item in contract["e2e_scenarios"]}
    _assert(
        set(scenarios)
        == {
            "synthetic_happy_path",
            "restart_after_analysis_checkpoint",
            "approval_wait_and_resume",
            "blocking_quality_defect_recycle",
            "idempotent_release_replay",
            "founder_cancellation",
            "tenant_and_data_boundary_rejection",
        },
        "E2E scenario set drifted",
    )
    _assert(scenarios["idempotent_release_replay"]["expected_terminal_state"] == "completed", "Replay outcome drifted")
    _assert(scenarios["tenant_and_data_boundary_rejection"]["expected_terminal_state"] == "blocked", "Data boundary no longer blocks")

    waves = contract["implementation_waves"]
    _assert(len(waves) == 8, "Exactly eight implementation waves are required")
    _assert(waves[0]["depends_on"] == [], "First wave dependency drifted")
    _assert(
        all(waves[index]["depends_on"] == [waves[index - 1]["wave_id"]] for index in range(1, 8)),
        "Wave dependency chain drifted",
    )
    expected_counts = {
        "lifecycle_stage_count": 13,
        "command_count": 10,
        "event_count": 15,
        "model_count": 58,
        "agent_count": 11,
        "primary_fixture_count": 13,
        "integration_component_count": 13,
        "integration_edge_count": 20,
        "scenario_count": 7,
        "implementation_wave_count": 8,
    }
    _assert(all(readiness[key] == value for key, value in expected_counts.items()), "Readiness counts drifted")
    _assert(readiness["oracle_grade_passed"] is True, "Oracle baseline does not pass")
    _assert(readiness["semantic_grade_passed"] is True, "Semantic baseline does not pass")
    _assert(readiness["local_prerequisites_passed"] is True, "Local prerequisites do not pass")
    _assert(readiness["northstar_implementation_authorized"] is False, "Implementation was authorized")


def _mutation_cases() -> list[tuple[str, Mutation]]:
    cases: list[tuple[str, Mutation]] = []

    def add(path: tuple[str, ...], replacement: Any, name: str) -> None:
        def mutate(value: dict[str, Any]) -> None:
            _set_path(value, path, replacement)
        cases.append((name, mutate))

    add(("phase_id",), "PCR-08", "change phase identity")
    add(("northstar_fixture", "fixture_id"), "FIXTURE-OTHER", "replace fixture")
    for key in [
        "implementation_authorized",
        "runtime_activation_authorized",
        "hermes_activation_authorized",
        "codex_start_authorized",
        "real_client_data_enabled",
        "external_actions_authorized",
        "production_deployment_authorized",
        "paid_services_authorized",
        "autonomous_merge_authorized",
    ]:
        add(("activation", key), True, f"enable {key}")
    add(("boundaries", "canonical_write_mode"), "direct", "allow direct writes")
    add(("boundaries", "runtime_memory_is_canonical"), True, "make memory canonical")
    add(("boundaries", "release_mode"), "external_client_release", "enable external release")
    add(("readiness_snapshot", "northstar_implementation_authorized"), True, "authorize implementation")

    def remove_stage(value: dict[str, Any]) -> None:
        value["journey_stages"].pop()

    def change_gate(value: dict[str, Any]) -> None:
        value["journey_stages"][8]["exit_gate"] = "GATE-08"

    def remove_quality(value: dict[str, Any]) -> None:
        value["journey_stages"][8]["primary_agents"].remove("independent_quality")

    def remove_approval(value: dict[str, Any]) -> None:
        value["journey_stages"][8]["command_sequence"].remove("record_approval")

    def remove_restart(value: dict[str, Any]) -> None:
        value["e2e_scenarios"] = [
            item for item in value["e2e_scenarios"]
            if item["name"] != "restart_after_analysis_checkpoint"
        ]

    def make_qa_canonical(value: dict[str, Any]) -> None:
        next(item for item in value["integration_components"] if item["component_id"] == "COMP-QA")["canonical_owner"] = True

    def break_edge(value: dict[str, Any]) -> None:
        value["integration_edges"][0]["to_component"] = "COMP-MISSING"

    def break_wave(value: dict[str, Any]) -> None:
        value["implementation_waves"][4]["depends_on"] = []

    cases.extend(
        [
            ("remove lifecycle stage", remove_stage),
            ("misalign release gate", change_gate),
            ("remove independent quality", remove_quality),
            ("remove release approval", remove_approval),
            ("remove restart scenario", remove_restart),
            ("make QA canonical", make_qa_canonical),
            ("create unresolved edge", break_edge),
            ("break wave chain", break_wave),
        ]
    )
    return cases


def main() -> None:
    source = _load_yaml(SOURCE_PATH)
    contract = _load_json(CONTRACT_PATH)
    schema = _load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(contract), key=lambda item: list(item.path))
    _assert(not errors, "Schema validation failed: " + "; ".join(error.message for error in errors))
    _assert(
        _canonical_json(build_northstar_blueprint()) == CONTRACT_PATH.read_text(encoding="utf-8"),
        "Generated Northstar blueprint is stale",
    )
    _assert(source["contract_id"] == contract["contract_id"], "Source and generated IDs differ")
    _validate_semantics(contract)
    documentation = DOC_PATH.read_text(encoding="utf-8")
    for token in [
        "PCR-07",
        "FIXTURE-DAI-001",
        "thirteen lifecycle stages",
        "internal_synthetic_only",
        "northstar_implementation_authorized=false",
        "restart",
        "independent quality",
    ]:
        _assert(token in documentation, f"PCR-07 documentation missing {token}")
    rejected = 0
    for name, mutate in _mutation_cases():
        candidate = copy.deepcopy(contract)
        mutate(candidate)
        try:
            if list(validator.iter_errors(candidate)):
                rejected += 1
                continue
            _validate_semantics(candidate)
        except (AssertionError, KeyError, TypeError, ValueError):
            rejected += 1
            continue
        raise AssertionError(f"Mutation was not rejected: {name}")
    readiness = contract["readiness_snapshot"]
    print(
        "PCR-07 Northstar end-to-end integration blueprint passed: "
        f"{readiness['lifecycle_stage_count']} lifecycle stages, "
        f"{readiness['integration_component_count']} components, "
        f"{readiness['integration_edge_count']} edges, "
        f"{readiness['scenario_count']} scenarios, "
        f"{len(_mutation_cases())} mutation cases rejected, "
        "local_prerequisites_passed=true, northstar_implementation_authorized=false."
    )


if __name__ == "__main__":
    main()
