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
PURPOSES = {
    "doctor": "Inspect the supported local environment without installing or activating services.",
    "bootstrap": "Prepare only the local synthetic IMP-P0 workspace and verified dependencies.",
    "up": "Start the approved local synthetic service profile and prove readiness.",
    "down": "Stop approved local services while preserving synthetic state and evidence.",
    "restart": "Perform one bounded stop/start cycle without resetting configuration or data.",
    "health": "Report distinct liveness, readiness and dependency health without repair.",
    "test": "Run declared synthetic test suites and retain reproducible local evidence.",
    "lint": "Run read-only lint checks across declared source surfaces.",
    "format": "Check or atomically format only the declared editable source allowlist.",
    "scan": "Run local secret, dependency and container scans without repository upload.",
    "reset-synthetic": "Reset only verified synthetic local state after a verified backup.",
    "backup": "Create an immutable verified synthetic backup with a manifest and digest.",
    "restore": "Verify and transactionally restore one compatible synthetic backup.",
    "clean": "Remove only allowlisted ephemeral build, cache and test artifacts.",
    "support-bundle": "Create a bounded local diagnostic bundle after redaction validation.",
}


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
    tasks = {
        match.group(1): match.group(2).strip()
        for match in TASK_HEADING.finditer(BACKLOG.read_text(encoding="utf-8"))
    }
    for required in ("P0.1", "P0.2", "P0.3", "P0.4"):
        if required not in tasks:
            raise ValueError(f"missing IMP-P0 task: {required}")
    return tasks


def _flag_name(spec: str) -> str:
    name = spec.split(":", 1)[0]
    if not name.startswith("--"):
        raise ValueError(f"invalid flag specification: {spec}")
    return name


