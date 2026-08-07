from __future__ import annotations

import copy
from typing import Any

from codex_phase0_launch_core import CURRENT_STATE_PATH, ROOT, digest_file, load_json

HERMES_REFRESH_PATH = ROOT / "repository" / "pcfa06-hermes-bounded-adoption-refresh.json"

REQUIRED_PRINCIPLES = {f"HERMES-BOUND-{index:02d}" for index in range(1, 11)}
REQUIRED_EVIDENCE = {
    "HERMES-EVID-RELEASE",
    "HERMES-EVID-GOAL",
    "HERMES-EVID-DELEGATION",
    "HERMES-EVID-SKILLS",
    "HERMES-EVID-LEARN",
    "HERMES-EVID-MEMORY",
    "HERMES-EVID-CURATOR",
    "HERMES-EVID-MOA",
}
REQUIRED_CAPABILITIES = {
    "HERMES-CAP-SKILLS",
    "HERMES-CAP-LEARN",
    "HERMES-CAP-JOURNEY",
    "HERMES-CAP-GOAL",
    "HERMES-CAP-DELEGATION",
    "HERMES-CAP-MOA",
    "HERMES-CAP-MEMORY",
    "HERMES-CAP-CURATOR",
    "HERMES-CAP-EXECUTE-CODE",
    "HERMES-CAP-EXTERNAL-TOOLS",
    "HERMES-CAP-RUNTIME-SURFACES",
}
REQUIRED_MODES = {
    "HERMES-CAP-SKILLS": "candidate_procedure_library_only",
    "HERMES-CAP-LEARN": "suggestion_only_candidate_drafting",
    "HERMES-CAP-JOURNEY": "read_only_suggestion_observability",
    "HERMES-CAP-GOAL": "workerpackage_completion_adapter_candidate",
    "HERMES-CAP-DELEGATION": "raw_surface_denied_adapter_required",
    "HERMES-CAP-MOA": "model_router_candidate_only",
    "HERMES-CAP-MEMORY": "noncanonical_ephemeral_or_suggestion_only",
    "HERMES-CAP-CURATOR": "disabled_suggestions_may_be_reimplemented_offdata_side",
    "HERMES-CAP-EXECUTE-CODE": "bounded_worker_tool_candidate",
    "HERMES-CAP-EXTERNAL-TOOLS": "denied_until_separate_tool_processor_review",
    "HERMES-CAP-RUNTIME-SURFACES": "deferred_replaceable_runtime_candidates",
}


