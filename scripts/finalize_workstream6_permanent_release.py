from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PREP_CONTRACT = ROOT / "contracts/workstream6-permanent-release-record.json"
BASE_LEDGER = ROOT / "repository/workstream6-defect-closure-ledger.json"
RELEASE_PATH = ROOT / "releases/pre-codex-final-reconciliation-2026-08-06.json"
FINAL_REPORT_PATH = ROOT / "reports/workstream6-final-evidence.md"
FINAL_LEDGER_PATH = ROOT / "repository/workstream6-final-defect-closure-ledger.json"

RELEASE_ID = "PRE-CODEX-FINAL-RECONCILIATION-2026-08-06"
CHECK_NAME = "Validate final pre-Codex canonical handoff and complete release"
PREP_BRANCH = "release/ws616-permanent-release-record"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_path(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def release_failures(record: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(record.get("schema_version") == 2, "release schema version drift")
    require(record.get("release_id") == RELEASE_ID, "release ID drift")
    require(record.get("work_package_id") == "WS6.16", "work package drift")
    require(record.get("record_type") == "permanent_post_merge_release", "record type drift")
    parent = record.get("release_parent_main_sha")
    tested = record.get("tested_merge_reference")
    head = record.get("preparation_head_sha")
    require(isinstance(parent, str) and bool(HEX40.fullmatch(parent)), "parent main SHA invalid")
    require(isinstance(tested, str) and bool(HEX40.fullmatch(tested)), "tested merge ref invalid")
    require(isinstance(head, str) and bool(HEX40.fullmatch(head)), "preparation head SHA invalid")
    require(parent != tested, "parent main SHA and tested merge ref must differ")
    require(isinstance(record.get("preparation_pr_number"), int) and record["preparation_pr_number"] > 0, "preparation PR invalid")
    require(record.get("main_binding_semantics") == "release_parent_main_sha_is_exact_integrated_main_before_release_record_commit", "main binding semantics drift")
    require(record.get("tested_merge_reference_semantics") == "tested_merge_reference_is_exact_successful_WS6.16_preparation_PR_merge_reference", "merge-ref semantics drift")
    final = record.get("final_check", {})
    require(final.get("name") == CHECK_NAME, "final check identity drift")
    for key in ("run_id", "job_id", "artifact_id"):
        require(isinstance(final.get(key), int) and final[key] > 0, f"{key} invalid")
    digest = final.get("artifact_digest_sha256")
    require(isinstance(digest, str) and bool(HEX64.fullmatch(digest)), "artifact digest invalid")
    require(final.get("conclusion") == "success", "final check was not successful")
    require(final.get("evidence_role") == "controlling_current_final_evidence", "current evidence role drift")
    pred = record.get("predecessor_evidence", {})
    require(pred.get("role") == "historical_only", "predecessor evidence role drift")
    require(pred.get("may_satisfy_current_release") is False, "predecessor evidence substitution allowed")
    closure = record.get("defect_closure", {})
    require(closure.get("closed_in_this_release") == ["WS6-BLOCK-006", "WS6-CONSIST-010"], "release closure set drift")
    require(closure.get("manual_remaining") == ["WS6-CONSIST-006"], "manual remaining set drift")
    require(closure.get("blocking_defects_remaining") == [], "blocking defects remain")
    for key in (
        "final_reconciliation_complete",
        "all_blocking_defects_closed",
        "exact_main_sha_bound",
        "tested_merge_reference_bound",
    ):
        require(record.get(key) is True, f"{key} must be true")
    require(record.get("manual_launch_gates_complete") is False, "manual gates claimed complete")
    manual = record.get("manual_gates", {})
    for key, value in manual.items():
        require(value is False, f"manual gate claimed complete: {key}")
    require(record.get("codex_start_authorized") is False, "release must not authorize Codex")
    boundaries = record.get("boundaries", {})
    require(boundaries.get("founder_accountability_preserved") is True, "Founder accountability lost")
    for key, value in boundaries.items():
        if key != "founder_accountability_preserved":
            require(value is False, f"boundary widened: {key}")
    ledger_digest = record.get("final_defect_ledger_sha256")
    require(isinstance(ledger_digest, str) and bool(HEX64.fullmatch(ledger_digest)), "final ledger digest invalid")
    return failures


def build_final_ledger(base: dict[str, Any]) -> dict[str, Any]:
    ledger = copy.deepcopy(base)
    entries = ledger.get("entries", [])
    for item in entries:
        if item.get("id") in {"WS6-BLOCK-006", "WS6-CONSIST-010"}:
            item["overlay_state"] = "release_addressed"
            item["remaining_gate"] = None
            item["closure_owner"] = "WS6.16"
        elif item.get("id") == "WS6-CONSIST-006":
            item["overlay_state"] = "post_merge_manual_remaining"
            item["remaining_gate"] = "historical_branch_cleanup_manual_gate"
    ledger["work_package_id"] = "WS6.16"
    ledger["repository_addressed_count"] = 25
    ledger["release_addressed_count"] = 2
    ledger["manual_unresolved_count"] = 1
    ledger["expected_unresolved_count"] = 1
    ledger["all_blocking_defects_closed"] = True
    ledger["remaining_manual_defects"] = ["WS6-CONSIST-006"]
    ledger["release_closed_defects"] = ["WS6-BLOCK-006", "WS6-CONSIST-010"]
    return ledger


def build_release_record(
    *,
    release_parent_main_sha: str,
    tested_merge_reference: str,
    preparation_pr_number: int,
    preparation_head_sha: str,
    final_check_run_id: int,
    final_check_job_id: int,
    final_check_artifact_id: int,
    final_check_artifact_digest_sha256: str,
    final_ledger_sha256: str,
) -> dict[str, Any]:
    return {
        "schema_version": 2,
        "release_id": RELEASE_ID,
        "work_package_id": "WS6.16",
        "record_type": "permanent_post_merge_release",
        "release_parent_main_sha": release_parent_main_sha,
        "main_binding_semantics": "release_parent_main_sha_is_exact_integrated_main_before_release_record_commit",
        "tested_merge_reference": tested_merge_reference,
        "tested_merge_reference_semantics": "tested_merge_reference_is_exact_successful_WS6.16_preparation_PR_merge_reference",
        "preparation_pr_number": preparation_pr_number,
        "preparation_head_sha": preparation_head_sha,
        "final_check": {
            "name": CHECK_NAME,
            "run_id": final_check_run_id,
            "job_id": final_check_job_id,
            "artifact_id": final_check_artifact_id,
            "artifact_digest_sha256": final_check_artifact_digest_sha256,
            "conclusion": "success",
            "evidence_role": "controlling_current_final_evidence",
        },
        "predecessor_evidence": {
            "role": "historical_only",
            "may_satisfy_current_release": False,
        },
        "final_defect_ledger_path": "repository/workstream6-final-defect-closure-ledger.json",
        "final_defect_ledger_sha256": final_ledger_sha256,
        "defect_closure": {
            "closed_in_this_release": ["WS6-BLOCK-006", "WS6-CONSIST-010"],
            "manual_remaining": ["WS6-CONSIST-006"],
            "blocking_defects_remaining": [],
        },
        "final_reconciliation_complete": True,
        "all_blocking_defects_closed": True,
        "exact_main_sha_bound": True,
        "tested_merge_reference_bound": True,
        "manual_launch_gates_complete": False,
        "manual_gates": {
            "issue_19_complete": False,
            "hosted_controls_verified": False,
            "branch_cleanup_complete": False,
            "clean_macos_environment_available": False,
            "explicit_founder_phase0_approval_received": False,
            "launch_permit_issued": False,
        },
        "codex_start_authorized": False,
        "boundaries": {
            "founder_accountability_preserved": True,
            "phase0_implementation_authorized": False,
            "phase0_merge_authorized": False,
            "phase1_authorized": False,
            "runtime_activation_authorized": False,
            "production_deployment_authorized": False,
            "real_client_data_enabled": False,
            "external_actions_authorized": False,
            "paid_services_authorized": False,
            "oauth_authorized": False,
            "autonomous_merge_authorized": False,
        },
    }


def build_report(record: dict[str, Any], release_sha256: str) -> str:
    final = record["final_check"]
    return "\n".join([
        "# Workstream 6 final evidence",
        "",
        "> [!IMPORTANT]",
        "> This is current final release evidence. Predecessor evidence remains historical only and cannot substitute for the exact bindings below.",
        "",
        f"- Release ID: `{record['release_id']}`.",
        f"- Release-parent integrated main SHA: `{record['release_parent_main_sha']}`.",
        f"- Tested WS6.16 preparation merge reference: `{record['tested_merge_reference']}`.",
        f"- Preparation PR: `#{record['preparation_pr_number']}`.",
        f"- Preparation head SHA: `{record['preparation_head_sha']}`.",
        f"- Final check: `{final['name']}`.",
        f"- Run ID: `{final['run_id']}`.",
        f"- Job ID: `{final['job_id']}`.",
        f"- Artifact ID: `{final['artifact_id']}`.",
        f"- Artifact SHA-256: `{final['artifact_digest_sha256']}`.",
        f"- Final defect ledger SHA-256: `{record['final_defect_ledger_sha256']}`.",
        f"- Permanent release record SHA-256: `{release_sha256}`.",
        "- Closed by this release: `WS6-BLOCK-006`, `WS6-CONSIST-010`.",
        "- Remaining post-merge manual defect: `WS6-CONSIST-006`.",
        "- Issue #19/manual hosted controls, clean macOS, exact-SHA Founder approval and launch permit remain separate gates.",
        "- `codex_start_authorized=false`.",
        "",
    ])


def self_test() -> None:
    base = {
        "schema_version": 1,
        "work_package_id": "WS6.14",
        "entries": [
            {"id": "WS6-BLOCK-006", "overlay_state": "expected_unresolved", "remaining_gate": "x", "closure_owner": "WS6.16"},
            {"id": "WS6-CONSIST-006", "overlay_state": "expected_unresolved", "remaining_gate": "x", "closure_owner": "post_merge_manual"},
            {"id": "WS6-CONSIST-010", "overlay_state": "expected_unresolved", "remaining_gate": "x", "closure_owner": "WS6.16"},
        ],
    }
    ledger = build_final_ledger(base)
    ledger_digest = digest_bytes(canonical(ledger).encode())
    record = build_release_record(
        release_parent_main_sha="1" * 40,
        tested_merge_reference="2" * 40,
        preparation_pr_number=57,
        preparation_head_sha="3" * 40,
        final_check_run_id=1,
        final_check_job_id=2,
        final_check_artifact_id=3,
        final_check_artifact_digest_sha256="4" * 64,
        final_ledger_sha256=ledger_digest,
    )
    if release_failures(record):
        raise SystemExit("valid synthetic release was rejected: " + "; ".join(release_failures(record)))
    mutations = [
        ("release_id", None),
        ("final_reconciliation_complete", False),
        ("all_blocking_defects_closed", False),
        ("exact_main_sha_bound", False),
        ("tested_merge_reference_bound", False),
        ("manual_launch_gates_complete", True),
        ("codex_start_authorized", True),
        ("release_parent_main_sha", "bad"),
        ("tested_merge_reference", "bad"),
        ("preparation_head_sha", "bad"),
    ]
    rejected = 0
    for key, replacement in mutations:
        candidate = copy.deepcopy(record)
        candidate[key] = replacement
        if release_failures(candidate):
            rejected += 1
        else:
            raise SystemExit(f"release mutation not rejected: {key}")
    for key in ("run_id", "job_id", "artifact_id"):
        candidate = copy.deepcopy(record)
        candidate["final_check"][key] = 0
        if release_failures(candidate):
            rejected += 1
        else:
            raise SystemExit(f"release mutation not rejected: final_check.{key}")
    for key, replacement in (
        ("name", "wrong"),
        ("artifact_digest_sha256", "bad"),
        ("conclusion", "failure"),
        ("evidence_role", "historical_only"),
    ):
        candidate = copy.deepcopy(record)
        candidate["final_check"][key] = replacement
        if release_failures(candidate):
            rejected += 1
        else:
            raise SystemExit(f"release mutation not rejected: final_check.{key}")
    candidate = copy.deepcopy(record)
    candidate["predecessor_evidence"]["may_satisfy_current_release"] = True
    assert release_failures(candidate)
    rejected += 1
    candidate = copy.deepcopy(record)
    candidate["defect_closure"]["manual_remaining"] = []
    assert release_failures(candidate)
    rejected += 1
    candidate = copy.deepcopy(record)
    candidate["manual_gates"]["issue_19_complete"] = True
    assert release_failures(candidate)
    rejected += 1
    candidate = copy.deepcopy(record)
    candidate["boundaries"]["phase0_implementation_authorized"] = True
    assert release_failures(candidate)
    rejected += 1
    print(
        f"WS6.16 permanent release finalizer self-test passed: {rejected} release mutations rejected; "
        "current evidence required; predecessor substitution rejected; codex_start_authorized=false."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--release-parent-main-sha")
    parser.add_argument("--tested-merge-reference")
    parser.add_argument("--preparation-pr-number", type=int)
    parser.add_argument("--preparation-head-sha")
    parser.add_argument("--final-check-run-id", type=int)
    parser.add_argument("--final-check-job-id", type=int)
    parser.add_argument("--final-check-artifact-id", type=int)
    parser.add_argument("--final-check-artifact-digest-sha256")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return

    required = [
        args.release_parent_main_sha,
        args.tested_merge_reference,
        args.preparation_pr_number,
        args.preparation_head_sha,
        args.final_check_run_id,
        args.final_check_job_id,
        args.final_check_artifact_id,
        args.final_check_artifact_digest_sha256,
    ]
    if any(value in (None, "") for value in required):
        raise SystemExit("all exact WS6.16 release evidence arguments are required")

    prep = load(PREP_CONTRACT)
    if prep.get("completion", {}).get("release_machinery_prepared") is not True:
        raise SystemExit("WS6.16 release machinery is not prepared")
    if prep.get("completion", {}).get("permanent_release_record_complete") is not False:
        raise SystemExit("WS6.16 preparation contract unexpectedly claims release completion")
    if any(path.exists() for path in (RELEASE_PATH, FINAL_REPORT_PATH, FINAL_LEDGER_PATH)):
        raise SystemExit("final release outputs already exist; refusing overwrite")

    head = _git("rev-parse", "HEAD")
    if head != args.release_parent_main_sha:
        raise SystemExit(f"release parent main SHA mismatch: HEAD={head}")
    branch = _git("branch", "--show-current")
    if branch != PREP_BRANCH:
        raise SystemExit(f"finalization must run on {PREP_BRANCH}, got {branch!r}")
    if _git("status", "--porcelain"):
        raise SystemExit("working tree must be clean before finalization")

    base_ledger = load(BASE_LEDGER)
    unresolved = {
        item.get("id")
        for item in base_ledger.get("entries", [])
        if item.get("overlay_state") == "expected_unresolved"
    }
    if unresolved != {"WS6-BLOCK-006", "WS6-CONSIST-006", "WS6-CONSIST-010"}:
        raise SystemExit(f"unexpected pre-release defect set: {sorted(unresolved)}")

    final_ledger = build_final_ledger(base_ledger)
    final_ledger_text = canonical(final_ledger)
    ledger_digest = digest_bytes(final_ledger_text.encode())
    record = build_release_record(
        release_parent_main_sha=args.release_parent_main_sha,
        tested_merge_reference=args.tested_merge_reference,
        preparation_pr_number=args.preparation_pr_number,
        preparation_head_sha=args.preparation_head_sha,
        final_check_run_id=args.final_check_run_id,
        final_check_job_id=args.final_check_job_id,
        final_check_artifact_id=args.final_check_artifact_id,
        final_check_artifact_digest_sha256=args.final_check_artifact_digest_sha256,
        final_ledger_sha256=ledger_digest,
    )
    failures = release_failures(record)
    if failures:
        raise SystemExit("release candidate invalid:\n- " + "\n- ".join(failures))

    FINAL_LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    FINAL_LEDGER_PATH.write_text(final_ledger_text, encoding="utf-8")
    release_text = canonical(record)
    RELEASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    RELEASE_PATH.write_text(release_text, encoding="utf-8")
    release_digest = digest_bytes(release_text.encode())
    FINAL_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    FINAL_REPORT_PATH.write_text(build_report(record, release_digest), encoding="utf-8")
    print(
        f"Finalized WS6.16 release candidate: parent_main={args.release_parent_main_sha}, "
        f"tested_merge_ref={args.tested_merge_reference}, run={args.final_check_run_id}, "
        f"job={args.final_check_job_id}, artifact={args.final_check_artifact_id}, "
        f"digest={args.final_check_artifact_digest_sha256}, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
