from __future__ import annotations

import copy
from typing import Any

from codex_phase0_launch_core import (
    CURRENT_STATE_PATH,
    FINAL_RELEASE_PATH,
    ISSUE19_BODY_PATH,
    ISSUE_BODY_PATH,
    canonical_json,
    current_state_failures,
    digest_bytes,
    digest_file,
    final_release_record_failures,
    load_json,
    repair_failures,
    semantic_failures,
)


def synthetic_bundle(state: dict[str, Any]) -> tuple[Any, ...]:
    current_sha = "b" * 40
    release_parent_sha = "a" * 40
    release_record_commit_sha = "c" * 40
    release_digest = "f" * 64
    state_digest = digest_file(CURRENT_STATE_PATH)
    issue1_digest = digest_file(ISSUE_BODY_PATH)
    issue19_digest = digest_file(ISSUE19_BODY_PATH)
    target = state["launch_target"]

    doctor = {
        "report_type": "offdata_pre_codex_macos_doctor",
        "non_destructive": True,
        "generated_values_include_secrets": False,
        "machine_checks_passed": True,
        "checks": {key: True for key in ("os", "arch", "git", "disk", "container")},
        "git": {"clean": True, "branch": "main", "head": current_sha},
        "codex_start_authorized": False,
    }
    doctor_digest = digest_bytes(canonical_json(doctor).encode())
    hosted = {
        "schema_version": "2.2.0",
        "evidence_type": "github_hosted_controls_attestation",
        "repository": state["repository"],
        "issue_number": 19,
        "issue_state": "closed",
        "issue_state_reason": "completed",
        "approved_main_sha": current_sha,
        "required_status_check_name": target["required_status_check"],
        "final_workstream6_release_sha256": release_digest,
        "current_operational_state_sha256": state_digest,
        "canonical_issue_body_sha256": issue1_digest,
        "issue_19_body_sha256": issue19_digest,
        "controls": {f"control_{index}": True for index in range(8)},
        "branch_cleanup": {"complete": True, "remaining_branches": ["main"]},
        "evidence_attachments": [{"kind": "settings_audit", "sha256": "a" * 64}],
        "attested": True,
        "attested_by": "rayrayxing",
    }
    mac = {
        "schema_version": "2.2.0",
        "evidence_type": "clean_macos_environment_attestation",
        "repository": state["repository"],
        "approved_main_sha": current_sha,
        "doctor_report_sha256": doctor_digest,
        "final_workstream6_release_sha256": release_digest,
        "current_operational_state_sha256": state_digest,
        "manual_attestations": {f"attestation_{index}": True for index in range(5)},
        "clean_macos_environment_verified": True,
        "attested": True,
        "attested_by": "rayrayxing",
    }
    approval = {
        "schema_version": "2.2.0",
        "evidence_type": "founder_codex_phase0_authorization",
        "repository": state["repository"],
        "canonical_issue": 1,
        "decision": "approve_codex_phase0_only",
        "approved_main_sha": current_sha,
        "canonical_issue_body_sha256": issue1_digest,
        "final_workstream6_release_sha256": release_digest,
        "current_operational_state_sha256": state_digest,
        "approved_phase": "Codex Phase 0 only",
        "approved_tasks": target["permitted_tasks"],
        "required_branch": target["required_branch"],
        "draft_pull_request_required": True,
        "merge_authorized": False,
        "phase1_authorized": False,
        "authorized_at": "2026-08-07T22:49:00+08:00",
        "attested": True,
        "attested_by": "rayrayxing",
    }
    repo = {
        "platform": "Darwin",
        "branch": "main",
        "head": current_sha,
        "clean": True,
        "remote_main_sha": current_sha,
        "final_release_parent_main_sha": release_parent_sha,
        "final_release_record_commit_sha": release_record_commit_sha,
        "final_release_parent_is_ancestor": True,
        "final_release_record_is_ancestor": True,
        "final_release_digest": release_digest,
        "final_workstream6_gate_complete": True,
        "codex_branch_absent": True,
    }
    live = {
        "issue1_state": "open",
        "issue1_body_sha256": issue1_digest,
        "issue2_state": "closed",
        "issue2_state_reason": "duplicate",
        "issue19_state": "closed",
        "issue19_state_reason": "completed",
        "issue19_body_sha256": issue19_digest,
        "open_codex_pull_request_absent": True,
    }
    return hosted, doctor, mac, approval, repo, live, doctor_digest


