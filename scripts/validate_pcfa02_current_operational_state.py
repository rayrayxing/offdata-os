from __future__ import annotations

import copy
from typing import Any

from jsonschema import Draft202012Validator

from build_pcfa02_current_operational_state import REPORT_PATH, build_records
from codex_phase0_launch_core import (
    CORRECTION_PATH,
    CURRENT_STATE_PATH,
    FINAL_RELEASE_PATH,
    ISSUE19_BODY_PATH,
    ISSUE_BODY_PATH,
    PREDECESSOR_CONTRACT_PATH,
    ROOT,
    current_state_failures,
    digest_file,
    final_release_record_failures,
    load_json,
)

STATE_SCHEMA_PATH = ROOT / "schemas" / "current-operational-state.schema.json"
PERMIT_SCHEMA_PATH = ROOT / "schemas" / "codex-phase0-launch-permit.schema.json"
CURRENT_HANDOFF_PATH = ROOT / "handoff" / "codex-phase0-current-handoff.json"
TEMPLATE_PATHS = {
    "hosted_controls": ROOT
    / "handoff"
    / "codex-phase0-current-hosted-controls-attestation.template.json",
    "clean_macos": ROOT / "handoff" / "codex-phase0-current-clean-macos-attestation.template.json",
    "founder_approval": ROOT
    / "handoff"
    / "codex-phase0-current-founder-authorization.template.json",
    "launch_ack": ROOT / "handoff" / "codex-phase0-current-launch-ack.template.json",
}
HISTORICAL_PATHS = {
    "launch_control": ROOT / "contracts" / "codex-phase0-launch-control.json",
    "ws62": ROOT / "contracts" / "workstream6-final-launch-control.json",
    "ws63": ROOT / "contracts" / "workstream6-current-status.json",
    "ws64": ROOT / "repository" / "canonical-authority-registry.json",
    "handoff": ROOT / "handoff" / "codex-phase0-handoff.json",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def _set(value: dict[str, Any], path: tuple[str, ...], replacement: Any) -> None:
    node: Any = value
    for part in path[:-1]:
        node = node[part]
    node[path[-1]] = replacement


def _template_failures(templates: dict[str, dict[str, Any]]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    hosted = templates["hosted_controls"]
    mac = templates["clean_macos"]
    approval = templates["founder_approval"]
    ack = templates["launch_ack"]
    for label, value in templates.items():
        require(value.get("schema_version") == "2.2.0", f"{label} template version drifted")
    for label, value in (
        ("hosted", hosted),
        ("mac", mac),
        ("approval", approval),
        ("ack", ack),
    ):
        require(
            "current_operational_state_sha256" in value,
            f"{label} template does not bind current operational state",
        )
        require(
            "final_workstream6_release_sha256" in value,
            f"{label} template does not bind permanent release digest",
        )
    require(
        "canonical_issue_body_sha256" in hosted and "issue_19_body_sha256" in hosted,
        "hosted template does not bind current Issue #1 and Issue #19 bodies",
    )
    require(
        "canonical_issue_body_sha256" in approval,
        "Founder approval template does not bind current Issue #1 body",
    )
    require(
        ack.get("branch") == "codex/phase-0-foundation"
        and ack.get("merge_authorized") is False
        and ack.get("phase1_authorized") is False,
        "launch acknowledgement authorization boundary drifted",
    )
    return failures


def _validate_historical_retention() -> None:
    old_launch = load_json(HISTORICAL_PATHS["launch_control"])
    old_ws62 = load_json(HISTORICAL_PATHS["ws62"])
    old_ws63 = load_json(HISTORICAL_PATHS["ws63"])
    old_ws64 = load_json(HISTORICAL_PATHS["ws64"])
    old_handoff = load_json(HISTORICAL_PATHS["handoff"])
    _require(old_launch["work_package_id"] == "WS6.2", "WS6.2 launch snapshot was rewritten")
    _require(
        old_launch["readiness_snapshot"]["final_workstream6_release_verified"] is False,
        "WS6.2 package-time readiness was rewritten instead of retained",
    )
    _require(
        old_ws62["work_package_id"] == "WS6.2"
        and old_ws63["work_package_id"] == "WS6.3"
        and old_ws64["work_package_id"] == "WS6.4",
        "historical WS6 package identities drifted",
    )
    _require(
        old_ws63["completion"]["next_permitted_work_package"] == "WS6.4",
        "WS6.3 package-time sequencing was rewritten",
    )
    _require(
        old_ws64["read_order_sources"]["machine_handoff"] == "handoff/codex-phase0-handoff.json",
        "WS6.4 package-time authority registry was rewritten",
    )
    _require(
        old_handoff["authority"]["current_launch_control"]
        == "contracts/codex-phase0-launch-control.json",
        "pre-PCFA handoff was rewritten instead of retained",
    )


def _validate_current_surfaces() -> None:
    handoff = load_json(CURRENT_HANDOFF_PATH)
    _require(handoff.get("schema_version") == "3.0.0", "current machine handoff version drifted")
    _require(
        handoff["authority"]["current_operational_state"]
        == "repository/current-operational-state.json"
        and handoff["authority"]["current_issue_body"] == "handoff/codex-phase0-current-issue.md",
        "current machine handoff does not use successor authority",
    )
    _require(
        handoff["readiness"]["workstream6_permanent_release_verified"] is True
        and handoff["readiness"]["pcfa01_launch_semantics_repaired"] is True
        and handoff["readiness"]["pcfa02_current_projection_active"] is True,
        "current machine handoff omits completed repository-side prerequisites",
    )
    _require(
        handoff["readiness"]["codex_start_authorized"] is False
        and handoff["readiness"]["launch_permit_issued"] is False,
        "current machine handoff must remain unauthorized",
    )

    issue1 = ISSUE_BODY_PATH.read_text(encoding="utf-8")
    issue19 = ISSUE19_BODY_PATH.read_text(encoding="utf-8")
    for token in (
        "repository/current-operational-state.json",
        "contracts/pcfa01-launch-control-repair.json",
        "release_parent_main_sha",
        "current_operational_state_sha256",
        "codex_start_authorized=false",
    ):
        _require(token in issue1, f"current Issue #1 body missing token: {token}")
    for token in (
        "repository/current-operational-state.json",
        "current_operational_state_sha256",
        'remaining_branches=["main"]',
        "release_parent_main_sha",
    ):
        _require(token in issue19, f"current Issue #19 body missing token: {token}")
    _require(
        "release must bind the exact current `main` SHA" not in issue1,
        "current Issue #1 reintroduced the historical release/current-main equality bug",
    )
    _require(
        "doctor report, attestation and final release reference the same SHA" not in issue19,
        "current Issue #19 reintroduced the historical release/current-main equality bug",
    )


def main() -> None:
    state = load_json(CURRENT_STATE_PATH)
    predecessor = load_json(PREDECESSOR_CONTRACT_PATH)
    repair = load_json(CORRECTION_PATH)
    release = load_json(FINAL_RELEASE_PATH)

    schema = load_json(STATE_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(state))
    _require(
        not errors,
        "current operational-state schema validation failed: "
        + "; ".join(error.message for error in errors),
    )

    expected_state, expected_report = build_records()
    _require(state == expected_state, "current operational-state JSON does not match its governed YAML source")
    _require(
        REPORT_PATH.read_text(encoding="utf-8") == expected_report,
        "PCFA-02 generated evidence report drifted",
    )

    failures = current_state_failures(state, predecessor, repair)
    _require(not failures, "PCFA-02 current-state semantics failed: " + "; ".join(failures))
    release_failures = final_release_record_failures(release)
    _require(
        not release_failures,
        "permanent WS6.16 release failed current-state validation: " + "; ".join(release_failures),
    )

    _validate_historical_retention()
    _validate_current_surfaces()

    templates = {key: load_json(path) for key, path in TEMPLATE_PATHS.items()}
    template_errors = _template_failures(templates)
    _require(
        not template_errors,
        "current evidence-template validation failed: " + "; ".join(template_errors),
    )

    permit_schema = load_json(PERMIT_SCHEMA_PATH)
    Draft202012Validator.check_schema(permit_schema)
    _require(
        permit_schema["properties"]["schema_version"]["const"] == "2.2.0",
        "current permit schema version drifted",
    )
    digest_required = permit_schema["properties"]["evidence_digests"]["required"]
    _require(
        "current_operational_state" in digest_required,
        "permit schema does not bind current operational-state digest",
    )
    _require(
        "stale_on_current_operational_state_change" in permit_schema["required"],
        "permit schema does not become stale on current-state change",
    )

    for path, label in (
        (CURRENT_STATE_PATH, "current operational-state"),
        (ISSUE_BODY_PATH, "current Issue #1"),
        (ISSUE19_BODY_PATH, "current Issue #19"),
    ):
        _require(len(digest_file(path)) == 64, f"{label} digest is unavailable")

    state_mutations: list[tuple[str, tuple[str, ...], Any]] = [
        ("status", ("status",), "ready"),
        (
            "operational path",
            ("current_authority", "operational_state"),
            "contracts/codex-phase0-launch-control.json",
        ),
        (
            "handoff path",
            ("current_authority", "machine_handoff"),
            "handoff/codex-phase0-handoff.json",
        ),
        (
            "issue path",
            ("current_authority", "canonical_issue_body"),
            "handoff/codex-phase0-issue-final.md",
        ),
        (
            "repair path",
            ("current_authority", "launch_semantics_repair"),
            "contracts/codex-phase0-launch-control.json",
        ),
        (
            "historical readiness semantics",
            ("state_semantics", "historical_snapshot_readiness_must_not_drive_current_launch_decisions"),
            False,
        ),
        (
            "sole projection semantics",
            ("state_semantics", "current_operational_state_is_the_only_live_machine_readiness_projection"),
            False,
        ),
        ("release parent history", ("state_semantics", "release_parent_main_sha_is_historical"), False),
        (
            "release parent ancestry",
            ("release_semantics", "release_parent_must_be_ancestor_of_approved_launch_main"),
            False,
        ),
        (
            "release record ancestry",
            ("release_semantics", "release_record_commit_must_be_ancestor_of_approved_launch_main"),
            False,
        ),
        (
            "release parent exclusion",
            ("release_semantics", "release_parent_excluded_from_current_launch_sha_equality"),
            False,
        ),
        (
            "release record exclusion",
            ("release_semantics", "release_record_commit_excluded_from_current_launch_sha_equality"),
            False,
        ),
        ("phase scope", ("launch_target", "permitted_tasks"), ["P0.1"]),
        ("branch", ("launch_target", "required_branch"), "feature"),
        ("status check", ("launch_target", "required_status_check"), "old check"),
        (
            "permit current-state staleness",
            ("launch_permit", "stale_on_current_operational_state_change"),
            False,
        ),
        (
            "repository readiness",
            ("repository_readiness", "pcfa01_launch_semantics_repaired"),
            False,
        ),
        ("manual authorization", ("manual_launch_gates", "codex_start_authorized"), True),
        ("implementation authorization", ("boundaries", "phase0_implementation_authorized"), True),
        ("merge authorization", ("boundaries", "merge_authorized"), True),
        ("scope widening", ("allowed_scope",), state["allowed_scope"] + ["activate_runtime"]),
        ("prohibition weakening", ("prohibited_scope",), state["prohibited_scope"][:-1]),
    ]
    rejected = 0
    for label, path, replacement in state_mutations:
        mutated = copy.deepcopy(state)
        _set(mutated, path, replacement)
        _require(
            bool(current_state_failures(mutated, predecessor, repair)),
            f"PCFA-02 state mutation was not rejected: {label}",
        )
        rejected += 1

    mutated = copy.deepcopy(state)
    for item in mutated["historical_package_snapshots"]:
        if item["path"] == "contracts/codex-phase0-launch-control.json":
            item["classification"] = "current_launch_contract"
    _require(
        bool(current_state_failures(mutated, predecessor, repair)),
        "historical launch-control reclassification was not rejected",
    )
    rejected += 1

    template_mutations = [
        ("hosted version", "hosted_controls", ("schema_version",), "2.1.0"),
        ("mac version", "clean_macos", ("schema_version",), "2.1.0"),
        ("approval version", "founder_approval", ("schema_version",), "2.1.0"),
        ("ack version", "launch_ack", ("schema_version",), "2.1.0"),
        ("ack merge", "launch_ack", ("merge_authorized",), True),
    ]
    for label, target, path, replacement in template_mutations:
        mutated_templates = copy.deepcopy(templates)
        _set(mutated_templates[target], path, replacement)
        _require(
            bool(_template_failures(mutated_templates)),
            f"PCFA-02 template mutation was not rejected: {label}",
        )
        rejected += 1

    print(
        "PCFA-02 current operational-state validation passed: "
        f"historical_snapshots={len(state['historical_package_snapshots'])}, "
        f"mutations_rejected={rejected}, current_issue_bodies=2, current_templates=4, "
        "permanent_release_valid=true, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
