from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "configs" / "codex-handoff.yaml"
OUTPUT_PATH = ROOT / "handoff" / "codex-phase0-handoff.json"

DEPENDENCIES = {
    "canonical_release": ROOT / "releases" / "canonical-chat-first-phase1-7-release.json",
    "referential_integrity": ROOT / "requirements" / "referential-integrity-baseline.json",
    "repository_governance": ROOT / "repository" / "repository-governance-baseline.json",
    "runtime_adapters": ROOT / "contracts" / "runtime-adapter-contracts.json",
    "hermes_compatibility": ROOT / "contracts" / "hermes-compatibility-pack.json",
    "northstar_blueprint": ROOT / "contracts" / "northstar-integration-blueprint.json",
    "initial_operating_controls": ROOT / "contracts" / "initial-operating-controls.json",
    "pre_codex_readiness": ROOT / "contracts" / "pre-codex-readiness.json",
    "workstream4_readiness": ROOT / "contracts" / "workstream4-readiness.json",
    "workstream5_launch_control": ROOT / "contracts" / "codex-phase0-launch-control.json",
    "workstream6_baseline_lock": ROOT / "contracts" / "workstream6-final-reconciliation.json",
    "workstream6_handoff_reconciliation": ROOT / "contracts" / "workstream6-handoff-reconciliation.json",
}

MERGED_ACTIVATION_CONDITIONS = {
    "pcr03_merged_to_main",
    "pcr04_merged_to_main",
    "pcr05_merged_to_main",
    "pcr06_merged_to_main",
    "pcr07_merged_to_main",
    "pcr08_merged_to_main",
    "pcr09_merged_to_main",
    "pcr10_merged_to_main",
    "workstream4_repository_package_merged_to_main",
    "workstream5_launch_control_merged_to_main",
    "workstream6_final_reconciliation_merged_to_main",
}


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
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ) + "\n"


def _all_false(record: dict[str, Any], fields: tuple[str, ...]) -> bool:
    return all(record.get(field) is False for field in fields)


