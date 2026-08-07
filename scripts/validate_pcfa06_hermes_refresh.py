from __future__ import annotations

import copy
import re
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from build_pcfa06_hermes_refresh import REPORT_PATH, build_records
from codex_phase0_launch_core import CURRENT_STATE_PATH, ROOT, load_json
from pcfa06_hermes_refresh import (
    HERMES_REFRESH_PATH,
    REQUIRED_CAPABILITIES,
    REQUIRED_EVIDENCE,
    REQUIRED_MODES,
    REQUIRED_PRINCIPLES,
    hermes_refresh_failures,
    run_self_test,
)

SCHEMA_PATH = ROOT / "schemas" / "pcfa06-hermes-bounded-adoption-refresh.schema.json"
BACKLOG_PATH = ROOT / "docs" / "11-BUILD-BACKLOG.md"
DOC_PATH = ROOT / "docs" / "73-PCFA-06-HERMES-BOUNDED-ADOPTION-REFRESH.md"
STATUS_PATH = ROOT / "docs" / "CURRENT-OPERATIONAL-STATE.md"
HANDOFF_PATH = ROOT / "handoff" / "codex-phase0-current-handoff.json"
ISSUE1_PATH = ROOT / "handoff" / "codex-phase0-current-issue.md"
PCR06_PATH = ROOT / "contracts" / "hermes-compatibility-pack.json"
PCR05_PATH = ROOT / "contracts" / "runtime-adapter-contracts.json"
AGENTS_GLOB_ROOT = ROOT / "agents"


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

    upstream = record.get("upstream_baseline", {})
    scope = record.get("scope_boundary", {})
    principles = record.get("operating_principles", [])
    principle_ids = {item.get("id") for item in principles if isinstance(item, dict)}
    evidence = record.get("upstream_evidence", [])
    evidence_ids = {item.get("evidence_id") for item in evidence if isinstance(item, dict)}
    capabilities = record.get("capability_assessments", [])
    capability_map = {
        item.get("capability_id"): item for item in capabilities if isinstance(item, dict)
    }

    require(record.get("assessment_date") == "2026-08-08", "PCFA-06 assessment date drifted")
    require(
        upstream.get("stable_release") == "v0.18.2"
        and upstream.get("stable_tag") == "v2026.7.7.2"
        and upstream.get("stable_commit") == "9de9c25"
        and upstream.get("version_change_from_pcr06") is False
        and upstream.get("update_policy") == "pinned_review_required"
        and upstream.get("documentation_snapshot_is_release_pin") is False,
        "PCFA-06 upstream pin/snapshot classification drifted",
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
        and scope.get("codex_start_authorized") is False,
        "PCFA-06 fail-closed scope drifted",
    )
    require(
        len(principles) == 10 and principle_ids == REQUIRED_PRINCIPLES,
        "PCFA-06 bounded-adoption principles drifted",
    )
    require(
        len(evidence) == 8
        and evidence_ids == REQUIRED_EVIDENCE
        and {item.get("source_kind") for item in evidence if isinstance(item, dict)}
        == {"stable_release", "current_documentation"},
        "PCFA-06 upstream evidence family drifted",
    )
    require(
        len(capabilities) == 11
        and set(capability_map) == REQUIRED_CAPABILITIES
        and all(
            item.get("status") == "planned_not_implemented"
            and item.get("owning_imp_phases")
            and item.get("integration_points")
            and "IMP-P0" not in item.get("owning_imp_phases", [])
            and item.get("required_controls")
            and item.get("denied_raw_actions")
            for item in capabilities
            if isinstance(item, dict)
        )
        and all(capability_map[key].get("offdata_mode") == mode for key, mode in REQUIRED_MODES.items()),
        "PCFA-06 capability family, modes or implementation boundary drifted",
    )

    goal = record.get("worker_goal_mapping", {})
    require(
        goal.get("raw_goal_authorized") is False
        and goal.get("hermes_goal_state_canonical") is False
        and goal.get("hermes_goal_judge_completion_authority") is False
        and goal.get("offdata_acceptance_completion_authority") is True
        and goal.get("mapping", {}).get("verification") == "WorkerPackage.acceptance"
        and goal.get("required_runtime_controls", {}).get("turn_budget_bounded") is True
        and goal.get("required_runtime_controls", {}).get("automatic_resume_after_budget") is False
        and goal.get("required_runtime_controls", {}).get("durable_checkpoint_owned_by_offdata") is True,
        "PCFA-06 /goal adapter semantics drifted",
    )
    skills = record.get("skills_learning_policy", {})
    require(
        skills.get("learn_command_mode") == "suggestion_only"
        and skills.get("journey_mode") == "read_only_observability"
        and skills.get("curator_mode") == "disabled"
        and skills.get("hub_skills_status") == "quarantined_candidate_only"
        and skills.get("automatic_skill_promotion_authorized") is False
        and skills.get("automatic_method_promotion_authorized") is False,
        "PCFA-06 skills/learning governance drifted",
    )
    models = record.get("model_orchestration_policy", {})
    require(
        models.get("moa_status") == "candidate_only"
        and models.get("moa_selected_directly_by_hermes") is False
        and models.get("offdata_model_router_owns_selection") is True
        and models.get("moa_counts_as_independent_quality_review") is False
        and models.get("fanout_requires_explicit_cost_budget") is True,
        "PCFA-06 MoA/router governance drifted",
    )
    delegation = record.get("delegation_policy", {})
    require(
        delegation.get("raw_delegate_task_authorized") is False
        and delegation.get("top_level_background_delegation_authorized") is False
        and delegation.get("nested_delegation_authorized") is False
        and delegation.get("parallel_fanout_authorized") is False
        and delegation.get("initial_adapter_concurrency_limit") == 1
        and delegation.get("parent_or_offdata_verification_required") is True
        and delegation.get("hermes_process_is_durable_workflow_authority") is False,
        "PCFA-06 delegation/durability governance drifted",
    )
    reconciliation = record.get("pcfa07_reconciliation_contract", {})
    require(
        isinstance(reconciliation, dict)
        and len(reconciliation) == 8
        and all(value is True for value in reconciliation.values()),
        "PCFA-06 PCFA-07 reconciliation contract drifted",
    )
    boundaries = record.get("boundaries", {})
    require(
        boundaries.get("founder_accountability_preserved") is True
        and all(value is False for key, value in boundaries.items() if key != "founder_accountability_preserved"),
        "PCFA-06 authorization boundaries drifted",
    )
    return failures


