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
BUILD_SCRIPT = ROOT / "scripts" / "build_pcr04_codex_handoff.py"
HANDOFF_PATH = ROOT / "handoff" / "codex-phase0-handoff.json"
SCHEMA_PATH = ROOT / "schemas" / "codex-handoff.schema.json"
KICKOFF_PATH = ROOT / "docs" / "14-CODEX-KICKOFF.md"
ADDENDUM_PATH = ROOT / "docs" / "19-PHASE-0-VALIDATION-ADDENDUM.md"

EXPECTED_TASKS = {"P0.1", "P0.2", "P0.3", "P0.4"}
EXPECTED_ACTIVATION_CONDITIONS = {
    "pcr03_merged_to_main",
    "pcr04_merged_to_main",
    "pcr05_merged_to_main",
    "pcr06_merged_to_main",
    "pcr07_merged_to_main",
    "pcr08_merged_to_main",
    "github_hosted_controls_in_issue_19_verified",
    "explicit_founder_phase_0_approval_received",
    "clean_macos_environment_available",
}
REQUIRED_DOCUMENT_TOKENS = {
    "handoff/codex-phase0-handoff.json",
    "scripts/validate_pcr04_codex_handoff.py",
    "scripts/validate_pcr05_runtime_adapters.py",
    "contracts/runtime-adapter-contracts.json",
    "scripts/validate_pcr06_hermes_compatibility.py",
    "contracts/hermes-compatibility-pack.json",
    "scripts/validate_pcr07_northstar_blueprint.py",
    "contracts/northstar-integration-blueprint.json",
    "scripts/validate_pcr08_initial_operating_controls.py",
    "contracts/initial-operating-controls.json",
    "codex/phase-0-foundation",
}
ROOT_PYTEST_COMMAND = (
    "cd packages/offdata-core && pytest --cov=offdata_core "
    "--cov-report=term-missing --cov-fail-under=90"
)
ROOT_MYPY_COMMAND = "cd packages/offdata-core && mypy src"


