from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINAL_RELEASE_PATH = ROOT / "releases" / "pre-codex-final-reconciliation-2026-08-06.json"


def _failures(record: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if record.get("release_id") != "PRE-CODEX-FINAL-RECONCILIATION-2026-08-06":
        failures.append("final Workstream 6 release ID is missing")
    if record.get("final_reconciliation_complete") is not True:
        failures.append("final Workstream 6 reconciliation is incomplete")
    if record.get("all_blocking_defects_closed") is not True:
        failures.append("blocking Workstream 6 defects remain open")
    if record.get("exact_main_sha_bound") is not True:
        failures.append("final release is not bound to exact main")
    if record.get("tested_merge_reference_bound") is not True:
        failures.append("final release is not bound to a tested merge reference")
    if record.get("codex_start_authorized") is not False:
        failures.append("the final release must not itself authorize Codex")
    return failures


def _self_test() -> None:
    incomplete = {
        "release_id": "PRE-CODEX-FINAL-RECONCILIATION-2026-08-06",
        "final_reconciliation_complete": False,
        "all_blocking_defects_closed": False,
        "exact_main_sha_bound": False,
        "tested_merge_reference_bound": False,
        "codex_start_authorized": False,
    }
    if not _failures(incomplete):
        raise SystemExit("incomplete final reconciliation was not rejected")
    complete = {
        "release_id": "PRE-CODEX-FINAL-RECONCILIATION-2026-08-06",
        "final_reconciliation_complete": True,
        "all_blocking_defects_closed": True,
        "exact_main_sha_bound": True,
        "tested_merge_reference_bound": True,
        "codex_start_authorized": False,
    }
    if _failures(complete):
        raise SystemExit("valid synthetic final reconciliation was rejected")
    print(
        "Final Workstream 6 gate self-test passed: incomplete evidence rejected, "
        "valid synthetic evidence accepted, Codex authorization not inferred."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        return
    if not FINAL_RELEASE_PATH.is_file():
        raise SystemExit(
            "Final Workstream 6 reconciliation is not available; Codex must not start."
        )
    record = json.loads(FINAL_RELEASE_PATH.read_text(encoding="utf-8"))
    failures = _failures(record)
    if failures:
        raise SystemExit("Final Workstream 6 gate failed:\n- " + "\n- ".join(failures))
    print(
        "Final Workstream 6 reconciliation gate passed; this result does not replace "
        "hosted-control, clean-macOS, Founder-approval or launch-permit validation."
    )


if __name__ == "__main__":
    main()
