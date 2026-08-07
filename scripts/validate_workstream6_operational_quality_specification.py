from __future__ import annotations

import copy
from typing import Any, Callable

import jsonschema

from build_workstream6_operational_quality_specification import (
    API_OUT,
    BP_OUT,
    BP_SRC,
    DOC,
    IOM,
    KNOW_OUT,
    OUT,
    OVERLAY,
    REG,
    REPORT,
    ROOT,
    SRC,
    build_records,
    canonical,
    load,
)

OP_IDS = [
    "OP-CORR",
    "OP-ERROR",
    "OP-TRACE",
    "OP-HEALTH",
    "OP-COST",
    "OP-FLAGS",
    "OP-SBOM",
    "OP-RECOVERY",
]
LEARNING_FIELDS = [
    "founder_correction_effort",
    "recommendation_override_reason",
    "output_editing_time",
    "repeated_manual_task",
    "defect_category",
    "missing_evidence_or_method",
    "agent_contribution_accepted_or_rejected",
    "task_completion_time",
    "human_time_saved",
    "quality_per_cost",
    "client_facing_usefulness",
]


def validate_source(source: dict[str, Any], blueprint: dict[str, Any]) -> None:
    if source["work_package_id"] != "WS6.13":
        raise ValueError("work package identity drift")
    if source["predecessor"]["head_sha"] != "b6e6ba2a8408b7634a0d7e31980f5b505bc726a5":
        raise ValueError("predecessor drift")
    expected_defects = [
        "WS6-QUALITY-005",
        "WS6-CODEXPREP-001",
        "WS6-CODEXPREP-002",
        "WS6-CODEXPREP-003",
        "WS6-CODEXPREP-004",
        "WS6-CODEXPREP-005",
    ]
    if source["defect_ids"] != expected_defects or source["closed_defects"] != expected_defects:
        raise ValueError("defect set drift")
    if [item["id"] for item in source["operational_signals"]] != OP_IDS:
        raise ValueError("operational signal order drift")
    if [item["field"] for item in source["learning_metrics"]] != LEARNING_FIELDS:
        raise ValueError("learning metric order drift")

    for item in source["operational_signals"]:
        required = ("source", "fields", "privacy", "retention", "availability", "evidence")
        if not all(key in item for key in required):
            raise ValueError("operational signal metadata incomplete")
        if item["collect"] or item["export"] or item["raw_content"]:
            raise ValueError("operational signal widened beyond planning boundary")

    for item in source["learning_metrics"]:
        if item["measurement"] != ["IMP-P12", "P12.3"]:
            raise ValueError("learning metric canonical measurement drift")
        if item["collect"] or item["raw_free_text"] or item["real_client"]:
            raise ValueError("learning metric widened beyond planning boundary")

    privacy_false = (
        "telemetry_default",
        "export_default",
        "raw_prompt",
        "raw_document",
        "secret_fields",
        "client_identity_pre_authorization",
    )
    if any(source["privacy"][key] for key in privacy_false):
        raise ValueError("privacy defaults widened")
    if source["remaining_preparation_defects"]:
        raise ValueError("WS6.13 must close its preparation defects")
    if source["remaining_blocking_defects"] != ["WS6-BLOCK-006"]:
        raise ValueError("blocking defect set drift")
    completion = source["completion"]
    if completion["next_permitted_work_package"] != "WS6.14":
        raise ValueError("next package drift")
    if completion["implementation_complete"] or completion["telemetry_enabled"]:
        raise ValueError("implementation or telemetry falsely claimed")
    boundaries = source["boundaries"]
    if boundaries["founder_accountability_preserved"] is not True:
        raise ValueError("Founder accountability must be preserved")
    if any(
        value is not False
        for key, value in boundaries.items()
        if key != "founder_accountability_preserved"
    ):
        raise ValueError("authorization boundary widened")

    if [item["id"] for item in blueprint["tasks"]] != ["P0.1", "P0.2", "P0.3", "P0.4"]:
        raise ValueError("Phase-0 task order drift")
    if blueprint["status"] != "planned_not_implemented" or blueprint["implementation_started"]:
        raise ValueError("Phase-0 implementation falsely started")
    if len(blueprint["services"]) != 4:
        raise ValueError("local service topology drift")
    if any(item["bind"] != "127.0.0.1" for item in blueprint["services"]):
        raise ValueError("local service binding widened")
    if blueprint["network"] != {
        "binding": "loopback_only",
        "external_default": "denied",
        "paid_cloud": False,
    }:
        raise ValueError("network policy drift")
    if any(blueprint["guards"].values()):
        raise ValueError("implementation guard widened")


