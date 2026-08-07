from __future__ import annotations

import copy
from typing import Any

from codex_phase0_launch_core import CURRENT_STATE_PATH, ROOT, digest_file, load_json

MVCL_PATH = ROOT / "repository" / "pcfa05-minimum-valuable-consulting-loop.json"

REQUIRED_TRUTH_CHAIN = [
    "opportunity",
    "mandate",
    "engagement",
    "decision_framing",
    "hypothesis_tree",
    "research_plan",
    "evidence",
    "claim_ledger",
    "method",
    "analysis_and_value",
    "options",
    "recommendation",
    "founder_decision",
    "storyline",
    "deliverables",
    "independent_qa",
    "implementation_initiatives",
    "benefits",
    "closeout",
]
REQUIRED_STAGE_IDS = [f"MVCL-{index:02d}" for index in range(1, 20)]
REQUIRED_INVARIANTS = {
    "MVCL-INV-ENGAGEMENT-ID",
    "MVCL-INV-CANONICAL-STATE",
    "MVCL-INV-CLAIM-TRACE",
    "MVCL-INV-NUMBER-REPRO",
    "MVCL-INV-CONTRARY-EVIDENCE",
    "MVCL-INV-METHOD-JUSTIFICATION",
    "MVCL-INV-IDEMPOTENCY",
    "MVCL-INV-EXACT-APPROVAL",
    "MVCL-INV-RESTART-SAFE",
    "MVCL-INV-INDEPENDENT-QA",
    "MVCL-INV-CROSS-FORMAT",
    "MVCL-INV-REC-TO-BENEFIT",
    "MVCL-INV-AUDIT-HISTORY",
    "MVCL-INV-FOUNDER-CONTROL",
    "MVCL-INV-NO-SELF-APPROVAL",
}
REQUIRED_NEGATIVE_CASES = {f"MVCL-NEG-{index:02d}" for index in range(1, 14)}
REQUIRED_INTERRUPTS = {f"MVCL-FI-{index:02d}" for index in range(1, 7)}


def mvcl_failures(
    state: dict[str, Any],
    record: dict[str, Any] | None = None,
) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    if not MVCL_PATH.is_file():
        return ["PCFA-05 Minimum Valuable Consulting Loop contract is missing"]
    value = record or load_json(MVCL_PATH)
    authority = state.get("current_authority", {})
    readiness = state.get("repository_readiness", {})
    target = state.get("launch_target", {})
    scope = value.get("scope_boundary", {})
    boundaries = value.get("boundaries", {})

    require(value.get("work_package_id") == "PCFA-05", "PCFA-05 MVCL identity is invalid")
    require(
        value.get("contract_id") == "MINIMUM-VALUABLE-CONSULTING-LOOP",
        "PCFA-05 MVCL contract identity drifted",
    )
    require(
        value.get("status") == "repository_specification_complete_planned_not_implemented",
        "PCFA-05 MVCL status drifted",
    )
    require(
        authority.get("mvcl_contract") == "repository/pcfa05-minimum-valuable-consulting-loop.json",
        "current operational state does not reference the PCFA-05 MVCL contract",
    )
    require(
        authority.get("mvcl_contract_sha256") == digest_file(MVCL_PATH),
        "current operational state does not bind the exact PCFA-05 MVCL digest",
    )
    require(
        readiness.get("pcfa05_mvcl_contract_complete") is True,
        "current operational state does not mark PCFA-05 complete",
    )
    require(
        scope.get("specification_only") is True
        and scope.get("product_runtime_implemented") is False
        and scope.get("workflow_runtime_implemented") is False
        and scope.get("canonical_state_mutation_implemented") is False
        and scope.get("imp_phase_scope_widened") is False
        and scope.get("codex_start_authorized") is False
        and scope.get("pcfa07_registry_reconciliation_required") is True
        and scope.get("pcfa08_final_acceptance_required") is True,
        "PCFA-05 specification/implementation boundary drifted",
    )
    require(
        target.get("permitted_tasks") == ["P0.1", "P0.2", "P0.3", "P0.4"]
        and target.get("permitted_phase") == "Codex Phase 0 only",
        "PCFA-05 cannot widen the current Codex Phase 0 launch target",
    )

    require(
        value.get("truth_chain") == REQUIRED_TRUTH_CHAIN,
        "PCFA-05 consulting truth-chain order or identity drifted",
    )
    stages = value.get("stages", [])
    stage_ids = [item.get("stage_id") for item in stages if isinstance(item, dict)] if isinstance(stages, list) else []
    stage_names = [item.get("name") for item in stages if isinstance(item, dict)] if isinstance(stages, list) else []
    require(
        isinstance(stages, list)
        and len(stages) == 19
        and stage_ids == REQUIRED_STAGE_IDS
        and stage_names == REQUIRED_TRUTH_CHAIN
        and all(
            isinstance(item, dict)
            and item.get("status") == "planned_not_implemented"
            and bool(item.get("purpose"))
            and bool(item.get("canonical_outputs"))
            and bool(item.get("owning_imp_phases"))
            and bool(item.get("integration_points"))
            and "IMP-P0" not in item.get("owning_imp_phases", [])
            and bool(item.get("founder_gate"))
            for item in stages
        ),
        "PCFA-05 exact stage sequence, ownership or planned_not_implemented semantics drifted",
    )

    invariants = value.get("loop_invariants", [])
    invariant_ids = {item.get("id") for item in invariants if isinstance(item, dict)} if isinstance(invariants, list) else set()
    require(
        isinstance(invariants, list)
        and len(invariants) == 15
        and invariant_ids == REQUIRED_INVARIANTS
        and all(isinstance(item, dict) and bool(item.get("statement")) for item in invariants),
        "PCFA-05 loop invariant identities drifted",
    )

    cases = value.get("negative_cases", [])
    case_ids = {item.get("case_id") for item in cases if isinstance(item, dict)} if isinstance(cases, list) else set()
    require(
        isinstance(cases, list)
        and len(cases) == 13
        and case_ids == REQUIRED_NEGATIVE_CASES
        and all(
            isinstance(item, dict) and bool(item.get("name")) and bool(item.get("expected"))
            for item in cases
        ),
        "PCFA-05 negative-path case identities drifted",
    )

    interrupts = value.get("founder_interrupts", [])
    interrupt_ids = {item.get("interrupt_id") for item in interrupts if isinstance(item, dict)} if isinstance(interrupts, list) else set()
    referenced_stage_ids = {
        stage_id
        for item in interrupts
        if isinstance(item, dict)
        for stage_id in item.get("stage_ids", [])
    } if isinstance(interrupts, list) else set()
    require(
        isinstance(interrupts, list)
        and len(interrupts) == 6
        and interrupt_ids == REQUIRED_INTERRUPTS
        and referenced_stage_ids.issubset(set(REQUIRED_STAGE_IDS))
        and all(
            isinstance(item, dict)
            and bool(item.get("trigger"))
            and bool(item.get("stage_ids"))
            and bool(item.get("permitted_outcomes"))
            for item in interrupts
        ),
        "PCFA-05 Founder interrupt identities or stage bindings drifted",
    )

    transition = value.get("transition_policy", {})
    require(
        transition.get("forward_sequence_required") is True
        and transition.get("stage_skipping_default") is False
        and transition.get("recycle_to_affected_prior_stage_allowed") is True
        and transition.get("recycle_requires_reason_and_audit_record") is True
        and transition.get("pause_resume_requires_durable_checkpoint") is True
        and transition.get("founder_cancel_prohibits_further_execution") is True
        and transition.get("blocking_defect_prohibits_release") is True
        and transition.get("stale_approval_prohibits_resume") is True
        and transition.get("duplicate_effects_prohibited") is True
        and set(transition.get("terminal_states", [])) == {"completed", "cancelled", "blocked", "paused"},
        "PCFA-05 transition, recycle, approval or idempotency policy drifted",
    )
    reconciliation = value.get("pcfa07_reconciliation_contract", {})
    require(
        isinstance(reconciliation, dict)
        and len(reconciliation) == 8
        and all(item is True for item in reconciliation.values()),
        "PCFA-05 PCFA-07 reconciliation contract drifted",
    )
    require(
        boundaries.get("founder_accountability_preserved") is True
        and all(item is False for key, item in boundaries.items() if key != "founder_accountability_preserved"),
        "PCFA-05 authorization boundaries must remain fail-closed",
    )
    require(len(digest_file(CURRENT_STATE_PATH)) == 64, "current operational-state digest is unavailable")
    return failures


