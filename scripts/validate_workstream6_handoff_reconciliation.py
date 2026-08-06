from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BUILD_PATH = ROOT / "scripts" / "build_workstream6_handoff_reconciliation.py"
HANDOFF_VALIDATOR_PATH = ROOT / "scripts" / "validate_ws61_codex_handoff.py"
CONTRACT_PATH = ROOT / "contracts" / "workstream6-handoff-reconciliation.json"
SCHEMA_PATH = ROOT / "schemas" / "workstream6-handoff-reconciliation.schema.json"
REPORT_PATH = ROOT / "reports" / "workstream6-handoff-reconciliation-evidence.md"
DOC_PATH = ROOT / "docs" / "53-WS6-1-CONTROLLING-MACHINE-HANDOFF-RECONCILIATION.md"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "workstream6-handoff-reconciliation.yml"
BASE_MAIN_SHA = "5c80cea82aa663cbe0a690e3f8f02504d121bea1"


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def semantic_failures(
    contract: dict[str, Any], *, check_files: bool = True, check_generated: bool = True
) -> list[str]:
    failures: list[str] = []
    if contract.get("work_package_id") != "WS6.1":
        failures.append("contract must describe WS6.1")
    if contract.get("status") != "controlling_machine_handoff_reconciled":
        failures.append("WS6.1 status is incorrect")
    if contract.get("base_main_sha") != BASE_MAIN_SHA:
        failures.append("WS6.1 base must be the exact WS6.0 merge")
    if contract.get("closed_defects") != ["WS6-BLOCK-001", "WS6-BLOCK-002"]:
        failures.append("WS6.1 must close exactly BLOCK-001 and BLOCK-002")
    if contract.get("remaining_blocking_defects") != [
        "WS6-BLOCK-003",
        "WS6-BLOCK-004",
        "WS6-BLOCK-005",
        "WS6-BLOCK-006",
    ]:
        failures.append("remaining blocking-defect sequence is incorrect")

    reconciliation = contract.get("reconciliation", {})
    for field in (
        "pcr10_included",
        "workstream4_included",
        "workstream5_included",
        "workstream6_baseline_and_ws61_included",
        "final_workstream6_activation_gate_required",
        "valid_launch_permit_required",
        "full_p0_3_regression_scope_required",
    ):
        if reconciliation.get(field) is not True:
            failures.append(f"reconciliation field {field} must be true")
    expected_counts = {
        "prerequisite_record_count": 14,
        "read_order_count": 45,
        "required_command_count": 49,
        "activation_condition_count": 15,
    }
    for field, expected in expected_counts.items():
        if reconciliation.get(field) != expected:
            failures.append(f"{field} must be {expected}")

    completion = contract.get("completion", {})
    if completion.get("ws60_complete") is not True:
        failures.append("WS6.0 must remain complete")
    if completion.get("ws61_complete") is not True:
        failures.append("WS6.1 must be complete")
    if completion.get("all_required_prior_components_pass") is not True:
        failures.append("all prior components must pass")
    if completion.get("all_blocking_defects_closed") is not False:
        failures.append("later blockers must remain open")
    if completion.get("final_reconciliation_complete") is not False:
        failures.append("final reconciliation must remain incomplete")
    if completion.get("next_permitted_work_package") != "WS6.2":
        failures.append("WS6.2 must be the next work package")

    boundaries = contract.get("boundaries", {})
    if boundaries.get("founder_accountability_preserved") is not True:
        failures.append("Founder accountability must remain preserved")
    for key, value in boundaries.items():
        if key != "founder_accountability_preserved" and value is not False:
            failures.append(f"boundary {key} must remain false")

    if check_files:
        for path in (
            BUILD_PATH,
            HANDOFF_VALIDATOR_PATH,
            CONTRACT_PATH,
            SCHEMA_PATH,
            REPORT_PATH,
            DOC_PATH,
            WORKFLOW_PATH,
            ROOT / "configs" / "workstream6-handoff-reconciliation.yaml",
            ROOT / "configs" / "codex-handoff.yaml",
            ROOT / "handoff" / "codex-phase0-handoff.json",
            ROOT / "scripts" / "require_workstream6_final_reconciliation.py",
        ):
            if not path.is_file():
                failures.append(f"required WS6.1 file is missing: {path.relative_to(ROOT)}")

        handoff_validator = _module(HANDOFF_VALIDATOR_PATH, "ws61_handoff_validator")
        handoff = _load_json(ROOT / "handoff" / "codex-phase0-handoff.json")
        failures.extend(
            f"handoff: {failure}"
            for failure in handoff_validator.semantic_failures(handoff)
        )

        report = REPORT_PATH.read_text(encoding="utf-8") if REPORT_PATH.is_file() else ""
        for token in (
            BASE_MAIN_SHA,
            "WS6-BLOCK-001",
            "WS6-BLOCK-002",
            "Next permitted work package: `WS6.2`",
            "codex_start_authorized=false",
        ):
            if token not in report:
                failures.append(f"evidence report is missing token: {token}")

        document = DOC_PATH.read_text(encoding="utf-8") if DOC_PATH.is_file() else ""
        for token in (
            "WS6.1",
            "PCR-10",
            "Workstream 4",
            "Workstream 5",
            "Workstream 6",
            "valid Codex Phase 0 launch permit",
            "WS6.2",
        ):
            if token not in document:
                failures.append(f"WS6.1 document is missing token: {token}")

        workflow = WORKFLOW_PATH.read_text(encoding="utf-8") if WORKFLOW_PATH.is_file() else ""
        for token in (
            "Validate WS6.1 controlling machine handoff and complete prior components",
            "python scripts/build_workstream6_handoff_reconciliation.py",
            "python scripts/validate_workstream6_handoff_reconciliation.py",
            "python scripts/require_workstream6_final_reconciliation.py --self-test",
            "pytest --cov=offdata_core",
            "mypy src",
        ):
            if token not in workflow:
                failures.append(f"WS6.1 workflow is missing token: {token}")

    if check_generated:
        builder = _module(BUILD_PATH, "ws61_package_builder")
        expected_contract, expected_report = builder.build_records()
        if contract != expected_contract:
            failures.append("generated WS6.1 contract is stale")
        if REPORT_PATH.read_text(encoding="utf-8") != expected_report:
            failures.append("generated WS6.1 report is stale")
    return failures