def _load_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("pcr04_builder", BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load PCR-04 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _referenced_paths(handoff: dict[str, Any]) -> set[str]:
    paths: set[str] = set()

    read_order = handoff.get("read_order", [])
    if isinstance(read_order, list):
        paths.update(item for item in read_order if isinstance(item, str))

    prerequisites = handoff.get("prerequisite_records", [])
    if isinstance(prerequisites, list):
        for item in prerequisites:
            if isinstance(item, dict):
                for field in ("path", "validator"):
                    value = item.get(field)
                    if isinstance(value, str):
                        paths.add(value)

    assets = handoff.get("existing_assets", {})
    if isinstance(assets, dict):
        for values in assets.values():
            if isinstance(values, list):
                paths.update(item for item in values if isinstance(item, str))

    return paths


def _command_paths(handoff: dict[str, Any]) -> set[str]:
    paths: set[str] = set()
    execution = handoff.get("execution", {})
    if not isinstance(execution, dict):
        return paths
    commands = execution.get("required_commands", [])
    if not isinstance(commands, list):
        return paths
    for command in commands:
        if not isinstance(command, str):
            continue
        parts = shlex.split(command)
        if len(parts) >= 2 and parts[0] == "python" and parts[1].endswith(".py"):
            paths.add(parts[1])
    return paths


def _cycle_nodes(tasks: list[dict[str, Any]]) -> set[str]:
    dependencies = {
        str(task.get("id")): {
            str(item)
            for item in task.get("dependencies", [])
            if isinstance(item, str)
        }
        for task in tasks
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
            visit(dependency)
            if dependency in cycles:
                cycles.add(task_id)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in dependencies:
        visit(task_id)
    return cycles


def semantic_failures(
    handoff: dict[str, Any], *, check_paths: bool = True
) -> list[str]:
    failures: list[str] = []

    if "stacked_base_branch" in handoff:
        failures.append(
            "transient stacked pull-request metadata must not enter the canonical handoff"
        )

    target = handoff.get("target")
    if not isinstance(target, dict):
        failures.append("target is missing")
    else:
        if target.get("phase_number") != 0:
            failures.append("only Phase 0 may be authorised")
        if target.get("maximum_authorised_phase") != 0:
            failures.append("maximum authorised phase must remain 0")
        if target.get("next_phase_is_prohibited") is not True:
            failures.append("progression beyond Phase 0 must remain prohibited")
        if target.get("start_requires_explicit_founder_approval") is not True:
            failures.append("Phase 0 start must require explicit Founder approval")

    authority = handoff.get("authority")
    if not isinstance(authority, dict) or authority.get("controlling_instruction") != "AGENTS.md":
        failures.append("AGENTS.md must remain the controlling instruction")

    tasks = handoff.get("task_graph")
    if not isinstance(tasks, list):
        failures.append("task graph is missing")
        tasks = []
    task_ids = [task.get("id") for task in tasks if isinstance(task, dict)]
    if set(task_ids) != EXPECTED_TASKS or len(task_ids) != len(EXPECTED_TASKS):
        failures.append("task graph must contain each P0.1-P0.4 task exactly once")
    known = set(item for item in task_ids if isinstance(item, str))
    for task in tasks:
        if not isinstance(task, dict):
            failures.append("task entries must be objects")
            continue
        dependencies = task.get("dependencies")
        if not isinstance(dependencies, list):
            failures.append(f"{task.get('id')} dependencies must be a list")
            continue
        unknown = sorted(set(dependencies) - known)
        if unknown:
            failures.append(f"{task.get('id')} has unknown dependencies: {unknown}")
        if task.get("id") in dependencies:
            failures.append(f"{task.get('id')} cannot depend on itself")
    cycles = sorted(_cycle_nodes([item for item in tasks if isinstance(item, dict)]))
    if cycles:
        failures.append(f"task dependency cycle detected: {cycles}")

    boundaries = handoff.get("boundaries")
    if not isinstance(boundaries, dict):
        failures.append("boundaries are missing")
    else:
        for field in (
            "real_client_data_enabled",
            "external_actions_authorised",
            "paid_services_authorised",
            "production_deployment_authorised",
            "autonomous_merge_authorised",
            "original_methodology_binaries_committed",
        ):
            if boundaries.get(field) is not False:
                failures.append(f"{field} must remain false")
        if boundaries.get("founder_accountability_preserved") is not True:
            failures.append("Founder accountability must remain preserved")

    readiness = handoff.get("readiness_snapshot")
    if not isinstance(readiness, dict):
        failures.append("readiness snapshot is missing")
    else:
        if readiness.get("local_prerequisites_passed") is not True:
            failures.append("local prerequisite records must pass")
        if readiness.get("codex_start_authorized") is not False:
            failures.append("PCR-04 must not autonomously authorise Codex start")
        runtime = readiness.get("runtime_adapters")
        if not isinstance(runtime, dict) or runtime.get("passed") is not True:
            failures.append("PCR-05 runtime adapter prerequisite must pass")
        elif runtime.get("runtime_activation_authorized") is not False:
            failures.append("PCR-05 runtime activation must remain false")
        hermes = readiness.get("hermes_compatibility")
        if not isinstance(hermes, dict) or hermes.get("passed") is not True:
            failures.append("PCR-06 Hermes compatibility prerequisite must pass")
        elif hermes.get("hermes_activation_authorized") is not False:
            failures.append("PCR-06 Hermes activation must remain false")
        northstar = readiness.get("northstar_blueprint")
        if not isinstance(northstar, dict) or northstar.get("passed") is not True:
            failures.append("PCR-07 Northstar blueprint prerequisite must pass")
        elif northstar.get("northstar_implementation_authorized") is not False:
            failures.append("PCR-07 Northstar implementation must remain false")
        operating = readiness.get("initial_operating_controls")
        if not isinstance(operating, dict) or operating.get("passed") is not True:
            failures.append("PCR-08 initial operating-control prerequisite must pass")
        else:
            if operating.get("initial_operating_controls_activation_authorized") is not False:
                failures.append("PCR-08 operating controls must remain inactive")
            if operating.get("hosted_control_evidence_complete") is not False:
                failures.append("PCR-08 hosted evidence must remain incomplete")
            if operating.get("operating_environment_evidence_complete") is not False:
                failures.append("PCR-08 operating evidence must remain incomplete")
            if operating.get("production_evidence_complete") is not False:
                failures.append("PCR-08 production evidence must remain incomplete")
        blockers = readiness.get("activation_blockers")
        if not isinstance(blockers, list) or set(blockers) != EXPECTED_ACTIVATION_CONDITIONS:
            failures.append("activation blockers do not match the governed conditions")

    activation = handoff.get("activation_conditions")
    if not isinstance(activation, list) or set(activation) != EXPECTED_ACTIVATION_CONDITIONS:
        failures.append("activation conditions are incomplete or changed")

    execution = handoff.get("execution")
    if not isinstance(execution, dict):
        failures.append("execution contract is missing")
    else:
        if execution.get("branch_name") != "codex/phase-0-foundation":
            failures.append("Codex Phase 0 branch name is not canonical")
        if execution.get("pull_request_mode") != "draft":
            failures.append("Codex must open a draft pull request")
        if execution.get("merge_requires_founder_approval") is not True:
            failures.append("merge must require Founder approval")
        commands = execution.get("required_commands")
        if not isinstance(commands, list):
            failures.append("required command list is missing")
        else:
            if "python scripts/validate_pcr04_codex_handoff.py" not in commands:
                failures.append("PCR-04 validation command is missing")
            if "python scripts/validate_pcr05_runtime_adapters.py" not in commands:
                failures.append("PCR-05 validation command is missing")
            if "python scripts/validate_pcr06_hermes_compatibility.py" not in commands:
                failures.append("PCR-06 validation command is missing")
            if "python scripts/validate_pcr07_northstar_blueprint.py" not in commands:
                failures.append("PCR-07 validation command is missing")
            if "python scripts/validate_pcr08_initial_operating_controls.py" not in commands:
                failures.append("PCR-08 validation command is missing")
            if ROOT_PYTEST_COMMAND not in commands:
                failures.append("root-executable package test command is missing")
            if ROOT_MYPY_COMMAND not in commands:
                failures.append("root-executable package MyPy command is missing")
            if any(
                command.startswith("pytest ") or command == "mypy src"
                for command in commands
            ):
                failures.append("package commands must declare their working directory")

    if check_paths:
        for relative in sorted(_referenced_paths(handoff) | _command_paths(handoff)):
            if not (ROOT / relative).exists():
                failures.append(f"referenced path does not exist: {relative}")

        for path in (KICKOFF_PATH, ADDENDUM_PATH):
            text = path.read_text(encoding="utf-8")
            for token in REQUIRED_DOCUMENT_TOKENS:
                if token not in text:
                    failures.append(f"{path.relative_to(ROOT)} is missing token: {token}")

    return failures


def _run_mutation_cases(handoff: dict[str, Any]) -> int:
    mutations: list[dict[str, Any]] = []

    phase_mutation = copy.deepcopy(handoff)
    phase_mutation["target"]["phase_number"] = 1
    mutations.append(phase_mutation)

    authority_mutation = copy.deepcopy(handoff)
    authority_mutation["readiness_snapshot"]["codex_start_authorized"] = True
    mutations.append(authority_mutation)

    boundary_mutation = copy.deepcopy(handoff)
    boundary_mutation["boundaries"]["external_actions_authorised"] = True
    mutations.append(boundary_mutation)

    duplicate_mutation = copy.deepcopy(handoff)
    duplicate_mutation["task_graph"][3]["id"] = "P0.3"
    mutations.append(duplicate_mutation)

    cycle_mutation = copy.deepcopy(handoff)
    cycle_mutation["task_graph"][0]["dependencies"] = ["P0.4"]
    mutations.append(cycle_mutation)

    command_mutation = copy.deepcopy(handoff)
    command_mutation["execution"]["required_commands"].remove(
        "python scripts/validate_pcr04_codex_handoff.py"
    )
    mutations.append(command_mutation)

    working_directory_mutation = copy.deepcopy(handoff)
    commands = working_directory_mutation["execution"]["required_commands"]
    commands[commands.index(ROOT_PYTEST_COMMAND)] = (
        "pytest --cov=offdata_core --cov-report=term-missing --cov-fail-under=90"
    )
    mutations.append(working_directory_mutation)

    transient_metadata_mutation = copy.deepcopy(handoff)
    transient_metadata_mutation["stacked_base_branch"] = "temporary/stacked-branch"
    mutations.append(transient_metadata_mutation)

    runtime_command_mutation = copy.deepcopy(handoff)
    runtime_command_mutation["execution"]["required_commands"].remove(
        "python scripts/validate_pcr05_runtime_adapters.py"
    )
    mutations.append(runtime_command_mutation)

    runtime_activation_mutation = copy.deepcopy(handoff)
    runtime_activation_mutation["readiness_snapshot"]["runtime_adapters"][
        "runtime_activation_authorized"
    ] = True
    mutations.append(runtime_activation_mutation)

    hermes_activation_mutation = copy.deepcopy(handoff)
    hermes_activation_mutation["readiness_snapshot"]["hermes_compatibility"][
        "hermes_activation_authorized"
    ] = True
    mutations.append(hermes_activation_mutation)

    northstar_activation_mutation = copy.deepcopy(handoff)
    northstar_activation_mutation["readiness_snapshot"]["northstar_blueprint"][
        "northstar_implementation_authorized"
    ] = True
    mutations.append(northstar_activation_mutation)

    operating_activation_mutation = copy.deepcopy(handoff)
    operating_activation_mutation["readiness_snapshot"]["initial_operating_controls"][
        "initial_operating_controls_activation_authorized"
    ] = True
    mutations.append(operating_activation_mutation)

    operating_evidence_mutation = copy.deepcopy(handoff)
    operating_evidence_mutation["readiness_snapshot"]["initial_operating_controls"][
        "production_evidence_complete"
    ] = True
    mutations.append(operating_evidence_mutation)

    pcr08_command_mutation = copy.deepcopy(handoff)
    pcr08_command_mutation["execution"]["required_commands"].remove(
        "python scripts/validate_pcr08_initial_operating_controls.py"
    )
    mutations.append(pcr08_command_mutation)

    for index, mutation in enumerate(mutations, start=1):
        if not semantic_failures(mutation, check_paths=False):
            raise SystemExit(f"PCR-04 mutation case {index} was not rejected")
    return len(mutations)


def main() -> None:
    if not HANDOFF_PATH.is_file():
        raise SystemExit("PCR-04 handoff is missing")

    handoff = _load_json(HANDOFF_PATH)
    schema = _load_json(SCHEMA_PATH)
    schema_errors = sorted(
        Draft202012Validator(schema).iter_errors(handoff),
        key=lambda error: list(error.absolute_path),
    )
    if schema_errors:
        messages = [error.message for error in schema_errors]
        raise SystemExit("PCR-04 schema validation failed:\n- " + "\n- ".join(messages))

    builder = _load_builder()
    expected = builder.build_handoff()
    if handoff != expected:
        raise SystemExit(
            "PCR-04 handoff is stale; run scripts/build_pcr04_codex_handoff.py "
            "and review the diff"
        )

    failures = semantic_failures(handoff)
    if failures:
        raise SystemExit("PCR-04 validation failed:\n- " + "\n- ".join(failures))

    mutation_count = _run_mutation_cases(handoff)
    readiness = handoff["readiness_snapshot"]
    print(
        "PCR-04 machine-readable Codex handoff passed: "
        f"{len(handoff['task_graph'])} Phase 0 tasks, "
        f"{len(handoff['read_order'])} read-order files, "
        f"{len(handoff['activation_conditions'])} activation conditions, "
        f"{mutation_count} mutation cases rejected, "
        f"local_prerequisites_passed={str(readiness['local_prerequisites_passed']).lower()}, "
        "codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
