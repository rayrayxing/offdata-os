from __future__ import annotations

import copy
import importlib.util
import json
import shlex
from pathlib import Path
from types import ModuleType
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BUILD_PATH = ROOT / "scripts" / "build_ws61_codex_handoff.py"
HANDOFF_PATH = ROOT / "handoff" / "codex-phase0-handoff.json"
SCHEMA_PATH = ROOT / "schemas" / "codex-handoff.schema.json"
DOC_PATH = ROOT / "docs" / "53-WS6-1-CONTROLLING-MACHINE-HANDOFF-RECONCILIATION.md"

EXPECTED_TASKS = ["P0.1", "P0.2", "P0.3", "P0.4"]
EXPECTED_ACTIVATION = [
    "pcr03_merged_to_main",
    "pcr04_merged_to_main",
    "pcr05_merged_to_main",
    "pcr06_merged_to_main",
    "pcr07_merged_to_main",
    "pcr08_merged_to_main",
    "pcr09_merged_to_main",
    "pcr10_merged_to_main",
    "workstream4_repository_package_merged_to_main",
    "workstream5_launch_control_merged_to_main",
    "workstream6_final_reconciliation_merged_to_main",
    "github_hosted_controls_in_issue_19_verified",
    "clean_macos_environment_available",
    "explicit_founder_phase_0_approval_received",
    "valid_codex_phase0_launch_permit_issued",
]
EXPECTED_PREREQUISITES = [
    "canonical_chat_first_release",
    "test_identity_and_referential_integrity",
    "repository_and_governance_hygiene",
    "runtime_adapters",
    "hermes_compatibility",
    "northstar_integration_blueprint",
    "initial_operating_controls",
    "first_codex_issue_rewrite",
    "pre_codex_readiness",
    "workstream4_readiness",
    "workstream5_launch_control",
    "workstream6_baseline_lock",
    "workstream6_handoff_reconciliation",
    "codex_handoff",
]
REQUIRED_READ_ORDER = {
    "docs/49-PCR-10-PRE-CODEX-RELEASE-AND-QUALITY-ACCEPTANCE.md",
    "contracts/pre-codex-readiness.json",
    "docs/50-WORKSTREAM-4-HOSTED-CONTROLS-EVIDENCE-AND-ENVIRONMENT-READINESS.md",
    "contracts/workstream4-readiness.json",
    "docs/51-WORKSTREAM-5-CODEX-PHASE-0-LAUNCH-CONTROL.md",
    "contracts/codex-phase0-launch-control.json",
    "docs/52-WORKSTREAM-6-FINAL-PRE-CODEX-RECONCILIATION.md",
    "contracts/workstream6-final-reconciliation.json",
    "docs/53-WS6-1-CONTROLLING-MACHINE-HANDOFF-RECONCILIATION.md",
    "contracts/workstream6-handoff-reconciliation.json",
    "schemas/codex-phase0-launch-permit.schema.json",
    "scripts/prepare_codex_phase0_launch.py",
    "scripts/require_workstream6_final_reconciliation.py",
}
REQUIRED_COMMANDS = {
    "python scripts/build_pcr10_pre_codex_readiness.py",
    "python scripts/build_workstream4_readiness.py",
    "python scripts/build_workstream5_launch_control.py",
    "python scripts/build_workstream6_final_reconciliation.py",
    "python scripts/build_workstream6_handoff_reconciliation.py",
    "python scripts/build_pcr04_codex_handoff.py",
    "python scripts/validate_pcr10_pre_codex_readiness.py",
    "python scripts/validate_workstream4_readiness.py",
    "python scripts/validate_workstream5_launch_control.py",
    "python scripts/validate_workstream6_final_reconciliation.py",
    "python scripts/validate_workstream6_handoff_reconciliation.py",
    "python scripts/validate_pcr04_codex_handoff.py",
    "python scripts/prepare_codex_phase0_launch.py --self-test",
    "python scripts/require_workstream6_final_reconciliation.py",
    "git diff --exit-code",
    "cd packages/offdata-core && pytest --cov=offdata_core --cov-report=term-missing --cov-fail-under=90",
    "python -m compileall -q packages/offdata-core/src packages/offdata-core/tests scripts",
    "ruff check --config packages/offdata-core/pyproject.toml packages/offdata-core/src packages/offdata-core/tests scripts",
    "cd packages/offdata-core && mypy src",
}
P0_3_SCOPE = "existing_cf_p1_to_p7_pcr_01_to_10_ws4_ws5_and_final_ws6_gates_remain_green"
FINAL_GATE_COMMAND = "python scripts/require_workstream6_final_reconciliation.py"


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ws61_handoff_builder", BUILD_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load WS6.1 handoff builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _referenced_paths(handoff: dict[str, Any]) -> set[str]:
    paths = set(handoff.get("read_order", []))
    for item in handoff.get("prerequisite_records", []):
        if isinstance(item, dict):
            paths.update(
                value
                for field in ("path", "validator")
                if isinstance((value := item.get(field)), str)
            )
    for values in handoff.get("existing_assets", {}).values():
        if isinstance(values, list):
            paths.update(value for value in values if isinstance(value, str))
    for command in handoff.get("execution", {}).get("required_commands", []):
        if not isinstance(command, str):
            continue
        parts = shlex.split(command)
        if len(parts) >= 2 and parts[0] == "python" and parts[1].endswith(".py"):
            paths.add(parts[1])
    return paths


