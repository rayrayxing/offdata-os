from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "configs" / "workstream6-developer-experience-specification.yaml"
CONTRACT = ROOT / "contracts" / "developer-experience-specification.json"
SPECIFICATION = ROOT / "docs" / "62-WS6-10-DEVELOPER-EXPERIENCE-SPECIFICATION.md"
REPORT = ROOT / "reports" / "workstream6-developer-experience-specification-evidence.md"
QUALITY = ROOT / "contracts" / "pre-codex-readiness.json"
OBLIGATION_MAP = ROOT / "requirements" / "implementation-obligation-map.json"
BACKLOG = ROOT / "docs" / "11-BUILD-BACKLOG.md"
TASK_HEADING = re.compile(r"^### (P(?:[0-9]|1[0-2])\.[0-9]+) (.+)$", re.MULTILINE)
ACCEPTANCE_CLASSES = ("positive", "failure", "safety", "retry")


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def _slug(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", value.upper()).strip("-")


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _backlog_tasks() -> dict[str, str]:
    text = BACKLOG.read_text(encoding="utf-8")
    tasks = {match.group(1): match.group(2).strip() for match in TASK_HEADING.finditer(text)}
    for required in ("P0.1", "P0.2", "P0.3", "P0.4"):
        if required not in tasks:
            raise ValueError(f"missing IMP-P0 task: {required}")
    return tasks


def _parse_flag(spec: str) -> dict[str, Any]:
    parts = spec.split(":")
    if len(parts) < 2 or not parts[0].startswith("--"):
        raise ValueError(f"invalid flag specification: {spec}")
    result: dict[str, Any] = {
        "name": parts[0],
        "type": parts[1],
        "required": "required" in parts[2:],
    }
    for part in parts[2:]:
        if part.startswith("default="):
            result["default"] = json.loads(part.removeprefix("default="))
        elif part.startswith("values="):
            result["allowed_values"] = part.removeprefix("values=").split("|")
        elif part.startswith("min="):
            result["minimum"] = float(part.removeprefix("min="))
        elif part.startswith("max="):
            result["maximum"] = float(part.removeprefix("max="))
        elif part != "required":
            raise ValueError(f"unknown flag modifier: {part}")
    return result


def _render_specification(
    source: dict[str, Any],
    commands: list[dict[str, Any]],
    global_flags: list[dict[str, Any]],
    exit_codes: list[dict[str, Any]],
) -> str:
    lines = [
        "# WS6.10 — Developer experience specification",
        "",
        "> [!CAUTION]",
        "> **SPECIFIED, NOT IMPLEMENTED OR AUTHORISED.** This document defines the future",
        "> IMP-P0 local command surface. It does not create the dispatcher, start services,",
        "> authorize Codex, or satisfy implementation evidence.",
        "",
        "## Purpose",
        "",
        "The future root dispatcher is `./offdata`. Every command runs from the repository",
        "root, remains local-first and synthetic-only, and follows one shared output,",
        "redaction, path-safety, network, failure and retry contract.",
        "",
        f"- Commands specified: `{len(commands)}`.",
        f"- Acceptance cases: `{sum(len(item['acceptance_cases']) for item in commands)}`.",
        "- Acceptance classes per command: `positive`, `failure`, `safety`, `retry`.",
        "- Registered executable tests: `0`.",
        "- Satisfied command evidence: `0`.",
        "- `codex_start_authorized=false`.",
        "",
        "The defect register suggested `docs/53-PHASE-0-DEVELOPER-EXPERIENCE-SPEC.md`,",
        "but numeric prefix `53` is already immutable WS6.1 evidence. This file is the",
        "canonical WS6.10 specification. The broader Phase 0 implementation blueprint",
        "remains deferred to WS6.13.",
        "",
        "## Shared command contract",
        "",
        f"- Dispatcher: `{source['surface']['dispatcher']}`.",
        f"- Working directory: `{source['surface']['working_directory']}`.",
        f"- Primary environment: `{source['surface']['primary_environment']}`.",
        "- Human and JSON output have semantic parity.",
        "- Errors identify a non-secret code, component, cause, safe remediation and retryability.",
        "- Raw exceptions are never the primary user message.",
        "- Redaction occurs before console or artifact writes.",
        "- Paths are resolved before access; symlink escape is rejected.",
        "- Destructive operations require a synthetic-only marker and exact confirmation.",
        "- A real-client marker denies mutation.",
        "- Network is denied by default; external upload, OAuth, credentials and paid services",
        "  remain prohibited.",
        "",
        "### Global flags",
        "",
        "| Flag | Type | Required | Default |",
        "|---|---|:---:|---:|",
    ]
    for item in global_flags:
        default = "`—`" if "default" not in item else f"`{item.get('default')}`"
        lines.append(
            f"| `{item['name']}` | `{item['type']}` | "
            f"`{str(item['required']).lower()}` | {default} |"
        )
    lines.extend(
        [
            "",
            "### Exit codes",
            "",
            "| Code | Name | Retryable | Meaning |",
            "|---:|---|:---:|---|",
        ]
    )
    for item in exit_codes:
        lines.append(
            f"| `{item['code']}` | `{item['name']}` | "
            f"`{str(item['retryable']).lower()}` | {item['meaning']} |"
        )
    lines.extend(
        [
            "",
            "## Command summary",
            "",
            "| Command | Task | Category | Mutation | Idempotency | Network |",
            "|---|---|---|---|---|---|",
        ]
    )
    for command in commands:
        lines.append(
            f"| `./offdata {command['name']}` | `{command['task']}` | "
            f"`{command['category']}` | `{command['mutation']}` | "
            f"`{command['idempotency']}` | `{command['network']}` |"
        )
    for command in commands:
        lines.extend(
            [
                "",
                f"## `./offdata {command['name']}`",
                "",
                command["purpose"],
                "",
                f"- Owner: `{command['task']}` / `{command['component']}`.",
                f"- Success: {command['success']}",
                f"- Failure: {command['failure']}",
                f"- Safety: {command['safety']}",
                f"- Allowed exits: {', '.join(f'`{item}`' for item in command['exits'])}.",
                f"- Maximum attempts: `{command['retry']['maximum_attempts']}`.",
                "",
                "### Flags",
                "",
                "| Flag | Type | Required | Default |",
                "|---|---|:---:|---:|",
            ]
        )
        for item in command["parsed_flags"]:
            default = "`—`" if "default" not in item else f"`{item.get('default')}`"
            lines.append(
                f"| `{item['name']}` | `{item['type']}` | "
                f"`{str(item['required']).lower()}` | {default} |"
            )
        if not command["parsed_flags"]:
            lines.append("| — | — | — | — |")
        lines.extend(
            [
                "",
                "### Acceptance cases",
                "",
                "| ID | Class | Expected exit | Scenario |",
                "|---|---|---:|---|",
            ]
        )
        for case in command["acceptance_cases"]:
            lines.append(
                f"| `{case['case_id']}` | `{case['acceptance_class']}` | "
                f"`{case['expected_exit_code']}` | {case['scenario']} |"
            )
    lines.extend(
        [
            "",
            "## Completion boundary",
            "",
            "WS6.10 closes only `WS6-QUALITY-002`. It does not register executable tests,",
            "create the Phase 0 topology blueprint, implement `./offdata`, activate services,",
            "or satisfy command evidence. `WS6-CODEXPREP-002` and `WS6-BLOCK-006` remain open.",
            "",
            "The next permitted package is WS6.11 after the governed WS6.8 → WS6.9 →",
            "WS6.10 integration sequence.",
            "",
            "## Rollback",
            "",
            "Before merge, close the WS6.10 pull request and delete only its branch. After",
            "merge, revert this specification package as one unit. No runtime exists to",
            "roll back.",
            "",
        ]
    )
    return "\n".join(lines)


def build_records() -> tuple[dict[str, Any], str, str]:
    source_text = SOURCE.read_text(encoding="utf-8")
    source = _load_yaml(SOURCE)
    quality = _load_json(QUALITY)
    obligation_map = _load_json(OBLIGATION_MAP)
    tasks = _backlog_tasks()

    canonical = quality["developer_experience"]["phase0_required_commands"]
    source_commands = source["commands"]
    names = [item["name"] for item in source_commands]
    if names != canonical:
        raise ValueError("WS6.10 commands must exactly match PCR-10 order")
    if len(names) != 15 or len(names) != len(set(names)):
        raise ValueError("WS6.10 command identities are invalid")

    global_flags = [_parse_flag(item) for item in source["global_flags"]]
    exit_codes = [
        {"code": item[0], "name": item[1], "retryable": item[2], "meaning": item[3]}
        for item in source["exit_codes"]
    ]
    obligation_ids = {
        item["criterion_id"]
        for item in obligation_map["obligations"]
        if isinstance(item, dict) and isinstance(item.get("criterion_id"), str)
    }
    display_commands: list[dict[str, Any]] = []
    index_commands: list[dict[str, Any]] = []
    all_cases = []
    for command in source_commands:
        if command["task"] not in tasks:
            raise ValueError(f"unknown implementation task: {command['task']}")
        unknown = sorted(set(command["criteria"]) - obligation_ids)
        if unknown:
            raise ValueError(f"unknown obligations for {command['name']}: {unknown}")
        if tuple(command["cases"]) != ACCEPTANCE_CLASSES:
            raise ValueError(f"invalid acceptance classes for {command['name']}")
        parsed_flags = [_parse_flag(item) for item in command["flags"]]
        retry_source = command["retry"]
        retry = {
            "maximum_attempts": retry_source["attempts"],
            "backoff_seconds": retry_source["backoff"],
            "retryable_conditions": retry_source["retryable"],
            "non_retryable_conditions": retry_source["non_retryable"],
            "state_recheck_required": True,
        }
        cases = []
        for acceptance_class in ACCEPTANCE_CLASSES:
            source_case = command["cases"][acceptance_class]
            case = {
                "case_id": f"DX-{_slug(command['name'])}-{acceptance_class.upper()}-001",
                "command": command["name"],
                "acceptance_class": acceptance_class,
                "scenario": source_case[1],
                "expected_exit_code": source_case[0],
                "assertions": source_case[2],
                "registration_status": "planned_unregistered",
                "executable_test_exists": False,
            }
            if case["expected_exit_code"] not in command["exits"]:
                raise ValueError(f"acceptance exit is not allowed: {case['case_id']}")
            cases.append(case)
            all_cases.append(case)
        display_commands.append(
            {
                **command,
                "parsed_flags": parsed_flags,
                "retry": retry,
                "task_title": tasks[command["task"]],
                "implementation_status": "specified_not_implemented",
                "acceptance_cases": cases,
            }
        )
        index_commands.append(
            {
                "name": command["name"],
                "task": command["task"],
                "component": command["component"],
                "category": command["category"],
                "mutation": command["mutation"],
                "idempotency": command["idempotency"],
                "confirmation": command["confirmation"],
                "network": command["network"],
                "flags": parsed_flags,
                "exits": command["exits"],
                "retry": retry,
                "criteria": command["criteria"],
                "acceptance_cases": [
                    {
                        "case_id": case["case_id"],
                        "acceptance_class": case["acceptance_class"],
                        "expected_exit_code": case["expected_exit_code"],
                        "assertion_count": len(case["assertions"]),
                    }
                    for case in cases
                ],
                "implementation_status": "specified_not_implemented",
            }
        )

    contract = {
        "schema_version": source["schema_version"],
        "work_package_id": source["work_package_id"],
        "title": source["title"],
        "predecessor": source["predecessor"],
        "defect_ids": source["defect_ids"],
        "canonical_sources": source["canonical_sources"],
        "document_path_resolution": source["document_path_resolution"],
        "surface": source["surface"],
        "shared_contracts": source["shared_contracts"],
        "generated_from": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": _sha256(source_text),
        "global_flags": global_flags,
        "exit_codes": exit_codes,
        "global_flag_count": len(global_flags),
        "exit_code_count": len(exit_codes),
        "command_count": len(index_commands),
        "acceptance_case_count": len(all_cases),
        "commands": index_commands,
        "test_registration": {
            "planned_case_count": len(all_cases),
            "registered_case_count": 0,
            "executable_test_count": 0,
            "separate_registration_defect": "WS6-CODEXPREP-002",
        },
        "implementation_evidence": {
            "satisfied_command_count": 0,
            "status": "not_available_pre_implementation",
        },
        "closed_defects": source["closed_defects"],
        "remaining_blocking_defects": source["remaining_blocking_defects"],
        "remaining_preparation_defects": source["remaining_preparation_defects"],
        "completion": source["completion"],
        "boundaries": source["boundaries"],
    }
    specification = _render_specification(source, display_commands, global_flags, exit_codes)
    report = "\n".join(
        [
            "# WS6.10 developer experience specification evidence",
            "",
            "<!-- Generated by scripts/build_workstream6_developer_experience_specification.py. -->",
            "",
            f"- Exact WS6.9 predecessor head: `{source['predecessor']['head_sha']}`.",
            f"- Exact PCR-10 commands specified: `{len(index_commands)}`.",
            f"- Command acceptance cases: `{len(all_cases)}` (`4` per command).",
            f"- Global flags: `{contract['global_flag_count']}`.",
            f"- Governed exit codes: `{contract['exit_code_count']}`.",
            "- Registered or executable command tests claimed: `0`.",
            "- Satisfied implementation evidence claimed: `0`.",
            "- Closed defect: `WS6-QUALITY-002`.",
            "- Separate test-registration defect remains open: `WS6-CODEXPREP-002`.",
            "- Remaining blocking defect: `WS6-BLOCK-006`.",
            "- `codex_start_authorized=false`; commands remain specified but unimplemented.",
            "",
            "Next permitted work package: `WS6.11`, after the governed predecessor sequence.",
            "",
        ]
    )
    return contract, specification, report


def main() -> None:
    contract, specification, report = build_records()
    CONTRACT.write_text(
        json.dumps(contract, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        + "\n",
        encoding="utf-8",
    )
    SPECIFICATION.write_text(specification, encoding="utf-8")
    REPORT.write_text(report, encoding="utf-8")
    print(
        "Built WS6.10 developer experience specification: "
        "commands=15, acceptance_cases=60, registered_tests=0, "
        "implementation_evidence=0, next=WS6.11, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
