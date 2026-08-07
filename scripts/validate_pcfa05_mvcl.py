from __future__ import annotations

import copy
import re
from typing import Any

from jsonschema import Draft202012Validator

from build_pcfa05_mvcl import REPORT_PATH, build_records
from codex_phase0_launch_core import CURRENT_STATE_PATH, ROOT, load_json
from pcfa05_mvcl import (
    MVCL_PATH,
    REQUIRED_INTERRUPTS,
    REQUIRED_INVARIANTS,
    REQUIRED_NEGATIVE_CASES,
    REQUIRED_STAGE_IDS,
    REQUIRED_TRUTH_CHAIN,
    mvcl_failures,
    run_self_test,
)

SCHEMA_PATH = ROOT / "schemas" / "pcfa05-minimum-valuable-consulting-loop.schema.json"
BACKLOG_PATH = ROOT / "docs" / "11-BUILD-BACKLOG.md"
DOC_PATH = ROOT / "docs" / "72-PCFA-05-MINIMUM-VALUABLE-CONSULTING-LOOP.md"
STATUS_PATH = ROOT / "docs" / "CURRENT-OPERATIONAL-STATE.md"
HANDOFF_PATH = ROOT / "handoff" / "codex-phase0-current-handoff.json"
ISSUE1_PATH = ROOT / "handoff" / "codex-phase0-current-issue.md"
AGENTS_PATH = ROOT / "AGENTS.md"
NORTHSTAR_PATH = ROOT / "contracts" / "northstar-integration-blueprint.json"
PRODUCT_SCOPE_PATH = ROOT / "repository" / "pcfa04-product-scope-implementation-addendum.json"