def _task_cycles(tasks: list[dict[str, Any]]) -> set[str]:
    dependencies = {
        str(task.get("id")): set(task.get("dependencies", [])) for task in tasks
    }
    visiting: set[str] = set()
    visited: set[str] = set()
    cycles: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            cycles.add(task_id)
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in dependencies.get(task_id, set()):
            visit(str(dependency))
            if dependency in cycles:
                cycles.add(task_id)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in dependencies:
        visit(task_id)
    return cycles


def semantic_failures(
    handoff: dict[str, Any], *, check_files: bool = True, check_generated: bool = True
) -> list[str]:
    failures: list[str] = []
    if handoff.get("schema_version") != 2:
        failures.append("handoff schema version must be 2")
    if handoff.get("phase_id") != "PCR-04" or handoff.get("reconciled_by") != "WS6.1":
        failures.append("handoff must be PCR-04 reconciled by WS6.1")
    if handoff.get("repository") != "rayrayxing/offdata-os":
        failures.append("repository is incorrect")
    if handoff.get("canonical_branch") != "main":
        failures.append("canonical branch must be main")

    target = handoff.get("target", {})
    if target.get("phase_number") != 0 or target.get("maximum_authorised_phase") != 0:
        failures.append("only Phase 0 may be authorised")
    if target.get("next_phase_is_prohibited") is not True:
        failures.append("progression beyond Phase 0 must remain prohibited")
    if target.get("start_requires_explicit_founder_approval") is not True:
        failures.append("explicit Founder approval is required")
    if target.get("start_requires_valid_launch_permit") is not True:
        failures.append("a valid launch permit is required")
    if target.get("start_requires_final_workstream6_reconciliation") is not True:
        failures.append("final Workstream 6 reconciliation is required")

    authority = handoff.get("authority", {})
    if authority.get("controlling_instruction") != "AGENTS.md":
        failures.append("AGENTS.md must remain controlling")
    if authority.get("final_workstream6_gate") != (
        "scripts/require_workstream6_final_reconciliation.py"
    ):
        failures.append("final Workstream 6 gate path is incorrect")

    if handoff.get("activation_conditions") != EXPECTED_ACTIVATION:
        failures.append("activation conditions must be the exact WS6 sequence")

    prerequisite_ids = [
        item.get("id") for item in handoff.get("prerequisite_records", [])
        if isinstance(item, dict)
    ]
    if prerequisite_ids != EXPECTED_PREREQUISITES:
        failures.append("prerequisite records must include PCR-10 and WS4-WS6 in order")

    read_order = handoff.get("read_order", [])
    if not isinstance(read_order, list) or len(read_order) != len(set(read_order)):
        failures.append("read order must be a unique list")
    missing_read = sorted(REQUIRED_READ_ORDER - set(read_order))
    if missing_read:
        failures.append(f"read order is missing final records: {missing_read}")

    tasks = handoff.get("task_graph", [])
    task_ids = [task.get("id") for task in tasks if isinstance(task, dict)]
    if task_ids != EXPECTED_TASKS:
        failures.append("task graph must contain P0.1-P0.4 in order")
    if _task_cycles([task for task in tasks if isinstance(task, dict)]):
        failures.append("task graph contains a dependency cycle")
    p03 = next((task for task in tasks if task.get("id") == "P0.3"), {})
    if P0_3_SCOPE not in p03.get("acceptance", []):
        failures.append("P0.3 regression scope stops before final Workstream 6")
    if (
        "valid_launch_permit_and_exact_approved_main_sha_are_verified_before_branch_creation"
        not in p03.get("acceptance", [])
    ):
        failures.append("P0.3 must verify permit and exact approved main SHA")

    execution = handoff.get("execution", {})
    if execution.get("branch_name") != "codex/phase-0-foundation":
        failures.append("Codex branch name is not canonical")
    if execution.get("pull_request_mode") != "draft":
        failures.append("Codex pull request must be draft")
    if execution.get("merge_requires_founder_approval") is not True:
        failures.append("merge must require Founder approval")
    if execution.get("launch_permit_required") is not True:
        failures.append("execution must require a launch permit")
    if execution.get("launch_permit_path") != ".local/codex-phase0-launch/permit.json":
        failures.append("launch permit path is incorrect")
    if execution.get("final_workstream6_gate_command") != FINAL_GATE_COMMAND:
        failures.append("final Workstream 6 gate command is incorrect")
    commands = execution.get("required_commands", [])
    if not isinstance(commands, list) or len(commands) != len(set(commands)):
        failures.append("required commands must be a unique list")
    missing_commands = sorted(REQUIRED_COMMANDS - set(commands))
    if missing_commands:
        failures.append(f"required commands are missing: {missing_commands}")
    if any(command.startswith("pytest ") or command == "mypy src" for command in commands):
        failures.append("package commands must declare their working directory")

    boundaries = handoff.get("boundaries", {})
    if boundaries.get("founder_accountability_preserved") is not True:
        failures.append("Founder accountability must remain preserved")
    for key, value in boundaries.items():
        if key != "founder_accountability_preserved" and value is not False:
            failures.append(f"boundary {key} must remain false")

    readiness = handoff.get("readiness_snapshot", {})
    for name in (
        "canonical_release",
        "referential_integrity",
        "repository_governance",
        "runtime_adapters",
        "hermes_compatibility",
        "northstar_blueprint",
        "initial_operating_controls",
        "pre_codex_readiness",
        "workstream4_readiness",
        "workstream5_launch_control",
        "workstream6_baseline_lock",
        "workstream6_handoff_reconciliation",
    ):
        if readiness.get(name, {}).get("passed") is not True:
            failures.append(f"repository prerequisite {name} must pass")
    if readiness.get("local_prerequisites_passed") is not True:
        failures.append("local repository prerequisites must pass")
    for field in (
        "final_workstream6_gate_complete",
        "hosted_controls_verified",
        "clean_macos_environment_verified",
        "explicit_founder_phase0_approval_received",
        "launch_permit_issued",
        "codex_start_authorized",
    ):
        if readiness.get(field) is not False:
            failures.append(f"readiness field {field} must remain false")
    activation_status = readiness.get("activation_status", {})
    if set(activation_status) != set(EXPECTED_ACTIVATION):
        failures.append("activation status must cover the exact activation conditions")
    for condition in EXPECTED_ACTIVATION[:10]:
        if activation_status.get(condition) is not True:
            failures.append(f"merged repository condition {condition} must be true")
    for condition in EXPECTED_ACTIVATION[10:]:
        if activation_status.get(condition) is not False:
            failures.append(f"pending condition {condition} must remain false")
    if readiness.get("activation_blockers") != EXPECTED_ACTIVATION[10:]:
        failures.append("activation blockers must be the five remaining gates")

    if check_files:
        for relative in sorted(_referenced_paths(handoff)):
            if not (ROOT / relative).exists():
                failures.append(f"referenced path does not exist: {relative}")
        document = DOC_PATH.read_text(encoding="utf-8") if DOC_PATH.is_file() else ""
        for token in (
            "WS6.1",
            "WS6-BLOCK-001",
            "WS6-BLOCK-002",
            "valid_codex_phase0_launch_permit_issued",
            "codex_start_authorized=false",
        ):
            if token not in document:
                failures.append(f"WS6.1 document is missing token: {token}")

    if check_generated:
        expected = _builder().build_handoff()
        if handoff != expected:
            failures.append("generated handoff is stale")
    return failures


