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
BUILD_PATH = ROOT / "scripts" / "build_workstream5_launch_control.py"
VERIFY_PATH = ROOT / "scripts" / "prepare_codex_phase0_launch.py"
SOURCE_PATH = ROOT / "configs" / "codex-phase0-launch-control.yaml"
CONTRACT_PATH = ROOT / "contracts" / "codex-phase0-launch-control.json"
SCHEMA_PATH = ROOT / "schemas" / "codex-phase0-launch-control.schema.json"
EVIDENCE_SCHEMA_PATH = ROOT / "schemas" / "codex-phase0-launch-evidence.schema.json"
PERMIT_SCHEMA_PATH = ROOT / "schemas" / "codex-phase0-launch-permit.schema.json"
ISSUE_BODY_PATH = ROOT / "handoff" / "codex-phase0-issue-workstream5.md"
RELEASE_PATH = ROOT / "releases" / "codex-phase0-launch-control-2026-08-06.json"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "workstream5-launch-control.yml"

EXPECTED_PRIOR_EVIDENCE = {
    "contracts/pre-codex-readiness.json": "0657d642a0a9b5fc6367c7ac1c7f0b557e20e67e501e5bb7824dc7c80d894a06",
    "contracts/workstream4-readiness.json": "f5fc5b48afad19be7419b4cffdc7482a3f3b5c5a76a0ab724fe3a3bc62161654",
    "releases/pre-codex-chat-first-2026-08-06.json": "064d6b95bdc70047fd4d1b98ce47230bb5a57a77130db971735d505947bb76a6",
    "handoff/codex-phase0-issue-pcr10.md": "01871803444487ef3e808f155a85cc13ac6fc2350eb11a401e6b5c14fc4a79ad",
    "scripts/doctor_pre_codex_macos.py": "48d16cc1fd0a6130176cd3425cf8e043f6b2b9bbdc74310a0db75f83aa703ba3",
}

