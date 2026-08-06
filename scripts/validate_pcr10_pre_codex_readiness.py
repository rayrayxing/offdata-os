from __future__ import annotations

import copy
import importlib.util
import hashlib
import json
import subprocess
from pathlib import Path
from types import ModuleType
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "scripts" / "build_pcr10_pre_codex_readiness.py"
CONTRACT_PATH = ROOT / "contracts" / "pre-codex-readiness.json"
SCHEMA_PATH = ROOT / "schemas" / "pre-codex-readiness.schema.json"
FINAL_BODY_PATH = ROOT / "handoff" / "codex-phase0-issue-pcr10.md"
PCR09_CONTRACT_PATH = ROOT / "contracts" / "codex-phase0-issue.json"
HANDOFF_PATH = ROOT / "handoff" / "codex-phase0-handoff.json"
DOC_PATH = ROOT / "docs" / "49-PCR-10-PRE-CODEX-RELEASE-AND-QUALITY-ACCEPTANCE.md"

EXPECTED_ACTIVATION = [
    "pcr03_merged_to_main", "pcr04_merged_to_main", "pcr05_merged_to_main",
    "pcr06_merged_to_main", "pcr07_merged_to_main", "pcr08_merged_to_main",
    "pcr09_merged_to_main", "pcr10_merged_to_main",
    "github_hosted_controls_in_issue_19_verified",
    "explicit_founder_phase_0_approval_received", "clean_macos_environment_available",
]
EXPECTED_COMMANDS = {
    "doctor", "bootstrap", "up", "down", "restart", "health", "test", "lint", "format", "scan",
    "reset-synthetic", "backup", "restore", "clean", "support-bundle",
}
PROHIBITED_TRACKED_PATTERNS = (
    ".pcr09_payload_",
    "materialize_pcr09_payload.py",
    "pcr09-materialize.yml",
)


