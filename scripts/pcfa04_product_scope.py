from __future__ import annotations

import copy
from collections import Counter
from typing import Any

from codex_phase0_launch_core import CURRENT_STATE_PATH, ROOT, digest_file, load_json

PRODUCT_SCOPE_PATH = ROOT / "repository" / "pcfa04-product-scope-implementation-addendum.json"

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


def product_scope_failures(
    state: dict[str, Any],
    record: dict[str, Any] | None = None,
) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    if not PRODUCT_SCOPE_PATH.is_file():
        return ["PCFA-04 product-scope implementation addendum is missing"]
    value = record or load_json(PRODUCT_SCOPE_PATH)
    authority = state.get("current_authority", {})
    readiness = state.get("repository_readiness", {})
    target = state.get("launch_target", {})
    boundary = value.get("scope_boundary", {})
    package_boundaries = value.get("boundaries", {})
    requirements = value.get("requirements", [])
    areas = value.get("product_areas", [])

    require(value.get("work_package_id") == "PCFA-04", "PCFA-04 product-scope identity is invalid")
    require(
        value.get("addendum_id") == "PRODUCT-SCOPE-IMPLEMENTATION-ADDENDUM",
        "PCFA-04 addendum identity drifted",
    )
    require(
        value.get("status") == "repository_specification_complete_planned_not_implemented",
        "PCFA-04 product-scope status drifted",
    )
    require(
        authority.get("product_scope_addendum")
        == "repository/pcfa04-product-scope-implementation-addendum.json",
        "current operational state does not reference the PCFA-04 product-scope addendum",
    )
    require(
        authority.get("product_scope_addendum_sha256") == digest_file(PRODUCT_SCOPE_PATH),
        "current operational state does not bind the exact PCFA-04 product-scope digest",
    )
    require(
        readiness.get("pcfa04_product_scope_addendum_complete") is True,
        "current operational state does not mark PCFA-04 complete",
    )
    require(
        boundary.get("specification_only") is True
        and boundary.get("product_runtime_implemented") is False
        and boundary.get("canonical_state_mutation_implemented") is False
        and boundary.get("imp_phase_scope_widened") is False
        and boundary.get("codex_start_authorized") is False
        and boundary.get("pcfa05_mvcl_contract_required") is True
        and boundary.get("pcfa07_registry_reconciliation_required") is True,
        "PCFA-04 specification/implementation boundary drifted",
    )
    require(
        target.get("permitted_tasks") == ["P0.1", "P0.2", "P0.3", "P0.4"]
        and target.get("permitted_phase") == "Codex Phase 0 only",
        "PCFA-04 cannot widen the current Codex Phase 0 launch target",
    )

    requirement_ids = [
        item.get("id")
        for item in requirements
        if isinstance(item, dict)
    ] if isinstance(requirements, list) else []
    cq_ids = {
        item
        for item in requirement_ids
        if isinstance(item, str) and item.startswith("CQ-")
    }
    ps_ids = {
        item
        for item in requirement_ids
        if isinstance(item, str) and item.startswith("PS-")
    }
    require(
        isinstance(requirements, list)
        and len(requirements) == 29
        and len(requirement_ids) == 29
        and len(set(requirement_ids)) == 29
        and cq_ids == REQUIRED_CQ
        and ps_ids == REQUIRED_PS
        and all(
            isinstance(item, dict)
            and item.get("status") == "planned_not_implemented"
            and bool(item.get("statement"))
            and bool(item.get("acceptance"))
            for item in requirements
        ),
        "PCFA-04 exact requirement identities or planned_not_implemented semantics drifted",
    )

    area_ids = [
        item.get("area_id")
        for item in areas
        if isinstance(item, dict)
    ] if isinstance(areas, list) else []
    references = [
        requirement_id
        for area in areas
        if isinstance(area, dict)
        for requirement_id in area.get("requirement_ids", [])
    ] if isinstance(areas, list) else []
    reference_counts = Counter(references)
    require(
        isinstance(areas, list)
        and len(areas) == 14
        and len(area_ids) == 14
        and set(area_ids) == REQUIRED_AREA_IDS
        and len(set(area_ids)) == 14
        and set(references) == set(requirement_ids)
        and all(reference_counts[requirement_id] == 1 for requirement_id in requirement_ids)
        and all(
            isinstance(item, dict)
            and item.get("status") == "planned_not_implemented"
            and bool(item.get("owning_imp_phases"))
            and bool(item.get("integration_points"))
            and "IMP-P0" not in item.get("owning_imp_phases", [])
            for item in areas
        ),
        "PCFA-04 exact product-area ownership/reference semantics drifted or widened IMP-P0",
    )
    require(
        set(value.get("phase_ownership_summary", {}))
        == {f"IMP-P{index}" for index in range(13)},
        "PCFA-04 phase ownership summary no longer covers IMP-P0 through IMP-P12",
    )
    reconciliation = value.get("pcfa07_reconciliation_contract", {})
    require(
        isinstance(reconciliation, dict)
        and len(reconciliation) == 6
        and all(item is True for item in reconciliation.values()),
        "PCFA-04 PCFA-07 reconciliation contract drifted",
    )
    require(
        package_boundaries.get("founder_accountability_preserved") is True
        and all(
            item is False
            for key, item in package_boundaries.items()
            if key != "founder_accountability_preserved"
        ),
        "PCFA-04 authorization boundaries must remain fail-closed",
    )
    require(len(digest_file(CURRENT_STATE_PATH)) == 64, "current operational-state digest is unavailable")
    return failures