def _set(value: dict[str, Any], path: tuple[str, ...], replacement: Any) -> None:
    node: Any = value
    for part in path[:-1]:
        node = node[part]
    node[path[-1]] = replacement


def run_self_test(
    state: dict[str, Any],
    predecessor: dict[str, Any],
    repair: dict[str, Any],
) -> int:
    repair_errors = repair_failures(predecessor, repair)
    if repair_errors:
        raise SystemExit("PCFA-01 corrective launch contract was rejected: " + "; ".join(repair_errors))
    state_errors = current_state_failures(state, predecessor, repair)
    if state_errors:
        raise SystemExit("PCFA-02 current operational state was rejected: " + "; ".join(state_errors))

    actual_release = load_json(FINAL_RELEASE_PATH)
    release_errors = final_release_record_failures(actual_release)
    if release_errors:
        raise SystemExit("actual WS6.16 schema-v2 permanent release was rejected: " + "; ".join(release_errors))
    if "integrated_main_sha" in actual_release or "main_sha" in actual_release:
        raise SystemExit("actual WS6.16 release unexpectedly contains a legacy launch-main field")

    base = synthetic_bundle(state)
    if semantic_failures(
        state,
        predecessor,
        *base[:-1],
        doctor_digest=base[-1],
        repair=repair,
    ):
        raise SystemExit("valid synthetic descendant launch bundle was rejected")

    cases: list[tuple[str, str, tuple[str, ...], Any]] = [
        *(("hosted", f"control_{index}", ("controls", f"control_{index}"), False) for index in range(8)),
        ("hosted", "old evidence version", ("schema_version",), "2.1.0"),
        ("hosted", "cleanup incomplete", ("branch_cleanup", "complete"), False),
        ("hosted", "extra branch", ("branch_cleanup", "remaining_branches"), ["main", "old"]),
        ("hosted", "issue open", ("issue_state",), "open"),
        ("hosted", "old status check", ("required_status_check_name",), "old check"),
        ("hosted", "unattested", ("attested",), False),
        ("hosted", "release digest drift", ("final_workstream6_release_sha256",), "d" * 64),
        ("hosted", "state digest drift", ("current_operational_state_sha256",), "d" * 64),
        ("hosted", "issue1 digest drift", ("canonical_issue_body_sha256",), "d" * 64),
        ("hosted", "issue19 digest drift", ("issue_19_body_sha256",), "d" * 64),
        ("doctor", "failed", ("machine_checks_passed",), False),
        ("doctor", "dirty", ("git", "clean"), False),
        ("doctor", "wrong branch", ("git", "branch"), "feature"),
        ("doctor", "authorizes", ("codex_start_authorized",), True),
        ("mac", "old evidence version", ("schema_version",), "2.1.0"),
        ("mac", "unverified", ("clean_macos_environment_verified",), False),
        ("mac", "unattested", ("attested",), False),
        ("mac", "release digest drift", ("final_workstream6_release_sha256",), "d" * 64),
        ("mac", "state digest drift", ("current_operational_state_sha256",), "d" * 64),
        ("approval", "old evidence version", ("schema_version",), "2.1.0"),
        ("approval", "missing", ("decision",), "not_approved"),
        ("approval", "merge", ("merge_authorized",), True),
        ("approval", "phase1", ("phase1_authorized",), True),
        ("approval", "scope", ("approved_tasks",), ["P0.1"]),
        ("approval", "unattested", ("attested",), False),
        ("approval", "release digest drift", ("final_workstream6_release_sha256",), "d" * 64),
        ("approval", "state digest drift", ("current_operational_state_sha256",), "d" * 64),
        ("approval", "issue1 digest drift", ("canonical_issue_body_sha256",), "d" * 64),
        ("repo", "linux", ("platform",), "Linux"),
        ("repo", "wrong branch", ("branch",), "feature"),
        ("repo", "dirty", ("clean",), False),
        ("repo", "branch exists", ("codex_branch_absent",), False),
        ("repo", "final release missing", ("final_workstream6_gate_complete",), False),
        ("repo", "final release digest missing", ("final_release_digest",), None),
        ("repo", "final release digest drift", ("final_release_digest",), "d" * 64),
        ("repo", "release parent ancestry missing", ("final_release_parent_is_ancestor",), False),
        ("repo", "release record ancestry missing", ("final_release_record_is_ancestor",), False),
        ("repo", "release record commit missing", ("final_release_record_commit_sha",), None),
        ("repo", "release parent equals launch main", ("final_release_parent_main_sha",), "b" * 40),
        ("repo", "release record equals release parent", ("final_release_record_commit_sha",), "a" * 40),
        ("live", "issue1 closed", ("issue1_state",), "closed"),
        ("live", "issue1 old Workstream 5 digest", ("issue1_body_sha256",), predecessor["historical_authority"]["workstream5_issue_body"]["sha256"]),
        ("live", "issue1 drift", ("issue1_body_sha256",), "c" * 64),
        ("live", "issue19 open", ("issue19_state",), "open"),
        ("live", "issue19 body drift", ("issue19_body_sha256",), "c" * 64),
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
        mutations.append((*values, base[-1], f"{target} current SHA drift"))

    values = [copy.deepcopy(item) for item in base[:-1]]
    values[4]["head"] = "d" * 40
    mutations.append((*values, base[-1], "repository head drift"))

    values = [copy.deepcopy(item) for item in base[:-1]]
    values[4]["remote_main_sha"] = "d" * 40
    mutations.append((*values, base[-1], "remote main drift"))

    values = [copy.deepcopy(item) for item in base[:-1]]
    values[2]["doctor_report_sha256"] = "e" * 64
    mutations.append((*values, base[-1], "doctor digest drift"))

    values = [copy.deepcopy(item) for item in base[:-1]]
    pre_release_sha = values[4]["final_release_parent_main_sha"]
    values[0]["approved_main_sha"] = pre_release_sha
    values[1]["git"]["head"] = pre_release_sha
    values[2]["approved_main_sha"] = pre_release_sha
    values[3]["approved_main_sha"] = pre_release_sha
    values[4]["head"] = pre_release_sha
    values[4]["remote_main_sha"] = pre_release_sha
    values[4]["final_release_record_is_ancestor"] = False
    mutations.append((*values, base[-1], "pre-release ancestor used as launch main"))

    rejected = 0
    for index, (*values, digest, label) in enumerate(mutations, start=1):
        if not semantic_failures(
            state,
            predecessor,
            *values,
            doctor_digest=digest,
            repair=repair,
        ):
            raise SystemExit(f"PCFA-02 launch self-test mutation {index} was not rejected: {label}")
        rejected += 1

    repair_mutations = [
        ("release parent treated as launch SHA", ("permanent_release", "release_parent_is_historical_not_launch_sha"), False),
        ("release parent ancestry disabled", ("permanent_release", "release_parent_must_be_ancestor_of_approved_launch_main"), False),
        ("release record ancestry disabled", ("permanent_release", "release_record_must_be_ancestor_of_approved_launch_main"), False),
        ("release digest binding disabled", ("launch_sha_binding", "release_digest_must_match_all_launch_evidence"), False),
        ("historical SHA exclusion drift", ("launch_sha_binding", "excluded_from_current_launch_sha_equality"), []),
        ("issue19 digest binding disabled", ("issue_digest_binding", "hosted_controls_must_bind_live_issue_19_body"), False),
        ("implementation authorized", ("authorization_boundaries", "phase0_implementation_authorized"), True),
    ]
    for label, path, replacement in repair_mutations:
        mutated = copy.deepcopy(repair)
        _set(mutated, path, replacement)
        if not repair_failures(predecessor, mutated):
            raise SystemExit(f"PCFA-01 corrective-contract mutation was not rejected: {label}")
        rejected += 1

    state_mutations = [
        ("old launch contract promoted", ("current_authority", "operational_state"), "contracts/codex-phase0-launch-control.json"),
        ("old handoff promoted", ("current_authority", "machine_handoff"), "handoff/codex-phase0-handoff.json"),
        ("old issue promoted", ("current_authority", "canonical_issue_body"), "handoff/codex-phase0-issue-final.md"),
        ("historical readiness enabled", ("state_semantics", "historical_snapshot_readiness_must_not_drive_current_launch_decisions"), False),
        ("release parent equality enabled", ("release_semantics", "release_parent_excluded_from_current_launch_sha_equality"), False),
        ("current-state permit staleness disabled", ("launch_permit", "stale_on_current_operational_state_change"), False),
        ("manual Codex authorization committed", ("manual_launch_gates", "codex_start_authorized"), True),
        ("runtime authorized", ("boundaries", "runtime_activation_authorized"), True),
    ]
    for label, path, replacement in state_mutations:
        mutated = copy.deepcopy(state)
        _set(mutated, path, replacement)
        if not current_state_failures(mutated, predecessor, repair):
            raise SystemExit(f"PCFA-02 current-state mutation was not rejected: {label}")
        rejected += 1

    return rejected