def main() -> None:
    source = load(SRC)
    blueprint = load(BP_SRC)
    validate_source(source, blueprint)

    generated = build_records()
    paths = (OUT, BP_OUT, API_OUT, KNOW_OUT, REG, OVERLAY, DOC, REPORT)
    for path, value in zip(paths, generated, strict=True):
        expected = value if isinstance(value, str) else canonical(value)
        if path.read_text(encoding="utf-8") != expected:
            raise ValueError(f"stale generated file: {path.relative_to(ROOT)}")

    operational, blueprint_contract, api, knowledge, registry, overlay, _, _ = generated
    jsonschema.validate(
        operational, load(ROOT / "schemas/operational-quality-specification.schema.json")
    )
    jsonschema.validate(
        blueprint_contract, load(ROOT / "schemas/phase0-implementation-blueprint.schema.json")
    )

    obligation_map = load(IOM)
    owned = [
        item
        for item in obligation_map["obligations"]
        if item.get("test_registration_owner") == "WS6.13"
    ]
    if len(owned) != 16:
        raise ValueError("WS6.13 registration ownership count drift")
    if any(item["phase_id"] != "IMP-P0" or not item["blocks_imp_p0"] for item in owned):
        raise ValueError("WS6.13 registration ownership phase drift")
    ownership = {
        item["criterion_id"]: (
            item["phase_id"],
            item["task_id"],
            item["component_id"],
            item["evidence_type"],
        )
        for item in obligation_map["obligations"]
    }
    for item in source["operational_signals"]:
        observed = tuple(item["owner"]) + (item["evidence"],)
        if observed != ownership[item["id"]]:
            raise ValueError(f"ownership drift: {item['id']}")

    expected_counts = {
        "phase0_criteria": 16,
        "developer_cases": 60,
        "phase0_total": 76,
        "conformance": 7,
        "planned_total": 83,
        "executable": 0,
        "evidence": 0,
    }
    if registry["counts"] != expected_counts:
        raise ValueError("planned registry count drift")
    grouped = (
        registry["phase0_obligation_registrations"]
        + registry["developer_command_cases"]
        + registry["workflow_agent_conformance_cases"]
    )
    if len(grouped) != 83 or len({item["id"] for item in grouped}) != 83:
        raise ValueError("planned registry identity drift")
    defaults = registry["defaults"]
    if (
        defaults["registration_status"] != "registered_planned"
        or defaults["executable"]
        or defaults["evidence_satisfied"]
        or defaults["provider_execution_required_preimplementation"]
    ):
        raise ValueError("planned test defaults widened")
    if overlay["registration_count"] != 16 or len(overlay["registrations"]) != 16:
        raise ValueError("obligation overlay count drift")
    if not overlay["source_map_immutable"]:
        raise ValueError("WS6.9 obligation map must remain immutable")
    if api["binding"] != "loopback_only" or api["external_binding"] or api["runtime_active"]:
        raise ValueError("API shell widened")
    if any(item["method"] != "GET" for item in api["endpoints"]):
        raise ValueError("API shell must remain read-only")
    if (
        knowledge["ingestion"]["real_document_import"]
        or knowledge["external_object_storage"]
        or knowledge["credentials_required"]
        or knowledge["runtime_active"]
    ):
        raise ValueError("knowledge topology widened")

    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.update(work_package_id="WS6.14"),
        lambda value: value["predecessor"].update(head_sha="bad"),
        lambda value: value.update(defect_ids=[]),
        lambda value: value.update(closed_defects=[]),
        lambda value: value["privacy"].update(telemetry_default=True),
        lambda value: value["privacy"].update(export_default=True),
        lambda value: value["privacy"].update(raw_prompt=True),
        lambda value: value["privacy"].update(raw_document=True),
        lambda value: value["privacy"].update(secret_fields=True),
        lambda value: value["privacy"].update(client_identity_pre_authorization=True),
        lambda value: value["operational_signals"][0].update(collect=True),
        lambda value: value["operational_signals"][0].update(export=True),
        lambda value: value["operational_signals"][0].update(raw_content=True),
        lambda value: value["learning_metrics"][0].update(collect=True),
        lambda value: value["learning_metrics"][0].update(raw_free_text=True),
        lambda value: value["learning_metrics"][0].update(real_client=True),
        lambda value: value["learning_metrics"][0].update(measurement=["IMP-P3", "P3.3"]),
        lambda value: value.update(remaining_preparation_defects=["x"]),
        lambda value: value.update(remaining_blocking_defects=[]),
        lambda value: value["completion"].update(next_permitted_work_package="IMP-P0"),
        lambda value: value["completion"].update(implementation_complete=True),
        lambda value: value["completion"].update(telemetry_enabled=True),
        lambda value: value["boundaries"].update(codex_start_authorized=True),
        lambda value: value["boundaries"].update(external_actions_authorized=True),
    ]
    rejected = 0
    for mutator in mutations:
        candidate = copy.deepcopy(source)
        mutator(candidate)
        try:
            validate_source(candidate, blueprint)
        except (KeyError, TypeError, ValueError):
            rejected += 1
    if rejected != len(mutations):
        raise ValueError("mutation rejection incomplete")

    print(
        f"WS6.13 operational quality specification passed: {rejected} mutations rejected, "
        "operational=8, learning=11, phase0_registered=76, conformance=7, "
        "executable=0, telemetry=false, next=WS6.14, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
