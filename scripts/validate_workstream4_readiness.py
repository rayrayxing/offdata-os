from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BUILD_PATH = ROOT / "scripts" / "build_workstream4_readiness.py"
CONTRACT_PATH = ROOT / "contracts" / "workstream4-readiness.json"
SCHEMA_PATH = ROOT / "schemas" / "workstream4-readiness.schema.json"
RELEASE_PATH = ROOT / "releases" / "pre-codex-chat-first-2026-08-06.json"
DOCTOR_PATH = ROOT / "scripts" / "doctor_pre_codex_macos.py"

EXPECTED_PINS = {
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1",
    "actions/setup-python": "5fda3b95a4ea91299a34e894583c3862153e4b97",
    "actions/upload-artifact": "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a",
}
LEGACY_PINS = {
    "11d5960a326750d5838078e36cf38b85af677262",
    "a26af69be951a213d495a4c3e4e4022e16d87065",
    "ea165f8d65b6e75b540449e92b4886f43607fa02",
}


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def _builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("workstream4_builder", BUILD_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load Workstream 4 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def semantic_failures(contract: dict[str, Any], *, check_files: bool = True) -> list[str]:
    failures: list[str] = []
    if contract.get("status") != "repository_preparation_complete_manual_attestations_pending":
        failures.append("status must describe repository completion with manual attestations pending")

    pins = contract.get("node24_action_pins", {})
    for repository, expected_sha in EXPECTED_PINS.items():
        key = {
            "actions/checkout": "checkout",
            "actions/setup-python": "setup_python",
            "actions/upload-artifact": "upload_artifact",
        }[repository]
        pin = pins.get(key, {}) if isinstance(pins, dict) else {}
        if pin.get("repository") != repository or pin.get("sha") != expected_sha:
            failures.append(f"invalid exact pin for {repository}")
        if pin.get("runtime") != "node24":
            failures.append(f"{repository} must use node24")

    inventory = contract.get("workflow_inventory", [])
    if len(inventory) != 8:
        failures.append("exactly eight permanent workflows are required")
    for workflow in inventory if isinstance(inventory, list) else []:
        for use in workflow.get("official_action_uses", []):
            if use.get("sha") != EXPECTED_PINS.get(use.get("repository")):
                failures.append(f"workflow {workflow.get('path')} has an unexpected action pin")
            if use.get("sha") in LEGACY_PINS:
                failures.append(f"workflow {workflow.get('path')} retains a legacy action pin")

    if contract.get("workflow_pin_failures") != []:
        failures.append("workflow pin failure list must be empty")

    status = contract.get("required_status_check", {})
    if status.get("job_name") != "Validate complete chat-first Phase 1–7 and PCR-01–10 release":
        failures.append("final required status-check name is incorrect")

    manual = contract.get("hosted_controls_manual_attestations", {})
    if not isinstance(manual, dict) or not manual or any(value is not False for value in manual.values()):
        failures.append("hosted controls cannot be claimed without manual evidence")

    mac = contract.get("clean_macos_environment", {})
    for field in (
        "machine_report_attached",
        "founder_environment_attestation_received",
        "clean_macos_environment_verified",
    ):
        if mac.get(field) is not False:
            failures.append(f"{field} must remain false before a real clean-macOS report")

    readiness = contract.get("readiness", {})
    snapshot = contract.get("readiness_snapshot", {})
    for field in (
        "hosted_controls_verified",
        "clean_macos_environment_verified",
        "explicit_founder_phase_0_approval_received",
        "workstream_4_complete",
        "codex_start_authorized",
    ):
        if readiness.get(field) is not False or snapshot.get(field) is not False:
            failures.append(f"{field} must remain false")

    boundaries = contract.get("boundaries", {})
    for key, value in boundaries.items() if isinstance(boundaries, dict) else []:
        expected = key == "founder_accountability_preserved"
        if value is not expected:
            failures.append(f"boundary {key} has invalid value")

    cleanup = contract.get("branch_cleanup", {})
    branches: list[str] = []
    branches.extend(cleanup.get("merged_or_obsolete_branches", []))
    branches.extend(cleanup.get("superseded_dependabot_branches", []))
    branches.extend(
        item.get("branch", "")
        for item in cleanup.get("explicitly_superseded_branches", [])
        if isinstance(item, dict)
    )
    if cleanup.get("deletion_policy") != "exact_allowlist_only":
        failures.append("branch cleanup must use an exact allowlist")
    if cleanup.get("verify_merged_ancestry_before_deletion") is not True:
        failures.append("merged ancestry verification is required")
    if "main" in branches or any("*" in branch for branch in branches):
        failures.append("branch cleanup must never include main or wildcard patterns")
    if len(branches) != len(set(branches)):
        failures.append("branch cleanup entries must be unique")

    evidence = contract.get("release_evidence", {})
    if evidence.get("unresolved_references") != 0:
        failures.append("release evidence must retain zero unresolved references")
    if evidence.get("runtime_tests_passed", 0) < 247:
        failures.append("release evidence test count regressed")
    if evidence.get("coverage_percent", 0) < 90:
        failures.append("release evidence coverage regressed")

    durable = contract.get("durable_release", {})
    if durable.get("path") != "releases/pre-codex-chat-first-2026-08-06.json":
        failures.append("durable release path is incorrect")

    if check_files:
        module = _builder()
        expected_contract, expected_release = module.build_records()
        if contract != expected_contract:
            failures.append("Workstream 4 contract is stale")
        release = _load_json(RELEASE_PATH)
        if release != expected_release:
            failures.append("permanent release manifest is stale")
        result = subprocess.run(
            [sys.executable, str(DOCTOR_PATH), "--self-test"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            failures.append(f"macOS doctor self-test failed: {result.stdout}{result.stderr}")
    return failures


def _mutation_count(contract: dict[str, Any]) -> int:
    cases: list[dict[str, Any]] = []

    for key in ("checkout", "setup_python", "upload_artifact"):
        mutation = copy.deepcopy(contract)
        mutation["node24_action_pins"][key]["sha"] = "0" * 40
        cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["node24_action_pins"]["checkout"]["runtime"] = "node20"
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["workflow_inventory"][0]["official_action_uses"][0]["sha"] = next(iter(LEGACY_PINS))
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["workflow_pin_failures"].append("legacy pin")
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["required_status_check"]["job_name"] = "old gate"
    cases.append(mutation)

    for key in contract["hosted_controls_manual_attestations"]:
        mutation = copy.deepcopy(contract)
        mutation["hosted_controls_manual_attestations"][key] = True
        cases.append(mutation)

    for key in (
        "machine_report_attached",
        "founder_environment_attestation_received",
        "clean_macos_environment_verified",
    ):
        mutation = copy.deepcopy(contract)
        mutation["clean_macos_environment"][key] = True
        cases.append(mutation)

    for key in (
        "hosted_controls_verified",
        "clean_macos_environment_verified",
        "explicit_founder_phase_0_approval_received",
        "workstream_4_complete",
        "codex_start_authorized",
    ):
        mutation = copy.deepcopy(contract)
        mutation["readiness"][key] = True
        cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["branch_cleanup"]["merged_or_obsolete_branches"].append("main")
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["branch_cleanup"]["merged_or_obsolete_branches"].append("governance/*")
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["branch_cleanup"]["deletion_policy"] = "prefix_match"
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["release_evidence"]["coverage_percent"] = 89.99
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["release_evidence"]["unresolved_references"] = 1
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["boundaries"]["real_client_data_enabled"] = True
    cases.append(mutation)

    schema = _load_json(SCHEMA_PATH)
    schema_validator = Draft202012Validator(schema)
    for index, mutation in enumerate(cases, start=1):
        schema_errors = list(schema_validator.iter_errors(mutation))
        semantic_errors = semantic_failures(mutation, check_files=False)
        if not schema_errors and not semantic_errors:
            raise SystemExit(f"Workstream 4 mutation case {index} was not rejected")
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
            "Workstream 4 schema validation failed:\n- "
            + "\n- ".join(error.message for error in schema_errors)
        )
    failures = semantic_failures(contract)
    if failures:
        raise SystemExit("Workstream 4 semantic validation failed:\n- " + "\n- ".join(failures))
    count = _mutation_count(contract)
    print(
        "Workstream 4 readiness passed: "
        f"{len(contract['workflow_inventory'])} workflows exactly pinned to Node 24 actions, "
        f"{count} mutation cases rejected, "
        "repository_side_prerequisites_passed=true, hosted_controls_verified=false, "
        "clean_macos_environment_verified=false, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