def _mutation_count(handoff: dict[str, Any]) -> int:
    cases: list[dict[str, Any]] = []

    def add(mutator: Any) -> None:
        mutation = copy.deepcopy(handoff)
        mutator(mutation)
        cases.append(mutation)

    add(lambda item: item["target"].__setitem__("phase_number", 1))
    add(lambda item: item["target"].__setitem__("start_requires_valid_launch_permit", False))
    add(lambda item: item["target"].__setitem__("start_requires_final_workstream6_reconciliation", False))
    add(lambda item: item["activation_conditions"].remove("pcr10_merged_to_main"))
    add(lambda item: item["activation_conditions"].remove("workstream4_repository_package_merged_to_main"))
    add(lambda item: item["activation_conditions"].remove("workstream5_launch_control_merged_to_main"))
    add(lambda item: item["activation_conditions"].remove("workstream6_final_reconciliation_merged_to_main"))
    add(lambda item: item["activation_conditions"].remove("valid_codex_phase0_launch_permit_issued"))
    add(lambda item: item["prerequisite_records"].pop(8))
    add(lambda item: item["prerequisite_records"].pop(9))
    add(lambda item: item["prerequisite_records"].pop(10))
    add(lambda item: item["prerequisite_records"].pop(11))
    add(lambda item: item["prerequisite_records"].pop(12))
    add(lambda item: item["read_order"].remove("contracts/pre-codex-readiness.json"))
    add(lambda item: item["read_order"].remove("contracts/workstream4-readiness.json"))
    add(lambda item: item["read_order"].remove("contracts/workstream5-launch-control.json") if "contracts/workstream5-launch-control.json" in item["read_order"] else item["read_order"].remove("contracts/codex-phase0-launch-control.json"))
    add(lambda item: item["read_order"].remove("contracts/workstream6-final-reconciliation.json"))
    add(lambda item: item["execution"]["required_commands"].remove("python scripts/validate_pcr10_pre_codex_readiness.py"))
    add(lambda item: item["execution"]["required_commands"].remove("python scripts/validate_workstream4_readiness.py"))
    add(lambda item: item["execution"]["required_commands"].remove("python scripts/validate_workstream5_launch_control.py"))
    add(lambda item: item["execution"]["required_commands"].remove("python scripts/validate_workstream6_final_reconciliation.py"))
    add(lambda item: item["execution"]["required_commands"].remove(FINAL_GATE_COMMAND))
    add(lambda item: item["execution"].__setitem__("launch_permit_required", False))
    add(lambda item: item["task_graph"][2]["acceptance"].remove(P0_3_SCOPE))
    add(lambda item: item["boundaries"].__setitem__("phase0_implementation_authorised", True))
    add(lambda item: item["readiness_snapshot"].__setitem__("codex_start_authorized", True))
    add(lambda item: item["readiness_snapshot"].__setitem__("launch_permit_issued", True))
    add(lambda item: item["readiness_snapshot"].__setitem__("final_workstream6_gate_complete", True))

    schema = _load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    for index, mutation in enumerate(cases, start=1):
        schema_errors = list(validator.iter_errors(mutation))
        semantic_errors = semantic_failures(
            mutation, check_files=False, check_generated=False
        )
        if not schema_errors and not semantic_errors:
            raise SystemExit(f"WS6.1 handoff mutation {index} was not rejected")
    return len(cases)


def main() -> None:
    handoff = _load_json(HANDOFF_PATH)
    schema = _load_json(SCHEMA_PATH)
    schema_errors = sorted(
        Draft202012Validator(schema).iter_errors(handoff),
        key=lambda error: list(error.absolute_path),
    )
    if schema_errors:
        raise SystemExit(
            "WS6.1 handoff schema validation failed:\n- "
            + "\n- ".join(error.message for error in schema_errors)
        )
    failures = semantic_failures(handoff)
    if failures:
        raise SystemExit("WS6.1 handoff validation failed:\n- " + "\n- ".join(failures))
    mutation_count = _mutation_count(handoff)
    print(
        "WS6.1-reconciled PCR-04 handoff passed: "
        f"{len(handoff['prerequisite_records'])} prerequisites, "
        f"{len(handoff['read_order'])} read-order paths, "
        f"{len(handoff['execution']['required_commands'])} commands, "
        f"{mutation_count} mutations rejected, final_workstream6_gate_complete=false, "
        "launch_permit_issued=false, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
