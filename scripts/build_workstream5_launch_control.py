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


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _validate_source(source: dict[str, Any]) -> None:
    if source.get("work_package_id") != "WS6.2":
        raise ValueError("launch-control source must describe WS6.2")
    if source.get("base_main_sha") != "a3fb3ea21029f01c52bc8e871dd7bcb284a31f7c":
        raise ValueError("WS6.2 must begin from the exact WS6.1 merge")
    target = source.get("launch_target", {})
    if target.get("permitted_tasks") != ["P0.1", "P0.2", "P0.3", "P0.4"]:
        raise ValueError("permitted tasks must be exactly P0.1-P0.4")
    if target.get("required_branch") != "codex/phase-0-foundation":
        raise ValueError("Codex branch identity is invalid")
    if target.get("required_pull_request_state") != "draft":
        raise ValueError("Phase 0 pull request must remain draft")
    if target.get("merge_authorized") is not False or target.get("phase1_authorized") is not False:
        raise ValueError("merge and Phase 1 must remain unauthorized")
    final_gate = source.get("final_release_gate", {})
    if final_gate.get("path") != "releases/pre-codex-final-reconciliation-2026-08-06.json":
        raise ValueError("final Workstream 6 release path is invalid")
    if final_gate.get("must_exist_before_permit") is not True:
        raise ValueError("final Workstream 6 release must precede permit issuance")
    check = source.get("required_status_check", {})
    if check.get("job_name") != "Validate final pre-Codex canonical handoff and complete release":
        raise ValueError("final status-check identity is invalid")
    if source.get("closed_defects") != ["WS6-BLOCK-004", "WS6-BLOCK-005"]:
        raise ValueError("WS6.2 may close only blockers 004 and 005")
    if source.get("remaining_blocking_defects") != ["WS6-BLOCK-003", "WS6-BLOCK-006"]:
        raise ValueError("WS6.2 remaining blockers are invalid")
    readiness = source.get("readiness", {})
    if readiness.get("repository_final_launch_control_complete") is not True:
        raise ValueError("repository final launch control must be complete")
    pending = (
        "final_workstream6_release_verified",
        "hosted_controls_verified",
        "clean_macos_environment_verified",
        "explicit_founder_phase0_approval_received",
        "approved_main_sha_bound",
        "launch_permit_issued",
        "codex_start_authorized",
    )
    if any(readiness.get(key) is not False for key in pending):
        raise ValueError("all manual, release and authorization gates must remain false")
    boundaries = source.get("boundaries", {})
    if boundaries.get("founder_accountability_preserved") is not True:
        raise ValueError("Founder accountability must be preserved")
    if any(
        value is not False
        for key, value in boundaries.items()
        if key != "founder_accountability_preserved"
    ):
        raise ValueError("all implementation and external-action boundaries must remain false")


