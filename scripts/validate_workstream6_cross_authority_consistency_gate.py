from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Callable

import jsonschema

from build_workstream6_cross_authority_consistency_gate import (
    DOC,
    LEDGER,
    OUT,
    REPORT,
    ROOT,
    SRC,
    build_records,
    canon,
    load,
)

EXACT_CHECK = "Validate final pre-Codex canonical handoff and complete release"


def obj(path: str) -> dict[str, Any]:
    value = load(ROOT / path)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be object")
    return value


def recursive_values(value: Any, key: str) -> list[Any]:
    result: list[Any] = []
    if isinstance(value, dict):
        for candidate, child in value.items():
            if candidate == key:
                result.append(child)
            result.extend(recursive_values(child, key))
    elif isinstance(value, list):
        for child in value:
            result.extend(recursive_values(child, key))
    return result


def source_failures(source: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(source.get("work_package_id") == "WS6.14", "work package drift")
    require(
        source.get("predecessor", {}).get("head_sha")
        == "5a7c39f55c9d2e69e1be45894dfb82db53af4fa8",
        "predecessor drift",
    )
    main = source.get("main_integration", {})
    require(
        main.get("integrated_main_sha") == "cb2bffe74e62804250ac36168c4206cb8b9d021a",
        "main SHA drift",
    )
    require(main.get("integrated_through") == "WS6.7", "integrated boundary drift")
    require(main.get("earliest_unintegrated") == "WS6.8", "earliest unintegrated drift")
    require(
        main.get("later_draft_packages_do_not_count_as_integrated") is True,
        "draft integration rule lost",
    )
    phrase = source.get("canonical_status_phrase", "")
    require(
        "WS6.7" in phrase and "later WS6 work remains unintegrated" in phrase,
        "canonical status drift",
    )
    require(len(source.get("authority_domains", [])) == 12, "domain count drift")
    require(len(source.get("defect_closure_map", {})) == 25, "closure count drift")
    require(
        set(source.get("expected_unresolved_defects", {}))
        == {"WS6-BLOCK-006", "WS6-CONSIST-006", "WS6-CONSIST-010"},
        "unresolved defect set drift",
    )
    expected = {
        "defects_total": 28,
        "repository_addressed": 25,
        "expected_unresolved": 3,
        "authority_domains": 12,
        "phase0_criteria": 16,
        "later_criteria": 22,
        "developer_commands": 15,
        "developer_cases": 60,
        "founder_criteria": 8,
        "founder_cases": 32,
        "renderers": 6,
        "deliverable_cases": 38,
        "operational_signals": 8,
        "learning_metrics": 11,
        "phase0_registered_planned": 76,
        "planned_total": 83,
        "workflow_agent_conformance": 7,
    }
    require(source.get("expected_counts") == expected, "expected count contract drift")
    require(
        source.get("live_policy")
        == {
            "open_issue_numbers": [1, 19],
            "duplicate_issue": 2,
            "codex_branch_absent": True,
            "reserved_final_automatic_runs": 0,
        },
        "live policy drift",
    )
    completion = source.get("completion", {})
    require(
        completion.get("repository_consistency_gate_complete") is True,
        "consistency gate incomplete",
    )
    require(
        completion.get("all_prior_repository_contracts_consistent") is True,
        "prior consistency false",
    )
    for key in ("final_workflow_active", "permanent_release_complete", "manual_launch_gates_complete"):
        require(completion.get(key) is False, f"{key} claimed early")
    require(completion.get("next_permitted_work_package") == "WS6.15", "next package drift")
    require(source.get("remaining_blocking_defects") == ["WS6-BLOCK-006"], "remaining blocker drift")
    boundaries = source.get("boundaries", {})
    require(boundaries.get("founder_accountability_preserved") is True, "Founder accountability lost")
    for key, value in boundaries.items():
        if key != "founder_accountability_preserved":
            require(value is False, f"boundary widened {key}")
    return failures


def repository_failures(contract: dict[str, Any], ledger: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    current = obj("contracts/workstream6-current-status.json")
    registry = obj("repository/canonical-authority-registry.json")
    phrase = contract["canonical_status_phrase"]
    require(current.get("canonical_status_phrase") == phrase, "current-status phrase mismatch")
    require(registry.get("canonical_status_phrase") == phrase, "authority-registry phrase mismatch")
    for relative in (
        "README.md",
        "docs/00-START-HERE.md",
        "docs/14-CODEX-KICKOFF.md",
        "docs/19-PHASE-0-VALIDATION-ADDENDUM.md",
        "docs/20-DEVELOPMENT-STATUS.md",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        require(phrase in text, f"current phrase missing {relative}")
        require("codex_start_authorized=false" in text, f"fail-closed token missing {relative}")

    phase = obj("contracts/workstream6-phase-namespace.json")
    namespaces = {item["prefix"]: item for item in phase.get("namespaces", []) if isinstance(item, dict)}
    require(set(namespaces) == {"CF-P", "PCR-", "WS", "IMP-P"}, "phase namespace family drift")
    require(
        namespaces.get("IMP-P", {}).get("canonical_ids") == [f"IMP-P{i}" for i in range(13)],
        "IMP namespace drift",
    )
    require(namespaces.get("IMP-P", {}).get("state") == "not_started", "IMP started early")
    require(
        all(item.get("implementation_authority") is False for item in phase.get("namespaces", []) if isinstance(item, dict)),
        "namespace granted implementation authority",
    )
    require("WS6.14" in namespaces.get("WS", {}).get("canonical_ids", []), "WS6.14 absent from namespace")
    require(
        contract["snapshot_field_policy"]["rule"].startswith("Historical package snapshot fields"),
        "snapshot scope missing",
    )

    workflow = obj("contracts/workstream6-required-workflow-identity.json")
    identity = workflow.get("canonical_identity", {})
    activation = workflow.get("activation", {})
    require(identity.get("job_name") == EXACT_CHECK, "required check identity drift")
    require(
        identity.get("workflow_file") == ".github/workflows/workstream6-final-pre-codex.yml",
        "final workflow path drift",
    )
    require(activation.get("activation_work_package") == "WS6.15", "workflow activation package drift")
    require(activation.get("permanent_release_work_package") == "WS6.16", "permanent release package drift")
    require(activation.get("automatic_triggers_enabled") is False, "final workflow automatic early")
    require(activation.get("state") == "reserved_fail_closed", "final workflow reservation drift")
    final_text = (ROOT / ".github/workflows/workstream6-final-pre-codex.yml").read_text(encoding="utf-8")
    require(
        "workflow_dispatch:" in final_text and "pull_request:" not in final_text and "push:" not in final_text,
        "reserved final workflow trigger drift",
    )
    require(
        EXACT_CHECK in final_text and "exit 1" in final_text and "WS6.15" in final_text,
        "reserved final workflow not fail-closed",
    )

    handoff = obj("handoff/codex-phase0-handoff.json")
    require(handoff.get("execution", {}).get("launch_permit_required") is True, "launch permit not required")
    require(handoff.get("boundaries", {}).get("final_workstream6_gate_complete") is False, "final gate claimed complete")
    require(handoff.get("boundaries", {}).get("launch_permit_issued") is False, "permit claimed issued")
    require(handoff.get("readiness_snapshot", {}).get("codex_start_authorized") is False, "handoff authorizes Codex")
    require(
        "workstream6_final_reconciliation_merged_to_main" in handoff.get("activation_conditions", []),
        "final WS6 activation condition missing",
    )

    obligations = obj("requirements/implementation-obligation-map.json")
    require(
        obligations.get("criterion_count") == 38
        and obligations.get("phase0_blocking_criterion_count") == 16
        and obligations.get("later_phase_criterion_count") == 22,
        "implementation obligation counts drift",
    )
    require(obligations.get("test_policy", {}).get("executable_test_count") == 0, "obligation executable evidence claimed")
    developer = obj("contracts/developer-experience-specification.json")
    require(developer.get("command_count") == 15 and developer.get("acceptance_case_count") == 60, "developer experience counts drift")
    require(developer.get("implementation_evidence", {}).get("satisfied_command_count") == 0, "developer implementation evidence claimed")
    founder = obj("contracts/founder-experience-specification.json")
    require(founder.get("criterion_count") == 8 and founder.get("acceptance_case_count") == 32, "Founder experience counts drift")
    require(founder.get("evidence", {}).get("satisfied_evidence_count") == 0, "Founder implementation evidence claimed")
    deliverable = obj("contracts/deliverable-quality-implementation-specification.json")
    require(deliverable.get("renderer_count") == 6 and deliverable.get("acceptance_case_count") == 38, "deliverable quality counts drift")
    renderer = obj("contracts/workstream6-renderer-preimplementation-assets.json")
    require(renderer.get("renderer_count") == 6 and renderer.get("golden_entry_count") == 6, "renderer prep counts drift")
    require(renderer.get("completion", {}).get("physical_renderer_outputs_present") is False, "physical render claimed")
    require(renderer.get("completion", {}).get("approved_golden_baselines_present") is False, "approved golden claimed")
    operational = obj("contracts/operational-quality-specification.json")
    require(operational.get("operational_signal_count") == 8 and operational.get("learning_metric_count") == 11, "operational counts drift")
    require(
        operational.get("test_registration", {}).get("phase0_total") == 76
        and operational.get("test_registration", {}).get("planned_total") == 83,
        "WS6.13 planned test counts drift",
    )
    require(operational.get("test_registration", {}).get("executable") == 0, "WS6.13 executable evidence claimed")
    require(operational.get("completion", {}).get("telemetry_enabled") is False, "telemetry enabled")
    licence = obj("contracts/phase0-licence-decision-placeholder.json")
    require(licence.get("owner") == "Founder", "licence owner drift")
    require(licence.get("licence_state", {}).get("selected_licence") is None, "licence selected early")
    require(licence.get("licence_state", {}).get("implicit_licence_grant") is False, "implicit licence grant")
    require(licence.get("licence_state", {}).get("public_distribution_authorized") is False, "public distribution authorized")
    require(licence.get("adr", {}).get("approved") is False, "licence ADR approved early")

    require(
        ledger.get("defect_count") == 28
        and ledger.get("repository_addressed_count") == 25
        and ledger.get("expected_unresolved_count") == 3,
        "defect ledger counts drift",
    )
    unresolved = {
        item["id"]
        for item in ledger.get("entries", [])
        if item.get("overlay_state") == "expected_unresolved"
    }
    require(
        unresolved == {"WS6-BLOCK-006", "WS6-CONSIST-006", "WS6-CONSIST-010"},
        "defect ledger unresolved drift",
    )

    for relative in (
        "contracts/codex-phase0-launch-control.json",
        "contracts/workstream6-final-launch-control.json",
        "handoff/codex-phase0-handoff.json",
    ):
        value = obj(relative)
        for key in (
            "codex_start_authorized",
            "codex_start_authorised",
            "phase0_implementation_authorized",
            "phase0_implementation_authorised",
            "phase0_merge_authorized",
            "phase0_merge_authorised",
            "phase1_authorized",
            "phase1_authorised",
            "runtime_activation_authorized",
            "runtime_activation_authorised",
            "real_client_data_enabled",
            "external_actions_authorized",
            "external_actions_authorised",
        ):
            values = recursive_values(value, key)
            require(
                all(candidate is False for candidate in values if isinstance(candidate, bool)),
                f"{relative} widened {key}",
            )
    return failures


def main() -> None:
    source = load(SRC)
    source_errors = source_failures(source)
    if source_errors:
        raise SystemExit("WS6.14 source validation failed:\n- " + "\n- ".join(source_errors))
    generated = build_records()
    for path, value in zip((OUT, LEDGER, DOC, REPORT), generated, strict=True):
        expected = value if isinstance(value, str) else canon(value)
        if path.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"stale generated file: {path.relative_to(ROOT)}")
    contract, ledger, _, _ = generated
    jsonschema.validate(contract, obj("schemas/workstream6-cross-authority-consistency-gate.schema.json"))
    repository_errors = repository_failures(contract, ledger)
    if repository_errors:
        raise SystemExit("WS6.14 repository consistency failed:\n- " + "\n- ".join(repository_errors))

    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value["predecessor"].update(head_sha="bad"),
        lambda value: value["main_integration"].update(integrated_main_sha="0" * 40),
        lambda value: value["main_integration"].update(integrated_through="WS6.8"),
        lambda value: value["main_integration"].update(earliest_unintegrated="WS6.9"),
        lambda value: value["main_integration"].update(later_draft_packages_do_not_count_as_integrated=False),
        lambda value: value.update(canonical_status_phrase="integrated through WS6.6"),
        lambda value: value.update(authority_domains=[]),
        lambda value: value.update(defect_closure_map={}),
        lambda value: value.update(expected_unresolved_defects={}),
        lambda value: value["expected_counts"].update(defects_total=27),
        lambda value: value["expected_counts"].update(repository_addressed=26),
        lambda value: value["expected_counts"].update(phase0_criteria=15),
        lambda value: value["expected_counts"].update(developer_commands=14),
        lambda value: value["expected_counts"].update(founder_cases=31),
        lambda value: value["expected_counts"].update(renderers=5),
        lambda value: value["expected_counts"].update(operational_signals=7),
        lambda value: value["expected_counts"].update(planned_total=82),
        lambda value: value["live_policy"].update(open_issue_numbers=[1, 19, 54]),
        lambda value: value["live_policy"].update(codex_branch_absent=False),
        lambda value: value["live_policy"].update(reserved_final_automatic_runs=1),
        lambda value: value["completion"].update(final_workflow_active=True),
        lambda value: value["completion"].update(permanent_release_complete=True),
        lambda value: value["completion"].update(manual_launch_gates_complete=True),
        lambda value: value["completion"].update(next_permitted_work_package="IMP-P0"),
        lambda value: value.update(remaining_blocking_defects=[]),
        lambda value: value["boundaries"].update(codex_start_authorized=True),
        lambda value: value["boundaries"].update(phase0_implementation_authorized=True),
        lambda value: value["boundaries"].update(phase0_merge_authorized=True),
        lambda value: value["boundaries"].update(phase1_authorized=True),
        lambda value: value["boundaries"].update(runtime_activation_authorized=True),
        lambda value: value["boundaries"].update(real_client_data_enabled=True),
        lambda value: value["boundaries"].update(external_actions_authorized=True),
    ]
    rejected = 0
    for mutate in mutations:
        candidate = copy.deepcopy(source)
        mutate(candidate)
        if source_failures(candidate):
            rejected += 1
        else:
            raise SystemExit("WS6.14 mutation not rejected")
    print(
        f"WS6.14 cross-authority consistency gate passed: {rejected} mutations rejected, "
        "domains=12, defects=28, addressed=25, unresolved=3, integrated_through=WS6.7, "
        "next=WS6.15, codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
