from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "configs" / "codex-phase0-launch-control.yaml"
CONTRACT_PATH = ROOT / "contracts" / "codex-phase0-launch-control.json"
FINAL_ISSUE_PATH = ROOT / "handoff" / "codex-phase0-issue-final.md"
TEMPLATE_PATHS = {
    "hosted_controls": ROOT / "handoff" / "codex-phase0-hosted-controls-attestation.template.json",
    "clean_macos": ROOT / "handoff" / "codex-phase0-clean-macos-attestation.template.json",
    "founder_approval": ROOT / "handoff" / "codex-phase0-founder-authorization.template.json",
    "launch_ack": ROOT / "handoff" / "codex-phase0-launch-ack.template.json",
}


def _yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def _digest_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _validate(source: dict[str, Any]) -> None:
    expected = {
        "work_package_id": "WS6.2",
        "base_main_sha": "a3fb3ea21029f01c52bc8e871dd7bcb284a31f7c",
        "status": "final_launch_control_reconciled_manual_gates_pending",
    }
    for key, value in expected.items():
        if source.get(key) != value:
            raise ValueError(f"invalid {key}")
    target = source["launch_target"]
    if target["permitted_tasks"] != ["P0.1", "P0.2", "P0.3", "P0.4"]:
        raise ValueError("Phase 0 scope drifted")
    if target["merge_authorized"] or target["phase1_authorized"]:
        raise ValueError("merge and Phase 1 must remain denied")
    if source["closed_defects"] != ["WS6-BLOCK-004", "WS6-BLOCK-005"]:
        raise ValueError("invalid defect closure")
    if source["remaining_blocking_defects"] != ["WS6-BLOCK-003", "WS6-BLOCK-006"]:
        raise ValueError("invalid remaining blockers")


def build_templates(source: dict[str, Any]) -> dict[str, dict[str, Any]]:
    zero_sha, zero_digest = "0" * 40, "0" * 64
    check = source["required_status_check"]["job_name"]
    tasks = source["launch_target"]["permitted_tasks"]
    return {
        "hosted_controls": {
            "schema_version": "2.0.0",
            "evidence_type": "github_hosted_controls_attestation",
            "repository": source["repository"],
            "issue_number": 19,
            "issue_state": "open",
            "issue_state_reason": None,
            "approved_main_sha": zero_sha,
            "required_status_check_name": check,
            "recorded_at": None,
            "attested_by": "rayrayxing",
            "controls": {
                key: False
                for key in (
                    "github_mfa_enabled",
                    "pull_request_required_for_main",
                    "final_launch_status_check_required_for_main",
                    "stale_approvals_dismissed",
                    "review_conversation_resolution_required",
                    "force_push_to_main_blocked",
                    "main_branch_deletion_blocked",
                    "merged_head_branches_auto_deleted",
                )
            },
            "branch_cleanup": {
                "complete": False,
                "remaining_branches": [],
                "inventory_sha256": zero_digest,
            },
            "evidence_attachments": [],
            "attested": False,
        },
        "clean_macos": {
            "schema_version": "2.0.0",
            "evidence_type": "clean_macos_environment_attestation",
            "repository": source["repository"],
            "approved_main_sha": zero_sha,
            "doctor_report_sha256": zero_digest,
            "recorded_at": None,
            "attested_by": "rayrayxing",
            "manual_attestations": {
                key: False
                for key in (
                    "clean_machine_available",
                    "no_real_client_files_present",
                    "no_repository_credentials_present",
                    "no_paid_service_or_trial_required",
                    "founder_environment_attestation_received",
                )
            },
            "clean_macos_environment_verified": False,
            "attested": False,
        },
        "founder_approval": {
            "schema_version": "2.0.0",
            "evidence_type": "founder_codex_phase0_authorization",
            "repository": source["repository"],
            "canonical_issue": 1,
            "decision": "not_approved",
            "approved_main_sha": zero_sha,
            "approved_phase": "Codex Phase 0 only",
            "approved_tasks": tasks,
            "required_branch": "codex/phase-0-foundation",
            "draft_pull_request_required": True,
            "merge_authorized": False,
            "phase1_authorized": False,
            "authorized_at": None,
            "attested_by": "rayrayxing",
            "attested": False,
        },
        "launch_ack": {
            "schema_version": "2.0.0",
            "ack_type": "codex_phase0_launch_acknowledgement",
            "launch_id": zero_digest,
            "approved_main_sha": zero_sha,
            "branch": "codex/phase-0-foundation",
            "permit_sha256": zero_digest,
            "final_workstream6_release_sha256": zero_digest,
            "phase": "Codex Phase 0 only",
            "tasks": tasks,
            "draft_pull_request_required": True,
            "merge_authorized": False,
            "phase1_authorized": False,
        },
    }


