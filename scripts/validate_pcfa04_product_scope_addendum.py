from __future__ import annotations

import copy
import re
from collections import Counter
from typing import Any

from jsonschema import Draft202012Validator

from build_pcfa04_product_scope_addendum import REPORT_PATH, build_records
from codex_phase0_launch_core import CURRENT_STATE_PATH, ROOT, load_json
from pcfa04_product_scope import PRODUCT_SCOPE_PATH, product_scope_failures, run_self_test

SCHEMA_PATH = ROOT / "schemas" / "pcfa04-product-scope-implementation-addendum.schema.json"
BACKLOG_PATH = ROOT / "docs" / "11-BUILD-BACKLOG.md"
DOC_PATH = ROOT / "docs" / "71-PCFA-04-PRODUCT-SCOPE-IMPLEMENTATION-ADDENDUM.md"
HANDOFF_PATH = ROOT / "handoff" / "codex-phase0-current-handoff.json"
ISSUE1_PATH = ROOT / "handoff" / "codex-phase0-current-issue.md"
STATUS_PATH = ROOT / "docs" / "CURRENT-OPERATIONAL-STATE.md"

REQUIRED_CQ = {
    "CQ-DECISION",
    "CQ-ANSWER",
    "CQ-TITLE",
    "CQ-STORY",
    "CQ-MECE",
    "CQ-ALT",
    "CQ-UNCERT",
    "CQ-DENSITY",
    "CQ-VISUAL",
    "CQ-HIER",
    "CQ-REDUND",
    "CQ-ACTION",
    "CQ-RISK",
    "CQ-AUDIENCE",
    "CQ-EXEC",
}
REQUIRED_PS = {
    "PS-MANDATE-001",
    "PS-ENGAGEMENT-001",
    "PS-QA-001",
    "PS-IMPLEMENTATION-001",
    "PS-INGEST-001",
    "PS-LOCATOR-001",
    "PS-LIBRARY-001",
    "PS-GOLDEN-001",
    "PS-ROUNDTRIP-001",
    "PS-STYLE-001",
    "PS-ASSET-RIGHTS-001",
    "PS-FOUNDER-ATTENTION-001",
    "PS-DELIVERABLE-VARIANTS-001",
    "PS-REVIEW-001",
}
REQUIRED_AREA_IDS = {
    "PSA-MANDATE",
    "PSA-ENGAGEMENT-WORKSPACE",
    "PSA-QUALITY-CONSOLE",
    "PSA-IMPLEMENTATION-BENEFITS",
    "PSA-INGESTION",
    "PSA-LIBRARY-COMPLETENESS",
    "PSA-CONSULTING-CRAFT",
    "PSA-GOLDEN-OUTPUTS",
    "PSA-OFFICE-ROUNDTRIP",
    "PSA-HOUSE-STYLE",
    "PSA-ASSET-RIGHTS",
    "PSA-FOUNDER-ATTENTION",
    "PSA-DELIVERABLE-VARIANTS",
    "PSA-REVIEW-WORKFLOW",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def _set(value: dict[str, Any], path: tuple[str, ...], replacement: Any) -> None:
    node: Any = value
    for part in path[:-1]:
        node = node[int(part)] if part.isdigit() else node[part]
    final = path[-1]
    if final.isdigit():
        node[int(final)] = replacement
    else:
        node[final] = replacement


def _semantic_failures(record: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    areas = record.get("product_areas", [])
    requirements = record.get("requirements", [])
    area_ids = [item.get("area_id") for item in areas if isinstance(item, dict)]
    requirement_ids = [item.get("id") for item in requirements if isinstance(item, dict)]
    cq_ids = {value for value in requirement_ids if isinstance(value, str) and value.startswith("CQ-")}
    ps_ids = {value for value in requirement_ids if isinstance(value, str) and value.startswith("PS-")}
    references = [
        requirement_id
        for area in areas
        if isinstance(area, dict)
        for requirement_id in area.get("requirement_ids", [])
    ]
    reference_counts = Counter(references)

    require(len(areas) == 14, "PCFA-04 must contain exactly 14 product areas")
    require(
        set(area_ids) == REQUIRED_AREA_IDS and len(area_ids) == len(set(area_ids)),
        "PCFA-04 product-area identities drifted",
    )
    require(len(requirements) == 29, "PCFA-04 must contain exactly 29 requirements")
    require(len(requirement_ids) == len(set(requirement_ids)), "PCFA-04 requirement IDs are not unique")
    require(cq_ids == REQUIRED_CQ, "PCFA-04 Consulting Craft requirement family is incomplete")
    require(ps_ids == REQUIRED_PS, "PCFA-04 product-scope requirement family is incomplete")
    require(
        set(references) == set(requirement_ids)
        and all(reference_counts[requirement_id] == 1 for requirement_id in requirement_ids),
        "every PCFA-04 requirement must be referenced by exactly one product area",
    )
    require(
        all(
            isinstance(item, dict)
            and item.get("status") == "planned_not_implemented"
            and item.get("owning_imp_phases")
            and item.get("integration_points")
            and "IMP-P0" not in item.get("owning_imp_phases", [])
            for item in areas
        ),
        "PCFA-04 product-area ownership/status invariant failed",
    )
    require(
        all(
            isinstance(item, dict)
            and item.get("status") == "planned_not_implemented"
            and bool(item.get("statement"))
            and bool(item.get("acceptance"))
            for item in requirements
        ),
        "PCFA-04 requirements must remain fully specified and planned_not_implemented",
    )
    expected_phases = {f"IMP-P{index}" for index in range(13)}
    require(
        set(record.get("phase_ownership_summary", {})) == expected_phases,
        "PCFA-04 phase ownership summary must cover IMP-P0 through IMP-P12",
    )
    reconciliation = record.get("pcfa07_reconciliation_contract", {})
    require(
        isinstance(reconciliation, dict)
        and len(reconciliation) == 6
        and all(value is True for value in reconciliation.values()),
        "PCFA-04 must preserve the PCFA-07 reconciliation contract",
    )
    boundaries = record.get("boundaries", {})
    require(
        boundaries.get("founder_accountability_preserved") is True
        and all(
            value is False
            for key, value in boundaries.items()
            if key != "founder_accountability_preserved"
        ),
        "PCFA-04 authorization boundaries drifted",
    )
    return failures


def _validate_existing_backlog_bindings(record: dict[str, Any]) -> None:
    text = BACKLOG_PATH.read_text(encoding="utf-8")
    task_ids = set(
        re.findall(r"^### (P(?:[0-9]|1[0-2])\.[0-9]+)\b", text, flags=re.MULTILINE)
    )
    referenced = {
        task
        for area in record["product_areas"]
        for task in area["integration_points"]
    }
    missing = sorted(referenced - task_ids)
    _require(
        not missing,
        "PCFA-04 references missing existing backlog tasks: " + ", ".join(missing),
    )


def _validate_current_surfaces(state: dict[str, Any]) -> None:
    handoff = load_json(HANDOFF_PATH)
    _require(
        handoff["authority"].get("product_scope_addendum")
        == "repository/pcfa04-product-scope-implementation-addendum.json",
        "current handoff omits PCFA-04 authority",
    )
    _require(
        handoff["readiness"].get("pcfa04_product_scope_addendum_complete") is True,
        "current handoff omits PCFA-04 readiness",
    )
    _require(
        "repository/pcfa04-product-scope-implementation-addendum.json" in handoff["read_order"]
        and "docs/71-PCFA-04-PRODUCT-SCOPE-IMPLEMENTATION-ADDENDUM.md"
        in handoff["read_order"],
        "current handoff read order omits PCFA-04",
    )
    _require(
        "python scripts/validate_pcfa04_product_scope_addendum.py"
        in handoff["execution"]["required_commands"],
        "current handoff preflight omits PCFA-04 validation",
    )
    _require(
        state["launch_target"]["permitted_tasks"] == ["P0.1", "P0.2", "P0.3", "P0.4"],
        "PCFA-04 widened the launch target",
    )
    for path, tokens in (
        (ISSUE1_PATH, ("PCFA-04", "product-scope", "planned_not_implemented")),
        (STATUS_PATH, ("PCFA-04", "product-scope", "planned_not_implemented")),
        (DOC_PATH, ("CQ-DECISION", "Office round-trip", "Founder attention burden")),
    ):
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            _require(token in text, f"{path.relative_to(ROOT)} missing PCFA-04 token: {token}")


def main() -> None:
    record = load_json(PRODUCT_SCOPE_PATH)
    state = load_json(CURRENT_STATE_PATH)
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(record))
    _require(
        not errors,
        "PCFA-04 schema validation failed: " + "; ".join(error.message for error in errors),
    )

    expected_record, expected_report = build_records()
    _require(record == expected_record, "PCFA-04 generated JSON does not match governed YAML source")
    _require(
        REPORT_PATH.read_text(encoding="utf-8") == expected_report,
        "PCFA-04 generated evidence report drifted",
    )

    semantic = _semantic_failures(record)
    _require(not semantic, "PCFA-04 semantic validation failed: " + "; ".join(semantic))
    launch = product_scope_failures(state, record)
    _require(not launch, "PCFA-04 launch binding failed: " + "; ".join(launch))
    _validate_existing_backlog_bindings(record)
    _validate_current_surfaces(state)

    mutations: list[tuple[str, tuple[str, ...], Any]] = [
        ("area status", ("product_areas", "0", "status"), "implemented"),
        ("requirement status", ("requirements", "0", "status"), "implemented"),
        ("IMP-P0 owner", ("product_areas", "0", "owning_imp_phases"), ["IMP-P0"]),
        ("missing ownership", ("product_areas", "1", "owning_imp_phases"), []),
        (
            "duplicate requirement reference",
            ("product_areas", "1", "requirement_ids"),
            ["PS-MANDATE-001"],
        ),
        ("CQ family drift", ("requirements", "7", "id"), "CQ-OTHER"),
        ("runtime implemented", ("scope_boundary", "product_runtime_implemented"), True),
        (
            "canonical mutation implemented",
            ("scope_boundary", "canonical_state_mutation_implemented"),
            True,
        ),
        ("P0 scope widened", ("scope_boundary", "imp_phase_scope_widened"), True),
        (
            "MVCL obligation removed",
            ("scope_boundary", "pcfa05_mvcl_contract_required"),
            False,
        ),
        (
            "registry reconciliation removed",
            ("scope_boundary", "pcfa07_registry_reconciliation_required"),
            False,
        ),
        ("Codex authorized", ("boundaries", "codex_start_authorized"), True),
    ]
    rejected = 0
    for label, path, replacement in mutations:
        mutated = copy.deepcopy(record)
        _set(mutated, path, replacement)
        if not _semantic_failures(mutated) and not product_scope_failures(state, mutated):
            raise SystemExit(f"PCFA-04 mutation was not rejected: {label}")
        rejected += 1

    launch_rejected = run_self_test(state)
    print(
        "PCFA-04 product-scope implementation addendum validation passed: "
        f"areas={len(record['product_areas'])}, requirements={len(record['requirements'])}, "
        f"consulting_craft={len(REQUIRED_CQ)}, semantic_mutations_rejected={rejected}, "
        f"launch_mutations_rejected={launch_rejected}, planned_not_implemented=true, "
        "pcfa05_required=true, pcfa07_required=true, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
