from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "configs/workstream6-operational-quality-specification.yaml"
BP_SRC = ROOT / "configs/phase0-implementation-blueprint.yaml"
IOM = ROOT / "requirements/implementation-obligation-map.json"
DX = ROOT / "contracts/developer-experience-specification.json"
OUT = ROOT / "contracts/operational-quality-specification.json"
BP_OUT = ROOT / "contracts/phase0-implementation-blueprint.json"
API_OUT = ROOT / "contracts/api-interface-contracts.json"
KNOW_OUT = ROOT / "contracts/knowledge-ingestion-contracts.json"
REG = ROOT / "tests/registry/ws613-planned-acceptance-tests.json"
OVERLAY = ROOT / "requirements/implementation-obligation-test-registration.json"
DOC = ROOT / "docs/65-WS6-13-OPERATIONAL-QUALITY-SPECIFICATION.md"
REPORT = ROOT / "reports/workstream6-operational-quality-specification-evidence.md"

PHASE0_CRITERIA = [
    "DX-ROOT",
    "DX-DIAG",
    "DX-PORTS",
    "DX-PATH",
    "DX-SECRETS",
    "DX-BACKUP",
    "DX-MAC",
    "OP-CORR",
    "OP-ERROR",
    "OP-TRACE",
    "OP-HEALTH",
    "OP-SBOM",
    "OP-RECOVERY",
    "XC-TIME",
    "XC-MIGRATE",
    "XC-PRIV",
]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def canonical(value: object) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ) + "\n"


