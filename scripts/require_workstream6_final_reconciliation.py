from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from finalize_workstream6_permanent_release import (
    FINAL_LEDGER_PATH,
    FINAL_REPORT_PATH,
    RELEASE_ID,
    RELEASE_PATH,
    release_failures,
    self_test as finalizer_self_test,
)

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _self_test() -> None:
    finalizer_self_test()
    incomplete = {
        "schema_version": 2,
        "release_id": RELEASE_ID,
        "work_package_id": "WS6.16",
        "record_type": "permanent_post_merge_release",
        "final_reconciliation_complete": False,
        "all_blocking_defects_closed": False,
        "exact_main_sha_bound": False,
        "tested_merge_reference_bound": False,
        "manual_launch_gates_complete": False,
        "codex_start_authorized": False,
    }
    if not release_failures(incomplete):
        raise SystemExit("incomplete final reconciliation was not rejected")
    print(
        "Final Workstream 6 gate self-test passed: incomplete evidence rejected, "
        "synthetic exact release accepted only with current evidence, Codex authorization not inferred."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--expected-parent-main-sha")
    parser.add_argument("--expected-tested-merge-reference")
    parser.add_argument("--expected-artifact-digest")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        return

    if not RELEASE_PATH.is_file():
        raise SystemExit(
            "Final Workstream 6 reconciliation is not available; Codex must not start."
        )
    if not FINAL_LEDGER_PATH.is_file():
        raise SystemExit("Final Workstream 6 defect ledger is missing")
    if not FINAL_REPORT_PATH.is_file():
        raise SystemExit("Final Workstream 6 evidence report is missing")

    record = _load(RELEASE_PATH)
    failures = release_failures(record)
    if failures:
        raise SystemExit("Final Workstream 6 gate failed:\n- " + "\n- ".join(failures))

    parent = record["release_parent_main_sha"]
    tested = record["tested_merge_reference"]
    artifact_digest = record["final_check"]["artifact_digest_sha256"]

    if args.expected_parent_main_sha and parent != args.expected_parent_main_sha:
        raise SystemExit("final release parent-main SHA does not match expected value")
    if args.expected_tested_merge_reference and tested != args.expected_tested_merge_reference:
        raise SystemExit("final release tested merge reference does not match expected value")
    if args.expected_artifact_digest and artifact_digest != args.expected_artifact_digest:
        raise SystemExit("final release artifact digest does not match expected value")

    ledger_digest = _digest(FINAL_LEDGER_PATH)
    if ledger_digest != record["final_defect_ledger_sha256"]:
        raise SystemExit("final defect ledger digest does not match release record")
    ledger = _load(FINAL_LEDGER_PATH)
    if ledger.get("all_blocking_defects_closed") is not True:
        raise SystemExit("final defect ledger still has blocking defects")
    if ledger.get("remaining_manual_defects") != ["WS6-CONSIST-006"]:
        raise SystemExit("final defect ledger manual remainder drifted")

    head = _git("rev-parse", "HEAD")
    if parent == head:
        raise SystemExit(
            "permanent release must be committed after the exact integrated parent-main SHA"
        )
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", parent, head],
        cwd=ROOT,
        check=False,
    )
    if ancestor.returncode != 0:
        raise SystemExit(
            "release_parent_main_sha is not an ancestor of the current release commit/ref"
        )

    report = FINAL_REPORT_PATH.read_text(encoding="utf-8")
    release_digest = _digest(RELEASE_PATH)
    for token in (
        parent,
        tested,
        str(record["final_check"]["run_id"]),
        str(record["final_check"]["job_id"]),
        str(record["final_check"]["artifact_id"]),
        artifact_digest,
        release_digest,
        "WS6-CONSIST-006",
        "codex_start_authorized=false",
    ):
        if token not in report:
            raise SystemExit(f"final evidence report missing token: {token}")

    print(
        "Final Workstream 6 reconciliation gate passed with exact parent-main, tested merge-ref, "
        "run, job, artifact, artifact digest and final-ledger bindings; this result does not replace "
        "issue #19, clean-macOS, Founder-approval or launch-permit validation."
    )


if __name__ == "__main__":
    main()