def build_records() -> tuple[dict[str, Any], str, dict[str, dict[str, Any]]]:
    source = _yaml(SOURCE_PATH)
    _validate(source)
    issue_body = FINAL_ISSUE_PATH.read_text(encoding="utf-8")
    templates = build_templates(source)
    checks = {
        "ws61_exact_base_bound": True,
        "workstream5_issue_retained_historical": source["historical_authority"]["workstream5_issue_body"]["classification"] == "historical_non_controlling",
        "workstream5_release_retained_historical": source["historical_authority"]["workstream5_release"]["classification"] == "historical_non_controlling",
        "final_issue_is_controlling": source["canonical_authority"]["generated_issue_body"] == "handoff/codex-phase0-issue-final.md",
        "final_release_required_before_permit": source["final_release_gate"]["must_exist_before_permit"] is True,
        "final_status_check_identity_bound": source["required_status_check"]["must_be_required_for_main"] is True,
        "phase0_scope_exact": source["launch_target"]["permitted_tasks"] == ["P0.1", "P0.2", "P0.3", "P0.4"],
        "manual_and_release_gates_pending": all(
            source["readiness"][key] is False
            for key in (
                "final_workstream6_release_verified",
                "hosted_controls_verified",
                "clean_macos_environment_verified",
                "explicit_founder_phase0_approval_received",
                "approved_main_sha_bound",
                "launch_permit_issued",
                "codex_start_authorized",
            )
        ),
        "authorization_boundaries_denied": all(
            value is False
            for key, value in source["boundaries"].items()
            if key != "founder_accountability_preserved"
        ),
        "founder_accountability_preserved": source["boundaries"]["founder_accountability_preserved"] is True,
    }
    complete = all(checks.values())
    contract = {
        **source,
        "status": "repository_launch_control_complete_manual_gates_pending",
        "final_status": source["status"],
        "generated_from": str(SOURCE_PATH.relative_to(ROOT)),
        "generated_issue": {
            "body_path": str(FINAL_ISSUE_PATH.relative_to(ROOT)),
            "body_sha256": _digest_text(issue_body),
            "body_line_count": len(issue_body.splitlines()),
            "body_character_count": len(issue_body),
            "github_issue_sync_verified": False,
        },
        "template_registry": {
            key: {
                "path": str(TEMPLATE_PATHS[key].relative_to(ROOT)),
                "sha256": _digest_text(_canonical(value)),
            }
            for key, value in templates.items()
        },
        "launch_protocol_registry": {
            "permitted_task_count": 4,
            "read_order_count": len(source["read_order"]),
            "preflight_command_count": len(source["required_preflight_commands"]),
            "allowed_scope_count": len(source["allowed_scope"]),
            "prohibited_scope_count": len(source["prohibited_scope"]),
            "stop_condition_count": len(source["stop_conditions"]),
            "revocation_condition_count": len(source["launch_permit"]["revocation_conditions"]),
        },
        "readiness_snapshot": {
            "checks": checks,
            "repository_final_launch_control_complete": complete,
            "repository_launch_control_complete": complete,
            "generated_final_issue_ready_for_sync": True,
            "github_issue_sync_verified": False,
            "final_workstream6_release_verified": False,
            "hosted_controls_verified": False,
            "clean_macos_environment_verified": False,
            "explicit_founder_phase0_approval_received": False,
            "approved_main_sha_bound": False,
            "launch_permit_issued": False,
            "codex_start_authorized": False,
            "next_permitted_phase_after_all_gates": "Codex Phase 0 only",
        },
    }
    return contract, issue_body, templates


def main() -> None:
    contract, issue_body, templates = build_records()
    CONTRACT_PATH.write_text(_canonical(contract), encoding="utf-8")
    FINAL_ISSUE_PATH.write_text(issue_body, encoding="utf-8")
    for key, value in templates.items():
        TEMPLATE_PATHS[key].write_text(_canonical(value), encoding="utf-8")
    registry = contract["launch_protocol_registry"]
    print(
        "Built WS6.2 final Codex Phase 0 launch control: "
        f"{registry['read_order_count']} read-order paths, "
        f"{registry['preflight_command_count']} commands, "
        "repository_launch_control_complete=true, final_release=false, "
        "hosted_controls=false, clean_macos=false, founder_approval=false, "
        "launch_permit=false, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