def build_templates(source: dict[str, Any]) -> dict[str, dict[str, Any]]:
    zero_sha = "0" * 40
    zero_digest = "0" * 64
    status_check = source["required_status_check"]["job_name"]
    hosted = {
        "schema_version": "2.0.0",
        "evidence_type": "github_hosted_controls_attestation",
        "repository": source["repository"],
        "issue_number": 19,
        "issue_state": "open",
        "issue_state_reason": None,
        "approved_main_sha": zero_sha,
        "required_status_check_name": status_check,
        "recorded_at": None,
        "attested_by": "rayrayxing",
        "controls": {
            "github_mfa_enabled": False,
            "pull_request_required_for_main": False,
            "final_launch_status_check_required_for_main": False,
            "stale_approvals_dismissed": False,
            "review_conversation_resolution_required": False,
            "force_push_to_main_blocked": False,
            "main_branch_deletion_blocked": False,
            "merged_head_branches_auto_deleted": False,
        },
        "branch_cleanup": {
            "complete": False,
            "remaining_branches": [],
            "inventory_sha256": zero_digest,
        },
        "evidence_attachments": [],
        "attested": False,
    }
    clean_macos = {
        "schema_version": "2.0.0",
        "evidence_type": "clean_macos_environment_attestation",
        "repository": source["repository"],
        "approved_main_sha": zero_sha,
        "doctor_report_sha256": zero_digest,
        "recorded_at": None,
        "attested_by": "rayrayxing",
        "manual_attestations": {
            "clean_machine_available": False,
            "no_real_client_files_present": False,
            "no_repository_credentials_present": False,
            "no_paid_service_or_trial_required": False,
            "founder_environment_attestation_received": False,
        },
        "clean_macos_environment_verified": False,
        "attested": False,
    }
    founder = {
        "schema_version": "2.0.0",
        "evidence_type": "founder_codex_phase0_authorization",
        "repository": source["repository"],
        "canonical_issue": 1,
        "decision": "not_approved",
        "approved_main_sha": zero_sha,
        "approved_phase": "Codex Phase 0 only",
        "approved_tasks": source["launch_target"]["permitted_tasks"],
        "required_branch": source["launch_target"]["required_branch"],
        "draft_pull_request_required": True,
        "merge_authorized": False,
        "phase1_authorized": False,
        "authorized_at": None,
        "attested_by": "rayrayxing",
        "attested": False,
    }
    ack = {
        "schema_version": "2.0.0",
        "ack_type": "codex_phase0_launch_acknowledgement",
        "launch_id": zero_digest,
        "approved_main_sha": zero_sha,
        "branch": source["launch_target"]["required_branch"],
        "permit_sha256": zero_digest,
        "final_workstream6_release_sha256": zero_digest,
        "phase": "Codex Phase 0 only",
        "tasks": source["launch_target"]["permitted_tasks"],
        "draft_pull_request_required": True,
        "merge_authorized": False,
        "phase1_authorized": False,
    }
    return {
        "hosted_controls": hosted,
        "clean_macos": clean_macos,
        "founder_approval": founder,
        "launch_ack": ack,
    }