def build_records() -> tuple[object, ...]:
    source = load(SRC)
    blueprint = load(BP_SRC)
    obligation_map = load(IOM)
    developer = load(DX)

    obligations = [
        item
        for item in obligation_map["obligations"]
        if item.get("test_registration_owner") == "WS6.13"
    ]
    if len(obligations) != 16:
        raise ValueError("expected 16 WS6.13-owned IMP-P0 obligations")
    if [item["criterion_id"] for item in obligations] != PHASE0_CRITERIA:
        raise ValueError("phase0 obligation order drift")
    if developer["command_count"] != 15 or developer["acceptance_case_count"] != 60:
        raise ValueError("developer case baseline drift")

    operational_contract = {
        **source,
        "generated_from": str(SRC.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
        "operational_signal_count": len(source["operational_signals"]),
        "learning_metric_count": len(source["learning_metrics"]),
    }
    blueprint_contract = {
        **blueprint,
        "generated_from": str(BP_SRC.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(BP_SRC.read_bytes()).hexdigest(),
        "task_count": len(blueprint["tasks"]),
        "service_count": len(blueprint["services"]),
        "registered_phase0_test_count": source["test_registration"]["phase0_total"],
        "root_command_count": developer["command_count"],
    }
    api_contract = {
        "schema_version": 1,
        "work_package_id": "WS6.13",
        "contract_id": "IMP-P0-API-UI-SHELL",
        "status": "planned_not_implemented",
        "owner": ["IMP-P0", "P0.2", "COMP-FOUNDATION-DEVENV"],
        "binding": "loopback_only",
        "ui": "http://127.0.0.1:3000",
        "api": "http://127.0.0.1:8000",
        "endpoints": [
            {"method": "GET", "path": path}
            for path in [
                "/health/live",
                "/health/ready",
                "/health",
                "/api/v1/system/status",
            ]
        ],
        "error_envelope": [
            "code",
            "message",
            "correlation_id",
            "retryable",
            "component",
        ],
        "raw_exception_primary": False,
        "external_binding": False,
        "founder_identity_deferred_to": "P2.1",
        "runtime_active": False,
        "boundaries": source["boundaries"],
    }
    knowledge_contract = {
        "schema_version": 1,
        "work_package_id": "WS6.13",
        "contract_id": "IMP-P0-STORAGE-AND-FUTURE-INGESTION",
        "status": "planned_not_implemented",
        "phase0_owner": ["IMP-P0", "P0.2", "COMP-FOUNDATION-DEVENV"],
        "future_ingestion_owner": ["IMP-P1", "P1.1/P1.2", "COMP-KNOWLEDGE"],
        "postgres": {"local": True, "synthetic_only": True, "backup": True},
        "object_storage": {
            "local_s3_emulator": True,
            "synthetic_only": True,
            "checksum": "sha256",
            "backup": True,
        },
        "ingestion": {
            "real_document_import": False,
            "synthetic_fixture_only_pre_authorization": True,
            "preserve_original_bytes": True,
            "stable_checksum": True,
            "quarantine_malformed_planned": True,
        },
        "external_object_storage": False,
        "credentials_required": False,
        "runtime_active": False,
        "boundaries": source["boundaries"],
    }

    obligation_tests = [
        {
            "id": item["test_obligation_id"],
            "criterion": item["criterion_id"],
            "task": item["task_id"],
            "component": item["component_id"],
            "evidence": item["evidence_type"],
        }
        for item in obligations
    ]
    developer_tests = [
        {
            "id": f"DX-{command['name'].upper()}-{case_class.upper()}-001",
            "command": command["name"],
            "class": case_class,
            "task": command["task"],
            "component": command["component"],
        }
        for command in developer["commands"]
        for case_class in ("positive", "failure", "safety", "retry")
    ]
    conformance_tests = [
        {"id": "WS613-WF-WAIT-001", "case": "wait", "phase": "IMP-P3", "task": "P3.2", "component": "COMP-WORKFLOW"},
        {"id": "WS613-WF-RETRY-001", "case": "retry", "phase": "IMP-P3", "task": "P3.2", "component": "COMP-WORKFLOW"},
        {"id": "WS613-WF-CANCEL-001", "case": "cancel", "phase": "IMP-P3", "task": "P3.2", "component": "COMP-WORKFLOW"},
        {"id": "WS613-WF-IDEMPOTENCY-001", "case": "idempotency", "phase": "IMP-P3", "task": "P3.3", "component": "COMP-API"},
        {"id": "WS613-AGENT-TOOL-PERMISSION-001", "case": "tool_permission", "phase": "IMP-P4", "task": "P4.4", "component": "COMP-QA"},
        {"id": "WS613-AGENT-COST-BUDGET-001", "case": "cost_budget", "phase": "IMP-P4", "task": "P4.4", "component": "COMP-QA"},
        {"id": "WS613-AGENT-CONTEXT-MINIMIZATION-001", "case": "context_minimization", "phase": "IMP-P4", "task": "P4.4", "component": "COMP-QA"},
    ]
    registry = {
        "schema_version": 1,
        "work_package_id": "WS6.13",
        "status": "planning_only",
        "defaults": {
            "owner": "WS6.13",
            "phase": "IMP-P0",
            "evidence": "developer_command_acceptance_report",
            "registration_status": "registered_planned",
            "executable": False,
            "evidence_satisfied": False,
            "provider_execution_required_preimplementation": False,
        },
        "counts": {
            "phase0_criteria": 16,
            "developer_cases": 60,
            "phase0_total": 76,
            "conformance": 7,
            "planned_total": 83,
            "executable": 0,
            "evidence": 0,
        },
        "phase0_obligation_registrations": obligation_tests,
        "developer_command_cases": developer_tests,
        "workflow_agent_conformance_cases": conformance_tests,
        "boundaries": source["boundaries"],
    }
    overlay = {
        "schema_version": 1,
        "work_package_id": "WS6.13",
        "source_obligation_map": "requirements/implementation-obligation-map.json",
        "source_map_immutable": True,
        "registration_count": 16,
        "registrations": [
            {
                "criterion": item["criterion_id"],
                "test_id": item["test_obligation_id"],
                "phase": item["phase_id"],
                "task": item["task_id"],
                "component": item["component_id"],
                "evidence": item["evidence_type"],
                "status": "registered_planned",
                "executable": False,
            }
            for item in obligations
        ],
        "closed_defect": "WS6-CODEXPREP-002",
    }

    document = "\n".join(
        [
            "# WS6.13 — Operational quality specification",
            "",
            "> [!CAUTION]",
            "> Planning and schema evidence only. Telemetry, runtime, services, real-client data and external actions remain disabled.",
            "",
            f"- Operational signals: `{len(source['operational_signals'])}`",
            f"- Learning metrics: `{len(source['learning_metrics'])}`",
            "- Registered IMP-P0 planned tests: `76`",
            "- Workflow/agent conformance cases: `7`",
            "- Executable new tests: `0`",
            "- Telemetry default: `false`",
            "- `codex_start_authorized=false`.",
            "",
            "## Operational signals",
            "",
        ]
        + [
            f"- `{item['id']}` — `{item['source']}`; owner `{item['owner'][0]}/{item['owner'][1]}/{item['owner'][2]}`; privacy `{item['privacy']}`; retention `{item['retention']}`; evidence `{item['evidence']}`."
            for item in source["operational_signals"]
        ]
        + ["", "## Learning metrics", ""]
        + [
            f"- `{item['field']}` — source `{item['source']}`; capture `{item['capture'][0]}/{item['capture'][1]}`; canonical measurement `IMP-P12/P12.3`; privacy `{item['privacy']}`; collection disabled."
            for item in source["learning_metrics"]
        ]
        + [
            "",
            "## IMP-P0 preparation",
            "",
            "- P0.1–P0.4 blueprint is machine-readable and planning-only.",
            "- Four local services are loopback-only; external networking defaults denied.",
            "- API/UI shell contracts are read-only and inactive.",
            "- Storage/ingestion contracts allow synthetic fixtures only; real document import is false.",
            "- 76 IMP-P0 planned tests are registered without becoming executable evidence.",
            "- Seven wait/retry/cancel/idempotency/tool-permission/cost/context conformance cases are planned without provider execution.",
            "",
            "## Completion",
            "",
            "Closes `WS6-QUALITY-005` and `WS6-CODEXPREP-001` through `WS6-CODEXPREP-005`. `WS6-BLOCK-006` remains open. Next permitted package: `WS6.14`.",
            "",
        ]
    )
    report = "\n".join(
        [
            "# WS6.13 operational quality evidence",
            "",
            "<!-- Generated by scripts/build_workstream6_operational_quality_specification.py. -->",
            "",
            f"- Predecessor: `{source['predecessor']['head_sha']}`",
            "- Operational signals: `8`",
            "- Learning metrics: `11`",
            "- Phase-0 registered planned tests: `76`",
            "- Workflow/agent conformance cases: `7`",
            "- Executable new tests: `0`",
            "- Implementation evidence: `0`",
            "- Telemetry enabled: `false`",
            "- Remaining blocker: `WS6-BLOCK-006`",
            "- `codex_start_authorized=false`.",
            "",
            "Next permitted work package: `WS6.14`.",
            "",
        ]
    )
    return (
        operational_contract,
        blueprint_contract,
        api_contract,
        knowledge_contract,
        registry,
        overlay,
        document,
        report,
    )


def main() -> None:
    records = build_records()
    paths = (OUT, BP_OUT, API_OUT, KNOW_OUT, REG, OVERLAY, DOC, REPORT)
    for path, value in zip(paths, records, strict=True):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            value if isinstance(value, str) else canonical(value), encoding="utf-8"
        )
    print(
        "Built WS6.13 operational quality specification: operational=8, learning=11, "
        "phase0_registered=76, conformance=7, executable=0, telemetry=false, "
        "next=WS6.14, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