REQUIRED_FILES = (
    SOURCE_PATH,
    CONTRACT_PATH,
    SCHEMA_PATH,
    EVIDENCE_SCHEMA_PATH,
    PERMIT_SCHEMA_PATH,
    BUILD_PATH,
    VERIFY_PATH,
    ROOT / "scripts" / "codex_phase0_launch_core.py",
    ROOT / "scripts" / "codex_phase0_launch_selftest.py",
    ISSUE_BODY_PATH,
    RELEASE_PATH,
    ROOT / "handoff" / "codex-phase0-hosted-controls-attestation.template.json",
    ROOT / "handoff" / "codex-phase0-clean-macos-attestation.template.json",
    ROOT / "handoff" / "codex-phase0-founder-authorization.template.json",
    ROOT / "handoff" / "codex-phase0-launch-ack.template.json",
    ROOT / "docs" / "51-WORKSTREAM-5-CODEX-PHASE-0-LAUNCH-CONTROL.md",
    ROOT / "reports" / "workstream5-launch-control-evidence.md",
    WORKFLOW_PATH,
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _sha256_file(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("workstream5_builder", BUILD_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load Workstream 5 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def semantic_failures(contract: dict[str, Any], *, check_files: bool = True) -> list[str]:
    failures: list[str] = []
    if contract.get("status") != "repository_launch_control_complete_manual_gates_pending":
        failures.append("status must describe a complete repository launch control with manual gates pending")
    declared_prior = {
        item.get("path"): item.get("sha256")
        for item in contract.get("prior_evidence", [])
        if isinstance(item, dict)
    }
    if declared_prior != EXPECTED_PRIOR_EVIDENCE:
        failures.append("declared prior-evidence digest register is incorrect")
    if contract.get("pre_workstream_main_sha") != "94fe29e60449a384c1c5fad1f3bb6289d4ac1c29":
        failures.append("pre-Workstream 5 main SHA is incorrect")

    target = contract.get("launch_target", {})
    if target.get("permitted_tasks") != ["P0.1", "P0.2", "P0.3", "P0.4"]:
        failures.append("launch tasks must be exactly P0.1-P0.4")
    if target.get("required_branch") != "codex/phase-0-foundation":
        failures.append("Codex branch is incorrect")
    if target.get("required_pull_request_state") != "draft":
        failures.append("Phase 0 pull request must be draft")
    if target.get("implementation_may_start_only_after_valid_permit") is not True:
        failures.append("implementation must require a valid launch permit")
    if target.get("merge_authorized") is not False or target.get("phase1_authorized") is not False:
        failures.append("launch target cannot authorize merge or Phase 1")

    sha_binding = contract.get("sha_binding", {})
    for key in (
        "approved_main_sha_required",
        "must_equal_current_main",
        "must_include_workstream5_launch_control",
        "all_evidence_must_reference_same_sha",
        "stale_on_main_advance",
        "stale_on_issue_body_change",
        "stale_on_evidence_digest_change",
    ):
        if sha_binding.get(key) is not True:
            failures.append(f"SHA-binding control {key} must be true")
    if sha_binding.get("approved_main_sha") is not None:
        failures.append("committed launch control must not pre-bind a Founder-approved SHA")

    permit = contract.get("launch_permit", {})
    if permit.get("output_directory") != ".local/codex-phase0-launch":
        failures.append("launch permit must remain in the ignored local directory")
    if permit.get("single_use") is not True or permit.get("commit_prohibited") is not True:
        failures.append("launch permit must be single-use and prohibited from commit")
    if permit.get("file_mode") != "0600":
        failures.append("launch permit file mode must be 0600")
    if len(permit.get("revocation_conditions", [])) < 8:
        failures.append("launch permit revocation register is incomplete")

    live = contract.get("live_repository_preconditions", {})
    if not isinstance(live, dict) or len(live) < 8 or any(value is not True for value in live.values()):
        failures.append("all live repository preconditions must be required")

    readiness = contract.get("readiness", {})
    snapshot = contract.get("readiness_snapshot", {})
    for field in (
        "hosted_controls_verified",
        "clean_macos_environment_verified",
        "explicit_founder_phase0_approval_received",
        "approved_main_sha_bound",
        "launch_permit_issued",
        "codex_start_authorized",
    ):
        if readiness.get(field) is not False or snapshot.get(field) is not False:
            failures.append(f"{field} must remain false in committed launch-control records")
    if readiness.get("repository_launch_control_complete") is not True:
        failures.append("source launch-control package must be complete")
    if snapshot.get("repository_launch_control_complete") is not True:
        failures.append("generated launch-control package must be complete")
    if snapshot.get("github_issue_sync_verified") is not False:
        failures.append("mutable GitHub issue sync cannot be hardcoded true")

    boundaries = contract.get("boundaries", {})
    for key, value in boundaries.items() if isinstance(boundaries, dict) else []:
        expected = key == "founder_accountability_preserved"
        if value is not expected:
            failures.append(f"boundary {key} has invalid value")

    if contract.get("allowed_scope") != list(dict.fromkeys(contract.get("allowed_scope", []))):
        failures.append("allowed scope entries must be unique")
    if contract.get("prohibited_scope") != list(dict.fromkeys(contract.get("prohibited_scope", []))):
        failures.append("prohibited scope entries must be unique")
    if contract.get("stop_conditions") != list(dict.fromkeys(contract.get("stop_conditions", []))):
        failures.append("stop conditions must be unique")
    if "begin_phase1" not in contract.get("prohibited_scope", []):
        failures.append("Phase 1 must remain prohibited")
    if "main_sha_drift" not in contract.get("stop_conditions", []):
        failures.append("main SHA drift must be a stop condition")

    registry = contract.get("launch_protocol_registry", {})
    if registry.get("permitted_task_count") != 4:
        failures.append("launch protocol must contain four permitted tasks")
    if registry.get("preflight_command_count", 0) < 40:
        failures.append("complete preflight command register is required")
    if registry.get("prohibited_scope_count", 0) < 13:
        failures.append("prohibited scope register is incomplete")

    issue = contract.get("generated_issue", {})
    if issue.get("body_path") != "handoff/codex-phase0-issue-workstream5.md":
        failures.append("generated issue path is incorrect")
    if issue.get("github_issue_sync_verified") is not False:
        failures.append("generated issue sync must remain a live external fact")

    if check_files:
        for path in REQUIRED_FILES:
            if not path.is_file():
                failures.append(f"required Workstream 5 file is missing: {path.relative_to(ROOT)}")

        declared = contract.get("prior_evidence", [])
        for item in declared if isinstance(declared, list) else []:
            path = ROOT / item.get("path", "")
            if not path.is_file():
                failures.append(f"prior evidence file is missing: {item.get('path')}")
            elif _sha256_file(path) != item.get("sha256"):
                failures.append(f"prior evidence digest drift: {item.get('path')}")

        module = _builder()
        expected_contract, expected_issue, expected_templates, expected_release = module.build_records()
        if contract != expected_contract:
            failures.append("Workstream 5 launch-control contract is stale")
        if ISSUE_BODY_PATH.read_text(encoding="utf-8") != expected_issue:
            failures.append("Workstream 5 generated issue body is stale")
        for key, value in expected_templates.items():
            path = module.TEMPLATE_PATHS[key]
            if _load_json(path) != value:
                failures.append(f"Workstream 5 template is stale: {path.relative_to(ROOT)}")
        if _load_json(RELEASE_PATH) != expected_release:
            failures.append("Workstream 5 durable release record is stale")

        body = ISSUE_BODY_PATH.read_text(encoding="utf-8")
        for token in (
            "Workstream 5 launch control",
            ".local/codex-phase0-launch/",
            "Codex Phase 0 only",
            "single-use",
            "governance/codex-phase0-launch-ack.json",
            "prepare_codex_phase0_launch.py --self-test",
        ):
            if token not in body:
                failures.append(f"generated issue body is missing launch-control token: {token}")

        workflow = WORKFLOW_PATH.read_text(encoding="utf-8") if WORKFLOW_PATH.is_file() else ""
        for token in (
            "Validate Codex Phase 0 launch control and complete prior release",
            "python scripts/build_workstream5_launch_control.py",
            "python scripts/validate_workstream5_launch_control.py",
            "python scripts/prepare_codex_phase0_launch.py --self-test",
            "git diff --exit-code",
            "pytest --cov=offdata_core",
            "ruff check",
            "mypy src",
            "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
            "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97",
            "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a",
        ):
            if token not in workflow:
                failures.append(f"Workstream 5 workflow is missing token: {token}")

        evidence_schema = _load_json(EVIDENCE_SCHEMA_PATH)
        evidence_validator = Draft202012Validator(evidence_schema)
        for item in contract.get("template_registry", {}).values():
            template = _load_json(ROOT / item["path"])
            errors = list(evidence_validator.iter_errors(template))
            if errors:
                failures.append(
                    f"launch evidence template schema failed for {item['path']}: "
                    + "; ".join(error.message for error in errors)
                )

        result = subprocess.run(
            [sys.executable, str(VERIFY_PATH), "--self-test"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            failures.append(f"launch verifier self-test failed: {result.stdout}{result.stderr}")
    return failures


def _mutation_count(contract: dict[str, Any]) -> int:
    cases: list[dict[str, Any]] = []

    for key in (
        "hosted_controls_verified",
        "clean_macos_environment_verified",
        "explicit_founder_phase0_approval_received",
        "approved_main_sha_bound",
        "launch_permit_issued",
        "codex_start_authorized",
    ):
        mutation = copy.deepcopy(contract)
        mutation["readiness"][key] = True
        cases.append(mutation)
        mutation = copy.deepcopy(contract)
        mutation["readiness_snapshot"][key] = True
        cases.append(mutation)

    for key in (
        "merge_authorized",
        "phase1_authorized",
    ):
        mutation = copy.deepcopy(contract)
        mutation["launch_target"][key] = True
        cases.append(mutation)

    for key in contract["sha_binding"]:
        if key == "approved_main_sha":
            mutation = copy.deepcopy(contract)
            mutation["sha_binding"][key] = "a" * 40
        else:
            mutation = copy.deepcopy(contract)
            mutation["sha_binding"][key] = False
        cases.append(mutation)

    for key in (
        "single_use",
        "commit_prohibited",
    ):
        mutation = copy.deepcopy(contract)
        mutation["launch_permit"][key] = False
        cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["launch_permit"]["output_directory"] = "reports"
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["launch_target"]["required_branch"] = "main"
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["launch_target"]["permitted_tasks"].append("P1.1")
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["prohibited_scope"].remove("begin_phase1")
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["stop_conditions"].remove("main_sha_drift")
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["live_repository_preconditions"]["codex_phase0_branch_absent"] = False
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["boundaries"]["real_client_data_enabled"] = True
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["boundaries"]["founder_accountability_preserved"] = False
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["generated_issue"]["github_issue_sync_verified"] = True
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["readiness_snapshot"]["github_issue_sync_verified"] = True
    cases.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["prior_evidence"][0]["sha256"] = "0" * 64
    cases.append(mutation)

    schema = _load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    for index, mutation in enumerate(cases, start=1):
        schema_errors = list(validator.iter_errors(mutation))
        semantic_errors = semantic_failures(mutation, check_files=False)
        if not schema_errors and not semantic_errors:
            raise SystemExit(f"Workstream 5 mutation case {index} was not rejected")
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
            "Workstream 5 schema validation failed:\n- "
            + "\n- ".join(error.message for error in schema_errors)
        )
    failures = semantic_failures(contract)
    if failures:
        raise SystemExit("Workstream 5 semantic validation failed:\n- " + "\n- ".join(failures))
    count = _mutation_count(contract)
    print(
        "Workstream 5 Codex Phase 0 launch control passed: "
        f"{contract['launch_protocol_registry']['preflight_command_count']} preflight commands, "
        f"{count} contract mutation cases rejected, launch-verifier self-test passed, "
        "hosted_controls_verified=false, clean_macos_environment_verified=false, "
        "founder_approval=false, launch_permit_issued=false, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
