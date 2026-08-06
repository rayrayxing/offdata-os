from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts" / "codex-phase0-launch-control.json"
ISSUE_BODY_PATH = ROOT / "handoff" / "codex-phase0-issue-workstream5.md"


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


def repository_state(contract: dict[str, Any]) -> dict[str, Any]:
    remote = git_value("ls-remote", "origin", "refs/heads/main")
    codex = git_value("ls-remote", "origin", f"refs/heads/{contract['launch_target']['required_branch']}")
    ancestor = run(["git", "merge-base", "--is-ancestor", contract["pre_workstream_main_sha"], "HEAD"])
    return {
        "platform": platform.system(),
        "branch": git_value("branch", "--show-current"),
        "head": git_value("rev-parse", "HEAD"),
        "clean": git_value("status", "--porcelain") == "",
        "remote_main_sha": remote.split()[0] if remote else None,
        "codex_branch_absent": codex == "",
        "pre_workstream_main_is_ancestor": ancestor.returncode == 0,
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
        "open_codex_pull_request_absent": isinstance(pulls, list) and not pulls,
    }


def semantic_failures(
    contract: dict[str, Any], hosted: dict[str, Any], doctor: dict[str, Any],
    mac: dict[str, Any], approval: dict[str, Any], repo: dict[str, Any],
    live: dict[str, Any], *, doctor_digest: str,
) -> list[str]:
    failures: list[str] = []
    target = contract["launch_target"]
    repository = contract["repository"]

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    snapshot = contract.get("readiness_snapshot", {})
    require(contract.get("status") == "repository_launch_control_complete_manual_gates_pending", "launch-control contract status is invalid")
    require(snapshot.get("repository_launch_control_complete") is True, "repository launch-control package is incomplete")
    require(snapshot.get("codex_start_authorized") is False, "committed launch-control contract must remain unauthorized")

    require(hosted.get("evidence_type") == "github_hosted_controls_attestation", "hosted-controls evidence type is invalid")
    require(hosted.get("repository") == repository and hosted.get("issue_number") == 19, "hosted-controls evidence targets the wrong repository or issue")
    require(hosted.get("issue_state") == "closed" and hosted.get("issue_state_reason") == "completed", "hosted-controls issue must be closed as completed")
    controls = hosted.get("controls", {})
    require(isinstance(controls, dict) and len(controls) == 8 and all(value is True for value in controls.values()), "all eight hosted controls require explicit true attestations")
    cleanup = hosted.get("branch_cleanup", {})
    require(cleanup.get("complete") is True, "historical branch cleanup is incomplete")
    require(cleanup.get("remaining_branches") == ["main"], "final branch inventory must contain only main before launch")
    require(bool(hosted.get("evidence_attachments")), "hosted-control evidence attachments are required")
    require(hosted.get("attested") is True and hosted.get("attested_by") == "rayrayxing", "hosted-control Founder attestation is missing")

    require(doctor.get("report_type") == "offdata_pre_codex_macos_doctor", "macOS doctor report type is invalid")
    require(doctor.get("non_destructive") is True and doctor.get("generated_values_include_secrets") is False, "macOS doctor report must be non-destructive and redacted")
    require(doctor.get("machine_checks_passed") is True, "macOS doctor machine checks did not all pass")
    checks = doctor.get("checks", {})
    require(isinstance(checks, dict) and bool(checks) and all(value is True for value in checks.values()), "every macOS doctor check must pass")
    doctor_git = doctor.get("git", {})
    require(doctor_git.get("clean") is True and doctor_git.get("branch") == "main", "macOS doctor must report a clean main branch")
    require(doctor.get("codex_start_authorized") is False, "macOS doctor may never authorize Codex")

    require(mac.get("evidence_type") == "clean_macos_environment_attestation", "clean-macOS attestation type is invalid")
    require(mac.get("repository") == repository, "clean-macOS attestation targets the wrong repository")
    require(mac.get("doctor_report_sha256") == doctor_digest, "clean-macOS attestation doctor digest mismatch")
    manual = mac.get("manual_attestations", {})
    require(isinstance(manual, dict) and len(manual) == 5 and all(value is True for value in manual.values()), "all clean-macOS manual attestations are required")
    require(mac.get("clean_macos_environment_verified") is True, "clean-macOS environment is not verified")
    require(mac.get("attested") is True and mac.get("attested_by") == "rayrayxing", "clean-macOS Founder attestation is missing")

    require(approval.get("evidence_type") == "founder_codex_phase0_authorization", "Founder approval evidence type is invalid")
    require(approval.get("repository") == repository and approval.get("canonical_issue") == 1, "Founder approval targets the wrong repository or issue")
    require(approval.get("decision") == "approve_codex_phase0_only", "Founder decision must explicitly approve Codex Phase 0 only")
    require(approval.get("approved_phase") == "Codex Phase 0 only", "Founder approval phase is invalid")
    require(approval.get("approved_tasks") == target["permitted_tasks"], "Founder approval tasks must be exactly P0.1-P0.4")
    require(approval.get("required_branch") == target["required_branch"], "Founder approval branch is invalid")
    require(approval.get("draft_pull_request_required") is True, "Founder approval must require a draft pull request")
    require(approval.get("merge_authorized") is False and approval.get("phase1_authorized") is False, "Founder approval cannot authorize merge or Phase 1")
    require(bool(approval.get("authorized_at")), "Founder approval timestamp is required")
    require(approval.get("attested") is True and approval.get("attested_by") == "rayrayxing", "explicit Founder approval attestation is missing")

    sha_values = {approval.get("approved_main_sha"), hosted.get("approved_main_sha"), mac.get("approved_main_sha"), doctor_git.get("head"), repo.get("head"), repo.get("remote_main_sha")}
    require(None not in sha_values and len(sha_values) == 1, "all evidence and repository state must bind to one exact main SHA")
    require(repo.get("platform") == "Darwin", "real launch preparation must run on macOS")
    require(repo.get("branch") == "main" and repo.get("clean") is True, "launch preparation requires a clean local main branch")
    require(repo.get("pre_workstream_main_is_ancestor") is True, "approved main does not include the Workstream 5 launch control")
    require(repo.get("codex_branch_absent") is True, "Codex Phase 0 branch already exists")

    require(live.get("issue1_state") == "open", "canonical issue #1 must remain open")
    require(live.get("issue1_body_sha256") == contract.get("generated_issue", {}).get("body_sha256"), "canonical issue #1 body digest is stale")
    require(live.get("issue2_state") == "closed" and live.get("issue2_state_reason") == "duplicate", "issue #2 must remain closed as duplicate")
    require(live.get("issue19_state") == "closed" and live.get("issue19_state_reason") == "completed", "issue #19 must be closed as completed")
    require(live.get("open_codex_pull_request_absent") is True, "an open Codex Phase 0 pull request already exists")
    return failures