def build_issue_body(source: dict[str, Any]) -> str:
    activation = [
        ("pcr03_merged_to_main", True),
        ("pcr04_merged_to_main", True),
        ("pcr05_merged_to_main", True),
        ("pcr06_merged_to_main", True),
        ("pcr07_merged_to_main", True),
        ("pcr08_merged_to_main", True),
        ("pcr09_merged_to_main", True),
        ("pcr10_merged_to_main", True),
        ("workstream4_repository_package_merged_to_main", True),
        ("workstream5_launch_control_merged_to_main", True),
        ("workstream6_final_reconciliation_merged_to_main", False),
        ("github_hosted_controls_in_issue_19_verified", False),
        ("clean_macos_environment_available", False),
        ("explicit_founder_phase_0_approval_received", False),
        ("valid_codex_phase0_launch_permit_issued", False),
    ]
    lines = [
        "<!-- Generated by scripts/build_workstream5_launch_control.py for WS6.2. Do not edit manually. -->",
        "# Codex Phase 0 — Validate and build the controlled local foundation",
        "",
        "> [!CAUTION]",
        "> **NOT AUTHORISED TO START.** This final issue body, a green workflow, an assignment, a branch name, or a future final release does not authorize Codex. Every activation item below must be independently verified and a valid local single-use permit must exist.",
        "",
        "## Canonical authority",
        "",
        "- `AGENTS.md` is the controlling instruction.",
        "- `handoff/codex-phase0-handoff.json` is the machine-readable Phase 0 execution contract.",
        "- `contracts/codex-phase0-launch-control.json` is the controlling final launch-control contract.",
        "- `contracts/workstream6-final-launch-control.json` records WS6.2 reconciliation and defect closure.",
        "- `handoff/codex-phase0-issue-final.md` is the only generated issue body accepted by the final launch verifier.",
        "- `releases/pre-codex-final-reconciliation-2026-08-06.json` must exist and pass the final Workstream 6 gate before permit issuance.",
        "- `handoff/codex-phase0-issue-workstream5.md` and earlier bodies are historical, non-controlling evidence.",
        "- Historical comments, chat snapshots and predecessor digests do not grant authority.",
        "",
        "## Activation gate — every item is required",
        "",
    ]
    for name, complete in activation:
        lines.append(f"- [{'x' if complete else ' '}] `{name}`")
    lines.extend([
        "",
        "The final Workstream 6 release, issue #19 evidence, clean-macOS attestation, exact-SHA Founder approval and valid permit are independent gates. Do not infer any gate from repository files or a successful workflow.",
        "",
        "## Objective",
        "",
        "After every activation gate is independently satisfied, validate the complete chat-first repository on the Founder’s clean macOS environment and implement only Codex Phase 0 — P0.1 through P0.4 — around the governed assets already present.",
        "",
        "## Required read order",
        "",
    ])
    for index, path in enumerate(source["read_order"], start=1):
        lines.append(f"{index}. `{path}`")
    lines.extend([
        "",
        "## Preflight validation — before planning or code",
        "",
        "Run the following from the repository root. Stop on the first failure or generated diff.",
        "",
        "```bash",
        *source["required_preflight_commands"],
        "```",
        "",
        "The non-self-test final Workstream 6 gate is intentionally expected to fail until the permanent final release exists. That failure blocks launch; it is not permission to bypass the gate.",
        "",
        "## Phase 0 scope",
        "",
        "Only the following tasks may be authorized by a valid permit:",
        "",
        "- `P0.1` — repository baseline;",
        "- `P0.2` — local development environment;",
        "- `P0.3` — engineering quality baseline, retaining CF-P1–7, PCR-01–10, WS-4, WS-5 and final WS-6 gates;",
        "- `P0.4` — security and operating documentation.",
        "",
        "The required branch is `codex/phase-0-foundation`. The pull request must remain draft. Merge and Phase 1 remain unauthorized.",
        "",
        "## Final Workstream 6 release requirement",
        "",
        "Before launch preparation, `python scripts/require_workstream6_final_reconciliation.py` must validate the permanent final release. The release must bind the exact current `main` SHA and tested merge reference, close every blocking Workstream 6 defect, and keep `codex_start_authorized=false`.",
        "",
        f"The hosted-controls attestation must prove that the required `main` status check is exactly `{source['required_status_check']['job_name']}`. Workstream 5-era and WS6.1 check names are rejected.",
        "",
        "## Launch evidence and permit",
        "",
        "The local verifier requires four evidence files bound to the same exact current `main` SHA:",
        "",
        "1. completed hosted controls and exact-allowlist historical branch cleanup recorded through closed issue #19;",
        "2. a redacted, non-destructive clean-macOS doctor report;",
        "3. the Founder’s clean-macOS attestation; and",
        "4. explicit Founder authorization for **Codex Phase 0 only**, tasks P0.1–P0.4.",
        "",
        "```bash",
        "python scripts/prepare_codex_phase0_launch.py \\",
        "  --hosted-controls .local/codex-phase0-launch/hosted-controls.json \\",
        "  --macos-report .local/codex-phase0-launch/macos-doctor.json \\",
        "  --macos-attestation .local/codex-phase0-launch/macos-attestation.json \\",
        "  --founder-approval .local/codex-phase0-launch/founder-approval.json",
        "```",
        "",
        "The permit is local, ignored, mode `0600`, single-use and stale after any `main`, final release, final issue-body, status-check, evidence or scope change. It never authorizes merge or Phase 1.",
        "",
        "## Required method",
        "",
        "1. Confirm every activation item independently.",
        "2. Run the complete preflight and final Workstream 6 gate.",
        "3. Create the branch only after a valid permit exists and from the permit’s approved SHA.",
        "4. Add `governance/codex-phase0-launch-ack.json` as the first commit.",
        "5. Implement only P0.1–P0.4 in dependency order.",
        "6. Retain exact test, scan, health, backup, restore and support-bundle evidence.",
        "7. Open a draft pull request and stop at the Founder gate.",
        "",
        "## Prohibited actions",
        "",
        *[f"- `{item}`" for item in source["prohibited_scope"]],
        "",
        "## Stop conditions",
        "",
        *[f"- `{item}`" for item in source["stop_conditions"]],
        "",
        "## Completion evidence",
        "",
        "The draft Phase 0 pull request and Founder report must include what was built, why it was needed, how to run it, complete tests and scans, clean-macOS evidence, final-release and permit identifiers, exact approved SHA, first-commit acknowledgement, costs, unresolved risks, rollback and the exact next phase recommendation.",
        "",
        "## Supersession",
        "",
        "This is the single canonical Codex Phase 0 issue body after WS6.2. PCR-09, PCR-10 and Workstream 5 issue bodies remain immutable historical evidence only. Issue #2 remains closed as a duplicate.",
        "",
        "## Rollback",
        "",
        "Before Codex starts, rollback is restoring issue #1 from this generated file after any accidental drift, deleting only untracked `.local/codex-phase0-launch/` evidence or permit files, and keeping the Codex branch absent. Reverting WS6.2 must restore the Workstream 5 launch verifier and issue body together while keeping authorization false.",
        "",
    ])
    return "\n".join(lines)


