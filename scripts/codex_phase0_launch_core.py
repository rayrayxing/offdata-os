from __future__ import annotations

import hashlib
import json
import platform
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts" / "codex-phase0-launch-control.json"
CORRECTION_PATH = ROOT / "contracts" / "pcfa01-launch-control-repair.json"
ISSUE_BODY_PATH = ROOT / "handoff" / "codex-phase0-issue-final.md"
FINAL_RELEASE_PATH = ROOT / "releases" / "pre-codex-final-reconciliation-2026-08-06.json"

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True, timeout=30)


def git_value(*args: str) -> str | None:
    result = run(["git", *args])
    return result.stdout.strip() if result.returncode == 0 else None


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and _SHA_RE.fullmatch(value) is not None


def _is_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST_RE.fullmatch(value) is not None


def _is_ancestor(base: object, head: object) -> bool:
    if not _is_sha(base) or not _is_sha(head):
        return False
    result = run(["git", "merge-base", "--is-ancestor", str(base), str(head)])
    return result.returncode == 0


def repair_failures(contract: dict[str, Any], repair: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    permanent = repair.get("permanent_release", {})
    binding = repair.get("launch_sha_binding", {})
    issue_binding = repair.get("issue_digest_binding", {})
    predecessor = repair.get("predecessor_launch_control", {})
    boundaries = repair.get("authorization_boundaries", {})

    require(repair.get("work_package_id") == "PCFA-01", "PCFA-01 repair identity is invalid")
    require(
        repair.get("status") == "corrective_launch_semantics_ready_manual_gates_pending",
        "PCFA-01 repair status is invalid",
    )
    require(repair.get("repository") == contract.get("repository"), "PCFA-01 repair repository drifted")
    require(
        predecessor.get("path") == "contracts/codex-phase0-launch-control.json"
        and predecessor.get("classification") == "retained_historical_package_snapshot",
        "WS6.2 launch-control predecessor classification is invalid",
    )
    require(
        permanent.get("path") == str(FINAL_RELEASE_PATH.relative_to(ROOT))
        and permanent.get("schema_version") == 2
        and permanent.get("record_type") == "permanent_post_merge_release",
        "PCFA-01 permanent release contract is invalid",
    )
    require(
        permanent.get("main_binding_semantics")
        == "release_parent_main_sha_is_exact_integrated_main_before_release_record_commit",
        "PCFA-01 release-parent semantics are invalid",
    )
    require(
        permanent.get("release_parent_is_historical_not_launch_sha") is True,
        "release parent must be classified as historical rather than launch SHA",
    )
    require(
        permanent.get("release_parent_must_be_ancestor_of_approved_launch_main") is True
        and permanent.get("release_record_must_be_ancestor_of_approved_launch_main") is True,
        "PCFA-01 release ancestry requirements are incomplete",
    )
    require(
        binding.get("all_current_launch_sha_values_must_equal") is True,
        "current launch SHA equality is not required",
    )
    require(
        binding.get("excluded_from_current_launch_sha_equality")
        == ["release_parent_main_sha", "permanent_release_record_commit_sha"],
        "historical release SHAs are not excluded from current launch SHA equality",
    )
    require(
        binding.get("release_digest_must_match_all_launch_evidence") is True,
        "release digest binding is not mandatory",
    )
    require(
        issue_binding.get("canonical_issue_body_must_match_committed_contract_digest") is True
        and issue_binding.get("founder_approval_must_bind_canonical_issue_body") is True
        and issue_binding.get("hosted_controls_must_bind_canonical_issue_body") is True
        and issue_binding.get("hosted_controls_must_bind_live_issue_19_body") is True,
        "issue digest bindings are incomplete",
    )
    require(
        boundaries.get("founder_accountability_preserved") is True
        and all(value is False for key, value in boundaries.items() if key != "founder_accountability_preserved"),
        "PCFA-01 authorization boundaries must remain fail-closed",
    )
    return failures


def final_release_record_failures(record: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    required = {
        "schema_version": 2,
        "release_id": "PRE-CODEX-FINAL-RECONCILIATION-2026-08-06",
        "work_package_id": "WS6.16",
        "record_type": "permanent_post_merge_release",
        "final_reconciliation_complete": True,
        "all_blocking_defects_closed": True,
        "exact_main_sha_bound": True,
        "tested_merge_reference_bound": True,
        "codex_start_authorized": False,
        "main_binding_semantics": "release_parent_main_sha_is_exact_integrated_main_before_release_record_commit",
    }
    for key, expected in required.items():
        require(record.get(key) == expected, f"final release field {key} is invalid")
    require(_is_sha(record.get("release_parent_main_sha")), "final release parent-main SHA is invalid")
    require(_is_sha(record.get("tested_merge_reference")), "final release tested merge reference is invalid")
    final_check = record.get("final_check", {})
    require(
        isinstance(final_check, dict) and _is_digest(final_check.get("artifact_digest_sha256")),
        "final release artifact digest is invalid",
    )
    return failures


def _final_release_state(head: str | None = None) -> dict[str, Any]:
    empty = {
        "final_workstream6_gate_complete": False,
        "final_release_parent_main_sha": None,
        "final_release_record_commit_sha": None,
        "final_release_parent_is_ancestor": False,
        "final_release_record_is_ancestor": False,
        "final_release_digest": None,
    }
    if not FINAL_RELEASE_PATH.is_file():
        return empty
    try:
        record = load_json(FINAL_RELEASE_PATH)
    except (ValueError, json.JSONDecodeError):
        return empty

    failures = final_release_record_failures(record)
    release_parent = record.get("release_parent_main_sha")
    relative = str(FINAL_RELEASE_PATH.relative_to(ROOT))
    release_commit = git_value("log", "-n", "1", "--format=%H", "--", relative)
    current_head = head or git_value("rev-parse", "HEAD")
    parent_is_ancestor = _is_ancestor(release_parent, current_head)
    record_is_ancestor = _is_ancestor(release_commit, current_head)
    complete = (
        not failures
        and _is_sha(release_commit)
        and release_commit != release_parent
        and parent_is_ancestor
        and record_is_ancestor
    )
    return {
        "final_workstream6_gate_complete": complete,
        "final_release_parent_main_sha": release_parent if _is_sha(release_parent) else None,
        "final_release_record_commit_sha": release_commit if _is_sha(release_commit) else None,
        "final_release_parent_is_ancestor": parent_is_ancestor,
        "final_release_record_is_ancestor": record_is_ancestor,
        "final_release_digest": digest_file(FINAL_RELEASE_PATH),
    }


def repository_state(contract: dict[str, Any]) -> dict[str, Any]:
    remote = git_value("ls-remote", "origin", "refs/heads/main")
    codex = git_value(
        "ls-remote",
        "origin",
        f"refs/heads/{contract['launch_target']['required_branch']}",
    )
    head = git_value("rev-parse", "HEAD")
    ancestor = run(["git", "merge-base", "--is-ancestor", contract["base_main_sha"], "HEAD"])
    return {
        "platform": platform.system(),
        "branch": git_value("branch", "--show-current"),
        "head": head,
        "clean": git_value("status", "--porcelain") == "",
        "remote_main_sha": remote.split()[0] if remote else None,
        "codex_branch_absent": codex == "",
        "ws61_main_is_ancestor": ancestor.returncode == 0,
        **_final_release_state(head),
    }


def gh_json(endpoint: str) -> Any:
    if shutil.which("gh") is None:
        raise RuntimeError("GitHub CLI is required and must be authenticated")
    result = run(["gh", "api", endpoint])
    if result.returncode != 0:
        raise RuntimeError(f"gh api failed for {endpoint}: {result.stderr.strip()}")
    return json.loads(result.stdout)


def live_repository_state(contract: dict[str, Any]) -> dict[str, Any]:
    repository = contract["repository"]
    issue1 = gh_json(f"repos/{repository}/issues/1")
    issue2 = gh_json(f"repos/{repository}/issues/2")
    issue19 = gh_json(f"repos/{repository}/issues/19")
    owner = repository.split("/", 1)[0]
    branch = contract["launch_target"]["required_branch"]
    pulls = gh_json(f"repos/{repository}/pulls?state=open&head={owner}:{branch}")
    return {
        "issue1_state": issue1.get("state"),
        "issue1_body_sha256": digest_bytes(issue1.get("body", "").encode()),
        "issue2_state": issue2.get("state"),
        "issue2_state_reason": issue2.get("state_reason"),
        "issue19_state": issue19.get("state"),
        "issue19_state_reason": issue19.get("state_reason"),
        "issue19_body_sha256": digest_bytes(issue19.get("body", "").encode()),
        "open_codex_pull_request_absent": isinstance(pulls, list) and not pulls,
    }


def semantic_failures(
    contract: dict[str, Any],
    hosted: dict[str, Any],
    doctor: dict[str, Any],
    mac: dict[str, Any],
    approval: dict[str, Any],
    repo: dict[str, Any],
    live: dict[str, Any],
    *,
    doctor_digest: str,
    repair: dict[str, Any] | None = None,
) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    repair_value = repair or {}
    failures.extend(repair_failures(contract, repair_value))
    target = contract["launch_target"]
    repository = contract["repository"]
    snapshot = contract.get("readiness_snapshot", {})

    require(
        contract.get("status") == "repository_launch_control_complete_manual_gates_pending",
        "legacy launch-control status alias is invalid",
    )
    require(
        contract.get("final_status") == "final_launch_control_reconciled_manual_gates_pending",
        "final launch-control contract status is invalid",
    )
    require(
        snapshot.get("repository_final_launch_control_complete") is True,
        "repository final launch-control package is incomplete",
    )
    require(
        snapshot.get("repository_launch_control_complete") is True,
        "legacy repository launch-control projection is incomplete",
    )
    require(
        snapshot.get("codex_start_authorized") is False,
        "committed launch-control contract must remain unauthorized",
    )
    require(
        contract.get("generated_issue", {}).get("body_path") == "handoff/codex-phase0-issue-final.md",
        "controlling issue path is not final",
    )
    require(
        contract.get("final_release_gate", {}).get("must_exist_before_permit") is True,
        "final Workstream 6 release gate is not mandatory",
    )

    require(
        hosted.get("evidence_type") == "github_hosted_controls_attestation",
        "hosted-controls evidence type is invalid",
    )
    require(
        hosted.get("repository") == repository and hosted.get("issue_number") == 19,
        "hosted-controls evidence targets the wrong repository or issue",
    )
    require(
        hosted.get("issue_state") == "closed" and hosted.get("issue_state_reason") == "completed",
        "hosted-controls issue must be closed as completed",
    )
    require(
        hosted.get("required_status_check_name") == contract["required_status_check"]["job_name"],
        "hosted-controls status-check identity is stale",
    )
    controls = hosted.get("controls", {})
    require(
        isinstance(controls, dict) and len(controls) == 8 and all(value is True for value in controls.values()),
        "all eight hosted controls require explicit true attestations",
    )
    cleanup = hosted.get("branch_cleanup", {})
    require(cleanup.get("complete") is True, "historical branch cleanup is incomplete")
    require(
        cleanup.get("remaining_branches") == ["main"],
        "final branch inventory must contain only main before launch",
    )
    require(bool(hosted.get("evidence_attachments")), "hosted-control evidence attachments are required")
    require(
        hosted.get("attested") is True and hosted.get("attested_by") == "rayrayxing",
        "hosted-control Founder attestation is missing",
    )

    require(
        doctor.get("report_type") == "offdata_pre_codex_macos_doctor",
        "macOS doctor report type is invalid",
    )
    require(
        doctor.get("non_destructive") is True and doctor.get("generated_values_include_secrets") is False,
        "macOS doctor report must be non-destructive and redacted",
    )
    require(doctor.get("machine_checks_passed") is True, "macOS doctor machine checks did not all pass")
    checks = doctor.get("checks", {})
    require(
        isinstance(checks, dict) and bool(checks) and all(value is True for value in checks.values()),
        "every macOS doctor check must pass",
    )
    doctor_git = doctor.get("git", {})
    require(
        doctor_git.get("clean") is True and doctor_git.get("branch") == "main",
        "macOS doctor must report a clean main branch",
    )
    require(doctor.get("codex_start_authorized") is False, "macOS doctor may never authorize Codex")

    require(
        mac.get("evidence_type") == "clean_macos_environment_attestation",
        "clean-macOS attestation type is invalid",
    )
    require(mac.get("repository") == repository, "clean-macOS attestation targets the wrong repository")
    require(mac.get("doctor_report_sha256") == doctor_digest, "clean-macOS attestation doctor digest mismatch")
    manual = mac.get("manual_attestations", {})
    require(
        isinstance(manual, dict) and len(manual) == 5 and all(value is True for value in manual.values()),
        "all clean-macOS manual attestations are required",
    )
    require(
        mac.get("clean_macos_environment_verified") is True,
        "clean-macOS environment is not verified",
    )
    require(
        mac.get("attested") is True and mac.get("attested_by") == "rayrayxing",
        "clean-macOS Founder attestation is missing",
    )

    require(
        approval.get("evidence_type") == "founder_codex_phase0_authorization",
        "Founder approval evidence type is invalid",
    )
    require(
        approval.get("repository") == repository and approval.get("canonical_issue") == 1,
        "Founder approval targets the wrong repository or issue",
    )
    require(
        approval.get("decision") == "approve_codex_phase0_only",
        "Founder decision must explicitly approve Codex Phase 0 only",
    )
    require(approval.get("approved_phase") == "Codex Phase 0 only", "Founder approval phase is invalid")
    require(
        approval.get("approved_tasks") == target["permitted_tasks"],
        "Founder approval tasks must be exactly P0.1-P0.4",
    )
    require(approval.get("required_branch") == target["required_branch"], "Founder approval branch is invalid")
    require(
        approval.get("draft_pull_request_required") is True,
        "Founder approval must require a draft pull request",
    )
    require(
        approval.get("merge_authorized") is False and approval.get("phase1_authorized") is False,
        "Founder approval cannot authorize merge or Phase 1",
    )
    require(bool(approval.get("authorized_at")), "Founder approval timestamp is required")
    require(
        approval.get("attested") is True and approval.get("attested_by") == "rayrayxing",
        "explicit Founder approval attestation is missing",
    )

    current_sha_values = {
        approval.get("approved_main_sha"),
        hosted.get("approved_main_sha"),
        mac.get("approved_main_sha"),
        doctor_git.get("head"),
        repo.get("head"),
        repo.get("remote_main_sha"),
    }
    require(
        None not in current_sha_values and len(current_sha_values) == 1,
        "all current launch evidence and repository state must bind to one exact main SHA",
    )
    current_sha = approval.get("approved_main_sha")

    release_digest_values = {
        hosted.get("final_workstream6_release_sha256"),
        mac.get("final_workstream6_release_sha256"),
        approval.get("final_workstream6_release_sha256"),
        repo.get("final_release_digest"),
    }
    require(
        None not in release_digest_values and len(release_digest_values) == 1,
        "all launch evidence must bind the exact permanent Workstream 6 release digest",
    )
    require(
        all(_is_digest(value) for value in release_digest_values),
        "permanent Workstream 6 release digest binding is malformed",
    )

    issue1_digest_values = {
        contract.get("generated_issue", {}).get("body_sha256"),
        hosted.get("canonical_issue_body_sha256"),
        approval.get("canonical_issue_body_sha256"),
        live.get("issue1_body_sha256"),
    }
    require(
        None not in issue1_digest_values and len(issue1_digest_values) == 1,
        "canonical issue #1 body digest drifted across launch evidence",
    )
    require(
        hosted.get("issue_19_body_sha256") == live.get("issue19_body_sha256")
        and _is_digest(hosted.get("issue_19_body_sha256")),
        "issue #19 body digest drifted after hosted-controls attestation",
    )

    require(repo.get("platform") == "Darwin", "real launch preparation must run on macOS")
    require(
        repo.get("branch") == "main" and repo.get("clean") is True,
        "launch preparation requires a clean local main branch",
    )
    require(repo.get("ws61_main_is_ancestor") is True, "approved main does not include WS6.1")
    require(
        repo.get("final_workstream6_gate_complete") is True,
        "final Workstream 6 release is missing, invalid, stale or outside approved-main ancestry",
    )
    require(_is_digest(repo.get("final_release_digest")), "final Workstream 6 release digest is unavailable")
    require(
        _is_sha(repo.get("final_release_parent_main_sha"))
        and repo.get("final_release_parent_is_ancestor") is True,
        "historical release-parent main is not an ancestor of approved launch main",
    )
    require(
        _is_sha(repo.get("final_release_record_commit_sha"))
        and repo.get("final_release_record_is_ancestor") is True,
        "permanent release record commit is not an ancestor of approved launch main",
    )
    require(
        repo.get("final_release_parent_main_sha") != current_sha,
        "approved launch main cannot equal the pre-release parent main SHA",
    )
    require(
        repo.get("final_release_record_commit_sha") != repo.get("final_release_parent_main_sha"),
        "permanent release record commit cannot equal its historical parent-main SHA",
    )
    require(repo.get("codex_branch_absent") is True, "Codex Phase 0 branch already exists")

    require(live.get("issue1_state") == "open", "canonical issue #1 must remain open")
    historical_digest = contract["historical_authority"]["workstream5_issue_body"]["sha256"]
    require(
        live.get("issue1_body_sha256") != historical_digest,
        "Workstream 5 issue body is historical and cannot satisfy final launch",
    )
    require(
        live.get("issue2_state") == "closed" and live.get("issue2_state_reason") == "duplicate",
        "issue #2 must remain closed as duplicate",
    )
    require(
        live.get("issue19_state") == "closed" and live.get("issue19_state_reason") == "completed",
        "issue #19 must be closed as completed",
    )
    require(
        live.get("open_codex_pull_request_absent") is True,
        "an open Codex Phase 0 pull request already exists",
    )
    return failures


def build_permit(
    contract: dict[str, Any],
    paths: list[Path],
    approval: dict[str, Any],
    repo: dict[str, Any],
) -> dict[str, Any]:
    digests = {
        "final_launch_control": digest_file(CONTRACT_PATH),
        "launch_control_repair": digest_file(CORRECTION_PATH),
        "canonical_issue_body": digest_file(ISSUE_BODY_PATH),
        "final_workstream6_release": digest_file(FINAL_RELEASE_PATH),
        "hosted_controls": digest_file(paths[0]),
        "macos_report": digest_file(paths[1]),
        "macos_attestation": digest_file(paths[2]),
        "founder_approval": digest_file(paths[3]),
    }
    identity = {
        "repository": contract["repository"],
        "approved_main_sha": approval["approved_main_sha"],
        "final_release_parent_main_sha": repo["final_release_parent_main_sha"],
        "final_release_record_commit_sha": repo["final_release_record_commit_sha"],
        "branch": contract["launch_target"]["required_branch"],
        "tasks": contract["launch_target"]["permitted_tasks"],
        "required_status_check": contract["required_status_check"]["job_name"],
        "evidence_digests": digests,
    }
    return {
        "schema_version": "2.1.0",
        "permit_type": "codex_phase0_launch_permit",
        "launch_id": digest_bytes(canonical_json(identity).encode()),
        "issued_at": approval["authorized_at"],
        "repository": contract["repository"],
        "approved_main_sha": approval["approved_main_sha"],
        "final_workstream6_release_parent_main_sha": repo["final_release_parent_main_sha"],
        "final_workstream6_release_record_commit_sha": repo["final_release_record_commit_sha"],
        "canonical_issue": 1,
        "hosted_controls_issue": 19,
        "required_status_check": contract["required_status_check"]["job_name"],
        "branch": contract["launch_target"]["required_branch"],
        "phase": "Codex Phase 0 only",
        "tasks": contract["launch_target"]["permitted_tasks"],
        "required_first_commit_ack": contract["launch_target"]["required_first_commit_ack"],
        "draft_pull_request_required": True,
        "merge_authorized": False,
        "phase1_authorized": False,
        "single_use": True,
        "stale_on_main_advance": True,
        "stale_on_final_release_advance": True,
        "evidence_digests": digests,
        "scope": contract["allowed_scope"],
        "prohibitions": contract["prohibited_scope"],
        "codex_start_authorized": True,
    }
