from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BUILD_PATH = ROOT / "scripts" / "build_workstream6_final_reconciliation.py"
CONTRACT_PATH = ROOT / "contracts" / "workstream6-final-reconciliation.json"
SCHEMA_PATH = ROOT / "schemas" / "workstream6-final-reconciliation.schema.json"
REPORT_PATH = ROOT / "reports" / "workstream6-initial-defect-register.md"
RELEASE_PATH = ROOT / "releases" / "workstream6-baseline-lock-2026-08-06.json"
DOC_PATH = ROOT / "docs" / "52-WORKSTREAM-6-FINAL-PRE-CODEX-RECONCILIATION.md"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "workstream6-baseline-lock.yml"

EXPECTED_MAIN_SHA = "ad24030200e421016066e7039e202ff9f0c5398d"
EXPECTED_BLOCKERS = {f"WS6-BLOCK-{number:03d}" for number in range(1, 7)}
EXPECTED_PREFIX_COUNTS = {
    "WS6-BLOCK": 6,
    "WS6-CONSIST": 10,
    "WS6-QUALITY": 5,
    "WS6-CODEXPREP": 7,
}

REQUIRED_FILES = (
    BUILD_PATH,
    CONTRACT_PATH,
    SCHEMA_PATH,
    REPORT_PATH,
    RELEASE_PATH,
    DOC_PATH,
    WORKFLOW_PATH,
    ROOT / "configs" / "workstream6-final-reconciliation.yaml",
    ROOT / "configs" / "workstream6-defects-blocking.yaml",
    ROOT / "configs" / "workstream6-defects-consistency.yaml",
    ROOT / "configs" / "workstream6-defects-quality.yaml",
    ROOT / "configs" / "workstream6-defects-codexprep.yaml",
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("workstream6_builder", BUILD_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load Workstream 6 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def semantic_failures(
    contract: dict[str, Any],
    *,
    check_files: bool,
    check_prior: bool,
) -> list[str]:
    failures: list[str] = []
    if contract.get("status") != "baseline_locked_repairs_pending":
        failures.append("status must be baseline_locked_repairs_pending")
    if contract.get("baseline", {}).get("main_sha") != EXPECTED_MAIN_SHA:
        failures.append("baseline main SHA must equal the Workstream 5 merge")
    if contract.get("baseline", {}).get("workstream5_pr") != 35:
        failures.append("baseline must identify Workstream 5 PR #35")
    if contract.get("baseline", {}).get("unresolved_reference_count") != 0:
        failures.append("baseline unresolved-reference count must be zero")

    components = contract.get("prior_components", [])
    component_ids = [item.get("id") for item in components if isinstance(item, dict)]
    required_ids = (
        [f"CF-P{number}" for number in range(1, 8)]
        + [f"PCR-{number:02d}" for number in range(1, 11)]
        + ["WS-4", "WS-5"]
    )
    if component_ids != required_ids:
        failures.append(
            "prior component sequence must be CF-P1-7, PCR-01-10, WS-4 and WS-5"
        )
    if any(item.get("required") is not True for item in components):
        failures.append("every prior component must be required")

    checks = contract.get("prior_component_checks", {})
    if not isinstance(checks, dict) or len(checks) < 12 or not all(checks.values()):
        failures.append("all prior component checks must be present and true")

    issue_snapshot = contract.get("live_issue_snapshot", {})
    if issue_snapshot.get("issue_1", {}).get("state") != "open":
        failures.append("issue #1 baseline state must be open")
    issue_2 = issue_snapshot.get("issue_2", {})
    if issue_2.get("state") != "closed" or issue_2.get("state_reason") != "duplicate":
        failures.append("issue #2 baseline state must be closed as duplicate")
    issue_19 = issue_snapshot.get("issue_19", {})
    if issue_19.get("state") != "open" or issue_19.get("state_reason") is not None:
        failures.append("issue #19 baseline state must be open")

    inventory = contract.get("branch_inventory_snapshot", {})
    branches = inventory.get("branches", [])
    if inventory.get("branch_count") != 28 or len(branches) != 28:
        failures.append("pre-WS6 branch inventory must contain exactly 28 branches")
    if len(branches) != len(set(branches)):
        failures.append("branch inventory must be unique")
    if "main" not in branches:
        failures.append("branch inventory must contain main")
    if "codex/phase-0-foundation" in branches:
        failures.append("Codex Phase 0 branch must be absent")
    if inventory.get("cleanup_complete") is not False:
        failures.append("historical branch cleanup must remain incomplete")

    defects = contract.get("defects", [])
    identifiers = [item.get("id") for item in defects if isinstance(item, dict)]
    if len(defects) != 28 or len(identifiers) != len(set(identifiers)):
        failures.append("defect register must contain 28 unique entries")
    blockers = {
        item.get("id")
        for item in defects
        if isinstance(item, dict) and item.get("severity") == "blocking"
    }
    if blockers != EXPECTED_BLOCKERS:
        failures.append("blocking defect register must be exactly WS6-BLOCK-001 through 006")
    for prefix, expected in EXPECTED_PREFIX_COUNTS.items():
        actual = sum(str(identifier).startswith(prefix) for identifier in identifiers)
        if actual != expected:
            failures.append(f"{prefix} count must be {expected}")
    for item in defects:
        if not isinstance(item, dict):
            failures.append("every defect must be an object")
            continue
        for field in (
            "title",
            "evidence",
            "affected_authority",
            "repair_files",
            "validation",
            "rollback",
            "owner",
            "target_work_package",
        ):
            if not item.get(field):
                failures.append(f"{item.get('id')} is missing {field}")
        if item.get("status") != "open":
            failures.append(f"{item.get('id')} must remain open at WS6.0")

    summary = contract.get("defect_summary", {})
    if summary.get("total") != 28:
        failures.append("defect summary total must be 28")
    if summary.get("by_severity") != {
        "blocking": 6,
        "important": 12,
        "planned": 10,
    }:
        failures.append("defect severity summary is incorrect")
    if summary.get("by_status") != {"open": 28}:
        failures.append("all WS6.0 entries must be open")

    manual = contract.get("manual_gates", {})
    if not isinstance(manual, dict) or len(manual) < 7 or any(manual.values()):
        failures.append("all manual launch gates must remain false")
    boundaries = contract.get("boundaries", {})
    if boundaries.get("founder_accountability_preserved") is not True:
        failures.append("Founder accountability must be preserved")
    for key, value in boundaries.items() if isinstance(boundaries, dict) else []:
        if key != "founder_accountability_preserved" and value is not False:
            failures.append(f"boundary {key} must remain false")

    completion = contract.get("completion_rule", {})
    if completion.get("baseline_locked") is not True:
        failures.append("baseline must be locked")
    if completion.get("defect_register_complete") is not True:
        failures.append("defect register must be complete")
    if completion.get("all_blocking_defects_closed") is not False:
        failures.append("WS6.0 cannot claim blocking defects are closed")
    if completion.get("final_reconciliation_complete") is not False:
        failures.append("WS6.0 cannot claim final reconciliation is complete")
    if completion.get("codex_start_authorized") is not False:
        failures.append("WS6.0 cannot authorize Codex")
    if completion.get("next_permitted_work_package") != "WS6.1":
        failures.append("the next permitted work package must be WS6.1")

    if check_files:
        for path in REQUIRED_FILES:
            if not path.is_file():
                failures.append(f"required WS6.0 file is missing: {path.relative_to(ROOT)}")
        if not failures:
            builder = _builder()
            expected_contract, expected_report, expected_release = builder.build_records()
            if contract != expected_contract:
                failures.append("generated Workstream 6 contract is stale")
            if REPORT_PATH.read_text(encoding="utf-8") != expected_report:
                failures.append("generated Workstream 6 defect report is stale")
            if _load_json(RELEASE_PATH) != expected_release:
                failures.append("generated Workstream 6 baseline release is stale")

        report = REPORT_PATH.read_text(encoding="utf-8") if REPORT_PATH.is_file() else ""
        for token in (
            "Workstream 6 initial defect register",
            EXPECTED_MAIN_SHA,
            "Total entries: 28",
            "WS6-BLOCK-006",
            "codex_start_authorized=false",
            "Next permitted work package: `WS6.1`",
        ):
            if token not in report:
                failures.append(f"defect report is missing token: {token}")

        document = DOC_PATH.read_text(encoding="utf-8") if DOC_PATH.is_file() else ""
        for token in (
            "WS6.0",
            EXPECTED_MAIN_SHA,
            "six blocking defects",
            "Codex remains unauthorized",
            "WS6.1",
            "Rollback",
        ):
            if token not in document:
                failures.append(f"WS6.0 document is missing token: {token}")

        workflow = WORKFLOW_PATH.read_text(encoding="utf-8") if WORKFLOW_PATH.is_file() else ""
        for token in (
            "Validate WS6.0 baseline lock and complete prior components",
            "python scripts/build_workstream6_final_reconciliation.py",
            "python scripts/validate_workstream6_final_reconciliation.py",
            "python scripts/prepare_codex_phase0_launch.py --self-test",
            "git diff --exit-code",
            "pytest --cov=offdata_core",
            "ruff check",
            "mypy src",
            EXPECTED_MAIN_SHA,
        ):
            if token not in workflow:
                failures.append(f"WS6.0 workflow is missing token: {token}")

    if check_prior:
        prior_paths = (
            ROOT / "contracts" / "pre-codex-readiness.json",
            ROOT / "contracts" / "workstream4-readiness.json",
            ROOT / "contracts" / "codex-phase0-launch-control.json",
            ROOT / "releases" / "codex-phase0-launch-control-2026-08-06.json",
            ROOT / "handoff" / "codex-phase0-issue-workstream5.md",
        )
        for path in prior_paths:
            if not path.is_file():
                failures.append(f"required prior component is missing: {path.relative_to(ROOT)}")
        if all(path.is_file() for path in prior_paths):
            pcr10 = _load_json(prior_paths[0])
            if pcr10.get("status") != "chat_first_complete_integrated":
                failures.append("PCR-10 release status is not integrated")
            if pcr10.get("readiness_snapshot", {}).get("codex_start_authorized") is not False:
                failures.append("PCR-10 must leave Codex unauthorized")

            workstream4 = _load_json(prior_paths[1])
            ws4_snapshot = workstream4.get("readiness_snapshot", {})
            if ws4_snapshot.get("repository_side_prerequisites_passed") is not True:
                failures.append("Workstream 4 repository prerequisites are incomplete")
            if ws4_snapshot.get("hosted_controls_verified") is not False:
                failures.append("Workstream 4 hosted controls must remain pending")
            if ws4_snapshot.get("clean_macos_environment_verified") is not False:
                failures.append("Workstream 4 clean macOS gate must remain pending")

            workstream5 = _load_json(prior_paths[2])
            if workstream5.get("status") != "repository_launch_control_complete_manual_gates_pending":
                failures.append("Workstream 5 launch-control status is incorrect")
            ws5_snapshot = workstream5.get("readiness_snapshot", {})
            if ws5_snapshot.get("repository_launch_control_complete") is not True:
                failures.append("Workstream 5 repository launch control is incomplete")
            if ws5_snapshot.get("codex_start_authorized") is not False:
                failures.append("Workstream 5 must leave Codex unauthorized")

            release = _load_json(prior_paths[3])
            if any(release.get("authorization", {}).values()):
                failures.append("Workstream 5 release cannot claim authorization")

            issue_body = prior_paths[4].read_text(encoding="utf-8")
            if not issue_body.startswith(
                "<!-- Generated by scripts/build_workstream5_launch_control.py."
            ):
                failures.append("current issue body is not the Workstream 5 generated body")
            if "**NOT AUTHORISED TO START.**" not in issue_body:
                failures.append("current issue body must deny launch authorization")
    return failures


def _mutation_count(contract: dict[str, Any]) -> int:
    cases: list[dict[str, Any]] = []

    mutation = copy.deepcopy(contract)
    mutation["baseline"]["main_sha"] = "0" * 40
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["prior_components"].pop()
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["prior_component_checks"]["all_pcr_01_to_10_complete"] = False
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["live_issue_snapshot"]["issue_1"]["state"] = "closed"
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["live_issue_snapshot"]["issue_2"]["state_reason"] = None
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["live_issue_snapshot"]["issue_19"]["state"] = "closed"
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["branch_inventory_snapshot"]["branches"].append("codex/phase-0-foundation")
    mutation["branch_inventory_snapshot"]["branch_count"] = 29
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["branch_inventory_snapshot"]["cleanup_complete"] = True
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["defects"].pop()
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["defects"][0]["status"] = "closed"
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["defects"][0]["severity"] = "important"
    cases.append(mutation)

    for key in contract["manual_gates"]:
        mutation = copy.deepcopy(contract)
        mutation["manual_gates"][key] = True
        cases.append(mutation)

    for key in contract["boundaries"]:
        mutation = copy.deepcopy(contract)
        mutation["boundaries"][key] = (
            False if key == "founder_accountability_preserved" else True
        )
        cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["completion_rule"]["all_blocking_defects_closed"] = True
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["completion_rule"]["final_reconciliation_complete"] = True
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["completion_rule"]["next_permitted_work_package"] = "IMP-P0"
    cases.append(mutation)

    rejected = 0
    for mutation in cases:
        if semantic_failures(mutation, check_files=False, check_prior=False):
            rejected += 1
    if rejected != len(cases):
        raise AssertionError(f"only {rejected} of {len(cases)} mutations failed")
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="validate generated WS6.0 records without prior repository files",
    )
    args = parser.parse_args()

    contract = _load_json(CONTRACT_PATH)
    schema = _load_json(SCHEMA_PATH)
    schema_errors = sorted(
        Draft202012Validator(schema).iter_errors(contract),
        key=lambda error: list(error.path),
    )
    if schema_errors:
        raise SystemExit(
            "schema validation failed: "
            + "; ".join(error.message for error in schema_errors)
        )
    failures = semantic_failures(
        contract,
        check_files=True,
        check_prior=not args.self_test,
    )
    if failures:
        raise SystemExit("\n".join(f"- {failure}" for failure in failures))
    mutations = _mutation_count(contract)
    print(
        "Workstream 6 WS6.0 baseline lock valid: "
        f"{len(contract['prior_components'])} prior components, "
        f"{len(contract['defects'])} register entries, "
        f"{mutations} mutations rejected, Codex unauthorized."
    )


if __name__ == "__main__":
    main()