def _load_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("pcr10_builder", BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load PCR-10 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _criteria_ids(contract: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for section in (
        "developer_experience",
        "founder_experience",
        "operational_quality",
        "cross_cutting",
    ):
        ids.extend(item["id"] for item in contract[section]["acceptance_criteria"])
    for section in ("evidence", "quantitative"):
        ids.extend(item["id"] for item in contract["output_quality"][section])
    return ids


def semantic_failures(
    contract: dict[str, Any], *, check_files: bool = True
) -> list[str]:
    failures: list[str] = []
    if contract.get("activation_conditions") != EXPECTED_ACTIVATION:
        failures.append(
            "activation conditions must be the exact governed PCR-03 through PCR-10 sequence"
        )

    boundaries = contract.get("boundaries", {})
    for key, value in boundaries.items() if isinstance(boundaries, dict) else []:
        expected = key == "founder_accountability_preserved"
        if value is not expected:
            failures.append(f"boundary {key} has an invalid value")

    developer = contract.get("developer_experience", {})
    commands = (
        developer.get("phase0_required_commands", [])
        if isinstance(developer, dict)
        else []
    )
    if set(commands) != EXPECTED_COMMANDS or len(commands) != len(EXPECTED_COMMANDS):
        failures.append("developer command inventory is incomplete or duplicated")

    ids = _criteria_ids(contract)
    registry = contract.get("quality_registry", {})
    if len(ids) != len(set(ids)):
        failures.append("quality criterion IDs must be unique")
    if registry.get("criterion_ids") != ids or registry.get("criterion_count") != len(ids):
        failures.append("quality registry does not match the governed criteria")
    if len(ids) < 30:
        failures.append("quality registry is below the minimum acceptance coverage")

    metrics = {
        item["metric"]: item["target"]
        for section in ("evidence", "quantitative")
        for item in contract.get("output_quality", {}).get(section, [])
        if isinstance(item, dict)
    }
    required_metrics = {
        "material_citation_resolution_percent": 100,
        "unsupported_material_claims": 0,
        "material_number_reconciliation_percent": 100,
        "unexplained_hardcoded_material_numbers": 0,
        "cross_format_material_number_agreement_percent": 100,
    }
    for name, target in required_metrics.items():
        if metrics.get(name) != target:
            failures.append(f"output-quality metric {name} must equal {target}")

    surfaces = contract.get("output_quality", {}).get("artifact_surfaces", {})
    if set(surfaces) != {"pptx", "docx", "xlsx", "pdf_svg_html"}:
        failures.append("all four governed artifact surface groups are required")
    if "opens_without_repair_warning" not in surfaces.get("pptx", []):
        failures.append("PPTX repair-warning acceptance is missing")
    if "formulas_remain_formulas" not in surfaces.get("xlsx", []):
        failures.append("XLSX formula editability acceptance is missing")

    readiness = contract.get("readiness_snapshot", {})
    if readiness.get("chat_first_scope_complete") is not True:
        failures.append("chat-first scope must be complete")
    for key in (
        "release_integration_complete",
        "issue_19_hosted_controls_verified",
        "clean_macos_environment_verified",
        "explicit_founder_phase_0_approval_received",
        "codex_start_authorized",
    ):
        if readiness.get(key) is not False:
            failures.append(
                f"{key} must remain false before the governed integration and Founder gates"
            )
    if readiness.get("pcr10_merge_required") is not True:
        failures.append("PCR-10 merge must remain required")

    generated = contract.get("generated_issue", {})
    if generated.get("github_issue_sync_verified") is not False:
        failures.append("offline contract must not claim hosted issue synchronization")

    if FINAL_BODY_PATH.is_file():
        actual_body_sha = hashlib.sha256(
            FINAL_BODY_PATH.read_text(encoding="utf-8").encode("utf-8")
        ).hexdigest()
        if generated.get("body_sha256") != actual_body_sha:
            failures.append("generated issue body digest does not match the final body")

    if check_files:
        builder = _load_builder()
        expected_contract, expected_body = builder.build_contract()
        if contract != expected_contract:
            failures.append("PCR-10 contract is stale")
        if (
            not FINAL_BODY_PATH.is_file()
            or FINAL_BODY_PATH.read_text(encoding="utf-8") != expected_body
        ):
            failures.append("PCR-10 final issue body is stale")
        body = (
            FINAL_BODY_PATH.read_text(encoding="utf-8")
            if FINAL_BODY_PATH.is_file()
            else ""
        )
        for token in (
            "pcr10_merged_to_main",
            "contracts/pre-codex-readiness.json",
            "scripts/validate_pcr10_pre_codex_readiness.py",
            "100 percent of material citations",
            "support-bundle",
            "Codex Phase 0 only",
        ):
            if token not in body:
                failures.append(f"final issue body is missing token: {token}")
        for path in (PCR09_CONTRACT_PATH, HANDOFF_PATH, DOC_PATH):
            if not path.is_file():
                failures.append(f"required path is missing: {path.relative_to(ROOT)}")
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        tracked = result.stdout.splitlines()
        for path in tracked:
            if any(pattern in path for pattern in PROHIBITED_TRACKED_PATTERNS):
                failures.append(
                    f"prohibited transfer or materialization path is tracked: {path}"
                )

    return failures


def _run_mutation_cases(contract: dict[str, Any]) -> int:
    mutations: list[dict[str, Any]] = []

    mutation = copy.deepcopy(contract)
    mutation["activation_conditions"].remove("pcr10_merged_to_main")
    mutations.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["activation_conditions"].append("unexpected_activation")
    mutations.append(mutation)

    for boundary in (
        "codex_start_authorized",
        "real_client_data_enabled",
        "external_actions_authorized",
    ):
        mutation = copy.deepcopy(contract)
        mutation["boundaries"][boundary] = True
        mutations.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["boundaries"]["founder_accountability_preserved"] = False
    mutations.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["developer_experience"]["phase0_required_commands"].remove("doctor")
    mutations.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["developer_experience"]["phase0_required_commands"].append("up")
    mutations.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["quality_registry"]["criterion_ids"][1] = mutation[
        "quality_registry"
    ]["criterion_ids"][0]
    mutations.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["quality_registry"]["criterion_count"] -= 1
    mutations.append(mutation)

    for section, index, target in (
        ("evidence", 0, 99),
        ("evidence", 1, 1),
        ("quantitative", 0, 99),
        ("quantitative", 1, 1),
    ):
        mutation = copy.deepcopy(contract)
        mutation["output_quality"][section][index]["target"] = target
        mutations.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["output_quality"]["artifact_surfaces"].pop("pptx")
    mutations.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["output_quality"]["artifact_surfaces"]["xlsx"].remove(
        "formulas_remain_formulas"
    )
    mutations.append(mutation)

    for readiness_field in (
        "release_integration_complete",
        "issue_19_hosted_controls_verified",
        "clean_macos_environment_verified",
        "explicit_founder_phase_0_approval_received",
    ):
        mutation = copy.deepcopy(contract)
        mutation["readiness_snapshot"][readiness_field] = True
        mutations.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["readiness_snapshot"]["pcr10_merge_required"] = False
    mutations.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["generated_issue"]["github_issue_sync_verified"] = True
    mutations.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["generated_issue"]["body_sha256"] = "0" * 64
    mutations.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["release_integrity"]["critical_or_high_defects_allowed"] = 1
    mutations.append(mutation)

    mutation = copy.deepcopy(contract)
    mutation["authority"]["final_pre_start_gate_owner"] = "PCR-09"
    mutations.append(mutation)

    schema = _load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    for index, mutation in enumerate(mutations, start=1):
        schema_errors = list(validator.iter_errors(mutation))
        semantic_errors = semantic_failures(mutation, check_files=False)
        if not schema_errors and not semantic_errors:
            raise SystemExit(f"PCR-10 mutation case {index} was not rejected")
    return len(mutations)


def main() -> None:
    contract = _load_json(CONTRACT_PATH)
    schema = _load_json(SCHEMA_PATH)
    schema_errors = sorted(
        Draft202012Validator(schema).iter_errors(contract),
        key=lambda error: list(error.absolute_path),
    )
    if schema_errors:
        raise SystemExit(
            "PCR-10 schema validation failed:\n- "
            + "\n- ".join(error.message for error in schema_errors)
        )
    failures = semantic_failures(contract)
    if failures:
        raise SystemExit("PCR-10 semantic validation failed:\n- " + "\n- ".join(failures))
    mutation_count = _run_mutation_cases(contract)
    print(
        "PCR-10 pre-Codex release and quality acceptance passed: "
        f"{len(contract['activation_conditions'])} activation conditions, "
        f"{contract['quality_registry']['criterion_count']} criteria, "
        f"{contract['quality_registry']['developer_command_count']} commands, "
        f"{mutation_count} mutation cases rejected, "
        "chat_first_scope_complete=true, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