def build_permit(contract: dict[str, Any], paths: list[Path], approval: dict[str, Any]) -> dict[str, Any]:
    digests = {
        "launch_control": digest_file(CONTRACT_PATH),
        "canonical_issue_body": digest_file(ISSUE_BODY_PATH),
        "hosted_controls": digest_file(paths[0]),
        "macos_report": digest_file(paths[1]),
        "macos_attestation": digest_file(paths[2]),
        "founder_approval": digest_file(paths[3]),
    }
    identity = {"repository": contract["repository"], "approved_main_sha": approval["approved_main_sha"], "branch": contract["launch_target"]["required_branch"], "tasks": contract["launch_target"]["permitted_tasks"], "evidence_digests": digests}
    return {
        "schema_version": "1.0.0", "permit_type": "codex_phase0_launch_permit",
        "launch_id": digest_bytes(canonical_json(identity).encode()), "issued_at": approval["authorized_at"],
        "repository": contract["repository"], "approved_main_sha": approval["approved_main_sha"],
        "canonical_issue": 1, "hosted_controls_issue": 19,
        "branch": contract["launch_target"]["required_branch"], "phase": "Codex Phase 0 only",
        "tasks": contract["launch_target"]["permitted_tasks"],
        "required_first_commit_ack": contract["launch_target"]["required_first_commit_ack"],
        "draft_pull_request_required": True, "merge_authorized": False, "phase1_authorized": False,
        "single_use": True, "stale_on_main_advance": True, "evidence_digests": digests,
        "scope": contract["allowed_scope"], "prohibitions": contract["prohibited_scope"],
        "codex_start_authorized": True,
    }