def run_self_test(state: dict[str, Any]) -> int:
    record = load_json(PRODUCT_SCOPE_PATH)
    failures = product_scope_failures(state, record)
    if failures:
        raise SystemExit("PCFA-04 launch-scope contract was rejected: " + "; ".join(failures))

    rejected = 0
    state_mutations: list[tuple[str, tuple[str, ...], Any]] = [
        (
            "product-scope authority removed",
            ("current_authority", "product_scope_addendum"),
            "docs/11-BUILD-BACKLOG.md",
        ),
        (
            "product-scope digest drift",
            ("current_authority", "product_scope_addendum_sha256"),
            "d" * 64,
        ),
        (
            "PCFA-04 readiness disabled",
            ("repository_readiness", "pcfa04_product_scope_addendum_complete"),
            False,
        ),
        ("Phase 0 scope widened", ("launch_target", "permitted_tasks"), ["P0.1", "P1.1"]),
    ]
    for label, path, replacement in state_mutations:
        mutated = copy.deepcopy(state)
        node: Any = mutated
        for part in path[:-1]:
            node = node[part]
        node[path[-1]] = replacement
        if not product_scope_failures(mutated, record):
            raise SystemExit(f"PCFA-04 launch-state mutation was not rejected: {label}")
        rejected += 1

    record_mutations: list[tuple[str, tuple[str, ...], Any]] = [
        ("runtime implemented", ("scope_boundary", "product_runtime_implemented"), True),
        ("MVCL no longer required", ("scope_boundary", "pcfa05_mvcl_contract_required"), False),
        ("registry reconciliation no longer required", ("scope_boundary", "pcfa07_registry_reconciliation_required"), False),
        ("Codex pre-authorized", ("boundaries", "codex_start_authorized"), True),
        ("requirement implemented", ("requirements", "0", "status"), "implemented"),
        ("CQ semantic substitution", ("requirements", "7", "id"), "CQ-OTHER"),
        ("duplicate requirement ownership", ("product_areas", "1", "requirement_ids"), ["PS-MANDATE-001"]),
        ("IMP-P0 product owner", ("product_areas", "0", "owning_imp_phases"), ["IMP-P0"]),
    ]
    for label, path, replacement in record_mutations:
        mutated = copy.deepcopy(record)
        node: Any = mutated
        for part in path[:-1]:
            node = node[int(part)] if part.isdigit() else node[part]
        final = path[-1]
        if final.isdigit():
            node[int(final)] = replacement
        else:
            node[final] = replacement
        if not product_scope_failures(state, mutated):
            raise SystemExit(f"PCFA-04 launch-record mutation was not rejected: {label}")
        rejected += 1
    return rejected