def run_self_test(state: dict[str, Any]) -> int:
    record = load_json(MVCL_PATH)
    failures = mvcl_failures(state, record)
    if failures:
        raise SystemExit("PCFA-05 MVCL launch contract was rejected: " + "; ".join(failures))

    rejected = 0
    state_mutations: list[tuple[str, tuple[str, ...], Any]] = [
        (
            "MVCL authority removed",
            ("current_authority", "mvcl_contract"),
            "contracts/northstar-integration-blueprint.json",
        ),
        (
            "MVCL digest drift",
            ("current_authority", "mvcl_contract_sha256"),
            "e" * 64,
        ),
        (
            "PCFA-05 readiness disabled",
            ("repository_readiness", "pcfa05_mvcl_contract_complete"),
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
        if not mvcl_failures(mutated, record):
            raise SystemExit(f"PCFA-05 launch-state mutation was not rejected: {label}")
        rejected += 1

    record_mutations: list[tuple[str, tuple[str, ...], Any]] = [
        ("workflow runtime implemented", ("scope_boundary", "workflow_runtime_implemented"), True),
        ("stage falsely implemented", ("stages", "0", "status"), "implemented"),
        ("stage identity substitution", ("stages", "0", "stage_id"), "MVCL-99"),
        ("truth-chain reorder", ("truth_chain",), list(reversed(REQUIRED_TRUTH_CHAIN))),
        ("invariant substitution", ("loop_invariants", "0", "id"), "MVCL-INV-OTHER"),
        ("negative-case substitution", ("negative_cases", "0", "case_id"), "MVCL-NEG-99"),
        ("Founder interrupt invalid stage", ("founder_interrupts", "0", "stage_ids"), ["MVCL-99"]),
        ("stale approval allowed", ("transition_policy", "stale_approval_prohibits_resume"), False),
        ("duplicate effects allowed", ("transition_policy", "duplicate_effects_prohibited"), False),
        ("PCFA-07 reconciliation removed", ("pcfa07_reconciliation_contract", "every_stage_must_receive_planned_test_ids"), False),
        ("PCFA-08 final acceptance removed", ("scope_boundary", "pcfa08_final_acceptance_required"), False),
        ("Codex pre-authorized", ("boundaries", "codex_start_authorized"), True),
    ]
    for label, path, replacement in record_mutations:
        mutated = copy.deepcopy(record)
        if len(path) == 1:
            mutated[path[0]] = replacement
        else:
            node = mutated
            for part in path[:-1]:
                node = node[int(part)] if part.isdigit() else node[part]
            final = path[-1]
            if final.isdigit():
                node[int(final)] = replacement
            else:
                node[final] = replacement
        if not mvcl_failures(state, mutated):
            raise SystemExit(f"PCFA-05 launch-record mutation was not rejected: {label}")
        rejected += 1
    return rejected