REQUIRED_NEGATIVE_NAMES = {
    "missing_material_evidence",
    "material_contradicting_evidence",
    "approval_wait",
    "stale_approval_after_material_change",
    "restart_after_checkpoint",
    "duplicate_command_or_action",
    "founder_cancellation",
    "blocking_qa_defect",
    "cross_engagement_access_attempt",
    "malicious_or_instruction_bearing_document",
    "provider_or_agent_runtime_failure",
    "numeric_or_formula_defect",
    "renderer_or_cross_format_reconciliation_defect",
}
REQUIRED_NORTHSTAR_SCENARIOS = {
    "restart_after_analysis_checkpoint",
    "approval_wait_and_resume",
    "blocking_quality_defect_recycle",
    "idempotent_release_replay",
    "founder_cancellation",
    "tenant_and_data_boundary_rejection",
}
REQUIRED_PCFA04_REQUIREMENTS = {
    "PS-MANDATE-001",
    "PS-ENGAGEMENT-001",
    "PS-QA-001",
    "PS-IMPLEMENTATION-001",
    "PS-ROUNDTRIP-001",
    "PS-REVIEW-001",
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

    stages = record.get("stages", [])
    stage_ids = [item.get("stage_id") for item in stages if isinstance(item, dict)]
    stage_names = [item.get("name") for item in stages if isinstance(item, dict)]
    invariants = record.get("loop_invariants", [])
    invariant_ids = {item.get("id") for item in invariants if isinstance(item, dict)}
    cases = record.get("negative_cases", [])
    case_ids = {item.get("case_id") for item in cases if isinstance(item, dict)}
    case_names = {item.get("name") for item in cases if isinstance(item, dict)}
    interrupts = record.get("founder_interrupts", [])
    interrupt_ids = {item.get("interrupt_id") for item in interrupts if isinstance(item, dict)}

    require(record.get("truth_chain") == REQUIRED_TRUTH_CHAIN, "MVCL truth chain drifted")
    require(
        len(stages) == 19
        and stage_ids == REQUIRED_STAGE_IDS
        and stage_names == REQUIRED_TRUTH_CHAIN,
        "MVCL stage sequence or identities drifted",
    )
    require(
        all(
            isinstance(item, dict)
            and item.get("status") == "planned_not_implemented"
            and item.get("owning_imp_phases")
            and item.get("integration_points")
            and item.get("canonical_outputs")
            and item.get("founder_gate")
            and "IMP-P0" not in item.get("owning_imp_phases", [])
            for item in stages
        ),
        "MVCL stage ownership/status invariant failed",
    )
    require(
        len(invariants) == 15 and invariant_ids == REQUIRED_INVARIANTS,
        "MVCL invariant family is incomplete",
    )
    require(
        len(cases) == 13
        and case_ids == REQUIRED_NEGATIVE_CASES
        and case_names == REQUIRED_NEGATIVE_NAMES,
        "MVCL negative-case family drifted",
    )
    require(
        len(interrupts) == 6 and interrupt_ids == REQUIRED_INTERRUPTS,
        "MVCL Founder interrupt family drifted",
    )
    discretionary = next(
        (item for item in interrupts if item.get("interrupt_id") == "MVCL-FI-06"),
        {},
    )
    require(
        set(discretionary.get("stage_ids", [])) == set(REQUIRED_STAGE_IDS),
        "Founder discretionary recycle/pause/cancel/stop control must cover every MVCL stage",
    )
    transition = record.get("transition_policy", {})
    require(
        transition.get("forward_sequence_required") is True
        and transition.get("stage_skipping_default") is False
        and transition.get("recycle_to_affected_prior_stage_allowed") is True
        and transition.get("recycle_requires_reason_and_audit_record") is True
        and transition.get("pause_resume_requires_durable_checkpoint") is True
        and transition.get("founder_cancel_prohibits_further_execution") is True
        and transition.get("blocking_defect_prohibits_release") is True
        and transition.get("stale_approval_prohibits_resume") is True
        and transition.get("duplicate_effects_prohibited") is True,
        "MVCL transition/recycle/restart/idempotency controls drifted",
    )
    reconciliation = record.get("pcfa07_reconciliation_contract", {})
    require(
        isinstance(reconciliation, dict)
        and len(reconciliation) == 8
        and all(value is True for value in reconciliation.values()),
        "MVCL PCFA-07 reconciliation contract drifted",
    )
    boundaries = record.get("boundaries", {})
    require(
        boundaries.get("founder_accountability_preserved") is True
        and all(value is False for key, value in boundaries.items() if key != "founder_accountability_preserved"),
        "MVCL authorization boundaries drifted",
    )
    return failures


def _validate_backlog_bindings(record: dict[str, Any]) -> None:
    text = BACKLOG_PATH.read_text(encoding="utf-8")
    task_ids = set(re.findall(r"^### (P(?:[0-9]|1[0-2])\.[0-9]+)\b", text, flags=re.MULTILINE))
    referenced = {
        task
        for stage in record["stages"]
        for task in stage["integration_points"]
    }
    missing = sorted(referenced - task_ids)
    _require(not missing, "PCFA-05 references missing existing backlog tasks: " + ", ".join(missing))


def _validate_prior_authorities(record: dict[str, Any]) -> None:
    agents = AGENTS_PATH.read_text(encoding="utf-8")
    _require(
        "decision → question → hypothesis → evidence → analysis → option → recommendation → implementation → benefit" in agents,
        "AGENTS consulting truth model drifted",
    )
    northstar = load_json(NORTHSTAR_PATH)
    scenario_names = {item.get("name") for item in northstar.get("e2e_scenarios", [])}
    _require(
        len(northstar.get("journey_stages", [])) == 13
        and REQUIRED_NORTHSTAR_SCENARIOS.issubset(scenario_names),
        "PCFA-05 no longer preserves the accepted Northstar restart/approval/recycle/idempotency/cancellation/isolation baseline",
    )
    obligations = set(northstar.get("acceptance_obligations", []))
    for required in (
        "restart_resumes_from_last_durable_checkpoint",
        "idempotent_commands_do_not_duplicate_effects",
        "independent_quality_context_is_separate_from_creator_context",
        "founder_approval_is_scoped_to_exact_version_and_action",
        "benefits_use_baseline_counterfactual_owner_and_verification",
    ):
        _require(required in obligations, f"Northstar acceptance obligation missing: {required}")

    product_scope = load_json(PRODUCT_SCOPE_PATH)
    requirement_ids = {item.get("id") for item in product_scope.get("requirements", [])}
    _require(
        REQUIRED_PCFA04_REQUIREMENTS.issubset(requirement_ids)
        and product_scope["scope_boundary"].get("pcfa05_mvcl_contract_required") is True,
        "PCFA-05 no longer fulfills the PCFA-04 MVCL dependency",
    )
    _require(
        record["stages"][1]["name"] == "mandate"
        and record["stages"][2]["name"] == "engagement"
        and record["stages"][15]["name"] == "independent_qa"
        and record["stages"][16]["name"] == "implementation_initiatives"
        and record["stages"][17]["name"] == "benefits",
        "PCFA-05 does not preserve PCFA-04 mandate/workspace/QA/implementation-benefits sequencing",
    )


def _validate_current_surfaces(state: dict[str, Any]) -> None:
    handoff = load_json(HANDOFF_PATH)
    _require(
        handoff["authority"].get("mvcl_contract")
        == "repository/pcfa05-minimum-valuable-consulting-loop.json",
        "current handoff omits PCFA-05 MVCL authority",
    )
    _require(
        handoff["readiness"].get("pcfa05_mvcl_contract_complete") is True,
        "current handoff omits PCFA-05 readiness",
    )
    _require(
        "repository/pcfa05-minimum-valuable-consulting-loop.json" in handoff["read_order"]
        and "docs/72-PCFA-05-MINIMUM-VALUABLE-CONSULTING-LOOP.md" in handoff["read_order"],
        "current handoff read order omits PCFA-05",
    )
    _require(
        "python scripts/validate_pcfa05_mvcl.py" in handoff["execution"]["required_commands"],
        "current handoff preflight omits PCFA-05 validation",
    )
    _require(
        state["launch_target"]["permitted_tasks"] == ["P0.1", "P0.2", "P0.3", "P0.4"],
        "PCFA-05 widened the launch target",
    )
    for path, tokens in (
        (ISSUE1_PATH, ("PCFA-05", "Minimum Valuable Consulting Loop", "planned_not_implemented")),
        (STATUS_PATH, ("PCFA-05", "Minimum Valuable Consulting Loop", "planned_not_implemented")),
        (DOC_PATH, ("opportunity → mandate → engagement", "restart-safe", "Founder can recycle")),
    ):
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            _require(token in text, f"{path.relative_to(ROOT)} missing PCFA-05 token: {token}")


def main() -> None:
    record = load_json(MVCL_PATH)
    state = load_json(CURRENT_STATE_PATH)
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(record))
    _require(
        not errors,
        "PCFA-05 schema validation failed: " + "; ".join(error.message for error in errors),
    )

    expected_record, expected_report = build_records()
    _require(record == expected_record, "PCFA-05 generated JSON does not match governed YAML source")
    _require(
        REPORT_PATH.read_text(encoding="utf-8") == expected_report,
        "PCFA-05 generated evidence report drifted",
    )

    semantic = _semantic_failures(record)
    _require(not semantic, "PCFA-05 semantic validation failed: " + "; ".join(semantic))
    launch = mvcl_failures(state, record)
    _require(not launch, "PCFA-05 launch binding failed: " + "; ".join(launch))
    _validate_backlog_bindings(record)
    _validate_prior_authorities(record)
    _validate_current_surfaces(state)

    mutations: list[tuple[str, tuple[str, ...], Any]] = [
        ("stage status", ("stages", "0", "status"), "implemented"),
        ("stage ID", ("stages", "0", "stage_id"), "MVCL-99"),
        ("stage name", ("stages", "0", "name"), "other"),
        ("IMP-P0 owner", ("stages", "0", "owning_imp_phases"), ["IMP-P0"]),
        ("missing integration point", ("stages", "0", "integration_points"), []),
        ("truth chain", ("truth_chain", "0"), "other"),
        ("invariant identity", ("loop_invariants", "0", "id"), "MVCL-INV-OTHER"),
        ("negative case identity", ("negative_cases", "0", "case_id"), "MVCL-NEG-99"),
        ("negative case semantic substitution", ("negative_cases", "0", "name"), "other"),
        ("interrupt identity", ("founder_interrupts", "0", "interrupt_id"), "MVCL-FI-99"),
        ("Founder universal control removed", ("founder_interrupts", "5", "stage_ids"), ["MVCL-01"]),
        ("stage skipping enabled", ("transition_policy", "stage_skipping_default"), True),
        ("restart unsafe", ("transition_policy", "pause_resume_requires_durable_checkpoint"), False),
        ("release despite defect", ("transition_policy", "blocking_defect_prohibits_release"), False),
        ("PCFA-07 mapping removed", ("pcfa07_reconciliation_contract", "every_negative_case_must_receive_planned_test_ids"), False),
        ("runtime implemented", ("scope_boundary", "workflow_runtime_implemented"), True),
        ("Codex authorized", ("boundaries", "codex_start_authorized"), True),
    ]
    rejected = 0
    for label, path, replacement in mutations:
        mutated = copy.deepcopy(record)
        _set(mutated, path, replacement)
        if not _semantic_failures(mutated) and not mvcl_failures(state, mutated):
            raise SystemExit(f"PCFA-05 mutation was not rejected: {label}")
        rejected += 1

    launch_rejected = run_self_test(state)
    print(
        "PCFA-05 Minimum Valuable Consulting Loop validation passed: "
        f"stages={len(record['stages'])}, invariants={len(record['loop_invariants'])}, "
        f"founder_interrupts={len(record['founder_interrupts'])}, "
        f"negative_cases={len(record['negative_cases'])}, semantic_mutations_rejected={rejected}, "
        f"launch_mutations_rejected={launch_rejected}, planned_not_implemented=true, "
        "pcfa07_required=true, pcfa08_required=true, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