def _validate_backlog_bindings(record: dict[str, Any]) -> None:
    text = BACKLOG_PATH.read_text(encoding="utf-8")
    task_ids = set(re.findall(r"^### (P(?:[0-9]|1[0-2])\.[0-9]+)\b", text, flags=re.MULTILINE))
    referenced = {
        task
        for item in record["capability_assessments"]
        for task in item["integration_points"]
    }
    missing = sorted(referenced - task_ids)
    _require(not missing, "PCFA-06 references missing existing backlog tasks: " + ", ".join(missing))


def _validate_predecessor_authority(record: dict[str, Any]) -> None:
    pcr06 = load_json(PCR06_PATH)
    _require(
        pcr06.get("phase_id") == "PCR-06"
        and pcr06.get("upstream", {}).get("assessed_release") == "v0.18.2"
        and pcr06.get("upstream", {}).get("assessed_tag") == "v2026.7.7.2"
        and pcr06.get("upstream", {}).get("assessed_commit") == "9de9c25"
        and pcr06.get("adoption", {}).get("runtime_activation_authorized") is False
        and pcr06.get("readiness_snapshot", {}).get("hermes_activation_authorized") is False,
        "PCFA-06 no longer preserves the accepted PCR-06 pin or fail-closed activation state",
    )
    _require(
        record["upstream_baseline"]["predecessor_contract"]
        == "contracts/hermes-compatibility-pack.json",
        "PCFA-06 predecessor contract binding drifted",
    )

    pcr05 = load_json(PCR05_PATH)
    profiles = {item.get("adapter_id"): item for item in pcr05.get("adapter_profiles", [])}
    hermes_adapter = profiles.get("hermes-worker-harness", {})
    _require(
        hermes_adapter.get("activation_authorized") is False
        and hermes_adapter.get("status") == "deferred"
        and hermes_adapter.get("credential_mode") == "none"
        and hermes_adapter.get("network_mode") == "deny_until_review",
        "PCFA-06 widened the PCR-05 Hermes runtime-adapter boundary",
    )

    skills = sorted(AGENTS_GLOB_ROOT.glob("*/SKILL.md"))
    _require(len(skills) == 11, "PCFA-06 expected exactly 11 repository-canonical offdata skills")


def _validate_current_surfaces(state: dict[str, Any]) -> None:
    handoff = load_json(HANDOFF_PATH)
    _require(
        handoff["authority"].get("hermes_bounded_adoption_refresh")
        == "repository/pcfa06-hermes-bounded-adoption-refresh.json",
        "current handoff omits PCFA-06 Hermes authority",
    )
    _require(
        handoff["readiness"].get("pcfa06_hermes_bounded_adoption_refresh_complete") is True,
        "current handoff omits PCFA-06 readiness",
    )
    _require(
        "repository/pcfa06-hermes-bounded-adoption-refresh.json" in handoff["read_order"]
        and "docs/73-PCFA-06-HERMES-BOUNDED-ADOPTION-REFRESH.md" in handoff["read_order"],
        "current handoff read order omits PCFA-06",
    )
    _require(
        "python scripts/validate_pcfa06_hermes_refresh.py" in handoff["execution"]["required_commands"],
        "current handoff preflight omits PCFA-06 validation",
    )
    _require(
        state["launch_target"]["permitted_tasks"] == ["P0.1", "P0.2", "P0.3", "P0.4"],
        "PCFA-06 widened the launch target",
    )
    snapshots = {
        (item.get("path"), item.get("package"), item.get("classification"))
        for item in state.get("historical_package_snapshots", [])
        if isinstance(item, dict)
    }
    _require(
        (
            "contracts/hermes-compatibility-pack.json",
            "PCR-06",
            "retained_historical_package_snapshot",
        )
        in snapshots,
        "current operational state does not retain PCR-06 as historical predecessor evidence",
    )
    for path, tokens in (
        (
            ISSUE1_PATH,
            (
                "PCFA-06",
                "Hermes bounded-adoption refresh",
                "v0.18.2",
                "planned_not_implemented",
            ),
        ),
        (
            STATUS_PATH,
            (
                "PCFA-06",
                "Hermes bounded-adoption refresh",
                "Raw `/goal`",
                "Mixture-of-Agents",
            ),
        ),
        (
            DOC_PATH,
            (
                "v0.18.2",
                "WorkerPackage.acceptance",
                "suggestion-only",
                "read-only",
                "Mixture-of-Agents",
                "background delegation",
                "codex_start_authorized=false",
            ),
        ),
    ):
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            _require(token in text, f"{path.relative_to(ROOT)} missing PCFA-06 token: {token}")


