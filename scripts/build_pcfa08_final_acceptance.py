from __future__ import annotations

import json

from pcfa08_final_acceptance import RECORD, REPORT, build_records


def main() -> None:
    record, report = build_records()
    RECORD.write_text(
        json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    REPORT.write_text(report, encoding="utf-8")
    summary = record["summary"]
    print(
        "Built PCFA-08 final pre-Codex cross-authority acceptance: "
        f"authorities={summary['authority_input_count']}, invariants={summary['cross_authority_invariant_count']}, "
        f"manual_gates={summary['manual_launch_gate_count']}, cleanup_branches={summary['planned_branch_deletion_count']}, "
        "repository_acceptance=true, manual_launch_evidence=false, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