def _dependency_readiness(*, check_dependencies: bool) -> dict[str, Any]:
    if not check_dependencies:
        return {
            "canonical_release": {"passed": True, "required_status": "success"},
            "referential_integrity": {
                "passed": True,
                "required_status": "passed",
                "unresolved_references": 0,
            },
            "repository_governance": {"passed": True, "required_status": "passed"},
            "runtime_adapters": {
                "passed": True,
                "runtime_activation_authorized": False,
            },
            "hermes_compatibility": {
                "passed": True,
                "hermes_activation_authorized": False,
            },
            "northstar_blueprint": {
                "passed": True,
                "northstar_implementation_authorized": False,
            },
            "initial_operating_controls": {
                "passed": True,
                "initial_operating_controls_activation_authorized": False,
            },
            "pre_codex_readiness": {
                "passed": True,
                "release_integration_complete": True,
                "codex_start_authorized": False,
            },
            "workstream4_readiness": {
                "passed": True,
                "repository_side_prerequisites_passed": True,
                "hosted_controls_verified": False,
                "clean_macos_environment_verified": False,
            },
            "workstream5_launch_control": {
                "passed": True,
                "repository_launch_control_complete": True,
                "launch_permit_issued": False,
                "codex_start_authorized": False,
            },
            "workstream6_baseline_lock": {
                "passed": True,
                "baseline_locked": True,
                "final_reconciliation_complete": False,
                "codex_start_authorized": False,
            },
            "workstream6_handoff_reconciliation": {
                "passed": True,
                "handoff_reconciled": True,
                "closed_defects": ["WS6-BLOCK-001", "WS6-BLOCK-002"],
                "codex_start_authorized": False,
            },
        }

    records = {name: _load_json(path) for name, path in DEPENDENCIES.items()}

    canonical = records["canonical_release"]
    canonical_boundaries = canonical.get("boundaries", {})
    canonical_passed = (
        canonical.get("phases") == [1, 2, 3, 4, 5, 6, 7]
        and canonical.get("final_validation", {}).get("conclusion") == "success"
        and canonical_boundaries.get("real_client_data_enabled") is False
        and canonical_boundaries.get("external_actions_authorised") is False
        and canonical_boundaries.get("founder_accountability_preserved") is True
    )

    referential = records["referential_integrity"]
    referential_passed = (
        referential.get("status") == "pass"
        and referential.get("issues") == []
        and referential.get("counts", {}).get("requirements") == 123
        and referential.get("counts", {}).get("edges") == 604
    )

    repository = records["repository_governance"]
    repository_passed = (
        repository.get("missing_required_files") == []
        and repository.get("prohibited_tracked_paths") == []
        and repository.get("case_collisions") == []
        and isinstance(repository.get("workflow_checks"), dict)
        and bool(repository.get("workflow_checks"))
        and all(repository["workflow_checks"].values())
        and repository.get("real_client_data_allowed") is False
    )

    runtime = records["runtime_adapters"]
    runtime_snapshot = runtime.get("readiness_snapshot", {})
    runtime_boundaries = runtime.get("boundaries", {})
    runtime_passed = (
        runtime.get("phase_id") == "PCR-05"
        and runtime_snapshot.get("local_prerequisites_passed") is True
        and runtime_snapshot.get("runtime_activation_authorized") is False
        and runtime_boundaries.get("runtime_activation_authorized") is False
        and runtime_boundaries.get("real_client_data_enabled") is False
    )

    hermes = records["hermes_compatibility"]
    hermes_snapshot = hermes.get("readiness_snapshot", {})
    hermes_boundaries = hermes.get("boundaries", {})
    hermes_passed = (
        hermes.get("phase_id") == "PCR-06"
        and hermes_snapshot.get("local_prerequisites_passed") is True
        and hermes_snapshot.get("hermes_activation_authorized") is False
        and hermes_boundaries.get("external_actions_authorized") is False
    )

    northstar = records["northstar_blueprint"]
    northstar_snapshot = northstar.get("readiness_snapshot", {})
    northstar_boundaries = northstar.get("boundaries", {})
    northstar_passed = (
        northstar.get("phase_id") == "PCR-07"
        and northstar_snapshot.get("local_prerequisites_passed") is True
        and northstar_snapshot.get("northstar_implementation_authorized") is False
        and northstar_boundaries.get("real_client_data_enabled") is False
    )

    operating = records["initial_operating_controls"]
    operating_snapshot = operating.get("readiness_snapshot", {})
    operating_boundaries = operating.get("boundaries", {})
    operating_passed = (
        operating.get("phase_id") == "PCR-08"
        and operating_snapshot.get("local_prerequisites_passed") is True
        and operating_snapshot.get("initial_operating_controls_activation_authorized")
        is False
        and operating_boundaries.get("codex_start_authorized") is False
        and operating_boundaries.get("real_client_data_enabled") is False
    )

    pcr10 = records["pre_codex_readiness"]
    pcr10_snapshot = pcr10.get("readiness_snapshot", {})
    pcr10_passed = (
        pcr10.get("phase_id") == "PCR-10"
        and pcr10.get("status") == "chat_first_complete_integrated"
        and pcr10.get("release_integrity", {}).get("integration_state")
        == "integrated_to_main"
        and pcr10_snapshot.get("local_prerequisites_passed") is True
        and pcr10_snapshot.get("release_integration_complete") is True
        and pcr10_snapshot.get("codex_start_authorized") is False
        and _all_false(
            pcr10.get("boundaries", {}),
            (
                "autonomous_merge_authorized",
                "external_actions_authorized",
                "paid_services_authorized",
                "phase1_authorized",
                "production_deployment_authorized",
                "real_client_data_enabled",
                "runtime_activation_authorized",
            ),
        )
    )

    ws4 = records["workstream4_readiness"]
    ws4_snapshot = ws4.get("readiness_snapshot", {})
    ws4_passed = (
        ws4.get("status")
        == "repository_preparation_complete_manual_attestations_pending"
        and ws4_snapshot.get("repository_side_prerequisites_passed") is True
        and ws4_snapshot.get("hosted_controls_verified") is False
        and ws4_snapshot.get("clean_macos_environment_verified") is False
        and ws4_snapshot.get("codex_start_authorized") is False
    )

    ws5 = records["workstream5_launch_control"]
    ws5_snapshot = ws5.get("readiness_snapshot", {})
    ws5_passed = (
        ws5.get("status")
        == "repository_launch_control_complete_manual_gates_pending"
        and ws5_snapshot.get("repository_launch_control_complete") is True
        and ws5_snapshot.get("launch_permit_issued") is False
        and ws5_snapshot.get("codex_start_authorized") is False
    )

    ws6 = records["workstream6_baseline_lock"]
    ws6_passed = (
        ws6.get("work_package_id") == "WS6.0"
        and ws6.get("status") == "baseline_locked_repairs_pending"
        and ws6.get("completion_rule", {}).get("baseline_locked") is True
        and ws6.get("completion_rule", {}).get("final_reconciliation_complete")
        is False
        and ws6.get("boundaries", {}).get("codex_start_authorized") is False
    )

    ws61 = records["workstream6_handoff_reconciliation"]
    ws61_passed = (
        ws61.get("work_package_id") == "WS6.1"
        and ws61.get("status") == "controlling_machine_handoff_reconciled"
        and ws61.get("closed_defects")
        == ["WS6-BLOCK-001", "WS6-BLOCK-002"]
        and ws61.get("completion", {}).get("ws61_complete") is True
        and ws61.get("boundaries", {}).get("codex_start_authorized") is False
    )

    return {
        "canonical_release": {"passed": canonical_passed, "required_status": "success"},
        "referential_integrity": {
            "passed": referential_passed,
            "required_status": "passed",
            "unresolved_references": len(referential.get("issues", [])),
        },
        "repository_governance": {"passed": repository_passed, "required_status": "passed"},
        "runtime_adapters": {
            "passed": runtime_passed,
            "runtime_activation_authorized": runtime_snapshot.get(
                "runtime_activation_authorized"
            ),
        },
        "hermes_compatibility": {
            "passed": hermes_passed,
            "hermes_activation_authorized": hermes_snapshot.get(
                "hermes_activation_authorized"
            ),
        },
        "northstar_blueprint": {
            "passed": northstar_passed,
            "northstar_implementation_authorized": northstar_snapshot.get(
                "northstar_implementation_authorized"
            ),
        },
        "initial_operating_controls": {
            "passed": operating_passed,
            "initial_operating_controls_activation_authorized": operating_snapshot.get(
                "initial_operating_controls_activation_authorized"
            ),
        },
        "pre_codex_readiness": {
            "passed": pcr10_passed,
            "release_integration_complete": pcr10_snapshot.get(
                "release_integration_complete"
            ),
            "codex_start_authorized": pcr10_snapshot.get("codex_start_authorized"),
        },
        "workstream4_readiness": {
            "passed": ws4_passed,
            "repository_side_prerequisites_passed": ws4_snapshot.get(
                "repository_side_prerequisites_passed"
            ),
            "hosted_controls_verified": ws4_snapshot.get("hosted_controls_verified"),
            "clean_macos_environment_verified": ws4_snapshot.get(
                "clean_macos_environment_verified"
            ),
        },
        "workstream5_launch_control": {
            "passed": ws5_passed,
            "repository_launch_control_complete": ws5_snapshot.get(
                "repository_launch_control_complete"
            ),
            "launch_permit_issued": ws5_snapshot.get("launch_permit_issued"),
            "codex_start_authorized": ws5_snapshot.get("codex_start_authorized"),
        },
        "workstream6_baseline_lock": {
            "passed": ws6_passed,
            "baseline_locked": ws6.get("completion_rule", {}).get("baseline_locked"),
            "final_reconciliation_complete": ws6.get("completion_rule", {}).get(
                "final_reconciliation_complete"
            ),
            "codex_start_authorized": ws6.get("boundaries", {}).get(
                "codex_start_authorized"
            ),
        },
        "workstream6_handoff_reconciliation": {
            "passed": ws61_passed,
            "handoff_reconciled": ws61.get("completion", {}).get("ws61_complete"),
            "closed_defects": ws61.get("closed_defects"),
            "codex_start_authorized": ws61.get("boundaries", {}).get(
                "codex_start_authorized"
            ),
        },
    }


