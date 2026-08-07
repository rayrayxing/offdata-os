from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from build_workstream6_developer_experience_specification import (
    ACCEPTANCE_CLASSES,
    SOURCE,
    build_records,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "developer-experience-specification.json"
SCHEMA = ROOT / "schemas" / "developer-experience-specification.schema.json"
SPECIFICATION = ROOT / "docs" / "62-WS6-10-DEVELOPER-EXPERIENCE-SPECIFICATION.md"
REPORT = ROOT / "reports" / "workstream6-developer-experience-specification-evidence.md"
QUALITY = ROOT / "contracts" / "pre-codex-readiness.json"

EXPECTED_COMMANDS = (
    "doctor", "bootstrap", "up", "down", "restart", "health", "test", "lint",
    "format", "scan", "reset-synthetic", "backup", "restore", "clean",
    "support-bundle",
)
EXPECTED_FLAGS = (
    "--help", "--version", "--json", "--no-color", "--quiet", "--verbose",
    "--non-interactive", "--timeout-seconds", "--correlation-id",
)
EXPECTED_EXITS = (0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 130)
EXPECTED_IDEMPOTENCY = {
    "doctor": "read_only",
    "bootstrap": "convergent",
    "up": "convergent",
    "down": "convergent",
    "restart": "convergent",
    "health": "read_only",
    "test": "repeatable_artifact",
    "lint": "read_only",
    "format": "convergent",
    "scan": "repeatable_artifact",
    "reset-synthetic": "destructive_confirmed",
    "backup": "repeatable_artifact",
    "restore": "destructive_confirmed",
    "clean": "convergent",
    "support-bundle": "repeatable_artifact",
}
EXPECTED_NETWORK = {
    "bootstrap": "dependency_fetch_opt_in",
    "scan": "vulnerability_database_opt_in",
}


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def _load_source() -> dict[str, Any]:
    value = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("WS6.10 source must contain a mapping")
    return value


def _source_failures(value: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(value.get("work_package_id") == "WS6.10", "work package")
    predecessor = value.get("predecessor", {})
    require(predecessor.get("work_package_id") == "WS6.9", "predecessor package")
    require(
        predecessor.get("head_sha") == "911e431551bb7eb41f1d5d1ccc9ff042f18858f9",
        "predecessor head",
    )
    require(predecessor.get("integrated_to_main") is False, "predecessor honesty")
    surface = value.get("surface", {})
    require(surface.get("dispatcher") == "./offdata", "dispatcher")
    require(surface.get("working_directory") == "repository_root", "working directory")
    require(
        surface.get("implementation_status") == "specified_not_implemented",
        "surface status",
    )

    flags = value.get("global_flags", [])
    require(
        tuple(str(item).split(":", 1)[0] for item in flags)
        == EXPECTED_FLAGS,
        "global flags",
    )
    exits = value.get("exit_codes", [])
    require(
        tuple(item[0] for item in exits if isinstance(item, list) and item)
        == EXPECTED_EXITS,
        "exit codes",
    )

    commands = value.get("commands", [])
    if not isinstance(commands, list):
        commands = []
    names = tuple(item.get("name") for item in commands if isinstance(item, dict))
    require(names == EXPECTED_COMMANDS, "command identity and order")
    require(len(names) == len(set(names)) == 15, "command uniqueness")
    case_ids: list[str] = []
    for command in commands:
        if not isinstance(command, dict):
            failures.append("command object")
            continue
        name = str(command.get("name"))
        require(command.get("task") in {"P0.2", "P0.3", "P0.4"}, f"task: {name}")
        require(
            command.get("idempotency") == EXPECTED_IDEMPOTENCY.get(name),
            f"idempotency: {name}",
        )
        require(
            command.get("network") == EXPECTED_NETWORK.get(name, "denied"),
            f"network: {name}",
        )
        allowed = command.get("exits", [])
        require(
            isinstance(allowed, list)
            and len(allowed) == len(set(allowed))
            and set(allowed).issubset(EXPECTED_EXITS),
            f"allowed exits: {name}",
        )
        require(0 in allowed and 7 in allowed, f"success/safety exits: {name}")
        retry = command.get("retry", {})
        require(
            isinstance(retry.get("attempts"), int)
            and 1 <= retry["attempts"] <= 20,
            f"retry budget: {name}",
        )
        require(retry.get("state_recheck_required") is True, f"retry recheck: {name}")
        require(
            isinstance(retry.get("non_retryable"), list)
            and retry["non_retryable"],
            f"non-retryable: {name}",
        )
        if command.get("idempotency") == "destructive_confirmed":
            require(retry.get("attempts") == 1, f"destructive retry: {name}")
        criteria = command.get("criteria")
        require(
            isinstance(criteria, list)
            and len(criteria) >= 2
            and len(criteria) == len(set(criteria)),
            f"criteria: {name}",
        )
        case_exits = command.get("case_exits", {})
        require(
            isinstance(case_exits, dict)
            and tuple(case_exits) == ACCEPTANCE_CLASSES,
            f"case classes: {name}",
        )
        if isinstance(case_exits, dict):
            for acceptance_class in ACCEPTANCE_CLASSES:
                require(
                    case_exits.get(acceptance_class) in allowed,
                    f"case exit: {name}:{acceptance_class}",
                )
                case_ids.append(f"{name}:{acceptance_class}")
    require(len(case_ids) == len(set(case_ids)) == 60, "case identity")

    shared = value.get("shared_contracts", {})
    output = shared.get("output", {})
    require(output.get("human_json_parity") is True, "output parity")
    require(output.get("raw_exception_user_message") is False, "raw exceptions")
    redaction = shared.get("redaction", {})
    require(redaction.get("before_output") is True, "redaction timing")
    require(redaction.get("failure_exit") == 10, "redaction exit")
    paths = shared.get("paths", {})
    require(paths.get("resolve_first") is True, "path resolution")
    require(paths.get("reject_symlink_escape") is True, "symlink escape")
    require(paths.get("synthetic_marker_required") is True, "synthetic marker")
    require(paths.get("real_client_marker_denies") is True, "real-client denial")
    network = shared.get("network", {})
    require(network.get("default") == "denied", "network default")
    for key in ("external_upload", "oauth", "credentials", "paid_services"):
        require(network.get(key) is False, f"network boundary: {key}")
    require(network.get("loopback_only") is True, "loopback only")

    require(value.get("closed_defects") == ["WS6-QUALITY-002"], "closed defect")
    require(
        value.get("remaining_blocking_defects") == ["WS6-BLOCK-006"],
        "remaining blocker",
    )
    require(
        value.get("remaining_preparation_defects") == ["WS6-CODEXPREP-002"],
        "remaining preparation defect",
    )
    completion = value.get("completion", {})
    for key in (
        "all_required_prior_components_pass",
        "stacked_on_exact_ws69_head",
        "ws610_repository_package_complete",
        "all_15_commands_specified",
        "all_four_acceptance_classes_per_command",
    ):
        require(completion.get(key) is True, key)
    for key in (
        "ws68_integrated_to_main",
        "ws69_integrated_to_main",
        "implementation_blueprint_complete",
        "commands_implemented",
        "final_reconciliation_complete",
        "all_blocking_defects_closed",
    ):
        require(completion.get(key) is False, key)
    require(completion.get("next_permitted_work_package") == "WS6.11", "next package")
    boundaries = value.get("boundaries", {})
    require(boundaries.get("founder_accountability_preserved") is True, "accountability")
    for key, current in boundaries.items():
        if key != "founder_accountability_preserved":
            require(current is False, f"boundary: {key}")
    return failures


def _contract_failures(value: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(value.get("work_package_id") == "WS6.10", "contract package")
    require(value.get("command_count") == 15, "command count")
    require(value.get("acceptance_case_count") == 60, "case count")
    require(value.get("global_flag_count") == 9, "flag count")
    require(value.get("exit_code_count") == 11, "exit count")
    require(tuple(value.get("global_flags", [])) == EXPECTED_FLAGS, "contract flags")
    require(tuple(value.get("exit_codes", [])) == EXPECTED_EXITS, "contract exits")
    commands = value.get("commands", [])
    if not isinstance(commands, list):
        commands = []
    require(
        tuple(item.get("name") for item in commands if isinstance(item, dict))
        == EXPECTED_COMMANDS,
        "contract command order",
    )
    for command in commands:
        if not isinstance(command, dict):
            failures.append("contract command object")
            continue
        name = str(command.get("name"))
        require(
            command.get("implementation_status") == "specified_not_implemented",
            f"contract status: {name}",
        )
        require(command.get("state_recheck_required") is True, f"contract recheck: {name}")
        require(command.get("retry_attempts") >= 1, f"contract retry: {name}")
        case_exits = command.get("case_exits", {})
        require(
            isinstance(case_exits, dict) and set(case_exits) == set(ACCEPTANCE_CLASSES),
            f"contract case exits: {name}",
        )
    tests = value.get("test_registration", {})
    require(tests.get("planned_case_count") == 60, "planned tests")
    require(tests.get("registered_case_count") == 0, "registered tests")
    require(tests.get("executable_test_count") == 0, "executable tests")
    evidence = value.get("implementation_evidence", {})
    require(evidence.get("satisfied_command_count") == 0, "evidence count")
    require(
        evidence.get("status") == "not_available_pre_implementation",
        "evidence status",
    )
    return failures


def _set(value: dict[str, Any], path: tuple[Any, ...], replacement: Any) -> None:
    node: Any = value
    for part in path[:-1]:
        node = node[part]
    node[path[-1]] = replacement


def main() -> None:
    source = _load_source()
    contract = _load_json(CONTRACT)
    errors = list(Draft202012Validator(_load_json(SCHEMA)).iter_errors(contract))
    if errors:
        raise SystemExit(
            "WS6.10 schema validation failed: "
            + "; ".join(error.message for error in errors)
        )
    expected, specification, report = build_records()
    if contract != expected:
        raise SystemExit("WS6.10 contract is not deterministic")
    expected_bytes = (
        json.dumps(expected, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        + "\n"
    )
    if CONTRACT.read_text(encoding="utf-8") != expected_bytes:
        raise SystemExit("WS6.10 contract bytes are not canonical")
    if SPECIFICATION.read_text(encoding="utf-8") != specification:
        raise SystemExit("WS6.10 specification is not deterministic")
    if REPORT.read_text(encoding="utf-8") != report:
        raise SystemExit("WS6.10 report is not deterministic")
    quality = _load_json(QUALITY)["developer_experience"]["phase0_required_commands"]
    if tuple(quality) != EXPECTED_COMMANDS:
        raise SystemExit("PCR-10 command list drifted")
    failures = [*_source_failures(source), *_contract_failures(contract)]
    if failures:
        raise SystemExit("WS6.10 semantic validation failed: " + "; ".join(failures))

    rejected = 0
    for command_index, command in enumerate(source["commands"]):
        for acceptance_class in ACCEPTANCE_CLASSES:
            mutated = copy.deepcopy(source)
            del mutated["commands"][command_index]["case_exits"][acceptance_class]
            if _source_failures(mutated):
                rejected += 1
            else:
                raise SystemExit(
                    f"WS6.10 missing case mutation passed: {command['name']}:{acceptance_class}"
                )
    for command_index, command in enumerate(source["commands"]):
        mutated = copy.deepcopy(source)
        mutated["commands"][command_index]["network"] = "external_upload"
        if _source_failures(mutated):
            rejected += 1
        else:
            raise SystemExit(f"WS6.10 network mutation passed: {command['name']}")
    for command_index, command in enumerate(source["commands"]):
        mutated = copy.deepcopy(source)
        mutated["commands"][command_index]["idempotency"] = "unsafe"
        if _source_failures(mutated):
            rejected += 1
        else:
            raise SystemExit(f"WS6.10 idempotency mutation passed: {command['name']}")

    source_cases: list[tuple[tuple[Any, ...], Any]] = [
        (("work_package_id",), "WS6.9"),
        (("predecessor", "head_sha"), "0" * 40),
        (("predecessor", "integrated_to_main"), True),
        (("surface", "dispatcher"), "make"),
        (("surface", "working_directory"), "anywhere"),
        (("surface", "implementation_status"), "implemented"),
        (("shared_contracts", "output", "human_json_parity"), False),
        (("shared_contracts", "output", "raw_exception_user_message"), True),
        (("shared_contracts", "redaction", "before_output"), False),
        (("shared_contracts", "redaction", "failure_exit"), 0),
        (("shared_contracts", "paths", "resolve_first"), False),
        (("shared_contracts", "paths", "reject_symlink_escape"), False),
        (("shared_contracts", "paths", "real_client_marker_denies"), False),
        (("shared_contracts", "network", "default"), "allowed"),
        (("shared_contracts", "network", "external_upload"), True),
        (("closed_defects",), []),
        (("remaining_blocking_defects",), []),
        (("remaining_preparation_defects",), []),
        (("completion", "all_required_prior_components_pass"), False),
        (("completion", "commands_implemented"), True),
        (("completion", "next_permitted_work_package"), "WS6.12"),
        (("boundaries", "codex_start_authorized"), True),
        (("boundaries", "phase0_implementation_authorized"), True),
    ]
    for path, replacement in source_cases:
        mutated = copy.deepcopy(source)
        _set(mutated, path, replacement)
        if _source_failures(mutated):
            rejected += 1
        else:
            raise SystemExit(f"WS6.10 source mutation passed: {path}")

    structural: list[tuple[str, dict[str, Any]]] = []
    missing = copy.deepcopy(source)
    missing["commands"] = missing["commands"][:-1]
    structural.append(("missing command", missing))
    duplicate = copy.deepcopy(source)
    duplicate["commands"][1]["name"] = duplicate["commands"][0]["name"]
    structural.append(("duplicate command", duplicate))
    missing_exit = copy.deepcopy(source)
    missing_exit["commands"][0]["exits"].remove(7)
    structural.append(("missing safety exit", missing_exit))
    destructive_retry = copy.deepcopy(source)
    destructive_retry["commands"][10]["retry"]["attempts"] = 2
    structural.append(("destructive retry", destructive_retry))
    missing_criteria = copy.deepcopy(source)
    missing_criteria["commands"][0]["criteria"] = []
    structural.append(("missing criteria", missing_criteria))
    paid = copy.deepcopy(source)
    paid["shared_contracts"]["network"]["paid_services"] = True
    structural.append(("paid service", paid))
    for label, mutated in structural:
        if _source_failures(mutated):
            rejected += 1
        else:
            raise SystemExit(f"WS6.10 structural mutation passed: {label}")

    contract_cases: list[tuple[tuple[Any, ...], Any]] = [
        (("command_count",), 14),
        (("acceptance_case_count",), 59),
        (("global_flag_count",), 8),
        (("exit_code_count",), 10),
        (("test_registration", "registered_case_count"), 1),
        (("test_registration", "executable_test_count"), 1),
        (("implementation_evidence", "satisfied_command_count"), 1),
    ]
    for path, replacement in contract_cases:
        mutated = copy.deepcopy(contract)
        _set(mutated, path, replacement)
        if _contract_failures(mutated):
            rejected += 1
        else:
            raise SystemExit(f"WS6.10 contract mutation passed: {path}")

    print(
        "WS6.10 developer experience specification passed: "
        f"{rejected} mutations rejected, commands=15, acceptance_cases=60, "
        "global_flags=9, exit_codes=11, registered_tests=0, "
        "implementation_evidence=0, next=WS6.11, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
