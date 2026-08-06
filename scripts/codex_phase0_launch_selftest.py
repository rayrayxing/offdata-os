from __future__ import annotations

import copy
from typing import Any

from codex_phase0_launch_core import canonical_json, digest_bytes, semantic_failures


def synthetic_bundle(contract: dict[str, Any]) -> tuple[Any, ...]:
    sha = "b" * 40
    doctor = {
        "report_type": "offdata_pre_codex_macos_doctor",
        "non_destructive": True,
        "generated_values_include_secrets": False,
        "machine_checks_passed": True,
        "checks": {key: True for key in ("os", "arch", "git", "disk", "container")},
        "git": {"clean": True, "branch": "main", "head": sha},
        "codex_start_authorized": False,
    }
    doctor_digest = digest_bytes(canonical_json(doctor).encode())
    hosted = {
        "evidence_type": "github_hosted_controls_attestation",
        "repository": contract["repository"],
        "issue_number": 19,
        "issue_state": "closed",
        "issue_state_reason": "completed",
        "approved_main_sha": sha,
        "required_status_check_name": contract["required_status_check"]["job_name"],
        "controls": {f"control_{index}": True for index in range(8)},
        "branch_cleanup": {"complete": True, "remaining_branches": ["main"]},
        "evidence_attachments": [{"kind": "settings_audit", "sha256": "a" * 64}],
        "attested": True,
        "attested_by": "rayrayxing",
    }
    mac = {
        "evidence_type": "clean_macos_environment_attestation",
        "repository": contract["repository"],
        "approved_main_sha": sha,
        "doctor_report_sha256": doctor_digest,
        "manual_attestations": {f"attestation_{index}": True for index in range(5)},
        "clean_macos_environment_verified": True,
        "attested": True,
        "attested_by": "rayrayxing",
    }
    approval = {
        "evidence_type": "founder_codex_phase0_authorization",
        "repository": contract["repository"],
        "canonical_issue": 1,
        "decision": "approve_codex_phase0_only",
        "approved_main_sha": sha,
        "approved_phase": "Codex Phase 0 only",
        "approved_tasks": contract["launch_target"]["permitted_tasks"],
        "required_branch": contract["launch_target"]["required_branch"],
        "draft_pull_request_required": True,
        "merge_authorized": False,
        "phase1_authorized": False,
        "authorized_at": "2026-08-06T17:22:00+08:00",
        "attested": True,
        "attested_by": "rayrayxing",
    }
    repo = {
        "platform": "Darwin",
        "branch": "main",
        "head": sha,
        "clean": True,
        "remote_main_sha": sha,
        "final_release_main_sha": sha,
        "final_release_digest": "f" * 64,
        "final_workstream6_gate_complete": True,
        "codex_branch_absent": True,
        "ws61_main_is_ancestor": True,
    }
    live = {
        "issue1_state": "open",
        "issue1_body_sha256": contract["generated_issue"]["body_sha256"],
        "issue2_state": "closed",
        "issue2_state_reason": "duplicate",
        "issue19_state": "closed",
        "issue19_state_reason": "completed",
        "open_codex_pull_request_absent": True,
    }
    return hosted, doctor, mac, approval, repo, live, doctor_digest


def _set(value: dict[str, Any], path: tuple[str, ...], replacement: Any) -> None:
    node: Any = value
    for part in path[:-1]:
        node = node[part]
    node[path[-1]] = replacement


def run_self_test(contract: dict[str, Any]) -> int:
    base = synthetic_bundle(contract)
    if semantic_failures(contract, *base[:-1], doctor_digest=base[-1]):
        raise SystemExit("valid synthetic final launch bundle was rejected")

    cases: list[tuple[str, str, tuple[str, ...], Any]] = [
        *(("hosted", f"control_{index}", ("controls", f"control_{index}"), False) for index in range(8)),
        ("hosted", "cleanup incomplete", ("branch_cleanup", "complete"), False),
        ("hosted", "extra branch", ("branch_cleanup", "remaining_branches"), ["main", "old"]),
        ("hosted", "issue open", ("issue_state",), "open"),
        ("hosted", "old status check", ("required_status_check_name",), "Validate Codex Phase 0 launch control and complete prior release"),
        ("hosted", "unattested", ("attested",), False),
        ("doctor", "failed", ("machine_checks_passed",), False),
        ("doctor", "dirty", ("git", "clean"), False),
        ("doctor", "authorizes", ("codex_start_authorized",), True),
        ("mac", "unverified", ("clean_macos_environment_verified",), False),
        ("mac", "unattested", ("attested",), False),
        ("approval", "missing", ("decision",), "not_approved"),
        ("approval", "merge", ("merge_authorized",), True),
        ("approval", "phase1", ("phase1_authorized",), True),
        ("approval", "scope", ("approved_tasks",), ["P0.1"]),
        ("approval", "unattested", ("attested",), False),
        ("repo", "linux", ("platform",), "Linux"),
        ("repo", "wrong branch", ("branch",), "feature"),
        ("repo", "dirty", ("clean",), False),
        ("repo", "branch exists", ("codex_branch_absent",), False),
        ("repo", "WS6.1 missing", ("ws61_main_is_ancestor",), False),
        ("repo", "final release missing", ("final_workstream6_gate_complete",), False),
        ("repo", "final release digest missing", ("final_release_digest",), None),
        ("repo", "final release SHA drift", ("final_release_main_sha",), "d" * 40),
        ("live", "issue1 closed", ("issue1_state",), "closed"),
        ("live", "issue1 old Workstream 5 digest", ("issue1_body_sha256",), contract["historical_authority"]["workstream5_issue_body"]["sha256"]),
        ("live", "issue1 drift", ("issue1_body_sha256",), "c" * 64),
        ("live", "issue19 open", ("issue19_state",), "open"),
        ("live", "issue2 open", ("issue2_state",), "open"),
        ("live", "PR exists", ("open_codex_pull_request_absent",), False),
    ]
    indexes = {"hosted": 0, "doctor": 1, "mac": 2, "approval": 3, "repo": 4, "live": 5}
    mutations: list[tuple[Any, ...]] = []
    for target, label, path, replacement in cases:
        values = [copy.deepcopy(item) for item in base[:-1]]
        _set(values[indexes[target]], path, replacement)
        mutations.append((*values, base[-1], label))

    for target in ("hosted", "mac", "approval"):
        values = [copy.deepcopy(item) for item in base[:-1]]
        values[indexes[target]]["approved_main_sha"] = "d" * 40
        mutations.append((*values, base[-1], f"{target} SHA drift"))

    values = [copy.deepcopy(item) for item in base[:-1]]
    values[2]["doctor_report_sha256"] = "e" * 64
    mutations.append((*values, base[-1], "doctor digest drift"))

    for index, (*values, digest, label) in enumerate(mutations, start=1):
        if not semantic_failures(contract, *values, doctor_digest=digest):
            raise SystemExit(f"final launch self-test mutation {index} was not rejected: {label}")
    return len(mutations)