def hermes_refresh_failures(
    state: dict[str, Any],
    record: dict[str, Any] | None = None,
) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    if not HERMES_REFRESH_PATH.is_file():
        return ["PCFA-06 Hermes bounded-adoption refresh is missing"]
    value = record or load_json(HERMES_REFRESH_PATH)
    authority = state.get("current_authority", {})
    readiness = state.get("repository_readiness", {})
    target = state.get("launch_target", {})
    scope = value.get("scope_boundary", {})
    boundaries = value.get("boundaries", {})
    upstream = value.get("upstream_baseline", {})

    require(value.get("work_package_id") == "PCFA-06", "PCFA-06 Hermes refresh identity is invalid")
    require(
        value.get("contract_id") == "HERMES-BOUNDED-ADOPTION-REFRESH",
        "PCFA-06 Hermes refresh contract identity drifted",
    )
    require(
        value.get("status") == "repository_specification_complete_not_activated",
        "PCFA-06 Hermes refresh status drifted",
    )
    require(
        value.get("assessment_date") == "2026-08-08",
        "PCFA-06 Hermes assessment date drifted",
    )
    require(
        authority.get("hermes_bounded_adoption_refresh")
        == "repository/pcfa06-hermes-bounded-adoption-refresh.json",
        "current operational state does not reference the PCFA-06 Hermes refresh",
    )
    require(
        authority.get("hermes_bounded_adoption_refresh_sha256") == digest_file(HERMES_REFRESH_PATH),
        "current operational state does not bind the exact PCFA-06 Hermes refresh digest",
    )
    require(
        readiness.get("pcfa06_hermes_bounded_adoption_refresh_complete") is True,
        "current operational state does not mark PCFA-06 complete",
    )
    require(
        target.get("permitted_tasks") == ["P0.1", "P0.2", "P0.3", "P0.4"]
        and target.get("permitted_phase") == "Codex Phase 0 only",
        "PCFA-06 cannot widen the current Codex Phase 0 launch target",
    )
    require(
        upstream.get("stable_release") == "v0.18.2"
        and upstream.get("stable_tag") == "v2026.7.7.2"
        and upstream.get("stable_commit") == "9de9c25"
        and upstream.get("predecessor_package") == "PCR-06"
        and upstream.get("predecessor_contract") == "contracts/hermes-compatibility-pack.json"
        and upstream.get("version_change_from_pcr06") is False
        and upstream.get("update_policy") == "pinned_review_required"
        and upstream.get("documentation_snapshot_is_release_pin") is False,
        "PCFA-06 stable-release or documentation-snapshot semantics drifted",
    )
    require(
        scope.get("specification_only") is True
        and scope.get("hermes_installation_authorized") is False
        and scope.get("hermes_runtime_activation_authorized") is False
        and scope.get("hermes_is_control_plane") is False
        and scope.get("hermes_canonical_state_authority") is False
        and scope.get("hermes_skill_promotion_authorized") is False
        and scope.get("hermes_memory_authority") is False
        and scope.get("hermes_background_execution_authorized") is False
        and scope.get("hermes_model_router_authority") is False
        and scope.get("imp_phase0_scope_widened") is False
        and scope.get("codex_start_authorized") is False
        and scope.get("pcfa07_registry_reconciliation_required") is True
        and scope.get("pcfa08_final_acceptance_required") is True,
        "PCFA-06 specification/adoption boundary drifted",
    )

    principles = value.get("operating_principles", [])
    principle_ids = {
        item.get("id") for item in principles if isinstance(item, dict)
    } if isinstance(principles, list) else set()
    require(
        isinstance(principles, list)
        and len(principles) == 10
        and principle_ids == REQUIRED_PRINCIPLES
        and all(isinstance(item, dict) and bool(item.get("statement")) for item in principles),
        "PCFA-06 operating-principle identities drifted",
    )

    evidence = value.get("upstream_evidence", [])
    evidence_ids = {
        item.get("evidence_id") for item in evidence if isinstance(item, dict)
    } if isinstance(evidence, list) else set()
    source_kinds = {
        item.get("source_kind") for item in evidence if isinstance(item, dict)
    } if isinstance(evidence, list) else set()
    require(
        isinstance(evidence, list)
        and len(evidence) == 8
        and evidence_ids == REQUIRED_EVIDENCE
        and source_kinds == {"stable_release", "current_documentation"}
        and all(
            isinstance(item, dict)
            and str(item.get("url", "")).startswith("https://")
            and bool(item.get("observed"))
            for item in evidence
        ),
        "PCFA-06 upstream evidence identities or provenance classification drifted",
    )

    capabilities = value.get("capability_assessments", [])
    capability_ids = {
        item.get("capability_id") for item in capabilities if isinstance(item, dict)
    } if isinstance(capabilities, list) else set()
    capability_map = {
        item["capability_id"]: item
        for item in capabilities
        if isinstance(item, dict) and isinstance(item.get("capability_id"), str)
    } if isinstance(capabilities, list) else {}
    require(
        isinstance(capabilities, list)
        and len(capabilities) == 11
        and capability_ids == REQUIRED_CAPABILITIES
        and all(
            isinstance(item, dict)
            and item.get("status") == "planned_not_implemented"
            and bool(item.get("owning_imp_phases"))
            and bool(item.get("integration_points"))
            and "IMP-P0" not in item.get("owning_imp_phases", [])
            and bool(item.get("required_controls"))
            and bool(item.get("denied_raw_actions"))
            for item in capabilities
        )
        and all(capability_map.get(key, {}).get("offdata_mode") == mode for key, mode in REQUIRED_MODES.items()),
        "PCFA-06 exact capability identities, modes, ownership or planned_not_implemented semantics drifted",
    )

    goal = value.get("worker_goal_mapping", {})
    mapping = goal.get("mapping", {}) if isinstance(goal, dict) else {}
    controls = goal.get("required_runtime_controls", {}) if isinstance(goal, dict) else {}
    require(
        goal.get("raw_goal_authorized") is False
        and goal.get("hermes_goal_state_canonical") is False
        and goal.get("hermes_goal_judge_completion_authority") is False
        and goal.get("offdata_acceptance_completion_authority") is True
        and mapping
        == {
            "outcome": "WorkerPackage.expected_outputs",
            "verification": "WorkerPackage.acceptance",
            "constraints": "WorkerPackage.constraints",
            "boundaries": "WorkerPackage.workspace_tool_and_data_scope",
            "stop_when": "WorkerPackage.escalation_and_stop_conditions",
            "subgoals": "additional_acceptance_criteria_recorded_by_offdata",
        }
        and controls.get("turn_budget_bounded") is True
        and controls.get("automatic_resume_after_budget") is False
        and controls.get("durable_checkpoint_owned_by_offdata") is True
        and controls.get("worker_result_recorded_via_command") is True
        and controls.get("retry_policy_owned_by_offdata") is True
        and controls.get("founder_interrupt_preempts_loop") is True,
        "PCFA-06 /goal to WorkerPackage mapping or completion authority drifted",
    )

    skills = value.get("skills_learning_policy", {})
    require(
        skills.get("canonical_repository_skill_glob") == "agents/*/SKILL.md"
        and skills.get("hermes_local_skills_canonical") is False
        and skills.get("bundled_skills_status") == "candidate_only"
        and skills.get("hub_skills_status") == "quarantined_candidate_only"
        and skills.get("learned_skills_status") == "suggestion_only"
        and skills.get("skill_bundles_status") == "candidate_task_profiles_only"
        and skills.get("learn_command_mode") == "suggestion_only"
        and skills.get("skill_manage_mode") == "noncanonical_staging_with_review"
        and skills.get("journey_mode") == "read_only_observability"
        and skills.get("curator_mode") == "disabled"
        and skills.get("autonomous_skill_write_authorized") is False
        and skills.get("automatic_skill_promotion_authorized") is False
        and skills.get("automatic_method_promotion_authorized") is False,
        "PCFA-06 skills, /learn, /journey or curator policy drifted",
    )

    models = value.get("model_orchestration_policy", {})
    require(
        models.get("moa_status") == "candidate_only"
        and models.get("moa_selected_directly_by_hermes") is False
        and models.get("offdata_model_router_owns_selection") is True
        and models.get("reference_outputs_are_advisory") is True
        and models.get("aggregator_must_obey_offdata_contracts") is True
        and models.get("moa_counts_as_independent_quality_review") is False
        and models.get("fanout_requires_explicit_cost_budget") is True
        and models.get("provider_allowlist_required") is True
        and models.get("evaluation_before_activation_required") is True,
        "PCFA-06 Mixture-of-Agents/model-router policy drifted",
    )

    delegation = value.get("delegation_policy", {})
    require(
        delegation.get("raw_delegate_task_authorized") is False
        and delegation.get("top_level_background_delegation_authorized") is False
        and delegation.get("nested_delegation_authorized") is False
        and delegation.get("parallel_fanout_authorized") is False
        and delegation.get("initial_adapter_concurrency_limit") == 1
        and delegation.get("child_summary_is_verified_evidence") is False
        and delegation.get("parent_or_offdata_verification_required") is True
        and delegation.get("child_direct_canonical_write_authorized") is False
        and delegation.get("hermes_process_is_durable_workflow_authority") is False,
        "PCFA-06 delegation/background/durability policy drifted",
    )

    reconciliation = value.get("pcfa07_reconciliation_contract", {})
    require(
        isinstance(reconciliation, dict)
        and len(reconciliation) == 8
        and all(item is True for item in reconciliation.values()),
        "PCFA-06 PCFA-07 reconciliation contract drifted",
    )
    require(
        boundaries.get("founder_accountability_preserved") is True
        and all(
            item is False
            for key, item in boundaries.items()
            if key != "founder_accountability_preserved"
        ),
        "PCFA-06 authorization boundaries must remain fail-closed",
    )
    require(len(digest_file(CURRENT_STATE_PATH)) == 64, "current operational-state digest is unavailable")
    return failures