def _mutation_count(contract: dict[str, Any]) -> int:
    cases: list[dict[str, Any]] = []

    def add(mutator: Any) -> None:
        mutation = copy.deepcopy(contract)
        mutator(mutation)
        cases.append(mutation)

    add(lambda item: item.__setitem__("base_main_sha", "0" * 40))
    add(lambda item: item["closed_defects"].pop())
    add(lambda item: item["closed_defects"].append("WS6-BLOCK-003"))
    add(lambda item: item["remaining_blocking_defects"].pop())
    add(lambda item: item["reconciliation"].__setitem__("pcr10_included", False))
    add(lambda item: item["reconciliation"].__setitem__("workstream4_included", False))
    add(lambda item: item["reconciliation"].__setitem__("workstream5_included", False))
    add(lambda item: item["reconciliation"].__setitem__("workstream6_baseline_and_ws61_included", False))
    add(lambda item: item["reconciliation"].__setitem__("final_workstream6_activation_gate_required", False))
    add(lambda item: item["reconciliation"].__setitem__("valid_launch_permit_required", False))
    add(lambda item: item["reconciliation"].__setitem__("full_p0_3_regression_scope_required", False))
    add(lambda item: item["reconciliation"].__setitem__("required_command_count", 48))
    add(lambda item: item["completion"].__setitem__("ws60_complete", False))
    add(lambda item: item["completion"].__setitem__("all_required_prior_components_pass", False))
    add(lambda item: item["completion"].__setitem__("all_blocking_defects_closed", True))
    add(lambda item: item["completion"].__setitem__("final_reconciliation_complete", True))
    add(lambda item: item["completion"].__setitem__("next_permitted_work_package", "WS6.3"))
    add(lambda item: item["boundaries"].__setitem__("codex_start_authorized", True))

    schema = _load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    for index, mutation in enumerate(cases, start=1):
        schema_errors = list(validator.iter_errors(mutation))
        semantic_errors = semantic_failures(
            mutation, check_files=False, check_generated=False
        )
        if not schema_errors and not semantic_errors:
            raise SystemExit(f"WS6.1 package mutation {index} was not rejected")
    return len(cases)


def main() -> None:
    contract = _load_json(CONTRACT_PATH)
    schema = _load_json(SCHEMA_PATH)
    schema_errors = sorted(
        Draft202012Validator(schema).iter_errors(contract),
        key=lambda error: list(error.absolute_path),
    )
    if schema_errors:
        raise SystemExit(
            "WS6.1 package schema validation failed:\n- "
            + "\n- ".join(error.message for error in schema_errors)
        )
    failures = semantic_failures(contract)
    if failures:
        raise SystemExit("WS6.1 package validation failed:\n- " + "\n- ".join(failures))
    mutation_count = _mutation_count(contract)
    print(
        "WS6.1 controlling handoff reconciliation passed: "
        f"closed_defects={len(contract['closed_defects'])}, "
        f"remaining_blockers={len(contract['remaining_blocking_defects'])}, "
        f"{mutation_count} mutations rejected, next=WS6.2, "
        "codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