def _render_specification(source: dict[str, Any], commands: list[dict[str, Any]]) -> str:
    lines = [
        "# WS6.10 — Developer experience specification",
        "",
        "> [!CAUTION]",
        "> **SPECIFIED, NOT IMPLEMENTED OR AUTHORISED.** This defines the future",
        "> IMP-P0 local command surface. It creates no dispatcher, runtime or authority.",
        "",
        "## Purpose and boundary",
        "",
        "The future dispatcher is `./offdata`, invoked from the repository root on the",
        "supported macOS/Apple Silicon environment. All commands are local-first,",
        "synthetic-only and fail closed. Registered executable tests and satisfied",
        "implementation evidence remain zero. `codex_start_authorized=false`.",
        "",
        "The defect register suggested `docs/53-PHASE-0-DEVELOPER-EXPERIENCE-SPEC.md`,",
        "but prefix `53` is immutable WS6.1 evidence. This `docs/62-*` file is canonical.",
        "The wider Phase 0 topology blueprint remains deferred to WS6.13.",
        "",
        "## Shared contract",
        "",
        "- Human and JSON results have semantic parity and RFC 3339 UTC timestamps.",
        "- Errors identify code, component, cause, safe remediation and retryability.",
        "- Raw exceptions are never the primary user message.",
        "- Secret-like keys and values are redacted before console or artifact output.",
        "- Paths are resolved first; symlink escape and protected-path writes are denied.",
        "- Destructive operations require a synthetic marker and exact confirmation.",
        "- A real-client marker denies mutation.",
        "- Network is denied by default; only declared dependency or vulnerability-data",
        "  fetches may be explicitly opted in. Upload, OAuth, credentials and paid services",
        "  remain prohibited.",
        "",
        "### Global flags",
        "",
        ", ".join(f"`{_flag_name(item)}`" for item in source["global_flags"]),
        "",
        "### Exit codes",
        "",
        "| Code | Name | Retryable | Meaning |",
        "|---:|---|:---:|---|",
    ]
    for code, name, retryable, meaning in source["exit_codes"]:
        lines.append(f"| `{code}` | `{name}` | `{str(retryable).lower()}` | {meaning} |")
    lines.extend(
        [
            "",
            "## Acceptance model",
            "",
            "Every command has exactly four planned, unregistered cases:",
            "",
            "- `positive`: expected state, exit code and redacted evidence are correct.",
            "- `failure`: cause is classified, remediation is safe and success is not claimed.",
            "- `safety`: request is denied before effects and the boundary is recorded.",
            "- `retry`: bounded attempts, state recheck and final result are evidenced.",
            "",
            "## Command contracts",
            "",
            "| Command | Owner | Purpose | Flags | Exits | Idempotency | Attempts | Case exits |",
            "|---|---|---|---|---|---|---:|---|",
        ]
    )
    for command in commands:
        flags = ", ".join(f"`{item}`" for item in command["flag_names"]) or "—"
        exits = ", ".join(str(item) for item in command["exits"])
        case_exits = ", ".join(
            f"{key}={command['case_exits'][key]}" for key in ACCEPTANCE_CLASSES
        )
        lines.append(
            f"| `./offdata {command['name']}` | `{command['task']}` / "
            f"`{command['component']}` | {command['purpose']} | {flags} | `{exits}` | "
            f"`{command['idempotency']}` | `{command['retry_attempts']}` | "
            f"`{case_exits}` |"
        )
    lines.extend(
        [
            "",
            "## Command-specific safety and retry rules",
            "",
        ]
    )
    for command in commands:
        confirmation = json.dumps(command["confirmation"], sort_keys=True)
        lines.extend(
            [
                f"### `./offdata {command['name']}`",
                "",
                f"- Category/mutation: `{command['category']}` / `{command['mutation']}`.",
                f"- Network: `{command['network']}`.",
                f"- Confirmation: `{confirmation}`.",
                f"- Retryable: {', '.join(f'`{item}`' for item in command['retryable']) or '`none`'}.",
                f"- Non-retryable: {', '.join(f'`{item}`' for item in command['non_retryable'])}.",
                f"- Quality obligations: {', '.join(f'`{item}`' for item in command['criteria'])}.",
                "",
            ]
        )
    lines.extend(
        [
            "## Completion boundary",
            "",
            "WS6.10 closes only `WS6-QUALITY-002`. It does not implement `./offdata`,",
            "register executable tests, create the WS6.13 blueprint, start services or",
            "satisfy command evidence. `WS6-CODEXPREP-002` and `WS6-BLOCK-006` remain open.",
            "",
            "Next permitted package: `WS6.11`, after the governed predecessor sequence.",
            "",
            "## Rollback",
            "",
            "Before merge, close the PR and delete only its branch. After merge, revert the",
            "specification package as one unit. No runtime exists to roll back.",
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
    names = [item["name"] for item in source["commands"]]
    if names != canonical or len(names) != len(set(names)) != 15:
        raise ValueError("WS6.10 commands must exactly match the 15 PCR-10 commands")
    obligation_ids = {
        item["criterion_id"]
        for item in obligation_map["obligations"]
        if isinstance(item, dict) and isinstance(item.get("criterion_id"), str)
    }
    commands: list[dict[str, Any]] = []
    case_ids: list[str] = []
    for command in source["commands"]:
        if command["task"] not in tasks:
            raise ValueError(f"unknown implementation task: {command['task']}")
        unknown = sorted(set(command["criteria"]) - obligation_ids)
        if unknown:
            raise ValueError(f"unknown obligations for {command['name']}: {unknown}")
        if tuple(command["case_exits"]) != ACCEPTANCE_CLASSES:
            raise ValueError(f"invalid acceptance classes for {command['name']}")
        for acceptance_class in ACCEPTANCE_CLASSES:
            case_id = f"DX-{_slug(command['name'])}-{acceptance_class.upper()}-001"
            if command["case_exits"][acceptance_class] not in command["exits"]:
                raise ValueError(f"case exit is not allowed: {case_id}")
            case_ids.append(case_id)
        commands.append(
            {
                "name": command["name"],
                "task": command["task"],
                "component": command["component"],
                "purpose": PURPOSES[command["name"]],
                "category": command["category"],
                "mutation": command["mutation"],
                "idempotency": command["idempotency"],
                "confirmation": command["confirmation"],
                "network": command["network"],
                "flag_names": [_flag_name(item) for item in command["flags"]],
                "exits": command["exits"],
                "retry_attempts": command["retry"]["attempts"],
                "retryable": command["retry"]["retryable"],
                "non_retryable": command["retry"]["non_retryable"],
                "state_recheck_required": True,
                "criteria": command["criteria"],
                "case_exits": command["case_exits"],
                "source_record_sha256": _sha256(
                    json.dumps(command, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
                ),
                "implementation_status": "specified_not_implemented",
            }
        )
    contract_commands = [
        {
            key: command[key]
            for key in (
                "name", "task", "component", "idempotency", "network",
                "flag_names", "exits", "retry_attempts",
                "state_recheck_required", "case_exits", "source_record_sha256",
                "implementation_status",
            )
        }
        for command in commands
    ]
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
        "global_flags": [_flag_name(item) for item in source["global_flags"]],
        "exit_codes": [item[0] for item in source["exit_codes"]],
        "global_flag_count": len(source["global_flags"]),
        "exit_code_count": len(source["exit_codes"]),
        "command_count": len(contract_commands),
        "acceptance_case_count": len(case_ids),
        "commands": contract_commands,
        "test_registration": {
            "planned_case_count": len(case_ids),
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
    specification = _render_specification(source, commands)
    report = "\n".join(
        [
            "# WS6.10 developer experience specification evidence",
            "",
            "<!-- Generated by scripts/build_workstream6_developer_experience_specification.py. -->",
            "",
            f"- Exact WS6.9 predecessor head: `{source['predecessor']['head_sha']}`.",
            "- Exact PCR-10 commands specified: `15`.",
            "- Command acceptance cases: `60` (`4` per command).",
            "- Global flags: `9`.",
            "- Governed exit codes: `11`.",
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
        "Built WS6.10 developer experience specification: commands=15, "
        "acceptance_cases=60, registered_tests=0, implementation_evidence=0, "
        "next=WS6.11, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
