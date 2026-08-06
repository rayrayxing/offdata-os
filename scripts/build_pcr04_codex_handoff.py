from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "configs" / "codex-handoff.yaml"
OUTPUT_PATH = ROOT / "handoff" / "codex-phase0-handoff.json"
CANONICAL_RELEASE_PATH = ROOT / "releases" / "canonical-chat-first-phase1-7-release.json"
REFERENTIAL_BASELINE_PATH = ROOT / "requirements" / "referential-integrity-baseline.json"
REPOSITORY_BASELINE_PATH = ROOT / "repository" / "repository-governance-baseline.json"
RUNTIME_ADAPTER_PATH = ROOT / "contracts" / "runtime-adapter-contracts.json"
HERMES_COMPATIBILITY_PATH = ROOT / "contracts" / "hermes-compatibility-pack.json"
NORTHSTAR_BLUEPRINT_PATH = ROOT / "contracts" / "northstar-integration-blueprint.json"
INITIAL_OPERATING_CONTROLS_PATH = ROOT / "contracts" / "initial-operating-controls.json"


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


def _repository_gate(repository: dict[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for field in ("missing_required_files", "prohibited_tracked_paths", "case_collisions"):
        if repository.get(field):
            failures.append(field)
    workflow_checks = repository.get("workflow_checks")
    if not isinstance(workflow_checks, dict) or not workflow_checks:
        failures.append("workflow_checks")
    elif any(value is not True for value in workflow_checks.values()):
        failures.append("workflow_checks")
    if repository.get("real_client_data_allowed") is not False:
        failures.append("real_client_data_allowed")
    return not failures, sorted(set(failures))


def build_handoff() -> dict[str, Any]:
    source = _load_yaml(SOURCE_PATH)
    canonical = _load_json(CANONICAL_RELEASE_PATH)
    referential = _load_json(REFERENTIAL_BASELINE_PATH)
    repository = _load_json(REPOSITORY_BASELINE_PATH)
    runtime_adapters = _load_json(RUNTIME_ADAPTER_PATH)
    hermes = _load_json(HERMES_COMPATIBILITY_PATH)
    northstar = _load_json(NORTHSTAR_BLUEPRINT_PATH)
    operating_controls = _load_json(INITIAL_OPERATING_CONTROLS_PATH)

    repository_passed, repository_failures = _repository_gate(repository)
    canonical_boundaries = canonical.get("boundaries", {})
    canonical_passed = (
        canonical.get("phases") == [1, 2, 3, 4, 5, 6, 7]
        and canonical.get("final_validation", {}).get("conclusion") == "success"
        and canonical_boundaries.get("real_client_data_enabled") is False
        and canonical_boundaries.get("external_actions_authorised") is False
        and canonical_boundaries.get("founder_accountability_preserved") is True
    )
    referential_passed = (
        referential.get("status") == "pass"
        and referential.get("issues") == []
        and referential.get("counts", {}).get("requirements") == 123
        and referential.get("counts", {}).get("edges") == 604
    )

    runtime_boundaries = runtime_adapters.get("boundaries", {})
    runtime_readiness = runtime_adapters.get("readiness_snapshot", {})
    runtime_passed = (
        runtime_adapters.get("phase_id") == "PCR-05"
        and runtime_readiness.get("local_prerequisites_passed") is True
        and runtime_readiness.get("runtime_activation_authorized") is False
        and runtime_boundaries.get("runtime_activation_authorized") is False
        and runtime_boundaries.get("real_client_data_enabled") is False
        and runtime_boundaries.get("external_actions_authorized") is False
        and runtime_boundaries.get("founder_accountability_preserved") is True
    )

    hermes_boundaries = hermes.get("boundaries", {})
    hermes_readiness = hermes.get("readiness_snapshot", {})
    hermes_passed = (
        hermes.get("phase_id") == "PCR-06"
        and hermes_readiness.get("local_prerequisites_passed") is True
        and hermes_readiness.get("hermes_activation_authorized") is False
        and hermes_boundaries.get("runtime_memory_is_canonical") is False
        and hermes_boundaries.get("external_actions_authorized") is False
        and hermes_boundaries.get("founder_accountability_preserved") is True
    )

    northstar_boundaries = northstar.get("boundaries", {})
    northstar_readiness = northstar.get("readiness_snapshot", {})
    northstar_passed = (
        northstar.get("phase_id") == "PCR-07"
        and northstar_readiness.get("local_prerequisites_passed") is True
        and northstar_readiness.get("northstar_implementation_authorized") is False
        and northstar_readiness.get("oracle_grade_passed") is True
        and northstar_readiness.get("semantic_grade_passed") is True
        and northstar_boundaries.get("release_mode") == "internal_synthetic_only"
        and northstar_boundaries.get("real_client_data_enabled") is False
        and northstar_boundaries.get("founder_accountability_preserved") is True
    )

    operating_boundaries = operating_controls.get("boundaries", {})
    operating_readiness = operating_controls.get("readiness_snapshot", {})
    operating_passed = (
        operating_controls.get("phase_id") == "PCR-08"
        and operating_readiness.get("local_prerequisites_passed") is True
        and operating_readiness.get("initial_operating_controls_activation_authorized") is False
        and operating_readiness.get("hosted_control_evidence_complete") is False
        and operating_readiness.get("operating_environment_evidence_complete") is False
        and operating_readiness.get("production_evidence_complete") is False
        and operating_boundaries.get("codex_start_authorized") is False
        and operating_boundaries.get("runtime_activation_authorized") is False
        and operating_boundaries.get("real_client_data_enabled") is False
        and operating_boundaries.get("founder_accountability_preserved") is True
    )

    readiness: dict[str, Any] = {
        "canonical_release": {
            "passed": canonical_passed,
            "release_id": canonical.get("release_id"),
            "phases": canonical.get("phases"),
            "final_validation_conclusion": canonical.get("final_validation", {}).get("conclusion"),
            "boundaries": canonical_boundaries,
        },
        "referential_integrity": {
            "passed": referential_passed,
            "status": referential.get("status"),
            "issue_count": len(referential.get("issues", [])),
            "counts": referential.get("counts", {}),
            "report_digest": referential.get("report_digest"),
        },
        "repository_governance": {
            "passed": repository_passed,
            "failures": repository_failures,
            "required_file_count": len(repository.get("required_files", [])),
            "workflow_invariant_count": len(repository.get("workflow_checks", {})),
            "hosted_settings_required_before_codex": repository.get("hosted_settings_required_before_codex", []),
        },
        "runtime_adapters": {
            "passed": runtime_passed,
            "contract_id": runtime_adapters.get("contract_id"),
            "adapter_kind_count": len(runtime_adapters.get("adapter_kinds", [])),
            "adapter_profile_count": len(runtime_adapters.get("adapter_profiles", [])),
            "tool_class_count": len(runtime_adapters.get("tool_classes", [])),
            "conformance_case_count": len(runtime_adapters.get("conformance_cases", [])),
            "runtime_activation_authorized": runtime_readiness.get("runtime_activation_authorized"),
            "boundaries": runtime_boundaries,
        },
        "hermes_compatibility": {
            "passed": hermes_passed,
            "contract_id": hermes.get("contract_id"),
            "compatibility_surface_count": len(hermes.get("compatibility_surfaces", [])),
            "capability_mapping_count": len(hermes.get("tool_mapping", [])),
            "repository_skill_count": hermes_readiness.get("repository_skill_count"),
            "hermes_activation_authorized": hermes_readiness.get("hermes_activation_authorized"),
            "boundaries": hermes_boundaries,
        },
        "northstar_blueprint": {
            "passed": northstar_passed,
            "contract_id": northstar.get("contract_id"),
            "lifecycle_stage_count": northstar_readiness.get("lifecycle_stage_count"),
            "integration_component_count": northstar_readiness.get("integration_component_count"),
            "scenario_count": northstar_readiness.get("scenario_count"),
            "implementation_wave_count": northstar_readiness.get("implementation_wave_count"),
            "northstar_implementation_authorized": northstar_readiness.get("northstar_implementation_authorized"),
            "boundaries": northstar_boundaries,
        },
        "initial_operating_controls": {
            "passed": operating_passed,
            "contract_id": operating_controls.get("contract_id"),
            "control_domain_count": operating_readiness.get("control_domain_count"),
            "security_control_count": operating_readiness.get("security_control_count"),
            "operating_gate_count": operating_readiness.get("operating_gate_count"),
            "control_switch_count": operating_readiness.get("control_switch_count"),
            "hosted_control_evidence_complete": operating_readiness.get("hosted_control_evidence_complete"),
            "operating_environment_evidence_complete": operating_readiness.get("operating_environment_evidence_complete"),
            "production_evidence_complete": operating_readiness.get("production_evidence_complete"),
            "initial_operating_controls_activation_authorized": operating_readiness.get("initial_operating_controls_activation_authorized"),
            "boundaries": operating_boundaries,
        },
    }
    readiness["local_prerequisites_passed"] = all(
        item.get("passed") is True
        for key, item in readiness.items()
        if key in {
            "canonical_release", "referential_integrity", "repository_governance",
            "runtime_adapters", "hermes_compatibility", "northstar_blueprint",
            "initial_operating_controls",
        }
    )
    readiness["codex_start_authorized"] = False
    readiness["activation_blockers"] = source.get("activation_conditions", [])

    output = dict(source)
    output["generated_from"] = "configs/codex-handoff.yaml"
    output["readiness_snapshot"] = readiness
    return output


def main() -> None:
    handoff = build_handoff()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(_canonical_json(handoff), encoding="utf-8")
    readiness = handoff["readiness_snapshot"]
    print(
        "Built PCR-04 Codex handoff: "
        f"{len(handoff['task_graph'])} Phase 0 tasks, "
        f"{len(handoff['read_order'])} read-order files, "
        f"{len(handoff['prerequisite_records'])} prerequisite records, "
        f"local_prerequisites_passed={str(readiness['local_prerequisites_passed']).lower()}, "
        "codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
