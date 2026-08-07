from __future__ import annotations

import copy
import fnmatch
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

from build_workstream6_canonical_authority import build_records

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "repository/canonical-authority-registry.json"
SCHEMA_PATH = ROOT / "schemas/canonical-authority-registry.schema.json"
REPORT_PATH = ROOT / "reports/workstream6-canonical-authority-evidence.md"
STATUS_FILES = (
    "README.md",
    "docs/00-START-HERE.md",
    "docs/14-CODEX-KICKOFF.md",
    "docs/19-PHASE-0-VALIDATION-ADDENDUM.md",
    "docs/20-DEVELOPMENT-STATUS.md",
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def exact_map(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item["path"]: item
        for item in registry.get("exact_records", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }


def classify(registry: dict[str, Any], relative: str) -> dict[str, Any] | None:
    exact = exact_map(registry).get(relative)
    if exact is not None:
        return exact
    matches = [
        rule
        for rule in registry.get("classification_rules", [])
        if isinstance(rule, dict)
        and fnmatch.fnmatchcase(relative, str(rule.get("pattern", "")))
    ]
    if not matches:
        return None
    priority = max(int(item.get("priority", -1)) for item in matches)
    winners = [item for item in matches if int(item.get("priority", -1)) == priority]
    if len({str(item.get("classification")) for item in winners}) != 1:
        return {"classification": "__CONFLICT__"}
    return winners[0]


def scanned_paths(registry: dict[str, Any]) -> list[str]:
    paths: set[str] = set()
    for root_name in registry.get("scan_roots", []):
        root = ROOT / str(root_name)
        if root.exists():
            for path in root.rglob("*"):
                if path.is_file():
                    paths.add(path.relative_to(ROOT).as_posix())
    return sorted(paths)


def failures(registry: dict[str, Any]) -> list[str]:
    out: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            out.append(message)

    require(registry.get("work_package_id") == "WS6.4", "work package drift")
    require(
        registry.get("base_main_sha") == "be83de22a1178ad9fb5c814d993a0ade8a54f53c",
        "historical WS6.4 base drift",
    )
    exact = registry.get("exact_records", [])
    rules = registry.get("classification_rules", [])
    external = registry.get("external_records", [])
    require(isinstance(exact, list) and len(exact) == 43, "exact record count drift")
    require(isinstance(rules, list) and len(rules) == 11, "rule count drift")
    require(isinstance(external, list) and len(external) == 3, "external count drift")

    paths = [item.get("path") for item in exact if isinstance(item, dict)]
    require(len(paths) == len(set(paths)), "duplicate exact authority path")
    rule_ids = [item.get("id") for item in rules if isinstance(item, dict)]
    rule_patterns = [item.get("pattern") for item in rules if isinstance(item, dict)]
    require(len(rule_ids) == len(set(rule_ids)), "duplicate rule id")
    require(len(rule_patterns) == len(set(rule_patterns)), "duplicate rule pattern")

    by_path = exact_map(registry)
    required_classes = {
        "repository/canonical-authority-registry.json": "current_authority_registry",
        "handoff/codex-phase0-handoff.json": "current_machine_handoff",
        "handoff/codex-phase0-issue-final.md": "current_issue_body",
        "contracts/codex-phase0-launch-control.json": "current_launch_contract",
        "contracts/workstream6-phase-namespace.json": "current_phase_namespace",
        ".github/workflows/workstream6-final-pre-codex.yml": "current_required_workflow",
        "contracts/workstream6-required-workflow-identity.json": "current_required_workflow_identity",
    }
    for path, expected in required_classes.items():
        require(by_path.get(path, {}).get("classification") == expected, f"classification drift: {path}")

    for path in paths:
        if isinstance(path, str):
            require((ROOT / path).is_file(), f"missing exact authority path: {path}")

    for relative in scanned_paths(registry):
        item = classify(registry, relative)
        require(item is not None, f"unclassified governed file: {relative}")
        if item is not None:
            require(item.get("classification") != "__CONFLICT__", f"classification conflict: {relative}")

    counts = Counter(
        str(item.get("classification"))
        for item in [*exact, *external]
        if isinstance(item, dict)
    )
    for classification, expected in registry.get("uniqueness_constraints", {}).items():
        require(counts[str(classification)] == expected, f"uniqueness drift: {classification}")

    issue_bodies = sorted((ROOT / "handoff").glob("codex-phase0-issue*.md"))
    current_issues = [
        path
        for path in issue_bodies
        if (classify(registry, path.relative_to(ROOT).as_posix()) or {}).get("classification")
        == "current_issue_body"
    ]
    require(len(current_issues) == 1, "current issue body not unique")
    handoffs = sorted((ROOT / "handoff").glob("codex-phase0-handoff*.json"))
    current_handoffs = [
        path
        for path in handoffs
        if (classify(registry, path.relative_to(ROOT).as_posix()) or {}).get("classification")
        == "current_machine_handoff"
    ]
    require(len(current_handoffs) == 1, "current machine handoff not unique")

    ext = {item.get("number"): item for item in external if isinstance(item, dict)}
    require(ext.get(1, {}).get("classification") == "current_actionable_assignment", "issue #1 role drift")
    require(ext.get(1, {}).get("expected_state") == "open", "issue #1 state drift")
    require(ext.get(19, {}).get("classification") == "current_manual_gate", "issue #19 role drift")
    require(ext.get(19, {}).get("expected_state") == "open", "issue #19 state drift")
    require(ext.get(2, {}).get("classification") == "superseded_duplicate", "issue #2 role drift")
    require(ext.get(2, {}).get("state_reason") == "duplicate", "issue #2 reason drift")

    status = registry.get("canonical_status_phrase")
    require(isinstance(status, str) and "WS6.7" in status, "canonical integrated WS6.7 status missing")
    require(isinstance(status, str) and "later WS6 work remains unintegrated" in status, "unintegrated successor boundary missing")
    if isinstance(status, str):
        for relative in STATUS_FILES:
            text = (ROOT / relative).read_text(encoding="utf-8")
            require(status in text, f"canonical status missing: {relative}")
            require("codex_start_authorized=false" in text, f"fail-closed status missing: {relative}")
            require("repository/canonical-authority-registry.json" in text, f"registry reference missing: {relative}")

    require(registry.get("closed_defects") == ["WS6-CONSIST-001", "WS6-CONSIST-007"], "historical closure set drift")
    require(registry.get("remaining_blocking_defects") == ["WS6-BLOCK-006"], "remaining blocker drift")
    completion = registry.get("completion", {})
    for key in (
        "all_required_prior_components_pass",
        "ws64_complete",
        "all_current_read_order_items_classified",
        "all_evidence_roots_classified",
    ):
        require(completion.get(key) is True, f"completion false: {key}")
    require(completion.get("final_reconciliation_complete") is False, "final reconciliation claimed early")
    require(completion.get("all_blocking_defects_closed") is False, "all blockers claimed closed early")
    require(completion.get("next_permitted_work_package") == "WS6.7", "historical WS6.4 next-package provenance drift")

    boundaries = registry.get("boundaries", {})
    require(boundaries.get("founder_accountability_preserved") is True, "Founder accountability lost")
    for key, value in boundaries.items():
        if key != "founder_accountability_preserved":
            require(value is False, f"boundary widened: {key}")
    return out


def main() -> None:
    registry = load(REGISTRY_PATH)
    schema = load(SCHEMA_PATH)
    errors = list(Draft202012Validator(schema).iter_errors(registry))
    if errors:
        raise SystemExit("WS6.4 schema validation failed: " + "; ".join(e.message for e in errors))
    expected, output, report = build_records()
    if registry != expected or REGISTRY_PATH.read_text(encoding="utf-8") != output:
        raise SystemExit("WS6.4 registry is not deterministic")
    if REPORT_PATH.read_text(encoding="utf-8") != report:
        raise SystemExit("WS6.4 evidence report is not deterministic")
    observed = failures(registry)
    if observed:
        raise SystemExit("WS6.4 semantic validation failed:\n- " + "\n- ".join(observed))

    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda v: v.update(work_package_id="WS6.14"),
        lambda v: v.update(base_main_sha="0" * 40),
        lambda v: v.update(canonical_status_phrase="integrated through WS6.6"),
        lambda v: v.update(closed_defects=[]),
        lambda v: v.update(remaining_blocking_defects=[]),
        lambda v: v["completion"].update(final_reconciliation_complete=True),
        lambda v: v["completion"].update(all_blocking_defects_closed=True),
        lambda v: v["boundaries"].update(founder_accountability_preserved=False),
        lambda v: v["boundaries"].update(codex_start_authorized=True),
        lambda v: v["boundaries"].update(phase0_implementation_authorized=True),
        lambda v: v["uniqueness_constraints"].update(current_machine_handoff=2),
        lambda v: v["uniqueness_constraints"].update(current_issue_body=2),
        lambda v: v["uniqueness_constraints"].update(current_required_workflow=2),
        lambda v: v["external_records"][0].update(expected_state="closed"),
        lambda v: v["external_records"][1].update(expected_state="closed"),
    ]
    rejected = 0
    for mutate in mutations:
        candidate = copy.deepcopy(registry)
        mutate(candidate)
        if failures(candidate):
            rejected += 1
        else:
            raise SystemExit("WS6.4 mutation was not rejected")

    structural = copy.deepcopy(registry)
    structural["exact_records"].append(copy.deepcopy(structural["exact_records"][0]))
    if failures(structural):
        rejected += 1
    else:
        raise SystemExit("duplicate exact path mutation not rejected")
    structural = copy.deepcopy(registry)
    structural["classification_rules"] = [item for item in structural["classification_rules"] if item["id"] != "reports"]
    if failures(structural):
        rejected += 1
    else:
        raise SystemExit("unclassified report mutation not rejected")

    print(
        f"WS6.4 canonical authority successor validation passed: scanned_files={len(scanned_paths(registry))}, "
        f"exact=43, rules=11, external=3, {rejected} mutations rejected, "
        "integrated_through=WS6.7, remaining_blockers=1, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