def _set(value: dict[str, Any], path: tuple[str, ...], replacement: Any) -> None:
    node: Any = value
    for part in path[:-1]:
        node = node[int(part)] if part.isdigit() else node[part]
    final = path[-1]
    if final.isdigit():
        node[int(final)] = replacement
    else:
        node[final] = replacement


def run_self_test(state: dict[str, Any]) -> int:
    record = load_json(HERMES_REFRESH_PATH)
    failures = hermes_refresh_failures(state, record)
    if failures:
        raise SystemExit("PCFA-06 Hermes refresh launch contract was rejected: " + "; ".join(failures))

    rejected = 0
    state_mutations: list[tuple[str, tuple[str, ...], Any]] = [
        (
            "Hermes refresh authority removed",
            ("current_authority", "hermes_bounded_adoption_refresh"),
            "contracts/hermes-compatibility-pack.json",
        ),
        (
            "Hermes refresh digest drift",
            ("current_authority", "hermes_bounded_adoption_refresh_sha256"),
            "f" * 64,
        ),
        (
            "PCFA-06 readiness disabled",
            ("repository_readiness", "pcfa06_hermes_bounded_adoption_refresh_complete"),
            False,
        ),
        ("Phase 0 scope widened", ("launch_target", "permitted_tasks"), ["P0.1", "P1.1"]),
    ]
    for label, path, replacement in state_mutations:
        mutated = copy.deepcopy(state)
        _set(mutated, path, replacement)
        if not hermes_refresh_failures(mutated, record):
            raise SystemExit(f"PCFA-06 launch-state mutation was not rejected: {label}")
        rejected += 1

    record_mutations: list[tuple[str, tuple[str, ...], Any]] = [
        ("Hermes installation authorized", ("scope_boundary", "hermes_installation_authorized"), True),
        ("Hermes made control plane", ("scope_boundary", "hermes_is_control_plane"), True),
        ("documentation mislabeled release pin", ("upstream_baseline", "documentation_snapshot_is_release_pin"), True),
        ("capability falsely implemented", ("capability_assessments", "0", "status"), "implemented"),
        ("IMP-P0 owner", ("capability_assessments", "0", "owning_imp_phases"), ["IMP-P0"]),
        ("raw goal authorized", ("worker_goal_mapping", "raw_goal_authorized"), True),
        ("Hermes judge made authority", ("worker_goal_mapping", "hermes_goal_judge_completion_authority"), True),
        ("unbounded goal resume", ("worker_goal_mapping", "required_runtime_controls", "automatic_resume_after_budget"), True),
        ("learn writes canonical skills", ("skills_learning_policy", "learn_command_mode"), "canonical_write"),
        ("journey edits canonical state", ("skills_learning_policy", "journey_mode"), "canonical_editor"),
        ("curator enabled", ("skills_learning_policy", "curator_mode"), "enabled"),
        ("MoA selected by Hermes", ("model_orchestration_policy", "moa_selected_directly_by_hermes"), True),
        ("MoA counts as independent QA", ("model_orchestration_policy", "moa_counts_as_independent_quality_review"), True),
        ("raw delegation authorized", ("delegation_policy", "raw_delegate_task_authorized"), True),
        ("background delegation authorized", ("delegation_policy", "top_level_background_delegation_authorized"), True),
        ("parallel fanout authorized", ("delegation_policy", "parallel_fanout_authorized"), True),
        ("PCFA-07 reconciliation removed", ("pcfa07_reconciliation_contract", "every_capability_must_receive_planned_test_ids"), False),
        ("PCFA-08 final acceptance removed", ("scope_boundary", "pcfa08_final_acceptance_required"), False),
        ("Codex pre-authorized", ("boundaries", "codex_start_authorized"), True),
    ]
    for label, path, replacement in record_mutations:
        mutated = copy.deepcopy(record)
        _set(mutated, path, replacement)
        if not hermes_refresh_failures(state, mutated):
            raise SystemExit(f"PCFA-06 launch-record mutation was not rejected: {label}")
        rejected += 1
    return rejected