def build_handoff(*, check_dependencies: bool = True) -> dict[str, Any]:
    source = _load_yaml(SOURCE_PATH)
    readiness = _dependency_readiness(check_dependencies=check_dependencies)
    readiness["local_prerequisites_passed"] = all(
        item.get("passed") is True for item in readiness.values()
    )
    activation = source.get("activation_conditions", [])
    activation_status = {
        item: item in MERGED_ACTIVATION_CONDITIONS
        for item in activation
        if isinstance(item, str)
    }
    final_release_path = ROOT / "releases" / "pre-codex-final-reconciliation-2026-08-06.json"
    final_release = _load_json(final_release_path) if final_release_path.is_file() else {}
    final_workstream6_gate_complete = (
        final_release.get("work_package_id") == "WS6.16"
        and final_release.get("final_reconciliation_complete") is True
        and final_release.get("all_blocking_defects_closed") is True
        and final_release.get("codex_start_authorized") is False
    )
    readiness.update(
        {
            "final_workstream6_gate_complete": final_workstream6_gate_complete,
            "hosted_controls_verified": False,
            "clean_macos_environment_verified": False,
            "explicit_founder_phase0_approval_received": False,
            "launch_permit_issued": False,
            "codex_start_authorized": False,
            "activation_status": activation_status,
            "activation_blockers": [
                item for item, value in activation_status.items() if not value
            ],
        }
    )
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
        "Built WS6.1-reconciled PCR-04 Codex handoff: "
        f"{len(handoff['task_graph'])} Phase 0 tasks, "
        f"{len(handoff['read_order'])} read-order paths, "
        f"{len(handoff['prerequisite_records'])} prerequisite records, "
        f"{len(handoff['execution']['required_commands'])} commands, "
        f"{len(handoff['activation_conditions'])} activation conditions, "
        f"local_prerequisites_passed={str(readiness['local_prerequisites_passed']).lower()}, "
        "final_workstream6_gate_complete=false, launch_permit_issued=false, "
        "codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
