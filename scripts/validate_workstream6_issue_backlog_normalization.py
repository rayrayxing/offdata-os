from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from build_workstream6_issue_backlog_normalization import build_records

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "workstream6-issue-backlog-normalization.json"
SCHEMA = ROOT / "schemas" / "workstream6-issue-backlog-normalization.schema.json"
REPORT = ROOT / "reports" / "workstream6-issue-backlog-normalization-evidence.md"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def _canonical(value: object) -> str:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ) + "\n"


def _failures(value: dict[str, Any], outputs: dict[str, str]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(value.get("work_package_id") == "WS6.8", "work package")
    require(
        value.get("base_main_sha")
        == "cb2bffe74e62804250ac36168c4206cb8b9d021a",
        "base main",
    )
    require(value.get("status") == "issue_and_backlog_normalized", "status")
    require(
        value.get("defect_ids")
        == ["WS6-CONSIST-005", "WS6-CODEXPREP-007"],
        "defect set",
    )
    policy = value.get("live_issue_policy", {})
    require(policy.get("only_actionable_implementation_issue") == 1, "issue #1")
    require(policy.get("only_manual_prelaunch_gate_issue") == 19, "issue #19")
    require(policy.get("duplicate_issue") == 2, "issue #2")
    issues = policy.get("normalized_issues", [])
    require([item.get("number") for item in issues] == [3, 4, 5], "issue set")
    for issue in issues:
        body = outputs.get(issue.get("body_path", ""), "")
        for token in (
            "CLOSED AS NOT PLANNED",
            "Classification: `superseded_non_actionable`",
            "Issue #1 is the only actionable implementation assignment",
            "Issue #19 is the only manual pre-launch gate",
            "codex_start_authorized=false",
        ):
            require(token in body, f"issue body token: {token}")

    phases = value.get("future_phases", [])
    expected_ids = [f"IMP-P{index}" for index in range(1, 13)]
    require([phase.get("id") for phase in phases] == expected_ids, "phase sequence")
    pack_path = f"{value.get('pack_directory')}/future-implementation-issues.md"
    pack = outputs.get(pack_path, "")
    for index, phase in enumerate(phases, start=1):
        expected_dependency = "IMP-P0" if index == 1 else f"IMP-P{index - 1}"
        require(phase.get("depends_on") == [expected_dependency], "phase dependency")
        require(phase.get("draft_only") is True, "draft only")
        require(phase.get("live_issue_created") is False, "live issue")
        require(phase.get("implementation_authorized") is False, "authorization")
        require(bool(phase.get("tasks")), "phase tasks")
        require(bool(phase.get("gate")), "phase gate")
        require(
            f"## [BLOCKED DRAFT] {phase['id']} — {phase['title']}" in pack,
            "phase draft section",
        )
    for token in (
        "NOT AUTHORISED TO START",
        "Issue #1 remains the only actionable implementation assignment",
        "Issue #19 remains the only manual pre-launch gate",
        "Live GitHub issue created: `false`",
        "Implementation authorized: `false`",
        "codex_start_authorized=false",
    ):
        require(token in pack, f"pack token: {token}")

    require(value.get("future_issue_count") == 12, "future issue count")
    require(value.get("normalized_live_issue_count") == 3, "normalized issue count")
    require(len(value.get("generated_files", [])) == 6, "generated file count")
    require(
        value.get("closed_defects")
        == ["WS6-CONSIST-005", "WS6-CODEXPREP-007"],
        "closed defects",
    )
    require(
        value.get("remaining_blocking_defects") == ["WS6-BLOCK-006"],
        "remaining blocker",
    )
    completion = value.get("completion", {})
    for key in (
        "all_required_prior_components_pass",
        "ws68_complete",
        "live_issues_3_to_5_normalized",
        "future_issue_pack_complete",
        "only_issue_1_actionable",
        "only_issue_19_manual_gate",
    ):
        require(completion.get(key) is True, key)
    require(completion.get("final_reconciliation_complete") is False, "final")
    require(completion.get("all_blocking_defects_closed") is False, "blockers")
    require(completion.get("next_permitted_work_package") == "WS6.9", "next")
    boundaries = value.get("boundaries", {})
    require(boundaries.get("founder_accountability_preserved") is True, "accountability")
    for key, item in boundaries.items():
        if key != "founder_accountability_preserved":
            require(item is False, key)
    return failures


def main() -> None:
    contract = _load(CONTRACT)
    schema = _load(SCHEMA)
    errors = list(Draft202012Validator(schema).iter_errors(contract))
    if errors:
        raise SystemExit(
            "WS6.8 schema validation failed: "
            + "; ".join(error.message for error in errors)
        )
    expected, outputs, report = build_records()
    if _canonical(contract) != _canonical(expected):
        raise SystemExit("WS6.8 contract is not deterministic")
    for relative, content in outputs.items():
        if (ROOT / relative).read_text(encoding="utf-8") != content:
            raise SystemExit(f"WS6.8 generated file is not deterministic: {relative}")
    if REPORT.read_text(encoding="utf-8") != report:
        raise SystemExit("WS6.8 report is not deterministic")
    failures = _failures(contract, outputs)
    if failures:
        raise SystemExit("WS6.8 semantic validation failed: " + "; ".join(failures))

    mutations: list[tuple[tuple[str, ...], Any]] = [
        (("live_issue_policy", "only_actionable_implementation_issue"), 4),
        (("live_issue_policy", "only_manual_prelaunch_gate_issue"), 3),
        (("closed_defects",), []),
        (("remaining_blocking_defects",), []),
        (("future_issue_count",), 11),
        (("completion", "ws68_complete"), False),
        (("completion", "next_permitted_work_package"), "WS6.10"),
        (("boundaries", "codex_start_authorized"), True),
        (("boundaries", "phase1_authorized"), True),
    ]
    rejected = 0
    for path, replacement in mutations:
        mutated = copy.deepcopy(contract)
        node: Any = mutated
        for part in path[:-1]:
            node = node[part]
        node[path[-1]] = replacement
        if _failures(mutated, outputs):
            rejected += 1
        else:
            raise SystemExit(f"WS6.8 mutation not rejected: {'.'.join(path)}")

    for index in range(12):
        mutated = copy.deepcopy(contract)
        mutated["future_phases"][index]["implementation_authorized"] = True
        if _failures(mutated, outputs):
            rejected += 1
        else:
            raise SystemExit("WS6.8 phase authorization mutation not rejected")

    print(
        "WS6.8 issue and backlog normalization passed: "
        f"{rejected} mutations rejected, live_issues=3, blocked_drafts=12, "
        "next=WS6.9, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