def main() -> None:
    record = load_json(HERMES_REFRESH_PATH)
    state = load_json(CURRENT_STATE_PATH)
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(record))
    _require(
        not errors,
        "PCFA-06 schema validation failed: " + "; ".join(error.message for error in errors),
    )

    expected_record, expected_report = build_records()
    _require(record == expected_record, "PCFA-06 generated JSON does not match governed YAML source")
    _require(
        REPORT_PATH.read_text(encoding="utf-8") == expected_report,
        "PCFA-06 generated evidence report drifted",
    )
    semantic = _semantic_failures(record)
    _require(not semantic, "PCFA-06 semantic validation failed: " + "; ".join(semantic))
    launch = hermes_refresh_failures(state, record)
    _require(not launch, "PCFA-06 launch binding failed: " + "; ".join(launch))
    _validate_backlog_bindings(record)
    _validate_predecessor_authority(record)
    _validate_current_surfaces(state)

    mutations: list[tuple[str, tuple[str, ...], Any]] = [
        ("stable release drift", ("upstream_baseline", "stable_release"), "v0.19.0"),
        ("docs mislabeled release pin", ("upstream_baseline", "documentation_snapshot_is_release_pin"), True),
        ("principle identity", ("operating_principles", "0", "id"), "HERMES-BOUND-99"),
        ("evidence identity", ("upstream_evidence", "0", "evidence_id"), "HERMES-EVID-OTHER"),
        ("capability identity", ("capability_assessments", "0", "capability_id"), "HERMES-CAP-OTHER"),
        ("capability implemented", ("capability_assessments", "0", "status"), "implemented"),
        ("IMP-P0 owner", ("capability_assessments", "0", "owning_imp_phases"), ["IMP-P0"]),
        ("raw goal authority", ("worker_goal_mapping", "raw_goal_authorized"), True),
        ("Hermes judge authority", ("worker_goal_mapping", "hermes_goal_judge_completion_authority"), True),
        ("goal budget auto-resume", ("worker_goal_mapping", "required_runtime_controls", "automatic_resume_after_budget"), True),
        ("learn canonical", ("skills_learning_policy", "learn_command_mode"), "canonical_write"),
        ("journey canonical editor", ("skills_learning_policy", "journey_mode"), "canonical_editor"),
        ("curator activated", ("skills_learning_policy", "curator_mode"), "enabled"),
        ("MoA direct selection", ("model_orchestration_policy", "moa_selected_directly_by_hermes"), True),
        ("MoA independent QA", ("model_orchestration_policy", "moa_counts_as_independent_quality_review"), True),
        ("background delegation", ("delegation_policy", "top_level_background_delegation_authorized"), True),
        ("nested delegation", ("delegation_policy", "nested_delegation_authorized"), True),
        ("parallel fanout", ("delegation_policy", "parallel_fanout_authorized"), True),
        ("PCFA-07 mapping removed", ("pcfa07_reconciliation_contract", "every_capability_must_receive_planned_test_ids"), False),
        ("runtime activation", ("boundaries", "runtime_activation_authorized"), True),
        ("Codex authorized", ("boundaries", "codex_start_authorized"), True),
    ]
    rejected = 0
    for label, path, replacement in mutations:
        mutated = copy.deepcopy(record)
        _set(mutated, path, replacement)
        if list(validator.iter_errors(mutated)):
            rejected += 1
            continue
        if _semantic_failures(mutated) or hermes_refresh_failures(state, mutated):
            rejected += 1
            continue
        raise SystemExit(f"PCFA-06 mutation was not rejected: {label}")

    launch_rejected = run_self_test(state)
    print(
        "PCFA-06 Hermes bounded-adoption refresh validation passed: "
        f"stable_release={record['upstream_baseline']['stable_release']}, "
        f"capabilities={len(record['capability_assessments'])}, "
        f"principles={len(record['operating_principles'])}, "
        f"upstream_evidence={len(record['upstream_evidence'])}, "
        f"semantic_mutations_rejected={rejected}, launch_mutations_rejected={launch_rejected}, "
        "planned_not_implemented=true, hermes_activation_authorized=false, "
        "pcfa07_required=true, pcfa08_required=true, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
