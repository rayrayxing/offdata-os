from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from build_workstream6_final_launch_control import build_records

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts" / "workstream6-final-launch-control.json"
SCHEMA_PATH = ROOT / "schemas" / "workstream6-final-launch-control.schema.json"
REPORT_PATH = ROOT / "reports" / "workstream6-final-launch-control-evidence.md"
LAUNCH_PATH = ROOT / "contracts" / "codex-phase0-launch-control.json"
FINAL_ISSUE_PATH = ROOT / "handoff" / "codex-phase0-issue-final.md"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
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

    require(contract.get("work_package_id") == "WS6.2", "work package is not WS6.2")
    require(contract.get("base_main_sha") == "a3fb3ea21029f01c52bc8e871dd7bcb284a31f7c", "exact WS6.1 base is missing")
    require(contract.get("status") == "final_launch_control_reconciled", "WS6.2 status is invalid")
    repairs = contract.get("repairs", {})
    for key in (
        "historical_workstream5_authority_retained",
        "final_issue_body_rebound",
        "final_release_gate_required",
        "final_status_check_identity_bound",
        "permit_requires_final_release_digest",
        "stale_workstream5_issue_digest_rejected",
    ):
        require(repairs.get(key) is True, f"repair {key} is incomplete")
    require(contract.get("closed_defects") == ["WS6-BLOCK-004", "WS6-BLOCK-005"], "closed defect set is invalid")
    require(contract.get("remaining_blocking_defects") == ["WS6-BLOCK-003", "WS6-BLOCK-006"], "remaining blocker set is invalid")
    completion = contract.get("completion", {})
    require(completion.get("all_required_prior_components_pass") is True, "prior components are incomplete")
    require(completion.get("ws62_complete") is True, "WS6.2 is incomplete")
    require(completion.get("final_reconciliation_complete") is False, "final reconciliation was claimed early")
    require(completion.get("all_blocking_defects_closed") is False, "all blockers were claimed closed early")
    require(completion.get("next_permitted_work_package") == "WS6.3", "next work package is invalid")
    evidence = contract.get("evidence", {})
    require(evidence.get("launch_contract_path") == "contracts/codex-phase0-launch-control.json", "launch contract path is invalid")
    require(evidence.get("final_issue_path") == "handoff/codex-phase0-issue-final.md", "final issue path is invalid")
    require(
        evidence.get("required_status_check") == "Validate final pre-Codex canonical handoff and complete release",
        "required final status check is stale",
    )
    require(evidence.get("read_order_count", 0) >= 49, "read order is incomplete")
    require(evidence.get("preflight_command_count", 0) >= 51, "preflight commands are incomplete")
    require(evidence.get("launch_self_test_mutation_minimum", 0) >= 39, "launch self-test floor is too low")
    require(evidence.get("package_mutation_minimum", 0) >= 20, "package mutation floor is too low")
    boundaries = contract.get("boundaries", {})
    require(boundaries.get("founder_accountability_preserved") is True, "Founder accountability was not preserved")
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
    contract = _load(CONTRACT_PATH)
    schema = _load(SCHEMA_PATH)
    errors = list(Draft202012Validator(schema).iter_errors(contract))
    if errors:
        raise SystemExit("WS6.2 package schema failed:\n- " + "\n- ".join(error.message for error in errors))
    expected, report = build_records()
    if _canonical(contract) != _canonical(expected):
        raise SystemExit("WS6.2 package contract is not deterministic")
    if REPORT_PATH.read_text(encoding="utf-8") != report:
        raise SystemExit("WS6.2 evidence report is not deterministic")
    semantic = failures(contract)
    if semantic:
        raise SystemExit("WS6.2 package semantic validation failed:\n- " + "\n- ".join(semantic))
    evidence = contract["evidence"]
    if evidence["launch_contract_sha256"] != _digest(LAUNCH_PATH):
        raise SystemExit("WS6.2 launch-contract digest drifted")
    if evidence["final_issue_sha256"] != _digest(FINAL_ISSUE_PATH):
        raise SystemExit("WS6.2 final issue digest drifted")
    cases = [
        (("work_package_id",), "WS6.1"),
        (("base_main_sha",), "0" * 40),
        (("status",), "pending"),
        (("repairs", "historical_workstream5_authority_retained"), False),
        (("repairs", "final_issue_body_rebound"), False),
        (("repairs", "final_release_gate_required"), False),
        (("repairs", "final_status_check_identity_bound"), False),
        (("repairs", "permit_requires_final_release_digest"), False),
        (("repairs", "stale_workstream5_issue_digest_rejected"), False),
        (("closed_defects",), ["WS6-BLOCK-004"]),
        (("remaining_blocking_defects",), []),
        (("completion", "all_required_prior_components_pass"), False),
        (("completion", "ws62_complete"), False),
        (("completion", "final_reconciliation_complete"), True),
        (("completion", "all_blocking_defects_closed"), True),
        (("completion", "next_permitted_work_package"), "WS6.4"),
        (("evidence", "final_issue_path"), "handoff/codex-phase0-issue-workstream5.md"),
        (("evidence", "required_status_check"), "Validate Codex Phase 0 launch control and complete prior release"),
        (("evidence", "read_order_count"), 10),
        (("evidence", "preflight_command_count"), 10),
        (("boundaries", "phase0_implementation_authorized"), True),
        (("boundaries", "founder_accountability_preserved"), False),
    ]
    for index, (path, replacement) in enumerate(cases, start=1):
        mutated = copy.deepcopy(contract)
        _set(mutated, path, replacement)
        if not failures(mutated):
            raise SystemExit(f"WS6.2 package mutation {index} was not rejected: {'.'.join(path)}")
    print(
        f"WS6.2 final launch-control reconciliation passed: {len(cases)} mutations rejected, "
        "closed_defects=2, remaining_blockers=2, next=WS6.3, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
