from __future__ import annotations

import copy
from typing import Any

from codex_phase0_launch_core import CURRENT_STATE_PATH, ROOT, digest_file, load_json

PRODUCT_SCOPE_PATH = ROOT / "repository" / "pcfa04-product-scope-implementation-addendum.json"


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
    require(
        isinstance(requirements, list)
        and len(requirements) == 29
        and all(
            isinstance(item, dict) and item.get("status") == "planned_not_implemented"
            for item in requirements
        ),
        "PCFA-04 requirements must remain exactly 29 planned_not_implemented obligations",
    )
    require(
        isinstance(areas, list)
        and len(areas) == 14
        and all(
            isinstance(item, dict)
            and item.get("status") == "planned_not_implemented"
            and "IMP-P0" not in item.get("owning_imp_phases", [])
            for item in areas
        ),
        "PCFA-04 product areas drifted or incorrectly widened IMP-P0 product scope",
    )
    require(
        package_boundaries.get("founder_accountability_preserved") is True
        and all(
            value is False
            for key, value in package_boundaries.items()
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
