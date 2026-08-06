from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from build_workstream5_launch_control import build_records

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "configs" / "codex-phase0-launch-control.yaml"
CONTRACT_PATH = ROOT / "contracts" / "codex-phase0-launch-control.json"
SCHEMA_PATH = ROOT / "schemas" / "codex-phase0-launch-control.schema.json"
FINAL_ISSUE_PATH = ROOT / "handoff" / "codex-phase0-issue-final.md"
HISTORICAL_ISSUE_PATH = ROOT / "handoff" / "codex-phase0-issue-workstream5.md"
HISTORICAL_RELEASE_PATH = ROOT / "releases" / "codex-phase0-launch-control-2026-08-06.json"


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


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_failures(contract: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(contract.get("work_package_id") == "WS6.2", "work package must be WS6.2")
    require(
        contract.get("status") == "final_launch_control_reconciled_manual_gates_pending",
        "final launch-control status is invalid",
    )
    authority = contract.get("canonical_authority", {})
    require(
        authority.get("generated_issue_body") == "handoff/codex-phase0-issue-final.md",
        "final issue body is not controlling",
    )
    historical = contract.get("historical_authority", {})
    require(
        historical.get("workstream5_issue_body", {}).get("classification")
        == "historical_non_controlling",
        "Workstream 5 issue body must be historical",
    )
    require(
        historical.get("workstream5_release", {}).get("classification")
        == "historical_non_controlling",
        "Workstream 5 release must be historical",
    )
    final_gate = contract.get("final_release_gate", {})
    require(
        final_gate.get("path")
        == "releases/pre-codex-final-reconciliation-2026-08-06.json",
        "final Workstream 6 release path is missing",
    )
    require(final_gate.get("must_exist_before_permit") is True, "permit can bypass final release")
    required_fields = final_gate.get("required_fields", {})
    require(
        required_fields
        == {
            "final_reconciliation_complete": True,
            "all_blocking_defects_closed": True,
            "exact_main_sha_bound": True,
            "tested_merge_reference_bound": True,
            "codex_start_authorized": False,
        },
        "final release requirements are incomplete",
    )
    check = contract.get("required_status_check", {})
    require(
        check.get("job_name")
        == "Validate final pre-Codex canonical handoff and complete release",
        "final status-check identity is stale",
    )
    rejected = check.get("historical_job_names_rejected", [])
    require(
        "Validate Codex Phase 0 launch control and complete prior release" in rejected,
        "Workstream 5 check name is not explicitly rejected",
    )
    target = contract.get("launch_target", {})
    require(target.get("permitted_tasks") == ["P0.1", "P0.2", "P0.3", "P0.4"], "Phase 0 task scope drifted")
    require(target.get("required_branch") == "codex/phase-0-foundation", "branch identity drifted")
    require(target.get("required_pull_request_state") == "draft", "pull request is not draft-only")
    require(target.get("merge_authorized") is False, "merge was authorized")
    require(target.get("phase1_authorized") is False, "Phase 1 was authorized")
    generated = contract.get("generated_issue", {})
    require(
        generated.get("body_path") == "handoff/codex-phase0-issue-final.md",
        "generated issue path is stale",
    )
    require(generated.get("github_issue_sync_verified") is False, "repository files may not claim live issue sync")
    readiness = contract.get("readiness_snapshot", {})
    require(readiness.get("repository_final_launch_control_complete") is True, "repository launch package is incomplete")
    for key in (
        "github_issue_sync_verified",
        "final_workstream6_release_verified",
        "hosted_controls_verified",
        "clean_macos_environment_verified",
        "explicit_founder_phase0_approval_received",
        "approved_main_sha_bound",
        "launch_permit_issued",
        "codex_start_authorized",
    ):
        require(readiness.get(key) is False, f"{key} must remain false")
    require(
        contract.get("closed_defects") == ["WS6-BLOCK-004", "WS6-BLOCK-005"],
        "WS6.2 defect closure is invalid",
    )
    require(
        contract.get("remaining_blocking_defects") == ["WS6-BLOCK-003", "WS6-BLOCK-006"],
        "WS6.2 remaining blockers are invalid",
    )
    boundaries = contract.get("boundaries", {})
    require(boundaries.get("founder_accountability_preserved") is True, "Founder accountability was not preserved")
    for key, value in boundaries.items():
        if key != "founder_accountability_preserved":
            require(value is False, f"boundary {key} must remain false")
    commands = contract.get("required_preflight_commands", [])
    for required in (
        "python scripts/build_workstream6_final_launch_control.py",
        "python scripts/validate_workstream6_final_launch_control.py",
        "python scripts/prepare_codex_phase0_launch.py --self-test",
        "python scripts/require_workstream6_final_reconciliation.py --self-test",
    ):
        require(required in commands, f"missing command: {required}")
    read_order = contract.get("read_order", [])
    for required in (
        "docs/54-WS6-2-FINAL-LAUNCH-CONTROL-RECONCILIATION.md",
        "contracts/workstream6-final-launch-control.json",
        "handoff/codex-phase0-issue-final.md",
    ):
        require(required in read_order, f"missing read-order path: {required}")
    return failures


def _set(value: dict[str, Any], path: tuple[str, ...], replacement: Any) -> None:
    node: Any = value
    for part in path[:-1]:
        node = node[part]
    node[path[-1]] = replacement


def _mutation_count(contract: dict[str, Any]) -> int:
    cases: list[tuple[tuple[str, ...], Any]] = [
        (("work_package_id",), "WS6.1"),
        (("status",), "repository_launch_control_complete_manual_gates_pending"),
        (("canonical_authority", "generated_issue_body"), "handoff/codex-phase0-issue-workstream5.md"),
        (("historical_authority", "workstream5_issue_body", "classification"), "controlling"),
        (("final_release_gate", "path"), "releases/codex-phase0-launch-control-2026-08-06.json"),
        (("final_release_gate", "must_exist_before_permit"), False),
        (("final_release_gate", "required_fields", "all_blocking_defects_closed"), False),
        (("final_release_gate", "required_fields", "codex_start_authorized"), True),
        (("required_status_check", "job_name"), "Validate Codex Phase 0 launch control and complete prior release"),
        (("launch_target", "permitted_tasks"), ["P0.1"]),
        (("launch_target", "required_branch"), "feature/phase0"),
        (("launch_target", "required_pull_request_state"), "open"),
        (("launch_target", "merge_authorized"), True),
        (("launch_target", "phase1_authorized"), True),
        (("generated_issue", "body_path"), "handoff/codex-phase0-issue-workstream5.md"),
        (("generated_issue", "github_issue_sync_verified"), True),
        (("readiness_snapshot", "repository_final_launch_control_complete"), False),
        (("readiness_snapshot", "final_workstream6_release_verified"), True),
        (("readiness_snapshot", "launch_permit_issued"), True),
        (("readiness_snapshot", "codex_start_authorized"), True),
        (("closed_defects",), ["WS6-BLOCK-004"]),
        (("remaining_blocking_defects",), []),
        (("boundaries", "phase0_implementation_authorized"), True),
        (("boundaries", "phase0_merge_authorized"), True),
        (("boundaries", "founder_accountability_preserved"), False),
    ]
    for index, (path, replacement) in enumerate(cases, start=1):
        mutated = copy.deepcopy(contract)
        _set(mutated, path, replacement)
        if not semantic_failures(mutated):
            raise SystemExit(f"WS6.2 launch-control mutation {index} was not rejected: {'.'.join(path)}")
    return len(cases)


def main() -> None:
    source = _load_yaml(SOURCE_PATH)
    contract = _load_json(CONTRACT_PATH)
    schema = _load_json(SCHEMA_PATH)
    errors = sorted(Draft202012Validator(schema).iter_errors(contract), key=lambda item: list(item.path))
    if errors:
        raise SystemExit("WS6.2 launch-control schema validation failed:\n- " + "\n- ".join(error.message for error in errors))

    expected_contract, expected_issue, expected_templates = build_records()
    if _canonical_json(contract) != _canonical_json(expected_contract):
        raise SystemExit("controlling final launch contract is not deterministically generated")
    if FINAL_ISSUE_PATH.read_text(encoding="utf-8") != expected_issue:
        raise SystemExit("final issue body is not deterministically generated")
    for key, value in expected_templates.items():
        path = ROOT / contract["template_registry"][key]["path"]
        if path.read_text(encoding="utf-8") != _canonical_json(value):
            raise SystemExit(f"{key} template is not deterministically generated")

    failures = semantic_failures(contract)
    if failures:
        raise SystemExit("WS6.2 launch-control semantic validation failed:\n- " + "\n- ".join(failures))

    historical = source["historical_authority"]
    if _digest(HISTORICAL_ISSUE_PATH) != historical["workstream5_issue_body"]["sha256"]:
        raise SystemExit("historical Workstream 5 issue body drifted")
    if _digest(HISTORICAL_RELEASE_PATH) != historical["workstream5_release"]["sha256"]:
        raise SystemExit("historical Workstream 5 release drifted")
    if _digest(FINAL_ISSUE_PATH) != contract["generated_issue"]["body_sha256"]:
        raise SystemExit("final issue-body digest is invalid")
    if contract["generated_issue"]["body_sha256"] == historical["workstream5_issue_body"]["sha256"]:
        raise SystemExit("final issue body was not rebound away from Workstream 5")

    mutations = _mutation_count(contract)
    print(
        "WS6.2 final launch control passed: "
        f"{contract['launch_protocol_registry']['read_order_count']} read-order paths, "
        f"{contract['launch_protocol_registry']['preflight_command_count']} commands, "
        f"{mutations} mutations rejected, final release pending, "
        "launch permit not issued, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
