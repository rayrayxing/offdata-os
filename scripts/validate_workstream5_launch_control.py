from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from build_workstream5_launch_control import build_records

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts" / "codex-phase0-launch-control.json"
SCHEMA_PATH = ROOT / "schemas" / "codex-phase0-launch-control.schema.json"
FINAL_ISSUE_PATH = ROOT / "handoff" / "codex-phase0-issue-final.md"
HISTORICAL_ISSUE_PATH = ROOT / "handoff" / "codex-phase0-issue-workstream5.md"
HISTORICAL_RELEASE_PATH = ROOT / "releases" / "codex-phase0-launch-control-2026-08-06.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def failures(contract: dict[str, Any]) -> list[str]:
    result: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            result.append(message)

    require(contract.get("work_package_id") == "WS6.2", "work package must be WS6.2")
    require(
        contract.get("status")
        == "repository_launch_control_complete_manual_gates_pending",
        "legacy status alias is invalid",
    )
    require(
        contract.get("final_status")
        == "final_launch_control_reconciled_manual_gates_pending",
        "final status is invalid",
    )
    require(
        contract.get("canonical_authority", {}).get("generated_issue_body")
        == "handoff/codex-phase0-issue-final.md",
        "final issue is not controlling",
    )
    require(
        contract.get("historical_authority", {})
        .get("workstream5_issue_body", {})
        .get("classification")
        == "historical_non_controlling",
        "historical issue classification is invalid",
    )
    require(
        contract.get("final_release_gate", {}).get("must_exist_before_permit")
        is True,
        "final release can be bypassed",
    )
    require(
        contract.get("required_status_check", {}).get("job_name")
        == "Validate final pre-Codex canonical handoff and complete release",
        "final check identity is stale",
    )
    target = contract.get("launch_target", {})
    require(
        target.get("permitted_tasks") == ["P0.1", "P0.2", "P0.3", "P0.4"],
        "task scope drifted",
    )
    require(
        target.get("required_branch") == "codex/phase-0-foundation",
        "branch drifted",
    )
    require(target.get("required_pull_request_state") == "draft", "PR must remain draft")
    require(
        target.get("merge_authorized") is False
        and target.get("phase1_authorized") is False,
        "merge or Phase 1 was authorized",
    )
    snapshot = contract.get("readiness_snapshot", {})
    require(
        snapshot.get("repository_final_launch_control_complete") is True,
        "final launch package is incomplete",
    )
    require(
        snapshot.get("repository_launch_control_complete") is True,
        "legacy readiness alias is incomplete",
    )
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
        require(snapshot.get(key) is False, f"{key} must remain false")
    require(
        contract.get("closed_defects") == ["WS6-BLOCK-004", "WS6-BLOCK-005"],
        "defect closure is invalid",
    )
    require(
        contract.get("remaining_blocking_defects")
        == ["WS6-BLOCK-003", "WS6-BLOCK-006"],
        "remaining blockers are invalid",
    )
    boundaries = contract.get("boundaries", {})
    require(
        boundaries.get("founder_accountability_preserved") is True,
        "Founder accountability is not preserved",
    )
    for key, value in boundaries.items():
        if key != "founder_accountability_preserved":
            require(value is False, f"boundary {key} must remain false")
    return result


def _set(value: dict[str, Any], path: tuple[str, ...], replacement: Any) -> None:
    node: Any = value
    for part in path[:-1]:
        node = node[part]
    node[path[-1]] = replacement


def main() -> None:
    contract, schema = _load(CONTRACT_PATH), _load(SCHEMA_PATH)
    errors = list(Draft202012Validator(schema).iter_errors(contract))
    if errors:
        raise SystemExit(
            "WS6.2 launch-control schema failed:\n- "
            + "\n- ".join(error.message for error in errors)
        )
    expected, issue, templates = build_records()
    if _canonical(contract) != _canonical(expected):
        raise SystemExit("final launch contract is not deterministic")
    if FINAL_ISSUE_PATH.read_text(encoding="utf-8") != issue:
        raise SystemExit("final issue is not deterministic")
    for key, value in templates.items():
        path = ROOT / contract["template_registry"][key]["path"]
        if path.read_text(encoding="utf-8") != _canonical(value):
            raise SystemExit(f"{key} template is stale")
    semantic = failures(contract)
    if semantic:
        raise SystemExit(
            "WS6.2 launch-control semantics failed:\n- " + "\n- ".join(semantic)
        )
    historical = contract["historical_authority"]
    if _digest(HISTORICAL_ISSUE_PATH) != historical["workstream5_issue_body"]["sha256"]:
        raise SystemExit("historical Workstream 5 issue drifted")
    if _digest(HISTORICAL_RELEASE_PATH) != historical["workstream5_release"]["sha256"]:
        raise SystemExit("historical Workstream 5 release drifted")
    if _digest(FINAL_ISSUE_PATH) != contract["generated_issue"]["body_sha256"]:
        raise SystemExit("final issue digest is invalid")
    cases = [
        (("status",), "pending"),
        (("final_status",), "pending"),
        (
            ("canonical_authority", "generated_issue_body"),
            "handoff/codex-phase0-issue-workstream5.md",
        ),
        (("final_release_gate", "must_exist_before_permit"), False),
        (
            ("required_status_check", "job_name"),
            "Validate Codex Phase 0 launch control and complete prior release",
        ),
        (("launch_target", "permitted_tasks"), ["P0.1"]),
        (("launch_target", "merge_authorized"), True),
        (("readiness_snapshot", "repository_launch_control_complete"), False),
        (("readiness_snapshot", "repository_final_launch_control_complete"), False),
        (("readiness_snapshot", "launch_permit_issued"), True),
        (("readiness_snapshot", "codex_start_authorized"), True),
        (("closed_defects",), ["WS6-BLOCK-004"]),
        (("remaining_blocking_defects",), []),
        (("boundaries", "phase0_implementation_authorized"), True),
        (("boundaries", "founder_accountability_preserved"), False),
    ]
    for index, (path, replacement) in enumerate(cases, 1):
        mutated = copy.deepcopy(contract)
        _set(mutated, path, replacement)
        if not failures(mutated):
            raise SystemExit(f"WS6.2 launch mutation {index} was not rejected")
    print(
        "WS6.2 final launch control passed: "
        f"{contract['launch_protocol_registry']['read_order_count']} read-order paths, "
        f"{contract['launch_protocol_registry']['preflight_command_count']} commands, "
        f"{len(cases)} mutations rejected, final release pending, "
        "launch permit not issued, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
