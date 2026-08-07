from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "configs/workstream6-cross-authority-consistency-gate.yaml"
OUT = ROOT / "contracts/workstream6-cross-authority-consistency-gate.json"
LEDGER = ROOT / "repository/workstream6-defect-closure-ledger.json"
DOC = ROOT / "docs/66-WS6-14-CROSS-AUTHORITY-CONSISTENCY-GATE.md"
REPORT = ROOT / "reports/workstream6-cross-authority-consistency-evidence.md"
DEFECT_FILES = [
    ROOT / "configs/workstream6-defects-blocking.yaml",
    ROOT / "configs/workstream6-defects-consistency.yaml",
    ROOT / "configs/workstream6-defects-quality.yaml",
    ROOT / "configs/workstream6-defects-codexprep.yaml",
]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canon(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def build_records() -> tuple[dict[str, Any], dict[str, Any], str, str]:
    source = load(SRC)
    defects: list[dict[str, Any]] = []
    for path in DEFECT_FILES:
        value = load(path)
        if not isinstance(value, list):
            raise ValueError(f"{path} must contain array")
        for item in value:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                raise ValueError("invalid defect")
            defects.append(
                {
                    "id": item["id"],
                    "baseline_status": item.get("status"),
                    "target_work_package": item.get("target_work_package"),
                    "source": path.relative_to(ROOT).as_posix(),
                }
            )
    ids = [item["id"] for item in defects]
    if len(ids) != 28 or len(ids) != len(set(ids)):
        raise ValueError("expected 28 unique baseline defects")
    closure = source["defect_closure_map"]
    unresolved = source["expected_unresolved_defects"]
    if set(ids) != set(closure) | set(unresolved):
        raise ValueError("closure overlay does not cover baseline defect set exactly")

    entries: list[dict[str, Any]] = []
    for item in sorted(defects, key=lambda record: record["id"]):
        defect_id = item["id"]
        if defect_id in closure:
            entries.append(
                {
                    **item,
                    "overlay_state": "repository_addressed",
                    "closure_owner": closure[defect_id],
                    "remaining_gate": None,
                }
            )
        else:
            record = unresolved[defect_id]
            entries.append(
                {
                    **item,
                    "overlay_state": "expected_unresolved",
                    "closure_owner": record["owner"],
                    "remaining_gate": record["reason"],
                }
            )

    ledger = {
        "schema_version": 1,
        "work_package_id": "WS6.14",
        "source_defect_files": [path.relative_to(ROOT).as_posix() for path in DEFECT_FILES],
        "baseline_status_fields_are_historical": True,
        "defect_count": len(entries),
        "repository_addressed_count": sum(item["overlay_state"] == "repository_addressed" for item in entries),
        "expected_unresolved_count": sum(item["overlay_state"] == "expected_unresolved" for item in entries),
        "entries": entries,
    }
    contract = {
        **source,
        "generated_from": SRC.relative_to(ROOT).as_posix(),
        "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
        "defect_ledger": "repository/workstream6-defect-closure-ledger.json",
        "defect_count": ledger["defect_count"],
        "repository_addressed_count": ledger["repository_addressed_count"],
        "expected_unresolved_count": ledger["expected_unresolved_count"],
        "authority_domain_count": len(source["authority_domains"]),
    }
    doc = "\n".join(
        [
            "# WS6.14 — Cross-authority consistency gate",
            "",
            "> [!CAUTION]",
            "> **CONSISTENCY GATE, NOT LAUNCH AUTHORIZATION.** This package reconciles repository authority. It does not activate the final workflow, create the permanent release, satisfy manual gates, issue a permit, or authorize Codex.",
            "",
            f"- Integrated `main`: `{source['main_integration']['integrated_main_sha']}` through `{source['main_integration']['integrated_through']}`.",
            f"- Earliest unintegrated package: `{source['main_integration']['earliest_unintegrated']}`.",
            f"- Authority domains checked: `{len(source['authority_domains'])}`.",
            f"- Baseline defects: `{ledger['defect_count']}`; repository-addressed: `{ledger['repository_addressed_count']}`; expected unresolved: `{ledger['expected_unresolved_count']}`.",
            "- Historical WS6.5/WS6.6 fingerprint/status fields remain package-time snapshots; current status comes from the WS6.3 successor current-status contract and canonical authority registry.",
            "- `WS6-BLOCK-006`, `WS6-CONSIST-006` and `WS6-CONSIST-010` remain unresolved by design.",
            "- WS6.15 must activate the reserved final workflow; WS6.16 must create the permanent release; hosted/manual evidence remains independent.",
            "- `codex_start_authorized=false`.",
            "",
            "## Domains",
            "",
            *[f"- `{item['id']}` — {item['assertion']}." for item in source["authority_domains"]],
            "",
            "## Defect closure overlay",
            "",
            *[f"- `{item['id']}` — `{item['overlay_state']}`; owner `{item['closure_owner']}`." for item in entries],
            "",
            "## Next gate",
            "",
            "`WS6.15` is the next permitted chat-first package. No merge, IMP-P0 implementation, runtime activation or external action is authorized.",
        ]
    )
    report = "\n".join(
        [
            "# WS6.14 cross-authority consistency evidence",
            "",
            "<!-- Generated by scripts/build_workstream6_cross_authority_consistency_gate.py. -->",
            "",
            f"- Predecessor head: `{source['predecessor']['head_sha']}`.",
            f"- Integrated main: `{source['main_integration']['integrated_main_sha']}` through `WS6.7`.",
            f"- Authority domains: `{len(source['authority_domains'])}`.",
            f"- Defects: `{ledger['defect_count']}` total, `{ledger['repository_addressed_count']}` repository-addressed, `{ledger['expected_unresolved_count']}` expected unresolved.",
            "- Final workflow active: `false`.",
            "- Permanent final release complete: `false`.",
            "- Manual launch gates complete: `false`.",
            "- `codex_start_authorized=false`.",
            "- Next permitted work package: `WS6.15`.",
        ]
    )
    return contract, ledger, doc, report


def main() -> None:
    contract, ledger, doc, report = build_records()
    for path, value in ((OUT, canon(contract)), (LEDGER, canon(ledger)), (DOC, doc), (REPORT, report)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")
    print(
        f"Built WS6.14 cross-authority gate: domains={contract['authority_domain_count']}, "
        f"defects={contract['defect_count']}, addressed={contract['repository_addressed_count']}, "
        f"unresolved={contract['expected_unresolved_count']}, next=WS6.15, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