def build_records() -> tuple[dict[str, Any], str, dict[str, dict[str, Any]]]:
    source = _load_yaml(SOURCE_PATH)
    _validate_source(source)
    issue_body = build_issue_body(source)
    templates = build_templates(source)
    template_registry = {
        key: {
            "path": str(TEMPLATE_PATHS[key].relative_to(ROOT)),
            "sha256": _sha256_text(_canonical_json(value)),
        }
        for key, value in templates.items()
    }
    checks = {
        "ws61_exact_base_bound": source["base_main_sha"] == "a3fb3ea21029f01c52bc8e871dd7bcb284a31f7c",
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
    contract = {
        **source,
        "generated_from": str(SOURCE_PATH.relative_to(ROOT)),
        "generated_issue": {
            "body_path": str(FINAL_ISSUE_PATH.relative_to(ROOT)),
            "body_sha256": _sha256_text(issue_body),
            "body_line_count": len(issue_body.splitlines()),
            "body_character_count": len(issue_body),
            "github_issue_sync_verified": False,
        },
        "template_registry": template_registry,
        "launch_protocol_registry": {
            "permitted_task_count": len(source["launch_target"]["permitted_tasks"]),
            "read_order_count": len(source["read_order"]),
            "preflight_command_count": len(source["required_preflight_commands"]),
            "allowed_scope_count": len(source["allowed_scope"]),
            "prohibited_scope_count": len(source["prohibited_scope"]),
            "stop_condition_count": len(source["stop_conditions"]),
            "revocation_condition_count": len(source["launch_permit"]["revocation_conditions"]),
        },
        "readiness_snapshot": {
            "checks": checks,
            "repository_final_launch_control_complete": all(checks.values()),
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
    CONTRACT_PATH.write_text(_canonical_json(contract), encoding="utf-8")
    FINAL_ISSUE_PATH.write_text(issue_body, encoding="utf-8")
    for key, value in templates.items():
        TEMPLATE_PATHS[key].write_text(_canonical_json(value), encoding="utf-8")
    snapshot = contract["readiness_snapshot"]
    registry = contract["launch_protocol_registry"]
    print(
        "Built WS6.2 final Codex Phase 0 launch control: "
        f"{registry['read_order_count']} read-order paths, "
        f"{registry['preflight_command_count']} commands, "
        f"repository_final_launch_control_complete={str(snapshot['repository_final_launch_control_complete']).lower()}, "
        "final_release=false, hosted_controls=false, clean_macos=false, "
        "founder_approval=false, launch_permit=false, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
