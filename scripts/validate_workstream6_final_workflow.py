from __future__ import annotations

import copy
from typing import Any, Callable

import jsonschema

from build_workstream6_final_workflow import DOC, OUT, REPORT, ROOT, SRC, build_records, canon, load

EXACT_CHECK = "Validate final pre-Codex canonical handoff and complete release"
FINAL_RELEASE = ROOT / "releases/pre-codex-final-reconciliation-2026-08-06.json"


def obj(path: str) -> dict[str, Any]:
    value = load(ROOT / path)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be object")
    return value


def source_failures(source: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(source.get("work_package_id") == "WS6.15", "work package drift")
    require(source.get("predecessor", {}).get("head_sha") == "a4e45baf836c86d7264f08aa6d351a31caa896dd", "predecessor drift")
    require(source.get("predecessor", {}).get("pull_request") == 60, "predecessor PR drift")
    require(source.get("predecessor", {}).get("integrated_to_main") is True, "predecessor integration drift")
    main = source.get("main_integration", {})
    require(main.get("integrated_main_sha") == "05e9dfa9f9038a56061d376e1783b78f9607665f", "integrated main drift")
    require(main.get("integrated_through") == "WS6.14", "integrated boundary drift")
    require(main.get("earliest_unintegrated") == "WS6.15", "earliest unintegrated drift")
    identity = source.get("canonical_identity", {})
    require(identity.get("workflow_file") == ".github/workflows/workstream6-final-pre-codex.yml", "workflow path drift")
    require(identity.get("workflow_name") == "Final pre-Codex canonical handoff and release", "workflow name drift")
    require(identity.get("job_key") == "validate-final-pre-codex", "job key drift")
    require(identity.get("job_name") == EXACT_CHECK, "job identity drift")
    require(identity.get("identity_must_not_change") is True, "identity mutability widened")
    activation = source.get("activation", {})
    require(activation.get("state") == "active_fail_closed_pending_permanent_release", "activation state drift")
    require(activation.get("automatic_triggers") == ["pull_request", "push_main", "workflow_dispatch"], "trigger drift")
    require(activation.get("activation_work_package") == "WS6.15", "activation package drift")
    require(activation.get("permanent_release_work_package") == "WS6.16", "release package drift")
    for key in ("non_activation_runs_require_permanent_release", "main_runs_require_permanent_release", "manual_dispatch_requires_permanent_release"):
        require(activation.get(key) is True, f"{key} must remain true")
    exception = activation.get("activation_exception", {})
    require(exception.get("event") == "pull_request", "exception event drift")
    require(exception.get("head_branch") == "governance/ws615-final-workflow", "exception head drift")
    require(exception.get("base_branch") == "main", "exception base drift")
    require(exception.get("base_sha") == "05e9dfa9f9038a56061d376e1783b78f9607665f", "exception base SHA drift")
    require(exception.get("requires_permanent_release") is False, "activation PR wrongly requires release")
    require(exception.get("requires_release_absent") is True, "activation PR no longer rejects premature release")
    require(exception.get("requires_final_gate_self_test") is True, "activation PR self-test removed")
    require(exception.get("must_be_removed_or_expire_in") == "WS6.16", "exception expiry drift")
    supersession = source.get("supersession", {})
    require(supersession.get("identity_snapshot_contract") == "contracts/workstream6-required-workflow-identity.json", "identity snapshot authority drift")
    require(supersession.get("current_activation_authority") == "contracts/workstream6-final-workflow.json", "current activation authority drift")
    require(supersession.get("preserved_identity_fields") == ["workflow_file", "workflow_name", "job_key", "job_name"], "preserved identity field drift")
    require(supersession.get("historical_snapshot_fields") == ["activation.state", "activation.allowed_triggers", "activation.automatic_triggers_enabled", "activation.final_release_verified", "activation.hosted_branch_protection_configured", "activation.manual_dispatch_must_fail"], "historical activation snapshot drift")
    require(supersession.get("rule") == "WS6.6 remains authoritative for the exact workflow/check identity and retained package evidence; WS6.15 supersedes only its package-time activation-state fields.", "supersession rule drift")
    pred = source.get("predecessor_consistency", {})
    require(pred.get("authority_domains") == 12 and pred.get("baseline_defects") == 28 and pred.get("repository_addressed") == 25, "WS6.14 counts drift")
    require(set(pred.get("expected_unresolved", [])) == {"WS6-BLOCK-006", "WS6-CONSIST-006", "WS6-CONSIST-010"}, "WS6.14 unresolved drift")
    require(pred.get("historical_ws614_final_workflow_active_false_is_package_snapshot") is True, "successor snapshot rule lost")
    completion = source.get("completion", {})
    require(completion.get("repository_final_workflow_package_complete") is True, "package incomplete")
    require(completion.get("final_workflow_active") is True, "workflow not active")
    for key in ("permanent_release_complete", "manual_launch_gates_complete", "all_blocking_defects_closed"):
        require(completion.get(key) is False, f"{key} claimed early")
    require(completion.get("next_permitted_work_package") == "WS6.16", "next package drift")
    require(source.get("remaining_defects") == ["WS6-BLOCK-006", "WS6-CONSIST-006", "WS6-CONSIST-010"], "remaining defect drift")
    boundaries = source.get("boundaries", {})
    require(boundaries.get("founder_accountability_preserved") is True, "Founder accountability lost")
    for key, value in boundaries.items():
        if key != "founder_accountability_preserved":
            require(value is False, f"boundary widened: {key}")
    return failures


def repository_failures(contract: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    ws614 = obj("contracts/workstream6-cross-authority-consistency-gate.json")
    require(ws614.get("authority_domain_count") == 12, "WS6.14 domain count drift")
    require(ws614.get("defect_count") == 28 and ws614.get("repository_addressed_count") == 25 and ws614.get("expected_unresolved_count") == 3, "WS6.14 defect counts drift")
    require(ws614.get("completion", {}).get("final_workflow_active") is False, "WS6.14 historical snapshot was rewritten")
    require(ws614.get("completion", {}).get("next_permitted_work_package") == "WS6.15", "WS6.14 successor drift")
    ledger = obj("repository/workstream6-defect-closure-ledger.json")
    unresolved = {item.get("id") for item in ledger.get("entries", []) if item.get("overlay_state") == "expected_unresolved"}
    require(unresolved == {"WS6-BLOCK-006", "WS6-CONSIST-006", "WS6-CONSIST-010"}, "defect ledger drift")
    identity = obj("contracts/workstream6-required-workflow-identity.json")
    require(identity.get("canonical_identity", {}).get("job_name") == EXACT_CHECK, "reserved identity drift")
    require(identity.get("activation", {}).get("activation_work_package") == "WS6.15", "reserved activation owner drift")
    workflow = (ROOT / ".github/workflows/workstream6-final-pre-codex.yml").read_text(encoding="utf-8")
    for token in (
        "name: Final pre-Codex canonical handoff and release",
        "pull_request:",
        "push:",
        "branches: [main]",
        "workflow_dispatch:",
        "validate-final-pre-codex:",
        f"name: {EXACT_CHECK}",
        "bash scripts/run_ws62_ci.sh",
        "governance/ws615-final-workflow",
        "EXPECTED_BASE: main",
        "05e9dfa9f9038a56061d376e1783b78f9607665f",
        "python scripts/require_workstream6_final_reconciliation.py --self-test",
        "python scripts/require_workstream6_final_reconciliation.py",
        "releases/pre-codex-final-reconciliation-2026-08-06.json",
        "Assemble exact final-check evidence",
        "Retain exact final-check evidence",
        "sha256sum -c ../repository-digests.txt",
        "offdata-final-pre-codex-${{ github.sha }}",
    ):
        require(token in workflow, f"final workflow missing token: {token}")
    require("Refuse activation before WS6.15" not in workflow, "reserved hard-fail step still active")
    require("exit 1" not in workflow, "unconditional hard-fail remains in final workflow")
    require(not FINAL_RELEASE.exists(), "permanent release exists before WS6.16")
    handoff = obj("handoff/codex-phase0-handoff.json")
    require(handoff.get("readiness_snapshot", {}).get("codex_start_authorized") is False, "handoff authorizes Codex")
    require(handoff.get("boundaries", {}).get("launch_permit_issued") is False, "permit claimed issued")
    require(handoff.get("execution", {}).get("launch_permit_required") is True, "permit requirement lost")
    launch = obj("contracts/codex-phase0-launch-control.json")
    bools = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"codex_start_authorized", "phase0_implementation_authorized", "phase0_merge_authorized", "phase1_authorized", "runtime_activation_authorized", "real_client_data_enabled", "external_actions_authorized"} and isinstance(child, bool):
                    bools.append((key, child))
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(launch)
    require(all(value is False for _, value in bools), "launch-control boundary widened")
    require(contract.get("remaining_defect_count") == 3, "contract remaining defect count drift")
    return failures


def main() -> None:
    source = load(SRC)
    failures = source_failures(source)
    if failures:
        raise SystemExit("WS6.15 source validation failed:\n- " + "\n- ".join(failures))
    contract, doc, report = build_records()
    expected = ((OUT, canon(contract)), (DOC, doc + "\n"), (REPORT, report + "\n"))
    for path, text in expected:
        if path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"stale generated file: {path.relative_to(ROOT)}")
    jsonschema.validate(contract, obj("schemas/workstream6-final-workflow.schema.json"))
    failures = repository_failures(contract)
    if failures:
        raise SystemExit("WS6.15 repository validation failed:\n- " + "\n- ".join(failures))
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda v: v["predecessor"].update(head_sha="bad"),
        lambda v: v["main_integration"].update(integrated_main_sha="0" * 40),
        lambda v: v["main_integration"].update(integrated_through="WS6.13"),
        lambda v: v["canonical_identity"].update(job_name="wrong"),
        lambda v: v["canonical_identity"].update(identity_must_not_change=False),
        lambda v: v["activation"].update(state="reserved_fail_closed"),
        lambda v: v["activation"].update(automatic_triggers=["workflow_dispatch"]),
        lambda v: v["activation"].update(activation_work_package="WS6.16"),
        lambda v: v["activation"].update(permanent_release_work_package="WS6.15"),
        lambda v: v["activation"].update(non_activation_runs_require_permanent_release=False),
        lambda v: v["activation"].update(main_runs_require_permanent_release=False),
        lambda v: v["activation"].update(manual_dispatch_requires_permanent_release=False),
        lambda v: v["activation"]["activation_exception"].update(event="push"),
        lambda v: v["activation"]["activation_exception"].update(head_branch="main"),
        lambda v: v["activation"]["activation_exception"].update(base_branch="stale-base"),
        lambda v: v["activation"]["activation_exception"].update(base_sha="0" * 40),
        lambda v: v["activation"]["activation_exception"].update(requires_permanent_release=True),
        lambda v: v["activation"]["activation_exception"].update(requires_release_absent=False),
        lambda v: v["activation"]["activation_exception"].update(requires_final_gate_self_test=False),
        lambda v: v["activation"]["activation_exception"].update(must_be_removed_or_expire_in="never"),
        lambda v: v["supersession"].update(identity_snapshot_contract="wrong"),
        lambda v: v["supersession"].update(current_activation_authority="wrong"),
        lambda v: v["supersession"].update(preserved_identity_fields=[]),
        lambda v: v["supersession"].update(historical_snapshot_fields=[]),
        lambda v: v["supersession"].update(rule="wrong"),
        lambda v: v["predecessor_consistency"].update(authority_domains=11),
        lambda v: v["predecessor_consistency"].update(baseline_defects=27),
        lambda v: v["predecessor_consistency"].update(repository_addressed=26),
        lambda v: v["predecessor_consistency"].update(expected_unresolved=[]),
        lambda v: v["predecessor_consistency"].update(historical_ws614_final_workflow_active_false_is_package_snapshot=False),
        lambda v: v["completion"].update(final_workflow_active=False),
        lambda v: v["completion"].update(permanent_release_complete=True),
        lambda v: v["completion"].update(manual_launch_gates_complete=True),
        lambda v: v["completion"].update(all_blocking_defects_closed=True),
        lambda v: v["completion"].update(next_permitted_work_package="IMP-P0"),
        lambda v: v.update(remaining_defects=[]),
        lambda v: v["boundaries"].update(codex_start_authorized=True),
        lambda v: v["boundaries"].update(phase0_implementation_authorized=True),
        lambda v: v["boundaries"].update(phase0_merge_authorized=True),
        lambda v: v["boundaries"].update(phase1_authorized=True),
        lambda v: v["boundaries"].update(runtime_activation_authorized=True),
        lambda v: v["boundaries"].update(real_client_data_enabled=True),
        lambda v: v["boundaries"].update(external_actions_authorized=True),
        lambda v: v["boundaries"].update(autonomous_merge_authorized=True),
    ]
    rejected = 0
    for mutate in mutations:
        candidate = copy.deepcopy(source)
        mutate(candidate)
        if source_failures(candidate):
            rejected += 1
        else:
            raise SystemExit("WS6.15 mutation not rejected")
    print(
        f"WS6.15 final workflow passed: {rejected} mutations rejected, triggers=3, "
        "activation_exception=exact_ws615_pr_only, permanent_release=false, next=WS6.16, "
        "codex_start_authorized=false."
    )


if __name__ == "__main__":
    main()
