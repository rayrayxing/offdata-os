from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "configs" / "workstream4-readiness.yaml"
CONTRACT_PATH = ROOT / "contracts" / "workstream4-readiness.json"
RELEASE_PATH = ROOT / "releases" / "pre-codex-chat-first-2026-08-06.json"
PRE_CODEX_PATH = ROOT / "contracts" / "pre-codex-readiness.json"

EXPECTED_WORKFLOWS = (
    ".github/workflows/contracts.yml",
    ".github/workflows/hermes-compatibility.yml",
    ".github/workflows/northstar-integration-blueprint.yml",
    ".github/workflows/initial-operating-controls.yml",
    ".github/workflows/first-codex-issue.yml",
    ".github/workflows/pcr09-final-evidence.yml",
    ".github/workflows/pcr10-pre-codex-readiness.yml",
    ".github/workflows/workstream4-readiness.yml",
)
ACTION_KEYS = {
    "actions/checkout": "checkout",
    "actions/setup-python": "setup_python",
    "actions/upload-artifact": "upload_artifact",
}
USES_RE = re.compile(r"uses:\s*(actions/(?:checkout|setup-python|upload-artifact))@([0-9a-f]{40})")


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _workflow_inventory(source: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    pins = source["node24_action_pins"]
    inventory: list[dict[str, Any]] = []
    failures: list[str] = []
    for relative in EXPECTED_WORKFLOWS:
        path = ROOT / relative
        if not path.is_file():
            failures.append(f"missing workflow: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        uses = [
            {"repository": repo, "sha": sha}
            for repo, sha in USES_RE.findall(text)
        ]
        for use in uses:
            key = ACTION_KEYS[use["repository"]]
            expected = pins[key]["sha"]
            if use["sha"] != expected:
                failures.append(
                    f"{relative} uses {use['repository']}@{use['sha']} instead of {expected}"
                )
        inventory.append(
            {
                "path": relative,
                "sha256": _sha256_path(path),
                "bytes": path.stat().st_size,
                "official_action_uses": uses,
            }
        )
    return inventory, failures


def build_records() -> tuple[dict[str, Any], dict[str, Any]]:
    source = _load_yaml(SOURCE_PATH)
    pre_codex = _load_json(PRE_CODEX_PATH)
    workflows, workflow_failures = _workflow_inventory(source)
    status_check = source["required_status_check"]
    pcr10_path = ROOT / status_check["workflow_file"]
    pcr10_text = pcr10_path.read_text(encoding="utf-8") if pcr10_path.is_file() else ""

    required_paths = (
        SOURCE_PATH,
        ROOT / "scripts" / "build_workstream4_readiness.py",
        ROOT / "scripts" / "validate_workstream4_readiness.py",
        ROOT / "scripts" / "doctor_pre_codex_macos.py",
        ROOT / "schemas" / "workstream4-readiness.schema.json",
        ROOT / "docs" / "50-WORKSTREAM-4-HOSTED-CONTROLS-EVIDENCE-AND-ENVIRONMENT-READINESS.md",
        ROOT / "reports" / "workstream4-readiness-evidence.md",
        ROOT / ".github" / "workflows" / "workstream4-readiness.yml",
    )
    checks = {
        "pre_codex_contract_is_integrated": (
            pre_codex.get("status") == "chat_first_complete_integrated"
            and pre_codex.get("readiness_snapshot", {}).get("release_integration_complete") is True
            and pre_codex.get("readiness_snapshot", {}).get("codex_start_authorized") is False
        ),
        "all_expected_workflows_present": len(workflows) == len(EXPECTED_WORKFLOWS),
        "all_official_action_uses_exactly_pinned": not workflow_failures,
        "required_final_status_check_named": status_check["job_name"] in pcr10_text,
        "required_files_present": all(path.is_file() for path in required_paths),
        "release_manifest_path_available": RELEASE_PATH.parent.is_dir(),
        "manual_hosted_attestations_remain_unverified": all(
            value is False
            for value in source["hosted_controls_manual_attestations"].values()
        ),
        "clean_macos_attestation_remains_unverified": (
            source["clean_macos_environment"]["clean_macos_environment_verified"] is False
            and source["clean_macos_environment"]["machine_report_attached"] is False
            and source["clean_macos_environment"]["founder_environment_attestation_received"] is False
        ),
        "founder_approval_remains_unverified": (
            source["readiness"]["explicit_founder_phase_0_approval_received"] is False
        ),
        "codex_start_remains_unauthorized": (
            source["readiness"]["codex_start_authorized"] is False
            and pre_codex.get("readiness_snapshot", {}).get("codex_start_authorized") is False
        ),
    }

    release = {
        "schema_version": "1.0.0",
        "release_id": source["release_evidence"]["release_id"],
        "release_class": "permanent_repository_evidence",
        "repository": source["repository"],
        "canonical_branch": source["canonical_branch"],
        "integrated_main_sha": source["release_evidence"]["integrated_main_sha"],
        "tested_merge_reference": source["release_evidence"]["tested_merge_reference"],
        "integration_pr": source["release_evidence"]["integration_pr"],
        "validation": {
            key: source["release_evidence"][key]
            for key in (
                "pcr10_run_id",
                "pcr10_job_id",
                "pcr10_artifact_id",
                "pcr10_artifact_sha256",
                "complete_release_run_id",
                "complete_release_artifact_id",
                "complete_release_artifact_sha256",
                "issue_1_body_sha256",
                "runtime_tests_passed",
                "coverage_percent",
                "executable_test_nodes",
                "semantic_tests",
                "reference_edges",
                "unresolved_references",
            )
        },
        "node24_action_pins": source["node24_action_pins"],
        "required_status_check": source["required_status_check"],
        "workflow_inventory": workflows,
        "manual_gates": {
            "hosted_controls_verified": False,
            "clean_macos_environment_verified": False,
            "explicit_founder_phase_0_approval_received": False,
        },
        "authorization": {
            "codex_start_authorized": False,
            "next_permitted_phase_after_all_gates": "Codex Phase 0 only",
        },
        "rollback": {
            "repository_changes": "reviewed revert of the Workstream 4 merge commit",
            "hosted_settings": "restore the prior documented branch-protection settings",
            "environment": "delete only the clean synthetic development clone and generated doctor report",
        },
    }
    release_text = _canonical_json(release)

    contract = {
        **source,
        "generated_from": str(SOURCE_PATH.relative_to(ROOT)),
        "workflow_inventory": workflows,
        "workflow_pin_failures": workflow_failures,
        "readiness_snapshot": {
            "checks": checks,
            "repository_side_prerequisites_passed": all(checks.values()),
            "hosted_controls_verified": False,
            "clean_macos_environment_verified": False,
            "explicit_founder_phase_0_approval_received": False,
            "branch_cleanup_complete": source["readiness"]["branch_cleanup_complete"],
            "workstream_4_complete": False,
            "codex_start_authorized": False,
            "next_permitted_phase_after_all_gates": "Codex Phase 0 only",
        },
        "durable_release": {
            "path": str(RELEASE_PATH.relative_to(ROOT)),
            "sha256": _sha256_bytes(release_text.encode("utf-8")),
            "release_id": release["release_id"],
        },
    }
    return contract, release


def main() -> None:
    contract, release = build_records()
    CONTRACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RELEASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONTRACT_PATH.write_text(_canonical_json(contract), encoding="utf-8")
    RELEASE_PATH.write_text(_canonical_json(release), encoding="utf-8")
    snapshot = contract["readiness_snapshot"]
    print(
        "Built Workstream 4 readiness: "
        f"{len(contract['workflow_inventory'])} workflows, "
        f"{len(contract['workflow_pin_failures'])} pin failures, "
        f"repository_side_prerequisites_passed={str(snapshot['repository_side_prerequisites_passed']).lower()}, "
        "hosted_controls_verified=false, clean_macos_environment_verified=false, "
        "codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
